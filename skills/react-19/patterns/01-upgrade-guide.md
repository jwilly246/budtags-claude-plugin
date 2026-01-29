# React 19 Upgrade Guide

Step-by-step guide for upgrading from React 18 to React 19.

## Package Updates

```bash
# Update React packages
npm install react@19 react-dom@19

# Update TypeScript types
npm install -D @types/react@19 @types/react-dom@19

# Update ESLint plugin (required for useEffectEvent in 19.2)
npm install -D eslint-plugin-react-hooks@latest
```

## Peer Dependency Updates

Many libraries need updates for React 19 compatibility:

```bash
# Common libraries to check
npm outdated | grep react
```

### Known Compatible Versions
- `@tanstack/react-query`: v5.x ✅
- `@inertiajs/react`: Check latest ✅
- `react-router-dom`: v6.x ✅
- `framer-motion`: v11.x ✅

## Codemods

React provides codemods to automate migrations:

```bash
# Install the codemod runner
npx types-react-codemod@latest preset-19 ./src
```

### Available Codemods

| Codemod | Purpose |
|---------|---------|
| `deprecated-react-child` | Remove deprecated `ReactChild` type |
| `deprecated-react-text` | Remove deprecated `ReactText` type |
| `deprecated-void-function-component` | Update `VoidFunctionComponent` |
| `no-implicit-ref-callback-return` | Fix ref callback implicit returns |
| `refobject-defaults` | Update `RefObject` generic defaults |
| `scoped-jsx` | Update JSX namespace imports |
| `useRef-required-initial` | Add required initial value to useRef |

## BudTags-Specific Notes

### Inertia.js Compatibility

Inertia.js works with React 19. Key considerations:

```typescript
// Inertia's useForm vs React 19's useActionState
// Both handle pending states - choose based on use case:

// Inertia useForm - for Inertia form submissions
const { data, setData, post, processing } = useForm({ name: '' });

// React 19 useActionState - for custom async actions
const [error, submitAction, isPending] = useActionState(asyncFn, null);
```

### React Query Compatibility

TanStack Query v5 works with React 19:

```typescript
// React 19's use() can complement React Query
// But React Query is still preferred for:
// - Caching
// - Background refetching
// - Mutations with invalidation
```

## Step-by-Step Migration

### 1. Update Dependencies

```bash
npm install react@19 react-dom@19
npm install -D @types/react@19 @types/react-dom@19
```

### 2. Run Codemods

```bash
npx types-react-codemod@latest preset-19 ./src
```

### 3. Fix Ref Callbacks

```typescript
// Before (implicit return - now errors)
<div ref={el => (myRef = el)} />

// After (explicit block)
<div ref={el => { myRef = el }} />
```

### 4. Update forwardRef Components

```typescript
// Before
const MyInput = forwardRef<HTMLInputElement, Props>((props, ref) => {
  return <input {...props} ref={ref} />;
});

// After (ref is now a regular prop)
function MyInput({ ref, ...props }: Props & { ref?: React.Ref<HTMLInputElement> }) {
  return <input {...props} ref={ref} />;
}
```

### 5. Update Context Providers

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

### 6. Rename useFormState

```typescript
// Before (React DOM)
import { useFormState } from 'react-dom';

// After (React)
import { useActionState } from 'react';
```

### 7. Test Thoroughly

- Run your test suite
- Check for hydration errors (now with better messages!)
- Verify ref cleanup behavior
- Test form submissions

## Common Issues

### Ref Callback Returns

**Error:** TypeScript error on ref callback
**Cause:** Implicit return of assignment
**Fix:** Use block syntax

```typescript
// ❌ Error
ref={el => myRef.current = el}

// ✅ Fixed
ref={el => { myRef.current = el }}
```

### Missing forwardRef

**Warning:** Component doesn't forward ref
**Cause:** Using old forwardRef pattern
**Fix:** Accept ref as prop

### Hydration Mismatches

React 19 shows better error messages with diffs:
```
Uncaught Error: Hydration failed because the server rendered HTML
didn't match the client.
  <App>
    <span>
+     Client
-     Server
```

## Rollback Plan

If issues arise, you can temporarily pin to React 18:

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  }
}
```

## Next Steps

After upgrading:
1. Read `02-new-hooks.md` to use new hooks
2. Read `03-actions-forms.md` for form improvements
3. Consider `11-activity-component.md` for UI state management
