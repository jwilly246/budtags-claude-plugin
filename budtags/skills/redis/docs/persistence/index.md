# Redis Persistence

Redis provides multiple persistence options to write data to durable storage.

---

## Overview

| Method | File | Description |
|--------|------|-------------|
| RDB | [rdb.md](./rdb.md) | Point-in-time snapshots |
| AOF | [aof.md](./aof.md) | Append-only log |
| Hybrid | [hybrid.md](./hybrid.md) | RDB + AOF combined |

---

## Quick Comparison

| Feature | RDB | AOF | RDB + AOF |
|---------|-----|-----|-----------|
| Data loss risk | Higher (minutes) | Lower (seconds) | Lowest |
| File size | Compact | Larger | Both |
| Restart speed | Fast | Slower | Fast (uses RDB) |
| Performance impact | Fork only | Every write | Both |
| Recovery | Full snapshot | Replay log | RDB + recent AOF |

---

## Configuration Quick Reference

### RDB Only

```
# Snapshot every 60 seconds if 1000 keys changed
save 60 1000
save 300 100
save 900 1

# Disable AOF
appendonly no
```

### AOF Only

```
# Disable RDB
save ""

# Enable AOF
appendonly yes
appendfsync everysec
```

### Hybrid (Recommended for Production)

```
# Enable both
save 60 1000
appendonly yes
appendfsync everysec

# Use RDB preamble in AOF (Redis 4.0+)
aof-use-rdb-preamble yes
```

---

## Persistence Selection Guide

| Scenario | Recommendation |
|----------|----------------|
| **Development** | RDB only or none |
| **Caching only** | RDB or none (data regenerable) |
| **Session store** | AOF everysec |
| **Database replacement** | RDB + AOF |
| **Maximum durability** | AOF always (slow) |
| **Fast restarts needed** | RDB with frequent saves |

---

## BudTags Recommendations

### For Cache (DB 1)

```
# Low persistence priority - data is regenerable
save 900 1
save 300 10
save 60 10000

appendonly no
```

### For Queues (DB 2)

```
# Higher persistence - avoid losing jobs
appendonly yes
appendfsync everysec
```

### For Sessions (DB 0)

```
# Moderate persistence
appendonly yes
appendfsync everysec
```

---

## Key Commands

### Manual Save

```php
// Blocking save (avoid in production)
Redis::save();

// Background save
Redis::bgsave();

// Check last save time
$timestamp = Redis::lastsave();
```

### AOF Rewrite

```php
// Trigger AOF rewrite
Redis::bgrewriteaof();
```

### Check Status

```php
$info = Redis::info('persistence');

// RDB status
$rdbLastSave = $info['rdb_last_save_time'];
$rdbChanges = $info['rdb_changes_since_last_save'];
$rdbInProgress = $info['rdb_bgsave_in_progress'];

// AOF status
$aofEnabled = $info['aof_enabled'];
$aofRewriteInProgress = $info['aof_rewrite_in_progress'];
$aofLastRewriteTime = $info['aof_last_rewrite_time_sec'];
```

---

## Backup Best Practices

### RDB Backups

```bash
# Safe to copy while Redis running
cp /var/lib/redis/dump.rdb /backup/redis-$(date +%Y%m%d).rdb

# Verify backup
redis-check-rdb /backup/redis-*.rdb
```

### AOF Backups

```bash
# Disable rewrite during backup
redis-cli CONFIG SET auto-aof-rewrite-percentage 0

# Wait for any rewrite to complete
while redis-cli INFO persistence | grep -q "aof_rewrite_in_progress:1"; do
    sleep 1
done

# Copy AOF directory
cp -r /var/lib/redis/appendonlydir /backup/

# Re-enable rewrite
redis-cli CONFIG SET auto-aof-rewrite-percentage 100
```

---

## Recovery Procedures

### From RDB

```bash
# Stop Redis
systemctl stop redis

# Replace dump.rdb
cp /backup/dump.rdb /var/lib/redis/dump.rdb
chown redis:redis /var/lib/redis/dump.rdb

# Start Redis
systemctl start redis
```

### From AOF

```bash
# Check for corruption
redis-check-aof --fix /var/lib/redis/appendonlydir/appendonly.aof.1.incr.aof

# Redis will automatically load AOF on restart
systemctl restart redis
```

---

## Monitoring

### Health Check Script

```php
class PersistenceMonitor
{
    public function check(): array
    {
        $info = Redis::info('persistence');

        return [
            'rdb' => [
                'last_save' => date('Y-m-d H:i:s', $info['rdb_last_save_time']),
                'changes_pending' => $info['rdb_changes_since_last_save'],
                'save_in_progress' => (bool) $info['rdb_bgsave_in_progress'],
                'last_status' => $info['rdb_last_bgsave_status'],
            ],
            'aof' => [
                'enabled' => (bool) $info['aof_enabled'],
                'rewrite_in_progress' => (bool) $info['aof_rewrite_in_progress'],
                'last_rewrite_duration' => $info['aof_last_rewrite_time_sec'] . 's',
            ],
        ];
    }
}
```

---

## Key Takeaways

1. **RDB for speed** - Fast restarts, compact backups
2. **AOF for durability** - Minimal data loss
3. **Hybrid for production** - Best of both worlds
4. **appendfsync everysec** - Good balance
5. **aof-use-rdb-preamble** - Faster AOF recovery
6. **Regular backups** - Even with persistence enabled
7. **Monitor persistence status** - Catch issues early
