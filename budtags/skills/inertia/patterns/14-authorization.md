# Pattern 14: Authorization

> **⚠️ BudTags Note:** Examples in this file show `confirm()` for simplicity. In BudTags, **NEVER use `confirm()` or `window.confirm()`**. Use a modal-based confirmation component or the `useConfirmDelete` hook instead.

## Overview

Pass authorization data from Laravel policies/gates to React components via Inertia props.

---

## Passing Permissions

### In Controller

```php
public function show(User $user)
{
    return Inertia::render('Users/Show', [
        'user' => $user,
        'can' => [
            'edit' => auth()->user()->can('update', $user),
            'delete' => auth()->user()->can('delete', $user),
        ],
    ]);
}
```

### In React

```tsx
interface Props {
  user: User;
  can: {
    edit: boolean;
    delete: boolean;
  };
}

export default function Show({ user, can }: Props) {
  return (
    <div>
      <h1>{user.name}</h1>

      {can.edit && (
        <Link href={`/users/${user.id}/edit`}>Edit</Link>
      )}

      {can.delete && (
        <Link
          href={`/users/${user.id}`}
          method="delete"
          onBefore={() => confirm('Delete user?')}
        >
          Delete
        </Link>
      )}
    </div>
  );
}
```

---

## Global Permissions (Shared Data)

### HandleInertiaRequests

```php
public function share(Request $request): array
{
    return array_merge(parent::share($request), [
        'permissions' => fn () => $request->user()
            ?->getAllPermissions()->pluck('name')
            ?? [],

        'roles' => fn () => $request->user()
            ?->getRoleNames()
            ?? [],
    ]);
}
```

### BudTags Pattern

```php
public function share(Request $request): array
{
    $user = $request->user();

    return array_merge(parent::share($request), [
        'user' => fn() => $user,
        'roles' => fn() => $user?->active_org_roles() ?? [],
        'permissions' => fn() => $user?->active_org_perms() ?? [],
    ]);
}
```

### React Usage

```tsx
import { usePage } from '@inertiajs/react';

function AdminLink() {
  const { permissions } = usePage<PageProps>().props;

  if (!permissions.includes('access-admin')) {
    return null;
  }

  return <Link href="/admin">Admin Panel</Link>;
}
```

---

## Permission Helper Hook

Create a custom hook for cleaner authorization checks:

```tsx
// hooks/usePermissions.ts
import { usePage } from '@inertiajs/react';
import { PageProps } from '@/Types/types';

export function usePermissions() {
  const { permissions, roles } = usePage<PageProps>().props;

  return {
    can: (permission: string) => permissions.includes(permission),
    hasRole: (role: string) => roles.includes(role),
    hasAnyRole: (...roleList: string[]) =>
      roleList.some(r => roles.includes(r)),
    hasAllRoles: (...roleList: string[]) =>
      roleList.every(r => roles.includes(r)),
  };
}

// Usage
function AdminPanel() {
  const { can, hasRole } = usePermissions();

  if (!hasRole('admin')) {
    return <AccessDenied />;
  }

  return (
    <div>
      {can('manage-users') && <UserManagement />}
      {can('view-reports') && <Reports />}
    </div>
  );
}
```

---

## Resource-Level Authorization

### Index with Create Permission

```php
public function index()
{
    return Inertia::render('Users/Index', [
        'users' => User::paginate(),
        'can' => [
            'create' => auth()->user()->can('create', User::class),
        ],
    ]);
}
```

```tsx
export default function Index({ users, can }: Props) {
  return (
    <div>
      {can.create && (
        <Link href="/users/create">Create User</Link>
      )}
      <UsersList users={users} />
    </div>
  );
}
```

### Per-Item Authorization

```php
public function index()
{
    $users = User::paginate()->through(fn ($user) => [
        'id' => $user->id,
        'name' => $user->name,
        'email' => $user->email,
        'can' => [
            'edit' => auth()->user()->can('update', $user),
            'delete' => auth()->user()->can('delete', $user),
        ],
    ]);

    return Inertia::render('Users/Index', ['users' => $users]);
}
```

```tsx
function UserRow({ user }: { user: UserWithCan }) {
  return (
    <tr>
      <td>{user.name}</td>
      <td>{user.email}</td>
      <td>
        {user.can.edit && <EditButton userId={user.id} />}
        {user.can.delete && <DeleteButton userId={user.id} />}
      </td>
    </tr>
  );
}
```

---

## BudTags Organization Scoping

```tsx
function PackagesPage({ packages }) {
  const { user, permissions } = usePage<PageProps>().props;
  const { can } = usePermissions();

  // Check if user can manage packages in current org
  const canManagePackages = can('manage-packages');

  // Check organization feature flags
  const hasLabsFeature = user?.active_org?.features
    .some(f => f.name === 'labs');

  return (
    <div>
      {canManagePackages && (
        <Button onClick={() => openCreateModal()}>
          Create Package
        </Button>
      )}

      {hasLabsFeature && <LabsIntegrationPanel />}

      <PackagesTable
        packages={packages}
        canEdit={canManagePackages}
      />
    </div>
  );
}
```

---

## Conditional UI Patterns

### Show/Hide Elements

```tsx
{can.edit && <EditButton />}
```

### Disable Elements

```tsx
<Button disabled={!can.edit}>Edit</Button>
```

### Replace with Message

```tsx
{can.delete ? (
  <DeleteButton />
) : (
  <span className="text-gray-400">Cannot delete</span>
)}
```

---

## Server-Side Enforcement

Always enforce authorization server-side:

```php
public function update(Request $request, User $user)
{
    $this->authorize('update', $user); // Throws 403 if unauthorized

    $user->update($request->validated());

    return redirect()->back()->with('message', 'User updated');
}
```

The React UI authorization is for **UX only**—server must always validate.

---

## Next Steps

- **Validation Errors** → Read `15-validation-errors.md`
- **Error Handling** → Read `17-error-handling.md`
- **Authentication** → Read `13-authentication.md`
