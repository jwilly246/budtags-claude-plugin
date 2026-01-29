# Pattern 01: Installation & Setup

## Installation

### NPM

```bash
npm install @tanstack/react-table
```

### Yarn

```bash
yarn add @tanstack/react-table
```

### PNPM

```bash
pnpm add @tanstack/react-table
```

## Peer Dependencies

TanStack Table requires:

- **React:** 18.0.0 or higher
- **React DOM:** 18.0.0 or higher

```json
{
  "peerDependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
```

## TypeScript Support

TanStack Table is written in TypeScript and provides full type safety out of the box.

**Minimum TypeScript Version:** 4.7+

**No additional @types packages needed** - types are included in the main package.

## Basic Setup

### Step 1: Import Required Functions

```typescript
import {
  useReactTable,
  getCoreRowModel,
  createColumnHelper,
  flexRender,
} from '@tanstack/react-table'
```

### Step 2: Define Your Data Type

```typescript
type Package = {
  Id: number
  Label: string
  ProductName: string
  Quantity: number
  UnitOfMeasureName: string
}
```

### Step 3: Create Column Helper

```typescript
const columnHelper = createColumnHelper<Package>()
```

### Step 4: Define Columns

```typescript
const columns = [
  columnHelper.accessor('Label', {
    header: 'Package Tag',
  }),
  columnHelper.accessor('ProductName', {
    header: 'Product',
  }),
  columnHelper.accessor('Quantity', {
    header: 'Quantity',
  }),
]
```

### Step 5: Create Table Instance

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div>
      <table>
        <thead>
          {table.getHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map(header => (
                <th key={header.id}>
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map(row => (
            <tr key={row.id}>
              {row.getVisibleCells().map(cell => (
                <td key={cell.id}>
                  {flexRender(
                    cell.column.columnDef.cell,
                    cell.getContext()
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

## Complete Minimal Example

```typescript
import { useReactTable, getCoreRowModel, createColumnHelper, flexRender } from '@tanstack/react-table'

type Person = {
  firstName: string
  lastName: string
  age: number
}

const columnHelper = createColumnHelper<Person>()

const columns = [
  columnHelper.accessor('firstName', {
    cell: info => info.getValue(),
  }),
  columnHelper.accessor('lastName', {
    cell: info => info.getValue(),
  }),
  columnHelper.accessor('age', {
    cell: info => info.getValue(),
  }),
]

function App() {
  const data: Person[] = [
    { firstName: 'John', lastName: 'Doe', age: 30 },
    { firstName: 'Jane', lastName: 'Smith', age: 25 },
  ]

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <table>
      <thead>
        {table.getHeaderGroups().map(headerGroup => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map(header => (
              <th key={header.id}>
                {flexRender(header.column.columnDef.header, header.getContext())}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map(row => (
          <tr key={row.id}>
            {row.getVisibleCells().map(cell => (
              <td key={cell.id}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
```

## BudTags Integration

### Existing Implementation

BudTags already uses TanStack Table in:

**File:** `resources/js/Components/DataTable.tsx`

```typescript
import { useReactTable, getCoreRowModel, /* ... */ } from '@tanstack/react-table'
```

### Package.json Entry

Check your `package.json`:

```json
{
  "dependencies": {
    "@tanstack/react-table": "^8.x.x"
  }
}
```

## Build Configuration

### Vite (BudTags uses Vite)

TanStack Table works out of the box with Vite. No special configuration needed.

**vite.config.ts:**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // TanStack Table works automatically
})
```

### Tree Shaking

TanStack Table is fully tree-shakeable. Only import what you use:

```typescript
// ✅ Only imports what you need
import { useReactTable, getCoreRowModel } from '@tanstack/react-table'

// ❌ Don't import everything
import * as Table from '@tanstack/react-table'
```

## Common Setup Errors

### Error: "Cannot find module '@tanstack/react-table'"

**Solution:** Install the package
```bash
npm install @tanstack/react-table
```

### Error: "React version mismatch"

**Solution:** Ensure React 18+
```bash
npm install react@^18.0.0 react-dom@^18.0.0
```

### Error: Type errors in TypeScript

**Solution:** Ensure TypeScript 4.7+
```bash
npm install -D typescript@^4.7.0
```

## Next Steps

After installation:

1. ✅ **Learn Core Concepts** → See pattern 02
2. ✅ **Define Columns** → See pattern 03
3. ✅ **Create Table Instance** → See pattern 04
4. ✅ **Add Features** → See patterns 07-20
