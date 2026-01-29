# Pattern 4: Page Components

## Basic Page Component

Page components receive props from the controller:

```tsx
// resources/js/Pages/Users/Index.tsx
interface Props {
  users: User[];
  filters: {
    search?: string;
    status?: string;
  };
}

export default function Index({ users, filters }: Props) {
  return (
    <div>
      <h1>Users</h1>
      <SearchForm initialFilters={filters} />
      <UsersList users={users} />
    </div>
  );
}
```

## File Naming Convention

Components are resolved from `resources/js/Pages/`:

| Inertia::render() | File Path |
|-------------------|-----------|
| `'Dashboard'` | `Pages/Dashboard.tsx` |
| `'Users/Index'` | `Pages/Users/Index.tsx` |
| `'Org/Settings/Profile'` | `Pages/Org/Settings/Profile.tsx` |

---

## Layouts

### Per-Page Layout

```tsx
import MainLayout from '@/Layouts/MainLayout';

export default function Dashboard({ user }) {
  return (
    <MainLayout>
      <h1>Dashboard</h1>
      <p>Welcome, {user.name}</p>
    </MainLayout>
  );
}
```

### Persistent Layouts

Layouts that persist across page navigations (no remount):

```tsx
import MainLayout from '@/Layouts/MainLayout';

function Dashboard({ user }) {
  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome, {user.name}</p>
    </div>
  );
}

// Define persistent layout
Dashboard.layout = (page: React.ReactNode) => <MainLayout>{page}</MainLayout>;

export default Dashboard;
```

### Nested Layouts

```tsx
import MainLayout from '@/Layouts/MainLayout';
import SettingsLayout from '@/Layouts/SettingsLayout';

function ProfileSettings({ user }) {
  return <div>Profile settings content</div>;
}

ProfileSettings.layout = (page: React.ReactNode) => (
  <MainLayout>
    <SettingsLayout>{page}</SettingsLayout>
  </MainLayout>
);

export default ProfileSettings;
```

---

## TypeScript Props

### Defining Page Props

```tsx
interface User {
  id: number;
  name: string;
  email: string;
}

interface Props {
  user: User;
  can: {
    edit: boolean;
    delete: boolean;
  };
}

export default function Show({ user, can }: Props) {
  // user and can are fully typed
}
```

### Extending PageProps

Include shared data in your page props:

```tsx
import { PageProps as InertiaPageProps } from '@inertiajs/core';

// Base shared props (from HandleInertiaRequests)
interface SharedProps {
  user: User | null;
  permissions: string[];
  session: {
    message?: string;
  };
}

// Extend for specific page
interface Props extends SharedProps {
  posts: Post[];
}

export default function Index({ user, permissions, posts }: Props) {
  // Has both shared and page-specific props
}
```

### BudTags PageProps Pattern

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

## Accessing Shared Data

### usePage Hook

```tsx
import { usePage } from '@inertiajs/react';
import { PageProps } from '@/Types/types';

function Header() {
  const { user, session } = usePage<PageProps>().props;

  return (
    <header>
      {user ? (
        <span>Welcome, {user.name}</span>
      ) : (
        <Link href="/login">Login</Link>
      )}
      {session.message && (
        <Flash message={session.message} />
      )}
    </header>
  );
}
```

### In Layout Components

```tsx
import { usePage } from '@inertiajs/react';
import { PageProps } from '@/Types/types';

export default function MainLayout({ children }) {
  const { user, permissions, session } = usePage<PageProps>().props;

  // Show flash message from any form submission
  useEffect(() => {
    if (session.message) {
      toast.success(session.message);
    }
  }, [session.message]);

  return (
    <div>
      <Navbar user={user} permissions={permissions} />
      <main>{children}</main>
    </div>
  );
}
```

---

## Default Props

For optional props with defaults:

```tsx
interface Props {
  users: User[];
  filters?: {
    search?: string;
  };
}

export default function Index({ users, filters = {} }: Props) {
  const { search = '' } = filters;
  // ...
}
```

---

## Page Titles

### Using Head Component

```tsx
import { Head } from '@inertiajs/react';

export default function Index({ users }) {
  return (
    <>
      <Head title="Users" />
      <div>
        <h1>Users</h1>
        {/* ... */}
      </div>
    </>
  );
}
```

### Dynamic Titles

```tsx
export default function Show({ user }) {
  return (
    <>
      <Head title={`${user.name} - Profile`} />
      <div>...</div>
    </>
  );
}
```

---

## BudTags Layout Pattern

```tsx
// resources/js/Layouts/MainLayout.tsx
import { usePage, Head, Link } from '@inertiajs/react';
import { PageProps } from '@/Types/types';
import { ToastContainer, toast } from 'react-toastify';
import { useEffect, useRef } from 'react';

interface Props {
  children: React.ReactNode;
  title?: string;
}

export default function MainLayout({ children, title }: Props) {
  const { user, session, permissions } = usePage<PageProps>().props;
  const lastMessage = useRef<string | null>(null);

  // Handle flash messages
  useEffect(() => {
    if (session.message && session.message !== lastMessage.current) {
      toast.success(session.message);
      lastMessage.current = session.message;
    }
  }, [session.message]);

  return (
    <>
      {title && <Head title={title} />}
      <div className="min-h-screen bg-gray-100">
        <Navbar user={user} permissions={permissions} />
        <main className="py-6">
          {children}
        </main>
        <ToastContainer />
      </div>
    </>
  );
}
```

---

## Next Steps

- **Link Component** → Read `05-link-component.md`
- **useForm Hook** → Read `07-forms-useform.md`
- **Head Component** → Read `24-head-component.md`
