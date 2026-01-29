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
- [ ] Appropriate `staleTime` for entity type
  - Invoices/Credit Memos: 2 min
  - Inventory/Packages: 5 min (default)
  - Items/Products: 10 min
  - Terms/Accounts: 10 min
- [ ] `retry` configuration (default 1 is usually fine)
- [ ] `enabled` parameter if conditional fetching

### Query Key
- [ ] Follows naming convention (kebab-case)
- [ ] Plural for lists (`invoices` not `invoice`)
- [ ] License-scoped if org/facility specific
- [ ] Consistent with other queries

### Error Handling
- [ ] `onError` callback with toast notification
- [ ] Console.error for debugging (optional)
- [ ] User-friendly error message

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
// ❌ WRONG - Uses default 5 min for rarely-changing data
useQuery({
    queryKey: ['quickbooks-items'],
    queryFn: fetchItems,
});

// ✅ FIX - Appropriate staleTime
useQuery({
    queryKey: ['quickbooks-items'],
    queryFn: fetchItems,
    staleTime: 10 * 60 * 1000,  // 10 min for rarely-changing data
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

## Example: Compliant Query Hook

```typescript
import { useQuery, UseQueryResult } from '@tanstack/react-query';
import axios from 'axios';
import { toast } from 'react-toastify';

type Invoice = {
    Id: string;
    DocNumber: string;
    TotalAmt: number;
};

const fetchInvoices = async (): Promise<Invoice[]> => {
    const response = await axios.get<Invoice[]>('/quickbooks/invoices');
    return response.data;
};

export function useQuickBooksInvoices(enabled: boolean = true): UseQueryResult<Invoice[], Error> {
    return useQuery({
        queryKey: ['quickbooks-invoices'],
        queryFn: fetchInvoices,
        enabled,
        staleTime: 2 * 60 * 1000,  // 2 minutes (frequent changes)
        retry: 2,
        onError: (error: Error) => {
            console.error('Failed to load QuickBooks invoices:', error);
            toast.error('Failed to load invoices. Please refresh the page.');
        },
    });
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

**HIGH**:
- Wrong staleTime for entity type
- Missing error handling
- Incorrect query key naming
