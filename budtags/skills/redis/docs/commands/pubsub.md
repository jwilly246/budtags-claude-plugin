# Redis Pub/Sub Commands

Pub/Sub implements a publish/subscribe messaging paradigm where senders (publishers) send messages to channels without knowledge of receivers (subscribers).

---

## Publishing

### PUBLISH

Sends a message to a channel.

```
PUBLISH channel message
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of subscribers that received the message |
| **Complexity** | O(N+M) where N is subscribers, M is pattern subscribers |

```php
// Publish event
$subscribers = Redis::publish('events', json_encode([
    'type' => 'user.created',
    'user_id' => 123,
    'timestamp' => time()
]));

// Publish to specific channel
Redis::publish('notifications:user:123', 'You have a new message');
```

---

## Subscribing

### SUBSCRIBE

Subscribes to channels.

```
SUBSCRIBE channel [channel ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Subscription confirmation, then messages |
| **Complexity** | O(N) where N is channels |
| **Blocking** | Yes - enters subscription mode |

Once subscribed, the connection can only use SUBSCRIBE, PSUBSCRIBE, UNSUBSCRIBE, PUNSUBSCRIBE, PING, RESET, and QUIT.

```php
// Laravel doesn't have native blocking subscribe, use raw connection
// or use Laravel Echo with Redis broadcaster
Redis::subscribe(['events'], function ($message) {
    echo "Received: {$message}\n";
});
```

---

### UNSUBSCRIBE

Unsubscribes from channels.

```
UNSUBSCRIBE [channel ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Unsubscription confirmation |
| **Note** | Without arguments, unsubscribes from all |

---

### PSUBSCRIBE

Subscribes to pattern-matched channels.

```
PSUBSCRIBE pattern [pattern ...]
```

| Pattern | Matches |
|---------|---------|
| `*` | All channels |
| `news.*` | news.sports, news.tech, etc. |
| `user:*:events` | user:123:events, user:456:events |
| `h?llo` | hello, hallo, hxllo |

| Aspect | Details |
|--------|---------|
| **Returns** | Pattern subscription confirmation, then messages |
| **Complexity** | O(N) where N is patterns |

```php
Redis::psubscribe(['user:*'], function ($message, $channel) {
    echo "Channel {$channel}: {$message}\n";
});
```

---

### PUNSUBSCRIBE

Unsubscribes from pattern subscriptions.

```
PUNSUBSCRIBE [pattern ...]
```

---

## Introspection

### PUBSUB CHANNELS

Lists active channels.

```
PUBSUB CHANNELS [pattern]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of channel names |
| **Complexity** | O(N) where N is active channels |

```php
// Get all active channels
$channels = Redis::pubsub('CHANNELS');

// Get channels matching pattern
$userChannels = Redis::pubsub('CHANNELS', 'user:*');
```

---

### PUBSUB NUMSUB

Returns subscriber count for channels.

```
PUBSUB NUMSUB [channel ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of [channel, count, channel, count, ...] |
| **Complexity** | O(N) where N is channels |

```php
$counts = Redis::pubsub('NUMSUB', 'events', 'notifications');
// ['events', 5, 'notifications', 2]
```

---

### PUBSUB NUMPAT

Returns total pattern subscriptions.

```
PUBSUB NUMPAT
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - total pattern subscriptions |
| **Complexity** | O(1) |

---

## Sharded Pub/Sub (Redis 7.0+)

Sharded pub/sub localizes messages to the shard where the channel's key would hash, reducing cross-node traffic in clusters.

### SPUBLISH

Publishes to a shard channel.

```
SPUBLISH shardchannel message
```

---

### SSUBSCRIBE

Subscribes to shard channels.

```
SSUBSCRIBE shardchannel [shardchannel ...]
```

---

### SUNSUBSCRIBE

Unsubscribes from shard channels.

```
SUNSUBSCRIBE [shardchannel ...]
```

---

### PUBSUB SHARDCHANNELS

Lists active shard channels.

```
PUBSUB SHARDCHANNELS [pattern]
```

---

### PUBSUB SHARDNUMSUB

Returns subscriber count for shard channels.

```
PUBSUB SHARDNUMSUB [shardchannel ...]
```

---

## Laravel Broadcasting

Laravel uses Redis Pub/Sub for real-time broadcasting.

### Configuration

```php
// config/broadcasting.php
'connections' => [
    'redis' => [
        'driver' => 'redis',
        'connection' => 'default',
    ],
],
```

### Broadcasting Events

```php
// Event class
class OrderShipped implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public function __construct(public Order $order) {}

    public function broadcastOn(): array
    {
        return [
            new PrivateChannel('orders.' . $this->order->user_id),
        ];
    }
}

// Dispatch event
event(new OrderShipped($order));
```

### Laravel Echo (Client-side)

```javascript
Echo.private(`orders.${userId}`)
    .listen('OrderShipped', (e) => {
        console.log(e.order);
    });
```

---

## Use Cases

### Real-time Notifications

```php
// Publisher (backend)
class NotificationService
{
    public function notifyUser(int $userId, array $notification): void
    {
        Redis::publish(
            "notifications:user:{$userId}",
            json_encode($notification)
        );
    }
}

// Subscriber (separate process)
Redis::subscribe(['notifications:user:*'], function ($message, $channel) {
    $notification = json_decode($message, true);
    // Push to WebSocket, etc.
});
```

### Cache Invalidation

```php
// Publisher: when data changes
public function updateProduct(Product $product): void
{
    $product->save();

    Redis::publish('cache:invalidate', json_encode([
        'type' => 'product',
        'id' => $product->id
    ]));
}

// Subscriber: multiple app servers
Redis::subscribe(['cache:invalidate'], function ($message) {
    $data = json_decode($message, true);
    Cache::forget("product:{$data['id']}");
});
```

### Activity Streams

```php
// Publish user activity
public function trackActivity(User $user, string $action): void
{
    Redis::publish('activity:stream', json_encode([
        'user_id' => $user->id,
        'action' => $action,
        'timestamp' => now()->toIso8601String()
    ]));
}

// Subscribe to activity feed
Redis::psubscribe(['activity:*'], function ($message, $channel) {
    // Process activity for analytics, logging, etc.
});
```

### Chat Messages

```php
// Send message to room
public function sendMessage(string $room, User $user, string $message): void
{
    Redis::publish("chat:room:{$room}", json_encode([
        'user' => $user->only(['id', 'name']),
        'message' => $message,
        'timestamp' => now()->toIso8601String()
    ]));
}

// Join room (subscriber)
Redis::subscribe(["chat:room:{$roomId}"], function ($message) {
    // Forward to WebSocket clients
});
```

---

## Important Characteristics

### Fire-and-Forget

- Messages are NOT persisted
- If no subscribers, message is lost
- Subscribers only receive messages after subscribing

### No Acknowledgment

- Publishers don't know if subscribers processed message
- No retry mechanism
- No guaranteed delivery

### Pattern Overhead

- Pattern subscriptions check every published message
- Can be slower than direct subscriptions
- Use sparingly in high-volume scenarios

---

## Pub/Sub vs Streams

| Feature | Pub/Sub | Streams |
|---------|---------|---------|
| Persistence | No | Yes |
| History | No | Yes |
| Consumer Groups | No | Yes |
| Acknowledgment | No | Yes |
| Latency | Lower | Slightly higher |
| Use Case | Real-time, transient | Durable messaging |

**Use Pub/Sub for:**
- Real-time updates where loss is acceptable
- Broadcasts to many subscribers
- Chat, notifications, cache invalidation

**Use Streams for:**
- Messages that must be processed
- Consumer groups
- Audit logs, event sourcing

---

## Performance Notes

| Aspect | Details |
|--------|---------|
| Publish | O(N+M) - N subscribers + M pattern matches |
| Subscribe | O(1) per channel |
| Pattern match | Checked for every message |
| Connection | Dedicated connection per subscriber |

**Best Practices:**
- Use separate connections for pub/sub
- Limit pattern subscriptions
- Don't rely on delivery guarantees
- Consider Streams for durability
- Use sharded pub/sub in clusters
