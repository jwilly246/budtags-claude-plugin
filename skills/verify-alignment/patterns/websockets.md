# WebSocket & Broadcasting Patterns

This document covers Laravel Reverb WebSocket broadcasting patterns for real-time updates.

---

## Critical Decision: ShouldBroadcast vs ShouldBroadcastNow

### The Problem

Laravel's queue system uses FIFO (First In, First Out) ordering. When using `ShouldBroadcast`:

1. Job A dispatches → queues broadcast event
2. Job B dispatches → queues broadcast event
3. Job C dispatches → queues broadcast event
4. Queue worker processes: Job A, Job B, Job C, Broadcast A, Broadcast B, Broadcast C

**Result**: All broadcasts fire AFTER all jobs complete - defeating the purpose of real-time updates.

### The Solution

```php
// ❌ WRONG - Queues broadcast (delays until queue catches up)
class LabelCreated implements ShouldBroadcast {

// ✅ CORRECT - Broadcasts immediately within current job
class LabelCreated implements ShouldBroadcastNow {
```

### When to Use Each

| Interface | Use When |
|-----------|----------|
| `ShouldBroadcastNow` | Real-time UX critical (progress indicators, live updates) |
| `ShouldBroadcast` | Non-urgent notifications, background sync |

---

## Event Enrichment Pattern

### The Problem

Minimal WebSocket events require page reloads to fetch display data:

```php
// ❌ Minimal event - requires reload to show data
class LabelCreated implements ShouldBroadcastNow {
    public string $label_id;  // Frontend must reload to get label details
}
```

### The Solution

Include all data needed for UI display directly in the event:

```php
// ✅ Enriched event - zero reloads needed
class LabelCreated implements ShouldBroadcastNow {
    public string $org_id;
    public string $label_id;
    public string $tag;
    public string $item;
    public string $label_type_name;      // For table display
    public int $fixed_print_amount;       // For table display
    public int $amt_in_group;             // For progress indicator
    public int $amt_success;              // For progress indicator
}
```

### Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| Minimal events + reload | Smaller payloads | Page flicker, jarring UX |
| Enriched events | Zero reloads, smooth UX | Slightly larger payloads |

**BudTags Pattern**: Prefer enriched events for user-facing real-time features.

---

## Organization Scoping (CRITICAL)

WebSocket channels MUST be scoped to organization:

```php
// ✅ CORRECT - Private org-scoped channel
public function broadcastOn(): array {
    return [
        new PrivateChannel("orgs.{$this->org_id}"),
    ];
}

// ❌ WRONG - Public channel (security violation)
public function broadcastOn(): array {
    return [
        new Channel("labels"),  // Any user can listen!
    ];
}
```

Channel authorization in `routes/channels.php`:

```php
Broadcast::channel('orgs.{org_id}', function (User $user, string $org_id) {
    return $user->active_org_id === $org_id;
});
```

---

## Frontend: EventEmitter Decoupling Pattern

### The Problem

Tight coupling between WebSocket reception and component handling:

```tsx
// ❌ Tight coupling - component directly uses Echo
useEffect(() => {
    window.Echo.private(`orgs.${orgId}`)
        .listen('.label-created', (data) => {
            // Handle in this component
        });
}, []);
```

### The Solution

Use EventEmitter to decouple reception from handling:

**events.tsx** - Define emitters:
```tsx
class EventEmitter<T> {
    private listeners: ((data: T) => void)[] = [];

    on(listener: (data: T) => void) { this.listeners.push(listener); }
    off(listener: (data: T) => void) {
        this.listeners = this.listeners.filter(l => l !== listener);
    }
    emit(data: T) { this.listeners.forEach(l => l(data)); }
}

export const onLabelCreated = new EventEmitter<EventLabelCreated>();
```

**MainLayout.tsx** - Single reception point:
```tsx
useEffect(() => {
    const channel = window.Echo?.private(`orgs.${orgId}`);

    channel?.listen('.label-created', (data: EventLabelCreated) => {
        onLabelCreated.emit(data);  // Broadcast to subscribers
    });

    return () => channel?.stopListening('.label-created');
}, [orgId]);
```

**LabelsBuilt.tsx** - Subscribe where needed:
```tsx
useEffect(() => {
    const handler = (data: EventLabelCreated) => {
        setLabels(prev => [...prev, buildLabelFromEvent(data)]);
    };

    onLabelCreated.on(handler);
    return () => onLabelCreated.off(handler);
}, []);
```

### Benefits

1. **Single Echo connection** in MainLayout
2. **Multiple subscribers** across components
3. **Easy testing** - emit events without WebSocket
4. **Proper cleanup** - each component manages its own listener

---

## Frontend: Building State from Events

When using enriched events, build display state directly:

```tsx
const [labels, setLabels] = useState<Label[]>(props.group.labels);

useEffect(() => {
    const handleLabelCreated = (data: EventLabelCreated) => {
        const newLabel = {
            id: data.label_id,
            metrc_tag: data.tag,
            metrc_item_name: data.item,
            label_type: { name: data.label_type_name },
            fixed_print_amount: data.fixed_print_amount,
        } as Label;

        // Prevent duplicates
        setLabels(prev => {
            if (prev.some(l => l.id === data.label_id)) return prev;
            return [...prev, newLabel];
        });
    };

    onLabelCreated.on(handleLabelCreated);
    return () => onLabelCreated.off(handleLabelCreated);
}, [props.group.id]);
```

---

## TypeScript Type Alignment

Ensure frontend types match backend event properties:

**PHP Event**:
```php
class LabelCreated implements ShouldBroadcastNow {
    public string $org_id;
    public string $label_id;
    public string $tag;
    public string $item;
    public string $label_type_name;
    public int $fixed_print_amount;
    public int $amt_in_group;
    public int $amt_success;
}
```

**TypeScript Type** (events.tsx):
```tsx
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

---

## Effect Cleanup (CRITICAL)

Always clean up WebSocket listeners to prevent:
- Memory leaks
- Duplicate handlers
- Stale closures

```tsx
// ✅ CORRECT - Proper cleanup
useEffect(() => {
    const handler = (data) => { /* ... */ };
    onLabelCreated.on(handler);
    return () => onLabelCreated.off(handler);  // Cleanup!
}, [dependency]);

// ❌ WRONG - No cleanup (memory leak)
useEffect(() => {
    onLabelCreated.on((data) => { /* ... */ });
}, []);
```

---

## Common Anti-Patterns

### 1. Reload on Every Event

```tsx
// ❌ WRONG - Defeats purpose of WebSockets
onLabelCreated.on(() => {
    router.reload();  // Page flickers on every event!
});
```

### 2. Using ShouldBroadcast for Real-Time Features

```php
// ❌ WRONG - Queued broadcasts delay real-time updates
class ProgressUpdate implements ShouldBroadcast {
```

### 3. Public Channels for Org Data

```php
// ❌ WRONG - Security violation
new Channel("labels.{$org_id}")  // Public despite ID
```

### 4. Missing Duplicate Prevention

```tsx
// ❌ WRONG - Same event can add duplicate rows
setLabels(prev => [...prev, newLabel]);

// ✅ CORRECT - Check before adding
setLabels(prev => {
    if (prev.some(l => l.id === newLabel.id)) return prev;
    return [...prev, newLabel];
});
```

---

## Environment Configuration

Vite environment variables for Reverb:

```env
# .env - Use direct values, NOT interpolation
VITE_REVERB_APP_KEY=your-key-here
VITE_REVERB_HOST=127.0.0.1
VITE_REVERB_PORT=8080
VITE_REVERB_SCHEME=http

# ❌ WRONG - Vite doesn't understand interpolation
VITE_REVERB_HOST="${REVERB_HOST}"
```

**app.tsx** Echo setup:
```tsx
window.Echo = new Echo({
    broadcaster: 'reverb',
    key: import.meta.env.VITE_REVERB_APP_KEY,
    wsHost: import.meta.env.VITE_REVERB_HOST,
    wsPort: import.meta.env.VITE_REVERB_PORT ?? 80,
    wssPort: import.meta.env.VITE_REVERB_PORT ?? 443,
    forceTLS: (import.meta.env.VITE_REVERB_SCHEME ?? 'https') === 'https',
    enabledTransports: ['ws', 'wss'],
    authEndpoint: '/broadcasting/auth',
});
```

---

## Quick Reference

| Pattern | Correct | Wrong |
|---------|---------|-------|
| Real-time broadcasts | `ShouldBroadcastNow` | `ShouldBroadcast` |
| Channel scoping | `PrivateChannel("orgs.{$org_id}")` | `Channel("labels")` |
| Event data | Include all display fields | Minimal ID only |
| Frontend updates | Build state from event | Reload page |
| Listener cleanup | Return cleanup function | No cleanup |
| Vite env vars | Direct values | `"${VAR}"` interpolation |
