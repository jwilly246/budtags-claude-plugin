# Redis ACL (Access Control Lists)

Fine-grained user permissions introduced in Redis 6.

---

## Overview

ACL provides:
- Multiple users with individual passwords
- Command restrictions per user
- Key pattern restrictions per user
- Channel restrictions (Pub/Sub)

---

## User Syntax

```
user <username> [on|off] [><password>] [~<key-pattern>] [+<command>|-<command>] [+@<category>|-@<category>]
```

| Component | Description |
|-----------|-------------|
| `on/off` | Enable/disable user |
| `>password` | Add password |
| `<password` | Remove password |
| `nopass` | Allow login without password |
| `~pattern` | Allow key patterns |
| `%R~pattern` | Read-only key access |
| `%W~pattern` | Write-only key access |
| `+command` | Allow command |
| `-command` | Deny command |
| `+@category` | Allow command category |
| `-@category` | Deny command category |
| `allcommands` | Allow all commands |
| `nocommands` | Deny all commands |
| `allkeys` | Allow all keys |
| `resetkeys` | Clear all key patterns |
| `&channel` | Allow Pub/Sub channel |

---

## Command Categories

| Category | Commands |
|----------|----------|
| `@read` | GET, HGET, LRANGE, etc. |
| `@write` | SET, HSET, LPUSH, etc. |
| `@admin` | CONFIG, DEBUG, etc. |
| `@dangerous` | FLUSHALL, KEYS, etc. |
| `@fast` | O(1) commands |
| `@slow` | O(N) commands |
| `@pubsub` | PUBLISH, SUBSCRIBE |
| `@transaction` | MULTI, EXEC |
| `@scripting` | EVAL, SCRIPT |

List all categories:
```bash
redis-cli ACL CAT
```

---

## Configuration

### In redis.conf

```
# Disable default user
user default off

# Application user with full access
user app on >strong-password ~* +@all

# Read-only user for monitoring
user monitor on >monitor-pass ~* +@read +INFO +CLIENT

# Limited user for specific prefix
user reports on >reports-pass ~reports:* +@read +@write

# Admin user
user admin on >admin-pass ~* +@all
```

### In ACL File

```
# acl.conf
user default off
user app on >strong-password ~* +@all
user monitor on >monitor-pass ~* +@read +INFO
```

```
# redis.conf
aclfile /etc/redis/acl.conf
```

---

## ACL Commands

### User Management

```bash
# Create/modify user
redis-cli ACL SETUSER myuser on >password ~* +@all

# List users
redis-cli ACL LIST

# Get user details
redis-cli ACL GETUSER myuser

# Delete user
redis-cli ACL DELUSER myuser

# Current user
redis-cli ACL WHOAMI
```

### Authentication

```php
// Authenticate as specific user
Redis::auth(['username', 'password']);

// Or in connection config
'redis' => [
    'default' => [
        'host' => env('REDIS_HOST'),
        'username' => env('REDIS_USERNAME'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', 6379),
    ],
],
```

---

## Common User Patterns

### Application User

```bash
ACL SETUSER app on >app-secret-password \
  ~* \
  +@all \
  -@admin \
  -@dangerous
```

### Read-Only User

```bash
ACL SETUSER readonly on >readonly-password \
  ~* \
  +@read \
  +PING \
  +INFO
```

### Cache-Only User

```bash
ACL SETUSER cache on >cache-password \
  ~cache:* \
  +GET +SET +DEL +EXISTS +EXPIRE +TTL \
  +MGET +MSET \
  +PING
```

### Queue Worker User

```bash
ACL SETUSER worker on >worker-password \
  ~queue:* ~job:* \
  +LPUSH +RPUSH +LPOP +RPOP +BLPOP +BRPOP \
  +LLEN +LRANGE \
  +PING
```

### Pub/Sub Only User

```bash
ACL SETUSER pubsub on >pubsub-password \
  &* \
  +SUBSCRIBE +UNSUBSCRIBE +PSUBSCRIBE +PUNSUBSCRIBE \
  +PUBLISH \
  +PING
```

### Session User (Read/Write specific keys)

```bash
ACL SETUSER session on >session-password \
  ~session:* \
  +GET +SET +DEL +EXISTS +EXPIRE +TTL \
  +PING
```

---

## Laravel Multi-User Configuration

```php
// config/database.php
'redis' => [
    'client' => 'phpredis',

    // Main application
    'default' => [
        'host' => env('REDIS_HOST'),
        'username' => env('REDIS_USERNAME', 'app'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', 6379),
        'database' => 0,
    ],

    // Read-only for dashboards
    'read' => [
        'host' => env('REDIS_HOST'),
        'username' => 'readonly',
        'password' => env('REDIS_READONLY_PASSWORD'),
        'port' => env('REDIS_PORT', 6379),
        'database' => 0,
    ],

    // Queue workers
    'queue' => [
        'host' => env('REDIS_HOST'),
        'username' => 'worker',
        'password' => env('REDIS_WORKER_PASSWORD'),
        'port' => env('REDIS_PORT', 6379),
        'database' => 0,
    ],
],
```

---

## Monitoring ACL

### Audit Log

```bash
# Enable ACL log
redis-cli CONFIG SET acllog-max-len 128
```

```php
class AclAuditor
{
    public function getLog(int $count = 10): array
    {
        $log = Redis::command('ACL', ['LOG', $count]);

        return array_map(function ($entry) {
            return [
                'count' => $entry[1],
                'reason' => $entry[3],
                'context' => $entry[5],
                'object' => $entry[7],
                'username' => $entry[9],
                'age_seconds' => $entry[11],
                'client_info' => $entry[13],
            ];
        }, $log);
    }

    public function clearLog(): void
    {
        Redis::command('ACL', ['LOG', 'RESET']);
    }
}
```

### Check Permissions

```php
class PermissionChecker
{
    public function canExecute(string $user, string $command, string $key = null): bool
    {
        $userInfo = Redis::command('ACL', ['GETUSER', $user]);

        if (!$userInfo) {
            return false;
        }

        // Parse user info and check permissions
        // This is simplified - full implementation would parse rules
        return true;
    }
}
```

---

## Security Best Practices

### 1. Disable Default User

```
user default off
```

### 2. Use Strong Passwords

```php
// Generate strong password
$password = bin2hex(random_bytes(32));
```

### 3. Principle of Least Privilege

```bash
# Only grant needed permissions
ACL SETUSER myapp on >password \
  ~myapp:* \
  +@read +@write \
  -KEYS -SCAN  # Deny expensive operations
```

### 4. Separate Users per Component

```
# Different passwords for different components
user web-app on >web-password ~* +@all -@admin
user queue-worker on >queue-password ~queue:* +@list +@string
user cache-service on >cache-password ~cache:* +GET +SET +DEL
```

### 5. Regular Password Rotation

```php
// Rotate password
Redis::command('ACL', ['SETUSER', 'myuser', ">{$newPassword}"]);
Redis::command('ACL', ['SETUSER', 'myuser', "<{$oldPassword}"]);
```

---

## Key Takeaways

1. **Disable default user** - Create specific users
2. **Use categories** - `+@read`, `+@write` vs. individual commands
3. **Key patterns** - Restrict access by key prefix
4. **Least privilege** - Only grant what's needed
5. **Separate users** - Per component/service
6. **Monitor ACL log** - Catch permission violations
7. **Strong passwords** - Random, long passwords
8. **Persist ACL** - Use aclfile for configuration as code
