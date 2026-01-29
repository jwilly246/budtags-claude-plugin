# Pattern 16: CSRF Protection

## Overview

Inertia automatically handles CSRF tokens for all non-GET requests. Laravel's CSRF protection works seamlessly.

---

## How It Works

1. Laravel includes CSRF token in the session
2. Inertia reads token from `XSRF-TOKEN` cookie
3. Inertia sends token in `X-XSRF-TOKEN` header on each request
4. Laravel validates the token automatically

**You don't need to do anything special** - it just works!

---

## Manual Token Access

If needed, access the token directly:

### In JavaScript

```tsx
// Inertia reads from cookie automatically
// But if you need it:
const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
```

### In Blade Template

```blade
<meta name="csrf-token" content="{{ csrf_token() }}">
```

---

## Axios Integration

If using Axios alongside Inertia:

```tsx
import axios from 'axios';

// Axios already reads XSRF-TOKEN cookie by default
// But ensure it's configured:
axios.defaults.withCredentials = true;
axios.defaults.withXSRFToken = true;
```

---

## Session Expiration

When the session expires, CSRF validation fails. Inertia handles this gracefully:

### 419 Error Handling

```tsx
// Inertia will show a modal prompting page refresh
// Or handle manually:
router.on('invalid', (event) => {
  if (event.detail.response.status === 419) {
    // Session expired
    toast.error('Session expired. Please refresh the page.');
  }
});
```

---

## Excluding Routes

Exclude routes from CSRF verification in Laravel:

```php
// app/Http/Middleware/VerifyCsrfToken.php
protected $except = [
    'webhook/*',
    'api/external/*',
];
```

---

## Common Issues

### Token Mismatch After Deploy

Clear browser cookies or:

```php
// Force new session on deploy
public function version(Request $request): ?string
{
    return md5_file(public_path('build/manifest.json'));
}
```

### CORS with External Domains

Ensure CORS is configured in `config/cors.php`:

```php
'supports_credentials' => true,
```

---

## Testing

In tests, CSRF is typically disabled:

```php
// Laravel automatically disables CSRF in testing
$this->post('/users', $data)->assertRedirect();
```

---

## Next Steps

- **Error Handling** → Read `17-error-handling.md`
- **Authentication** → Read `13-authentication.md`
- **Validation** → Read `15-validation-errors.md`
