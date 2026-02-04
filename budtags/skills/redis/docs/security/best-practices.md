# Redis Security Best Practices

Comprehensive security hardening for Redis deployments.

---

## Network Security

### 1. Never Expose to Internet

```
# redis.conf
bind 127.0.0.1 192.168.1.100
# OR bind to specific interface only
bind 10.0.0.5
```

### 2. Use Firewall

```bash
# UFW
ufw default deny incoming
ufw allow from 10.0.0.0/24 to any port 6379

# iptables
iptables -A INPUT -s 10.0.0.0/24 -p tcp --dport 6379 -j ACCEPT
iptables -A INPUT -p tcp --dport 6379 -j DROP
```

### 3. VPC/Private Network

- Deploy Redis in private subnet
- No public IP assignment
- Use bastion/jump host for access

### 4. Protected Mode

```
# redis.conf (enabled by default)
protected-mode yes
```

---

## Authentication

### 1. Strong Passwords

```php
// Generate strong password
$password = bin2hex(random_bytes(32)); // 64 character hex
```

```
# redis.conf
requirepass a3f8d2e9c1b4a7f5e0d3c6b9a2f5e8d1c4b7a0f3e6d9c2b5a8f1e4d7c0b3a6
```

### 2. Use ACL (Redis 6+)

```
# Disable default user
user default off

# Create application user
user app on >strong-password ~* +@all -@admin -@dangerous

# Create read-only user
user readonly on >readonly-pass ~* +@read +PING
```

### 3. Per-Service Credentials

```
user web-app on >web-pass ~* +@all -CONFIG -FLUSHALL
user queue-worker on >queue-pass ~queue:* ~job:* +@list +@string
user cache on >cache-pass ~cache:* +GET +SET +DEL +EXPIRE
```

---

## Command Security

### 1. Disable Dangerous Commands

```
# redis.conf
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command CONFIG ""
rename-command DEBUG ""
rename-command SHUTDOWN ""
rename-command BGSAVE ""
rename-command BGREWRITEAOF ""
rename-command SLAVEOF ""
rename-command REPLICAOF ""
rename-command SYNC ""
rename-command PSYNC ""
rename-command REPLCONF ""
rename-command MODULE ""
```

### 2. Or Rename to Random Strings

```
rename-command CONFIG "CONFIG_d8a72fb3e4c159"
rename-command FLUSHALL "FLUSHALL_c7e4a9f2b3d158"
```

### 3. ACL Command Restrictions

```
# Block specific commands via ACL
user app on >password ~* +@all -KEYS -FLUSHALL -FLUSHDB -CONFIG -DEBUG
```

---

## Data Security

### 1. Enable TLS

```
# redis.conf
tls-port 6379
port 0
tls-cert-file /etc/redis/tls/redis.crt
tls-key-file /etc/redis/tls/redis.key
tls-ca-cert-file /etc/redis/tls/ca.crt
```

### 2. Encrypt Sensitive Data at Application Level

```php
class SecureCache
{
    private string $key;

    public function __construct()
    {
        $this->key = config('app.key');
    }

    public function set(string $cacheKey, mixed $value): void
    {
        $encrypted = encrypt($value);
        Redis::set($cacheKey, $encrypted);
    }

    public function get(string $cacheKey): mixed
    {
        $encrypted = Redis::get($cacheKey);
        return $encrypted ? decrypt($encrypted) : null;
    }
}
```

### 3. Secure Key Naming

```php
// Don't include sensitive data in key names
// ❌ Bad
Redis::set("user:john.doe@email.com:token", $token);

// ✅ Good
Redis::set("user:{$hashedUserId}:token", $token);
```

---

## Operating System Security

### 1. Run as Non-Root

```bash
# Create redis user
useradd -r -s /bin/false redis

# Set ownership
chown -R redis:redis /var/lib/redis
chown -R redis:redis /etc/redis

# Run as redis user
sudo -u redis redis-server /etc/redis/redis.conf
```

### 2. File Permissions

```bash
chmod 700 /var/lib/redis
chmod 600 /etc/redis/redis.conf
chmod 600 /etc/redis/acl.conf
```

### 3. Disable Transparent Huge Pages

```bash
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```

### 4. Set Resource Limits

```bash
# /etc/security/limits.conf
redis soft nofile 65535
redis hard nofile 65535
```

---

## Logging and Monitoring

### 1. Enable Logging

```
# redis.conf
loglevel notice
logfile /var/log/redis/redis.log
```

### 2. Monitor Auth Failures

```php
class SecurityMonitor
{
    private int $lastRejected = 0;

    public function checkAuthFailures(): ?array
    {
        $stats = Redis::info('stats');
        $rejected = $stats['rejected_connections'];

        $newFailures = $rejected - $this->lastRejected;
        $this->lastRejected = $rejected;

        if ($newFailures > 10) {
            return [
                'alert' => 'high_auth_failures',
                'count' => $newFailures,
            ];
        }

        return null;
    }
}
```

### 3. Monitor ACL Log

```php
Schedule::hourly(function () {
    $log = Redis::command('ACL', ['LOG', 10]);

    foreach ($log as $entry) {
        if ($entry[3] === 'auth') {
            Log::warning('ACL auth failure', [
                'user' => $entry[9],
                'reason' => $entry[5],
            ]);
        }
    }
});
```

### 4. Audit Client Connections

```php
class ClientAuditor
{
    public function audit(array $allowedIps): array
    {
        $clients = Redis::client('LIST');
        $suspicious = [];

        foreach ($this->parseClients($clients) as $client) {
            $ip = explode(':', $client['addr'])[0];
            if (!in_array($ip, $allowedIps)) {
                $suspicious[] = $client;
            }
        }

        return $suspicious;
    }
}
```

---

## Backup Security

### 1. Encrypt Backups

```bash
# Backup with encryption
redis-cli BGSAVE
gpg --symmetric --cipher-algo AES256 /var/lib/redis/dump.rdb

# Restore
gpg --decrypt dump.rdb.gpg > dump.rdb
```

### 2. Secure Backup Transfer

```bash
# Use SCP with key auth
scp -i ~/.ssh/backup_key dump.rdb.gpg backup@remote:/backups/

# Or use encrypted S3
aws s3 cp dump.rdb.gpg s3://bucket/redis-backups/ --sse aws:kms
```

### 3. Backup Access Control

- Separate backup credentials
- Rotate backup encryption keys
- Test restore procedures

---

## Security Checklist

### Infrastructure
- [ ] Redis in private network/VPC
- [ ] Firewall rules configured
- [ ] No public IP on Redis server
- [ ] TLS enabled (if cross-network)

### Authentication
- [ ] Strong password set
- [ ] ACL configured (Redis 6+)
- [ ] Default user disabled
- [ ] Per-service credentials

### Commands
- [ ] FLUSHALL disabled/renamed
- [ ] CONFIG disabled/renamed
- [ ] DEBUG disabled/renamed
- [ ] KEYS disabled (use SCAN)

### Operating System
- [ ] Running as non-root user
- [ ] Restrictive file permissions
- [ ] Resource limits configured
- [ ] Logging enabled

### Monitoring
- [ ] Auth failure alerting
- [ ] ACL log review
- [ ] Client connection auditing
- [ ] Certificate expiry monitoring

### Backups
- [ ] Encrypted backups
- [ ] Secure backup transfer
- [ ] Regular restore testing

---

## Key Takeaways

1. **Defense in depth** - Multiple security layers
2. **Least privilege** - Minimum permissions needed
3. **Network isolation** - Never expose to internet
4. **Strong authentication** - Passwords + ACL
5. **Command restrictions** - Disable dangerous operations
6. **Encryption** - TLS for transit, app-level for sensitive data
7. **Monitoring** - Log and alert on security events
8. **Regular audits** - Review and update security posture
