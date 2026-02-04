# Redis Sentinel

Automatic failover and monitoring for Redis high availability.

---

## Overview

Sentinel provides:
1. **Monitoring** - Checks master and replicas
2. **Notification** - Alerts on failures
3. **Automatic failover** - Promotes replica to master
4. **Configuration provider** - Clients query for current master

---

## Architecture

```
                    ┌─────────────┐
                    │  Sentinel 1 │
                    └──────┬──────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
┌────────┐           ┌─────────────┐        ┌─────────────┐
│ Master │◄─────────►│  Sentinel 2 │◄──────►│  Sentinel 3 │
└────┬───┘           └─────────────┘        └─────────────┘
     │
     ├────────────┐
     │            │
     ▼            ▼
┌─────────┐  ┌─────────┐
│ Replica │  │ Replica │
└─────────┘  └─────────┘
```

**Minimum setup:** 3 Sentinels (for quorum), 1 Master, 2 Replicas

---

## Configuration

### sentinel.conf

```
# Sentinel port
port 26379

# Monitor master (name, ip, port, quorum)
sentinel monitor mymaster 192.168.1.10 6379 2

# Auth (if master has password)
sentinel auth-pass mymaster your-password

# Time before master is considered down
sentinel down-after-milliseconds mymaster 5000

# Timeout for failover
sentinel failover-timeout mymaster 60000

# Replicas to sync at once during failover
sentinel parallel-syncs mymaster 1

# Notification script (optional)
# sentinel notification-script mymaster /path/to/script.sh

# Reconfig script (optional)
# sentinel client-reconfig-script mymaster /path/to/script.sh
```

### Quorum

The number of Sentinels that must agree master is down:

| Sentinels | Quorum | Can Survive |
|-----------|--------|-------------|
| 3 | 2 | 1 failure |
| 5 | 3 | 2 failures |
| 7 | 4 | 3 failures |

---

## Starting Sentinel

```bash
# Option 1: Dedicated command
redis-sentinel /path/to/sentinel.conf

# Option 2: Via redis-server
redis-server /path/to/sentinel.conf --sentinel
```

---

## Sentinel Commands

```bash
# Get master address
redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster

# List masters
redis-cli -p 26379 SENTINEL masters

# List replicas
redis-cli -p 26379 SENTINEL replicas mymaster

# List sentinels
redis-cli -p 26379 SENTINEL sentinels mymaster

# Force failover
redis-cli -p 26379 SENTINEL failover mymaster

# Check if failover in progress
redis-cli -p 26379 SENTINEL ckquorum mymaster
```

---

## Laravel Configuration

### Using phpredis

```php
// config/database.php
'redis' => [
    'client' => 'phpredis',

    'default' => [
        'tcp://sentinel1:26379',
        'tcp://sentinel2:26379',
        'tcp://sentinel3:26379',
        'options' => [
            'replication' => 'sentinel',
            'service' => 'mymaster',
            'parameters' => [
                'password' => env('REDIS_PASSWORD'),
                'database' => 0,
            ],
        ],
    ],
],
```

### Using Predis

```php
// config/database.php
'redis' => [
    'client' => 'predis',

    'default' => [
        'tcp://sentinel1:26379?role=sentinel&service=mymaster',
        'tcp://sentinel2:26379?role=sentinel&service=mymaster',
        'tcp://sentinel3:26379?role=sentinel&service=mymaster',
        'options' => [
            'replication' => 'sentinel',
            'service' => 'mymaster',
            'parameters' => [
                'password' => env('REDIS_PASSWORD'),
                'database' => 0,
            ],
        ],
    ],
],
```

---

## Failover Process

### Automatic Failover

1. Sentinel detects master is down (subjective down)
2. Quorum agrees (objective down)
3. Sentinel elected to lead failover
4. Best replica selected and promoted
5. Other replicas repoint to new master
6. Old master becomes replica when it returns

### Replica Selection Priority

1. Lowest `replica-priority` value
2. Most data (highest replication offset)
3. Lexicographically smaller runid

Configure priority:
```
# redis.conf on replica
replica-priority 100  # Lower = higher priority, 0 = never promote
```

---

## Monitoring

### PHP Sentinel Client

```php
class SentinelMonitor
{
    private array $sentinels = [
        ['host' => 'sentinel1', 'port' => 26379],
        ['host' => 'sentinel2', 'port' => 26379],
        ['host' => 'sentinel3', 'port' => 26379],
    ];

    public function getMasterAddress(string $service = 'mymaster'): ?array
    {
        foreach ($this->sentinels as $sentinel) {
            try {
                $redis = new \Redis();
                $redis->connect($sentinel['host'], $sentinel['port'], 1.0);

                $result = $redis->rawCommand('SENTINEL', 'get-master-addr-by-name', $service);

                if ($result) {
                    return [
                        'host' => $result[0],
                        'port' => (int) $result[1],
                    ];
                }
            } catch (\Exception $e) {
                continue;
            }
        }

        return null;
    }

    public function getStatus(string $service = 'mymaster'): array
    {
        foreach ($this->sentinels as $sentinel) {
            try {
                $redis = new \Redis();
                $redis->connect($sentinel['host'], $sentinel['port'], 1.0);

                $master = $redis->rawCommand('SENTINEL', 'master', $service);
                $replicas = $redis->rawCommand('SENTINEL', 'replicas', $service);
                $sentinels = $redis->rawCommand('SENTINEL', 'sentinels', $service);

                return [
                    'master' => $this->parseInfo($master),
                    'replicas' => array_map([$this, 'parseInfo'], $replicas),
                    'sentinels' => array_map([$this, 'parseInfo'], $sentinels),
                ];
            } catch (\Exception $e) {
                continue;
            }
        }

        return ['error' => 'No sentinel available'];
    }

    private function parseInfo(array $data): array
    {
        $result = [];
        for ($i = 0; $i < count($data); $i += 2) {
            $result[$data[$i]] = $data[$i + 1];
        }
        return $result;
    }
}
```

### Health Check

```php
Schedule::everyMinute(function () {
    $monitor = new SentinelMonitor();
    $status = $monitor->getStatus();

    if (isset($status['error'])) {
        Log::error('Sentinel unavailable', $status);
        return;
    }

    // Check master flags
    if (str_contains($status['master']['flags'] ?? '', 's_down')) {
        Log::error('Master is subjectively down');
    }

    if (str_contains($status['master']['flags'] ?? '', 'o_down')) {
        Log::error('Master is objectively down');
    }

    // Check replica count
    $healthyReplicas = count(array_filter($status['replicas'], function ($r) {
        return $r['flags'] === 'slave' && $r['master-link-status'] === 'ok';
    }));

    if ($healthyReplicas < 1) {
        Log::warning('No healthy replicas');
    }

    // Check sentinel count
    $healthySentinels = count(array_filter($status['sentinels'], function ($s) {
        return !str_contains($s['flags'] ?? '', 'disconnected');
    })) + 1; // +1 for the one we queried

    if ($healthySentinels < 2) {
        Log::warning('Insufficient sentinels');
    }
});
```

---

## Failover Testing

### Manual Failover

```bash
# Trigger failover
redis-cli -p 26379 SENTINEL failover mymaster

# Watch failover progress
redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
```

### Simulate Master Failure

```bash
# On master
redis-cli DEBUG SLEEP 30  # Simulate hang

# Or
sudo systemctl stop redis  # Stop Redis

# Watch Sentinel logs for failover
tail -f /var/log/redis/sentinel.log
```

---

## Common Issues

### Split Brain

**Problem:** Network partition causes two masters

**Solution:**
- Use odd number of Sentinels
- Configure min-replicas-to-write on master
```
min-replicas-to-write 1
min-replicas-max-lag 10
```

### Failover Loops

**Problem:** Continuous failovers

**Causes:**
- Unstable network
- Resource contention
- Too aggressive down-after-milliseconds

**Solution:**
```
# Increase timeout
sentinel down-after-milliseconds mymaster 30000

# Increase failover timeout
sentinel failover-timeout mymaster 180000
```

---

## Key Takeaways

1. **Odd number of Sentinels** - 3 or 5 recommended
2. **Quorum = majority** - For consensus
3. **down-after-milliseconds** - Balance speed vs. stability
4. **replica-priority** - Control promotion order
5. **Test failover** - Before production incidents
6. **Monitor all components** - Master, replicas, and sentinels
7. **Use Sentinel-aware clients** - For automatic reconnection
