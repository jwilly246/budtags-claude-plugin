# Implementation Patterns Reference

Quick reference for BudTags implementation patterns. Agents should rarely need this—SHARED_CONTEXT.md has the specifics.

---

## Form Pattern (Inertia useForm)

```tsx
import { useForm } from '@inertiajs/react';

const { data, setData, post, processing, errors, reset } = useForm({
    name: '',
});

const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    post('/items', {
        onSuccess: () => { reset(); onClose(); },
    });
};
```

**Inertia useForm:** All mutations (create, update, delete)
**React Query:** Read-only fetching, polling, cached data

---

## Forbidden Stub Patterns

```php
// PHP - will cause rejection
// TODO
// FIXME
throw new \Exception('Not implemented');
public function foo() { }  // empty
```

```tsx
// TypeScript - will cause rejection
// TODO
throw new Error('Not implemented');
const foo = () => { };
any  // type
```

---

## BudTags Conventions

```php
// Org scoping
->where('organization_id', request()->user()->active_org_id)

// Logging
LogService::store('action', 'description', ['data' => $data]);

// Flash
->with('message', 'Done');

// Methods: snake_case
fetch_all(), create(), delete()
```

