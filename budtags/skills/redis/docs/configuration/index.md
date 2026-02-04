# Redis Configuration

Comprehensive guide to Redis configuration options.

---

## Overview

| Topic | File | Description |
|-------|------|-------------|
| redis.conf | [redis-conf.md](./redis-conf.md) | Full configuration reference |
| Runtime Config | [runtime-config.md](./runtime-config.md) | CONFIG GET/SET |

---

## Configuration Sources

### 1. Configuration File

```bash
# Start with config file
redis-server /etc/redis/redis.conf

# Multiple config files
redis-server /etc/redis/redis.conf /etc/redis/local.conf
```

### 2. Command Line

```bash
redis-server --port 6380 --bind 127.0.0.1
```

### 3. Runtime (CONFIG SET)

```php
Redis::config('SET', 'maxmemory', '2gb');
Redis::config('SET', 'maxmemory-policy', 'allkeys-lru');
```

### Priority

Command line > CONFIG SET > Config file

---

## Essential Settings

### Network

```
bind 127.0.0.1              # Listen address
port 6379                   # Listen port
timeout 0                   # Client timeout (0 = disabled)
tcp-keepalive 300           # TCP keepalive
```

### Security

```
requirepass your-password   # Password
protected-mode yes          # Block external access
rename-command FLUSHALL ""  # Disable dangerous commands
```

### Memory

```
maxmemory 2gb               # Memory limit
maxmemory-policy allkeys-lru # Eviction policy
```

### Persistence

```
# RDB
save 900 1
save 300 10
save 60 10000

# AOF
appendonly yes
appendfsync everysec
```

---

## Configuration Categories

### Network & Connections

| Setting | Default | Description |
|---------|---------|-------------|
| `bind` | 127.0.0.1 | Listen addresses |
| `port` | 6379 | Listen port |
| `unixsocket` | - | Unix socket path |
| `timeout` | 0 | Client idle timeout |
| `tcp-keepalive` | 300 | Keepalive interval |
| `maxclients` | 10000 | Max connections |

### Memory Management

| Setting | Default | Description |
|---------|---------|-------------|
| `maxmemory` | 0 | Memory limit (0 = unlimited) |
| `maxmemory-policy` | noeviction | Eviction policy |
| `maxmemory-samples` | 5 | LRU sample size |

### Persistence (RDB)

| Setting | Default | Description |
|---------|---------|-------------|
| `save` | various | Snapshot triggers |
| `dbfilename` | dump.rdb | RDB filename |
| `rdbcompression` | yes | Compress RDB |
| `rdbchecksum` | yes | Verify checksum |

### Persistence (AOF)

| Setting | Default | Description |
|---------|---------|-------------|
| `appendonly` | no | Enable AOF |
| `appendfilename` | appendonly.aof | AOF filename |
| `appendfsync` | everysec | Fsync policy |
| `auto-aof-rewrite-percentage` | 100 | Rewrite threshold |
| `auto-aof-rewrite-min-size` | 64mb | Min size for rewrite |

### Replication

| Setting | Default | Description |
|---------|---------|-------------|
| `replicaof` | - | Master address |
| `masterauth` | - | Master password |
| `replica-read-only` | yes | Read-only replica |
| `repl-diskless-sync` | no | Diskless replication |

### Security

| Setting | Default | Description |
|---------|---------|-------------|
| `requirepass` | - | Password |
| `protected-mode` | yes | Block external |
| `aclfile` | - | ACL file path |

### Performance

| Setting | Default | Description |
|---------|---------|-------------|
| `activedefrag` | no | Active defragmentation |
| `lazyfree-lazy-eviction` | no | Async eviction |
| `lazyfree-lazy-expire` | no | Async expiration |

---

## BudTags Recommended Configuration

### Production Template

```
# Network
bind 10.0.0.5
port 6379
timeout 0
tcp-keepalive 300
maxclients 10000

# Security
requirepass your-strong-password-here
protected-mode yes
rename-command FLUSHALL ""
rename-command CONFIG ""
rename-command DEBUG ""

# Memory
maxmemory 2gb
maxmemory-policy allkeys-lru
maxmemory-samples 10

# Persistence (Hybrid)
appendonly yes
appendfsync everysec
aof-use-rdb-preamble yes
save 900 1
save 300 10
save 60 10000

# Logging
loglevel notice
logfile /var/log/redis/redis.log

# Performance
activedefrag yes
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
```

### Development Template

```
# Network
bind 127.0.0.1
port 6379

# Security (minimal for dev)
protected-mode yes

# Memory
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence (RDB only for dev)
save 900 1
save 300 10
appendonly no

# Logging
loglevel debug
logfile ""
```

---

## Viewing Configuration

### Get All Settings

```php
$config = Redis::config('GET', '*');
```

### Get Specific Settings

```php
$maxmemory = Redis::config('GET', 'maxmemory');
$persistence = Redis::config('GET', 'save');
```

### Rewrite Config File

```php
// Save current config to file
Redis::config('REWRITE');
```

---

## Key Takeaways

1. **Start with defaults** - Only change what you need
2. **Bind securely** - Never bind to 0.0.0.0 without firewall
3. **Set maxmemory** - Prevent OOM killer
4. **Enable persistence** - Appropriate for your use case
5. **Disable dangerous commands** - FLUSHALL, CONFIG, DEBUG
6. **Monitor settings** - CONFIG GET to verify
7. **Document changes** - Keep track of customizations
8. **Test configuration** - Verify before production
