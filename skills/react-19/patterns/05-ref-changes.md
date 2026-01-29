# React 19 Ref Changes

Major changes to how refs work in React 19, including ref as a prop and cleanup functions.

## Ref as a Regular Prop

In React 19, functional components can receive `ref` as a regular prop - no `forwardRef` needed!

### Before (React 18)

```typescript
import { forwardRef } from 'react';

interface InputProps {
  placeholder?: string;
}

const MyInput = forwardRef<HTMLInputElement, InputProps>(
  function MyInput({ placeholder }, ref) {
    return <input placeholder={placeholder} ref={ref} />;
  }
);

// Usage
<MyInput ref={inputRef} placeholder="Enter text" />
```

### After (React 19)

```typescript
interface InputProps {
  placeholder?: string;
  ref?: React.Ref<HTMLInputElement>;
}

function MyInput({ placeholder, ref }: InputProps) {
  return <input placeholder={placeholder} ref={ref} />;
}

// Usage - exactly the same!
<MyInput ref={inputRef} placeholder="Enter text" />
```

### forwardRef Deprecation

- `forwardRef` still works in React 19
- It will be deprecated in a future version
- Use the codemod to migrate: `npx types-react-codemod@latest`

---

## Ref Cleanup Functions

Refs can now return cleanup functions, similar to useEffect:

### Before (React 18)

```typescript
// React calls ref with null on unmount
<input ref={(el) => {
  if (el) {
    // Mount: el is the element
    el.focus();
  } else {
    // Unmount: el is null
    // Limited cleanup options here
  }
}} />
```

### After (React 19)

```typescript
// Return a cleanup function instead
<input ref={(el) => {
  // Mount: el is the element
  el.focus();

  // Return cleanup function
  return () => {
    // Called on unmount - can do proper cleanup
    console.log('Element removed');
  };
}} />
```

### Practical Example: Event Listeners

```typescript
function Resizable({ children }) {
  return (
    <div ref={(el) => {
      if (!el) return;

      const handleResize = () => {
        // Handle resize
      };

      window.addEventListener('resize', handleResize);

      // Cleanup
      return () => {
        window.removeEventListener('resize', handleResize);
      };
    }}>
      {children}
    </div>
  );
}
```

---

## Breaking Change: No More Null on Unmount

React 19 does **not** call ref callbacks with `null` on unmount if you return a cleanup function.

### Migration Required

```typescript
// ❌ This pattern needs updating
<div ref={(el) => {
  if (el) {
    myRef.current = el;
  } else {
    myRef.current = null; // Won't be called in React 19!
  }
}} />

// ✅ Use cleanup function instead
<div ref={(el) => {
  myRef.current = el;
  return () => {
    myRef.current = null;
  };
}} />
```

---

## Implicit Return Fix

**TypeScript now rejects implicit returns from ref callbacks.**

### Before (Worked but problematic)

```typescript
// This returns the result of assignment - undefined
<div ref={el => myRef.current = el} />
```

### After (Must use block syntax)

```typescript
// Explicit block - no return value
<div ref={el => { myRef.current = el }} />

// Or with cleanup
<div ref={el => {
  myRef.current = el;
  return () => { myRef.current = null };
}} />
```

### Codemod

Run the codemod to fix all implicit returns:

```bash
npx types-react-codemod@latest no-implicit-ref-callback-return ./src
```

---

## BudTags Examples

### Custom Input Component

```typescript
// Old pattern
const TextInput = forwardRef<HTMLInputElement, TextInputProps>(
  function TextInput({ label, error, ...props }, ref) {
    return (
      <div className="form-group">
        <label>{label}</label>
        <input ref={ref} {...props} className={error ? 'error' : ''} />
        {error && <span className="error-text">{error}</span>}
      </div>
    );
  }
);

// New pattern
interface TextInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  ref?: React.Ref<HTMLInputElement>;
}

function TextInput({ label, error, ref, ...props }: TextInputProps) {
  return (
    <div className="form-group">
      <label>{label}</label>
      <input ref={ref} {...props} className={error ? 'error' : ''} />
      {error && <span className="error-text">{error}</span>}
    </div>
  );
}
```

### Modal with Focus Management

```typescript
function Modal({ isOpen, onClose, children }) {
  const previousActiveElement = useRef<HTMLElement | null>(null);

  return (
    <dialog
      open={isOpen}
      ref={(el) => {
        if (!el) return;

        // Store previous focus
        previousActiveElement.current = document.activeElement as HTMLElement;

        // Focus the modal
        el.focus();

        // Cleanup: restore focus
        return () => {
          previousActiveElement.current?.focus();
        };
      }}
    >
      {children}
      <button onClick={onClose}>Close</button>
    </dialog>
  );
}
```

### Scroll Position Restoration

```typescript
function ScrollRestoreList({ items, savedPosition }) {
  return (
    <div
      ref={(el) => {
        if (!el) return;

        // Restore scroll position
        el.scrollTop = savedPosition;

        // Save position on unmount
        return () => {
          // Could save to state/localStorage here
          console.log('Final scroll position:', el.scrollTop);
        };
      }}
      style={{ overflow: 'auto', height: '400px' }}
    >
      {items.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}
```

---

## Class Components

Class component refs still work the same way - they point to the instance:

```typescript
class ClassComponent extends React.Component {
  focus() {
    // Instance method
  }

  render() {
    return <div>Hello</div>;
  }
}

// ref.current is the component instance
const ref = useRef<ClassComponent>(null);
<ClassComponent ref={ref} />
ref.current?.focus();
```

---

## Migration Checklist

- [ ] Replace `forwardRef` with ref as prop
- [ ] Fix implicit ref callback returns: `ref={r => (x = r)}` → `ref={r => { x = r }}`
- [ ] Update cleanup logic to use return function instead of checking for null
- [ ] Run codemod: `npx types-react-codemod@latest no-implicit-ref-callback-return ./src`
- [ ] Update TypeScript types if needed

## Next Steps

- Read `06-context-changes.md` for Context simplification
- Read `14-breaking-changes.md` for all breaking changes
