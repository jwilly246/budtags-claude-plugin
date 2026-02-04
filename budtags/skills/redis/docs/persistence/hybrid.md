# Redis Hybrid Persistence (RDB + AOF)

Combining RDB and AOF provides the best balance of durability and performance.

---

## Why Hybrid?

| Requirement | RDB | AOF | Hybrid |
|-------------|-----|-----|--------|
| Fast restart | ✅ | ❌ | ✅ |
| Minimal data loss | ❌ | ✅ | ✅ |
| Compact backups | ✅ | ❌ | ✅ |
| Point-in-time recovery | ✅ | ✅ | ✅ |

**Hybrid = RDB's fast recovery + AOF's durability**

---

## Configuration

### Recommended Production Setup

```
# redis.conf

# Enable both
appendonly yes
save 900 1
save 300 10
save 60 10000

# AOF settings
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Use RDB preamble in AOF (key for hybrid)
aof-use-rdb-preamble yes
```

### RDB Preamble Explained

With `aof-use-rdb-preamble yes`:

1. AOF rewrite creates RDB snapshot first
2. New commands append after RDB portion
3. On restart: load RDB, replay AOF tail
4. Result: Fast loading + minimal data loss

```
appendonly.aof structure:
┌─────────────────────────┐
│   RDB Binary Snapshot   │  ← Fast to load
├─────────────────────────┤
│   Recent AOF Commands   │  ← Small, fast replay
└─────────────────────────┘
```

---

## How Hybrid Works

### Normal Operation

```
1. RDB snapshots at configured intervals
2. AOF logs every write (with fsync policy)
3. AOF rewrite periodically compacts log
```

### On Restart

```
1. Redis checks for AOF (if appendonly=yes)
2. Loads RDB preamble portion (fast)
3. Replays AOF commands after preamble
4. Dataset fully restored
```

### Data Loss Window

| Configuration | Max Data Loss |
|---------------|---------------|
| `appendfsync always` | 0 |
| `appendfsync everysec` | ~1 second |
| RDB only | Up to 15 minutes |

---

## Recovery Scenarios

### Scenario 1: Clean Shutdown

```
1. Redis receives SHUTDOWN
2. Final RDB snapshot created
3. AOF fsynced
4. No data loss on restart
```

### Scenario 2: Crash with everysec

```
1. Crash occurs
2. RDB: Last snapshot (could be minutes old)
3. AOF: Commands up to ~1 second before crash
4. Restart loads AOF (includes RDB preamble)
5. Data loss: ~1 second maximum
```

### Scenario 3: Corrupted AOF

```bash
# 1. Check AOF
redis-check-aof /var/lib/redis/appendonlydir/appendonly.aof.1.incr.aof

# 2. If corrupted, fix or use RDB
redis-check-aof --fix /var/lib/redis/appendonlydir/appendonly.aof.1.incr.aof
# OR
mv /var/lib/redis/appendonlydir /var/lib/redis/appendonlydir.bak
# Redis will use RDB on restart

# 3. Restart
systemctl restart redis
```

---

## Monitoring Hybrid Setup

```php
class PersistenceMonitor
{
    public function getStatus(): array
    {
        $info = Redis::info('persistence');

        return [
            'rdb' => [
                'enabled' => $this->isRdbEnabled($info),
                'last_save' => date('Y-m-d H:i:s', $info['rdb_last_save_time']),
                'changes_pending' => $info['rdb_changes_since_last_save'],
                'last_status' => $info['rdb_last_bgsave_status'],
                'in_progress' => (bool) $info['rdb_bgsave_in_progress'],
            ],
            'aof' => [
                'enabled' => (bool) $info['aof_enabled'],
                'current_size_mb' => round($info['aof_current_size'] / 1048576, 2),
                'rewrite_in_progress' => (bool) $info['aof_rewrite_in_progress'],
                'last_rewrite_status' => $info['aof_last_bgrewrite_status'],
            ],
            'health' => $this->assessHealth($info),
        ];
    }

    private function isRdbEnabled(array $info): bool
    {
        // Check if any save points are configured
        $config = Redis::config('GET', 'save');
        return !empty($config['save']);
    }

    private function assessHealth(array $info): string
    {
        // Check for issues
        if ($info['rdb_last_bgsave_status'] !== 'ok') {
            return 'error: RDB save failed';
        }

        if ($info['aof_last_bgrewrite_status'] !== 'ok') {
            return 'warning: AOF rewrite failed';
        }

        $timeSinceSave = time() - $info['rdb_last_save_time'];
        if ($timeSinceSave > 3600) {
            return 'warning: No RDB save in 1+ hours';
        }

        return 'healthy';
    }
}
```

---

## Backup Strategy

### Comprehensive Backup

```bash
#!/bin/bash
# Hybrid backup: Both RDB and AOF

REDIS_DIR="/var/lib/redis"
BACKUP_DIR="/backup/redis"
DATE=$(date +%Y%m%d_%H%M%S)

# 1. Trigger fresh RDB
redis-cli BGSAVE

# 2. Wait for completion
while redis-cli LASTSAVE == $(cat /tmp/lastsave 2>/dev/null); do
    sleep 1
done
redis-cli LASTSAVE > /tmp/lastsave

# 3. Pause AOF rewrite during backup
redis-cli CONFIG SET auto-aof-rewrite-percentage 0

# 4. Copy both RDB and AOF
mkdir -p ${BACKUP_DIR}/${DATE}
cp ${REDIS_DIR}/dump.rdb ${BACKUP_DIR}/${DATE}/
cp -r ${REDIS_DIR}/appendonlydir ${BACKUP_DIR}/${DATE}/

# 5. Re-enable AOF rewrite
redis-cli CONFIG SET auto-aof-rewrite-percentage 100

# 6. Verify
redis-check-rdb ${BACKUP_DIR}/${DATE}/dump.rdb

echo "Backup complete: ${BACKUP_DIR}/${DATE}"
```

### Restore Procedure

```bash
#!/bin/bash
# Restore from hybrid backup

BACKUP_PATH=$1
REDIS_DIR="/var/lib/redis"

# 1. Stop Redis
systemctl stop redis

# 2. Backup current data
mv ${REDIS_DIR}/dump.rdb ${REDIS_DIR}/dump.rdb.old
mv ${REDIS_DIR}/appendonlydir ${REDIS_DIR}/appendonlydir.old

# 3. Restore from backup
cp ${BACKUP_PATH}/dump.rdb ${REDIS_DIR}/
cp -r ${BACKUP_PATH}/appendonlydir ${REDIS_DIR}/

# 4. Fix permissions
chown -R redis:redis ${REDIS_DIR}

# 5. Start Redis (will use AOF if present)
systemctl start redis

# 6. Verify
redis-cli DBSIZE
```

---

## Performance Considerations

### Memory During Saves

Both RDB and AOF rewrite fork:
```
Peak Memory = Current + Max(RDB_COW, AOF_COW)
```

Stagger saves to avoid simultaneous forks:
```
# Avoid both running at once
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 128mb  # Large enough to not trigger during RDB
```

### Disk I/O

```
# Separate disks if possible
dir /fast-ssd/redis                # RDB
appenddirname /another-ssd/aof     # AOF
```

---

## BudTags Recommendations

### Production Configuration

```
# Enable hybrid for maximum reliability
appendonly yes
save 900 1
save 300 10
save 60 10000

# Balanced fsync
appendfsync everysec

# RDB preamble for fast restarts
aof-use-rdb-preamble yes

# Reasonable rewrite thresholds
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Don't block on save errors
stop-writes-on-bgsave-error no
```

### For Different Use Cases

```
# Sessions (DB 0) - Need durability
appendonly yes
appendfsync everysec

# Cache (DB 1) - Can regenerate
# Lower priority, RDB sufficient
save 900 1

# Queues (DB 2) - Need durability
appendonly yes
appendfsync everysec
```

---

## Disaster Recovery Checklist

### Daily Verification

```php
Schedule::daily(function () {
    $info = Redis::info('persistence');

    // Check RDB
    $rdbAge = time() - $info['rdb_last_save_time'];
    if ($rdbAge > 86400) {
        Log::error("RDB not saved in 24 hours");
    }

    // Check AOF
    if ($info['aof_enabled'] && $info['aof_last_bgrewrite_status'] !== 'ok') {
        Log::error("AOF rewrite failing");
    }

    // Check for save errors
    if ($info['rdb_last_bgsave_status'] !== 'ok') {
        Log::error("Last RDB save failed");
    }
});
```

### Recovery Testing

Monthly test procedure:
1. Create backup
2. Spin up test Redis instance
3. Restore from backup
4. Verify data integrity
5. Document recovery time

---

## Key Takeaways

1. **Best of both worlds** - Fast restart + minimal data loss
2. **RDB preamble essential** - `aof-use-rdb-preamble yes`
3. **appendfsync everysec** - Best balance for most uses
4. **AOF takes precedence** - On restart with both present
5. **Backup both files** - RDB for snapshots, AOF for recent data
6. **Monitor both** - Check status of RDB and AOF regularly
7. **Test recovery** - Periodic restore tests are critical
8. **Stagger operations** - Avoid simultaneous RDB and AOF rewrites
