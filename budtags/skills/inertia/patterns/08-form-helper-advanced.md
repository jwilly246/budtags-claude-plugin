# Pattern 8: Advanced Form Patterns

## Data Transformation

Transform data before submission using `transform()`:

```tsx
const { data, setData, transform, post } = useForm({
  remember: false,
  date: new Date(),
});

function handleSubmit(e: React.FormEvent) {
  e.preventDefault();

  transform((data) => ({
    ...data,
    remember: data.remember ? 'on' : '',
    date: data.date.toISOString().split('T')[0], // Format date
  }));

  post('/login');
}
```

### Chained Transform

```tsx
const form = useForm({ name: '', tags: [] as string[] });

form
  .transform((data) => ({
    ...data,
    name: data.name.trim(),
    tags: data.tags.join(','),
  }))
  .post('/items');
```

---

## File Uploads

### Basic File Upload

```tsx
const { data, setData, post, progress } = useForm({
  name: '',
  avatar: null as File | null,
});

<input
  type="file"
  onChange={e => setData('avatar', e.target.files?.[0] ?? null)}
/>

{progress && (
  <div>
    <progress value={progress.percentage} max={100} />
    <span>{progress.percentage}%</span>
  </div>
)}
```

### Multiple Files

```tsx
const { data, setData, post } = useForm({
  documents: [] as File[],
});

<input
  type="file"
  multiple
  onChange={e => setData('documents', Array.from(e.target.files ?? []))}
/>
```

### Upload Progress Tracking

```tsx
post('/upload', {
  forceFormData: true, // Required for file uploads
  onProgress: (progress) => {
    console.log(`${progress.percentage}% uploaded`);
    console.log(`${progress.loaded} of ${progress.total} bytes`);
  },
  onSuccess: () => {
    toast.success('Upload complete!');
  },
});
```

### File Validation (Client-Side)

```tsx
function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
  const file = e.target.files?.[0];
  if (!file) return;

  // Validate size (5MB max)
  if (file.size > 5 * 1024 * 1024) {
    toast.error('File must be less than 5MB');
    return;
  }

  // Validate type
  if (!['image/jpeg', 'image/png'].includes(file.type)) {
    toast.error('Only JPEG and PNG files allowed');
    return;
  }

  setData('avatar', file);
}
```

---

## Form Remembering

Persist form data across page navigations using `remember`:

### Remember All Fields

```tsx
const form = useForm('CreateUser', {
  name: '',
  email: '',
  role: 'user',
});

// Form data persists when navigating away and back
// Key 'CreateUser' identifies this form in history
```

### Remember Specific Fields

```tsx
const form = useForm('Filters', {
  search: '',
  status: 'all',
  page: 1, // Don't remember this
});

// In submit
form.get('/users', {
  remember: 'search,status', // Only remember these
});
```

### Manual Remember Control

```tsx
const { data, setData } = useForm({
  search: '',
});

// Programmatically remember
function handleSearch() {
  router.get('/search', { q: data.search }, {
    preserveState: true,
    remember: 'q',
  });
}
```

---

## Defaults Management

### setDefaults()

Update what reset() resets to:

```tsx
const { data, setData, setDefaults, reset } = useForm({
  name: '',
  email: '',
});

// After loading existing data
useEffect(() => {
  if (user) {
    setData({ name: user.name, email: user.email });
    setDefaults({ name: user.name, email: user.email });
  }
}, [user]);

// Now reset() returns to loaded user data, not empty strings
```

### defaults()

Shortcut to set current data as new defaults:

```tsx
// Make current state the new baseline
form.defaults();

// Now isDirty compares against current values
```

---

## Nested Data (Dot Notation)

Inertia supports dot notation for nested data:

```tsx
const form = useForm({
  'user.name': '',
  'user.email': '',
  'address.street': '',
  'address.city': '',
});

<input
  value={data['user.name']}
  onChange={e => setData('user.name', e.target.value)}
/>

// Submits as nested object:
// {
//   user: { name: '', email: '' },
//   address: { street: '', city: '' }
// }
```

### Alternative: Object Structure

```tsx
interface FormData {
  user: {
    name: string;
    email: string;
  };
  address: {
    street: string;
    city: string;
  };
}

const form = useForm<FormData>({
  user: { name: '', email: '' },
  address: { street: '', city: '' },
});

// Update nested field
setData('user', { ...data.user, name: 'John' });
```

---

## setError() and clearErrors()

### Set Custom Errors

```tsx
const { setError, clearErrors, errors } = useForm({ email: '' });

// Client-side validation
function validate() {
  if (!data.email.includes('@')) {
    setError('email', 'Please enter a valid email');
    return false;
  }
  clearErrors('email');
  return true;
}
```

### Set Multiple Errors

```tsx
setError({
  email: 'Email is required',
  password: 'Password is too short',
});
```

### Clear on Change

```tsx
<input
  value={data.email}
  onChange={e => {
    setData('email', e.target.value);
    clearErrors('email'); // Clear error when user types
  }}
/>
```

---

## Cancel Requests

Cancel an in-flight form submission:

```tsx
const { cancel, processing } = useForm({ search: '' });

function handleCancel() {
  cancel();
}

{processing && (
  <button type="button" onClick={handleCancel}>
    Cancel
  </button>
)}
```

---

## Form Component Alternative

Instead of `useForm`, use the `<Form>` component:

```tsx
import { Form } from '@inertiajs/react';

<Form action="/users" method="post">
  {({ data, setData, errors, processing }) => (
    <>
      <input
        value={data.name}
        onChange={e => setData('name', e.target.value)}
      />
      {errors.name && <span>{errors.name}</span>}

      <button disabled={processing}>Submit</button>
    </>
  )}
</Form>
```

---

## BudTags Advanced Examples

### Form with Feature Toggles

```tsx
function FormEditOrgFeatures({ org, features }) {
  const { data, setData, post, processing } = useForm({
    features: org.features.map(p => p.name),
  });

  function handleFeatureToggle(feature: string) {
    if (data.features.includes(feature)) {
      setData('features', data.features.filter(p => p !== feature));
    } else {
      setData('features', [...data.features, feature]);
    }
  }

  const isDiff = useMemo(() => {
    if (data.features.length !== org.features.length) return true;
    return data.features.some(f => !org.features.find(p => p.name === f));
  }, [data.features, org.features]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    post(`/orgs/${org.id}/features`, { preserveScroll: true });
  }

  return (
    <form onSubmit={handleSubmit}>
      {features.map((perm) => (
        <InputCheckbox
          key={perm.name}
          label={perm.display_name ?? perm.name}
          checked={data.features.includes(perm.name)}
          onChange={() => handleFeatureToggle(perm.name)}
        />
      ))}

      {isDiff && (
        <Button primary disabled={processing}>
          {processing ? 'Updating...' : 'Update'}
        </Button>
      )}
    </form>
  );
}
```

### Form Reset on Modal Open

```tsx
function EditPackageModal({ isOpen, onClose, pkg }) {
  const { data, setData, patch, reset, processing } = useForm({
    label: '',
    weight: 0,
    location: '',
  });

  // Reset and populate when modal opens
  useEffect(() => {
    if (isOpen && pkg) {
      setData({
        label: pkg.Label,
        weight: pkg.Weight,
        location: pkg.LocationName,
      });
    }
  }, [isOpen, pkg]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    patch(`/packages/${pkg.id}`, {
      preserveScroll: true,
      onSuccess: () => {
        reset();
        onClose();
        toast.success('Package updated');
      },
    });
  };

  return (
    <Modal show={isOpen} onClose={onClose}>
      <form onSubmit={handleSubmit}>
        {/* fields */}
      </form>
    </Modal>
  );
}
```

---

## Next Steps

- **Validation Errors** → Read `15-validation-errors.md`
- **Shared Data** → Read `09-shared-data.md`
- **Events** → Read `21-events-lifecycle.md`
