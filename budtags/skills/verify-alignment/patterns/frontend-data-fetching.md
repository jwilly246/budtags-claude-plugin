# Frontend Data Fetching Patterns

**Source:** `.claude/docs/frontend/data-fetching.md`
**Last Updated:** 2025-12-13
**Pattern Count:** React Query vs Inertia decision patterns + supporting hooks

---

## Overview

BudTags uses **two data fetching patterns**: React Query (client-side caching) and Inertia (server-driven). Using the wrong tool creates bugs and poor UX.

**Architecture Note (Mar 2026):** BudTags uses a **3-layer React Query architecture**. Domain code lives in `resources/js/Hooks/{domain}/` with three separate files:

- **`keys.ts`** — Query key factories (plain objects of functions returning `as const` tuples)
- **`queries.ts`** — `queryOptions()` factories bundling key + fn + staleTime (fetch functions are private, NOT exported)
- **`use*.ts`** — Hook wrappers that spread `queryOptions` and add/override `enabled`, etc.

Mutations live in hook files, NOT in `queries.ts`. Page-level queries with no reuse can co-locate in `{page}-queries.ts` next to the page component (e.g., `Pages/Org/Items/items-queries.ts`).

**Complete Reference:** `.claude/docs/frontend/data-fetching.md` (~400 lines with full examples)

---

## Quick Decision Tree

### ✅ Use React Query When:
- Read-heavy dashboards with frequent updates
- Real-time data that changes often
- Inline editing with optimistic updates
- No page navigation after operation
- Need client-side caching and background refetching

**Examples:** QuickBooks Dashboard, inline editing, live inventory status

### ✅ Use Inertia `useForm` When:
- Form submissions with validation
- CRUD operations (create, update, delete)
- Operations that navigate to new page
- Server-driven validation and error handling
- Traditional form → submit → redirect workflow

**Examples:** Most modals, all forms, package creation, plant operations

---

## Critical Anti-Patterns

### ❌ Global Cache Invalidation

```typescript
// ❌ WRONG - Invalidates EVERYTHING!
queryClient.invalidateQueries();

// ✅ FIX - Specific query key
queryClient.invalidateQueries({ queryKey: ['metrc-items'] });
```

### ❌ Using React Query for Form Submissions

```typescript
// ❌ WRONG - Use Inertia for forms!
const createMutation = useMutation({
    mutationFn: (data) => axios.post('/metrc/packages/create', data),
});

// ✅ FIX - Use Inertia
const { data, setData, post } = useForm({ name: '', quantity: 0 });
post('/metrc/packages/create');
```

### ❌ Using Inertia for Read-Heavy Dashboards

```typescript
// ❌ WRONG - Requires full page reload for refresh
const { invoices } = usePage<PageProps>().props;
<button onClick={() => router.reload()}>Refresh</button>

// ✅ FIX - Use React Query
const { data: invoices, refetch } = useQuickBooksInvoices();
<button onClick={() => refetch()}>Refresh</button>
```

### ❌ Inconsistent Query Key Syntax

```typescript
// ❌ WRONG - Mixing old and new syntax
queryClient.invalidateQueries(['qbo-items']);  // Old
queryClient.invalidateQueries({ queryKey: ['quickbooks-items'] });  // New

// ✅ FIX - Use new syntax consistently
queryClient.invalidateQueries({ queryKey: ['quickbooks-items'] });
```

---

## Query Key Naming Conventions

```typescript
// Global entities (no scope)
['quickbooks-invoices']
['quickbooks-items']
['metrc-items']

// License-scoped entities (org/facility specific)
['packages-summary', license]
['leaflink-inventory', license]
['packaging-materials', license]
```

**Rules:**
- Use kebab-case: `quickbooks-invoices` not `QuickBooksInvoices`
- Plural for lists: `invoices` not `invoice`
- Include scope for org/facility-specific data

---

## Stale Time Guidelines

Use the `STALE_TIME` constants from `@/constants/query-config` — **never use raw millisecond numbers**:

```typescript
import { STALE_TIME } from '@/constants/query-config';
```

| Constant | Duration | Use Case | Example |
|----------|----------|----------|---------|
| `STALE_TIME.REALTIME` | 5 sec | Real-time polling endpoints | Health checks |
| `STALE_TIME.SUGGESTIONS` | 30 sec | Typeahead/autocomplete | Package search |
| `STALE_TIME.MONITORING` | 30 sec | Monitoring dashboards | API monitor |
| `STALE_TIME.POLLING` | 60 sec | Background polling | Transfer tracking |
| `STALE_TIME.SHORT` | 2 min | Frequently changing data | Invoices, orders |
| `STALE_TIME.DEFAULT` | 5 min | Most CRUD data (global default) | Products, customers |
| `STALE_TIME.LONG` | 10 min | Rarely changing data | Brands, packages |
| `STALE_TIME.STATIC` | 15 min | Nearly static reference data | Category dropdowns |
| `STALE_TIME.REFERENCE` | 30 min | Lookup/reference data | Strains, UOM, items |
| `STALE_TIME.REGULATORY` | 24 hr | Regulatory data | Lab test batches |
| `STALE_TIME.FOREVER` | Infinity | Fetch once per page lifecycle | Static config |

**Note:** `staleTime` is set inside `queryOptions()` factories in `queries.ts`, not in individual hooks or components.

---

## Verification Checklist

### React Query Usage
- [ ] Appropriate use case (read-heavy, caching needed, NOT form submission)
- [ ] Correct staleTime for entity type
- [ ] Error handling with toast notification
- [ ] Query key follows naming convention
- [ ] License-scoped if org/facility specific
- [ ] Mutation invalidates correct cache keys
- [ ] No global invalidation
- [ ] Optimistic updates for inline edits

### Inertia useForm Usage
- [ ] Form submissions use Inertia, not React Query
- [ ] Uses `useForm` hook
- [ ] Handles `onSuccess` and `onError`
- [ ] Redirects handled server-side

### Cache Invalidation
- [ ] Specific query keys, not global
- [ ] Invalidates all affected queries
- [ ] Uses new syntax: `{ queryKey: [...] }`
- [ ] Scoped to license when needed

---

## Automated Verification

```bash
# Find React Query usage
grep -r "useQuery\|useMutation" resources/js --include="*.tsx"

# Find cache invalidations
grep -r "invalidateQueries" resources/js --include="*.tsx"

# Check for global invalidation (anti-pattern)
grep -r "invalidateQueries()" resources/js --include="*.tsx"

# Check for old syntax
grep -r "invalidateQueries(\[" resources/js --include="*.tsx"
```

---

## Real-World Examples

### Good: QuickBooks Dashboard (React Query)

```typescript
const { invoices, items, isLoading, refetch } = useQuickBooksData();

// Fast refresh without page reload
<button onClick={() => refetch()}>Refresh</button>
```

### Good: Package Creation (Inertia)

```typescript
const { data, setData, post } = useForm({ name: '', quantity: 0 });

post('/metrc/packages/create', {
    onSuccess: () => {
        onClose();  // MainLayout handles flash message
    }
});
```

### Bad: Form with React Query

```typescript
// ❌ WRONG
const mutation = useMutation({
    mutationFn: (data) => axios.post('/api/create', data)
});
```

---

## When in Doubt

**Ask these questions:**

1. Does the user navigate after this operation?
   - Yes → Use Inertia
   - No → Consider React Query

2. Is this a form submission?
   - Yes → Use Inertia
   - No → Consider React Query

3. Does data change frequently and need background refetching?
   - Yes → Use React Query
   - No → Use Inertia

4. Is this a dashboard with multiple data sources?
   - Yes → Use React Query
   - No → Use Inertia

5. Do I need optimistic UI updates?
   - Yes → Use React Query mutation
   - No → Use Inertia

---

## Advanced Patterns

### Composite Hooks (Aggregating Multiple Queries)

**Pattern:** Create a single hook that aggregates multiple related queries for convenience.

```typescript
// ✅ GOOD - Composite hook pattern
export function useQuickBooksData(enabled: boolean = true) {
    const invoices = useQuickBooksInvoices(enabled);
    const creditMemos = useQuickBooksCreditMemos(enabled);
    const items = useQuickBooksItems(enabled);

    return {
        // Data arrays
        invoices: invoices.data || [],
        creditMemos: creditMemos.data || [],
        items: items.data || [],

        // Overall loading state
        isLoading: invoices.isLoading || creditMemos.isLoading || items.isLoading,

        // Individual loading states (for granular UI feedback)
        loadingStates: {
            invoices: invoices.isLoading,
            creditMemos: creditMemos.isLoading,
            items: items.isLoading,
        },

        // Refetch functions
        refetch: {
            invoices: invoices.refetch,
            creditMemos: creditMemos.refetch,
            items: items.refetch,
        },
    };
}
```

**Use When:**
- Dashboard/page needs multiple related data sources
- Want to avoid repeating multiple useQuery calls
- Need aggregate loading states

**Reference:** `resources/js/Hooks/useQuickBooksData.tsx`

---

### Domain-Organized 3-Layer Architecture

**Pattern:** Separate domain logic into three files: `keys.ts`, `queries.ts`, and `use*.ts` hook wrappers.

```
resources/js/Hooks/{domain}/
├── keys.ts         # Key factories only
├── queries.ts      # queryOptions factories + private fetch functions
└── use*.ts         # Hook wrappers (spread queryOptions) + mutations
```

```typescript
// ── keys.ts — Key factories only ──
// Two patterns: flat (metrc) or hierarchical (marketplace)

// Pattern A: Flat (most Metrc reference data)
export const metrcPackageKeys = {
    all: () => ['metrc-packages'] as const,
    byLicense: (license: string | null) => [...metrcPackageKeys.all(), license] as const,
    paginated: (license: string | null, page: number, perPage: number) =>
        ['metrc-packages-paginated', license, page, perPage] as const,
    paginatedPrefix: (license: string | null) =>
        ['metrc-packages-paginated', license] as const,  // for broad invalidation
};

// Pattern B: Hierarchical (marketplace entities with granular invalidation)
export const marketplaceOrderKeys = {
    all: (orgId: string, viewMode: 'seller' | 'buyer') =>
        ['marketplace-orders', orgId, viewMode] as const,
    lists: (orgId: string, viewMode: 'seller' | 'buyer') =>
        [...marketplaceOrderKeys.all(orgId, viewMode), 'list'] as const,
    list: (orgId: string, viewMode: 'seller' | 'buyer', filters?: object) =>
        [...marketplaceOrderKeys.lists(orgId, viewMode), filters] as const,
    details: (orgId: string, viewMode: 'seller' | 'buyer') =>
        [...marketplaceOrderKeys.all(orgId, viewMode), 'detail'] as const,
    detail: (orgId: string, viewMode: 'seller' | 'buyer', id: string) =>
        [...marketplaceOrderKeys.details(orgId, viewMode), id] as const,
};
```

```typescript
// ── queries.ts — queryOptions factories + private fetchers ──
import { queryOptions } from '@tanstack/react-query';
import { STALE_TIME } from '@/constants/query-config';
import { metrcPackageKeys } from './keys';
import axios from 'axios';

// Private fetch function (NOT exported)
const fetchPackages = async (license: string, signal?: AbortSignal) => {
    const { data } = await axios.get(`/metrc/packages/${license}`, { signal });
    return data.packages;
};

// Exported queryOptions factory
export const metrcQueries = {
    packages: (license: string | null) => queryOptions({
        queryKey: metrcPackageKeys.byLicense(license),
        queryFn: ({ signal }) => fetchPackages(license!, signal),
        staleTime: STALE_TIME.DEFAULT,
    }),
};
```

```typescript
// ── useMetrcPackages.ts — Hook wrapper ──
import { useQuery } from '@tanstack/react-query';
import { metrcQueries } from './queries';

export function useMetrcPackages(license: string | null, enabled = true) {
    return useQuery({
        ...metrcQueries.packages(license),  // spread queryOptions
        enabled: enabled && !!license,       // add/override at consumption
    });
}
```

**Use When:**
- Domain has multiple related queries (metrc, marketplace, leaflink)
- Keys need to be imported separately for invalidation in mutations
- Multiple hooks share the same fetch logic via `queryOptions`

**When to co-locate instead (single file):**
- Small domains with 1-2 queries (e.g., `usePendingTransferCart.tsx`, `useForecastBatch.tsx`)
- Page-specific queries unlikely to be reused (e.g., `Pages/Org/Items/items-queries.ts`)

**Naming Conventions:**
- Key factory names: `{entity}Keys` (e.g., `metrcPackageKeys`, `marketplaceOrderKeys`)
- Query factory names: `{domain}Queries` (e.g., `metrcQueries`, `marketplaceOrderQueries`)
- Top-level key strings: kebab-case (`'metrc-packages'`, `'marketplace-orders'`)
- Hook functions: `useCamelCase` (React convention, required by React)

---

### useLocalSync Pattern (Optimistic Updates with Props)

**Pattern:** Maintain local state synchronized with server props for optimistic updates.

```typescript
// ✅ GOOD - useLocalSync pattern
export function useLocalSync<T>(initialData: T[]) {
    const [localData, setLocalData] = useState<T[]>(initialData);

    // Sync local state with prop changes from server
    useEffect(() => {
        setLocalData(initialData);
    }, [initialData]);

    return [localData, setLocalData] as const;
}

// Usage in component:
const [localItems, setLocalItems] = useLocalSync<Item>(items);

// Optimistic update before server confirms
const handleUpdate = (itemId: number, newValue: number) => {
    setLocalItems(prev => prev.map(item =>
        item.Id === itemId ? { ...item, quantity: newValue } : item
    ));

    // Server update happens async
    updateMutation.mutate({ itemId, newValue });
};
```

**Use When:**
- Need optimistic UI updates while waiting for server
- Data passed via Inertia props but needs client-side modifications
- Combining server-driven data with local mutations

**Reference:** `resources/js/Hooks/useLocalSync.tsx`

---

### Non-React-Query Refresh Hooks

**Pattern:** For Metrc data refreshes that POST to trigger Metrc API sync (not pure React Query caching).

```typescript
// ✅ GOOD - useRefreshMetrcItems pattern
export function useRefreshMetrcItems(setItems: (items: Item[]) => void) {
    const [isRefreshing, setIsRefreshing] = useState(false);

    const refreshItems = async () => {
        setIsRefreshing(true);
        try {
            const response = await axios.post('/metrc/refresh/items');
            setItems(response.data.items);
            toast.success('Items refreshed from Metrc');
        } catch (error) {
            toast.error('Failed to refresh items');
        } finally {
            setIsRefreshing(false);
        }
    };

    return { refreshItems, isRefreshing };
}

// Usage with useLocalSync:
const [localItems, setLocalItems] = useLocalSync<Item>(items);
const { refreshItems, isRefreshing } = useRefreshMetrcItems(setLocalItems);

<RefreshButton onClick={refreshItems} disabled={isRefreshing} />
```

**Why NOT React Query?**
- Triggers external API sync (Metrc API call) not just cache refresh
- Server POST endpoint that fetches fresh data from Metrc
- Updates Inertia-provided prop data, not query cache

**Reference:** `resources/js/Hooks/useRefreshMetrcItems.tsx`, `useRefreshMetrcLocations.tsx`

---

### Optimistic Update Callbacks

**Pattern:** Pass callback props to allow parent components to update their local state optimistically.

```typescript
// ✅ GOOD - Callback pattern for optimistic updates
const statusMutation = useMutation({
    mutationFn: async (listing_state: string) => {
        const response = await axios.patch(`/orders/leaflink/inventory/${item.id}`, {
            listing_state,
        });
        return response.data;
    },
    onSuccess: (data) => {
        toast.success('Status updated');

        // Update parent's local state via callback
        onItemUpdated(data.item);

        // Also invalidate cache for background refetch
        queryClient.invalidateQueries({ queryKey: ['leaflink-inventory', license] });
    },
});
```

**Callback Naming Conventions:**
- `onItemUpdated` - Single item update
- `onLocalUpdate` - Immediate local update before server response
- `onSuccess` - After mutation completes

**Reference:** `resources/js/Components/InventoryStatusMenu.tsx`, inline edit hooks

---

### Two-Click Confirmation Pattern

**Pattern:** Require two clicks for dangerous mutations (archive, delete, etc).

```typescript
// ✅ GOOD - Confirmation workflow
const [pendingConfirmation, setPendingConfirmation] = useState<string | null>(null);

const handleDangerousAction = (itemId: string, requiresConfirmation: boolean) => {
    // First click: set pending
    if (requiresConfirmation && pendingConfirmation !== itemId) {
        setPendingConfirmation(itemId);
        return;
    }

    // Second click: execute
    dangerousMutation.mutate(itemId);
    setPendingConfirmation(null);
};

// Visual feedback for pending confirmation
const buttonClass = pendingConfirmation === itemId
    ? 'bg-orange-100 text-orange-800'  // Pending state
    : 'text-red-700 hover:bg-red-50';   // Normal state
```

**Reference:** `resources/js/Components/InventoryStatusMenu.tsx`

---

## Related Patterns

- **frontend-critical.md** - Component patterns, modal behavior
- **frontend-typescript.md** - Type safety for query hooks
- **backend-flash-messages.md** - Flash message integration
- `.claude/docs/frontend/data-fetching.md` - **FULL documentation with examples**

### Reference Implementations

**3-Layer Domain Pattern (keys → queries → hooks):**
- `resources/js/Hooks/metrc/keys.ts` - Key factories (flat pattern)
- `resources/js/Hooks/metrc/queries.ts` - `queryOptions` factories with `STALE_TIME`
- `resources/js/Hooks/metrc/useMetrcPackages.ts` - Hook wrapper with spread pattern
- `resources/js/Hooks/marketplace/keys.ts` - Key factories (hierarchical pattern)
- `resources/js/Hooks/marketplace/queries.ts` - Multiple named `queryOptions` exports
- `resources/js/Hooks/marketplace/useMarketplaceOrders.ts` - Hook + mutations + optimistic updates

**Co-located Queries (small domains):**
- `resources/js/Hooks/useQuickBooksData.tsx` - Composite hook with inline keys/queries
- `resources/js/Pages/Org/Items/items-queries.ts` - Page-level co-located queries

**Stale Time Constants:**
- `resources/js/constants/query-config.ts` - All `STALE_TIME` constants

**Prefetch Utilities:**
- `resources/js/Hooks/metrc/prefetch.ts` - `usePrefetchPages` for adjacent-page prefetch

**Supporting Hooks:**
- `resources/js/Hooks/useLocalSync.tsx` - Local state sync with props
- `resources/js/Hooks/useRefreshMetrcItems.tsx` - Non-React-Query refresh

**Component Examples:**
- `resources/js/Components/InventoryStatusMenu.tsx` - Mutation with confirmation workflow
- `resources/js/Pages/Quickbooks/Dashboard.tsx` - Using composite hook
