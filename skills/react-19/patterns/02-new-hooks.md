# React 19 New Hooks

New hooks introduced in React 19 for handling async operations, forms, and optimistic updates.

## useActionState

Handles async functions with automatic pending state and error handling.

**Renamed from:** `ReactDOM.useFormState` (deprecated)

### Signature

```typescript
const [state, formAction, isPending] = useActionState(
  fn: (prevState: State, formData: FormData) => Promise<State>,
  initialState: State,
  permalink?: string
);
```

### Basic Usage

```typescript
import { useActionState } from 'react';

function UpdateNameForm() {
  const [error, submitAction, isPending] = useActionState(
    async (previousState, formData) => {
      const name = formData.get('name') as string;
      const error = await updateName(name);
      if (error) {
        return error; // Return error to state
      }
      redirect('/success');
      return null;
    },
    null // Initial state (no error)
  );

  return (
    <form action={submitAction}>
      <input type="text" name="name" />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Updating...' : 'Update'}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
```

### BudTags Comparison: useActionState vs Inertia useForm

```typescript
// Inertia useForm - for Inertia router submissions
const { data, setData, post, processing, errors } = useForm({
  name: '',
});

const handleSubmit = (e) => {
  e.preventDefault();
  post('/api/update-name');
};

// React 19 useActionState - for custom async actions
const [error, submitAction, isPending] = useActionState(
  async (prev, formData) => {
    const response = await fetch('/api/custom', {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) return 'Failed';
    return null;
  },
  null
);
```

**When to use which:**
- **Inertia useForm:** Standard form submissions, page navigations
- **useActionState:** Custom async actions, non-Inertia endpoints

---

## useOptimistic

Show optimistic UI updates while async operations are in progress.

### Signature

```typescript
const [optimisticState, addOptimistic] = useOptimistic(
  state: State,
  updateFn?: (currentState: State, optimisticValue: Value) => State
);
```

### Basic Usage

```typescript
import { useOptimistic } from 'react';

function LikeButton({ likes, onLike }) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    likes,
    (currentLikes, increment) => currentLikes + increment
  );

  const handleLike = async () => {
    addOptimisticLike(1); // Immediately show +1
    await onLike(); // Then actually send request
  };

  return (
    <button onClick={handleLike}>
      ❤️ {optimisticLikes}
    </button>
  );
}
```

### BudTags Example: Optimistic Package Finish

```typescript
function FinishPackageButton({ pkg, onFinish }) {
  const [optimisticStatus, setOptimisticStatus] = useOptimistic(
    pkg.FinishedDate,
    (current, newDate) => newDate
  );

  const handleFinish = async () => {
    const now = new Date().toISOString();
    setOptimisticStatus(now); // Show finished immediately

    try {
      await onFinish(pkg.Id);
    } catch (error) {
      // State automatically reverts on error
      toast.error('Failed to finish package');
    }
  };

  const isFinished = !!optimisticStatus;

  return (
    <button
      onClick={handleFinish}
      disabled={isFinished}
      className={isFinished ? 'text-green-500' : ''}
    >
      {isFinished ? '✓ Finished' : 'Finish Package'}
    </button>
  );
}
```

### With useActionState

```typescript
function ChangeName({ currentName, onUpdateName }) {
  const [optimisticName, setOptimisticName] = useOptimistic(currentName);

  const [error, submitAction, isPending] = useActionState(
    async (prev, formData) => {
      const newName = formData.get('name') as string;
      setOptimisticName(newName); // Optimistic update

      const error = await onUpdateName(newName);
      if (error) return error;
      return null;
    },
    null
  );

  return (
    <form action={submitAction}>
      <p>Your name is: {optimisticName}</p>
      <input
        type="text"
        name="name"
        disabled={currentName !== optimisticName}
      />
      <button type="submit">Update</button>
      {error && <p>{error}</p>}
    </form>
  );
}
```

---

## useFormStatus

Access the status of a parent `<form>` without prop drilling.

### Signature

```typescript
const { pending, data, method, action } = useFormStatus();
```

**Must be used inside a component rendered within a `<form>`**

### Basic Usage

```typescript
import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  );
}

function MyForm() {
  return (
    <form action={submitAction}>
      <input name="email" />
      <SubmitButton /> {/* Has access to form status */}
    </form>
  );
}
```

### BudTags Example: Reusable Submit Button

```typescript
// components/FormSubmitButton.tsx
import { useFormStatus } from 'react-dom';

interface Props {
  children?: React.ReactNode;
  loadingText?: string;
  className?: string;
}

export function FormSubmitButton({
  children = 'Submit',
  loadingText = 'Submitting...',
  className = ''
}: Props) {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className={`btn btn-primary ${className} ${pending ? 'opacity-50' : ''}`}
    >
      {pending ? (
        <>
          <span className="loading loading-spinner loading-sm mr-2" />
          {loadingText}
        </>
      ) : children}
    </button>
  );
}

// Usage
<form action={submitAction}>
  <input name="name" />
  <FormSubmitButton loadingText="Saving...">
    Save Changes
  </FormSubmitButton>
</form>
```

### Full Form Status Object

```typescript
function FormDebug() {
  const status = useFormStatus();

  // status = {
  //   pending: boolean,      // Is form submitting?
  //   data: FormData | null, // Form data being submitted
  //   method: string,        // HTTP method
  //   action: string | fn,   // Form action
  // }

  return (
    <pre>{JSON.stringify(status, null, 2)}</pre>
  );
}
```

---

## Hooks Summary

| Hook | Purpose | Returns |
|------|---------|---------|
| `useActionState` | Handle async form actions | `[state, action, isPending]` |
| `useOptimistic` | Optimistic UI updates | `[optimisticState, setOptimistic]` |
| `useFormStatus` | Parent form status | `{ pending, data, method, action }` |

## Next Steps

- Read `03-actions-forms.md` for form action patterns
- Read `04-use-api.md` for the `use()` API
- Read `12-use-effect-event.md` for useEffectEvent (React 19.2)
