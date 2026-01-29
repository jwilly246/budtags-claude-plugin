# React 19 Context Changes

React 19 simplifies Context usage by allowing `<Context>` to be used directly as a provider.

## The Change

### Before (React 18)

```typescript
import { createContext } from 'react';

const ThemeContext = createContext('light');

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Page />
    </ThemeContext.Provider>
  );
}
```

### After (React 19)

```typescript
import { createContext } from 'react';

const ThemeContext = createContext('light');

function App() {
  return (
    <ThemeContext value="dark">
      <Page />
    </ThemeContext>
  );
}
```

**Key difference:** No more `.Provider` - just use the Context directly!

---

## Deprecation Timeline

- **React 19:** Both patterns work, `.Provider` is NOT deprecated yet
- **Future version:** `.Provider` will be deprecated
- **Later:** `.Provider` will be removed

**Recommendation:** Start using `<Context>` now for new code.

---

## Codemod

Automatically update your codebase:

```bash
npx types-react-codemod@latest context-provider-to-context ./src
```

This transforms:
```typescript
// Before
<ThemeContext.Provider value={theme}>

// After
<ThemeContext value={theme}>
```

---

## Multiple Contexts

The change works the same with multiple contexts:

```typescript
// Before
function Providers({ children }) {
  return (
    <ThemeContext.Provider value={theme}>
      <UserContext.Provider value={user}>
        <SettingsContext.Provider value={settings}>
          {children}
        </SettingsContext.Provider>
      </UserContext.Provider>
    </ThemeContext.Provider>
  );
}

// After
function Providers({ children }) {
  return (
    <ThemeContext value={theme}>
      <UserContext value={user}>
        <SettingsContext value={settings}>
          {children}
        </SettingsContext>
      </UserContext>
    </ThemeContext>
  );
}
```

---

## BudTags Example

### Organization Context

```typescript
// contexts/OrganizationContext.tsx
import { createContext, useContext } from 'react';

interface Organization {
  id: number;
  name: string;
  licenses: string[];
}

const OrganizationContext = createContext<Organization | null>(null);

// Provider component
export function OrganizationProvider({
  organization,
  children
}: {
  organization: Organization;
  children: React.ReactNode;
}) {
  // React 19 style - no .Provider
  return (
    <OrganizationContext value={organization}>
      {children}
    </OrganizationContext>
  );
}

// Hook for consuming
export function useOrganization() {
  const context = useContext(OrganizationContext);
  if (!context) {
    throw new Error('useOrganization must be used within OrganizationProvider');
  }
  return context;
}
```

### Theme Context

```typescript
// contexts/ThemeContext.tsx
import { createContext, useContext, useState } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');

  // React 19 style
  return (
    <ThemeContext value={{ theme, setTheme }}>
      {children}
    </ThemeContext>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

---

## With use() API

React 19's `use()` can read context conditionally (see `04-use-api.md`):

```typescript
import { use } from 'react';

function ConditionalThemedComponent({ needsTheme }) {
  // Can read context after early return!
  if (!needsTheme) {
    return <div>Default styling</div>;
  }

  const { theme } = use(ThemeContext);

  return (
    <div className={theme === 'dark' ? 'bg-gray-900' : 'bg-white'}>
      Themed content
    </div>
  );
}
```

---

## Consumer Pattern (Still Works)

The Consumer pattern is unchanged:

```typescript
// This still works in React 19
<ThemeContext.Consumer>
  {theme => <div className={theme}>Content</div>}
</ThemeContext.Consumer>
```

But prefer `useContext` or `use()` for cleaner code.

---

## TypeScript Types

Types remain the same:

```typescript
import { createContext, useContext } from 'react';

// Create with type
const MyContext = createContext<string | null>(null);

// Use with type inference
function Component() {
  const value = useContext(MyContext); // type: string | null
  return <div>{value}</div>;
}
```

---

## Migration Checklist

- [ ] Run codemod: `npx types-react-codemod@latest context-provider-to-context ./src`
- [ ] Update `<Context.Provider>` to `<Context>` in new code
- [ ] Consider using `use()` for conditional context reading
- [ ] No changes needed for `useContext` or Consumer patterns

## Next Steps

- Read `04-use-api.md` for conditional context with `use()`
- Read `14-breaking-changes.md` for all breaking changes
