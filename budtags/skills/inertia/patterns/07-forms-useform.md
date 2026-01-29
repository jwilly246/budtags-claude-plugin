# Pattern 7: Forms with useForm

## Overview

The `useForm` hook is Inertia's primary tool for handling form state, validation, and submission:

```tsx
import { useForm } from '@inertiajs/react';

function CreateUserForm() {
  const { data, setData, post, processing, errors, reset } = useForm({
    name: '',
    email: '',
    password: '',
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    post('/users');
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={data.name}
        onChange={e => setData('name', e.target.value)}
      />
      {errors.name && <span className="error">{errors.name}</span>}

      <button disabled={processing}>
        {processing ? 'Creating...' : 'Create User'}
      </button>
    </form>
  );
}
```

---

## useForm Return Values

### data

The current form data object:

```tsx
const { data } = useForm({ name: '', email: '' });
console.log(data.name);  // ''
```

### setData

Update form data:

```tsx
const { setData } = useForm({ name: '', email: '' });

// Single field
setData('name', 'John');

// Multiple fields
setData({ name: 'John', email: 'john@example.com' });

// With callback (for derived values)
setData(prev => ({ ...prev, name: prev.name.toUpperCase() }));
```

### errors

Validation errors from server:

```tsx
const { errors } = useForm({ email: '' });
// errors.email = "The email field is required."

// Check if any errors
const hasErrors = Object.keys(errors).length > 0;
```

### hasErrors

Boolean indicating presence of errors:

```tsx
const { hasErrors } = useForm({ email: '' });
if (hasErrors) {
  console.log('Form has validation errors');
}
```

### processing

Boolean indicating submission in progress:

```tsx
const { processing } = useForm({ name: '' });

<button disabled={processing}>
  {processing ? 'Saving...' : 'Save'}
</button>
```

### progress

Upload progress object (for file uploads):

```tsx
const { progress } = useForm({ file: null });
// progress.percentage, progress.total, progress.loaded

{progress && (
  <progress value={progress.percentage} max={100} />
)}
```

### wasSuccessful

Boolean, true after successful submission:

```tsx
const { wasSuccessful } = useForm({ name: '' });

useEffect(() => {
  if (wasSuccessful) {
    toast.success('Saved!');
  }
}, [wasSuccessful]);
```

### recentlySuccessful

Boolean, stays true for 2 seconds after success:

```tsx
const { recentlySuccessful } = useForm({ name: '' });

<button disabled={processing}>
  {recentlySuccessful ? 'Saved!' : 'Save'}
</button>
```

### isDirty

Boolean, true if data differs from defaults:

```tsx
const { isDirty } = useForm({ name: '' });

// Warn on navigation if dirty
useEffect(() => {
  if (isDirty) {
    window.onbeforeunload = () => true;
    return () => { window.onbeforeunload = null; };
  }
}, [isDirty]);
```

---

## Submission Methods

### post(), put(), patch(), delete()

Submit the form with specific HTTP methods:

```tsx
const { post, put, patch, delete: destroy } = useForm({ name: '' });

// Create
post('/users');

// Update (full)
put(`/users/${id}`);

// Update (partial)
patch(`/users/${id}`);

// Delete
destroy(`/users/${id}`);
```

### get()

Submit as GET request (useful for filters):

```tsx
const { data, setData, get } = useForm({
  search: '',
  status: 'active',
});

function handleFilter() {
  get('/users', {
    preserveState: true,
    preserveScroll: true,
  });
}
```

---

## Submission Options

### preserveScroll

Keep scroll position after submission:

```tsx
post('/users', {
  preserveScroll: true,
});
```

### preserveState

Keep React state after submission:

```tsx
post('/users', {
  preserveState: true,
});
```

### onSuccess

Callback after successful submission:

```tsx
post('/users', {
  onSuccess: (page) => {
    toast.success('User created!');
    reset();
    closeModal();
  },
});
```

### onError

Callback on validation errors:

```tsx
post('/users', {
  onError: (errors) => {
    toast.error(errors.email || 'Please fix the errors');
    // errors = { email: 'Email is required', ... }
  },
});
```

### onFinish

Callback after success or error:

```tsx
post('/users', {
  onFinish: () => {
    setLoading(false);
  },
});
```

### onBefore

Callback before submission, return false to cancel:

```tsx
post('/users', {
  onBefore: () => {
    if (!data.name) {
      toast.error('Name is required');
      return false;
    }
    return true;
  },
});
```

### onProgress

Track file upload progress:

```tsx
post('/upload', {
  onProgress: (progress) => {
    setUploadProgress(progress.percentage);
  },
});
```

---

## reset() and clearErrors()

### reset()

Reset form to initial values:

```tsx
const { reset } = useForm({ name: '', email: '' });

// Reset all fields
reset();

// Reset specific fields
reset('name');
reset('name', 'email');
```

### clearErrors()

Clear validation errors:

```tsx
const { clearErrors } = useForm({ email: '' });

// Clear all errors
clearErrors();

// Clear specific field error
clearErrors('email');
clearErrors('email', 'name');
```

### Combined reset

```tsx
// After successful submission
onSuccess: () => {
  reset();
  clearErrors();
  // Or combined:
  // form.reset() also clears errors for reset fields
}
```

---

## TypeScript Usage

### Typed Form

```tsx
interface FormData {
  name: string;
  email: string;
  role: 'admin' | 'user';
}

const { data, setData, errors } = useForm<FormData>({
  name: '',
  email: '',
  role: 'user',
});

// data.name is string
// data.role is 'admin' | 'user'
// errors.name is string | undefined
```

### Complex Types

```tsx
interface CreatePackageForm {
  label: string;
  weight: number;
  item_id: number | null;
  plants: string[];
}

const form = useForm<CreatePackageForm>({
  label: '',
  weight: 0,
  item_id: null,
  plants: [],
});

// Updating array
form.setData('plants', [...form.data.plants, newPlant]);
```

---

## Common Patterns

### Input Change Handler

```tsx
function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
  setData(e.target.name as keyof typeof data, e.target.value);
}

<input
  name="email"
  value={data.email}
  onChange={handleChange}
/>
```

### Select Input

```tsx
<select
  value={data.status}
  onChange={e => setData('status', e.target.value)}
>
  <option value="active">Active</option>
  <option value="inactive">Inactive</option>
</select>
```

### Checkbox

```tsx
<input
  type="checkbox"
  checked={data.remember}
  onChange={e => setData('remember', e.target.checked)}
/>
```

### Multiple Checkboxes (Array)

```tsx
const { data, setData } = useForm({
  features: [] as string[],
});

function handleFeatureToggle(feature: string) {
  if (data.features.includes(feature)) {
    setData('features', data.features.filter(f => f !== feature));
  } else {
    setData('features', [...data.features, feature]);
  }
}

{features.map(f => (
  <input
    key={f.name}
    type="checkbox"
    checked={data.features.includes(f.name)}
    onChange={() => handleFeatureToggle(f.name)}
  />
))}
```

---

## BudTags Modal Pattern

```tsx
import { useForm } from '@inertiajs/react';
import { handleInertiaSuccess, handleInertiaError } from '@/utils/inertiaHandlers';

function HarvestPlantsModal({ isOpen, onClose, selectedPlants }) {
  const { data, setData, post, reset, processing } = useForm({
    harvest_name: '',
    harvest_weight: 0,
    drying_location: '',
    plants: selectedPlants.map(p => p.Label),
  });

  // Sync plants when selection changes
  useEffect(() => {
    setData('plants', selectedPlants.map(p => p.Label));
  }, [selectedPlants]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Client-side validation
    if (!data.harvest_name.trim()) {
      toast.error('Please enter a harvest name');
      return;
    }

    post('/harvest-plants', {
      preserveScroll: true,
      onSuccess: (page) => handleInertiaSuccess(page, onClose, reset),
      onError: (errors) => handleInertiaError(errors, 'Failed to harvest'),
    });
  };

  return (
    <Modal show={isOpen} onClose={onClose}>
      <form onSubmit={handleSubmit}>
        <InputText
          label="Harvest Name"
          value={data.harvest_name}
          onChange={e => setData('harvest_name', e.target.value)}
          required
        />

        <InputNumber
          label="Weight"
          value={data.harvest_weight}
          onChange={e => setData('harvest_weight', parseFloat(e.target.value))}
        />

        <div className="flex justify-end gap-2">
          <Button secondary onClick={onClose}>Cancel</Button>
          <Button primary disabled={processing}>
            {processing ? 'Harvesting...' : 'Harvest Plants'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
```

---

## Next Steps

- **Advanced Forms** → Read `08-form-helper-advanced.md`
- **Validation Errors** → Read `15-validation-errors.md`
- **File Uploads** → See `08-form-helper-advanced.md`
