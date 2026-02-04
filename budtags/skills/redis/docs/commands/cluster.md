# Redis Cluster Commands

Cluster commands manage Redis Cluster, which provides automatic data sharding across multiple nodes.

---

## Overview

| Feature | Details |
|---------|---------|
| **Sharding** | 16,384 hash slots distributed across nodes |
| **Replication** | Each master can have replicas |
| **Failover** | Automatic promotion of replicas |
| **Multi-key** | Only works for keys in same slot |

---

## Slot Management

### CLUSTER SLOTS (Deprecated)

Use CLUSTER SHARDS instead.

### CLUSTER SHARDS

Returns cluster shard information.

```
CLUSTER SHARDS
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of shard information |
| **Since** | Redis 7.0 |

---

### CLUSTER KEYSLOT

Returns the hash slot for a key.

```
CLUSTER KEYSLOT key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - slot number (0-16383) |
| **Complexity** | O(N) where N is key length |

```php
$slot = Redis::cluster('KEYSLOT', 'mykey');
// Returns: 5798 (or similar)
```

---

### CLUSTER COUNTKEYSINSLOT

Counts keys in a hash slot.

```
CLUSTER COUNTKEYSINSLOT slot
```

---

### CLUSTER GETKEYSINSLOT

Returns keys in a hash slot.

```
CLUSTER GETKEYSINSLOT slot count
```

---

### CLUSTER ADDSLOTS

Assigns hash slots to current node.

```
CLUSTER ADDSLOTS slot [slot ...]
```

---

### CLUSTER ADDSLOTSRANGE

Assigns hash slot ranges.

```
CLUSTER ADDSLOTSRANGE start-slot end-slot [start-slot end-slot ...]
```

---

### CLUSTER DELSLOTS

Removes hash slot assignments.

```
CLUSTER DELSLOTS slot [slot ...]
```

---

### CLUSTER DELSLOTSRANGE

Removes hash slot range assignments.

```
CLUSTER DELSLOTSRANGE start-slot end-slot [start-slot end-slot ...]
```

---

### CLUSTER SETSLOT

Configures a slot for migration or node binding.

```
CLUSTER SETSLOT slot IMPORTING|MIGRATING|STABLE|NODE node-id
```

| State | Description |
|-------|-------------|
| `IMPORTING` | Slot is being imported from another node |
| `MIGRATING` | Slot is being migrated to another node |
| `STABLE` | Clear importing/migrating state |
| `NODE` | Bind slot to specified node |

---

### CLUSTER FLUSHSLOTS

Removes all slot assignments from node.

```
CLUSTER FLUSHSLOTS
```

---

## Node Management

### CLUSTER NODES

Returns cluster configuration.

```
CLUSTER NODES
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string with node configuration |
| **Complexity** | O(N) |

Output includes node IDs, addresses, flags, slots, etc.

---

### CLUSTER MYID

Returns current node's ID.

```
CLUSTER MYID
```

---

### CLUSTER MYSHARDID

Returns current node's shard ID.

```
CLUSTER MYSHARDID
```

| Aspect | Details |
|--------|---------|
| **Since** | Redis 7.2 |

---

### CLUSTER INFO

Returns cluster state information.

```
CLUSTER INFO
```

| Aspect | Details |
|--------|---------|
| **Returns** | Cluster state, slots assigned, etc. |
| **Complexity** | O(1) |

Key fields:
- `cluster_state` - ok or fail
- `cluster_slots_assigned` - slots assigned to nodes
- `cluster_slots_ok` - slots in working state
- `cluster_known_nodes` - known node count

---

### CLUSTER MEET

Joins nodes together.

```
CLUSTER MEET ip port
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(1) |

---

### CLUSTER FORGET

Removes a node from cluster.

```
CLUSTER FORGET node-id
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Note** | Must be executed on all nodes |

---

### CLUSTER REPLICATE

Makes current node a replica.

```
CLUSTER REPLICATE node-id
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Note** | Target must be a master |

---

### CLUSTER REPLICAS

Lists replicas of a master.

```
CLUSTER REPLICAS node-id
```

---

### CLUSTER LINKS

Lists cluster bus connections.

```
CLUSTER LINKS
```

| Aspect | Details |
|--------|---------|
| **Since** | Redis 7.0 |

---

## Failover

### CLUSTER FAILOVER

Triggers manual failover.

```
CLUSTER FAILOVER [FORCE|TAKEOVER]
```

| Option | Description |
|--------|-------------|
| (none) | Coordinated failover - waits for master |
| `FORCE` | Force failover even if master unreachable |
| `TAKEOVER` | Force without cluster consensus |

Must be executed on a replica.

---

## Configuration

### CLUSTER BUMPEPOCH

Advances the cluster config epoch.

```
CLUSTER BUMPEPOCH
```

---

### CLUSTER SET-CONFIG-EPOCH

Sets the config epoch for new nodes.

```
CLUSTER SET-CONFIG-EPOCH config-epoch
```

---

### CLUSTER SAVECONFIG

Saves cluster config to disk.

```
CLUSTER SAVECONFIG
```

---

### CLUSTER RESET

Resets the cluster node.

```
CLUSTER RESET [SOFT|HARD]
```

| Option | Description |
|--------|-------------|
| `SOFT` | Reset slots and known nodes |
| `HARD` | Reset everything including node ID |

---

## Migration

### CLUSTER MIGRATION

Manages slot migration (Redis 8.0+).

```
CLUSTER MIGRATION node-id slot START|STATUS|ABORT
```

---

## Diagnostics

### CLUSTER COUNT-FAILURE-REPORTS

Counts failure reports for a node.

```
CLUSTER COUNT-FAILURE-REPORTS node-id
```

---

### CLUSTER SLOT-STATS

Returns slot usage statistics.

```
CLUSTER SLOT-STATS
```

| Aspect | Details |
|--------|---------|
| **Since** | Redis 7.4 |

---

## Client Command

### ASKING

Signals redirect acceptance.

```
ASKING
```

Clients send this after receiving -ASK redirect, before the redirected command.

---

## Hash Tags

Force keys to same slot using hash tags:

```php
// These keys will be in the same slot
$key1 = 'user:{123}:profile';
$key2 = 'user:{123}:settings';
$key3 = 'user:{123}:notifications';

// Only content within first {} is hashed
Redis::cluster('KEYSLOT', 'user:{123}:profile');    // Same slot
Redis::cluster('KEYSLOT', 'user:{123}:settings');   // Same slot
```

This enables multi-key operations on related keys.

---

## Redirect Handling

Cluster clients must handle redirects:

| Redirect | Meaning |
|----------|---------|
| `-MOVED slot ip:port` | Slot permanently moved to another node |
| `-ASK slot ip:port` | Slot temporarily at another node (migration) |

```php
// Laravel/Predis handles this automatically
// But if using raw commands:
try {
    $result = Redis::get('key');
} catch (\Exception $e) {
    if (str_contains($e->getMessage(), 'MOVED')) {
        // Parse redirect and retry on correct node
    }
}
```

---

## BudTags Considerations

BudTags uses standalone Redis (not cluster):

```php
// config/database.php shows:
// REDIS_DB=0, REDIS_CACHE_DB=1, REDIS_QUEUE_DB=2
// This is database-based separation, not clustering
```

If migrating to cluster:
1. Use hash tags for related keys
2. Remove multi-database usage
3. Handle cross-slot operations differently
4. Test all multi-key operations

---

## Performance Notes

| Command | Complexity | Notes |
|---------|------------|-------|
| CLUSTER KEYSLOT | O(N) | N = key length |
| CLUSTER INFO | O(1) | Fast |
| CLUSTER NODES | O(N) | N = nodes |
| CLUSTER SLOTS | O(N) | N = slots |

**Best Practices:**
- Use hash tags for multi-key atomicity
- Monitor cluster state regularly
- Test failover scenarios
- Keep replicas synchronized
- Size nodes appropriately for data
