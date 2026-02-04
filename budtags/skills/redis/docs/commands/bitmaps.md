# Redis Bitmap Commands

Bitmaps are not a separate data type - they're operations on strings that treat them as arrays of bits. Extremely memory-efficient for binary state tracking.

---

## Overview

| Feature | Details |
|---------|---------|
| **Storage** | 1 bit per position |
| **Max size** | 512 MB string = 2^32 bits |
| **Memory** | 100M bits = 12.5 MB |
| **Use case** | Binary state tracking (online, flags, presence) |

---

## Bit Operations

### SETBIT

Sets or clears a bit at offset.

```
SETBIT key offset value
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - original bit value (0 or 1) |
| **Complexity** | O(1) |
| **Creates** | Key if doesn't exist |
| **Expands** | String automatically if offset > length |

```php
// Track user login (offset = user_id)
Redis::setbit('logins:2024-01-15', 123, 1);  // User 123 logged in
Redis::setbit('logins:2024-01-15', 456, 1);  // User 456 logged in

// Clear bit
Redis::setbit('logins:2024-01-15', 123, 0);  // User 123 logged out
```

---

### GETBIT

Returns the bit value at offset.

```
GETBIT key offset
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - 0 or 1 |
| **Complexity** | O(1) |
| **Default** | 0 for non-existent key or offset beyond length |

```php
// Check if user logged in today
$loggedIn = Redis::getbit('logins:2024-01-15', $userId);
```

---

### BITCOUNT

Counts set bits (1s) in a string.

```
BITCOUNT key [start end [BYTE|BIT]]
```

| Option | Description |
|--------|-------------|
| `start end` | Byte range (default) or bit range |
| `BYTE` | Range is in bytes (default) |
| `BIT` | Range is in bits (Redis 7.0+) |

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - count of 1 bits |
| **Complexity** | O(N) |

```php
// Count unique logins today
$uniqueLogins = Redis::bitcount('logins:2024-01-15');

// Count bits in byte range
$partial = Redis::bitcount('logins:2024-01-15', 0, 100);  // First 101 bytes

// Count bits in bit range (Redis 7.0+)
$bitRange = Redis::bitcount('logins:2024-01-15', 0, 999, 'BIT');
```

---

### BITPOS

Finds first bit with specified value.

```
BITPOS key bit [start [end [BYTE|BIT]]]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - position, or -1 if not found |
| **Complexity** | O(N) |

```php
// Find first user who logged in (first 1 bit)
$firstUser = Redis::bitpos('logins:2024-01-15', 1);

// Find first inactive user (first 0 bit)
$firstInactive = Redis::bitpos('logins:2024-01-15', 0);
```

---

## Bitwise Operations

### BITOP

Performs bitwise operations between strings.

```
BITOP operation destkey key [key ...]
```

| Operation | Description |
|-----------|-------------|
| `AND` | Intersection - bits set in ALL keys |
| `OR` | Union - bits set in ANY key |
| `XOR` | Exclusive or - bits set in odd number of keys |
| `NOT` | Negation - inverts all bits (single key) |

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - size of resulting string |
| **Complexity** | O(N) |

```php
// Users logged in BOTH days
Redis::bitop('AND', 'logins:both', 'logins:2024-01-15', 'logins:2024-01-16');
$bothDays = Redis::bitcount('logins:both');

// Users logged in EITHER day
Redis::bitop('OR', 'logins:either', 'logins:2024-01-15', 'logins:2024-01-16');
$eitherDay = Redis::bitcount('logins:either');

// Users logged in ONLY one day (not both)
Redis::bitop('XOR', 'logins:onlyone', 'logins:2024-01-15', 'logins:2024-01-16');

// Invert bitmap
Redis::bitop('NOT', 'logins:not', 'logins:2024-01-15');
```

---

## Bitfield Operations

### BITFIELD

Performs arbitrary bitfield integer operations.

```
BITFIELD key [GET type offset] [SET type offset value] [INCRBY type offset increment] [OVERFLOW WRAP|SAT|FAIL]
```

| Type | Description |
|------|-------------|
| `u8` | Unsigned 8-bit integer |
| `i8` | Signed 8-bit integer |
| `u16` | Unsigned 16-bit integer |
| `i32` | Signed 32-bit integer |
| `u63` | Max unsigned (63 bits) |
| `i64` | Max signed (64 bits) |

| Overflow | Description |
|----------|-------------|
| `WRAP` | Wrap around (default) |
| `SAT` | Saturate at min/max |
| `FAIL` | Return nil on overflow |

| Aspect | Details |
|--------|---------|
| **Returns** | Array of operation results |
| **Complexity** | O(1) per subcommand |

```php
// Store multiple counters in single key
// Counter 1: offset 0, 16 bits
// Counter 2: offset 16, 16 bits
Redis::bitfield('counters',
    'SET', 'u16', 0, 100,      // Set counter 1 to 100
    'SET', 'u16', 16, 200      // Set counter 2 to 200
);

// Increment counters
Redis::bitfield('counters',
    'INCRBY', 'u16', 0, 1,     // Increment counter 1
    'INCRBY', 'u16', 16, 5     // Increment counter 2 by 5
);

// Get counters
$values = Redis::bitfield('counters',
    'GET', 'u16', 0,           // Get counter 1
    'GET', 'u16', 16           // Get counter 2
);

// With overflow handling
Redis::bitfield('counters',
    'OVERFLOW', 'SAT',         // Saturate on overflow
    'INCRBY', 'u8', 0, 100     // Won't exceed 255
);
```

---

### BITFIELD_RO

Read-only version of BITFIELD.

```
BITFIELD_RO key [GET type offset ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of values |
| **Since** | Redis 6.0 |

Can run on replicas.

---

## Use Cases

### Daily Active Users

```php
class DailyActiveUsers
{
    public function markActive(int $userId): void
    {
        $today = date('Y-m-d');
        Redis::setbit("dau:{$today}", $userId, 1);
    }

    public function isActive(int $userId, string $date): bool
    {
        return Redis::getbit("dau:{$date}", $userId) === 1;
    }

    public function countActive(string $date): int
    {
        return Redis::bitcount("dau:{$date}");
    }

    public function countActiveRange(string $startDate, string $endDate): int
    {
        $keys = $this->getDateKeys($startDate, $endDate);
        Redis::bitop('OR', 'dau:range', ...$keys);
        return Redis::bitcount('dau:range');
    }

    public function getRetention(string $day1, string $day2): array
    {
        // Users active on both days
        Redis::bitop('AND', 'retention:both', "dau:{$day1}", "dau:{$day2}");
        $both = Redis::bitcount('retention:both');
        $day1Count = Redis::bitcount("dau:{$day1}");

        return [
            'day1_users' => $day1Count,
            'retained' => $both,
            'retention_rate' => $day1Count > 0 ? ($both / $day1Count) * 100 : 0
        ];
    }
}
```

### Feature Flags

```php
class FeatureFlags
{
    private string $key = 'features:enabled';

    // Feature IDs as bit offsets
    const DARK_MODE = 0;
    const BETA_UI = 1;
    const NEW_CHECKOUT = 2;
    const AI_SUGGESTIONS = 3;

    public function enableFeature(int $featureId): void
    {
        Redis::setbit($this->key, $featureId, 1);
    }

    public function disableFeature(int $featureId): void
    {
        Redis::setbit($this->key, $featureId, 0);
    }

    public function isEnabled(int $featureId): bool
    {
        return Redis::getbit($this->key, $featureId) === 1;
    }

    public function getEnabledCount(): int
    {
        return Redis::bitcount($this->key);
    }
}
```

### User Permissions

```php
class UserPermissions
{
    const READ = 0;
    const WRITE = 1;
    const DELETE = 2;
    const ADMIN = 3;

    public function setPermission(int $userId, int $permission): void
    {
        Redis::setbit("permissions:{$userId}", $permission, 1);
    }

    public function revokePermission(int $userId, int $permission): void
    {
        Redis::setbit("permissions:{$userId}", $permission, 0);
    }

    public function hasPermission(int $userId, int $permission): bool
    {
        return Redis::getbit("permissions:{$userId}", $permission) === 1;
    }

    public function hasAllPermissions(int $userId, array $permissions): bool
    {
        foreach ($permissions as $perm) {
            if (!$this->hasPermission($userId, $perm)) {
                return false;
            }
        }
        return true;
    }
}
```

### Bloom Filter Simulation

```php
class SimpleBloomFilter
{
    private string $key;
    private int $size;
    private int $hashCount;

    public function __construct(string $name, int $size = 1000000, int $hashCount = 3)
    {
        $this->key = "bloom:{$name}";
        $this->size = $size;
        $this->hashCount = $hashCount;
    }

    public function add(string $item): void
    {
        for ($i = 0; $i < $this->hashCount; $i++) {
            $hash = $this->hash($item, $i) % $this->size;
            Redis::setbit($this->key, $hash, 1);
        }
    }

    public function mightContain(string $item): bool
    {
        for ($i = 0; $i < $this->hashCount; $i++) {
            $hash = $this->hash($item, $i) % $this->size;
            if (Redis::getbit($this->key, $hash) === 0) {
                return false;  // Definitely not in set
            }
        }
        return true;  // Probably in set
    }

    private function hash(string $item, int $seed): int
    {
        return abs(crc32($item . $seed));
    }
}
```

---

## Memory Efficiency

| Users | Bitmap Size | Set Size |
|-------|-------------|----------|
| 1M | 125 KB | ~56 MB |
| 10M | 1.25 MB | ~560 MB |
| 100M | 12.5 MB | ~5.6 GB |

Bitmaps use **~450x less memory** than sets for binary state.

---

## Performance Notes

| Command | Complexity | Notes |
|---------|------------|-------|
| SETBIT | O(1) | Constant time |
| GETBIT | O(1) | Constant time |
| BITCOUNT | O(N) | N = string length |
| BITOP | O(N) | N = longest string |
| BITPOS | O(N) | Stops at first match |
| BITFIELD | O(1) | Per subcommand |

**Best Practices:**
- Use integer IDs as offsets (not UUIDs)
- Partition by time for efficient expiration
- Use BITOP for set operations
- Consider sparse bitmaps for very large ID spaces
- Use BITFIELD for multiple small counters
