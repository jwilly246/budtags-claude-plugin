# Scenario: React Query Hook

**Use this checklist when verifying React Query usage (data fetching, NOT forms).**

---

## Required Pattern Files

- `patterns/frontend-data-fetching.md` - **CRITICAL**
- `.claude/docs/frontend/data-fetching.md` - Full reference
- `patterns/frontend-typescript.md` - Type safety

---

## Decision: Is React Query Appropriate?

**Use React Query ONLY when:**
- [ ] Read-heavy data fetching (dashboards, lists)
- [ ] Data changes frequently and needs refetching
- [ ] Inline editing with optimistic updates
- [ ] Staying on same page (no navigation)
- [ ] Need client-side caching

**DO NOT use React Query for:**
- [ ] Form submissions (use Inertia `useForm`)
- [ ] Standard CRUD operations that redirect
- [ ] Operations that navigate to new page

---

## Query Hook Verification Checklist

### Hook Structure
- [ ] Proper TypeScript types (NO `any`)
- [ ] Defined return type for query function
- [ ] Uses `UseQueryResult<DataType, Error>` return type

### Configuration
- [ ] Uses `STALE_TIME` constant from `@/constants/query-config` (never raw numbers)
  - `STALE_TIME.SHORT` (2 min) — invoices, credit memos, frequently changing
  - `STALE_TIME.DEFAULT` (5 min) — inventory, packages, products, customers
  - `STALE_TIME.LONG` (10 min) — brands, rarely changing items
  - `STALE_TIME.REFERENCE` (30 min) — categories, strains, UOM
  - `STALE_TIME.REGULATORY` (24 hr) — lab test batches, compliance categories
- [ ] `retry` configuration (default 1 is usually fine)
- [ ] `enabled` parameter if conditional fetching

### Query Key
- [ ] Follows naming convention (kebab-case)
- [ ] Plural for lists (`invoices` not `invoice`)
- [ ] License-scoped if org/facility specific
- [ ] Consistent with other queries

### Error Handling
- [ ] Error state handled in consuming component via returned `error`/`isError` (v5 removed `onError` from `useQuery`)
- [ ] User-friendly error display in component JSX
- [ ] Optional: `throwOnError` for error boundary delegation

---

## Mutation Verification Checklist

### Mutation Structure
- [ ] Appropriate use case (inline edits, NOT form submissions)
- [ ] Proper TypeScript types
- [ ] Uses `useMutation` hook

### Cache Invalidation
- [ ] Invalidates correct cache keys after success
- [ ] NO global invalidation (`queryClient.invalidateQueries()` with no key)
- [ ] Uses new syntax: `{ queryKey: [...] }`
- [ ] Scoped to license when needed

### Optimistic Updates (for inline edits)
- [ ] `onLocalUpdate` callback for immediate UI feedback
- [ ] UI reverts on error (cache refetch)
- [ ] Success toast shown
- [ ] Error toast shown with details

### Callback Props Pattern
- [ ] If updating parent state, uses callback props (`onItemUpdated`, `onLocalUpdate`)
- [ ] Callback called BEFORE cache invalidation (for instant UI update)
- [ ] Follows naming convention (`onItemUpdated` for single items)

---

## Supporting Patterns Verification

### Composite Hooks (if applicable)
- [ ] Aggregates multiple related queries
- [ ] Returns structured object with data, loading states, and refetch functions
- [ ] All underlying queries use same `enabled` parameter
- [ ] Provides both aggregate and individual loading states

### useLocalSync Pattern (if using Inertia props + React Query)
- [ ] Uses `useLocalSync` to sync local state with server props
- [ ] Setter passed to refresh hooks or optimistic update callbacks
- [ ] useEffect syncs when initialData changes
- [ ] Returns tuple: `[localData, setLocalData] as const`

### Non-React-Query Refresh (if applicable)
- [ ] Uses axios directly, NOT React Query (for Metrc API sync)
- [ ] Has loading state (`isRefreshing`)
- [ ] Shows toast notifications on success/error
- [ ] Updates local state via callback, NOT query cache
- [ ] Pattern: POST to `/metrc/refresh/{entity}` endpoint

---

## Common Violations

### Using React Query for Form Submission
```typescript
// ❌ WRONG - Use Inertia for forms!
const mutation = useMutation({
    mutationFn: (data) => axios.post('/api/create', data),
    onSuccess: () => {
        toast.success('Created');  // Should be backend flash message!
    }
});

// ✅ FIX - Use Inertia
const { post } = useForm({ name: '' });
post('/api/create');
```

### Global Cache Invalidation
```typescript
// ❌ WRONG - Invalidates EVERYTHING!
queryClient.invalidateQueries();

// ✅ FIX - Specific key
queryClient.invalidateQueries({ queryKey: ['metrc-items'] });
```

### No staleTime Configuration
```typescript
// ❌ WRONG - Relies on global default for rarely-changing data
useQuery({
    queryKey: ['quickbooks-items'],
    queryFn: fetchItems,
});

// ❌ WRONG - Raw milliseconds instead of STALE_TIME constant
useQuery({
    queryKey: ['quickbooks-items'],
    queryFn: fetchItems,
    staleTime: 10 * 60 * 1000,
});

// ✅ FIX - Use STALE_TIME constant from @/constants/query-config
import { STALE_TIME } from '@/constants/query-config';

useQuery({
    ...qbQueries.items(),  // queryOptions factory handles key + fn + staleTime
    enabled,
});
```

### Old Syntax
```typescript
// ❌ WRONG - Old syntax
queryClient.invalidateQueries(['qbo-items']);

// ✅ FIX - New syntax
queryClient.invalidateQueries({ queryKey: ['quickbooks-items'] });
```

---

## Example: Compliant 3-Layer Query Pattern

BudTags uses a 3-layer architecture: **keys.ts** → **queries.ts** → **use*.ts** hooks.

```typescript
// ── Layer 1: Key Factory (keys.ts) ──
export const quickbooksKeys = {
    invoices: () => ['quickbooks-invoices'] as const,
    items: () => ['quickbooks-items'] as const,
};

// ── Layer 2: queryOptions Factory (queries.ts) ──
import { queryOptions } from '@tanstack/react-query';
import { STALE_TIME } from '@/constants/query-config';
import { quickbooksKeys } from './keys';
import axios from 'axios';

type Invoice = {
    Id: string;
    DocNumber: string;
    TotalAmt: number;
};

const fetchInvoices = async (signal?: AbortSignal): Promise<Invoice[]> => {
    const { data } = await axios.get<Invoice[]>('/quickbooks/invoices', { signal });
    return data;
};

export const qbQueries = {
    invoices: () => queryOptions({
        queryKey: quickbooksKeys.invoices(),
        queryFn: ({ signal }) => fetchInvoices(signal),
        staleTime: STALE_TIME.SHORT,
        retry: 2,
    }),
};

// ── Layer 3: Hook Wrapper (useQuickBooksData.tsx) ──
import { useQuery } from '@tanstack/react-query';
import { qbQueries } from './queries';

export function useQuickBooksInvoices(enabled: boolean = true) {
    return useQuery({
        ...qbQueries.invoices(),  // spread queryOptions (key + fn + staleTime)
        enabled,                   // add/override options at consumption point
    });
}

// ── Error handling in consuming component (NOT in hook) ──
function InvoicesDashboard() {
    const { data: invoices, isLoading, error } = useQuickBooksInvoices();

    if (error) return <div className="text-red-600">Failed to load invoices</div>;
    if (isLoading) return <Spinner />;
    return <InvoicesTable data={invoices} />;
}
```

## Example: Compliant Mutation

```typescript
const updateMutation = useMutation({
    mutationFn: async ({ itemId, newValue }: { itemId: number; newValue: number }) => {
        const response = await axios.patch(`/api/items/${itemId}`, {
            current_quantity: newValue,
        });
        return response.data;
    },
    onSuccess: () => {
        toast.success('Quantity updated');
        queryClient.invalidateQueries({ queryKey: ['inventory-items'] });
    },
    onError: (error: unknown) => {
        if (error instanceof AxiosError) {
            toast.error(error.response?.data?.message ?? 'Update failed');
        } else {
            toast.error('An unexpected error occurred');
        }
    },
});
```

---

## Automated Verification

```bash
# Find React Query usage
grep -r "useQuery\|useMutation" resources/js --include="*.tsx"

# Check for global invalidation (anti-pattern)
grep -r "invalidateQueries()" resources/js --include="*.tsx"
```

---

## Priority

**CRITICAL**:
- Using React Query for form submissions
- Global cache invalidation
- Using `onError` in `useQuery` options (removed in v5)
- Raw millisecond staleTime instead of `STALE_TIME` constants

**HIGH**:
- Not using 3-layer pattern (keys.ts → queries.ts → hooks)
- Wrong staleTime constant for entity type
- Incorrect query key naming (must be kebab-case)
