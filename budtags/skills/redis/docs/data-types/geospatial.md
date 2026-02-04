# Redis Geospatial - Deep Dive

Redis geospatial indexes store coordinates and enable location-based queries. Built on sorted sets using geohash encoding.

---

## Internal Representation

Geospatial data uses sorted sets:
- **Member** - Location identifier (string)
- **Score** - 52-bit geohash of coordinates
- **Precision** - ~0.6mm at equator

The geohash encoding allows range queries on sorted set scores to efficiently find nearby locations.

---

## Core Commands

### Adding Locations

```php
// Add single location
Redis::geoadd('stores', -122.4194, 37.7749, 'san-francisco');

// Add multiple locations
Redis::geoadd('stores',
    -118.2437, 34.0522, 'los-angeles',
    -73.9857, 40.7484, 'new-york',
    -87.6298, 41.8781, 'chicago'
);

// With options (Redis 6.2+)
Redis::geoadd('stores', 'NX', -122.4194, 37.7749, 'sf'); // Only if not exists
Redis::geoadd('stores', 'XX', -122.4194, 37.7750, 'sf'); // Only if exists
```

### Getting Coordinates

```php
// Get position
$coords = Redis::geopos('stores', 'san-francisco');
// Returns: [[-122.4194, 37.7749]]

// Multiple positions
$coords = Redis::geopos('stores', 'san-francisco', 'los-angeles');
```

### Distance Calculations

```php
// Distance between two members
$distance = Redis::geodist('stores', 'san-francisco', 'los-angeles', 'km');
// Returns: 559.1... km

// Units: m (meters), km (kilometers), mi (miles), ft (feet)
$miles = Redis::geodist('stores', 'san-francisco', 'los-angeles', 'mi');
```

---

## Search Commands

### GEOSEARCH (Redis 6.2+)

```php
// Search by radius from coordinates
$nearby = Redis::geosearch('stores',
    'FROMMEMBER', 'san-francisco',  // or FROMLONLAT -122.4 37.7
    'BYRADIUS', 100, 'km',          // or BYBOX 200 100 km
    'ASC',                          // or DESC
    'COUNT', 10,
    'WITHDIST', 'WITHCOORD'
);

// Search by bounding box
$inBox = Redis::geosearch('stores',
    'FROMLONLAT', -122.4, 37.7,
    'BYBOX', 200, 100, 'km',  // width x height
    'ASC'
);
```

### GEOSEARCHSTORE (Redis 6.2+)

```php
// Store results in new sorted set
Redis::geosearchstore('nearby:sf', 'stores',
    'FROMMEMBER', 'san-francisco',
    'BYRADIUS', 100, 'km'
);

// Store with distances as scores
Redis::geosearchstore('nearby:sf', 'stores',
    'FROMMEMBER', 'san-francisco',
    'BYRADIUS', 100, 'km',
    'STOREDIST'
);
```

### Legacy: GEORADIUS / GEORADIUSBYMEMBER

```php
// Search by radius from coordinates (deprecated, use GEOSEARCH)
$nearby = Redis::georadius('stores',
    -122.4194, 37.7749,  // longitude, latitude
    100, 'km',           // radius
    'WITHDIST',          // include distance
    'WITHCOORD',         // include coordinates
    'COUNT', 10,         // limit results
    'ASC'                // sort by distance
);

// Search from existing member
$nearby = Redis::georadiusbymember('stores',
    'san-francisco',
    100, 'km',
    'WITHDIST', 'ASC', 'COUNT', 10
);
```

---

## Use Cases

### 1. Store Locator

```php
class StoreLocator
{
    private string $key = 'stores:locations';

    public function addStore(string $storeId, float $lat, float $lon): void
    {
        Redis::geoadd($this->key, $lon, $lat, $storeId);
    }

    public function removeStore(string $storeId): void
    {
        Redis::zrem($this->key, $storeId);
    }

    public function findNearby(float $lat, float $lon, float $radiusKm, int $limit = 10): array
    {
        $results = Redis::geosearch($this->key,
            'FROMLONLAT', $lon, $lat,
            'BYRADIUS', $radiusKm, 'km',
            'ASC',
            'COUNT', $limit,
            'WITHDIST', 'WITHCOORD'
        );

        return array_map(function ($item) {
            return [
                'id' => $item[0],
                'distance_km' => (float) $item[1],
                'coordinates' => [
                    'longitude' => (float) $item[2][0],
                    'latitude' => (float) $item[2][1],
                ],
            ];
        }, $results);
    }

    public function getDistance(string $from, string $to): ?float
    {
        return Redis::geodist($this->key, $from, $to, 'km');
    }
}
```

### 2. Delivery Zone Check

```php
class DeliveryZone
{
    public function isInDeliveryRange(string $storeId, float $customerLat, float $customerLon): bool
    {
        $maxDeliveryKm = 15;

        // Check if customer is within range of store
        $nearby = Redis::geosearch('stores:locations',
            'FROMMEMBER', $storeId,
            'BYRADIUS', $maxDeliveryKm, 'km'
        );

        // Add temporary point for customer
        $tempKey = 'temp:customer:' . uniqid();
        Redis::geoadd($tempKey, $customerLon, $customerLat, 'customer');

        $distance = $this->calculateDistance($storeId, $customerLat, $customerLon);

        return $distance !== null && $distance <= $maxDeliveryKm;
    }

    private function calculateDistance(string $storeId, float $lat, float $lon): ?float
    {
        // Get store coordinates
        $coords = Redis::geopos('stores:locations', $storeId);

        if (!$coords || !$coords[0]) {
            return null;
        }

        // Calculate using Haversine formula
        return $this->haversine(
            $coords[0][1], $coords[0][0],  // store lat, lon
            $lat, $lon                       // customer lat, lon
        );
    }

    private function haversine(float $lat1, float $lon1, float $lat2, float $lon2): float
    {
        $earthRadius = 6371; // km

        $dLat = deg2rad($lat2 - $lat1);
        $dLon = deg2rad($lon2 - $lon1);

        $a = sin($dLat / 2) ** 2 +
             cos(deg2rad($lat1)) * cos(deg2rad($lat2)) * sin($dLon / 2) ** 2;

        $c = 2 * asin(sqrt($a));

        return $earthRadius * $c;
    }
}
```

### 3. Fleet Tracking

```php
class FleetTracker
{
    private string $key = 'fleet:positions';

    public function updatePosition(string $vehicleId, float $lat, float $lon): void
    {
        Redis::pipeline(function ($pipe) use ($vehicleId, $lat, $lon) {
            // Update current position
            $pipe->geoadd($this->key, $lon, $lat, $vehicleId);

            // Store timestamp of last update
            $pipe->hset('fleet:updated', $vehicleId, time());
        });
    }

    public function getPosition(string $vehicleId): ?array
    {
        $coords = Redis::geopos($this->key, $vehicleId);

        if (!$coords || !$coords[0]) {
            return null;
        }

        return [
            'longitude' => $coords[0][0],
            'latitude' => $coords[0][1],
            'updated_at' => Redis::hget('fleet:updated', $vehicleId),
        ];
    }

    public function findVehiclesNear(float $lat, float $lon, float $radiusKm): array
    {
        return Redis::geosearch($this->key,
            'FROMLONLAT', $lon, $lat,
            'BYRADIUS', $radiusKm, 'km',
            'WITHDIST',
            'ASC'
        );
    }

    public function getClosestVehicle(float $lat, float $lon): ?array
    {
        $result = Redis::geosearch($this->key,
            'FROMLONLAT', $lon, $lat,
            'BYRADIUS', 100, 'km',
            'ASC',
            'COUNT', 1,
            'WITHDIST'
        );

        return $result ? $result[0] : null;
    }
}
```

### 4. Geofencing

```php
class Geofence
{
    public function addZone(string $zoneId, float $lat, float $lon, float $radiusKm): void
    {
        Redis::pipeline(function ($pipe) use ($zoneId, $lat, $lon, $radiusKm) {
            $pipe->geoadd('geofences', $lon, $lat, $zoneId);
            $pipe->hset('geofences:radius', $zoneId, $radiusKm);
        });
    }

    public function checkPosition(float $lat, float $lon): array
    {
        // Get all zones within reasonable distance
        $nearbyZones = Redis::geosearch('geofences',
            'FROMLONLAT', $lon, $lat,
            'BYRADIUS', 100, 'km',  // Max check radius
            'WITHDIST'
        );

        $inZones = [];

        foreach ($nearbyZones as $zone) {
            $zoneId = $zone[0];
            $distance = (float) $zone[1];
            $radius = (float) Redis::hget('geofences:radius', $zoneId);

            if ($distance <= $radius) {
                $inZones[] = [
                    'zone_id' => $zoneId,
                    'distance_km' => $distance,
                    'radius_km' => $radius,
                ];
            }
        }

        return $inZones;
    }
}
```

---

## Performance Characteristics

| Command | Complexity |
|---------|------------|
| GEOADD | O(log N) per element |
| GEOPOS | O(1) per element |
| GEODIST | O(1) |
| GEOSEARCH (radius) | O(N + log M) |
| GEOSEARCH (box) | O(N + log M) |
| GEOHASH | O(1) per element |

N = elements in result, M = total elements in sorted set

---

## BudTags Potential Usage

### Facility Location Search

```php
class FacilityLocator
{
    public function indexFacility(string $facilityId, float $lat, float $lon): void
    {
        Redis::geoadd('facilities:geo', $lon, $lat, $facilityId);
    }

    public function findNearbyFacilities(float $lat, float $lon, float $radiusMiles = 50): array
    {
        return Redis::geosearch('facilities:geo',
            'FROMLONLAT', $lon, $lat,
            'BYRADIUS', $radiusMiles, 'mi',
            'ASC',
            'COUNT', 20,
            'WITHDIST'
        );
    }
}
```

---

## Key Takeaways

1. **Built on sorted sets** - Use ZREM to remove, ZCARD for count
2. **Geohash encoding** - ~0.6mm precision
3. **GEOSEARCH** - Preferred over deprecated GEORADIUS
4. **Longitude first** - Commands take (lon, lat) order
5. **Distance units** - m, km, mi, ft
6. **Count + Sort** - Always limit and sort results
7. **Index updates** - GEOADD replaces existing members
8. **No expiration** - Combine with TTL on separate key if needed
