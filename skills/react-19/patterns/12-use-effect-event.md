# React 19.2 useEffectEvent

Extract "event" logic from Effects to avoid unnecessary re-runs.

**Introduced in:** React 19.2 (October 2025)

## The Problem

Effects re-run when dependencies change, even when some dependencies aren't really "reactive":

```typescript
function ChatRoom({ roomId, theme }) {
  useEffect(() => {
    const connection = createConnection(roomId);

    connection.on('connected', () => {
      // theme is in deps, but changing theme shouldn't reconnect!
      showNotification('Connected!', theme);
    });

    connection.connect();
    return () => connection.disconnect();
  }, [roomId, theme]); // ← theme causes unnecessary reconnects
}
```

**Problem:** Changing `theme` causes the chat to disconnect and reconnect!

---

## The Solution: useEffectEvent

```typescript
import { useEffectEvent } from 'react';

function ChatRoom({ roomId, theme }) {
  // Extract the "event" - always reads latest values
  const onConnected = useEffectEvent(() => {
    showNotification('Connected!', theme);
  });

  useEffect(() => {
    const connection = createConnection(roomId);

    connection.on('connected', () => {
      onConnected(); // Always uses latest theme
    });

    connection.connect();
    return () => connection.disconnect();
  }, [roomId]); // ← Clean! Only reconnects when roomId changes
}
```

---

## How It Works

`useEffectEvent` creates a function that:
1. **Always reads the latest values** of props and state
2. **Should NOT be in the dependency array** of useEffect
3. **Is conceptually an "event"** triggered by something in the Effect

### Key Rules

```typescript
// ✅ DO: Use for "event handlers" inside Effects
const onConnected = useEffectEvent(() => {
  logAnalytics(userId, theme);
});

// ❌ DON'T: Include in dependency array
useEffect(() => {
  connection.on('connected', onConnected);
}, [onConnected]); // WRONG!

// ✅ DO: Omit from dependency array
useEffect(() => {
  connection.on('connected', onConnected);
}, []); // Correct!

// ❌ DON'T: Call outside of Effects
onClick={() => onConnected()} // Not intended for this!
```

---

## ESLint Plugin Required

You need the latest ESLint plugin to use this correctly:

```bash
npm install -D eslint-plugin-react-hooks@latest
```

The plugin will:
- Warn if you include Effect Events in deps
- Suggest when to use useEffectEvent

---

## BudTags Examples

### Toast Notifications in Effects

```typescript
function PackageSubscription({ packageId, toastPosition }) {
  // Toast position might change, but shouldn't restart subscription
  const showPackageUpdate = useEffectEvent((update: PackageUpdate) => {
    toast.success(`Package updated: ${update.label}`, {
      position: toastPosition, // Always uses latest position
    });
  });

  useEffect(() => {
    const unsubscribe = subscribeToPackage(packageId, (update) => {
      showPackageUpdate(update);
    });

    return unsubscribe;
  }, [packageId]); // Only re-subscribes when package changes
}
```

### Analytics in Effects

```typescript
function MetrcDataFetch({ license, organization }) {
  // Analytics context shouldn't trigger refetch
  const logFetch = useEffectEvent((result: FetchResult) => {
    analytics.track('metrc_fetch', {
      license,
      organization: organization.name,
      success: result.success,
      count: result.count,
    });
  });

  const { data, refetch } = useQuery({
    queryKey: ['metrc', license],
    queryFn: async () => {
      const result = await fetchMetrcData(license);
      logFetch(result); // Always has latest organization
      return result;
    },
  });
}
```

### WebSocket Connection with Settings

```typescript
function LiveUpdates({ channel, notificationSettings }) {
  // Settings changes shouldn't reconnect WebSocket
  const handleMessage = useEffectEvent((message: Message) => {
    if (notificationSettings.sound) {
      playNotificationSound();
    }
    if (notificationSettings.desktop) {
      showDesktopNotification(message.title);
    }
    updateUI(message);
  });

  useEffect(() => {
    const ws = new WebSocket(`wss://api.example.com/${channel}`);

    ws.onmessage = (event) => {
      handleMessage(JSON.parse(event.data));
    };

    return () => ws.close();
  }, [channel]); // Only reconnects when channel changes
}
```

### Metrc Polling with User Preferences

```typescript
function MetrcPackagePoller({ license, pollingEnabled, refreshInterval }) {
  // Interval changes shouldn't restart effect
  // (though you might want a separate effect for that)
  const handleNewData = useEffectEvent((packages: Package[]) => {
    if (packages.some(p => p.isNew)) {
      toast.info(`${packages.filter(p => p.isNew).length} new packages`);
    }
  });

  useEffect(() => {
    if (!pollingEnabled) return;

    const poll = async () => {
      const packages = await fetchPackages(license);
      handleNewData(packages);
    };

    const interval = setInterval(poll, refreshInterval);
    poll(); // Initial fetch

    return () => clearInterval(interval);
  }, [license, pollingEnabled, refreshInterval]);
  // Note: refreshInterval IS reactive here - we want to restart polling
}
```

---

## When to Use useEffectEvent

### ✅ Use When

1. **Callbacks inside Effects that read props/state**
   ```typescript
   const onSuccess = useEffectEvent(() => {
     showToast(message); // message from props
   });
   ```

2. **Event handlers triggered by Effect logic**
   ```typescript
   const onConnected = useEffectEvent(() => {
     logEvent('connected', userId);
   });
   ```

3. **The value changes frequently but shouldn't restart the Effect**
   ```typescript
   const logWithTheme = useEffectEvent(() => {
     console.log('Theme:', theme); // theme changes often
   });
   ```

### ❌ Don't Use When

1. **The value SHOULD restart the Effect**
   ```typescript
   // roomId changing SHOULD reconnect
   useEffect(() => {
     connect(roomId);
   }, [roomId]); // Keep in deps!
   ```

2. **For regular event handlers (onClick, etc.)**
   ```typescript
   // Just use regular function
   const handleClick = () => {
     doSomething(value);
   };
   ```

3. **For values you want to "freeze"**
   ```typescript
   // Use useRef or closure instead
   const valueRef = useRef(value);
   ```

---

## Comparison

### Before useEffectEvent

```typescript
function Component({ id, theme, user }) {
  useEffect(() => {
    const sub = subscribe(id, (data) => {
      // Need theme and user, but they cause re-subscribes
      log(theme, user);
      process(data);
    });
    return () => sub.unsubscribe();
  }, [id, theme, user]); // Too many deps!
}
```

### After useEffectEvent

```typescript
function Component({ id, theme, user }) {
  const handleData = useEffectEvent((data) => {
    log(theme, user); // Always latest
    process(data);
  });

  useEffect(() => {
    const sub = subscribe(id, handleData);
    return () => sub.unsubscribe();
  }, [id]); // Clean deps!
}
```

---

## Summary

| Scenario | Solution |
|----------|----------|
| Value should trigger re-run | Keep in deps |
| Value shouldn't trigger re-run | useEffectEvent |
| Need latest value in callback | useEffectEvent |
| Event handler for user interaction | Regular function |

## Next Steps

- Read `11-activity-component.md` for UI state management
- Read `13-performance-tracks.md` for debugging tools
- Read `14-breaking-changes.md` for all React 19 changes
