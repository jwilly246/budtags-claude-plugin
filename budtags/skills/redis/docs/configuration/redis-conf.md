# Redis Configuration Reference (redis.conf)

Complete reference for Redis 7.x configuration options.

---

## Network

```
# Bind to specific interfaces (comma-separated)
bind 127.0.0.1 -::1

# Accept connections on port
port 6379

# Unix socket (alternative to TCP)
unixsocket /var/run/redis/redis.sock
unixsocketperm 700

# Close connection after N seconds of idle (0 = disabled)
timeout 0

# TCP keepalive (in seconds)
tcp-keepalive 300

# TCP backlog (connection queue)
tcp-backlog 511
```

---

## General

```
# Run as daemon
daemonize no

# Supervised by systemd/upstart
supervised auto

# PID file location
pidfile /var/run/redis_6379.pid

# Log level: debug, verbose, notice, warning
loglevel notice

# Log file (empty = stdout)
logfile /var/log/redis/redis.log

# Number of databases (0-15 default)
databases 16

# Show ASCII logo at startup
always-show-logo no
```

---

## Security

```
# Password for all clients
requirepass your-password-here

# ACL configuration file
aclfile /etc/redis/users.acl

# ACL log max length
acllog-max-len 128

# Protected mode (block external connections when no auth)
protected-mode yes

# Rename dangerous commands
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command CONFIG "CONFIG_SECRET_NAME"
rename-command DEBUG ""
rename-command SHUTDOWN SHUTDOWN_SECRET
```

---

## Memory

```
# Maximum memory (bytes, kb, mb, gb)
maxmemory 2gb

# Eviction policy when maxmemory reached
# noeviction, allkeys-lru, allkeys-lfu, volatile-lru, volatile-lfu,
# allkeys-random, volatile-random, volatile-ttl
maxmemory-policy allkeys-lru

# LRU/LFU sample size (higher = more accurate, more CPU)
maxmemory-samples 10

# Eviction processing per loop (higher = more aggressive)
maxmemory-eviction-tenacity 10

# Replica ignore maxmemory (allow replicas to exceed)
replica-ignore-maxmemory yes

# Active memory defragmentation
activedefrag yes
active-defrag-ignore-bytes 100mb
active-defrag-threshold-lower 10
active-defrag-threshold-upper 100
active-defrag-cycle-min 1
active-defrag-cycle-max 25
active-defrag-max-scan-fields 1000
```

---

## RDB Persistence

```
# Save triggers: save <seconds> <changes>
save 900 1      # At least 1 change in 900 seconds
save 300 10     # At least 10 changes in 300 seconds
save 60 10000   # At least 10000 changes in 60 seconds

# Disable RDB
save ""

# Stop writes on bgsave error
stop-writes-on-bgsave-error yes

# Compress RDB with LZF
rdbcompression yes

# Verify RDB checksum on load
rdbchecksum yes

# RDB filename
dbfilename dump.rdb

# Delete RDB on replica desync
rdb-del-sync-files no

# Working directory for RDB/AOF
dir /var/lib/redis
```

---

## AOF Persistence

```
# Enable AOF
appendonly yes

# AOF directory (Redis 7+)
appenddirname "appendonlydir"

# AOF filename
appendfilename "appendonly.aof"

# Fsync policy: always, everysec, no
appendfsync everysec

# Don't fsync during rewrite (faster, less safe)
no-appendfsync-on-rewrite no

# Auto-rewrite thresholds
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Load truncated AOF (yes = load partial, no = refuse to start)
aof-load-truncated yes

# Use RDB preamble in AOF (faster loading)
aof-use-rdb-preamble yes

# AOF rewrite incremental fsync
aof-rewrite-incremental-fsync yes

# AOF timestamp
aof-timestamp-enabled no
```

---

## Replication

```
# Make this instance a replica
replicaof <masterip> <masterport>

# Master password
masterauth <master-password>

# Master user (ACL)
masteruser <master-username>

# Replica read-only
replica-read-only yes

# Diskless replication (send RDB over socket)
repl-diskless-sync yes
repl-diskless-sync-delay 5
repl-diskless-sync-max-replicas 0

# Replication backlog
repl-backlog-size 1mb
repl-backlog-ttl 3600

# Replica priority (lower = higher priority for promotion)
replica-priority 100

# Minimum replicas for writes
min-replicas-to-write 0
min-replicas-max-lag 10

# Replica announce address (for NAT)
replica-announce-ip <ip>
replica-announce-port <port>
```

---

## Cluster

```
# Enable cluster mode
cluster-enabled yes

# Cluster config file (auto-generated)
cluster-config-file nodes.conf

# Node timeout (ms)
cluster-node-timeout 15000

# Failover settings
cluster-replica-validity-factor 10
cluster-migration-barrier 1
cluster-require-full-coverage yes
cluster-replica-no-failover no

# Allow reads during failure
cluster-allow-reads-when-down no

# Prefer replica reads
cluster-allow-replica-migration yes
```

---

## Clients

```
# Max clients
maxclients 10000

# Output buffer limits
# client-output-buffer-limit <class> <hard limit> <soft limit> <soft seconds>
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60

# Client query buffer limit
client-query-buffer-limit 1gb
```

---

## Scripting

```
# Lua script timeout (ms)
lua-time-limit 5000

# Enable function persistence
lua-replicate-commands yes
```

---

## Slow Log

```
# Log commands slower than (microseconds)
slowlog-log-slower-than 10000

# Max slow log entries
slowlog-max-len 128
```

---

## Latency Monitoring

```
# Latency monitoring threshold (ms, 0 = disabled)
latency-monitor-threshold 0
```

---

## Lazy Freeing

```
# Async deletion for eviction
lazyfree-lazy-eviction yes

# Async deletion for expiration
lazyfree-lazy-expire yes

# Async deletion for DEL command
lazyfree-lazy-server-del yes

# Async flush during replica sync
replica-lazy-flush yes

# Async deletion on key/DB overwrite
lazyfree-lazy-user-del yes
lazyfree-lazy-user-flush yes
```

---

## TLS/SSL

```
# TLS port (use 0 to disable non-TLS)
tls-port 6379
port 0

# Certificate files
tls-cert-file /etc/redis/tls/redis.crt
tls-key-file /etc/redis/tls/redis.key
tls-ca-cert-file /etc/redis/tls/ca.crt

# Require client certificates
tls-auth-clients no

# TLS versions
tls-protocols "TLSv1.2 TLSv1.3"

# TLS for replication
tls-replication yes

# TLS for cluster
tls-cluster yes

# Session caching
tls-session-caching yes
tls-session-cache-size 20480
tls-session-cache-timeout 300
```

---

## Data Structure Encoding

```
# Hash encoding thresholds
hash-max-listpack-entries 512
hash-max-listpack-value 64

# List encoding
list-max-listpack-size -2
list-compress-depth 0

# Set encoding
set-max-intset-entries 512
set-max-listpack-entries 128
set-max-listpack-value 64

# Sorted set encoding
zset-max-listpack-entries 128
zset-max-listpack-value 64

# HyperLogLog sparse encoding
hll-sparse-max-bytes 3000

# Stream encoding
stream-node-max-bytes 4096
stream-node-max-entries 100
```

---

## Advanced

```
# Hash seed for randomization
hash-seed random

# Active rehashing
activerehashing yes

# Client output buffer resize
dynamic-hz yes

# Server frequency
hz 10

# Jemalloc background threads
jemalloc-bg-thread yes

# Ignore RDB/AOF read errors (dangerous)
ignore-warnings ARM64-COW-BUG
```

---

## Key Takeaways

1. **Defaults are sensible** - Start there
2. **Security first** - `requirepass`, `protected-mode`, rename commands
3. **Memory limits** - Always set `maxmemory` in production
4. **Persistence choice** - RDB for speed, AOF for durability
5. **Encoding thresholds** - Tune for your data patterns
6. **Lazy freeing** - Enable for large datasets
7. **TLS for cross-network** - When data leaves private network
8. **Document changes** - Keep notes on customizations
