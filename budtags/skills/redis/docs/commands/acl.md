# Redis ACL Commands

Access Control Lists (ACLs) control user authentication and command authorization. Available since Redis 6.0.

---

## Overview

| Feature | Details |
|---------|---------|
| **Users** | Named accounts with passwords |
| **Permissions** | Command and key pattern access |
| **Categories** | Groups of related commands |
| **Selectors** | Multiple permission sets per user |

---

## User Management

### ACL LIST

Lists all ACL rules.

```
ACL LIST
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of ACL rule strings |
| **Complexity** | O(N) |

```php
$rules = Redis::acl('LIST');
// ["user default on nopass ~* &* +@all", ...]
```

---

### ACL USERS

Lists all usernames.

```
ACL USERS
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of usernames |
| **Complexity** | O(N) |

---

### ACL GETUSER

Gets user ACL details.

```
ACL GETUSER username
```

| Aspect | Details |
|--------|---------|
| **Returns** | User configuration array |
| **Complexity** | O(N) |

```php
$user = Redis::acl('GETUSER', 'appuser');
// Returns flags, passwords, commands, keys, channels info
```

---

### ACL SETUSER

Creates or modifies a user.

```
ACL SETUSER username [rule ...]
```

| Rule | Description |
|------|-------------|
| `on` | Enable user |
| `off` | Disable user |
| `>password` | Add password |
| `<password` | Remove password |
| `#hash` | Add SHA256 password hash |
| `nopass` | Allow passwordless auth |
| `resetpass` | Remove all passwords |
| `~pattern` | Allow key patterns |
| `%R~pattern` | Read-only key pattern |
| `%W~pattern` | Write-only key pattern |
| `&pattern` | Allow pub/sub channel pattern |
| `+command` | Allow command |
| `-command` | Deny command |
| `+@category` | Allow command category |
| `-@category` | Deny command category |
| `allcommands` | Allow all commands |
| `nocommands` | Deny all commands |
| `allkeys` | Allow all keys |
| `resetkeys` | Remove key permissions |
| `allchannels` | Allow all pub/sub channels |
| `resetchannels` | Remove channel permissions |
| `reset` | Reset user to defaults |

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(N) |

```php
// Create read-only app user
Redis::acl('SETUSER', 'readonly',
    'on',                    // Enable
    '>secretpass123',        // Set password
    '~cache:*',              // Only cache: keys
    '+get', '+mget',         // Only GET commands
    '-@dangerous'            // No dangerous commands
);

// Create full-access app user
Redis::acl('SETUSER', 'appuser',
    'on',
    '>apppassword',
    '~*',                    // All keys
    '+@all',                 // All commands
    '-@admin',               // Except admin
    '-@dangerous'            // And dangerous
);
```

---

### ACL DELUSER

Deletes users.

```
ACL DELUSER username [username ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number deleted |
| **Complexity** | O(N) |

---

### ACL WHOAMI

Returns current authenticated user.

```
ACL WHOAMI
```

| Aspect | Details |
|--------|---------|
| **Returns** | Username string |
| **Complexity** | O(1) |

---

## Authentication

### AUTH

Authenticates the connection.

```
AUTH [username] password
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Error** | WRONGPASS if invalid |

```php
// Password only (default user)
Redis::auth('mypassword');

// Username and password
Redis::auth('appuser', 'apppassword');
```

---

## Command Categories

### ACL CAT

Lists command categories or commands in a category.

```
ACL CAT [category]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of categories or commands |
| **Complexity** | O(N) |

```php
// List all categories
$categories = Redis::acl('CAT');
// ["read", "write", "set", "sortedset", "list", "hash", "string", ...]

// List commands in category
$writeCommands = Redis::acl('CAT', 'write');
// ["set", "lpush", "hset", "zadd", ...]
```

Common categories:
- `@read` - Read operations
- `@write` - Write operations
- `@admin` - Administrative commands
- `@dangerous` - Potentially harmful commands
- `@slow` - Slow commands
- `@fast` - Fast commands
- `@pubsub` - Pub/Sub commands
- `@transaction` - Transaction commands
- `@scripting` - Script commands

---

## Persistence

### ACL LOAD

Reloads ACL from file.

```
ACL LOAD
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **File** | Configured with `aclfile` directive |

---

### ACL SAVE

Saves ACL to file.

```
ACL SAVE
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **File** | Configured with `aclfile` directive |

---

## Logging

### ACL LOG

Shows security events.

```
ACL LOG [count | RESET]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of security events |
| **Events** | Command denied, key denied, auth failed |

```php
// Get recent ACL violations
$log = Redis::acl('LOG', 10);

// Clear log
Redis::acl('LOG', 'RESET');
```

---

## Utilities

### ACL GENPASS

Generates a secure password.

```
ACL GENPASS [bits]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Random hex string |
| **Default** | 256 bits (64 hex characters) |

```php
$password = Redis::acl('GENPASS');
// "a3f2c1e8d9b4..."

$shortPass = Redis::acl('GENPASS', 128);
// 32 hex characters
```

---

### ACL DRYRUN

Tests if a command would be allowed.

```
ACL DRYRUN username command [arg ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK if allowed |
| **Since** | Redis 7.0 |

```php
$result = Redis::acl('DRYRUN', 'readonly', 'SET', 'key', 'value');
// Error if not allowed, OK if allowed
```

---

## Configuration Examples

### Read-Only User

```php
Redis::acl('SETUSER', 'reader',
    'on',
    '>readerpass',
    '~*',                    // All keys
    '+@read',                // Read commands
    '-@dangerous'
);
```

### Write-Only User (Specific Keys)

```php
Redis::acl('SETUSER', 'writer',
    'on',
    '>writerpass',
    '~logs:*',               // Only logs: keys
    '~events:*',             // And events: keys
    '+@write',               // Write commands
    '+@read',                // Need read for some ops
    '-del', '-flushdb'       // But no deletion
);
```

### Application User (Cache Only)

```php
Redis::acl('SETUSER', 'cacheuser',
    'on',
    '>cachepass',
    '~cache:*',              // Cache keys only
    '+get', '+set', '+del',  // Basic ops
    '+expire', '+ttl',       // TTL management
    '+exists', '+type'       // Info commands
);
```

### Pub/Sub Only User

```php
Redis::acl('SETUSER', 'pubsubuser',
    'on',
    '>pubsubpass',
    '&events:*',             // Only events: channels
    '+subscribe', '+unsubscribe',
    '+publish', '+psubscribe',
    '+punsubscribe'
);
```

---

## Default User

The `default` user is used when:
- No username specified in AUTH
- No `requirepass` set (then default is `nopass`)

```php
// Configure default user
Redis::acl('SETUSER', 'default',
    'on',
    '>defaultpassword',
    '~*',
    '+@all',
    '-@admin'
);
```

---

## Security Best Practices

1. **Disable default user** in production
   ```php
   Redis::acl('SETUSER', 'default', 'off');
   ```

2. **Use unique passwords** per user
   ```php
   $pass = Redis::acl('GENPASS', 256);
   Redis::acl('SETUSER', 'appuser', ">$pass");
   ```

3. **Minimal permissions** - only what's needed
   ```php
   // Instead of +@all, be specific
   Redis::acl('SETUSER', 'user', '+get', '+set', '+del');
   ```

4. **Key pattern restrictions**
   ```php
   // Restrict to app namespace
   Redis::acl('SETUSER', 'user', '~app:*');
   ```

5. **Monitor ACL log**
   ```php
   // Check for violations periodically
   $violations = Redis::acl('LOG');
   ```

6. **Persist ACL changes**
   ```php
   Redis::acl('SAVE');
   ```

---

## Laravel Integration

```php
// config/database.php
'redis' => [
    'client' => env('REDIS_CLIENT', 'phpredis'),
    'default' => [
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'username' => env('REDIS_USERNAME', null),
        'password' => env('REDIS_PASSWORD', null),
        'port' => env('REDIS_PORT', '6379'),
        'database' => env('REDIS_DB', '0'),
    ],
],

// .env
REDIS_USERNAME=appuser
REDIS_PASSWORD=securepassword
```

---

## Performance Notes

| Command | Complexity | Notes |
|---------|------------|-------|
| ACL LIST | O(N) | N = users |
| ACL GETUSER | O(N) | N = rules |
| ACL SETUSER | O(N) | N = rules |
| AUTH | O(N) | N = passwords to check |
| ACL LOG | O(N) | N = entries |

ACL checks add minimal overhead to command execution.
