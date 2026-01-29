# React 19.2 Activity Component

The `<Activity>` component lets you hide and restore UI while preserving state.

**Introduced in:** React 19.2 (October 2025)

## Overview

```typescript
import { Activity } from 'react';

<Activity mode={isVisible ? 'visible' : 'hidden'}>
  <ExpensiveComponent />
</Activity>
```

## Modes

| Mode | Visibility | Effects | Updates |
|------|------------|---------|---------|
| `visible` | Shown | Mounted | Normal |
| `hidden` | Hidden | Unmounted | Deferred until idle |

---

## Why Activity?

### Before: Conditional Rendering

```typescript
// Destroys state when hidden
{isVisible && <Page />}
```

**Problems:**
- State is lost when component unmounts
- Re-renders everything when shown again
- Can't preload hidden content

### After: Activity Component

```typescript
// Preserves state when hidden
<Activity mode={isVisible ? 'visible' : 'hidden'}>
  <Page />
</Activity>
```

**Benefits:**
- State preserved (inputs, scroll position, etc.)
- Effects unmounted when hidden (no background work)
- Updates deferred until React is idle
- Can pre-render hidden content

---

## Basic Usage

### Tab Switching

```typescript
function Tabs() {
  const [activeTab, setActiveTab] = useState('packages');

  return (
    <div>
      <div className="tabs">
        <button onClick={() => setActiveTab('packages')}>Packages</button>
        <button onClick={() => setActiveTab('transfers')}>Transfers</button>
        <button onClick={() => setActiveTab('sales')}>Sales</button>
      </div>

      {/* All tabs stay mounted, only active one is visible */}
      <Activity mode={activeTab === 'packages' ? 'visible' : 'hidden'}>
        <PackagesTab />
      </Activity>

      <Activity mode={activeTab === 'transfers' ? 'visible' : 'hidden'}>
        <TransfersTab />
      </Activity>

      <Activity mode={activeTab === 'sales' ? 'visible' : 'hidden'}>
        <SalesTab />
      </Activity>
    </div>
  );
}
```

### Back Navigation

```typescript
function Navigator() {
  const [history, setHistory] = useState([{ route: 'list' }]);
  const currentRoute = history[history.length - 1].route;

  return (
    <div>
      {/* Previous pages stay mounted for instant back */}
      {history.map((entry, index) => (
        <Activity
          key={entry.route}
          mode={index === history.length - 1 ? 'visible' : 'hidden'}
        >
          <Page route={entry.route} />
        </Activity>
      ))}
    </div>
  );
}
```

---

## BudTags Examples

### Dashboard Tabs with State Preservation

```typescript
function PackagesDashboard() {
  const [activeView, setActiveView] = useState<'active' | 'onhold' | 'finished'>('active');

  return (
    <div>
      <div className="flex gap-2 mb-4">
        <button
          className={`btn ${activeView === 'active' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveView('active')}
        >
          Active Packages
        </button>
        <button
          className={`btn ${activeView === 'onhold' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveView('onhold')}
        >
          On Hold
        </button>
        <button
          className={`btn ${activeView === 'finished' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveView('finished')}
        >
          Finished
        </button>
      </div>

      {/* Each tab preserves its filter state, scroll position, selections */}
      <Activity mode={activeView === 'active' ? 'visible' : 'hidden'}>
        <ActivePackagesTable />
      </Activity>

      <Activity mode={activeView === 'onhold' ? 'visible' : 'hidden'}>
        <OnHoldPackagesTable />
      </Activity>

      <Activity mode={activeView === 'finished' ? 'visible' : 'hidden'}>
        <FinishedPackagesTable />
      </Activity>
    </div>
  );
}
```

### Modal with Preserved Form State

```typescript
function EditPackageModal({ pkg, isOpen, onClose }) {
  return (
    <Activity mode={isOpen ? 'visible' : 'hidden'}>
      <Modal show={isOpen} onClose={onClose}>
        {/* Form state preserved if modal is closed and reopened */}
        <PackageForm package={pkg} />
      </Modal>
    </Activity>
  );
}
```

### Preloading Next Page

```typescript
function PackageListWithPrefetch({ packages }) {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [hoveredId, setHoveredId] = useState<number | null>(null);

  return (
    <div>
      <ul>
        {packages.map(pkg => (
          <li
            key={pkg.Id}
            onClick={() => setSelectedId(pkg.Id)}
            onMouseEnter={() => setHoveredId(pkg.Id)}
            onMouseLeave={() => setHoveredId(null)}
          >
            {pkg.Label}
          </li>
        ))}
      </ul>

      {/* Preload hovered package details in background */}
      {hoveredId && hoveredId !== selectedId && (
        <Activity mode="hidden">
          <PackageDetails packageId={hoveredId} />
        </Activity>
      )}

      {/* Show selected package details */}
      {selectedId && (
        <Activity mode="visible">
          <PackageDetails packageId={selectedId} />
        </Activity>
      )}
    </div>
  );
}
```

---

## When Hidden Mode is Active

### Effects are Unmounted

```typescript
function DataPollingComponent() {
  useEffect(() => {
    // This interval STOPS when Activity mode='hidden'
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return <DataDisplay />;
}
```

### Updates are Deferred

```typescript
// When hidden, state updates are queued
// They only apply when React is idle
// This prevents hidden components from competing with visible ones
```

### DOM is Hidden (Not Removed)

```typescript
// The DOM stays in place but is hidden
// This means:
// - Faster show/hide (no DOM creation)
// - Scroll position preserved
// - Form inputs keep their values
```

---

## Comparison with Alternatives

### vs Conditional Rendering

```typescript
// Conditional - destroys state
{isVisible && <Component />}

// Activity - preserves state
<Activity mode={isVisible ? 'visible' : 'hidden'}>
  <Component />
</Activity>
```

### vs CSS display: none

```typescript
// CSS - keeps effects running, competes for resources
<div style={{ display: isVisible ? 'block' : 'none' }}>
  <Component />
</div>

// Activity - unmounts effects, defers updates
<Activity mode={isVisible ? 'visible' : 'hidden'}>
  <Component />
</Activity>
```

### vs keepAlive (Vue)

React's Activity is similar to Vue's `<KeepAlive>` but with:
- Effect unmounting in hidden mode
- Deferred updates
- No LRU cache limit (yet)

---

## Best Practices

### 1. Use for Expensive Components

```typescript
// ✅ Good - expensive to re-render
<Activity mode={tab === 'reports' ? 'visible' : 'hidden'}>
  <ComplexReportsChart />
</Activity>

// ❌ Overkill - simple component
<Activity mode={tab === 'about' ? 'visible' : 'hidden'}>
  <AboutText />
</Activity>
```

### 2. Limit Number of Hidden Activities

```typescript
// ⚠️ Be careful with many hidden components
// Each one keeps state in memory

// ✅ Good - limited tabs
{tabs.slice(0, 5).map(tab => (
  <Activity key={tab.id} mode={activeTab === tab.id ? 'visible' : 'hidden'}>
    <TabContent tab={tab} />
  </Activity>
))}

// ❌ Bad - unlimited history
{history.map(entry => (
  <Activity key={entry.id} mode={...}>
    <Page entry={entry} />
  </Activity>
))}
```

### 3. Consider Memory vs Performance

```typescript
// Activity trades memory for performance
// Good when:
// - Tab switching is frequent
// - Component initialization is expensive
// - State preservation is important

// Use conditional rendering when:
// - Memory is constrained
// - Component is cheap to render
// - State doesn't need preservation
```

---

## Summary

| Feature | Conditional | CSS Hidden | Activity |
|---------|-------------|------------|----------|
| State preserved | ❌ | ✅ | ✅ |
| Effects unmounted | ✅ | ❌ | ✅ |
| Updates deferred | N/A | ❌ | ✅ |
| DOM preserved | ❌ | ✅ | ✅ |
| Memory usage | Low | High | Medium |

## Next Steps

- Read `12-use-effect-event.md` for another React 19.2 feature
- Read `13-performance-tracks.md` for debugging tools
