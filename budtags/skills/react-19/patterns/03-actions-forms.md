# React 19 Actions & Forms

React 19 introduces native support for async functions in form handling with automatic state management.

## Form Action Prop

Forms can now accept functions as the `action` prop:

```typescript
<form action={async (formData) => {
  await saveData(formData);
}}>
  <input name="email" />
  <button type="submit">Submit</button>
</form>
```

## Key Features

### Automatic Pending State

```typescript
function ContactForm() {
  const [error, submitAction, isPending] = useActionState(
    async (prev, formData) => {
      const result = await sendMessage(formData);
      if (result.error) return result.error;
      return null;
    },
    null
  );

  return (
    <form action={submitAction}>
      <input name="message" disabled={isPending} />
      <button disabled={isPending}>
        {isPending ? 'Sending...' : 'Send'}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
```

### Automatic Form Reset

For **uncontrolled components**, React automatically resets the form on successful submission:

```typescript
// Form resets automatically after successful action
<form action={async (formData) => {
  await saveData(formData);
  // Form inputs are cleared automatically!
}}>
  <input name="name" /> {/* Uncontrolled - will reset */}
  <button>Submit</button>
</form>
```

**Note:** Controlled components (with `value` prop) don't auto-reset.

### Sequential Request Handling

When multiple submissions happen quickly, React handles them sequentially:

```typescript
// If user clicks submit 3 times rapidly:
// - Only the LAST submission's result is used
// - Previous pending requests are not cancelled (they complete)
// - UI shows result of final submission
```

---

## formAction on Buttons

Individual buttons can have their own actions:

```typescript
<form>
  <input name="item" />

  {/* Different actions per button */}
  <button formAction={saveAsDraft}>Save Draft</button>
  <button formAction={publish}>Publish</button>
  <button formAction={deleteItem}>Delete</button>
</form>
```

### Example: Multi-Action Form

```typescript
function ItemForm({ item }) {
  const saveDraft = async (formData) => {
    await api.saveDraft(item.id, formData);
    toast.success('Draft saved');
  };

  const publish = async (formData) => {
    await api.publish(item.id, formData);
    toast.success('Published!');
    redirect('/items');
  };

  return (
    <form>
      <input name="title" defaultValue={item.title} />
      <textarea name="content" defaultValue={item.content} />

      <div className="flex gap-2">
        <button formAction={saveDraft} className="btn-secondary">
          Save Draft
        </button>
        <button formAction={publish} className="btn-primary">
          Publish
        </button>
      </div>
    </form>
  );
}
```

---

## BudTags Comparison: Actions vs Inertia Forms

### When to Use React 19 Actions

```typescript
// ✅ Good for: Custom async operations, non-navigation forms
const [error, submitAction, isPending] = useActionState(
  async (prev, formData) => {
    // Direct API call, no page navigation
    const response = await axios.post('/api/quick-action', {
      packageId: formData.get('packageId'),
    });
    if (!response.data.success) return response.data.error;
    return null;
  },
  null
);
```

### When to Use Inertia useForm

```typescript
// ✅ Good for: Page navigation, Inertia router integration
const { data, setData, post, processing, errors } = useForm({
  name: '',
  email: '',
});

const handleSubmit = (e) => {
  e.preventDefault();
  post('/users', {
    onSuccess: () => {
      // Inertia handles page update automatically
    },
  });
};
```

### Comparison Table

| Feature | React 19 Actions | Inertia useForm |
|---------|------------------|-----------------|
| Page navigation | Manual | Automatic |
| Pending state | `isPending` | `processing` |
| Error handling | Return from action | `errors` object |
| Form reset | Automatic (uncontrolled) | Manual |
| Flash messages | Manual | Via Laravel |
| SPA experience | Custom | Built-in |

---

## useTransition with Actions

For non-form async operations, use `useTransition`:

```typescript
import { useTransition } from 'react';

function UpdateButton({ onUpdate }) {
  const [isPending, startTransition] = useTransition();

  const handleClick = () => {
    startTransition(async () => {
      await onUpdate();
    });
  };

  return (
    <button onClick={handleClick} disabled={isPending}>
      {isPending ? 'Updating...' : 'Update'}
    </button>
  );
}
```

### BudTags Example: Quick Action Button

```typescript
function QuickFinishButton({ packageId, onFinished }) {
  const [isPending, startTransition] = useTransition();

  const handleFinish = () => {
    startTransition(async () => {
      await axios.post(`/api/packages/${packageId}/finish`);
      onFinished();
      toast.success('Package finished');
    });
  };

  return (
    <button
      onClick={handleFinish}
      disabled={isPending}
      className="btn btn-sm btn-success"
    >
      {isPending ? (
        <span className="loading loading-spinner loading-xs" />
      ) : (
        'Finish'
      )}
    </button>
  );
}
```

---

## Error Boundaries with Actions

Actions integrate with Error Boundaries:

```typescript
<ErrorBoundary fallback={<FormErrorFallback />}>
  <form action={async (formData) => {
    // If this throws, Error Boundary catches it
    await riskyOperation(formData);
  }}>
    <input name="data" />
    <button>Submit</button>
  </form>
</ErrorBoundary>
```

For more control, handle errors in the action:

```typescript
const [error, submitAction, isPending] = useActionState(
  async (prev, formData) => {
    try {
      await riskyOperation(formData);
      return null;
    } catch (e) {
      return e.message; // Return error to state instead of throwing
    }
  },
  null
);
```

---

## Best Practices

### 1. Use Uncontrolled Inputs for Auto-Reset

```typescript
// ✅ Form resets automatically
<form action={submitAction}>
  <input name="message" defaultValue="" />
</form>

// ❌ Form doesn't reset (controlled)
<form action={submitAction}>
  <input name="message" value={message} onChange={e => setMessage(e.target.value)} />
</form>
```

### 2. Combine with useOptimistic

```typescript
const [optimisticItems, addOptimistic] = useOptimistic(items);

const addItem = async (formData) => {
  const newItem = { id: Date.now(), name: formData.get('name') };
  addOptimistic([...items, newItem]); // Show immediately
  await api.addItem(newItem); // Then save
};
```

### 3. Show Loading in Submit Button

```typescript
function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button disabled={pending}>
      {pending ? 'Saving...' : 'Save'}
    </button>
  );
}
```

## Next Steps

- Read `02-new-hooks.md` for hook details
- Read `04-use-api.md` for the `use()` API
- Read `05-ref-changes.md` for ref updates
