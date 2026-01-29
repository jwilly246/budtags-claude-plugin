# Pattern 11: Deferred Props (v2.0+)

## Overview

Deferred props are loaded **after** the initial page render, improving perceived performance by showing the page immediately while heavy data loads in the background.

```php
// Server
return Inertia::render('Dashboard', [
    'user' => $user,  // Immediate
    'stats' => Inertia::defer(fn () => $this->calculateStats()),  // Deferred
]);
```

```tsx
// Client
<Deferred data="stats" fallback={<Spinner />}>
  <StatsWidget stats={stats} />
</Deferred>
```

---

## Server-Side: Inertia::defer()

### Basic Usage

```php
return Inertia::render('Dashboard', [
    // Loaded immediately
    'user' => $request->user(),
    'notifications' => $request->user()->notifications->take(5),

    // Loaded after initial render
    'analytics' => Inertia::defer(fn () => $this->calculateAnalytics()),
    'recentActivity' => Inertia::defer(fn () => Activity::latest()->take(20)->get()),
]);
```

### Grouping Deferred Props

By default, all deferred props load in a single request. Group them for parallel loading:

```php
return Inertia::render('Dashboard', [
    'user' => $request->user(),

    // Group 1: Analytics (loads together)
    'revenue' => Inertia::defer(fn () => $this->getRevenue(), 'analytics'),
    'visitors' => Inertia::defer(fn () => $this->getVisitors(), 'analytics'),

    // Group 2: Activity (loads separately, in parallel)
    'recentOrders' => Inertia::defer(fn () => Order::latest()->take(10)->get(), 'activity'),
    'recentUsers' => Inertia::defer(fn () => User::latest()->take(10)->get(), 'activity'),
]);
```

### once() Modifier

Load deferred data only once, persist across navigations:

```php
return Inertia::render('Dashboard', [
    // Only fetches once, cached for session
    'systemStats' => Inertia::defer(fn () => $this->getSystemStats())->once(),
]);
```

---

## Client-Side: Deferred Component

### Basic Usage

```tsx
import { Deferred } from '@inertiajs/react';

function Dashboard({ user, stats }) {
  return (
    <div>
      <h1>Welcome, {user.name}</h1>

      <Deferred data="stats" fallback={<LoadingSpinner />}>
        <StatsWidget stats={stats} />
      </Deferred>
    </div>
  );
}
```

### Multiple Props

Wait for multiple deferred props:

```tsx
<Deferred data={['revenue', 'visitors']} fallback={<Spinner />}>
  <AnalyticsPanel revenue={revenue} visitors={visitors} />
</Deferred>
```

### Custom Fallback

```tsx
<Deferred
  data="analytics"
  fallback={
    <div className="animate-pulse bg-gray-200 h-40 rounded" />
  }
>
  <AnalyticsChart data={analytics} />
</Deferred>
```

### Render Prop Pattern

```tsx
<Deferred data="stats">
  {(stats) => stats ? <StatsWidget stats={stats} /> : <Skeleton />}
</Deferred>
```

---

## Comparison: Lazy vs Deferred vs Optional

| Type | When Evaluated | Initial Response | Partial Reload |
|------|----------------|------------------|----------------|
| **Closure** | On access | Included | Included if requested |
| **defer()** | After render | Not included | Separate request |
| **optional()** | Only if requested | Never included | Only if explicitly requested |

```php
return Inertia::render('Page', [
    // Regular: Evaluated on every request
    'users' => User::all(),

    // Closure: Lazy, but included in initial response
    'stats' => fn () => $this->calculateStats(),

    // Defer: Loaded after page renders
    'analytics' => Inertia::defer(fn () => $this->heavyAnalytics()),

    // Optional: Only loaded when explicitly requested
    'exportData' => Inertia::optional(fn () => $this->prepareExport()),
]);
```

---

## When to Use Deferred Props

### Good Use Cases

- **Analytics dashboards** - Show page immediately, load charts after
- **Activity feeds** - Display layout, then load recent activity
- **Heavy calculations** - User sees page while data processes
- **Non-critical data** - Sidebar widgets, recommendations

### Not Ideal For

- **Critical content** - Main page content should load immediately
- **Form data** - Forms need data before render
- **Navigation-dependent data** - Data user expects immediately

---

## BudTags Example

### Dashboard with Deferred Stats

```php
// Controller
public function dashboard(Request $request)
{
    $user = $request->user();
    $org = $user->active_org;

    return Inertia::render('Dashboard', [
        // Immediate - user needs to see this
        'user' => $user,
        'org' => $org,
        'quickStats' => [
            'activePackages' => Package::where('org_id', $org->id)->active()->count(),
            'pendingTransfers' => Transfer::where('org_id', $org->id)->pending()->count(),
        ],

        // Deferred - nice to have, can wait
        'recentActivity' => Inertia::defer(
            fn () => Activity::where('org_id', $org->id)
                ->latest()
                ->take(10)
                ->get()
        ),

        'inventoryChart' => Inertia::defer(
            fn () => $this->calculateInventoryChart($org)
        ),
    ]);
}
```

```tsx
// Dashboard.tsx
function Dashboard({ user, org, quickStats, recentActivity, inventoryChart }) {
  return (
    <MainLayout>
      <h1>Welcome, {user.name}</h1>

      {/* Immediate stats */}
      <div className="grid grid-cols-2 gap-4">
        <StatCard label="Active Packages" value={quickStats.activePackages} />
        <StatCard label="Pending Transfers" value={quickStats.pendingTransfers} />
      </div>

      {/* Deferred content */}
      <div className="grid grid-cols-2 gap-4 mt-6">
        <Deferred
          data="recentActivity"
          fallback={<ActivitySkeleton />}
        >
          <ActivityFeed items={recentActivity} />
        </Deferred>

        <Deferred
          data="inventoryChart"
          fallback={<ChartSkeleton />}
        >
          <InventoryChart data={inventoryChart} />
        </Deferred>
      </div>
    </MainLayout>
  );
}
```

---

## Performance Tips

1. **Group related deferred props** to minimize requests
2. **Use `once()`** for data that doesn't change often
3. **Keep critical data immediate** - only defer non-essential content
4. **Provide meaningful fallbacks** - skeleton screens, not just spinners
5. **Consider mobile users** - they benefit most from faster initial loads

---

## ⚠️ Gotcha: Silent Updates with Deferred Props

When a page uses deferred props, **any Inertia request that triggers a redirect will re-evaluate those props**, causing a brief loading state (skeleton flash).

### The Problem

```typescript
// Page has deferred props
const isLoading = !props.packages_data;  // Shows skeleton when undefined

// User preference save with router.post()
router.post('/user/preferences/column-visibility', {
  columnVisibility: visibility
}, { preserveState: true });
// ❌ Backend returns redirect()->back()
// ❌ Inertia follows redirect, re-fetches page
// ❌ Deferred props re-evaluate → undefined → skeleton flash!
```

### The Solution: Bypass Inertia for Silent Saves

For "fire-and-forget" operations (preferences, analytics, etc.) that don't need page updates:

**Backend:** Return 204 No Content
```php
public function savePreference(Request $request): Response {
    $request->user()->setPreference($request->input('key'), $request->input('value'));
    return response()->noContent();  // 204 = success, no page update
}
```

**Frontend:** Use axios instead of router.post()
```typescript
import axios from 'axios';

// ✅ axios bypasses Inertia entirely
axios.post('/user/preferences/column-visibility', {
  columnVisibility: visibility,
});
// Backend returns 204 → axios receives it → no page update
// Deferred props remain unchanged → no skeleton flash
```

### When to Use This Pattern

- ✅ User preference saves (column visibility, UI settings)
- ✅ Analytics/telemetry events
- ✅ Any operation where the page state is already updated optimistically
- ❌ Form submissions that need success/error feedback
- ❌ Operations that change page data

---

## Next Steps

- **Scroll Management** → Read `12-scroll-management.md`
- **Partial Reloads** → Read `10-partial-reloads.md`
- **BudTags Integration** → Read `25-budtags-integration.md`
