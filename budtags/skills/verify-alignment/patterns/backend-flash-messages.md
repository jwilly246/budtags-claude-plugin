# Flash Message Patterns

**Source:** `.claude/docs/frontend/structure.md`, `.claude/CLAUDE.md`
**Last Updated:** 2025-11-14
**Pattern Count:** Critical user feedback patterns

---

## Overview

Flash messages are a **frequent source of bugs and anti-patterns** in BudTags. Most violations stem from not knowing that `MainLayout` **automatically handles** `session.message`.

**Key Principle:** Use `->with('message')` on backend, let `MainLayout` handle display. NO manual frontend flash handling for simple messages.

---

## Backend Pattern: Simple Messages (99% of cases)

**Rule:** Use `->with('message', $text)` for success. `MainLayout` handles display automatically.

### ✅ CORRECT

```php
// Success messages
return redirect()->back()->with('message', 'Credit memo created successfully!');
return redirect()->back()->with('message', 'Inventory updated');
return redirect()->back()->with('message', "{$synced} items synced successfully");

// Error messages
return redirect()->back()->with('error', 'Failed to sync: ' . $e->getMessage());
return redirect()->back()->with('error', 'Invalid data provided');
```

### ❌ WRONG

```php
// ❌ Wrong key - MainLayout doesn't handle 'success'
return redirect()->back()->with('success', 'Credit memo created');

// ❌ Array syntax for simple message
return redirect()->back()->with(['success' => 'Item created']);
return redirect()->back()->with(['message' => 'Item created']);  // Unnecessary array

// ❌ Custom keys without TypeScript types
return redirect()->back()->with('flash_success', 'Done');  // Frontend won't show this!
```

---

## Frontend Pattern: Simple Messages (NO manual handling!)

**Rule:** `MainLayout` auto-handles `session.message`. `onSuccess` is ONLY for component state.

### ✅ CORRECT

```typescript
// MainLayout handles flash message automatically - NO manual code needed
router.post('/api/save-mappings', data, {
    preserveScroll: true,
    onSuccess: () => {
        onClose();  // Component state only
        queryClient.invalidateQueries(['mappings']);
    },
    onError: (errors) => {
        toast.error('Validation failed');  // Client-side feedback
    }
});
```

### ❌ WRONG

```typescript
// ❌ Redundant! MainLayout already handles session.message
router.post('/api/endpoint', data, {
    onSuccess: (page) => {
        const flashSuccess = (page.props as any).flash?.success;
        if (flashSuccess) {
            toast.success(flashSuccess);  // Redundant!
        }
        onClose();
    }
});

// ❌ Using 'as any' to access flash
const flashSuccess = (page.props as any).flash?.success;
if (flashSuccess) toast.success(flashSuccess);
```

---

## How MainLayout Works

`MainLayout.tsx` automatically displays flash messages:

```typescript
// MainLayout.tsx - Automatically handles session.message
useEffect(() => {
    if (session.message?.length ?? 0 > 0) {
        toast.success(session.message);  // Green toast
    }
    if (session.error?.length ?? 0 > 0) {
        toast.error(session.error);  // Red toast
    }
}, [session.message, session.error]);
```

**Shared via HandleInertiaRequests:**

```php
// app/Http/Middleware/HandleInertiaRequests.php
public function share(Request $request): array
{
    return [
        ...parent::share($request),
        'session' => [
            'message' => session('message'),  // Auto-handled by MainLayout
            'error' => session('error'),      // Auto-handled by MainLayout
            // ...
        ],
    ];
}
```

---

## Backend Pattern: Complex Data (rare, requires custom handling)

**Rule:** Use custom flash keys ONLY for complex data structures (arrays of objects). MUST have TypeScript types.

### ✅ CORRECT - Complex Flash Data

```php
// Backend: Complex data requires custom keys
public function create_packages_from_packages() {
    // ... processing logic ...

    return redirect()->back()
        ->with('recipe_deductions', $deduction_results)  // Array of objects
        ->with('recipe_warnings', $warnings)             // Array of strings
        ->with('recipe_failures', $failures);
}
```

**Required TypeScript types:**

```typescript
// resources/js/Types/index.d.ts
export interface PageProps {
    // ... other props
    flash?: {
        recipe_deductions?: RecipeDeductionResult[];
        recipe_warnings?: string[];
        recipe_failures?: RecipeFailure[];
    };
}
```

---

## Frontend Pattern: Complex Data (manual handling required)

**Rule:** Complex flash data requires manual handling in `onSuccess`. Use proper TypeScript types.

### ✅ CORRECT - Complex Flash Handling

```typescript
import { PageProps } from '@/Types';

onSuccess: (page) => {
    const { flash } = (page.props as PageProps);

    // Custom handling for complex data
    if (flash?.recipe_deductions && flash.recipe_deductions.length > 0) {
        const total = flash.recipe_deductions.reduce((sum, d) =>
            sum + d.deductions.length, 0
        );
        toast.success(`${total} packaging materials deducted`);
    }

    // Display warnings
    flash?.recipe_warnings?.forEach((warning) => {
        toast.warning(warning);
    });

    // Complex failure handling with retry option
    if (flash?.recipe_failures && flash.recipe_failures.length > 0) {
        toast.error(
            <div>
                <div>Failed to deduct {flash.recipe_failures.length} recipes</div>
                <button onClick={() => retryDeduction(flash.recipe_failures)}>
                    Retry
                </button>
            </div>,
            { autoClose: false }
        );
    }

    onClose();
}
```

---

## Manual Toast Pattern (immediate client-side feedback)

**Rule:** Manual `toast` is ONLY for immediate client-side feedback BEFORE API call.

### ✅ CORRECT - Immediate Feedback

```typescript
// Manual toast for immediate feedback (no backend flash)
const handleAction = () => {
    toast.success('Processing...');  // Immediate feedback
    router.post('/api/endpoint', data);
};

// Validation feedback (client-side, before submit)
const handleSubmit = () => {
    if (!selectedItems.length) {
        toast.error('Please select at least one item');  // ✅ Client-side validation
        return;
    }
    router.post('/api/submit', data);
};
```

### ❌ WRONG - Manual Toast After API Call

```typescript
// ❌ Don't manually toast backend success message
router.post('/api/endpoint', data, {
    onSuccess: () => {
        toast.success('Item created');  // ❌ Use backend flash instead!
    }
});

// ✅ FIX - Let backend send flash message
// Backend: return redirect()->back()->with('message', 'Item created');
// Frontend: onSuccess: () => { onClose(); }  // MainLayout shows toast
```

---

## Real-World Examples

### Example 1: QuickBooks Controller (Simple Messages)

```php
// app/Http/Controllers/QuickBooksController.php

public function save_item_mappings() {
    // ... logic ...
    return redirect()->back()->with('message', 'Item mappings saved successfully!');
}

public function sync_quantities() {
    // ... logic ...
    return redirect()->back()->with('message', "{$synced} items synced successfully");
}

public function create_invoice() {
    // ... logic ...
    return redirect()->back()->with('message', 'Invoice created successfully!');
}
```

**Frontend - NO manual flash handling needed:**

```typescript
// SyncQuantitiesModal.tsx
router.post('/quickbooks/sync-quantities', data, {
    onSuccess: () => {
        queryClient.invalidateQueries(['qbo-items']);
        onClose();  // MainLayout shows "items synced" toast
    }
});
```

---

### Example 2: Metrc Controller (Complex Data)

```php
// app/Http/Controllers/MetrcController.php

public function create_packages_from_packages() {
    // ... complex recipe deduction logic ...

    return redirect()->back()
        ->with('recipe_deductions', $deduction_results)
        ->with('recipe_warnings', $warnings)
        ->with('recipe_failures', $failures);
}
```

**Frontend - Manual handling for complex data:**

```typescript
// CreatePackageFromPackagesModal.tsx
onSuccess: (page) => {
    const { flash } = (page.props as PageProps);

    if (flash?.recipe_deductions) {
        // Custom display for complex data
        toast.success(`Deducted ${flash.recipe_deductions.length} recipes`);
    }

    flash?.recipe_warnings?.forEach(warning => toast.warning(warning));

    onClose();
}
```

---

## Automated Verification

### Backend Anti-Pattern Scan

```bash
# Check for wrong flash key usage (should be 'message' not 'success')
grep -r "->with('success'" app/Http/Controllers --include="*.php"

# Check for array-based flash (anti-pattern)
grep -r "->with(\['success'" app/Http/Controllers --include="*.php"

# Check for custom flash keys that may need TypeScript types
grep -r "->with(\[" app/Http/Controllers --include="*.php" | grep -v "->withErrors"

# Verify correct pattern usage
grep -r "->with('message'" app/Http/Controllers --include="*.php"
```

### Frontend Anti-Pattern Scan

```bash
# Check for manual flash.success access (MainLayout handles it)
grep -r "flash\?\.success" resources/js --include="*.tsx"

# Check for manual flash access (complex data requires types)
grep -r "page\.props.*flash\?" resources/js --include="*.tsx"

# Check for redundant toast in onSuccess
grep -r "onSuccess.*toast\.success" resources/js --include="*.tsx" -A 5

# Check for custom flash key access without proper types
grep -r "(page\.props as any)\.flash" resources/js --include="*.tsx"
```

---

## Verification Checklist

### Backend Flash Messages
- [ ] Uses `->with('message')` not `->with('success')`
- [ ] No array syntax for simple messages
- [ ] Custom flash keys ONLY for complex data structures
- [ ] Error messages use `->with('error')`

### Frontend Flash Handling
- [ ] `onSuccess` only handles component state (close modal, reset form, invalidate queries)
- [ ] NO manual flash access: `(page.props as any).flash?.success`
- [ ] NO redundant `toast.success()` in onSuccess for simple messages
- [ ] Manual `toast.error()` in onError for validation feedback
- [ ] Proper TypeScript types for complex flash data (no `as any` without TODO)

### TypeScript Requirements
- [ ] All custom flash keys have TypeScript types defined in `PageProps`
- [ ] Use proper type assertions: `(page.props as PageProps).flash?.key`
- [ ] NO `(page.props as any).flash` without TODO comment explaining why

---

## Compliance Thresholds

| Status | Backend Violations | Frontend Violations | Action |
|--------|-------------------|---------------------|--------|
| ✅ **EXCELLENT** | 0 `->with('success'` | 0 `flash?.success` | None needed |
| ⚠️ **ACCEPTABLE** | 1-2 violations | 1-2 violations | Add TODO to fix |
| ❌ **CRITICAL** | >2 violations | >2 violations | **Immediate fix required** |

---

## Common Violations

### Violation 1: Wrong Flash Key

```php
// ❌ WRONG - MainLayout doesn't handle 'success'
return redirect()->back()->with('success', 'Item created');

// ✅ FIX
return redirect()->back()->with('message', 'Item created');
```

### Violation 2: Manual Frontend Flash Handling

```typescript
// ❌ WRONG - Redundant with MainLayout
onSuccess: (page) => {
    const flashSuccess = (page.props as any).flash?.success;
    if (flashSuccess) toast.success(flashSuccess);
}

// ✅ FIX - Let MainLayout handle it
onSuccess: () => {
    onClose();  // That's it!
}
```

### Violation 3: Using `as any` for Flash

```typescript
// ❌ WRONG - No type safety
const flash = (page.props as any).flash;

// ✅ FIX - Use PageProps
import { PageProps } from '@/Types';
const { flash } = (page.props as PageProps);
```

### Violation 4: Manual Toast for Backend Message

```typescript
// ❌ WRONG - Manual toast for server success
onSuccess: () => {
    toast.success('Item created');  // Should come from backend!
}

// ✅ FIX
// Backend: ->with('message', 'Item created')
// Frontend: onSuccess: () => { onClose(); }
```

---

## Impact of Violations

| Violation | Impact | Severity |
|-----------|--------|----------|
| Wrong flash key | User sees no feedback | **HIGH** |
| Manual flash handling | Redundant code, confusing patterns | **MEDIUM** |
| Missing TypeScript types | Runtime errors, type unsafety | **MEDIUM** |
| Using `as any` | Loss of type checking | **LOW** |

---

## Related Patterns

- **frontend-critical.md** - Component patterns, modal handling
- **frontend-typescript.md** - Type safety requirements
- **backend-critical.md** - Security, logging
- **backend-style.md** - Redirect patterns
- `.claude/docs/frontend/components.md` - Toast notification usage
