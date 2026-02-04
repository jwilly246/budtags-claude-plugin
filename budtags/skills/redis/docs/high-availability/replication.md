# Redis Replication

Master-replica replication for read scaling and data redundancy.

---

## How It Works

1. Replica connects to master
2. Master sends RDB snapshot to replica
3. Master streams new commands to replica
4. Replica applies commands to stay in sync

```
Writes ─────> Master ─────> Replica 1
                │
                └─────────> Replica 2
                │
                └─────────> Replica N
Reads <────── (Any)
```

---

## Configuration

### Master (redis.conf)

```
# Bind to network interface
bind 0.0.0.0

# Optional: Require password
requirepass your-password

# Optional: Set master password for replicas
masterauth your-password
```

### Replica (redis.conf)

```
# Point to master
replicaof master-ip 6379

# Password for connecting to master
masterauth your-password

# Local password (optional, for client connections)
requirepass your-password

# Read-only mode (recommended)
replica-read-only yes

# Serve stale data during sync (recommended)
replica-serve-stale-data yes
```

### Runtime Configuration

```php
// Make this instance a replica of another
Redis::replicaof('master-ip', 6379);

// Promote replica to master
Redis::replicaof('NO', 'ONE');

// Check replication status
$info = Redis::info('replication');
```

---

## Replication Modes

### Asynchronous (Default)

Master doesn't wait for replica acknowledgment:
- **Pros:** Fast writes
- **Cons:** Possible data loss on master failure

### Semi-Synchronous

Wait for N replicas before acknowledging write:
```
# Master config
min-replicas-to-write 1
min-replicas-max-lag 10
```

This blocks writes if < N replicas are connected or lag > 10 seconds.

---

## Laravel Configuration

### Read/Write Splitting

```php
// config/database.php
'redis' => [
    'client' => 'phpredis',

    'default' => [
        'url' => env('REDIS_URL'),
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', '6379'),
        'database' => '0',
    ],

    'read' => [
        'host' => env('REDIS_READ_HOST', '127.0.0.1'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', '6379'),
        'database' => '0',
    ],
],
```

### Usage

```php
// Writes go to master
Redis::connection('default')->set('key', 'value');

// Reads can go to replica
Redis::connection('read')->get('key');

// Helper class
class RedisReadWrite
{
    public static function write(): \Illuminate\Redis\Connections\Connection
    {
        return Redis::connection('default');
    }

    public static function read(): \Illuminate\Redis\Connections\Connection
    {
        return Redis::connection('read');
    }
}

// Usage
RedisReadWrite::write()->set('key', 'value');
$value = RedisReadWrite::read()->get('key');
```

---

## Monitoring Replication

### Check Status

```php
class ReplicationMonitor
{
    public function getMasterStatus(): array
    {
        $info = Redis::info('replication');

        if ($info['role'] !== 'master') {
            return ['error' => 'Not a master'];
        }

        $replicas = [];
        for ($i = 0; $i < $info['connected_slaves']; $i++) {
            $slaveInfo = $info["slave{$i}"];
            $parts = explode(',', $slaveInfo);
            $replica = [];
            foreach ($parts as $part) {
                [$key, $value] = explode('=', $part);
                $replica[$key] = $value;
            }
            $replicas[] = $replica;
        }

        return [
            'role' => 'master',
            'connected_replicas' => $info['connected_slaves'],
            'replicas' => $replicas,
        ];
    }

    public function getReplicaStatus(): array
    {
        $info = Redis::info('replication');

        if ($info['role'] !== 'slave') {
            return ['error' => 'Not a replica'];
        }

        return [
            'role' => 'replica',
            'master_host' => $info['master_host'],
            'master_port' => $info['master_port'],
            'master_link_status' => $info['master_link_status'],
            'master_last_io_seconds_ago' => $info['master_last_io_seconds_ago'],
            'master_sync_in_progress' => (bool) $info['master_sync_in_progress'],
            'slave_read_only' => (bool) $info['slave_read_only'],
            'replica_repl_offset' => $info['slave_repl_offset'],
        ];
    }
}
```

### Monitor Lag

```php
Schedule::everyMinute(function () {
    $info = Redis::info('replication');

    if ($info['role'] === 'slave') {
        $lag = $info['master_last_io_seconds_ago'];

        if ($lag > 10) {
            Log::warning("Replica lag: {$lag} seconds");
        }

        if ($info['master_link_status'] !== 'up') {
            Log::error("Replica disconnected from master");
        }
    }
});
```

---

## Failover (Manual)

### Promote Replica to Master

```bash
# On replica
redis-cli REPLICAOF NO ONE
```

### Point Other Replicas to New Master

```bash
# On other replicas
redis-cli REPLICAOF new-master-ip 6379
```

### Update Application Config

```env
REDIS_HOST=new-master-ip
REDIS_READ_HOST=replica-ip
```

---

## Best Practices

### 1. Set Timeouts

```
# Master
repl-timeout 60

# Replica
repl-timeout 60
```

### 2. Enable Diskless Replication (Fast Networks)

```
# Master - send RDB directly to socket
repl-diskless-sync yes
repl-diskless-sync-delay 5
```

### 3. Backlog for Reconnection

```
# Master - buffer for partial resync
repl-backlog-size 64mb
repl-backlog-ttl 3600
```

### 4. Ping Replicas

```
# Master - ping replicas every N seconds
repl-ping-replica-period 10
```

---

## Common Issues

### Replica Can't Connect

```php
// Check master_link_status
$info = Redis::info('replication');
if ($info['master_link_status'] !== 'up') {
    // Check: network, firewall, password
}
```

### High Replication Lag

Causes:
- Network latency
- Replica overloaded
- Large writes on master

Solutions:
- Use faster network
- Add more replicas
- Increase repl-backlog-size

### Full Resync Too Often

Cause: Backlog too small for write rate

Solution:
```
repl-backlog-size 256mb  # Increase backlog
```

---

## Key Takeaways

1. **Asynchronous by default** - Master doesn't wait for replicas
2. **Read-only replicas** - Enable `replica-read-only yes`
3. **Monitor lag** - `master_last_io_seconds_ago`
4. **Backlog sizing** - Larger = fewer full resyncs
5. **Diskless sync** - Faster on fast networks
6. **Manual failover** - `REPLICAOF NO ONE` to promote
7. **Split reads/writes** - Use separate connections
