# Frontend Critical Patterns

**Source:** `.claude/docs/frontend/components.md`, `.claude/docs/frontend/structure.md`
**Last Updated:** 2025-12-13
**Pattern Count:** Essential React/Inertia patterns + React 19 features

> **Note (Dec 2025):** Added React 19 useTransition pattern, expanded deferred props with Inertia::defer(), added TableSkeleton pattern.

---

## Overview

Critical patterns for React components, Inertia integration, and modal behavior. These patterns ensure consistent UX and prevent common bugs.

---

## Pattern 1: Self-Contained Modal Components

**Rule:** Modal components handle their own form state and API calls. NO parent-managed submission.

### ✅ CORRECT - Self-Contained Modal

```typescript
import { useForm } from '@inertiajs/react';
import { useModalState } from '@/Hooks/useModalState';

const MyModal: React.FC<{ isOpen: boolean; onClose: () => void; items: Item[] }> = ({
    isOpen, onClose, items
}) => {
    const { cancelButtonRef, getTodayDate } = useModalState(isOpen);
    const { data, setData, post } = useForm({
        name: '',
        quantity: 0,
        item_ids: [],
    });

    useEffect(() => {
        if (isOpen) {
            setData('item_ids', items.map(i => i.Id));
        }
    }, [isOpen]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        post('/api/endpoint', {
            onSuccess: () => {
                onClose();
            },
            onError: (errors) => {
                toast.error(Object.values(errors)[0] as string);
            }
        });
    };

    return (
        <Modal show={isOpen} onClose={onClose}>
            <form onSubmit={handleSubmit}>
                <InputSelect value={data.name} onChange={(e) => setData('name', e.target.value)} />
                <Button ref={cancelButtonRef}>Cancel</Button>
                <Button primary>Save</Button>
            </form>
        </Modal>
    );
};
```

### ❌ WRONG - Parent Manages Everything

```typescript
// ❌ Don't do this: Parent shouldn't handle modal's internal logic
const handleSubmit = (data) => { router.post(...) };
<MyModal isOpen={open} onClose={close} onSubmit={handleSubmit} />
```

---

## Pattern 2: useForm for Form State

**Rule:** Use Inertia's `useForm` hook. NO multiple `useState` for form fields.

### ✅ CORRECT

```typescript
const { data, setData, post, processing, errors } = useForm({
    name: '',
    quantity: 0,
    location_id: '',
});

<InputText
    value={data.name}
    onChange={(e) => setData('name', e.target.value)}
    errors={errors.name}
/>
```

### ❌ WRONG

```typescript
// ❌ Multiple useState - verbose and error-prone
const [name, setName] = useState('');
const [quantity, setQuantity] = useState(0);
const [locationId, setLocationId] = useState('');
const [processing, setProcessing] = useState(false);
const [errors, setErrors] = useState({});
```

---

## Pattern 3: Toast Notifications (Typed Methods)

**Rule:** Use typed toast methods (`toast.error()`, `toast.success()`). NEVER use `alert()`.

### ✅ CORRECT

```typescript
// Validation errors
toast.error('Please select at least one item');

// Success feedback (client-side, before API call)
toast.success('Processing...');

// Warning
toast.warning('This action cannot be undone');

// In onError handler
onError: (errors) => {
    const message = Object.values(errors)[0] as string;
    toast.error(message || 'Validation failed');
}
```

### ❌ WRONG

```typescript
// ❌ Never use alert()!
alert('Please select at least one item');

// ❌ Generic toast (no color)
toast('Error occurred');  // Use toast.error()

// ❌ Manual flash handling (MainLayout handles it)
onSuccess: (page) => {
    toast.success((page.props as any).flash?.success);
}
```

---

## Pattern 4: onSuccess / onError Handling

**Rule:** ALWAYS handle both callbacks. `onSuccess` for component state, `onError` for validation feedback.

### ✅ CORRECT

```typescript
router.post('/api/endpoint', data, {
    preserveScroll: true,
    onSuccess: () => {
        onClose();  // Component state
        queryClient.invalidateQueries(['items']);
    },
    onError: (errors) => {
        const message = Object.values(errors)[0] as string;
        toast.error(message || 'Failed to submit');
    }
});
```

### ❌ WRONG

```typescript
// ❌ No error handling!
router.post('/api/endpoint', data, {
    onSuccess: () => {
        onClose();
    }
    // Missing onError!
});

// ❌ Using alert in onError
onError: (errors) => {
    alert('Error!');  // Use toast.error()
}
```

---

## Pattern 5: Inertia Deferred Props (`Inertia::defer()`)

**Rule:** Use `Inertia::defer()` for heavy data payloads to render page shell immediately, then load data in background.

### PHP Controller Side

```php
return Inertia::render('Org/MetrcNavigatorPackages', [
    // IMMEDIATE - Needed for page shell (renders first)
    'metrc_employee_id' => $user->metrc_employee_id,
    'legacy_view_preference' => $user->getLegacyViewPreference(),
    'strains' => $strains,
    'templates' => $templates,

    // DEFERRED - Heavy payload loaded after render
    'packages_data' => Inertia::defer(function () use ($api, $facility, $user) {
        ini_set('memory_limit', '256M');
        $api->set_user($user);

        $days_of_packages = $api->get_history_from_cache($facility, now(), 365);
        return [
            'days_of_packages' => $days_of_packages,
            'available_package_tags' => $api->package_available_tags($facility),
        ];
    }),

    // DEFERRED (named group) - Reference data (parallel loading)
    'reference_data' => Inertia::defer(function () use ($api, $facility, $user) {
        return [
            'locations' => $api->locations($facility),
            'employees' => $employees,
            'recipe_data' => ItemRecipe::where('organization_id', $user->active_org->id)->get(),
        ];
    }, 'reference'),  // Named group for parallel loading
]);
```

### React Component Side

```typescript
export type MetrcNavigatorPackagesPageProps = {
    // IMMEDIATE - Available on page load
    metrc_employee_id: string;
    legacy_view_preference: boolean;
    strains: Strain[];
    templates: Template[];

    // DEFERRED - undefined until loaded
    packages_data?: {
        days_of_packages: PackagesByDate[];
        available_package_tags: PackageTag[];
    };
    reference_data?: {
        locations: Location[];
        employees: Employee[];
        recipe_data: Record<number, ItemRecipe[]>;
    };
};

// Check loading state
const isPackagesLoading = !props.packages_data;
const isReferenceLoading = !props.reference_data;

// Render skeleton or content
{isPackagesLoading ? (
    <TableSkeleton rows={10} columns={6} message="Loading packages..." />
) : (
    <PackagesTable data={props.packages_data.days_of_packages} />
)}
```

### When to Use Deferred Props

- **Large datasets** (365 days of packages, 1000+ items)
- **Multiple API calls** (Metrc API fetches that take 2-5s)
- **Reference data** that isn't needed for initial render
- **Heavy computations** on server side

### ✅ CORRECT - Silent Saves on Deferred Pages

For "fire-and-forget" saves, use `axios.post()` to avoid triggering deferred prop re-evaluation:

```typescript
import axios from 'axios';

// Preference saves - no page update needed
const handleColumnVisibilityChange = useCallback((visibility: VisibilityState) => {
    axios.post('/user/preferences/table-columns/packages', {
        columnVisibility: visibility,
    });
}, []);
```

### ❌ WRONG - router.post on Deferred Pages

```typescript
// ❌ Causes skeleton flash - deferred props become undefined again!
router.post('/user/preferences/table-columns/packages', {
    columnVisibility: visibility
}, {
    preserveState: true,  // Doesn't help - redirect still triggers re-fetch
});
```

### Backend for Silent Saves

```php
// Return 204 No Content - not redirect
return response()->noContent();
```

### TableSkeleton Component

Use `TableSkeleton` for loading states with deferred props:

```typescript
import { TableSkeleton } from '@/Components/Skeletons/TableSkeleton';

interface TableSkeletonProps {
    rows?: number;       // Default: 10
    columns?: number;    // Default: 6
    showHeader?: boolean; // Default: true
    message?: string;    // Default: "Loading data..."
}

// Usage
{isLoading ? (
    <TableSkeleton rows={10} columns={6} message="Loading packages..." />
) : (
    <DataTable data={data} />
)}
```

**Skeleton Behavior:**
- Shows spinner + message above skeleton table
- Animates with pulse effect
- Matches approximate table layout

---

## Pattern 6: React 19 useTransition

**Rule:** Use `useTransition` for form submissions and modal actions in React 19. Keeps UI responsive during async operations.

### ✅ CORRECT - useTransition for Submissions

```typescript
import { useState, useTransition } from 'react';

const [isPending, startTransition] = useTransition();

const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // ... validation ...

    startTransition(() => {
        createTransfer.mutate(payload, {
            onSuccess: () => {
                setFormData(initialFormState);
                onSuccess();
            }
        });
    });
};

// Combine both pending states for button
<Button
    primary
    disabled={isPending || createTransfer.isPending}
>
    {(isPending || createTransfer.isPending) ? 'Creating...' : 'Create Transfer'}
</Button>
```

### ❌ WRONG - Old useState Pattern

```typescript
// ❌ Old pattern - manual state management
const [isLoading, setIsLoading] = useState(false);

const handleSubmit = async () => {
    setIsLoading(true);
    try {
        await api.create(data);
        setIsLoading(false);
    } catch (e) {
        setIsLoading(false);  // Must handle in both branches
    }
};
```

### When to Use Each Pattern

| Pattern | Use Case |
|---------|----------|
| `useTransition` | Form submissions, modal actions, any UI that should remain responsive |
| `mutation.isPending` | React Query mutations (already tracks state) |
| `useState` + loading | Legacy code, simple one-off states (avoid for new code) |

### Loading State Combination Pattern

When using both `useTransition` and React Query mutations, combine pending states:

```typescript
const [isPending, startTransition] = useTransition();
const mutation = useMutation({ ... });

// Button disabled when EITHER is pending
const isSubmitting = isPending || mutation.isPending;

<Button disabled={isSubmitting}>
    {isSubmitting ? 'Saving...' : 'Save'}
</Button>
```

---

## Pattern 7: Smart Defaults in useEffect (Modals)

**Rule:** Pre-fill smart defaults when modal opens. Only depend on `isOpen`.

### ✅ CORRECT

```typescript
const { data, setData, post } = useForm({
    location_id: '',
    date: '',
});

useEffect(() => {
    if (isOpen) {
        // Smart default: Auto-select if all items in same location
        const locations = items.map(i => i.LocationId);
        if (new Set(locations).size === 1) {
            setData('location_id', locations[0]);
        }

        setData('date', getTodayDate());
    }
}, [isOpen]);  // Only isOpen, not functions
```

### ❌ WRONG

```typescript
// ❌ No smart defaults - user must manually select everything
useEffect(() => {
    if (isOpen) {
        // Just resets, no defaults
    }
}, [isOpen]);

// ❌ Including hook functions in dependencies
}, [isOpen, getTodayDate, setData]);  // Causes re-runs!
```

---

## Pattern 8: BudTags Component & Design System Usage

**Rule:** Use BudTags components and design tokens. NO raw HTML elements or inline dark mode classes.

### 8a: Reusable Input Components

Use `InputSelect`, `InputDate`, `InputText`, etc. NO raw HTML inputs.

```typescript
// ✅ CORRECT
<InputSelect label="Location" value={data.location_id} onChange={(e) => setData('location_id', e.target.value)}>
    <option value="">Select Location</option>
</InputSelect>

// ❌ WRONG - Raw HTML
<select value={data.location_id}><option>Select</option></select>
<input type="date" value={data.date} />
```

### 8b: Button Component

Use `Button` component. NO raw `<button>` elements.

```typescript
// ✅ CORRECT - Button component with variants
<Button primary onClick={handleSubmit}>Save</Button>
<Button secondary onClick={onClose}>Cancel</Button>
<Button link danger onClick={handleDelete}>Delete</Button>
<Button lil secondary onClick={handleRefresh}>Refresh</Button>

// ❌ WRONG - Raw button with inline classes
<button onClick={handleSubmit} className="px-4 py-2 bg-blue-600 text-white rounded">Save</button>
```

### 8c: Lucide React Icons

Use Lucide React icons. NO inline `<svg>` elements.

```typescript
// ✅ CORRECT - Lucide React
import { AlertTriangle, Check, X, ChevronDown } from 'lucide-react';
<AlertTriangle className="w-4 h-4" />

// ❌ WRONG - Inline SVG
<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
    <path fillRule="evenodd" d="M8.257 3.099c..." clipRule="evenodd" />
</svg>
```

### 8d: Semantic CSS Tokens (NO inline dark: classes)

Use semantic CSS classes from `app.css`. NO inline `dark:` conditional classes.

```typescript
// ✅ CORRECT - Semantic tokens (auto-switch light/dark)
<div className="info-box">Info message</div>
<div className="warning-box">Warning message</div>
<span className="text-status-danger">Error text</span>
<span className="badge-success">Completed</span>
<div className="surface-muted">Background</div>

// ❌ WRONG - Inline dark: classes
<div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800">
<span className="text-red-600 dark:text-red-400">Error</span>
```

**Available semantic classes (from app.css):**
- **Boxes:** `info-box`, `warning-box`, `error-box`
- **Badges:** `badge-success`, `badge-warning`, `badge-danger`, `badge-info`
- **Text:** `text-status-success`, `text-status-warning`, `text-status-danger`, `text-status-info`
- **Text (on bg):** `text-status-success-text`, `text-status-warning-text`, etc.
- **Backgrounds:** `bg-status-success-bg`, `bg-status-warning-bg`, etc.
- **Surfaces:** `surface-muted`, `surface-card`, `surface-elevated`
- **Borders:** `border-theme-default`, `border-status-info`, etc.

### Automated Scans

```bash
# Inline SVGs (should use Lucide React)
grep -n "<svg" [TSX_FILES] 2>/dev/null

# Raw <button> elements (should use Button component)
grep -n "<button" [TSX_FILES] 2>/dev/null | grep -v "Button.tsx"

# Raw <input> elements (should use Input components)
grep -n "<input" [TSX_FILES] 2>/dev/null | grep -v "Inputs.tsx\|type=\"hidden\""

# Inline dark: classes (should use semantic CSS tokens)
grep -n "dark:" [TSX_FILES] 2>/dev/null
```

### Severity

| Violation | Severity |
|-----------|----------|
| Raw `<button>` | 🔴 **CRITICAL** - Use Button component |
| Inline `dark:` classes | 🟠 **HIGH** - Use semantic CSS tokens |
| Inline `<svg>` | 🟠 **HIGH** - Use Lucide React icons |
| Raw `<input>` | 🟠 **HIGH** - Use Input components |

---

## Pattern 9: Data Flow Verification

**Rule:** Verify data source exists in `HandleInertiaRequests`. NO assumptions about global data.

### ✅ CORRECT - Verified Data Flow

```typescript
// 1. Check HandleInertiaRequests shares this data
const { user } = usePage<PageProps>().props;

// 2. Verify the exact structure
const hasDevFeatures = user?.active_org?.features?.some(f => f.name === 'dev-features') ?? false;

// 3. Use verified data
{hasDevFeatures && <DevOnlyButton />}
```

### ❌ WRONG - Assumptions

```typescript
// ❌ Assumes window.Laravel exists (doesn't in BudTags!)
{(window as any).Laravel?.features?.includes('dev-features') && (
    <button>Admin Only</button>
)}

// ❌ Wrong method - features is array of objects, not strings
{user.active_org.features.includes('dev-features')}  // Use .some()
```

**Verification Steps:**
1. Check `app/Http/Middleware/HandleInertiaRequests::share()` - is data shared?
2. Check TypeScript types - is `PageProps` defined with this structure?
3. Search for similar patterns - how do other components access this data?
4. Verify runtime - does the data path actually work?

---

## Pattern 10: React Compiler Awareness

**Rule:** BudTags uses React 19.2 with React Compiler. The compiler auto-memoizes, reducing need for manual `useMemo`/`useCallback`.

### When React Compiler Works Well
- Standard component patterns
- Pure functions and computations
- Most use cases are handled automatically

### When to Use `'use no-forget'`
Add `'use no-forget'` directive at top of component file when:
- Component has complex side effects the compiler mishandles
- Debugging memoization issues
- Third-party library incompatibility

### Example - Opting Out

```typescript
'use no-forget';  // Opt this component out of React Compiler

const ComplexComponent: React.FC<Props> = ({ data }) => {
    // Component with unusual patterns that confuse the compiler
};
```

### ✅ With React Compiler (Most Cases)

```typescript
// No need for useMemo in most cases - compiler handles it
const filteredItems = items.filter(i => i.active);
const sortedItems = [...filteredItems].sort((a, b) => a.name.localeCompare(b.name));
```

### ⚠️ Still Use useMemo When
- Very expensive computations (100ms+)
- Explicit dependency control needed for debugging
- Complex reduce operations on large datasets

```typescript
// Still beneficial for genuinely expensive operations
const groupedItems = useMemo(() => {
    return items.reduce((acc, item) => {
        const key = item.LocationId;
        if (!acc[key]) acc[key] = [];
        acc[key].push(item);
        return acc;
    }, {} as Record<string, Item[]>);
}, [items]);
```

---

## Pattern 11: Constants & Values (Inline by Default)

**Rule:** Keep values inline. Only extract when the SAME value appears 3+ times across DIFFERENT files.

### ✅ CORRECT - Inline Values

```typescript
// Status values - inline where used
const isActive = status === 'active';
const isPending = status === 'pending';

// Styles/classes - inline in component
<div className="px-4 py-2 bg-emerald-500">

// Config - inline unless shared across files
const PAGE_SIZE = 25;
```

### ❌ WRONG - Premature Abstraction

```typescript
// ❌ Constants file for single-component values
// constants/crm-constants.ts
export const CUSTOMER_STATUS = {
    ACTIVE: 'active',
    INACTIVE: 'inactive',
};

// Usage - unnecessary indirection
if (status === CUSTOMER_STATUS.ACTIVE) { ... }
```

### When to Extract (3+ Cross-File Rule)

Extract ONLY when:
1. SAME exact value used 3+ times
2. Usages span DIFFERENT files
3. Value change would require multi-file updates

### Never Extract

- Component-local status strings
- Tailwind classes
- Single-use configuration
- Domain values used in one component

---

## Verification Checklist

### Component & Design System (Pattern 8)
- [ ] Uses `Button` component, not raw `<button>` elements
- [ ] Uses `InputSelect`, `InputText`, etc., not raw `<input>` elements
- [ ] Uses Lucide React icons, not inline `<svg>` elements
- [ ] Uses semantic CSS tokens, not inline `dark:` classes
- [ ] Buttons use correct variants (`primary`, `secondary`, `link`, `danger`, `lil`)

### Modal Components
- [ ] Self-contained (handles own form state and submission)
- [ ] Uses `useForm` hook
- [ ] Uses `useModalState` hook
- [ ] Pre-fills smart defaults in `useEffect`
- [ ] Handles `onSuccess` and `onError`
- [ ] Uses reusable input components
- [ ] Only closes modal AFTER successful submission

### Error Handling
- [ ] Uses `toast.error()` not `alert()`
- [ ] Typed toast methods (`toast.error`, `toast.success`, etc.)
- [ ] Client-side validation before submit
- [ ] Server errors displayed to user

### Data Flow
- [ ] Verified data source in `HandleInertiaRequests`
- [ ] No assumptions about `window` globals
- [ ] Correct access methods (`.some()` not `.includes()` for object arrays)
- [ ] Proper TypeScript types

### Deferred Props (Heavy Data Pages)
- [ ] Heavy data uses `Inertia::defer()` in controller
- [ ] Component types mark deferred props as optional (`?`)
- [ ] Loading check uses `!props.deferred_data` pattern
- [ ] `TableSkeleton` used for loading state
- [ ] Silent saves use `axios.post()` not `router.post()`

### React 19 Patterns
- [ ] Form submissions use `useTransition` for responsiveness
- [ ] Button combines `isPending || mutation.isPending`
- [ ] No manual `useState` for loading (use useTransition)
- [ ] React Compiler handles memoization (minimal useMemo needed)

### Performance
- [ ] Uses `useMemo` only for expensive computations (100ms+)
- [ ] Uses `useCallback` for functions passed to children (when needed)
- [ ] No unnecessary re-renders
- [ ] React Compiler handles most memoization automatically

### Constants & Values
- [ ] Values inline in components (default)
- [ ] No constants files for component-local values
- [ ] Only extracted if 3+ usages across different files

---

## Common Violations

### Violation 1: Using alert()

```typescript
// ❌ WRONG
alert('Please select an item');

// ✅ FIX
toast.error('Please select an item');
```

### Violation 1b: Inline dark: classes

```typescript
// ❌ WRONG
<div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800">

// ✅ FIX - Use semantic tokens
<div className="info-box">
```

### Violation 1c: Inline SVG instead of Lucide

```typescript
// ❌ WRONG
<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
    <path d="M8.257 3.099c..." />
</svg>

// ✅ FIX
import { AlertTriangle } from 'lucide-react';
<AlertTriangle className="w-4 h-4" />
```

### Violation 1d: Raw button instead of Button component

```typescript
// ❌ WRONG
<button onClick={handleClick} className="text-red-600 hover:text-red-800">Cancel</button>

// ✅ FIX
<Button link danger onClick={handleClick}>Cancel</Button>
```

### Violation 2: Parent-Managed Modal

```typescript
// ❌ WRONG
<MyModal onSubmit={handleSubmit} />

// ✅ FIX - Modal handles its own submission
<MyModal isOpen={open} onClose={() => setOpen(false)} items={items} />
```

### Violation 3: Multiple useState for Form

```typescript
// ❌ WRONG
const [name, setName] = useState('');
const [qty, setQty] = useState(0);

// ✅ FIX
const { data, setData } = useForm({ name: '', qty: 0 });
```

### Violation 4: No Data Flow Verification

```typescript
// ❌ WRONG - Assumes data exists
{window.Something.feature && <Button />}

// ✅ FIX - Verify in HandleInertiaRequests first
const { user } = usePage<PageProps>().props;
{user?.active_org?.features?.some(f => f.name === 'feature') && <Button />}
```

---

## Related Patterns

- **frontend-typescript.md** - Type safety requirements
- **frontend-data-fetching.md** - React Query vs Inertia
- **backend-flash-messages.md** - Flash message handling
- `.claude/docs/frontend/components.md` - Complete component patterns
- `.claude/docs/frontend/structure.md` - Inertia integration
