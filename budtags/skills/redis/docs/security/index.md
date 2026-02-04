# Redis Security

Securing Redis deployments from unauthorized access and attacks.

---

## Overview

| Topic | File | Description |
|-------|------|-------------|
| ACL | [acl.md](./acl.md) | Access Control Lists |
| TLS | [tls.md](./tls.md) | Encryption in transit |
| Best Practices | [best-practices.md](./best-practices.md) | Security hardening |

---

## Security Model

Redis was designed for trusted environments. Security must be added through:

1. **Network isolation** - Firewall, VPC, bind address
2. **Authentication** - Password or ACL
3. **Encryption** - TLS for data in transit
4. **Authorization** - ACL for command/key restrictions

---

## Quick Security Checklist

### Minimum Security

- [ ] Set strong password: `requirepass`
- [ ] Bind to specific interface: `bind 127.0.0.1`
- [ ] Disable dangerous commands: `rename-command`
- [ ] Use firewall rules

### Production Security

- [ ] Enable ACL with per-user permissions
- [ ] Enable TLS encryption
- [ ] Run as non-root user
- [ ] Enable protected mode
- [ ] Audit log access
- [ ] Regular security updates

---

## Basic Authentication

### Password Setup

```
# redis.conf
requirepass your-very-strong-password-here
```

### Laravel Configuration

```php
// config/database.php
'redis' => [
    'default' => [
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', 6379),
        'database' => 0,
    ],
],
```

```env
REDIS_PASSWORD=your-very-strong-password-here
```

---

## Network Security

### Bind to Localhost

```
# redis.conf
bind 127.0.0.1

# Or specific interface
bind 192.168.1.100
```

### Protected Mode

```
# redis.conf (enabled by default)
protected-mode yes
```

Protected mode blocks external connections when:
- No password is set
- Not bound to localhost

### Firewall Rules

```bash
# Allow only from app servers
sudo ufw allow from 192.168.1.0/24 to any port 6379

# Or iptables
iptables -A INPUT -s 192.168.1.0/24 -p tcp --dport 6379 -j ACCEPT
iptables -A INPUT -p tcp --dport 6379 -j DROP
```

---

## Disable Dangerous Commands

### Rename or Disable

```
# redis.conf
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command DEBUG ""
rename-command CONFIG ""
rename-command SHUTDOWN ""
rename-command KEYS ""
rename-command BGSAVE ""
rename-command BGREWRITEAOF ""
rename-command SAVE ""

# Or rename to obscure names
rename-command FLUSHALL "FLUSHALL_49f3a8b2"
```

### Commands to Consider Disabling

| Command | Risk |
|---------|------|
| FLUSHALL/FLUSHDB | Data deletion |
| KEYS | Performance (blocks) |
| CONFIG | Runtime config changes |
| DEBUG | Debug operations |
| SHUTDOWN | Service disruption |
| SLAVEOF/REPLICAOF | Replication changes |
| SCRIPT | Lua script execution |
| EVAL | Lua script execution |

---

## Monitoring

### Failed Auth Attempts

```php
class SecurityMonitor
{
    public function checkAuthFailures(): array
    {
        $info = Redis::info('stats');

        return [
            'rejected_connections' => $info['rejected_connections'],
            'total_connections' => $info['total_connections_received'],
        ];
    }
}

// Alert on many failures
Schedule::everyFiveMinutes(function () {
    static $lastRejected = 0;

    $stats = Redis::info('stats');
    $rejected = $stats['rejected_connections'];

    if ($rejected - $lastRejected > 100) {
        Log::warning('High Redis auth failures', [
            'new_failures' => $rejected - $lastRejected,
        ]);
    }

    $lastRejected = $rejected;
});
```

### Client List Audit

```php
class ClientAuditor
{
    public function getClients(): array
    {
        $clients = Redis::client('LIST');
        return $this->parseClientList($clients);
    }

    public function checkUnknownClients(array $knownIps): array
    {
        $clients = $this->getClients();

        return array_filter($clients, function ($client) use ($knownIps) {
            $ip = explode(':', $client['addr'])[0];
            return !in_array($ip, $knownIps);
        });
    }

    private function parseClientList(string $list): array
    {
        $clients = [];
        foreach (explode("\n", trim($list)) as $line) {
            if (empty($line)) continue;

            $client = [];
            foreach (explode(' ', $line) as $pair) {
                [$key, $value] = explode('=', $pair);
                $client[$key] = $value;
            }
            $clients[] = $client;
        }
        return $clients;
    }
}
```

---

## BudTags Recommendations

### Development

```
# redis.conf
bind 127.0.0.1
requirepass dev-password
protected-mode yes
```

### Production

```
# redis.conf
bind 10.0.0.5
requirepass <strong-random-password>
protected-mode yes

# ACL for specific users
user default off
user app on >app-password ~* +@all
user readonly on >readonly-password ~* +@read

# Disable dangerous commands
rename-command FLUSHALL ""
rename-command CONFIG ""

# TLS (if across networks)
tls-port 6379
port 0
```

---

## Key Takeaways

1. **Never expose to internet** - Always behind firewall
2. **Always use password** - Even in private networks
3. **Bind to specific IP** - Not 0.0.0.0
4. **Use ACL** - Granular permissions (Redis 6+)
5. **Disable dangerous commands** - FLUSHALL, CONFIG, etc.
6. **Enable TLS** - If traffic crosses networks
7. **Monitor failures** - Track rejected connections
8. **Regular updates** - Apply security patches
