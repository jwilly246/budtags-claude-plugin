# Scenario: WebSocket Broadcast Event

Use this checklist when implementing new WebSocket broadcast events for real-time updates.

---

## Backend Checklist (PHP Event)

### 1. Interface Selection
- [ ] Uses `ShouldBroadcastNow` (NOT `ShouldBroadcast`) for real-time UX
- [ ] Only use `ShouldBroadcast` for non-urgent background notifications

```php
// ✅ CORRECT
class LabelCreated implements ShouldBroadcastNow {

// ❌ WRONG for real-time features
class LabelCreated implements ShouldBroadcast {
```

### 2. Channel Security
- [ ] Uses `PrivateChannel` scoped to organization
- [ ] Channel authorization defined in `routes/channels.php`

```php
// ✅ CORRECT
public function broadcastOn(): array {
    return [new PrivateChannel("orgs.{$this->org_id}")];
}

// ❌ WRONG - Security violation
return [new Channel("labels")];
```

### 3. Event Data Enrichment
- [ ] Includes all data needed for frontend display
- [ ] Avoids requiring page reload to fetch additional data
- [ ] All properties have explicit type declarations

```php
// ✅ CORRECT - Enriched event
public string $org_id;
public string $label_id;
public string $tag;
public string $item;
public string $label_type_name;      // For display
public int $fixed_print_amount;       // For display
public int $amt_in_group;             // For progress
public int $amt_success;              // For progress
```

### 4. Broadcast Name
- [ ] Uses `broadcastAs()` for clean event names
- [ ] Event name is kebab-case

```php
public function broadcastAs(): string {
    return 'label-created';  // Not 'App\Events\LabelCreated'
}
```

---

## Frontend Checklist (TypeScript/React)

### 5. Type Definition
- [ ] TypeScript type matches PHP event properties exactly
- [ ] Type defined in `resources/js/events.tsx`

```typescript
// events.tsx
export type EventLabelCreated = {
    org_id: string;
    label_id: string;
    tag: string;
    item: string;
    label_type_name: string;
    fixed_print_amount: number;
    amt_in_group: number;
    amt_success: number;
};
```

### 6. EventEmitter Setup
- [ ] EventEmitter created for decoupling
- [ ] Exported from events.tsx

```typescript
export const onLabelCreated = new EventEmitter<EventLabelCreated>();
```

### 7. MainLayout Listener
- [ ] Echo listener added in MainLayout.tsx
- [ ] Emits to EventEmitter (not handling directly)
- [ ] Proper cleanup on unmount

```typescript
// MainLayout.tsx
orgChannel?.listen('.label-created', (data: EventLabelCreated) => {
    onLabelCreated.emit(data);
});

// Cleanup
return () => {
    orgChannel?.stopListening('.label-created');
};
```

### 8. Component Subscription
- [ ] Component subscribes to EventEmitter
- [ ] Proper cleanup in useEffect return
- [ ] Builds state directly from event data (no reload)

```typescript
useEffect(() => {
    const handler = (data: EventLabelCreated) => {
        // Build display object from event data
        const newItem = {
            id: data.label_id,
            name: data.tag,
            // ... other display fields
        };

        // Prevent duplicates
        setItems(prev => {
            if (prev.some(i => i.id === data.label_id)) return prev;
            return [...prev, newItem];
        });
    };

    onLabelCreated.on(handler);
    return () => onLabelCreated.off(handler);
}, [dependency]);
```

---

## Anti-Pattern Checklist

### ❌ Avoid These Patterns

- [ ] NOT using `router.reload()` on every event
- [ ] NOT using `ShouldBroadcast` for real-time features
- [ ] NOT using public channels for org-scoped data
- [ ] NOT missing duplicate prevention in state updates
- [ ] NOT missing cleanup in useEffect
- [ ] NOT using Vite env var interpolation (`"${VAR}"`)

---

## Testing Checklist

### Manual Testing
- [ ] Reverb server running (`php artisan reverb:start`)
- [ ] Queue worker running (`php artisan queue:work`)
- [ ] Browser DevTools Network tab shows WebSocket connection
- [ ] Events appear in real-time (not after job completion)
- [ ] No page flicker or jarring refreshes
- [ ] Multiple browser tabs receive events correctly

### Debug Tips
```javascript
// Console - check connection state
window.Echo.connector.pusher.connection.state  // Should be 'connected'

// Console - check channel subscriptions
window.Echo.connector.channels
```

---

## Files to Modify

| Location | Purpose |
|----------|---------|
| `app/Events/YourEvent.php` | New broadcast event class |
| `routes/channels.php` | Channel authorization (if new channel) |
| `resources/js/events.tsx` | TypeScript type + EventEmitter |
| `resources/js/Layouts/MainLayout.tsx` | Echo listener |
| `resources/js/Pages/YourPage.tsx` | EventEmitter subscription |

---

## Quick Reference

```php
// PHP Event Template
class YourEvent implements ShouldBroadcastNow {
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public string $org_id;
    // ... enriched data fields

    public function __construct(YourModel $model) {
        $this->org_id = $model->organization_id;
        // ... populate fields
    }

    public function broadcastOn(): array {
        return [new PrivateChannel("orgs.{$this->org_id}")];
    }

    public function broadcastAs(): string {
        return 'your-event-name';
    }
}
```

```typescript
// TypeScript Template
export type YourEventType = {
    org_id: string;
    // ... matching fields
};

export const onYourEvent = new EventEmitter<YourEventType>();
```
