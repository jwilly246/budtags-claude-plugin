# Migration Guide: React 18 to React 19

Step-by-step guide for migrating from React 18 to React 19.

## Prerequisites

- Node.js 18+ recommended
- TypeScript 5.0+ for best type support
- Current app working on React 18.3.x

---

## Step 1: Update Dependencies

```bash
# Core packages
npm install react@19 react-dom@19

# TypeScript types
npm install -D @types/react@19 @types/react-dom@19

# ESLint plugin (recommended for new hooks)
npm install -D eslint-plugin-react-hooks@latest
```

### Check Peer Dependencies

```bash
# See what needs updating
npm outdated

# Common packages to check:
# - @tanstack/react-query
# - @inertiajs/react
# - react-router-dom
# - framer-motion
```

---

## Step 2: Run Codemods

React provides codemods to automate common migrations:

```bash
# Run all React 19 codemods
npx types-react-codemod@latest preset-19 ./src
```

### What the Codemod Fixes

1. **Ref callback implicit returns**
   ```typescript
   // Before
   <div ref={el => myRef.current = el} />

   // After
   <div ref={el => { myRef.current = el }} />
   ```

2. **Deprecated types**
   ```typescript
   // Before
   children: React.ReactChild

   // After
   children: React.ReactNode
   ```

---

## Step 3: Manual Fixes

### 3.1 Ref Callbacks with Cleanup

If you use ref callbacks that need cleanup:

```typescript
// Before: Check for null
<div ref={(el) => {
  if (el) {
    el.addEventListener('scroll', handler);
  } else {
    // Cleanup - but can't access el anymore!
  }
}} />

// After: Return cleanup function
<div ref={(el) => {
  el.addEventListener('scroll', handler);
  return () => {
    el.removeEventListener('scroll', handler);
  };
}} />
```

### 3.2 forwardRef Migration (Optional)

You can migrate incrementally - `forwardRef` still works.

```typescript
// Before
import { forwardRef } from 'react';

interface InputProps {
  label: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  function Input({ label }, ref) {
    return (
      <label>
        {label}
        <input ref={ref} />
      </label>
    );
  }
);

// After
interface InputProps {
  label: string;
  ref?: React.Ref<HTMLInputElement>;
}

function Input({ label, ref }: InputProps) {
  return (
    <label>
      {label}
      <input ref={ref} />
    </label>
  );
}
```

### 3.3 Context.Provider Migration (Optional)

```typescript
// Before
<ThemeContext.Provider value={theme}>
  {children}
</ThemeContext.Provider>

// After
<ThemeContext value={theme}>
  {children}
</ThemeContext>
```

### 3.4 useFormState to useActionState

If you were using `useFormState` from react-dom:

```typescript
// Before
import { useFormState } from 'react-dom';

const [state, action] = useFormState(fn, initial);

// After
import { useActionState } from 'react';

const [state, action, isPending] = useActionState(fn, initial);
```

---

## Step 4: Test Thoroughly

### 4.1 Run Your Test Suite

```bash
npm test
```

Common issues to look for:
- Ref-related test failures
- StrictMode double-render issues
- Type errors from updated types

### 4.2 Test Hydration (If Using SSR)

React 19 has improved hydration error messages. Check for:
- Any hydration warnings in console
- New error format with diffs

### 4.3 Test Forms

If using form actions:
- Verify forms still submit correctly
- Check pending states work

---

## Step 5: Adopt New Features (Optional)

### New Hooks

```typescript
// useActionState for form handling
const [error, submitAction, isPending] = useActionState(fn, null);

// useOptimistic for optimistic updates
const [optimisticValue, setOptimistic] = useOptimistic(value);

// useFormStatus for form state in children
const { pending } = useFormStatus();
```

### use() API

```typescript
// Read promises with Suspense
const data = use(dataPromise);

// Read context conditionally
if (condition) {
  const theme = use(ThemeContext);
}
```

---

## Step 6: Update Error Handling (Optional)

Add new root callbacks:

```typescript
// app.tsx
createRoot(container, {
  onCaughtError: (error, errorInfo) => {
    // Log caught errors
    logError(error, { caught: true, ...errorInfo });
  },
  onUncaughtError: (error, errorInfo) => {
    // Log uncaught errors
    logError(error, { caught: false, ...errorInfo });
  },
  onRecoverableError: (error, errorInfo) => {
    // Log recovered errors
    console.warn('Recovered:', error);
  },
});
```

---

## BudTags-Specific Notes

### Inertia.js Compatibility

Inertia.js works with React 19. Update your app.tsx:

```typescript
// resources/js/app.tsx
import { createRoot } from 'react-dom/client';
import { createInertiaApp } from '@inertiajs/react';

createInertiaApp({
  resolve: (name) => resolvePageComponent(
    `./Pages/${name}.tsx`,
    import.meta.glob('./Pages/**/*.tsx')
  ),
  setup({ el, App, props }) {
    const root = createRoot(el, {
      // Optional: Add error handlers
      onUncaughtError: (error) => {
        console.error('React error:', error);
      },
    });
    root.render(<App {...props} />);
  },
});
```

### React Query Compatibility

TanStack Query v5 works with React 19:

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

// Use as normal
<QueryClientProvider client={queryClient}>
  <App />
</QueryClientProvider>
```

### Component Library Updates

Check if your UI libraries need updates:
- Headless UI
- DaisyUI (Tailwind-based, usually fine)
- Custom component libraries

---

## Troubleshooting

### "Cannot find module 'react'"

```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
```

### TypeScript Errors in Ref Callbacks

```typescript
// Error: Type '() => void' is not assignable to type 'void'
<div ref={el => (myRef.current = el)} />

// Fix: Use block syntax
<div ref={el => { myRef.current = el }} />
```

### Hydration Errors

React 19 shows better error messages with diffs. Common causes:
- `Date.now()` or `Math.random()` in render
- `typeof window !== 'undefined'` checks
- Browser extensions modifying DOM

### StrictMode Double Effects

If you see effects running twice in development:
- This is expected StrictMode behavior
- Ensures effects have proper cleanup
- Doesn't happen in production

---

## Rollback Plan

If you need to rollback:

```bash
npm install react@18.3.1 react-dom@18.3.1
npm install -D @types/react@18 @types/react-dom@18
```

## Checklist

- [ ] Update react and react-dom to 19
- [ ] Update TypeScript types
- [ ] Run codemods
- [ ] Fix ref callback implicit returns
- [ ] Test all forms
- [ ] Test SSR/hydration (if applicable)
- [ ] Update error handling (optional)
- [ ] Adopt new features (optional)

## Next Steps

- Read `14-breaking-changes.md` for complete list of changes
- Read `02-new-hooks.md` to use new hooks
- Read `19-to-19-1.md` for 19.1 migration
