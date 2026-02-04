# Redis Geospatial Commands

Geospatial commands store and query locations using longitude/latitude coordinates. Internally uses sorted sets with geohash-encoded scores.

---

## Adding Locations

### GEOADD

Adds geographic locations to a key.

```
GEOADD key [NX|XX] [CH] longitude latitude member [longitude latitude member ...]
```

| Option | Description |
|--------|-------------|
| `NX` | Only add new members (don't update existing) |
| `XX` | Only update existing members (don't add new) |
| `CH` | Return changed count instead of added count |

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of elements added |
| **Complexity** | O(log N) per element |
| **Longitude** | -180 to 180 |
| **Latitude** | -85.05112878 to 85.05112878 |

```php
// Add store locations
Redis::geoadd('stores',
    -122.4194, 37.7749, 'San Francisco',
    -118.2437, 34.0522, 'Los Angeles',
    -73.9857, 40.7484, 'New York'
);

// Add single location
Redis::geoadd('users:locations', -122.4194, 37.7749, 'user:123');
```

---

## Querying Locations

### GEOPOS

Returns coordinates of members.

```
GEOPOS key member [member ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of [longitude, latitude] pairs (nil for missing) |
| **Complexity** | O(N) |

```php
$coords = Redis::geopos('stores', 'San Francisco', 'Los Angeles');
// [[-122.4194, 37.7749], [-118.2437, 34.0522]]
```

---

### GEODIST

Returns distance between two members.

```
GEODIST key member1 member2 [M|KM|FT|MI]
```

| Unit | Description |
|------|-------------|
| `M` | Meters (default) |
| `KM` | Kilometers |
| `FT` | Feet |
| `MI` | Miles |

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string - distance, or nil |
| **Complexity** | O(1) |

```php
// Distance in kilometers
$km = Redis::geodist('stores', 'San Francisco', 'Los Angeles', 'KM');
// "559.1..."

// Distance in miles
$miles = Redis::geodist('stores', 'San Francisco', 'New York', 'MI');
```

---

### GEOHASH

Returns geohash strings for members.

```
GEOHASH key member [member ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of geohash strings |
| **Complexity** | O(N) |

Geohash is an 11-character string encoding the location.

```php
$hashes = Redis::geohash('stores', 'San Francisco', 'Los Angeles');
// ["9q8yy...", "9q5c..."]
```

---

### GEOSEARCH

Searches for locations within an area.

```
GEOSEARCH key [FROMMEMBER member | FROMLONLAT longitude latitude]
  [BYRADIUS radius M|KM|FT|MI | BYBOX width height M|KM|FT|MI]
  [ASC|DESC] [COUNT count [ANY]] [WITHCOORD] [WITHDIST] [WITHHASH]
```

| Option | Description |
|--------|-------------|
| `FROMMEMBER` | Search from existing member |
| `FROMLONLAT` | Search from coordinates |
| `BYRADIUS` | Circular search area |
| `BYBOX` | Rectangular search area |
| `ASC` | Sort by distance ascending |
| `DESC` | Sort by distance descending |
| `COUNT n` | Limit results |
| `ANY` | Return any N matches (faster, less sorted) |
| `WITHCOORD` | Include coordinates |
| `WITHDIST` | Include distances |
| `WITHHASH` | Include geohash |

| Aspect | Details |
|--------|---------|
| **Returns** | Array of members with optional data |
| **Complexity** | O(N+log(M)) |
| **Since** | Redis 6.2 |

```php
// Find stores within 100km of coordinates
$nearby = Redis::geosearch('stores',
    'FROMLONLAT', -122.4194, 37.7749,
    'BYRADIUS', 100, 'KM',
    'WITHCOORD', 'WITHDIST',
    'ASC', 'COUNT', 10
);

// Find stores within 50 miles of an existing member
$nearby = Redis::geosearch('stores',
    'FROMMEMBER', 'San Francisco',
    'BYRADIUS', 50, 'MI',
    'ASC'
);

// Search in rectangular area
$inBox = Redis::geosearch('stores',
    'FROMLONLAT', -122.4, 37.7,
    'BYBOX', 100, 100, 'KM',
    'WITHCOORD'
);
```

---

### GEOSEARCHSTORE

Stores search results in a destination key.

```
GEOSEARCHSTORE destination source [FROMMEMBER member | FROMLONLAT lon lat]
  [BYRADIUS radius unit | BYBOX width height unit]
  [ASC|DESC] [COUNT count [ANY]] [STOREDIST]
```

| Option | Description |
|--------|-------------|
| `STOREDIST` | Store distances as scores (instead of geohash) |

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of elements stored |
| **Since** | Redis 6.2 |

```php
// Store nearby results for later use
$count = Redis::geosearchstore('nearby:user:123', 'stores',
    'FROMLONLAT', $userLon, $userLat,
    'BYRADIUS', 10, 'KM',
    'ASC', 'COUNT', 20
);
```

---

## Deprecated Commands

| Deprecated | Replacement |
|------------|-------------|
| `GEORADIUS` | `GEOSEARCH ... BYRADIUS` |
| `GEORADIUS_RO` | `GEOSEARCH ... BYRADIUS` |
| `GEORADIUSBYMEMBER` | `GEOSEARCH FROMMEMBER ... BYRADIUS` |
| `GEORADIUSBYMEMBER_RO` | `GEOSEARCH FROMMEMBER ... BYRADIUS` |

---

## Use Cases

### Store Locator

```php
class StoreLocator
{
    private string $key = 'stores';

    public function addStore(string $id, float $lon, float $lat, array $data): void
    {
        // Add to geo index
        Redis::geoadd($this->key, $lon, $lat, $id);

        // Store details in hash
        Redis::hmset("store:{$id}", $data);
    }

    public function findNearby(float $lon, float $lat, float $radiusKm, int $limit = 10): array
    {
        $results = Redis::geosearch($this->key,
            'FROMLONLAT', $lon, $lat,
            'BYRADIUS', $radiusKm, 'KM',
            'WITHCOORD', 'WITHDIST',
            'ASC', 'COUNT', $limit
        );

        return array_map(function ($result) {
            $storeId = $result[0];
            return [
                'id' => $storeId,
                'distance_km' => $result[1],
                'coordinates' => $result[2],
                'details' => Redis::hgetall("store:{$storeId}"),
            ];
        }, $results);
    }

    public function distanceBetweenStores(string $store1, string $store2): ?float
    {
        return Redis::geodist($this->key, $store1, $store2, 'KM');
    }
}
```

### Delivery Zone Check

```php
class DeliveryZoneChecker
{
    public function isInDeliveryZone(string $warehouseId, float $customerLon, float $customerLat): bool
    {
        // Check if customer is within 25km of warehouse
        $results = Redis::geosearch('warehouses',
            'FROMMEMBER', $warehouseId,
            'BYRADIUS', 25, 'KM'
        );

        // Add customer temporarily to check
        Redis::geoadd('temp:check', $customerLon, $customerLat, 'customer');
        $dist = Redis::geodist('temp:check', 'customer', $warehouseId, 'KM');
        Redis::del('temp:check');

        return $dist !== null && $dist <= 25;
    }
}
```

### User Proximity

```php
class UserProximity
{
    public function updateLocation(int $userId, float $lon, float $lat): void
    {
        Redis::geoadd('users:locations', $lon, $lat, "user:{$userId}");
        Redis::expire('users:locations', 3600);  // Expire after 1 hour
    }

    public function findNearbyUsers(int $userId, float $radiusMiles = 5): array
    {
        return Redis::geosearch('users:locations',
            'FROMMEMBER', "user:{$userId}",
            'BYRADIUS', $radiusMiles, 'MI',
            'WITHDIST',
            'ASC', 'COUNT', 50
        );
    }

    public function distanceToUser(int $fromUser, int $toUser): ?float
    {
        return Redis::geodist('users:locations',
            "user:{$fromUser}",
            "user:{$toUser}",
            'MI'
        );
    }
}
```

---

## Sorted Set Compatibility

Geo keys are stored as sorted sets, so you can use sorted set commands:

```php
// Count locations
$count = Redis::zcard('stores');

// Remove location
Redis::zrem('stores', 'Old Store');

// Get all locations (sorted by geohash)
$all = Redis::zrange('stores', 0, -1);

// Check if location exists
$exists = Redis::zscore('stores', 'San Francisco') !== null;
```

---

## Precision and Accuracy

| Aspect | Details |
|--------|---------|
| Geohash precision | 11 characters (~0.1 meter) |
| Distance accuracy | ~0.5% error for haversine formula |
| Coordinate range | Lon: -180 to 180, Lat: -85.05 to 85.05 |
| Storage | 52-bit integer (sorted set score) |

---

## Performance Notes

| Command | Complexity | Notes |
|---------|------------|-------|
| GEOADD | O(log N) per item | Uses sorted set |
| GEOPOS | O(N) | N = members requested |
| GEODIST | O(1) | Fast lookup |
| GEOSEARCH | O(N+log M) | N = area items, M = results |

**Best Practices:**
- Use COUNT to limit results
- Consider STOREDIST for distance-based queries
- Clean up stale locations with ZREM
- Use separate keys for different location types
- Index only necessary locations
