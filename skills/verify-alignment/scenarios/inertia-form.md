# Scenario: Inertia Form Submission

**Use this checklist when verifying Inertia form submissions (MOST common pattern).**

---

## Required Pattern Files

- `patterns/backend-flash-messages.md` - **CRITICAL**
- `patterns/frontend-critical.md` - Form patterns
- `patterns/backend-critical.md` - Org scoping

---

## Backend Verification Checklist

### Flash Messages (CRITICAL)
- [ ] Returns `->with('message', $text)` for success (NOT `->with('success')`)
- [ ] Returns `->with('error', $text)` for errors
- [ ] NO array syntax for simple messages (e.g., `->with(['success' => ...])`)
- [ ] Custom flash keys ONLY for complex data structures (arrays of objects)

### Standard Patterns
- [ ] Uses `request()->validate()` for validation
- [ ] Creates models with `organization_id`
- [ ] Uses `LogService::store()` for logging
- [ ] Redirects with `redirect()->back()`

---

## Frontend Verification Checklist

### Form State
- [ ] Uses Inertia's `useForm` hook
- [ ] NO React Query mutations (use Inertia for forms!)
- [ ] Form data structure matches backend expectations

### Success Handling (CRITICAL)
- [ ] `onSuccess` only handles component state (close modal, reset form, invalidate queries)
- [ ] **NO manual flash access**: `(page.props as any).flash?.success`
- [ ] **NO redundant `toast.success()`** in onSuccess (MainLayout handles it!)
- [ ] Only closes modal/resets form in onSuccess

### Error Handling
- [ ] `onError` callback handles validation errors
- [ ] Uses `toast.error()` for user feedback
- [ ] Displays specific error messages from backend
- [ ] NO `alert()` usage

### TypeScript
- [ ] Uses proper types (NO `as any` without TODO)
- [ ] Complex flash data has TypeScript types in `PageProps`

---

## Common Violations

### Backend: Wrong Flash Key
```php
// ❌ WRONG - MainLayout doesn't handle 'success'
return redirect()->back()->with('success', 'Item created');

// ✅ FIX
return redirect()->back()->with('message', 'Item created');
```

### Frontend: Manual Flash Handling
```typescript
// ❌ WRONG - Redundant! MainLayout already handles this
router.post('/api/endpoint', data, {
    onSuccess: (page) => {
        const flashSuccess = (page.props as any).flash?.success;
        if (flashSuccess) {
            toast.success(flashSuccess);  // Redundant!
        }
        onClose();
    }
});

// ✅ FIX - Let MainLayout handle flash message
router.post('/api/endpoint', data, {
    onSuccess: () => {
        onClose();  // That's it! MainLayout shows toast automatically
    },
    onError: (errors) => {
        toast.error('Validation failed');
    }
});
```

### Frontend: Using React Query for Form
```typescript
// ❌ WRONG - Use Inertia for forms!
const mutation = useMutation({
    mutationFn: (data) => axios.post('/api/create', data)
});

// ✅ FIX
const { data, setData, post } = useForm({ name: '', quantity: 0 });
post('/api/create');
```

---

## Example: Compliant Pattern

### Backend

```php
public function create() {
    $values = request()->validate([
        'name' => 'string|required',
        'quantity' => 'integer|required',
    ]);

    $item = Item::create([
        ...$values,
        'organization_id' => request()->user()->active_org_id,
    ]);

    LogService::store('Item Created', "Created item {$item->name}", $item);

    return redirect()->back()->with('message', 'Item created successfully');
}
```

### Frontend

```typescript
const { data, setData, post, processing, errors } = useForm({
    name: '',
    quantity: 0,
});

const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    post('/api/items/create', {
        preserveScroll: true,
        onSuccess: () => {
            onClose();  // MainLayout handles "Item created successfully" toast
            queryClient.invalidateQueries(['items']);
        },
        onError: (errors) => {
            const message = Object.values(errors)[0] as string;
            toast.error(message || 'Validation failed');
        }
    });
};
```

---

## Priority

**CRITICAL** (Must fix):
- Wrong flash key (`->with('success')` instead of `->with('message')`)
- Manual flash handling in frontend
- Using React Query instead of Inertia for forms

**HIGH**:
- Missing error handling
- Using `as any` without TODO
- No validation feedback to user
