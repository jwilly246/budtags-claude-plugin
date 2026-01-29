---
name: react-19
description: React 19 changes, new hooks, Actions, Activity component, and migration guides for upgrading from React 18
version: 1.0.0
category: project
auto_activate:
  patterns:
    - "**/*.{ts,tsx,js,jsx}"
  keywords:
    - "react 19"
    - "useActionState"
    - "useOptimistic"
    - "useFormStatus"
    - "useEffectEvent"
    - "use()"
    - "Activity"
    - "forwardRef deprecated"
    - "ref as prop"
    - "react upgrade"
    - "form action"
    - "useDeferredValue"
---

# React 19 Skill

Comprehensive documentation for **React 19** changes, including new hooks, Actions, forms, and migration guides.

## Release Timeline

| Version | Release Date | Key Features |
|---------|--------------|--------------|
| **19.0** | Dec 5, 2024 | Actions, new hooks, ref changes, Context simplification |
| **19.1** | Mar 28, 2025 | Owner Stack debugging, `captureOwnerStack` API |
| **19.2** | Oct 1, 2025 | Activity component, useEffectEvent, Performance Tracks |

---

## BudTags Stack Context

**Our stack:** Laravel + Inertia.js + React + TypeScript

| React 19 Feature | BudTags Relevance |
|------------------|-------------------|
| **useActionState** | ⚠️ Compare to Inertia `useForm` - similar pending/error handling |
| **useOptimistic** | ✅ Great for quick actions (finish package, adjust inventory) |
| **useFormStatus** | ✅ Useful for submit button components |
| **use()** | ✅ Can complement React Query for promise handling |
| **useEffectEvent** | ✅ Solves common dependency array issues |
| **Activity** | ✅ Perfect for tabs, modals that preserve state |
| **Server Components** | ❌ Not applicable - we use Laravel controllers |
| **Server Actions** | ❌ Not applicable - we use Inertia forms/axios |
| **Metadata hoisting** | ⚠️ Inertia's `<Head>` component handles this |

---

## Progressive Loading Strategy

Load only the patterns you need:

### Upgrade Path (~500 lines, 17%)
```
patterns/01-upgrade-guide.md
patterns/14-breaking-changes.md
migrations/from-18-to-19.md
```

### New Features Overview (~550 lines, 19%)
```
patterns/02-new-hooks.md
patterns/03-actions-forms.md
patterns/04-use-api.md
```

### Forms & Actions (~400 lines, 14%)
```
patterns/03-actions-forms.md
patterns/02-new-hooks.md (useFormStatus section)
```

### React 19.2 Features (~425 lines, 15%)
```
patterns/11-activity-component.md
patterns/12-use-effect-event.md
patterns/13-performance-tracks.md
```

---

## Quick Reference

### New Hooks (React 19.0)

```typescript
// useActionState - Handle async form actions
const [error, submitAction, isPending] = useActionState(
  async (previousState, formData) => {
    const error = await updateName(formData.get("name"));
    if (error) return error;
    redirect("/path");
    return null;
  },
  null
);

// useOptimistic - Optimistic UI updates
const [optimisticName, setOptimisticName] = useOptimistic(currentName);

// useFormStatus - Access parent form state
function SubmitButton() {
  const { pending } = useFormStatus();
  return <button disabled={pending}>Submit</button>;
}

// use() - Read promises/context (can be conditional!)
function Comments({ commentsPromise }) {
  const comments = use(commentsPromise); // Suspends until resolved
  return comments.map(c => <p key={c.id}>{c.text}</p>);
}
```

### Ref Changes (React 19.0)

```typescript
// OLD - forwardRef (deprecated)
const MyInput = forwardRef(function MyInput({ placeholder }, ref) {
  return <input placeholder={placeholder} ref={ref} />;
});

// NEW - ref as regular prop
function MyInput({ placeholder, ref }) {
  return <input placeholder={placeholder} ref={ref} />;
}

// NEW - Ref cleanup functions
<input ref={(el) => {
  // Setup
  return () => {
    // Cleanup (instead of receiving null)
  };
}} />
```

### Context Changes (React 19.0)

```typescript
// OLD
<ThemeContext.Provider value="dark">
  {children}
</ThemeContext.Provider>

// NEW
<ThemeContext value="dark">
  {children}
</ThemeContext>
```

### Activity Component (React 19.2)

```typescript
// Hide content without destroying state
<Activity mode={isVisible ? 'visible' : 'hidden'}>
  <ExpensiveComponent />
</Activity>

// Modes:
// - 'visible': Normal rendering, effects mounted
// - 'hidden': Hidden, effects unmounted, updates deferred
```

### useEffectEvent (React 19.2)

```typescript
// Problem: theme in deps causes reconnects
useEffect(() => {
  connection.on('connected', () => showNotification(theme));
  // ...
}, [roomId, theme]); // theme causes unnecessary effect runs

// Solution: Extract event logic
const onConnected = useEffectEvent(() => {
  showNotification(theme); // Always reads latest theme
});

useEffect(() => {
  connection.on('connected', onConnected);
  // ...
}, [roomId]); // Clean deps!
```

---

## All Pattern Files

### Foundation
- `01-upgrade-guide.md` - Step-by-step upgrade from React 18
- `14-breaking-changes.md` - All breaking changes and migrations

### New Hooks & APIs
- `02-new-hooks.md` - useActionState, useOptimistic, useFormStatus
- `03-actions-forms.md` - Form action prop, automatic handling
- `04-use-api.md` - use() for promises and context

### Syntax Changes
- `05-ref-changes.md` - ref as prop, cleanup functions
- `06-context-changes.md` - Simplified Context provider

### DOM & Resources
- `07-metadata-stylesheets.md` - Metadata hoisting, stylesheet precedence
- `08-resource-preloading.md` - prefetchDNS, preconnect, preload, preinit

### Error Handling & Suspense
- `09-error-handling.md` - Improved errors, new root callbacks
- `10-suspense-hydration.md` - useDeferredValue, hydration improvements

### React 19.2
- `11-activity-component.md` - Activity for hidden/visible UI
- `12-use-effect-event.md` - Extract event logic from effects
- `13-performance-tracks.md` - Chrome DevTools integration

### Migrations
- `migrations/from-18-to-19.md` - Full 18→19 migration guide
- `migrations/19-to-19-1.md` - 19.0→19.1 changes
- `migrations/19-1-to-19-2.md` - 19.1→19.2 changes

---

## Migration Checklist

### React 18 → 19

- [ ] Update packages: `npm install react@19 react-dom@19`
- [ ] Run codemods for refs: `npx types-react-codemod@latest`
- [ ] Replace `forwardRef` with `ref` prop
- [ ] Fix ref callbacks returning values: `ref={r => (x = r)}` → `ref={r => {x = r}}`
- [ ] Update `<Context.Provider>` to `<Context>`
- [ ] Rename `useFormState` to `useActionState`
- [ ] Test hydration (improved error messages will help!)
- [ ] Update TypeScript to latest for new types

### React 19.1 → 19.2

- [ ] Update ESLint plugin: `npm install eslint-plugin-react-hooks@latest`
- [ ] Consider using `<Activity>` for tab/modal state preservation
- [ ] Refactor effects with `useEffectEvent` where appropriate
- [ ] Use Performance Tracks in Chrome DevTools for debugging

---

## Resources

- **React 19 Blog Post:** https://react.dev/blog/2024/12/05/react-19
- **React 19.2 Blog Post:** https://react.dev/blog/2025/10/01/react-19-2
- **React Changelog:** https://github.com/facebook/react/blob/main/CHANGELOG.md
- **Upgrade Codemods:** https://github.com/eps1lon/types-react-codemod
