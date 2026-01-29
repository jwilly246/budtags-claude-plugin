# Pattern 15: Validation Errors

## How Validation Works

Laravel validation errors are automatically passed to Inertia and available in the `errors` object.

### Server-Side

```php
public function store(Request $request)
{
    $validated = $request->validate([
        'name' => 'required|string|max:255',
        'email' => 'required|email|unique:users',
        'password' => 'required|min:8|confirmed',
    ]);

    User::create($validated);

    return redirect()->route('users.index')
        ->with('message', 'User created!');
}
```

### Client-Side

```tsx
const { data, setData, post, errors } = useForm({
  name: '',
  email: '',
  password: '',
});

// errors.name = "The name field is required."
// errors.email = "The email has already been taken."
```

---

## Displaying Errors

### Inline Errors

```tsx
<div>
  <label>Email</label>
  <input
    type="email"
    value={data.email}
    onChange={e => setData('email', e.target.value)}
    className={errors.email ? 'border-red-500' : ''}
  />
  {errors.email && (
    <p className="text-red-500 text-sm mt-1">{errors.email}</p>
  )}
</div>
```

### Reusable Input Component

```tsx
interface InputProps {
  label: string;
  name: string;
  value: string;
  error?: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

function TextInput({ label, name, value, error, onChange }: InputProps) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      <input
        name={name}
        value={value}
        onChange={onChange}
        className={`mt-1 block w-full rounded-md border ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}

// Usage
<TextInput
  label="Email"
  name="email"
  value={data.email}
  error={errors.email}
  onChange={e => setData('email', e.target.value)}
/>
```

---

## Error Summary

Display all errors at once:

```tsx
function ErrorSummary({ errors }: { errors: Record<string, string> }) {
  const errorList = Object.values(errors);

  if (errorList.length === 0) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded p-4 mb-4">
      <h3 className="text-red-800 font-medium">
        Please fix the following errors:
      </h3>
      <ul className="mt-2 list-disc list-inside text-red-700">
        {errorList.map((error, i) => (
          <li key={i}>{error}</li>
        ))}
      </ul>
    </div>
  );
}

// Usage
<form onSubmit={handleSubmit}>
  <ErrorSummary errors={errors} />
  {/* form fields */}
</form>
```

---

## Clearing Errors

### Clear on Input Change

```tsx
<input
  value={data.email}
  onChange={e => {
    setData('email', e.target.value);
    clearErrors('email');
  }}
/>
```

### Clear All Errors

```tsx
const { clearErrors } = useForm({ email: '' });

// Clear all
clearErrors();

// Clear specific
clearErrors('email');
clearErrors('email', 'password');
```

---

## hasErrors Property

Check if form has any errors:

```tsx
const { hasErrors, errors } = useForm({ email: '' });

{hasErrors && (
  <div className="text-red-600">
    Please fix the errors below
  </div>
)}
```

---

## Error Bags

Handle multiple forms on one page using error bags:

### Server-Side

```php
$request->validateWithBag('updatePassword', [
    'current_password' => 'required',
    'password' => 'required|confirmed',
]);
```

### Client-Side

```tsx
// Access specific error bag
const { errors } = usePage().props;
const updatePasswordErrors = errors.updatePassword || {};
```

---

## Nested Errors (Dot Notation)

For nested form data:

```php
$request->validate([
    'user.name' => 'required',
    'user.email' => 'required|email',
]);
```

```tsx
// Access nested errors
errors['user.name']
errors['user.email']
```

---

## Client-Side Validation

Add instant validation before server submission:

```tsx
function handleSubmit(e: React.FormEvent) {
  e.preventDefault();

  // Clear previous errors
  clearErrors();

  // Client-side validation
  if (!data.email) {
    setError('email', 'Email is required');
    return;
  }

  if (!data.email.includes('@')) {
    setError('email', 'Please enter a valid email');
    return;
  }

  // Submit if valid
  post('/users');
}
```

---

## Toast on Errors

Show toast notification for errors:

```tsx
post('/users', {
  onError: (errors) => {
    const firstError = Object.values(errors)[0];
    toast.error(firstError || 'Please fix the errors');
  },
});
```

---

## BudTags Error Handlers

### inertiaHandlers.tsx

```tsx
export function handleInertiaError(
  errors: Record<string, string>,
  defaultMessage: string
) {
  console.error('Inertia errors:', errors);

  if (errors.metrc_error) {
    // Special handling for Metrc API errors
    toast.error(errors.metrc_error, { autoClose: false });

    if (errors.metrc_details) {
      try {
        const details = JSON.parse(errors.metrc_details);
        toast.error(
          <div>
            <strong>Metrc Response:</strong>
            <pre style={{ fontSize: '11px' }}>
              {JSON.stringify(details, null, 2)}
            </pre>
          </div>,
          { autoClose: false }
        );
      } catch {
        toast.error(errors.metrc_details);
      }
    }
  } else {
    const errorMessage = Object.values(errors)[0];
    toast.error(errorMessage || defaultMessage);
  }
}

// Usage
post('/harvest-plants', {
  onError: (errors) => handleInertiaError(errors, 'Failed to harvest'),
});
```

---

## Form Validation States

```tsx
const { processing, wasSuccessful, recentlySuccessful, hasErrors } = useForm({});

<button disabled={processing || hasErrors}>
  {processing ? 'Saving...' : recentlySuccessful ? 'Saved!' : 'Save'}
</button>

{hasErrors && (
  <span className="text-red-600">Please fix errors above</span>
)}
```

---

## Next Steps

- **CSRF Protection** → Read `16-csrf-protection.md`
- **Error Handling** → Read `17-error-handling.md`
- **Forms** → Read `07-forms-useform.md`
