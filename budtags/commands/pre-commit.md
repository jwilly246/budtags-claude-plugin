# Pre-Commit Check

Fail-fast pre-commit validation with critical pattern scanning, static analysis, skill detection, and domain-specific subagent reviews.

## Instructions

### Step 1: Gather Changed Files

Get all modified and staged files:

```bash
git status --porcelain | grep -E '^.M|^M|^A|^\?\?' | awk '{print $2}'
```

Categorize into:
- **PHP_FILES**: Files ending in `.php`
- **TSX_FILES**: Files ending in `.tsx`
- **TS_FILES**: Files ending in `.ts` (but not `.tsx`)
- **TEST_FILES**: Files matching `*Test.php` or `*.test.ts(x)`
- **OTHER_FILES**: Everything else

Display to user:

```
## Files to Check

### PHP Files (X files)
- path/to/file.php

### TSX Files (X files)
- path/to/file.tsx

### TS Files (X files)
- path/to/file.ts

### Test Files (X files)
- path/to/Test.php

### Other Files (X files)
- path/to/other
```

**Exit if:** No PHP, TSX, or TS files to check → "✅ No code files to check. Ready to commit."

---

### Step 2: Critical Pattern Scan (Fast Blockers)

Run **fast grep checks** for critical violations BEFORE expensive static analysis:

#### TypeScript/React Critical Patterns

For TSX_FILES and TS_FILES:

```bash
# Console statements (CRITICAL)
grep -n "console\.log\|console\.error\|console\.warn" [TSX_FILES] [TS_FILES] 2>/dev/null

# Alert usage (CRITICAL)
grep -n "alert(" [TSX_FILES] [TS_FILES] 2>/dev/null

# Native button elements - EXCLUDE Button.tsx itself (CRITICAL)
grep -n "<button" [TSX_FILES] 2>/dev/null | grep -v "Button.tsx"

# TypeScript any usage (HIGH)
grep -n ": any\|as any" [TSX_FILES] [TS_FILES] 2>/dev/null
```

#### PHP Critical Patterns

For PHP_FILES:

```bash
# Log facade usage (CRITICAL)
grep -n "Log::\|\\\\Log::" [PHP_FILES] 2>/dev/null

# Wrong flash message key (MEDIUM)
grep -n "->with('success'" [PHP_FILES] 2>/dev/null
```

#### Pattern Severity Table

| Pattern | Files | Severity | Action |
|---------|-------|----------|--------|
| `console.log/error/warn` | TSX/TS | 🔴 CRITICAL | Must remove |
| `alert(` | TSX/TS | 🔴 CRITICAL | Use toast |
| `<button` (not Button.tsx) | TSX | 🔴 CRITICAL | Use Button component |
| `Log::` or `\Log::` | PHP | 🔴 CRITICAL | Use LogService |
| `: any` or `as any` | TSX/TS | 🟠 HIGH | Add proper types |
| `->with('success'` | PHP | 🟡 MEDIUM | Use `->with('message'` |

#### Early Exit Decision

**If ANY CRITICAL violations found:**

```
## ❌ Critical Violations Found (Step 2)

Found critical patterns that must be fixed before commit:

### 🔴 CRITICAL Issues

1. `resources/js/Components/Modal.tsx:23` - console.log statement
2. `resources/js/Pages/Dashboard.tsx:45` - Native <button> element
3. `app/Http/Controllers/ItemController.php:67` - Log:: facade usage

---

**Stopping pre-commit check.** Fix these CRITICAL issues first - no point running PHPStan with blocking violations.

Would you like me to fix these issues?
- Fix all CRITICAL issues
- Fix specific issues (tell me which)
- No, I'll fix manually
```

**If no CRITICAL violations:** Continue to Step 3.

---

### Step 3: Run Static Analysis

For PHP_FILES, run PHPStan and Pint. Use **Claude's native parallel tool calls** (spawn both Bash commands in the same response):

**PHPStan:**
```bash
./vendor/bin/phpstan analyse [PHP_FILES] --memory-limit=512M --no-progress
```

**Pint (check only):**
```bash
./vendor/bin/pint [PHP_FILES] --test
```

#### Error Threshold Exit

**If PHPStan has >20 errors:**

```
## ❌ PHPStan Threshold Exceeded

PHPStan found [X] errors (threshold: 20). Too many issues to meaningfully review in pre-commit.

**Stopping pre-commit check.** Run `./vendor/bin/phpstan analyse [files]` and fix errors incrementally.
```

**Otherwise:** Record results and continue.

---

### Step 4: Detect and Load Skills

Grep file contents to detect which skills apply:

| Skill | Detection Patterns | Files |
|-------|-------------------|-------|
| tanstack-query | `useQuery`, `useMutation`, `QueryClient`, `useInfiniteQuery`, `useQueryClient` | TSX/TS |
| tanstack-table | `useReactTable`, `getCoreRowModel`, `flexRender`, `ColumnDef` | TSX/TS |
| tanstack-virtual | `useVirtualizer`, `virtualizer`, `virtualRows` | TSX/TS |
| tanstack-form | `@tanstack/react-form`, `formOptions`, `useForm` from tanstack | TSX/TS |
| inertia | `usePage`, `router.visit`, `router.post`, `router.get`, `Inertia::render`, `Inertia::defer` | TSX/TS/PHP |
| react-19 | `useActionState`, `useOptimistic`, `useFormStatus`, `<Activity` | TSX/TS |
| metrc-api | `MetrcApi`, `Metrc` class usage | PHP |
| leaflink | `LeafLink`, `LeafLinkApi` | PHP |
| quickbooks | `QuickBooks`, `QuickBooksApi`, `qbo_` | PHP |
| quill | `Quill`, `ReactQuill`, `useQuill` | TSX/TS |
| zpl | `^XA`, `^XZ`, `^FO`, `ZPL` | Any |
| budtags-testing | `TestCase`, `->mock(`, `Mockery`, `factory(` | PHP (tests) |
| websockets | `ShouldBroadcast`, `ShouldBroadcastNow`, `Reverb`, `Echo.` | PHP/TSX |

**Always load:** `verify-alignment` skill (read `.claude/skills/verify-alignment/skill.md`)

Report detected skills:

```
### Skills Detected
- verify-alignment (always loaded)
- tanstack-query (found in: usePackages.ts, PackageList.tsx)
- inertia (found in: Create.tsx)
- metrc-api (found in: MetrcSyncController.php)
```

---

### Step 5: Spawn Domain Subagents (Parallel)

Spawn all applicable subagents **in a single message** using Claude's native parallel tool calls:

#### For PHP Files → `budtags-specialist`

```
Review these PHP files for BudTags pattern compliance:
[list PHP files]

Files have already passed critical pattern scan. Check for:
- Organization scoping (queries scoped to active_org)
- LogService usage patterns
- Method naming (snake_case, verb-first: create, delete, fetch_*, update_*)
- Request handling (request() helper, not injected Request)
- Array spread for model creation
- PHPStan/Pint compliance notes

Reference: .claude/skills/verify-alignment/patterns/backend-critical.md
```

#### For TSX Files → `react-specialist`

```
Review these React/TSX files for BudTags frontend patterns:
[list TSX files]

Files have already passed critical pattern scan. Check for:
- Button component usage (no native <button>, no type attribute on Button)
- Modal behavior patterns
- TypeScript type safety (no 'any' types)
- React Query vs Inertia usage (React Query for read-heavy, Inertia for forms/CRUD)
- Toast/flash message handling (MainLayout handles flash)
- Props interface patterns

Reference: .claude/skills/verify-alignment/patterns/frontend-critical.md
```

#### For Integration Files (Conditional)

**If MetrcApi detected → `metrc-specialist`:**
```
Review these files for Metrc API integration patterns:
[list Metrc-related files]

Check for:
- License-specific endpoints usage
- Error handling patterns
- Rate limiting awareness
- Facility context handling
```

**If QuickBooksApi detected → `quickbooks-specialist`:**
```
Review these files for QuickBooks integration patterns:
[list QuickBooks-related files]

Check for:
- OAuth token refresh handling
- Invoice/customer sync patterns
- Error handling for API failures
```

**If LeafLinkApi detected → `leaflink-specialist`:**
```
Review these files for LeafLink integration patterns:
[list LeafLink-related files]

Check for:
- Order sync patterns
- Product/inventory sync
- Customer data handling
```

#### For TanStack Files (Conditional)

**If any tanstack-* skill detected → `tanstack-specialist`:**
```
Review these files for TanStack ecosystem patterns:
[list files with TanStack usage]

Detected TanStack usage: [list which: Query, Table, Virtual, Form]

Check for:
- Query key naming and structure
- Proper staleTime/gcTime configuration
- Mutation with proper invalidation
- Column definitions type safety
- Virtualization implementation
- NO `any` types in query/table generics

Reference: Auto-loaded tanstack-* skills
```

---

### Step 6: Generate Report

Aggregate all findings into a consolidated report:

```markdown
## Pre-Commit Check Results

### Static Analysis
- **PHPStan (Level 10)**: ✅ Passed / ❌ X errors found
- **Pint**: ✅ Clean / ⚠️ X files need formatting

### Files Checked
- PHP: X files
- TSX: X files
- TS: X files
- Tests: X files

### Skills Loaded
- verify-alignment (core patterns)
- [list other detected skills with files]

### Subagent Reviews

**budtags-specialist:**
- [findings summary]

**react-specialist:**
- [findings summary]

**[integration-specialist]:** (if applicable)
- [findings summary]

---

## Issues Found

### 🔴 CRITICAL (Must fix before commit)
1. `file:line` - [issue description]

### 🟠 HIGH (Should fix before merge)
1. `file:line` - [issue description]

### 🟡 MEDIUM (Fix when convenient)
1. `file:line` - [issue description]

---

## Recommended Actions
1. [specific action with file reference]
2. [specific action with file reference]
```

---

### Step 7: Offer to Fix

After presenting the report:

```
Would you like me to fix any of these issues?
- Fix all CRITICAL issues
- Fix all issues
- Fix specific issues (tell me which)
- No, I'll fix manually
```

---

## Quick Reference

### Commands

```bash
# Get changed files
git status --porcelain | grep -E '^.M|^M|^A|^\?\?' | awk '{print $2}'

# PHPStan
./vendor/bin/phpstan analyse [files] --memory-limit=512M --no-progress

# Pint (check only)
./vendor/bin/pint [files] --test

# Pint (fix)
./vendor/bin/pint [files]
```

### Subagent Types

- `budtags-specialist` - PHP/Laravel BudTags patterns
- `react-specialist` - React/TypeScript frontend
- `tanstack-specialist` - TanStack ecosystem (Query, Table, Virtual, Form)
- `metrc-specialist` - Metrc API integration
- `quickbooks-specialist` - QuickBooks integration
- `leaflink-specialist` - LeafLink integration

### Key Skills

- `verify-alignment` - Core BudTags patterns (always)
- `tanstack-query` - React Query v5 patterns
- `tanstack-table` - Data table patterns
- `tanstack-virtual` - Virtualization patterns
- `tanstack-form` - Form validation patterns
- `inertia` - Inertia.js patterns
- `react-19` - React 19 features
- `websockets` - Laravel Reverb/broadcasting

---

## Example Output (Clean)

```
## Pre-Commit Check Results

### Static Analysis
- **PHPStan (Level 10)**: ✅ Passed
- **Pint**: ✅ Clean

### Files Checked
- PHP: 3 files
- TSX: 2 files

### Skills Loaded
- verify-alignment (core patterns)
- tanstack-query (found in: usePackages.ts)
- inertia (found in: PackageList.tsx)

### Subagent Reviews

**budtags-specialist:**
- ✅ Organization scoping correct in all files
- ✅ LogService used properly
- ✅ Method naming follows conventions

**react-specialist:**
- ✅ TypeScript types look good
- ✅ React Query patterns correct
- ✅ Button component usage correct

---

## Issues Found

No issues found! ✅

---

Ready to commit.
```

---

## Step 8: Update Pre-Commit State (On Success)

**IMPORTANT:** When the pre-commit check completes successfully (no CRITICAL issues), create the state file to allow commits:

```bash
# Create state file with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Passed" > .claude/.pre-commit-passed
```

This enables the pre-commit-gate hook to allow `git commit` commands. The state file is valid for 2 minutes.

**Note:** If there are CRITICAL or HIGH issues that need fixing, do NOT create the state file until they are resolved and the check passes.

## Example Output (With Issues)

```
## Pre-Commit Check Results

### Static Analysis
- **PHPStan (Level 10)**: ⚠️ 3 errors found
- **Pint**: ✅ Clean

### Files Checked
- PHP: 2 files
- TSX: 3 files

### Skills Loaded
- verify-alignment (core patterns)
- tanstack-query (found in: useInventory.ts)

### Subagent Reviews

**budtags-specialist:**
- ✅ Organization scoping correct
- ⚠️ `FacilityController.php:45` - Consider session-cached permissions

**react-specialist:**
- ⚠️ `Modal.tsx:23` - Button has type="submit" attribute (remove it)
- ✅ TypeScript types good

---

## Issues Found

### 🟠 HIGH (Should fix before merge)
1. `resources/js/Components/Modal.tsx:23` - Button should not have type="submit"

### 🟡 MEDIUM (Fix when convenient)
1. `app/Http/Controllers/FacilityController.php:45` - Consider session-cached permission check

---

## Recommended Actions
1. Remove type="submit" from Button in Modal.tsx:23
2. Consider refactoring permission check to use session cache

Would you like me to fix any of these issues?
- Fix all issues
- Fix specific issues (tell me which)
- No, I'll fix manually
```
