# Redis RDB Persistence

RDB (Redis Database) creates point-in-time snapshots of your dataset at specified intervals.

---

## How RDB Works

1. Redis forks the main process
2. Child process writes dataset to temporary file
3. On completion, file is renamed to `dump.rdb`
4. Parent continues serving requests during save

### Fork and Copy-on-Write

- **Fork** creates child process with same memory
- **Copy-on-Write** - Only modified pages are duplicated
- Memory usage temporarily increases during save
- Larger datasets = longer save times

---

## Configuration

### Automatic Snapshots

```
# redis.conf
# save <seconds> <changes>

save 900 1      # Save if 1+ keys changed in 900 seconds (15 min)
save 300 10     # Save if 10+ keys changed in 300 seconds (5 min)
save 60 10000   # Save if 10000+ keys changed in 60 seconds

# Disable automatic saves
save ""
```

### File Settings

```
# Snapshot filename
dbfilename dump.rdb

# Directory for RDB file
dir /var/lib/redis

# Compress with LZF (recommended)
rdbcompression yes

# CRC64 checksum (small performance hit)
rdbchecksum yes

# Stop writes on background save error
stop-writes-on-bgsave-error yes
```

---

## Commands

### Manual Save

```php
// Blocking save (avoid in production)
Redis::save();

// Background save (non-blocking)
Redis::bgsave();

// Background save with schedule option (Redis 7.4+)
Redis::bgsave('SCHEDULE');  // Wait if another save in progress

// Check last save timestamp
$timestamp = Redis::lastsave();
$lastSave = date('Y-m-d H:i:s', $timestamp);
```

### Monitoring Save Status

```php
$info = Redis::info('persistence');

$status = [
    'last_save_time' => date('Y-m-d H:i:s', $info['rdb_last_save_time']),
    'changes_since_save' => $info['rdb_changes_since_last_save'],
    'bgsave_in_progress' => (bool) $info['rdb_bgsave_in_progress'],
    'last_bgsave_status' => $info['rdb_last_bgsave_status'],  // 'ok' or 'err'
    'last_bgsave_time_sec' => $info['rdb_last_bgsave_time_sec'],
    'current_bgsave_time_sec' => $info['rdb_current_bgsave_time_sec'],
];
```

---

## RDB Advantages

| Advantage | Description |
|-----------|-------------|
| **Compact** | Single compressed file |
| **Fast recovery** | Direct memory load, faster than AOF replay |
| **Disaster recovery** | Easy to transfer/backup |
| **Performance** | No impact on normal operations (fork only) |
| **Versions** | Keep multiple snapshots for point-in-time recovery |

---

## RDB Disadvantages

| Disadvantage | Description |
|--------------|-------------|
| **Data loss risk** | Minutes of data can be lost |
| **Fork overhead** | Large datasets = more memory during save |
| **Blocking potential** | Very large datasets may cause brief pauses |
| **Not real-time** | Not suitable for minimal data loss requirements |

---

## Data Loss Calculation

With default configuration (`save 900 1`, `save 300 10`, `save 60 10000`):

| Scenario | Max Data Loss |
|----------|---------------|
| 1-9 changes | 15 minutes |
| 10-9999 changes | 5 minutes |
| 10000+ changes | 1 minute |
| Crash during BGSAVE | Previous interval |

---

## Memory During BGSAVE

### Peak Memory Usage

```
Peak = Current + (Modified Pages × Page Size)

Example: 4 GB dataset, 20% modified during save
Peak = 4 GB + (0.2 × 4 GB) = 4.8 GB
```

### Monitoring Memory During Save

```php
$info = Redis::info('memory');

$memory = [
    'used_memory' => $info['used_memory_human'],
    'used_memory_rss' => $info['used_memory_rss_human'],
    'fork_cow_size' => $info['rdb_last_cow_size'] ?? 'N/A',
];
```

---

## Backup Best Practices

### Safe Backup Procedure

```bash
#!/bin/bash
# Redis RDB backup script

REDIS_DIR="/var/lib/redis"
BACKUP_DIR="/backup/redis"
DATE=$(date +%Y%m%d_%H%M%S)

# Trigger background save
redis-cli BGSAVE

# Wait for save to complete
while [ $(redis-cli LASTSAVE) == $(cat /tmp/last_save 2>/dev/null) ]; do
    sleep 1
done
redis-cli LASTSAVE > /tmp/last_save

# Verify and copy
redis-check-rdb ${REDIS_DIR}/dump.rdb
if [ $? -eq 0 ]; then
    cp ${REDIS_DIR}/dump.rdb ${BACKUP_DIR}/dump_${DATE}.rdb

    # Keep last 7 backups
    ls -t ${BACKUP_DIR}/dump_*.rdb | tail -n +8 | xargs rm -f
fi
```

### Verification

```bash
# Check RDB file integrity
redis-check-rdb /var/lib/redis/dump.rdb

# Output on success
# RDB looks OK!
# Checksum OK
```

### Offsite Backup

```bash
# Compress and upload to S3
gzip -c /var/lib/redis/dump.rdb | \
    aws s3 cp - s3://bucket/redis-backups/dump_$(date +%Y%m%d).rdb.gz
```

---

## Recovery

### Standard Recovery

```bash
# 1. Stop Redis
systemctl stop redis

# 2. Replace dump.rdb
cp /backup/dump_20240101.rdb /var/lib/redis/dump.rdb
chown redis:redis /var/lib/redis/dump.rdb

# 3. Start Redis
systemctl start redis
```

### Verify Recovery

```php
// After restart, verify data
$dbsize = Redis::dbsize();
$info = Redis::info('keyspace');

Log::info("Redis recovered", [
    'keys' => $dbsize,
    'keyspace' => $info,
]);
```

---

## Performance Tuning

### Reduce Fork Impact

```
# Allow overcommit (Linux)
vm.overcommit_memory = 1

# Disable transparent huge pages
echo never > /sys/kernel/mm/transparent_hugepage/enabled
```

### Monitor Fork Time

```php
$info = Redis::info('persistence');

$forkTimeMs = $info['rdb_last_bgsave_time_sec'] * 1000;

if ($forkTimeMs > 1000) {
    Log::warning("Slow RDB save: {$forkTimeMs}ms");
}
```

---

## BudTags Configuration

### Recommended for Cache Database

```
# Low frequency saves for cache data
# Data is regenerable from Metrc API

save 900 1
save 300 100
save 60 10000

rdbcompression yes
rdbchecksum yes
stop-writes-on-bgsave-error yes
```

### For Development

```
# More frequent saves in development
save 300 1
save 60 10
save 15 1000
```

---

## Key Takeaways

1. **Point-in-time snapshots** - Not continuous persistence
2. **Fork-based** - Child process writes, parent serves
3. **Compact files** - LZF compression by default
4. **Fast recovery** - Direct memory load
5. **Data loss possible** - Minutes between saves
6. **Memory overhead** - Copy-on-write during save
7. **Great for backups** - Single file, easy to transfer
8. **Combine with AOF** - For better durability
