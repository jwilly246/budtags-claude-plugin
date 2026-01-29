# Pattern 17: Error Handling

## Error Types

| Status | Type | Handling |
|--------|------|----------|
| 422 | Validation | `errors` object in useForm |
| 403 | Forbidden | Custom error page |
| 404 | Not Found | Custom error page |
| 419 | CSRF Expired | Session refresh |
| 500 | Server Error | Custom error page |
| 503 | Maintenance | Maintenance page |

---

## Custom Error Pages

### Create Error Pages

```tsx
// resources/js/Pages/Error.tsx
interface Props {
  status: number;
}

export default function Error({ status }: Props) {
  const title = {
    503: 'Service Unavailable',
    500: 'Server Error',
    404: 'Page Not Found',
    403: 'Forbidden',
  }[status] || 'Error';

  const description = {
    503: 'Sorry, we are doing some maintenance. Please check back soon.',
    500: 'Whoops, something went wrong on our servers.',
    404: 'Sorry, the page you are looking for could not be found.',
    403: 'Sorry, you are not authorized to access this page.',
  }[status] || 'An unexpected error occurred.';

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900">{status}</h1>
        <h2 className="text-2xl font-medium text-gray-700 mt-4">{title}</h2>
        <p className="text-gray-500 mt-2">{description}</p>
        <Link href="/" className="mt-6 inline-block text-blue-600">
          Go Home
        </Link>
      </div>
    </div>
  );
}
```

### Laravel Exception Handler

```php
// app/Exceptions/Handler.php (Laravel 10)
// or bootstrap/app.php (Laravel 11)

use Inertia\Inertia;

// Laravel 11
->withExceptions(function (Exceptions $exceptions) {
    $exceptions->respond(function (Response $response, Throwable $e, Request $request) {
        if (! app()->environment(['local', 'testing']) && in_array($response->getStatusCode(), [500, 503, 404, 403])) {
            return Inertia::render('Error', ['status' => $response->getStatusCode()])
                ->toResponse($request)
                ->setStatusCode($response->getStatusCode());
        }

        return $response;
    });
})
```

---

## Validation Errors (422)

Handled automatically by useForm:

```tsx
const { errors } = useForm({ email: '' });

// errors.email = "The email field is required."
```

See `15-validation-errors.md` for details.

---

## Global Error Listener

Listen to all errors:

```tsx
// In app.tsx or layout
import { router } from '@inertiajs/react';

router.on('error', (event) => {
  console.error('Inertia error:', event.detail.errors);
});

router.on('invalid', (event) => {
  const status = event.detail.response.status;

  if (status === 419) {
    toast.error('Session expired. Please refresh.');
  }
});
```

---

## Form Error Callbacks

### onError Callback

```tsx
post('/users', {
  onError: (errors) => {
    // errors is Record<string, string>
    toast.error(Object.values(errors)[0] || 'An error occurred');
  },
});
```

### BudTags Pattern

```tsx
import { handleInertiaError } from '@/utils/inertiaHandlers';

post('/harvest-plants', {
  onError: (errors) => handleInertiaError(errors, 'Failed to harvest'),
});
```

---

## Network Errors

Handle connection failures:

```tsx
router.on('exception', (event) => {
  // Network error, timeout, etc.
  toast.error('Connection failed. Please check your internet.');
});
```

---

## Session Expiration (419)

Handle expired sessions:

```tsx
router.on('invalid', (event) => {
  if (event.detail.response.status === 419) {
    // Option 1: Show message
    toast.error('Your session has expired. Please refresh the page.');

    // Option 2: Force refresh
    // window.location.reload();

    // Option 3: Redirect to login
    // window.location.href = '/login';
  }
});
```

---

## Error Boundaries (React)

Catch React rendering errors:

```tsx
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('React error:', error, info);
    // Send to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded">
          <h2 className="text-red-800">Something went wrong</h2>
          <button
            onClick={() => window.location.reload()}
            className="mt-2 text-blue-600"
          >
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage in layout
<ErrorBoundary>
  {children}
</ErrorBoundary>
```

---

## Axios Error Handling

For non-Inertia requests (React Query, etc.):

```tsx
try {
  const response = await axios.get('/api/data');
} catch (error) {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 401) {
      router.visit('/login');
    } else if (error.response?.status === 403) {
      toast.error('Access denied');
    } else {
      toast.error(error.response?.data?.message || 'Request failed');
    }
  }
}
```

---

## BudTags Error Handlers

```tsx
// utils/inertiaHandlers.tsx
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
            <pre className="text-xs mt-2 max-h-48 overflow-auto">
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

export function handleInertiaSuccess(
  page: Page,
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
```

---

## Next Steps

- **Asset Versioning** → Read `18-asset-versioning.md`
- **Validation Errors** → Read `15-validation-errors.md`
- **Events** → Read `21-events-lifecycle.md`
