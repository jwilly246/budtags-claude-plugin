# React 19 Error Handling

Improved error reporting and new error handling callbacks in React 19.

## Improved Error Messages

### Hydration Errors

React 19 shows clear diffs for hydration mismatches:

**Before (React 18):**
```
Warning: Text content did not match. Server: "Server" Client: "Client"
Warning: An error occurred during hydration...
Warning: Text content did not match... (duplicate)
Uncaught Error: Text content does not match...
```

**After (React 19):**
```
Uncaught Error: Hydration failed because the server rendered HTML
didn't match the client. This can happen if:
- A server/client branch `if (typeof window !== 'undefined')`
- Variable input like `Date.now()` or `Math.random()`
- Date formatting in user's locale
- External changing data without snapshots
- Invalid HTML tag nesting
- Browser extension modifications

  <App>
    <span>
+     Client
-     Server
```

### Consolidated Error Reporting

**Before (React 18) - One error, three logs:**
```
Uncaught Error: Something went wrong
Uncaught Error: Something went wrong (duplicate)
The above error occurred in the MyComponent component...
```

**After (React 19) - One error, one log:**
```
Error: Something went wrong
at MyComponent...
The above error occurred in the MyComponent component...
```

---

## New Root Callbacks

React 19 adds three callbacks to `createRoot`:

```typescript
import { createRoot } from 'react-dom/client';

const root = createRoot(document.getElementById('root'), {
  onCaughtError: (error, errorInfo) => {
    // Called when an Error Boundary catches an error
  },
  onUncaughtError: (error, errorInfo) => {
    // Called when an error is thrown and NOT caught
  },
  onRecoverableError: (error, errorInfo) => {
    // Called when React auto-recovers from an error
  },
});
```

### onCaughtError

Fires when an Error Boundary successfully catches an error:

```typescript
createRoot(container, {
  onCaughtError: (error, errorInfo) => {
    // Log to error tracking service
    errorTracker.captureException(error, {
      componentStack: errorInfo.componentStack,
      caught: true,
    });
  },
});
```

### onUncaughtError

Fires when an error bubbles up without being caught:

```typescript
createRoot(container, {
  onUncaughtError: (error, errorInfo) => {
    // Critical error - log and possibly show error UI
    errorTracker.captureException(error, {
      componentStack: errorInfo.componentStack,
      caught: false,
      critical: true,
    });

    // Could show a global error modal
    showGlobalErrorModal(error);
  },
});
```

### onRecoverableError

Fires when React recovers automatically (e.g., hydration retry):

```typescript
createRoot(container, {
  onRecoverableError: (error, errorInfo) => {
    // Non-critical, but worth logging
    console.warn('React recovered from error:', error);

    // Track for monitoring
    analytics.track('react_recovery', {
      error: error.message,
    });
  },
});
```

---

## BudTags Implementation

### Setup in app.tsx

```typescript
// resources/js/app.tsx
import { createRoot } from 'react-dom/client';
import { createInertiaApp } from '@inertiajs/react';

createInertiaApp({
  resolve: (name) => resolvePageComponent(`./Pages/${name}.tsx`, import.meta.glob('./Pages/**/*.tsx')),
  setup({ el, App, props }) {
    const root = createRoot(el, {
      // Error caught by Error Boundary
      onCaughtError: (error, errorInfo) => {
        console.error('Caught error:', error);

        // Send to error tracking (Sentry, Bugsnag, etc.)
        if (window.Sentry) {
          window.Sentry.captureException(error, {
            extra: { componentStack: errorInfo.componentStack },
          });
        }
      },

      // Uncaught error - critical
      onUncaughtError: (error, errorInfo) => {
        console.error('Uncaught error:', error);

        // Log to Laravel backend
        fetch('/api/log-error', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: error.message,
            stack: error.stack,
            componentStack: errorInfo.componentStack,
          }),
        });
      },

      // Auto-recovered error
      onRecoverableError: (error, errorInfo) => {
        console.warn('Recovered from error:', error.message);
      },
    });

    root.render(<App {...props} />);
  },
});
```

### Error Boundary Component

```typescript
// components/ErrorBoundary.tsx
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // This is also caught by onCaughtError
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 bg-red-50 border border-red-200 rounded">
          <h2 className="text-red-800 font-bold">Something went wrong</h2>
          <p className="text-red-600">{this.state.error?.message}</p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-2 btn btn-sm btn-primary"
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Page-Level Error Boundary

```typescript
// layouts/MainLayout.tsx
function MainLayout({ children }) {
  return (
    <div className="min-h-screen">
      <Navigation />
      <ErrorBoundary fallback={<PageErrorFallback />}>
        {children}
      </ErrorBoundary>
    </div>
  );
}

function PageErrorFallback() {
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <h1 className="text-2xl font-bold text-gray-800">
        Oops! Something went wrong
      </h1>
      <p className="mt-2 text-gray-600">
        Please try refreshing the page
      </p>
      <button
        onClick={() => window.location.reload()}
        className="mt-4 btn btn-primary"
      >
        Refresh Page
      </button>
    </div>
  );
}
```

---

## Error Info Object

The `errorInfo` parameter contains:

```typescript
interface ErrorInfo {
  componentStack: string;  // Component stack trace
  // React 19.1 adds:
  // digest?: string;      // Server error digest
}
```

### Using Component Stack

```typescript
onCaughtError: (error, errorInfo) => {
  // componentStack shows the React component tree
  console.log(errorInfo.componentStack);
  // Output:
  // at Button (<anonymous>:1:1)
  // at Form (<anonymous>:1:1)
  // at Page (<anonymous>:1:1)
  // at App (<anonymous>:1:1)
}
```

---

## Best Practices

### 1. Always Have Error Boundaries

```typescript
// Wrap major sections
<ErrorBoundary>
  <Dashboard />
</ErrorBoundary>

<ErrorBoundary>
  <DataTable />
</ErrorBoundary>
```

### 2. Use onUncaughtError for Critical Alerts

```typescript
onUncaughtError: (error) => {
  // Alert team for critical errors
  if (isProduction) {
    notifyTeam(error);
  }
}
```

### 3. Log Recoverable Errors for Monitoring

```typescript
onRecoverableError: (error) => {
  // Track recovery patterns
  metrics.increment('react.recovery', {
    errorType: error.name,
  });
}
```

## Next Steps

- Read `10-suspense-hydration.md` for hydration patterns
- Read `14-breaking-changes.md` for all changes
