# Pattern 22: Server-Side Rendering (SSR)

## Overview

SSR pre-renders React components on the server for:
- Faster initial page load (HTML available immediately)
- Better SEO (search engines see rendered content)
- Improved perceived performance

> **Note:** BudTags does not currently use SSR, but this pattern is included for reference.

---

## Setup

### Install Dependencies

```bash
npm install @inertiajs/react
npm install -D @vitejs/plugin-react
```

### Create SSR Entry Point

```tsx
// resources/js/ssr.tsx
import { createInertiaApp } from '@inertiajs/react';
import createServer from '@inertiajs/react/server';
import { renderToString } from 'react-dom/server';
import { resolvePageComponent } from 'laravel-vite-plugin/inertia-helpers';

createServer((page) =>
  createInertiaApp({
    page,
    render: renderToString,
    resolve: (name) =>
      resolvePageComponent(
        `./Pages/${name}.tsx`,
        import.meta.glob('./Pages/**/*.tsx')
      ),
    setup: ({ App, props }) => <App {...props} />,
  })
);
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
      input: 'resources/js/app.tsx',
      ssr: 'resources/js/ssr.tsx',
      refresh: true,
    }),
    react(),
  ],
});
```

---

## Laravel Configuration

### Enable SSR

```php
// config/inertia.php
return [
    'ssr' => [
        'enabled' => true,
        'url' => 'http://127.0.0.1:13714',
    ],
];
```

### Start SSR Server

Build and run the SSR server:

```bash
# Build SSR bundle
npm run build

# Start SSR server
php artisan inertia:start-ssr
```

---

## SSR Considerations

### Browser APIs

Don't use browser APIs (window, document) during SSR:

```tsx
// Bad - breaks SSR
const windowWidth = window.innerWidth;

// Good - check for browser
const windowWidth = typeof window !== 'undefined' ? window.innerWidth : 0;

// Good - use effect (only runs in browser)
useEffect(() => {
  const width = window.innerWidth;
}, []);
```

### useEffect vs useLayoutEffect

`useLayoutEffect` doesn't run during SSR:

```tsx
// Warning in SSR
useLayoutEffect(() => {
  // ...
}, []);

// Use useEffect or check environment
useEffect(() => {
  // Safe for SSR
}, []);
```

---

## Hydration

After SSR, React "hydrates" the server-rendered HTML:

1. Server renders HTML with React
2. Browser receives HTML (visible immediately)
3. JavaScript loads
4. React hydrates (attaches event handlers)

### Hydration Mismatches

Avoid differences between server and client render:

```tsx
// Bad - different on server vs client
function Component() {
  return <div>{Date.now()}</div>; // Always different!
}

// Good - use effect for dynamic content
function Component() {
  const [time, setTime] = useState<number | null>(null);

  useEffect(() => {
    setTime(Date.now());
  }, []);

  return <div>{time ?? 'Loading...'}</div>;
}
```

---

## When to Use SSR

### Good Candidates

- Marketing pages
- Blog/content sites
- SEO-critical pages
- Public-facing pages

### Not Needed For

- Admin dashboards (authenticated, not SEO)
- Internal tools
- Apps behind login
- Real-time applications

---

## Production

### Process Manager

Use PM2 or similar:

```bash
# ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'ssr',
      script: 'bootstrap/ssr/ssr.mjs',
    },
  ],
};

pm2 start ecosystem.config.js
```

### Disable in Development

```php
// config/inertia.php
'ssr' => [
    'enabled' => env('INERTIA_SSR_ENABLED', false),
],
```

---

## Next Steps

- **Testing** → Read `23-testing.md`
- **Head Component** → Read `24-head-component.md`
