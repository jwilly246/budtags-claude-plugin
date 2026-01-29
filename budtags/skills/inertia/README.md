# Inertia.js Skill

A comprehensive, modular Claude skill providing complete Inertia.js v2 reference using **progressive disclosure** for Laravel + React applications.

## What's Included

This skill package uses a **progressive disclosure architecture** with:

- **skill.md** - Main orchestration file (~400 lines)
- **patterns/** - 25 modular pattern files (~50-250 lines each)

**Total Size**: ~4,000 lines
**Context Efficiency**: 60-80% reduction vs monolithic documentation

## Version Targets

| Package | Version |
|---------|---------|
| @inertiajs/react | ^2.2.16 |
| inertiajs/inertia-laravel | ^2.0 |
| React | 19.x |
| Laravel | 11.x |

## Installation

### Laravel (Server-Side)

```bash
composer require inertiajs/inertia-laravel
```

Publish the middleware:

```bash
php artisan inertia:middleware
```

Add middleware to `app/Http/Kernel.php` or `bootstrap/app.php`:

```php
// Laravel 11+ (bootstrap/app.php)
->withMiddleware(function (Middleware $middleware) {
    $middleware->web(append: [
        \App\Http\Middleware\HandleInertiaRequests::class,
    ]);
})
```

Create root view `resources/views/app.blade.php`:

```blade
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    @viteReactRefresh
    @vite(['resources/js/app.tsx', "resources/js/Pages/{$page['component']}.tsx"])
    @inertiaHead
</head>
<body>
    @inertia
</body>
</html>
```

### React (Client-Side)

```bash
npm install @inertiajs/react
```

Create `resources/js/app.tsx`:

```typescript
import { createRoot } from 'react-dom/client';
import { createInertiaApp } from '@inertiajs/react';
import { resolvePageComponent } from 'laravel-vite-plugin/inertia-helpers';

createInertiaApp({
  title: title => `${title} - My App`,
  resolve: name =>
    resolvePageComponent(
      `./Pages/${name}.tsx`,
      import.meta.glob('./Pages/**/*.tsx')
    ),
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />);
  },
  progress: {
    color: '#4B5563',
  },
});
```

## How to Use

### Method 1: Skill Tool (Recommended)

```
You: Use the inertia skill to explain useForm
```

### Method 2: Direct Questions

```
You: How do I handle form validation with Inertia?
```

### Method 3: Specific Pattern

```
You: Show me the partial reloads pattern
```

## Package Structure

```
.claude/skills/inertia/
├── skill.md (~400 lines)
├── README.md (this file)
└── patterns/
    ├── 01-installation-setup.md
    ├── 02-core-concepts.md
    ├── 03-creating-responses.md
    ├── 04-pages-components.md
    ├── 05-link-component.md
    ├── 06-manual-visits.md
    ├── 07-forms-useform.md
    ├── 08-form-helper-advanced.md
    ├── 09-shared-data.md
    ├── 10-partial-reloads.md
    ├── 11-deferred-props.md
    ├── 12-scroll-management.md
    ├── 13-authentication.md
    ├── 14-authorization.md
    ├── 15-validation-errors.md
    ├── 16-csrf-protection.md
    ├── 17-error-handling.md
    ├── 18-asset-versioning.md
    ├── 19-progress-indicators.md
    ├── 20-remembering-state.md
    ├── 21-events-lifecycle.md
    ├── 22-ssr.md
    ├── 23-testing.md
    ├── 24-head-component.md
    └── 25-budtags-integration.md
```

**Total Files**: 27
**Total Size**: ~4,000 lines

## Key Topics Covered

### Client-Side (React)
- **useForm** - Form state, validation, processing, file uploads
- **usePage** - Access shared props, auth, session data
- **Link** - Client-side navigation with prefetch
- **router** - Programmatic navigation

### Server-Side (Laravel)
- **Inertia::render()** - Creating responses with props
- **HandleInertiaRequests** - Sharing global data
- **Redirects** - Post-form redirect patterns
- **Lazy/Deferred** - Optimized data loading

### BudTags-Specific
- Modal + useForm patterns
- inertiaHandlers utility
- React Query coexistence
- Organization scoping
