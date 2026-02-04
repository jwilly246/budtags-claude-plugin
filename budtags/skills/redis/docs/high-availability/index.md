# Redis High Availability

Options for ensuring Redis reliability and uptime.

---

## Overview

| Method | Use Case | Complexity |
|--------|----------|------------|
| Replication | Read scaling, basic HA | Low |
| Sentinel | Automatic failover | Medium |
| Cluster | Horizontal scaling, data sharding | High |

---

## Quick Comparison

| Feature | Standalone | Replication | Sentinel | Cluster |
|---------|-----------|-------------|----------|---------|
| Automatic failover | ❌ | ❌ | ✅ | ✅ |
| Read scaling | ❌ | ✅ | ✅ | ✅ |
| Write scaling | ❌ | ❌ | ❌ | ✅ |
| Data sharding | ❌ | ❌ | ❌ | ✅ |
| Complexity | Low | Low | Medium | High |
| Min nodes | 1 | 2 | 5+ | 6+ |

---

## Topics

| Topic | File | Description |
|-------|------|-------------|
| Replication | [replication.md](./replication.md) | Master-replica setup |
| Sentinel | [sentinel.md](./sentinel.md) | Automatic failover |
| Cluster | [cluster.md](./cluster.md) | Data sharding |

---

## BudTags Recommendations

### Development

```
Single Redis instance
No HA needed for local development
```

### Small Production

```
Redis + 1 Replica
Manual failover acceptable
Use for: < 10K ops/sec, < 5GB data
```

### Medium Production

```
Redis Sentinel (3 sentinels, 1 master, 2 replicas)
Automatic failover
Use for: < 50K ops/sec, < 25GB data
```

### Large Production

```
Redis Cluster (6+ nodes)
Horizontal scaling
Use for: > 50K ops/sec, > 25GB data, or multi-region
```

---

## Decision Flowchart

```
Need horizontal write scaling?
├── Yes → Redis Cluster
└── No
    ├── Need automatic failover?
    │   ├── Yes → Sentinel
    │   └── No
    │       ├── Need read scaling?
    │       │   ├── Yes → Replication
    │       │   └── No → Standalone
```

---

## Quick Setup Guides

### Replication (Basic HA)

Master (redis.conf):
```
# No special config needed
bind 0.0.0.0
```

Replica (redis.conf):
```
replicaof master-ip 6379
replica-read-only yes
```

### Sentinel (Auto Failover)

sentinel.conf:
```
sentinel monitor mymaster master-ip 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
sentinel parallel-syncs mymaster 1
```

### Cluster (Horizontal Scaling)

```bash
# Create 6-node cluster (3 masters, 3 replicas)
redis-cli --cluster create \
  node1:6379 node2:6379 node3:6379 \
  node4:6379 node5:6379 node6:6379 \
  --cluster-replicas 1
```

---

## Laravel Configuration

### With Sentinel

```php
// config/database.php
'redis' => [
    'client' => 'phpredis',

    'default' => [
        'host' => env('REDIS_HOST'),
        'port' => env('REDIS_PORT', 26379),
        'database' => 0,
        'options' => [
            'replication' => 'sentinel',
            'service' => env('REDIS_SENTINEL_SERVICE', 'mymaster'),
            'parameters' => [
                'password' => env('REDIS_PASSWORD'),
                'database' => 0,
            ],
        ],
    ],
],
```

### With Cluster

```php
// config/database.php
'redis' => [
    'client' => 'phpredis',
    'options' => [
        'cluster' => 'redis',
    ],

    'clusters' => [
        'default' => [
            [
                'host' => env('REDIS_HOST_1', 'node1'),
                'port' => env('REDIS_PORT', 6379),
                'password' => env('REDIS_PASSWORD'),
                'database' => 0,
            ],
            [
                'host' => env('REDIS_HOST_2', 'node2'),
                'port' => env('REDIS_PORT', 6379),
                'password' => env('REDIS_PASSWORD'),
                'database' => 0,
            ],
            [
                'host' => env('REDIS_HOST_3', 'node3'),
                'port' => env('REDIS_PORT', 6379),
                'password' => env('REDIS_PASSWORD'),
                'database' => 0,
            ],
        ],
    ],
],
```

---

## Monitoring

```php
class HaMonitor
{
    public function checkReplication(): array
    {
        $info = Redis::info('replication');

        return [
            'role' => $info['role'],
            'connected_slaves' => $info['connected_slaves'] ?? 0,
            'master_link_status' => $info['master_link_status'] ?? 'N/A',
            'replication_lag' => $this->getReplicationLag($info),
        ];
    }

    private function getReplicationLag(array $info): ?int
    {
        if ($info['role'] === 'slave') {
            return $info['master_last_io_seconds_ago'] ?? null;
        }
        return null;
    }
}
```

---

## Key Takeaways

1. **Start simple** - Standalone is fine for many use cases
2. **Add replicas first** - Easy read scaling and backup
3. **Sentinel for failover** - When downtime is unacceptable
4. **Cluster for scale** - When you outgrow single-node limits
5. **Test failover** - Before you need it in production
6. **Monitor replication lag** - Catch issues early
