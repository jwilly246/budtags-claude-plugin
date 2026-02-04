# Redis Bitmaps & Bitfields - Deep Dive

Bitmaps and bitfields enable compact storage and manipulation of binary data and small integers.

---

## Bitmaps

### Concept

Bitmaps are not a separate data type - they're string values treated as bit arrays. Each bit can be 0 or 1.

**Memory:** 1 bit per flag = 8 flags per byte
- 1 million flags = 125 KB
- 1 billion flags = 125 MB

### Core Commands

```php
// Set bit at position
Redis::setbit('users:active', 1000, 1);  // User 1000 is active
Redis::setbit('users:active', 1001, 0);  // User 1001 is not active

// Get bit at position
$isActive = Redis::getbit('users:active', 1000);  // Returns 1 or 0

// Count set bits
$activeCount = Redis::bitcount('users:active');

// Count bits in range (byte range, not bit range)
$count = Redis::bitcount('users:active', 0, 100);  // Bytes 0-100
```

### Bitwise Operations

```php
// AND - Users active on BOTH days
Redis::bitop('AND', 'active:both', 'active:day1', 'active:day2');

// OR - Users active on EITHER day
Redis::bitop('OR', 'active:either', 'active:day1', 'active:day2');

// XOR - Users active on exactly one day
Redis::bitop('XOR', 'active:one', 'active:day1', 'active:day2');

// NOT - Invert bits
Redis::bitop('NOT', 'inactive:day1', 'active:day1');
```

### Bit Position Search

```php
// Find first set bit (1)
$firstActive = Redis::bitpos('users:active', 1);

// Find first unset bit (0)
$firstInactive = Redis::bitpos('users:active', 0);

// Search within byte range
$pos = Redis::bitpos('users:active', 1, 100, 200);  // Bytes 100-200
```

---

## Bitmap Use Cases

### 1. Daily Active Users

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
        return (bool) Redis::getbit("dau:{$date}", $userId);
    }

    public function countActive(string $date): int
    {
        return Redis::bitcount("dau:{$date}");
    }

    public function getActiveOnBothDays(string $date1, string $date2): int
    {
        $resultKey = "dau:both:{$date1}:{$date2}";

        Redis::bitop('AND', $resultKey, "dau:{$date1}", "dau:{$date2}");
        $count = Redis::bitcount($resultKey);
        Redis::del($resultKey);

        return $count;
    }

    public function getActiveOnAnyDay(array $dates): int
    {
        $keys = array_map(fn($d) => "dau:{$d}", $dates);
        $resultKey = 'dau:any:' . md5(implode(',', $dates));

        Redis::bitop('OR', $resultKey, ...$keys);
        $count = Redis::bitcount($resultKey);
        Redis::del($resultKey);

        return $count;
    }

    public function getRetention(string $date1, string $date2): float
    {
        $day1Count = Redis::bitcount("dau:{$date1}");

        if ($day1Count === 0) {
            return 0;
        }

        $bothDays = $this->getActiveOnBothDays($date1, $date2);

        return round(($bothDays / $day1Count) * 100, 2);
    }
}
```

### 2. Feature Flags

```php
class FeatureFlags
{
    private const FEATURES = [
        'dark_mode' => 0,
        'beta_ui' => 1,
        'new_dashboard' => 2,
        'export_v2' => 3,
    ];

    public function enableFeature(int $userId, string $feature): void
    {
        $bit = self::FEATURES[$feature] ?? throw new \InvalidArgumentException("Unknown feature");
        Redis::setbit("features:{$userId}", $bit, 1);
    }

    public function disableFeature(int $userId, string $feature): void
    {
        $bit = self::FEATURES[$feature] ?? throw new \InvalidArgumentException("Unknown feature");
        Redis::setbit("features:{$userId}", $bit, 0);
    }

    public function hasFeature(int $userId, string $feature): bool
    {
        $bit = self::FEATURES[$feature] ?? throw new \InvalidArgumentException("Unknown feature");
        return (bool) Redis::getbit("features:{$userId}", $bit);
    }

    public function getEnabledFeatures(int $userId): array
    {
        $enabled = [];

        foreach (self::FEATURES as $feature => $bit) {
            if (Redis::getbit("features:{$userId}", $bit)) {
                $enabled[] = $feature;
            }
        }

        return $enabled;
    }
}
```

### 3. Online Status Tracking

```php
class OnlineStatus
{
    public function setOnline(int $userId): void
    {
        $minute = floor(time() / 60);
        Redis::setbit("online:{$minute}", $userId, 1);
    }

    public function getOnlineCount(): int
    {
        $minute = floor(time() / 60);
        return Redis::bitcount("online:{$minute}");
    }

    public function getOnlineInLastMinutes(int $minutes = 5): int
    {
        $currentMinute = floor(time() / 60);
        $keys = [];

        for ($i = 0; $i < $minutes; $i++) {
            $keys[] = "online:" . ($currentMinute - $i);
        }

        $resultKey = 'online:recent:' . $currentMinute;
        Redis::bitop('OR', $resultKey, ...$keys);
        $count = Redis::bitcount($resultKey);
        Redis::del($resultKey);

        return $count;
    }
}
```

---

## Bitfields

### Concept

Bitfields allow storing multiple integers within a single string, with configurable bit widths per field.

```php
// Types: i (signed), u (unsigned)
// u8 = unsigned 8-bit (0-255)
// i16 = signed 16-bit (-32768 to 32767)
// u32 = unsigned 32-bit (0 to 4,294,967,295)
```

### Core Commands

```php
// Set values at bit offsets
Redis::bitfield('stats', 'SET', 'u8', 0, 100);    // First byte: 100
Redis::bitfield('stats', 'SET', 'u16', 8, 5000);  // Next 2 bytes: 5000

// Get values
$values = Redis::bitfield('stats', 'GET', 'u8', 0, 'GET', 'u16', 8);

// Increment with overflow handling
Redis::bitfield('counter', 'OVERFLOW', 'WRAP', 'INCRBY', 'u8', 0, 1);
Redis::bitfield('counter', 'OVERFLOW', 'SAT', 'INCRBY', 'u8', 0, 1);   // Saturate at max
Redis::bitfield('counter', 'OVERFLOW', 'FAIL', 'INCRBY', 'u8', 0, 1);  // Fail if overflow
```

### Overflow Behaviors

| Behavior | Description |
|----------|-------------|
| WRAP | Wraps around (255 + 1 = 0 for u8) |
| SAT | Saturates at min/max (255 + 1 = 255 for u8) |
| FAIL | Returns nil, doesn't change value |

---

## Bitfield Use Cases

### 1. Compact Counters

```php
class CompactCounters
{
    // Store multiple small counters in one key
    // Layout: [views:u16][likes:u16][shares:u16][comments:u16]

    private const FIELDS = [
        'views' => ['type' => 'u16', 'offset' => 0],
        'likes' => ['type' => 'u16', 'offset' => 16],
        'shares' => ['type' => 'u16', 'offset' => 32],
        'comments' => ['type' => 'u16', 'offset' => 48],
    ];

    public function increment(string $itemId, string $field, int $amount = 1): int
    {
        $config = self::FIELDS[$field] ?? throw new \InvalidArgumentException();

        $result = Redis::bitfield(
            "counters:{$itemId}",
            'OVERFLOW', 'SAT',
            'INCRBY', $config['type'], $config['offset'], $amount
        );

        return $result[0];
    }

    public function getAll(string $itemId): array
    {
        $args = [];
        foreach (self::FIELDS as $field => $config) {
            $args[] = 'GET';
            $args[] = $config['type'];
            $args[] = $config['offset'];
        }

        $values = Redis::bitfield("counters:{$itemId}", ...$args);

        return array_combine(array_keys(self::FIELDS), $values);
    }

    public function get(string $itemId, string $field): int
    {
        $config = self::FIELDS[$field] ?? throw new \InvalidArgumentException();

        $result = Redis::bitfield(
            "counters:{$itemId}",
            'GET', $config['type'], $config['offset']
        );

        return $result[0] ?? 0;
    }
}
```

### 2. Time-Series Buckets

```php
class HourlyStats
{
    // Store 24 hours of stats in one key
    // Each hour is a u16 (max 65535)

    public function increment(string $metric, int $hour, int $amount = 1): int
    {
        $offset = $hour * 16;  // 16 bits per hour

        $result = Redis::bitfield(
            "hourly:{$metric}:" . date('Y-m-d'),
            'OVERFLOW', 'SAT',
            'INCRBY', 'u16', $offset, $amount
        );

        return $result[0];
    }

    public function getHour(string $metric, string $date, int $hour): int
    {
        $offset = $hour * 16;

        $result = Redis::bitfield(
            "hourly:{$metric}:{$date}",
            'GET', 'u16', $offset
        );

        return $result[0] ?? 0;
    }

    public function getDay(string $metric, string $date): array
    {
        $args = [];
        for ($hour = 0; $hour < 24; $hour++) {
            $args[] = 'GET';
            $args[] = 'u16';
            $args[] = $hour * 16;
        }

        $values = Redis::bitfield("hourly:{$metric}:{$date}", ...$args);

        return array_combine(range(0, 23), $values ?? array_fill(0, 24, 0));
    }
}
```

### 3. Permission Bits

```php
class PermissionManager
{
    // 32-bit permission field per user-resource pair
    private const PERMISSIONS = [
        'read' => 0,
        'write' => 1,
        'delete' => 2,
        'admin' => 3,
        'share' => 4,
    ];

    public function grant(int $userId, string $resource, string $permission): void
    {
        $bit = self::PERMISSIONS[$permission] ?? throw new \InvalidArgumentException();
        Redis::setbit("perms:{$userId}:{$resource}", $bit, 1);
    }

    public function revoke(int $userId, string $resource, string $permission): void
    {
        $bit = self::PERMISSIONS[$permission] ?? throw new \InvalidArgumentException();
        Redis::setbit("perms:{$userId}:{$resource}", $bit, 0);
    }

    public function has(int $userId, string $resource, string $permission): bool
    {
        $bit = self::PERMISSIONS[$permission] ?? throw new \InvalidArgumentException();
        return (bool) Redis::getbit("perms:{$userId}:{$resource}", $bit);
    }

    public function getAll(int $userId, string $resource): array
    {
        $result = [];

        foreach (self::PERMISSIONS as $perm => $bit) {
            $result[$perm] = (bool) Redis::getbit("perms:{$userId}:{$resource}", $bit);
        }

        return $result;
    }
}
```

---

## Memory Comparison

Tracking 1 million users' daily activity:

| Method | Memory |
|--------|--------|
| **Set of user IDs** | ~8-16 MB |
| **Hash** | ~16-32 MB |
| **Bitmap** | 125 KB |

**Savings:** 100-200x less memory

---

## Performance Characteristics

| Command | Complexity |
|---------|------------|
| SETBIT | O(1) |
| GETBIT | O(1) |
| BITCOUNT | O(N) where N = byte length |
| BITOP | O(N) where N = longest string |
| BITPOS | O(N) |
| BITFIELD | O(1) per operation |

---

## BudTags Usage Opportunities

### Package Processing Flags

```php
class PackageFlags
{
    // Track which packages have been processed for a sync
    public function markProcessed(string $syncId, int $packageIndex): void
    {
        Redis::setbit("sync:{$syncId}:processed", $packageIndex, 1);
    }

    public function isProcessed(string $syncId, int $packageIndex): bool
    {
        return (bool) Redis::getbit("sync:{$syncId}:processed", $packageIndex);
    }

    public function countProcessed(string $syncId): int
    {
        return Redis::bitcount("sync:{$syncId}:processed");
    }
}
```

### Daily User Actions

```php
class UserActionTracker
{
    public function trackLogin(int $userId): void
    {
        Redis::setbit("logins:" . date('Y-m-d'), $userId, 1);
    }

    public function getLoginCount(string $date): int
    {
        return Redis::bitcount("logins:{$date}");
    }
}
```

---

## Key Takeaways

### Bitmaps
1. **Extremely compact** - 1 bit per flag
2. **O(1) bit operations** - SETBIT, GETBIT
3. **Bitwise operations** - AND, OR, XOR, NOT
4. **Perfect for flags** - Active users, feature flags
5. **ID must be integer** - Use as array index

### Bitfields
1. **Multiple integers** - In single key
2. **Configurable widths** - u8, u16, u32, i8, etc.
3. **Overflow control** - WRAP, SAT, FAIL
4. **Atomic operations** - Multiple fields in one call
5. **Compact counters** - Multiple small counters per key
