# Redis Pub/Sub

Real-time messaging with publish/subscribe pattern.

---

## Overview

Pub/Sub enables:
- Real-time message broadcasting
- Decoupled publishers and subscribers
- Pattern-based subscriptions
- Fire-and-forget messaging

**Note:** Messages are NOT persisted. Use Streams for durable messaging.

---

## Basic Commands

### Publishing

```php
// Publish message to channel
$subscribers = Redis::publish('channel:name', 'Hello, World!');
// Returns number of subscribers that received the message
```

### Subscribing

```php
// Subscribe blocks - must run in separate process
Redis::subscribe(['channel:name'], function ($message, $channel) {
    echo "Received: {$message} on {$channel}\n";
});
```

### Pattern Subscription

```php
// Subscribe to pattern
Redis::psubscribe(['user:*'], function ($message, $channel, $pattern) {
    echo "Pattern: {$pattern}, Channel: {$channel}, Message: {$message}\n";
});

// Matches: user:123, user:abc, user:updates, etc.
```

---

## Laravel Broadcasting

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

### Event Broadcasting

```php
// app/Events/OrderUpdated.php
class OrderUpdated implements ShouldBroadcast
{
    public function __construct(public Order $order) {}

    public function broadcastOn(): array
    {
        return [
            new PrivateChannel('orders.' . $this->order->organization_id),
        ];
    }

    public function broadcastWith(): array
    {
        return [
            'order_id' => $this->order->id,
            'status' => $this->order->status,
        ];
    }
}
```

### Broadcasting Events

```php
// Dispatch event
broadcast(new OrderUpdated($order));

// Or dispatch without waiting
broadcast(new OrderUpdated($order))->toOthers();
```

---

## Low-Level Pub/Sub

### Publisher Service

```php
class MessagePublisher
{
    public function broadcast(string $channel, array $data): int
    {
        return Redis::publish($channel, json_encode([
            'data' => $data,
            'timestamp' => now()->toIso8601String(),
        ]));
    }

    public function notifyUser(int $userId, string $type, array $data): int
    {
        return $this->broadcast("user:{$userId}", [
            'type' => $type,
            ...$data,
        ]);
    }

    public function notifyOrganization(int $orgId, string $type, array $data): int
    {
        return $this->broadcast("org:{$orgId}", [
            'type' => $type,
            ...$data,
        ]);
    }
}
```

### Subscriber Worker

```php
// app/Console/Commands/SubscribeWorker.php
class SubscribeWorker extends Command
{
    protected $signature = 'subscribe:worker {channel}';

    public function handle(): void
    {
        $channel = $this->argument('channel');

        $this->info("Subscribing to: {$channel}");

        Redis::subscribe([$channel], function ($message, $channel) {
            $data = json_decode($message, true);

            $this->processMessage($channel, $data);
        });
    }

    private function processMessage(string $channel, array $data): void
    {
        $this->info("Received on {$channel}: " . json_encode($data));

        // Process based on message type
        match ($data['type'] ?? null) {
            'notification' => $this->handleNotification($data),
            'update' => $this->handleUpdate($data),
            default => $this->warn("Unknown message type"),
        };
    }
}
```

---

## Pattern Subscriptions

### Examples

```php
// All user channels
Redis::psubscribe(['user:*'], function ($message, $channel, $pattern) {
    // Matches: user:1, user:123, user:abc
});

// All notification channels
Redis::psubscribe(['notification:*:*'], function ($message, $channel, $pattern) {
    // Matches: notification:org:1, notification:user:123
});

// Multiple patterns
Redis::psubscribe(['user:*', 'org:*'], function ($message, $channel, $pattern) {
    // Matches both patterns
});
```

### Pattern Syntax

| Pattern | Matches |
|---------|---------|
| `h?llo` | hello, hallo, hxllo |
| `h*llo` | hllo, heeeello |
| `h[ae]llo` | hello, hallo |
| `h[^e]llo` | hallo, hbllo (not hello) |
| `h[a-b]llo` | hallo, hbllo |

---

## Pub/Sub Commands

```php
// List active channels
$channels = Redis::pubsub('CHANNELS');

// List channels matching pattern
$channels = Redis::pubsub('CHANNELS', 'user:*');

// Count subscribers per channel
$counts = Redis::pubsub('NUMSUB', 'channel1', 'channel2');

// Count pattern subscribers
$count = Redis::pubsub('NUMPAT');
```

---

## Real-Time Notifications

### Notification System

```php
class RealtimeNotifier
{
    public function notifySync(string $syncId, string $status, array $progress): void
    {
        Redis::publish("sync:{$syncId}", json_encode([
            'event' => 'progress',
            'status' => $status,
            'progress' => $progress,
            'timestamp' => now()->toIso8601String(),
        ]));
    }

    public function notifySyncComplete(string $syncId, array $summary): void
    {
        Redis::publish("sync:{$syncId}", json_encode([
            'event' => 'complete',
            'summary' => $summary,
            'timestamp' => now()->toIso8601String(),
        ]));
    }
}
```

### Frontend Integration (Laravel Echo)

```javascript
// Subscribe to channel
Echo.channel('sync.' + syncId)
    .listen('SyncProgress', (e) => {
        console.log('Progress:', e.progress);
    })
    .listen('SyncComplete', (e) => {
        console.log('Complete:', e.summary);
    });
```

---

## Limitations

### No Message Persistence

```
Publisher publishes → No subscribers → Message lost
```

**Solution:** Use Streams for durable messaging:
```php
// Instead of publish (fire-and-forget)
Redis::xadd('events', '*', 'type', 'notification', 'data', json_encode($data));
```

### Blocking Subscription

```php
// SUBSCRIBE blocks the connection
Redis::subscribe(['channel'], function ($message) {
    // This blocks until unsubscribed
});
```

**Solution:** Run subscribers in separate processes:
```bash
php artisan subscribe:worker channel &
```

### No Guaranteed Delivery

- At-most-once delivery
- No acknowledgments
- No retry mechanism

---

## Pub/Sub vs Streams

| Feature | Pub/Sub | Streams |
|---------|---------|---------|
| Persistence | No | Yes |
| History | No | Yes |
| Consumer groups | No | Yes |
| Acknowledgments | No | Yes |
| Replay | No | Yes |
| Use case | Real-time, ephemeral | Reliable messaging |

---

## Best Practices

### 1. Use JSON for Messages

```php
Redis::publish('channel', json_encode([
    'type' => 'event_type',
    'data' => $data,
    'timestamp' => time(),
]));
```

### 2. Handle Reconnection

```php
while (true) {
    try {
        Redis::subscribe(['channel'], function ($message) {
            // Process message
        });
    } catch (\Exception $e) {
        Log::error('Subscription error', ['error' => $e->getMessage()]);
        sleep(5);  // Wait before reconnecting
    }
}
```

### 3. Separate Connections

```php
// Publisher uses default connection
Redis::connection('default')->publish('channel', $message);

// Subscriber uses dedicated connection
Redis::connection('subscriber')->subscribe(['channel'], $callback);
```

---

## Key Takeaways

1. **Fire-and-forget** - No message persistence
2. **Real-time only** - Subscribers must be connected
3. **Pattern subscriptions** - `psubscribe` for wildcards
4. **Blocking** - Subscription blocks connection
5. **Separate processes** - Subscribers need dedicated processes
6. **Use Streams** - For reliable, persistent messaging
7. **Laravel Echo** - Integrates with frontend
8. **At-most-once** - No delivery guarantees
