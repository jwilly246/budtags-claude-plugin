# Pattern 1: Installation & Setup

## Server-Side Setup (Laravel)

### Install the Package

```bash
composer require inertiajs/inertia-laravel
```

### Publish Middleware

```bash
php artisan inertia:middleware
```

This creates `app/Http/Middleware/HandleInertiaRequests.php`.

### Register Middleware

**Laravel 11+ (bootstrap/app.php)**:

```php
->withMiddleware(function (Middleware $middleware) {
    $middleware->web(append: [
        \App\Http\Middleware\HandleInertiaRequests::class,
    ]);
})
```

**Laravel 10 and earlier (app/Http/Kernel.php)**:

```php
protected $middlewareGroups = [
    'web' => [
        // ... other middleware
        \App\Http\Middleware\HandleInertiaRequests::class,
    ],
];
```

### Create Root Template

Create `resources/views/app.blade.php`:

```blade
<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0" />
    @viteReactRefresh
    @vite(['resources/js/app.tsx', "resources/js/Pages/{$page['component']}.tsx"])
    @inertiaHead
</head>
<body class="font-sans antialiased">
    @inertia
</body>
</html>
```

**Key directives:**
- `@viteReactRefresh` - Enables React Fast Refresh during development
- `@vite()` - Includes your compiled assets
- `@inertiaHead` - Renders `<Head>` component contents
- `@inertia` - Renders the Inertia app root

---

## Client-Side Setup (React)

### Install Packages

```bash
npm install @inertiajs/react
```

### Create App Entry Point

Create `resources/js/app.tsx`:

```typescript
import { createRoot } from 'react-dom/client';
import { createInertiaApp } from '@inertiajs/react';
import { resolvePageComponent } from 'laravel-vite-plugin/inertia-helpers';

const appName = import.meta.env.VITE_APP_NAME || 'Laravel';

createInertiaApp({
  // Dynamic page title
  title: title => `${title} - ${appName}`,

  // Resolve page components from Pages directory
  resolve: name =>
    resolvePageComponent(
      `./Pages/${name}.tsx`,
      import.meta.glob('./Pages/**/*.tsx')
    ),

  // Mount the app
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />);
  },

  // Progress bar configuration
  progress: {
    color: '#4B5563',
    showSpinner: false,
  },
});
```

### BudTags Setup (with React Query)

```typescript
import { createRoot } from 'react-dom/client';
import { createInertiaApp } from '@inertiajs/react';
import { resolvePageComponent } from 'laravel-vite-plugin/inertia-helpers';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      gcTime: 10 * 60 * 1000,
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
    color: '#F87415',
  },
});
```

---

## Configuration Options

### createInertiaApp Options

```typescript
createInertiaApp({
  // Page title template
  title: title => `${title} - App Name`,

  // Page component resolver
  resolve: name => resolvePageComponent(...),

  // App setup function
  setup({ el, App, props }) { ... },

  // Progress bar settings
  progress: {
    color: '#4B5563',    // Progress bar color
    showSpinner: false,  // Hide loading spinner
    delay: 250,          // Delay before showing (ms)
  },

  // Default visit options (v2.x)
  defaults: {
    visitOptions: () => ({
      viewTransition: true,  // Enable View Transitions API
    }),
  },
});
```

### Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import laravel from 'laravel-vite-plugin';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    laravel({
      input: ['resources/js/app.tsx'],
      refresh: true,
    }),
    react(),
  ],
  resolve: {
    alias: {
      '@': '/resources/js',
    },
  },
});
```

---

## TypeScript Setup

### Page Props Type

Create `resources/js/Types/types.tsx`:

```typescript
export interface PageProps {
  user: User | null;
  permissions: string[];
  roles: string[];
  session: {
    message?: string;
    license?: string;
    licenses?: string[];
  };
  // Add your app-specific props
}

export interface User {
  id: number;
  name: string;
  email: string;
  active_org?: Organization;
}
```

### Typed usePage

```typescript
import { usePage } from '@inertiajs/react';
import { PageProps } from '@/Types/types';

function MyComponent() {
  const { user, permissions } = usePage<PageProps>().props;
  // user and permissions are properly typed
}
```

---

## Next Steps

- **Core Concepts** → Read `02-core-concepts.md`
- **Creating Responses** → Read `03-creating-responses.md`
- **Forms** → Read `07-forms-useform.md`
