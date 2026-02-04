# Redis TLS/SSL

Encrypting Redis connections for data in transit.

---

## When to Use TLS

| Scenario | TLS Needed |
|----------|------------|
| Same server (localhost) | No |
| Same private network | Optional |
| Across VPCs/networks | Yes |
| Public internet | Yes (but avoid) |
| Compliance requirements | Yes |

---

## Server Configuration

### Generate Certificates

```bash
# Create CA
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "/CN=Redis CA"

# Create server certificate
openssl genrsa -out redis.key 2048
openssl req -new -key redis.key -out redis.csr \
  -subj "/CN=redis-server"
openssl x509 -req -days 365 -in redis.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out redis.crt

# Create client certificate (optional, for mTLS)
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr \
  -subj "/CN=redis-client"
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out client.crt
```

### redis.conf

```
# Enable TLS port, disable plain port
tls-port 6379
port 0

# Certificate files
tls-cert-file /etc/redis/tls/redis.crt
tls-key-file /etc/redis/tls/redis.key
tls-ca-cert-file /etc/redis/tls/ca.crt

# Optional: Require client certificates (mTLS)
# tls-auth-clients yes

# Optional: Allow both TLS and non-TLS
# port 6379
# tls-port 6380

# Disable older TLS versions
tls-protocols "TLSv1.2 TLSv1.3"

# Cipher suites (optional)
# tls-ciphers DEFAULT:!MEDIUM

# TLS for replication
tls-replication yes

# TLS for cluster bus
tls-cluster yes
```

### Verify Configuration

```bash
# Test TLS connection
redis-cli --tls \
  --cert /etc/redis/tls/client.crt \
  --key /etc/redis/tls/client.key \
  --cacert /etc/redis/tls/ca.crt \
  -h redis-server -p 6379 PING
```

---

## Laravel Configuration

### phpredis with TLS

```php
// config/database.php
'redis' => [
    'client' => 'phpredis',

    'default' => [
        'scheme' => 'tls',
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', 6379),
        'database' => 0,
        'context' => [
            'ssl' => [
                'verify_peer' => true,
                'verify_peer_name' => true,
                'cafile' => env('REDIS_TLS_CA_CERT'),
                // For mTLS:
                // 'local_cert' => env('REDIS_TLS_CLIENT_CERT'),
                // 'local_pk' => env('REDIS_TLS_CLIENT_KEY'),
            ],
        ],
    ],
],
```

### Predis with TLS

```php
// config/database.php
'redis' => [
    'client' => 'predis',

    'default' => [
        'scheme' => 'tls',
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', 6379),
        'database' => 0,
        'ssl' => [
            'verify_peer' => true,
            'verify_peer_name' => true,
            'cafile' => env('REDIS_TLS_CA_CERT'),
        ],
    ],
],
```

### Environment Variables

```env
REDIS_HOST=redis.example.com
REDIS_PORT=6379
REDIS_PASSWORD=your-password
REDIS_TLS_CA_CERT=/path/to/ca.crt
REDIS_TLS_CLIENT_CERT=/path/to/client.crt
REDIS_TLS_CLIENT_KEY=/path/to/client.key
```

---

## Mutual TLS (mTLS)

Client certificates for additional security:

### Server Configuration

```
# redis.conf
tls-auth-clients yes
tls-ca-cert-file /etc/redis/tls/ca.crt
```

### Laravel Configuration

```php
'default' => [
    'scheme' => 'tls',
    'host' => env('REDIS_HOST'),
    'port' => env('REDIS_PORT', 6379),
    'context' => [
        'ssl' => [
            'verify_peer' => true,
            'cafile' => env('REDIS_TLS_CA_CERT'),
            'local_cert' => env('REDIS_TLS_CLIENT_CERT'),
            'local_pk' => env('REDIS_TLS_CLIENT_KEY'),
        ],
    ],
],
```

---

## Replication with TLS

### Master

```
tls-port 6379
port 0
tls-replication yes
tls-cert-file /etc/redis/tls/redis.crt
tls-key-file /etc/redis/tls/redis.key
tls-ca-cert-file /etc/redis/tls/ca.crt
```

### Replica

```
tls-port 6379
port 0
tls-replication yes
tls-cert-file /etc/redis/tls/redis.crt
tls-key-file /etc/redis/tls/redis.key
tls-ca-cert-file /etc/redis/tls/ca.crt

replicaof master-host 6379
```

---

## Sentinel with TLS

### sentinel.conf

```
port 0
tls-port 26379

tls-cert-file /etc/redis/tls/sentinel.crt
tls-key-file /etc/redis/tls/sentinel.key
tls-ca-cert-file /etc/redis/tls/ca.crt

tls-replication yes

sentinel monitor mymaster master-host 6379 2
```

---

## Cluster with TLS

### redis.conf (each node)

```
tls-port 6379
port 0
tls-cluster yes
tls-replication yes

tls-cert-file /etc/redis/tls/redis.crt
tls-key-file /etc/redis/tls/redis.key
tls-ca-cert-file /etc/redis/tls/ca.crt

cluster-enabled yes
```

### Create Cluster

```bash
redis-cli --tls \
  --cert /etc/redis/tls/client.crt \
  --key /etc/redis/tls/client.key \
  --cacert /etc/redis/tls/ca.crt \
  --cluster create node1:6379 node2:6379 node3:6379 \
  --cluster-replicas 0
```

---

## Certificate Management

### Certificate Rotation

```bash
# Generate new certificate
openssl genrsa -out redis-new.key 2048
openssl req -new -key redis-new.key -out redis-new.csr
openssl x509 -req -days 365 -in redis-new.csr \
  -CA ca.crt -CAkey ca.key -out redis-new.crt

# Replace certificates
cp redis-new.crt /etc/redis/tls/redis.crt
cp redis-new.key /etc/redis/tls/redis.key

# Reload Redis (no restart needed for cert reload)
redis-cli DEBUG RELOAD-CONFIG
```

### Certificate Monitoring

```php
class CertificateMonitor
{
    public function checkExpiry(string $certPath, int $warningDays = 30): array
    {
        $cert = openssl_x509_parse(file_get_contents($certPath));
        $expiryTime = $cert['validTo_time_t'];
        $daysUntilExpiry = ($expiryTime - time()) / 86400;

        return [
            'path' => $certPath,
            'expires' => date('Y-m-d', $expiryTime),
            'days_remaining' => (int) $daysUntilExpiry,
            'warning' => $daysUntilExpiry < $warningDays,
        ];
    }
}

// Monitor
Schedule::daily(function () {
    $monitor = new CertificateMonitor();
    $certs = [
        env('REDIS_TLS_CA_CERT'),
        env('REDIS_TLS_CLIENT_CERT'),
    ];

    foreach ($certs as $cert) {
        $status = $monitor->checkExpiry($cert);
        if ($status['warning']) {
            Log::warning("Redis certificate expiring soon", $status);
        }
    }
});
```

---

## Performance Impact

TLS adds overhead:

| Metric | Plain | TLS | Impact |
|--------|-------|-----|--------|
| Latency | 0.1ms | 0.2ms | +0.1ms |
| Throughput | 100K | 80K | -20% |
| CPU | Low | Medium | +30% |
| Handshake | N/A | 2-5ms | Per connection |

**Mitigation:**
- Use persistent connections
- Use TLSv1.3 (faster handshake)
- Consider connection pooling

---

## Troubleshooting

### Connection Refused

```bash
# Check TLS port is open
openssl s_client -connect redis-host:6379

# Verify certificate
openssl x509 -in redis.crt -text -noout
```

### Certificate Errors

```php
// Temporarily disable verification for debugging
'context' => [
    'ssl' => [
        'verify_peer' => false,  // Don't use in production!
    ],
],
```

### Check Connection

```php
try {
    Redis::ping();
} catch (\Exception $e) {
    Log::error('Redis TLS connection failed', [
        'error' => $e->getMessage(),
    ]);
}
```

---

## Key Takeaways

1. **Use for cross-network** - Required when traffic leaves trusted network
2. **TLSv1.2+ only** - Disable older versions
3. **Persistent connections** - Reduce handshake overhead
4. **mTLS for high security** - Client certificates add authentication
5. **Monitor certificates** - Alert before expiry
6. **Performance impact** - ~20% throughput reduction
7. **Apply to replication** - Enable tls-replication
8. **Cluster bus** - Enable tls-cluster
