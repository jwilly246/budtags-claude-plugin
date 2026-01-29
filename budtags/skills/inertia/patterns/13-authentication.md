# Pattern 13: Authentication

## Overview

Inertia works seamlessly with Laravel's authentication systems (Breeze, Fortify, Sanctum). Auth state is typically shared via HandleInertiaRequests middleware.

---

## Sharing Auth Data

### HandleInertiaRequests

```php
public function share(Request $request): array
{
    return array_merge(parent::share($request), [
        'auth' => [
            'user' => $request->user(),
        ],
        // Or with specific fields
        'user' => fn () => $request->user()
            ? $request->user()->only('id', 'name', 'email')
            : null,
    ]);
}
```

### BudTags Pattern

```php
public function share(Request $request): array
{
    $user = $request->user();
    $user?->load(['active_org.features']);

    return array_merge(parent::share($request), [
        'user' => fn() => $user,
        'roles' => fn() => $user?->active_org_roles() ?? [],
        'permissions' => fn() => $user?->active_org_perms() ?? [],
    ]);
}
```

---

## Accessing Auth State (React)

### Check Authentication

```tsx
import { usePage } from '@inertiajs/react';
import { PageProps } from '@/Types/types';

function Header() {
  const { user } = usePage<PageProps>().props;

  return (
    <header>
      {user ? (
        <>
          <span>Welcome, {user.name}</span>
          <Link href="/logout" method="post" as="button">
            Logout
          </Link>
        </>
      ) : (
        <>
          <Link href="/login">Login</Link>
          <Link href="/register">Register</Link>
        </>
      )}
    </header>
  );
}
```

### Protected Components

```tsx
function AdminPanel() {
  const { user, permissions } = usePage<PageProps>().props;

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (!permissions.includes('admin')) {
    return <div>Access denied</div>;
  }

  return <div>Admin content</div>;
}
```

---

## Login Form

### React Component

```tsx
import { useForm, Link } from '@inertiajs/react';

export default function Login() {
  const { data, setData, post, processing, errors } = useForm({
    email: '',
    password: '',
    remember: false,
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    post('/login');
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Email</label>
        <input
          type="email"
          value={data.email}
          onChange={e => setData('email', e.target.value)}
        />
        {errors.email && <span className="error">{errors.email}</span>}
      </div>

      <div>
        <label>Password</label>
        <input
          type="password"
          value={data.password}
          onChange={e => setData('password', e.target.value)}
        />
        {errors.password && <span className="error">{errors.password}</span>}
      </div>

      <div>
        <label>
          <input
            type="checkbox"
            checked={data.remember}
            onChange={e => setData('remember', e.target.checked)}
          />
          Remember me
        </label>
      </div>

      <button disabled={processing}>
        {processing ? 'Logging in...' : 'Login'}
      </button>

      <Link href="/forgot-password">Forgot password?</Link>
    </form>
  );
}
```

### Laravel Controller

```php
public function store(LoginRequest $request)
{
    $request->authenticate();
    $request->session()->regenerate();

    return redirect()->intended('/dashboard');
}
```

---

## Logout

### React

```tsx
<Link href="/logout" method="post" as="button">
  Logout
</Link>

// Or with router
function handleLogout() {
  router.post('/logout');
}
```

### Laravel

```php
public function destroy(Request $request)
{
    Auth::guard('web')->logout();
    $request->session()->invalidate();
    $request->session()->regenerateToken();

    return redirect('/');
}
```

---

## Registration

```tsx
import { useForm } from '@inertiajs/react';

export default function Register() {
  const { data, setData, post, processing, errors } = useForm({
    name: '',
    email: '',
    password: '',
    password_confirmation: '',
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    post('/register');
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Name, email, password fields */}
      <button disabled={processing}>Register</button>
    </form>
  );
}
```

---

## Password Reset

### Request Reset Link

```tsx
const { data, setData, post, processing, errors } = useForm({
  email: '',
});

post('/forgot-password', {
  onSuccess: () => toast.success('Reset link sent!'),
});
```

### Reset Password

```tsx
export default function ResetPassword({ token, email }: Props) {
  const { data, setData, post, processing, errors } = useForm({
    token,
    email,
    password: '',
    password_confirmation: '',
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    post('/reset-password');
  }

  return <form onSubmit={handleSubmit}>{/* Fields */}</form>;
}
```

---

## Guest vs Auth Layouts

```tsx
// GuestLayout.tsx
export default function GuestLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      {children}
    </div>
  );
}

// AuthLayout.tsx
export default function AuthLayout({ children }) {
  const { user } = usePage<PageProps>().props;

  return (
    <div className="min-h-screen">
      <Navbar user={user} />
      <main>{children}</main>
    </div>
  );
}

// Usage in page component
Login.layout = (page) => <GuestLayout>{page}</GuestLayout>;
Dashboard.layout = (page) => <AuthLayout>{page}</AuthLayout>;
```

---

## Auth Middleware (Laravel)

Protect routes server-side:

```php
// routes/web.php
Route::middleware('auth')->group(function () {
    Route::get('/dashboard', [DashboardController::class, 'index']);
    Route::resource('users', UserController::class);
});

Route::middleware('guest')->group(function () {
    Route::get('/login', [LoginController::class, 'create']);
    Route::post('/login', [LoginController::class, 'store']);
});
```

---

## Next Steps

- **Authorization** → Read `14-authorization.md`
- **CSRF Protection** → Read `16-csrf-protection.md`
- **Validation Errors** → Read `15-validation-errors.md`
