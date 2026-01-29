# Frontend Data Fetching Patterns

**Source:** `.claude/docs/frontend/data-fetching.md`
**Last Updated:** 2025-12-13
**Pattern Count:** React Query vs Inertia decision patterns + supporting hooks

---

## Overview

BudTags uses **two data fetching patterns**: React Query (client-side caching) and Inertia (server-driven). Using the wrong tool creates bugs and poor UX.

**Architecture Note (Dec 2025):** BudTags uses a **hooks-as-services** pattern where React Query hooks serve AS the service layer. There is NO separate `services/` directory - this is intentional. All fetch functions, query keys, and mutations are co-located in hook files.

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

Use the `STALE_TIME` constants from `@/app` for consistency:

```typescript
import { STALE_TIME } from '@/app';
// STALE_TIME.SHORT (2 min), DEFAULT (5 min), LONG (10 min), REGULATORY (24 hr)
```

| Entity Type | Stale Time | Constant | Example |
|-------------|------------|----------|---------|
| Invoices/Credit Memos | 2 min | `STALE_TIME.SHORT` | `useQuickBooksInvoices` |
| Inventory/Packages | 5 min | `STALE_TIME.DEFAULT` | `useMetrcItems` |
| Items/Products | 10 min | `STALE_TIME.LONG` | `useQuickBooksItems` |
| Terms/Accounts | 10 min | `STALE_TIME.LONG` | `useQuickBooksTerms` |
| **Regulatory/Static** | **24 hr** | `STALE_TIME.REGULATORY` | `useTestBatches` |

**REGULATORY** is for data that only changes with regulatory updates (test batch types, compliance categories, etc.)

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

### Domain-Organized Hooks (Consolidated Domain Logic)

**Pattern:** Consolidate all hooks, constants, and helpers for a domain into a single file.

This extends the Composite Hook pattern by also including:
- Module-level **constants** (exported)
- Module-level **pure helper functions** (exported)
- **Private fetchers** (internal)
- **Individual hooks** (exported)
- **Composite hook** that aggregates everything (exported)

```typescript
// ✅ GOOD - Domain-organized hook file structure
// resources/js/Hooks/useTestingData.tsx

// ========================================
// Constants (module-level, exported)
// ========================================
export const PRODUCT_CATEGORY_TO_TEST_BATCH: Record<string, string> = { ... };
export const RELEVANT_ADDITIONAL_TESTS: Record<string, string[]> = { ... };

// ========================================
// Pure Helper Functions (module-level, exported)
// ========================================
export const categorizeTestBatch = (batch: TestBatch): 'compliance' | 'additional' | 'rd' | 'other' => {
    // Pure function - no React hooks, just logic
};

// ========================================
// Private Fetchers (internal)
// ========================================
const fetchTestBatches = async (): Promise<TestBatch[]> => {
    const response = await fetch('/metrc/lab-tests/batches');
    return response.json();
};

// ========================================
// Individual Hooks (exported)
// ========================================
export function useTestBatches(enabled: boolean = true) {
    return useQuery({
        queryKey: ['metrc-test-batches'],
        queryFn: fetchTestBatches,
        enabled,
        staleTime: STALE_TIME.REGULATORY,
    });
}

export function useSampleSizeCalculation(packages: Package[], category: string | null) {
    return useMemo(() => {
        // Calculation logic
    }, [packages, category]);
}

// ========================================
// Composite Hook (exports everything needed)
// ========================================
export function useTestingData({ packages, enabled = true }) {
    const { data: testBatches, isLoading, error, refetch } = useTestBatches(enabled);
    const primaryCategory = usePrimaryCategory(packages);
    const suggestedBatch = useSuggestedBatch(primaryCategory, testBatches);

    return {
        testBatches,
        isLoading,
        error,
        refetch,
        primaryCategory,
        suggestedBatch,
        // Expose helper functions for UI
        categorizeTestBatch,
    };
}
```

**Use When:**
- Domain has multiple related hooks, constants, and helpers
- Want to reduce imports in consumer components
- Logic is domain-specific (testing, QuickBooks, LeafLink, etc.)
- Need to share constants between hooks and UI

**Naming Convention:**
- File: `use{Domain}Data.tsx` (e.g., `useTestingData.tsx`, `useQuickBooksData.tsx`)
- Constants: `UPPER_SNAKE_CASE`
- Helper functions: `snake_case` preferred (e.g., `categorize_test_batch`)
- Hooks: `useCamelCase` (React convention, required by React)
- Variables: `snake_case` preferred

**Reference:** `resources/js/Hooks/useTestingData.tsx`, `resources/js/Hooks/useQuickBooksData.tsx`

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

**Query Hooks:**
- `resources/js/Hooks/useQuickBooksData.tsx` - Composite hook pattern
- `resources/js/Hooks/useMetrcItems.tsx` (in useQuickBooksData.tsx) - Single query hook

**Mutation Hooks:**
- `resources/js/Hooks/useInlineQuantityEdit.tsx` - Mutation with optimistic updates
- `resources/js/Hooks/useInlineTextEdit.tsx` - Text field mutations

**Supporting Hooks:**
- `resources/js/Hooks/useLocalSync.tsx` - Local state sync with props
- `resources/js/Hooks/useRefreshMetrcItems.tsx` - Non-React-Query refresh
- `resources/js/Hooks/useRefreshMetrcLocations.tsx` - Non-React-Query refresh

**Component Examples:**
- `resources/js/Components/InventoryStatusMenu.tsx` - Mutation with confirmation workflow
- `resources/js/Components/ChangeItemModal.tsx` - Combining useLocalSync + useMetrcItems
- `resources/js/Pages/Quickbooks/Dashboard.tsx` - Using composite hook
