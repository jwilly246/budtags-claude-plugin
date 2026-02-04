# Redis Cluster

Horizontal scaling with automatic sharding and built-in high availability.

---

## Overview

Redis Cluster provides:
1. **Data sharding** - Automatic partitioning across nodes
2. **High availability** - Built-in failover (no Sentinel needed)
3. **Linear scalability** - Add nodes to increase capacity

---

## Architecture

### Hash Slots

Redis Cluster divides keyspace into 16384 hash slots:

```
Slot = CRC16(key) mod 16384
```

Each master node handles a subset of slots:
```
Master 1: slots 0-5460
Master 2: slots 5461-10922
Master 3: slots 10923-16383
```

### Node Layout

```
┌─────────────────────────────────────────────────────┐
│                    Redis Cluster                     │
├─────────────────┬─────────────────┬─────────────────┤
│   Master 1      │   Master 2      │   Master 3      │
│   (0-5460)      │   (5461-10922)  │   (10923-16383) │
│       │         │       │         │       │         │
│       ▼         │       ▼         │       ▼         │
│   Replica 1     │   Replica 2     │   Replica 3     │
└─────────────────┴─────────────────┴─────────────────┘
```

**Minimum:** 3 masters + 3 replicas = 6 nodes

---

## Setup

### Configuration (each node)

```
# redis.conf
port 6379
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
appendonly yes
```

### Create Cluster

```bash
# Create 6-node cluster (3 masters, 3 replicas)
redis-cli --cluster create \
  192.168.1.1:6379 192.168.1.2:6379 192.168.1.3:6379 \
  192.168.1.4:6379 192.168.1.5:6379 192.168.1.6:6379 \
  --cluster-replicas 1

# Verify cluster
redis-cli --cluster check 192.168.1.1:6379
```

---

## Laravel Configuration

### phpredis

```php
// config/database.php
'redis' => [
    'client' => 'phpredis',

    'options' => [
        'cluster' => 'redis',  // Enable cluster mode
    ],

    'clusters' => [
        'default' => [
            [
                'host' => env('REDIS_HOST_1', '192.168.1.1'),
                'port' => env('REDIS_PORT', 6379),
                'password' => env('REDIS_PASSWORD'),
                'database' => 0,
            ],
            [
                'host' => env('REDIS_HOST_2', '192.168.1.2'),
                'port' => env('REDIS_PORT', 6379),
                'password' => env('REDIS_PASSWORD'),
                'database' => 0,
            ],
            [
                'host' => env('REDIS_HOST_3', '192.168.1.3'),
                'port' => env('REDIS_PORT', 6379),
                'password' => env('REDIS_PASSWORD'),
                'database' => 0,
            ],
        ],
    ],
],
```

### Usage

```php
// Client automatically routes to correct node
Redis::set('key', 'value');  // Routed by hash slot
$value = Redis::get('key');
```

---

## Hash Tags

Force keys to same slot using `{tag}`:

```php
// These go to same slot (same hash tag)
Redis::set('{user:123}:profile', $profile);
Redis::set('{user:123}:settings', $settings);
Redis::set('{user:123}:sessions', $sessions);

// Now multi-key operations work
Redis::mget(['{user:123}:profile', '{user:123}:settings']);
```

**Important:** Without hash tags, multi-key operations may fail if keys are on different nodes.

---

## Multi-Key Command Limitations

### Commands That Require Same Slot

```php
// ❌ May fail: Keys on different slots
Redis::mget(['key1', 'key2', 'key3']);
Redis::mset(['key1' => 'a', 'key2' => 'b']);

// ✅ Works: Same hash tag
Redis::mget(['{user:1}:a', '{user:1}:b']);
Redis::mset(['{user:1}:a' => 'x', '{user:1}:b' => 'y']);
```

### Cross-Slot Pipeline

```php
class ClusterAwarePipeline
{
    public function getMultiple(array $keys): array
    {
        $results = [];

        // phpredis handles slot routing automatically
        $values = Redis::pipeline(function ($pipe) use ($keys) {
            foreach ($keys as $key) {
                $pipe->get($key);
            }
        });

        return array_combine($keys, $values);
    }
}
```

---

## Cluster Commands

### Cluster Info

```bash
# Cluster state
redis-cli CLUSTER INFO

# Node list
redis-cli CLUSTER NODES

# Slot mapping
redis-cli CLUSTER SLOTS
```

### PHP Cluster Info

```php
class ClusterMonitor
{
    public function getInfo(): array
    {
        $info = [];
        $rawInfo = Redis::command('CLUSTER', ['INFO']);

        foreach (explode("\n", $rawInfo) as $line) {
            if (str_contains($line, ':')) {
                [$key, $value] = explode(':', trim($line));
                $info[$key] = $value;
            }
        }

        return [
            'state' => $info['cluster_state'],
            'slots_assigned' => $info['cluster_slots_assigned'],
            'slots_ok' => $info['cluster_slots_ok'],
            'known_nodes' => $info['cluster_known_nodes'],
            'size' => $info['cluster_size'],
        ];
    }

    public function getNodes(): array
    {
        $nodes = [];
        $rawNodes = Redis::command('CLUSTER', ['NODES']);

        foreach (explode("\n", trim($rawNodes)) as $line) {
            if (empty($line)) continue;

            $parts = explode(' ', $line);
            $nodes[] = [
                'id' => $parts[0],
                'address' => $parts[1],
                'flags' => $parts[2],
                'master' => $parts[3] === '-' ? null : $parts[3],
                'ping_sent' => $parts[4],
                'pong_recv' => $parts[5],
                'config_epoch' => $parts[6],
                'link_state' => $parts[7],
                'slots' => array_slice($parts, 8),
            ];
        }

        return $nodes;
    }
}
```

---

## Scaling

### Add Node

```bash
# Add new master
redis-cli --cluster add-node new-node:6379 existing-node:6379

# Add as replica
redis-cli --cluster add-node new-node:6379 existing-node:6379 \
  --cluster-slave --cluster-master-id <master-node-id>
```

### Reshard

```bash
# Interactively move slots
redis-cli --cluster reshard existing-node:6379

# Or specify parameters
redis-cli --cluster reshard existing-node:6379 \
  --cluster-from <source-id> \
  --cluster-to <dest-id> \
  --cluster-slots 1000
```

### Remove Node

```bash
# Remove empty node
redis-cli --cluster del-node existing-node:6379 <node-id>

# First reshard slots away from node
redis-cli --cluster reshard existing-node:6379 \
  --cluster-from <removing-id> \
  --cluster-to <other-id> \
  --cluster-slots <all-slots>
```

---

## Failover

### Automatic Failover

When master fails:
1. Replicas detect master failure
2. Replicas request votes from other masters
3. One replica promoted to master
4. Cluster continues with new master

### Manual Failover

```bash
# On replica, force takeover
redis-cli -h replica-host CLUSTER FAILOVER

# Force even if master is up
redis-cli -h replica-host CLUSTER FAILOVER FORCE
```

---

## Monitoring

### Health Check

```php
Schedule::everyMinute(function () {
    $monitor = new ClusterMonitor();
    $info = $monitor->getInfo();

    if ($info['state'] !== 'ok') {
        Log::error('Cluster state not OK', $info);
    }

    if ($info['slots_ok'] !== '16384') {
        Log::warning('Not all slots covered', $info);
    }

    $nodes = $monitor->getNodes();
    $failingNodes = array_filter($nodes, function ($n) {
        return str_contains($n['flags'], 'fail');
    });

    if (!empty($failingNodes)) {
        Log::error('Failing nodes detected', ['nodes' => $failingNodes]);
    }
});
```

---

## BudTags Considerations

### When to Use Cluster

- Data > 25GB
- Ops > 100K/sec
- Multi-region requirements
- Need horizontal write scaling

### Hash Tag Strategy

```php
class ClusterKeyStrategy
{
    // Organization-scoped keys share slot
    public function orgKey(int $orgId, string $suffix): string
    {
        return "{org:{$orgId}}:{$suffix}";
    }

    // Facility-scoped keys share slot
    public function facilityKey(string $facility, string $suffix): string
    {
        return "{facility:{$facility}}:{$suffix}";
    }
}

// Usage
$strategy = new ClusterKeyStrategy();
Redis::set($strategy->orgKey(123, 'settings'), $data);
Redis::set($strategy->orgKey(123, 'cache'), $cache);
// Both on same slot - can use MGET
```

---

## Key Takeaways

1. **16384 hash slots** - Automatic distribution
2. **Hash tags `{}`** - Force same slot
3. **Minimum 6 nodes** - 3 masters + 3 replicas
4. **Built-in failover** - No Sentinel needed
5. **Multi-key limitations** - Same slot required
6. **phpredis routing** - Automatic slot handling
7. **Reshard to scale** - Move slots between nodes
8. **Monitor cluster state** - `CLUSTER INFO`
