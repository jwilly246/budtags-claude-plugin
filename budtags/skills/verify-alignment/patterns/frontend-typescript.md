# Frontend TypeScript Type Safety Patterns

**Source:** `.claude/docs/frontend/types.md`, `.claude/docs/frontend/components.md`
**Last Updated:** 2026-01-09
**Pattern Count:** Type safety enforcement

---

## Overview

TypeScript type safety is **NON-NEGOTIABLE**. Using `any` bypasses type checking and leads to runtime errors. This file includes automated scans to detect violations.

**Zero Tolerance Policy:** NO `any` type, NO TypeScript suppressions (`@ts-ignore`, `@ts-expect-error`, `@ts-nocheck`).

---

## Pattern 1: Explicit Types Everywhere

**Rule:** Explicit types for functions, parameters, return values, and component props.

### ✅ CORRECT

```typescript
import { Package } from '@/Types/types-metrc';

interface MyComponentProps {
    packages: Package[];
    onSelect: (id: number) => void;
    title: string;
}

const MyComponent: React.FC<MyComponentProps> = ({ packages, onSelect, title }) => {
    const [selected, setSelected] = useState<Package | null>(null);

    const handleClick = useCallback((pkg: Package): void => {
        setSelected(pkg);
        onSelect(pkg.Id);
    }, [onSelect]);

    return <div>{title}</div>;
};
```

### ❌ WRONG

```typescript
// ❌ No props interface
const MyComponent = (props: any) => {
    const [selected, setSelected] = useState(null);  // ❌ Implicit any

    const handleClick = (pkg) => {  // ❌ No parameter types
        setSelected(pkg);
        props.onSelect(pkg.Id);
    };

    return <div>{props.title}</div>;
};
```

---

## Pattern 2: Error Handling (use `unknown`)

**Rule:** NEVER use `any` for error handling. Use `unknown` + `instanceof` checks.

### ✅ CORRECT

```typescript
try {
    await someAsyncOperation();
} catch (error: unknown) {
    if (error instanceof Error) {
        toast.error(error.message);
    } else if (error instanceof AxiosError) {
        toast.error(error.response?.data?.message ?? 'Request failed');
    } else {
        toast.error('An unexpected error occurred');
    }
}
```

### ❌ WRONG

```typescript
// ❌ Using any
} catch (error: any) {
    toast.error(error.message || 'Failed');
}
```

---

## Pattern 3: Component Props Interfaces

**Rule:** ALWAYS define interfaces for component props. NO `any` props.

### ✅ CORRECT

```typescript
interface TableItemsProps {
    items: Item[];
    onEdit?: (item: Item) => void;
    loading?: boolean;
}

const TableItems: React.FC<TableItemsProps> = ({ items, onEdit, loading = false }) => {
    // ...
};
```

### ❌ WRONG

```typescript
// ❌ No interface
const TableItems = (props: any) => {
    // ...
};

// ❌ Inline props without interface
const TableItems: React.FC<{ items: any[], onEdit: any }> = ({ items, onEdit }) => {
    // ...
};
```

---

## Pattern 4: Hook Return Types

**Rule:** Explicitly type hook return values.

### ✅ CORRECT

```typescript
function usePackageFilter(packages: Package[]): {
    filtered: Package[];
    setFilter: (filter: string) => void;
} {
    const [filter, setFilter] = useState<string>('');

    const filtered = useMemo((): Package[] => {
        return packages.filter(p => p.Name.includes(filter));
    }, [packages, filter]);

    return { filtered, setFilter };
}
```

### ❌ WRONG

```typescript
// ❌ Implicit return type
function usePackageFilter(packages) {
    const [filter, setFilter] = useState('');
    const filtered = packages.filter(p => p.Name.includes(filter));
    return { filtered, setFilter };
}
```

---

## Pattern 5: Type Assertions (Specific, Not `any`)

**Rule:** Use specific type assertions. `as any` is NEVER acceptable without TODO.

### ✅ CORRECT - Specific Type Assertion

```typescript
// Specific type assertion with proper type
const fontFamily = (fontOverride as ZplFont) ?? '0';

// Acceptable with TODO for migration
// TODO: Replace with proper PageProps type after types.tsx update
const flashSuccess = (page.props as any).flash?.success;
```

### ❌ WRONG

```typescript
// ❌ Using any to bypass type checking
const data = someFunction() as any;
data.doesnt.exist.boom();  // Runtime error!

// ❌ No TODO comment for as any
const flashSuccess = (page.props as any).flash?.success;
```

---

## Pattern 6: Import Types from Centralized Files

**Rule:** Import types from `types.tsx` or `types-metrc.tsx`. NEVER duplicate type definitions.

### ✅ CORRECT

```typescript
import { Package, Plant, Harvest } from '@/Types/types-metrc';
import { PageProps } from '@/Types';

interface MyComponentProps {
    packages: Package[];
    plants: Plant[];
}
```

**Metrc Type Optimization Note:**
```typescript
import { Package, Plant, Harvest, Item } from '@/Types/types-metrc';

// Note: Package, Item, Harvest types include many optional fields
// The backend optimizes payloads by excluding rarely-used fields:
// - Package: 22 fields excluded (27.5% reduction)
// - Item: 43 fields excluded (64% reduction)
// - Harvest: 15 fields excluded (48% reduction)
//
// Excluded fields marked with "// Excluded from payload" comments
// See: app/Http/Controllers/MetrcController.php optimization methods
```

### ❌ WRONG

```typescript
// ❌ Duplicating type definitions
interface Package {
    Id: number;
    Tag: string;
    // ... 50 more fields
}
```

---

## Pattern 7: Type Definition Syntax Style

**Rule:** Use the project's established type syntax: **comma separators, no spaces around colons**.

### ✅ CORRECT (Project Pattern)

```typescript
export type User = {
  id?:string,
  name:string,
  email:string,
  roles:string,
};
```

### ❌ WRONG (Industry Default - Not Used Here)

```typescript
export type User = {
  id?: string;
  name: string;
  email: string;
  roles: string;
};
```

**Key differences:**
- Use `,` comma separator (not `;` semicolon)
- No space after `:` colon (`name:string` not `name: string`)
- Use `type` keyword (not `interface` unless extending)
- Follow existing file conventions over "industry standards"

---

## Pattern 8: NO TypeScript Suppressions

**Rule:** NEVER use `@ts-ignore`, `@ts-expect-error`, `@ts-nocheck`.

### ✅ CORRECT

```typescript
// Fix the underlying type issue
interface ProperType {
    field: string;
}

const data: ProperType = {
    field: 'value'
};
```

### ❌ WRONG

```typescript
// ❌ Suppressing type error instead of fixing it
// @ts-ignore
const data = someFunction();
```

---

## Pattern 9: Type Organization (Single Source of Truth)

**Rule:** ALL shared types MUST live in `resources/js/Types/`. Each domain has ONE type file. Components MUST NOT export types.

### Domain Type Files

| Domain | File | Examples |
|--------|------|----------|
| Core app | `types.tsx` | User, Organization, Label, Template, PageProps, DesignElement |
| Metrc | `types-metrc.tsx` | Package, Plant, Harvest, Item, Location, Employee |
| QuickBooks | `types-qbo.tsx` | Customer, Invoice, QboItem, Account |
| LeafLink | `types-leaflink.tsx` | Order, Buyer, LineItem |
| Marketplace | `types-marketplace.tsx` | ShopProduct, CartItem, CheckoutSession, PublicStore |

### Rules

1. **Single Source of Truth**: Each type has exactly ONE export location
2. **Domain Organization**: Types grouped by integration/domain
3. **No Exported Types in Components**: Components may have local interfaces but MUST NOT export types
4. **Reuse Threshold**: Types used in 2+ files MUST be in a type file

### Where to Add New Types

| Type Category | File |
|---------------|------|
| Metrc API response types | `types-metrc.tsx` |
| QuickBooks API types | `types-qbo.tsx` |
| LeafLink API types | `types-leaflink.tsx` |
| Marketplace/Shop types | `types-marketplace.tsx` |
| Everything else | `types.tsx` |

### ✅ CORRECT - Local Props Interface (Not Exported)

```typescript
// In a component file - OK because not exported
interface PackageTableProps {
    packages: Package[];
    onSelect: (pkg: Package) => void;
}

const PackageTable: React.FC<PackageTableProps> = ({ packages, onSelect }) => {
    // ...
};
```

### ✅ CORRECT - Shared Type in Types Directory

```typescript
// In resources/js/Types/types.tsx
export type LabelPrintJob = {
    id:string,
    label_id:string,
    quantity:number,
    status:'pending' | 'printing' | 'complete' | 'failed',
};
```

### ❌ WRONG - Exported Type in Component File

```typescript
// In resources/js/Components/Labels/LabelPrinter.tsx
// ❌ Should be in types.tsx!
export type LabelPrintJob = {
    id: string;
    label_id: string;
    quantity: number;
};
```

### ❌ WRONG - Duplicate Type Definition

```typescript
// In resources/js/Pages/Packages/Index.tsx
// ❌ Package already exists in types-metrc.tsx!
interface Package {
    Id: number;
    Label: string;
}
```

---

## Automated Verification

### Run These Scans Before Committing

#### `any` Type Violations

```bash
# Count `as any` type assertions
grep -r "as any" resources/js --include="*.ts" --include="*.tsx" | wc -l

# Count `: any` type annotations
grep -r ": any" resources/js --include="*.ts" --include="*.tsx" | wc -l

# Find files with >3 violations
grep -r "as any\|: any" resources/js --include="*.ts" --include="*.tsx" -c | grep -v ":0$" | sort -t: -k2 -nr | head -10

# Check for TypeScript suppressions
grep -r "@ts-ignore\|@ts-expect-error\|@ts-nocheck" resources/js --include="*.ts" --include="*.tsx"

# Check for semicolon-style type definitions in types files (Pattern 7 violation)
grep -E "^\s+\w+:\s+\w+;" resources/js/Types/*.tsx | head -5
```

#### Type Organization Violations (Pattern 9)

```bash
# Find exported types OUTSIDE Types/ directory (potential violations)
grep -rn "^export type\|^export interface" resources/js --include="*.tsx" --include="*.ts" | grep -v "resources/js/Types/" | head -20

# Find duplicate type names across type files
grep -rhn "^export type \w\+" resources/js/Types/*.tsx | awk -F: '{print $3}' | sort | uniq -d

# Find components/pages exporting types (should be in Types/)
grep -rln "^export type\|^export interface" resources/js/Pages resources/js/Components --include="*.tsx" 2>/dev/null

# Count types per domain file (sanity check)
for f in resources/js/Types/*.tsx; do echo "$f: $(grep -c '^export type' "$f" 2>/dev/null || echo 0) types"; done

# Find types defined but not exported (local is OK, but verify intent)
grep -rn "^type \w\+ =" resources/js/Pages resources/js/Components --include="*.tsx" | head -10
```

---

## Compliance Thresholds

### `any` Type Thresholds

| Status | Total `any` Occurrences | Per-File `any` Count | Action |
|--------|------------------------|----------------------|--------|
| ✅ **EXCELLENT** | 0-10 | 0-2 | None |
| ⚠️ **ACCEPTABLE** | 11-30 | 3-5 | Document with TODO |
| ❌ **CRITICAL** | >30 | >5 | **Immediate refactor required** |

### Type Organization Thresholds (Pattern 9)

| Status | Exported Types Outside `Types/` | Duplicate Type Names | Action |
|--------|--------------------------------|---------------------|--------|
| ✅ **EXCELLENT** | 0-5 (local props OK) | 0 | None |
| ⚠️ **ACCEPTABLE** | 6-15 | 1-2 (document why) | Move shared types to `Types/` |
| ❌ **CRITICAL** | >15 | >2 | **Immediate consolidation required** |

---

## Common Violations to Check

### Violation 1: Error Handling with `any`

```typescript
// ❌ WRONG
} catch (error: any) {
    toast.error(error.message);
}

// ✅ FIX
} catch (error: unknown) {
    if (error instanceof Error) {
        toast.error(error.message);
    } else {
        toast.error('An unexpected error occurred');
    }
}
```

### Violation 2: Type Assertions to `any`

```typescript
// ❌ WRONG
fontFamily: (fontOverride as any) || '0'

// ✅ FIX
fontFamily: (fontOverride as ZplFont) ?? '0'
```

### Violation 3: Function Parameters without Types

```typescript
// ❌ WRONG
function processData(data) { ... }

// ✅ FIX
function processData(data: Package[]): void { ... }
```

### Violation 4: Component Props without Interface

```typescript
// ❌ WRONG
const MyComponent = (props: any) => { ... }

// ✅ FIX
interface MyComponentProps {
    data: Package[];
    onSelect: (id: string) => void;
}
const MyComponent: React.FC<MyComponentProps> = ({ data, onSelect }) => { ... }
```

### Violation 5: Wrong Type Definition Syntax

```typescript
// ❌ WRONG - Industry default style
export type LabFacility = {
    id: number;
    name: string;
};

// ✅ FIX - Project pattern (comma, no space)
export type LabFacility = {
    id:number,
    name:string,
};
```

### Violation 6: Type Organization (Pattern 9)

```typescript
// ❌ WRONG - Type exported from component file
// In resources/js/Components/Labels/LabelQueue.tsx
export type PrintQueueItem = {
    id: string;
    label: Label;
    copies: number;
};

// ✅ FIX - Move to types.tsx
// In resources/js/Types/types.tsx
export type PrintQueueItem = {
    id:string,
    label:Label,
    copies:number,
};
```

---

## Acceptable Exceptions (Document with TODO)

```typescript
// ✅ ACCEPTABLE - Inertia flash messages (until PageProps extended)
// TODO: Add flash types to PageProps interface
const flashSuccess = (page.props as any).flash?.success;

// ✅ ACCEPTABLE - Third-party library without types
// TODO: Create ambient types for this library
import externalLib from 'untyped-library';
const result = (externalLib as any).doSomething();

// ✅ ACCEPTABLE - Migration in progress
// TODO: Replace with proper MetrcPackage type after types-metrc.tsx update
const packages: any[] = response.data;
```

---

## Verification Report Format

```markdown
### TypeScript Type Safety

**Scan Results:**
- `as any` occurrences: 19 (⚠️ Above threshold)
- `: any` annotations: 11 (⚠️ Above threshold)
- TypeScript suppressions: 1 file (❌ Not allowed)

**Files Needing Attention:**
1. `ElementPropertiesPanel.tsx`: 13 `as any` (❌ CRITICAL)
2. `PackagePicker.tsx`: 3 `: any` (⚠️ REVIEW)
3. `DataTable.tsx`: 8 `as any` (❌ CRITICAL)

**Compliance Status:** ❌ FAILS (30 total violations, >30 threshold)

**Required Actions:**
1. Refactor ElementPropertiesPanel.tsx font handling
2. Replace error handling `any` with `unknown`
3. Remove TypeScript suppressions
```

---

## Impact of Violations

| Violation | Impact | Severity |
|-----------|--------|----------|
| Using `any` | Bypasses type checking, runtime errors | **HIGH** |
| No interface for props | No IntelliSense, prop validation | **MEDIUM** |
| TypeScript suppressions | Hidden type errors | **HIGH** |
| Error handling with `any` | Unhandled error cases | **MEDIUM** |

---

## Related Patterns

- **frontend-critical.md** - Component patterns
- **frontend-data-fetching.md** - React Query types
- `.claude/docs/frontend/types.md** - Complete type definitions
- `resources/js/Types/types-metrc.tsx` - Metrc type definitions
