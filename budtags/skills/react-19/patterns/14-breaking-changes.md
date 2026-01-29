# React 19 Breaking Changes

Complete list of breaking changes across React 19.0, 19.1, and 19.2.

## React 19.0 Breaking Changes

### 1. Ref Callback Behavior

**Change:** Ref callbacks no longer receive `null` on unmount if they return a cleanup function.

```typescript
// Before: React calls with null on unmount
<div ref={(el) => {
  if (el) {
    // Mount
  } else {
    // Unmount - el is null
  }
}} />

// After: Return cleanup function instead
<div ref={(el) => {
  // Mount - el is element
  return () => {
    // Unmount - cleanup function called
  };
}} />
```

**Migration:** Update ref callbacks to use cleanup functions.

---

### 2. Implicit Ref Callback Returns

**Change:** TypeScript now rejects implicit returns from ref callbacks.

```typescript
// ❌ Before: Worked but returned undefined
<div ref={el => myRef.current = el} />

// ✅ After: Must use block syntax
<div ref={el => { myRef.current = el }} />
```

**Migration:** Run codemod `npx types-react-codemod@latest no-implicit-ref-callback-return ./src`

---

### 3. useFormState Renamed

**Change:** `ReactDOM.useFormState` renamed to `React.useActionState`.

```typescript
// Before
import { useFormState } from 'react-dom';
const [state, action] = useFormState(fn, initial);

// After
import { useActionState } from 'react';
const [state, action, isPending] = useActionState(fn, initial);
```

**Note:** New hook also returns `isPending` as third element.

---

### 4. StrictMode Behavior

**Change:** StrictMode now re-runs refs during double-render in development.

```typescript
// In development with StrictMode:
// - Ref callback runs
// - Cleanup runs
// - Ref callback runs again
// This helps catch bugs in ref cleanup
```

---

### 5. Context.Provider Deprecation Path

**Change:** `<Context.Provider>` still works but new syntax preferred.

```typescript
// Old (still works, will be deprecated)
<ThemeContext.Provider value={theme}>

// New (preferred)
<ThemeContext value={theme}>
```

---

### 6. forwardRef Deprecation Path

**Change:** `forwardRef` still works but ref-as-prop preferred.

```typescript
// Old (still works, will be deprecated)
const Input = forwardRef((props, ref) => <input ref={ref} {...props} />);

// New (preferred)
function Input({ ref, ...props }) {
  return <input ref={ref} {...props} />;
}
```

---

### 7. Removed/Changed APIs

| API | Status | Migration |
|-----|--------|-----------|
| `ReactDOM.render` | Removed | Use `createRoot` |
| `ReactDOM.hydrate` | Removed | Use `hydrateRoot` |
| `ReactDOM.unmountComponentAtNode` | Removed | Use `root.unmount()` |
| `ReactDOM.findDOMNode` | Removed | Use refs |
| `react-test-renderer` | Deprecated | Use React Testing Library |

---

## React 19.1 Breaking Changes

### 1. useId Format Change

**Change:** `useId` format changed from `:r123:` to `«r123»`.

```typescript
// React 19.0
const id = useId(); // ":r0:"

// React 19.1
const id = useId(); // "«r0»"
```

**Impact:** If you were parsing/matching useId output (you shouldn't), update patterns.

---

### 2. Owner Stack (Development Only)

**Addition:** New `captureOwnerStack` API in development.

```typescript
import { captureOwnerStack } from 'react';

// Only works in development
const stack = captureOwnerStack();
```

---

## React 19.2 Breaking Changes

### 1. useId Format Change (Again)

**Change:** `useId` format changed from `«r123»` to `_r123_`.

```typescript
// React 19.0
const id = useId(); // ":r0:"

// React 19.1
const id = useId(); // "«r0»"

// React 19.2
const id = useId(); // "_r0_"
```

**Reason:** New format works with `view-transition-name` CSS property and is valid in XML 1.0.

---

### 2. ESLint Plugin v6

**Change:** `eslint-plugin-react-hooks` v6 required for `useEffectEvent`.

```bash
# If using useEffectEvent, update ESLint plugin
npm install -D eslint-plugin-react-hooks@latest
```

**Config change:**
```javascript
// If using legacy config format
// Before
extends: ['plugin:react-hooks/recommended']

// After (if issues)
extends: ['plugin:react-hooks/recommended-legacy']
```

---

## TypeScript Changes

### 1. @types/react Updates

```bash
npm install -D @types/react@19 @types/react-dom@19
```

### 2. New Types

```typescript
// New hook types
type UseActionStateReturn<State> = [State, (formData: FormData) => void, boolean];

// Ref as prop type
interface Props {
  ref?: React.Ref<HTMLInputElement>;
}
```

### 3. Removed/Changed Types

| Type | Change |
|------|--------|
| `ReactChild` | Removed, use `ReactNode` |
| `ReactText` | Removed, use `string \| number` |
| `VoidFunctionComponent` | Removed, use `FunctionComponent` |
| `StatelessComponent` | Removed, use `FunctionComponent` |

---

## Environment Requirements

### JavaScript Features Required

React 19 requires these JavaScript features:
- `Promise`
- `Symbol`
- `Object.assign`

If supporting older browsers, include polyfills.

### Minimum Node.js Version

- Node.js 18.x or higher recommended
- Node.js 16.x minimum (end of life)

---

## Migration Codemods

Run all codemods at once:

```bash
npx types-react-codemod@latest preset-19 ./src
```

Or run individually:

```bash
# Fix ref callbacks
npx types-react-codemod@latest no-implicit-ref-callback-return ./src

# Fix deprecated types
npx types-react-codemod@latest deprecated-react-child ./src
npx types-react-codemod@latest deprecated-react-text ./src

# Fix Context.Provider
npx types-react-codemod@latest context-provider-to-context ./src
```

---

## BudTags Migration Checklist

### High Priority
- [ ] Update packages: `npm install react@19 react-dom@19`
- [ ] Run codemods: `npx types-react-codemod@latest preset-19 ./src`
- [ ] Fix ref callback implicit returns
- [ ] Update TypeScript types

### Medium Priority
- [ ] Replace `forwardRef` with ref-as-prop (can do incrementally)
- [ ] Replace `<Context.Provider>` with `<Context>` (can do incrementally)
- [ ] Rename `useFormState` to `useActionState` (if used)

### Low Priority
- [ ] Update ESLint plugin for 19.2 features
- [ ] Consider using new hooks (`useOptimistic`, `useEffectEvent`)
- [ ] Consider using `<Activity>` for tab/modal optimization

---

## Rollback Plan

If critical issues arise:

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0"
  }
}
```

## Next Steps

- Read `01-upgrade-guide.md` for step-by-step upgrade
- Read `migrations/from-18-to-19.md` for detailed migration
