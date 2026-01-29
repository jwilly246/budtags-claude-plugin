# React 19.2 Performance Tracks

New Chrome DevTools integration for debugging React performance.

**Introduced in:** React 19.2 (October 2025)

## Overview

React 19.2 adds custom tracks to Chrome DevTools Performance panel:
- **Scheduler Track ⚛** - Shows React's work scheduling
- **Components Track ⚛** - Shows component render timing

---

## Accessing Performance Tracks

1. Open Chrome DevTools (F12)
2. Go to **Performance** tab
3. Click **Record** and interact with your app
4. Stop recording
5. Look for **⚛ Scheduler** and **⚛ Components** tracks

---

## Scheduler Track ⚛

Shows how React schedules and prioritizes work.

### What You'll See

| Label | Meaning |
|-------|---------|
| **Render** | React is rendering components |
| **Commit** | React is committing changes to DOM |
| **Blocking** | High-priority synchronous work |
| **Transition** | Low-priority transition work |
| **Idle** | Work scheduled during idle time |

### Reading the Track

```
┌─────────────────────────────────────────────────┐
│ Scheduler Track ⚛                               │
├─────────────────────────────────────────────────┤
│ [Blocking]──[Commit] [Transition]───────[Commit]│
│     ↑                      ↑                    │
│  User click         startTransition work       │
└─────────────────────────────────────────────────┘
```

### Use Cases

1. **Identify Priority Issues**
   - Is blocking work taking too long?
   - Are transitions being interrupted?

2. **Debug Responsiveness**
   - See when React yields to browser
   - Identify work that blocks main thread

3. **Understand Batching**
   - Multiple state updates batched together
   - When batches are flushed

---

## Components Track ⚛

Shows when components mount, update, and unmount.

### What You'll See

| Label | Meaning |
|-------|---------|
| **Mount** | Component and children are mounting |
| **Update** | Component is re-rendering |
| **Unmount** | Component is being removed |
| **Blocked** | Component yielded to higher priority work |

### Reading the Track

```
┌─────────────────────────────────────────────────┐
│ Components Track ⚛                              │
├─────────────────────────────────────────────────┤
│ App                                             │
│   └─ PackageList [Mount]                        │
│        └─ PackageRow [Mount] ×100              │
│                                                 │
│ Later:                                          │
│   └─ PackageRow [Update] (row 5)               │
└─────────────────────────────────────────────────┘
```

### Use Cases

1. **Identify Slow Components**
   - Which components take longest to render?
   - Are unnecessary components re-rendering?

2. **Debug Mount Timing**
   - When do components actually mount?
   - What's the component tree structure?

3. **Find Render Cascades**
   - Parent update causing child updates
   - Unnecessary re-renders

---

## BudTags Debugging Examples

### Slow Package Table

**Symptom:** Table feels sluggish when filtering

**Investigation:**
1. Record performance while typing in filter
2. Check Components Track for PackageRow updates
3. Look for: Are all 100 rows re-rendering on each keystroke?

**What to look for:**
```
Components Track ⚛
  PackageTable [Update]
    └─ PackageRow [Update] ×100  ← Problem: All rows updating!
```

**Solution:** Memoize rows or use virtualization

### Modal Open Delay

**Symptom:** Modal takes time to appear

**Investigation:**
1. Record performance while clicking "Open Modal"
2. Check Scheduler Track for blocking work
3. Check Components Track for mount timing

**What to look for:**
```
Scheduler Track ⚛
  [Blocking]──────────────────[Commit]
       ↑ Long blocking work before modal shows

Components Track ⚛
  Modal [Mount]
    └─ ExpensiveForm [Mount]  ← Takes 200ms!
```

**Solution:** Lazy load modal content, use Activity for pre-rendering

### Transition Not Working

**Symptom:** UI feels janky during navigation

**Investigation:**
1. Record during page transition
2. Check Scheduler Track for transition vs blocking

**What to look for:**
```
Scheduler Track ⚛
  [Blocking]──────────  ← Should be [Transition]!
```

**Solution:** Wrap navigation in startTransition

---

## Tips for Using Performance Tracks

### 1. Record Specific Interactions

```typescript
// Add markers for easier identification
performance.mark('filter-start');
setFilter(value);
performance.mark('filter-end');
performance.measure('filter', 'filter-start', 'filter-end');
```

### 2. Look for Patterns

```
Common Issues:

1. Too many [Blocking] segments
   → Consider startTransition

2. Same component [Update] many times
   → Check memo/dependencies

3. Long [Mount] times
   → Consider lazy loading

4. [Blocked] appearing often
   → Work being interrupted, may need optimization
```

### 3. Compare Before/After

1. Record baseline
2. Make optimization
3. Record again
4. Compare tracks

---

## Combining with React DevTools Profiler

React DevTools Profiler shows:
- Component render times
- What caused re-renders
- Flamegraph of component tree

Performance Tracks show:
- Scheduling and priorities
- Timeline view
- Main thread activity

**Use both together:**
1. Performance Tracks to find slow periods
2. React Profiler to drill into specific renders

---

## Practical Workflow

### Step 1: Identify the Problem

```
User reports: "Package list is slow to filter"
```

### Step 2: Record Performance

1. Open DevTools → Performance
2. Click Record
3. Reproduce the issue (type in filter)
4. Stop recording

### Step 3: Analyze Scheduler Track

```
Questions:
- Is work blocking or transitioning?
- How long are render phases?
- Is work being batched?
```

### Step 4: Analyze Components Track

```
Questions:
- Which components are updating?
- Are updates necessary?
- How long does each component take?
```

### Step 5: Fix and Verify

```typescript
// Before: All rows re-render
function PackageTable({ packages, filter }) {
  const filtered = packages.filter(p => p.Label.includes(filter));
  return filtered.map(p => <PackageRow key={p.Id} pkg={p} />);
}

// After: Memoized rows
const PackageRow = memo(function PackageRow({ pkg }) {
  return <tr>...</tr>;
});
```

Record again to verify improvement.

---

## Summary

| Track | Shows | Use For |
|-------|-------|---------|
| Scheduler ⚛ | Work scheduling | Priority issues, blocking work |
| Components ⚛ | Component timing | Slow renders, unnecessary updates |

## Next Steps

- Read `14-breaking-changes.md` for all React 19 changes
- Read `11-activity-component.md` for UI optimization
- Read `12-use-effect-event.md` for effect optimization
