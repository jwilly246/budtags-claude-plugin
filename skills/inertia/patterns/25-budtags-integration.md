# Pattern 25: BudTags Integration

## Overview

BudTags uses Inertia.js with React and Laravel. This pattern documents project-specific conventions and when to use Inertia vs React Query.

---

## Stack Configuration

### app.tsx

```tsx
import { createRoot } from 'react-dom/client';
import { createInertiaApp } from '@inertiajs/react';
import { resolvePageComponent } from 'laravel-vite-plugin/inertia-helpers';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// React Query for Metrc API data
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 min
      gcTime: 10 * 60 * 1000,         // 10 min
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

createInertiaApp({
  title: title => `${title} - Budtags`,
  resolve: name =>
    resolvePageComponent(
      `./Pages/${name}.tsx`,
      import.meta.glob('./Pages/**/*.tsx')
    ),
  setup({ el, App, props }) {
    // Persist root across HMR
    if (!(el as any)._inertiaRoot) {
      (el as any)._inertiaRoot = createRoot(el);
    }
    (el as any)._inertiaRoot.render(
      <QueryClientProvider client={queryClient}>
        <App {...props} />
        {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
      </QueryClientProvider>
    );
  },
  progress: {
    color: '#F87415',  // BudTags orange
  },
});
```

---

## HandleInertiaRequests

```php
class HandleInertiaRequests extends Middleware
{
    protected $rootView = 'app';

    public function share(Request $request): array
    {
        $user = $request->user();
        $user?->load(['active_org.features']);

        return array_merge(parent::share($request), [
            'user' => fn() => $user ?? null,
            'roles' => fn() => $user?->active_org_roles() ?? [],
            'permissions' => fn() => $user?->active_org_perms() ?? [],
            'ui_preferences' => fn() => $user?->ui_preferences ?? [],
            'latest_announcement' => fn() => Announcement::where('is_published', true)
                ->orderBy('release_date', 'desc')
                ->first(),
            'session' => [
                'licenses' => fn () => $request->session()->get('licenses'),
                'license' => fn () => $request->session()->get('license'),
                'org' => fn () => $request->session()->get('org'),
                'message' => fn () => $request->session()->get('message'),
                'facility_permissions' => fn () => $request->session()->get('facility_permissions', []),
            ],
        ]);
    }
}
```

---

## PageProps Type

```tsx
// resources/js/Types/types.tsx
export interface PageProps {
  user: User | null;
  roles: Role[];
  permissions: string[];
  ui_preferences: Record<string, any>;
  latest_announcement: Announcement | null;
  session: {
    licenses?: string[];
    license?: string;
    org?: number;
    message?: string;
    facility_permissions?: string[];
  };
}
```

---

## When to Use Inertia vs React Query

### Use Inertia useForm When:

| Scenario | Example |
|----------|---------|
| Form submissions | Creating/updating packages, harvests |
| CRUD operations | Creating users, editing orgs |
| Actions with redirect | Logout, delete with redirect |
| Laravel validation needed | Server validates and returns errors |

### Use React Query When:

| Scenario | Example |
|----------|---------|
| Metrc API fetches | Getting packages, plants, locations |
| Background polling | Refreshing Metrc data |
| Complex caching | Multiple components need same data |
| Optimistic updates | Quick status changes |

### Decision Tree

```
Is it a form submission?
├── YES → useForm
└── NO → Is it Metrc/external API data?
    ├── YES → React Query
    └── NO → Is it on page load?
        ├── YES → Inertia props
        └── NO → React Query for dynamic fetch
```

---

## inertiaHandlers Utility

```tsx
// resources/js/utils/inertiaHandlers.tsx
import { toast } from 'react-toastify';
import { Page } from '@inertiajs/core';
import { PageProps } from '@/Types/types';

export function handleInertiaSuccess(
  page: Page<PageProps>,
  onClose: () => void,
  reset?: () => void,
  successMessage?: string
) {
  if (successMessage) {
    toast.success(successMessage);
  }
  reset?.();
  onClose();
}

export function handleInertiaError(
  errors: Record<string, string>,
  defaultMessage: string
) {
  console.error('Inertia errors:', errors);

  if (errors.metrc_error) {
    toast.error(errors.metrc_error, { autoClose: false });

    if (errors.metrc_details) {
      try {
        const details = JSON.parse(errors.metrc_details);
        toast.error(
          <div>
            <strong>Metrc Response:</strong>
            <pre style={{ fontSize: '11px', marginTop: '8px' }}>
              {JSON.stringify(details, null, 2)}
            </pre>
          </div>,
          { autoClose: false }
        );
      } catch {
        toast.error(errors.metrc_details, { autoClose: false });
      }
    }
  } else {
    toast.error(Object.values(errors)[0] || defaultMessage);
  }
}
```

---

## Modal Pattern

```tsx
import { useForm } from '@inertiajs/react';
import { handleInertiaSuccess, handleInertiaError } from '@/utils/inertiaHandlers';
import Modal from '@/Components/Modal';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  selectedItems: Item[];
  clearSelection?: () => void;
}

function ActionModal({ isOpen, onClose, selectedItems, clearSelection }: Props) {
  const { data, setData, post, reset, processing } = useForm({
    items: selectedItems.map(i => i.id),
    // other form fields
  });

  // Sync when selection changes
  useEffect(() => {
    if (isOpen) {
      setData('items', selectedItems.map(i => i.id));
    }
  }, [isOpen, selectedItems]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Client-side validation
    if (data.items.length === 0) {
      toast.error('Please select at least one item');
      return;
    }

    post('/action-endpoint', {
      preserveScroll: true,
      onSuccess: (page) => {
        handleInertiaSuccess(page, onClose, reset);
        clearSelection?.();
      },
      onError: (errors) => handleInertiaError(errors, 'Action failed'),
    });
  };

  return (
    <Modal show={isOpen} onClose={onClose} title="Action Title">
      <form onSubmit={handleSubmit}>
        {/* Form fields */}

        <div className="flex justify-end gap-2 mt-4">
          <Button secondary onClick={onClose}>
            Cancel
          </Button>
          <Button primary disabled={processing}>
            {processing ? 'Processing...' : 'Submit'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
```

---

## Feature Toggles Pattern

```tsx
function FormEditOrgFeatures({ org, features, readonly }) {
  const { data, setData, post, processing } = useForm({
    features: org.features.map(f => f.name),
  });

  function handleFeatureToggle(feature: string) {
    if (readonly) return;

    if (data.features.includes(feature)) {
      setData('features', data.features.filter(f => f !== feature));
    } else {
      setData('features', [...data.features, feature]);
    }
  }

  const isDiff = useMemo(() => {
    if (data.features.length !== org.features.length) return true;
    return data.features.some(f =>
      !org.features.find(p => p.name === f)
    );
  }, [data.features, org.features]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (readonly) return;
    post(`/orgs/${org.id}/features`, { preserveScroll: true });
  }

  return (
    <form onSubmit={handleSubmit}>
      {features.map(perm => (
        <InputCheckbox
          key={perm.name}
          label={perm.display_name ?? perm.name}
          checked={data.features.includes(perm.name)}
          onChange={() => handleFeatureToggle(perm.name)}
          readOnly={readonly}
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

---

## Organization Scoping

### Access Current Org

```tsx
const { user } = usePage<PageProps>().props;
const currentOrg = user?.active_org;
const orgFeatures = currentOrg?.features ?? [];

// Check feature
const hasLabsFeature = orgFeatures.some(f => f.name === 'labs');
```

### Check Permissions

```tsx
const { permissions } = usePage<PageProps>().props;

// Simple check
const canManageUsers = permissions.includes('manage-users');

// Custom hook
function usePermissions() {
  const { permissions } = usePage<PageProps>().props;
  return {
    can: (perm: string) => permissions.includes(perm),
    canAny: (...perms: string[]) => perms.some(p => permissions.includes(p)),
    canAll: (...perms: string[]) => perms.every(p => permissions.includes(p)),
  };
}
```

---

## Flash Messages in Layout

```tsx
export default function MainLayout({ children }) {
  const { session } = usePage<PageProps>().props;
  const lastMessage = useRef<string | null>(null);

  useEffect(() => {
    if (session.message && session.message !== lastMessage.current) {
      toast.success(session.message);
      lastMessage.current = session.message;
    }
  }, [session.message]);

  return (
    <div className="min-h-screen">
      <Navbar />
      <main>{children}</main>
      <ToastContainer />
    </div>
  );
}
```

---

## License Switching

```tsx
function LicenseSelector() {
  const { session } = usePage<PageProps>().props;
  const { licenses, license: currentLicense } = session;

  const handleLicenseChange = (newLicense: string) => {
    router.post('/switch-license', { license: newLicense }, {
      preserveScroll: true,
    });
  };

  return (
    <select
      value={currentLicense || ''}
      onChange={e => handleLicenseChange(e.target.value)}
    >
      {licenses?.map(lic => (
        <option key={lic} value={lic}>{lic}</option>
      ))}
    </select>
  );
}
```

---

## Quick Reference

### Inertia Imports

```tsx
import { useForm, usePage, Link, router, Head } from '@inertiajs/react';
import { PageProps } from '@/Types/types';
```

### Common Form Pattern

```tsx
const { data, setData, post, processing, errors, reset } = useForm({
  field: '',
});

post('/endpoint', {
  preserveScroll: true,
  onSuccess: (page) => handleInertiaSuccess(page, onClose, reset),
  onError: (errors) => handleInertiaError(errors, 'Action failed'),
});
```

### Common Link Pattern

```tsx
<Link href="/path" preserveScroll preserveState>
  Navigate
</Link>
```

---

## Related Skills

- **tanstack-query** - For Metrc API and complex data fetching
- **react-19** - React 19 features and hooks
- **verify-alignment** - BudTags coding standards
