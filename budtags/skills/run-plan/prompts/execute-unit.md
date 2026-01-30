# Execute Work Unit Prompt Template

Use this template when spawning a Task agent to execute a work unit.

---

## Prompt

```
Execute this work unit completely.

WORK UNIT FILE: {directory}/WU-{N}-{slug}.md

INSTRUCTIONS:
1. Read the work unit file completely before starting any work
2. Read the Context section to understand what you're building
3. Check the Dependencies section - required units must be DONE
4. **COMPLETE ALL MANDATORY CONTEXT EXPLORATION (below) before writing code**
5. Execute each task in the Tasks section, in order
6. Create/modify all files listed in the Files section
7. Follow all patterns referenced in the work unit
8. Write tests as specified (use PHPUnit, not Pest)
9. Update the "Decisions Made" section with any choices you made

╔══════════════════════════════════════════════════════════════════════════════╗
║  ZERO TOLERANCE FOR STUBS - COMPLETE IMPLEMENTATIONS ONLY                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

A "stub" is any placeholder code that defers implementation. STUBS ARE FORBIDDEN.

⛔ FORBIDDEN PATTERNS - NEVER WRITE THESE:

PHP:
- `// TODO` or `// FIXME` or `// IMPLEMENT`
- `throw new \Exception('Not implemented');`
- `throw new \RuntimeException('...');` as placeholder
- Empty method bodies: `public function foo() { }`
- `return null;` when a real value is expected
- `// ... rest of implementation`
- `// Add logic here`
- `/* implement */`
- Method signatures without bodies
- `pass;` or equivalent no-ops

TypeScript/React:
- `// TODO` or `// FIXME`
- `throw new Error('Not implemented');`
- Empty function bodies: `const foo = () => { };`
- `return null;` or `return <></>;` as placeholders
- `{/* TODO */}` in JSX
- `any` type as a "figure it out later" escape
- `console.log('implement me');`
- Empty event handlers: `onClick={() => {}}`

Comments that indicate incomplete work:
- "will implement later"
- "needs implementation"
- "placeholder"
- "stub"
- "temporary"
- "mock"
- "fake" (unless it's a test factory)

✅ WHAT TO DO INSTEAD:

If you don't know how to implement something:
1. READ more context - search for similar implementations
2. READ the sibling files - see how others solved it
3. ASK via the work unit's "Decisions Made" section - document the uncertainty
4. IMPLEMENT FULLY or DON'T CREATE THE FILE AT ALL

If a method truly should do nothing (rare):
```php
// Intentionally empty - this hook exists for future extension
public function on_before_save(): void
{
    // No-op by design - subclasses may override
}
```

If functionality is out of scope for this work unit:
- The file/method should NOT be created in this work unit
- It belongs in a different work unit
- Document in "Decisions Made" that it was deferred

╔══════════════════════════════════════════════════════════════════════════════╗
║  EVERY METHOD YOU WRITE MUST BE FULLY FUNCTIONAL.                            ║
║  EVERY COMPONENT YOU CREATE MUST RENDER CORRECTLY.                           ║
║  EVERY TEST YOU WRITE MUST ACTUALLY TEST SOMETHING.                          ║
║                                                                               ║
║  STUBS WILL BE DETECTED AND THE WORK UNIT WILL BE REJECTED.                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║  MANDATORY CONTEXT EXPLORATION - DO THIS BEFORE WRITING ANY CODE             ║
╚══════════════════════════════════════════════════════════════════════════════╝

You are starting with ZERO knowledge of this codebase. Before writing ANY code,
you MUST explore and understand what already exists. NEVER recreate something
that already exists - ALWAYS use existing components, types, services, and patterns.

───────────────────────────────────────────────────────────────────────────────
STEP 1: FRONTEND COMPONENTS (if work unit has frontend tasks)
───────────────────────────────────────────────────────────────────────────────

Search and READ existing components:
- Glob: resources/js/Components/*.tsx
- Glob: resources/js/Components/**/*.tsx

READ these core files to understand available props and usage:
- resources/js/Components/Button.tsx → All buttons
- resources/js/Components/Inputs.tsx → TextInput, TextArea, Select, Checkbox
- resources/js/Components/Badge.tsx → Status badges
- resources/js/Components/DataTable.tsx → Tables
- resources/js/Components/ToggleSwitch.tsx → Toggle switches
- resources/js/Components/FuzzyPicker.tsx → Searchable dropdowns
- resources/js/Components/DateRangePicker.tsx → Date selection
- resources/js/Components/WarningBox.tsx → Alerts/warnings
- resources/js/Components/BoxMain.tsx → Content containers
- resources/js/Components/Headline.tsx → Section headers

Check domain-specific components:
- resources/js/Components/Marketplace/
- resources/js/Components/Items/
- resources/js/Components/Contacts/
- resources/js/Components/Customers/

⛔ NEVER CREATE: buttons, inputs, textareas, selects, checkboxes, toggles,
   tables, badges, date pickers, or any basic UI element. USE EXISTING.

───────────────────────────────────────────────────────────────────────────────
STEP 2: TYPESCRIPT TYPES & INTERFACES (if work unit has frontend tasks)
───────────────────────────────────────────────────────────────────────────────

Search and READ existing types:
- Glob: resources/js/types/*.ts
- Glob: resources/js/types/**/*.d.ts
- READ: resources/js/types/index.d.ts (main type definitions)

⛔ NEVER recreate types for models/entities that already exist.
   Add new types to existing type files, don't create new type files.

───────────────────────────────────────────────────────────────────────────────
STEP 3: FORMS & MODALS (if work unit creates any form or modal)
───────────────────────────────────────────────────────────────────────────────

⚠️ CRITICAL: All forms MUST use Inertia's useForm hook. READ existing modals first!

Search and READ existing modals:
- Glob: resources/js/Components/**/*Modal*.tsx
- READ at least 2-3 existing modals to understand the pattern

The CORRECT pattern:
```tsx
import { useForm } from '@inertiajs/react';

export const CreateItemModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
    isOpen, onClose
}) => {
    const { data, setData, post, processing, errors, reset } = useForm({
        name: '',
        description: '',
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        post(route('items-create'), {
            onSuccess: () => {
                reset();
                onClose();
            },
        });
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <form onSubmit={handleSubmit}>
                <InputText
                    value={data.name}
                    onChange={(e) => setData('name', e.target.value)}
                    errors={errors.name}
                />
                <Button primary disabled={processing}>Save</Button>
            </form>
        </Modal>
    );
};
```

⛔ FORBIDDEN FORM PATTERNS:
- useState for form fields (use useForm instead)
- axios.post for form submission (use useForm's post/put/delete)
- Manual error state management (useForm provides errors object)
- Lifting form state to parent (modal owns its form)
- Using react-hook-form (use Inertia useForm)
- Using fetch() for mutations (use Inertia)

✅ When to use Inertia useForm:
- All form submissions (create, update, delete)
- Modal forms
- Settings pages
- Any mutation that should show flash messages

✅ When to use React Query:
- Read-only data fetching
- Polling/real-time data
- Dashboard stats
- Data that benefits from caching

───────────────────────────────────────────────────────────────────────────────
STEP 4: CUSTOM REACT HOOKS (if work unit has frontend tasks)
───────────────────────────────────────────────────────────────────────────────

Search existing hooks:
- Glob: resources/js/Hooks/**/*.ts
- Glob: resources/js/Hooks/*.ts

Check for existing:
- Data fetching hooks (useQuery patterns)
- Form handling hooks
- Utility hooks

⛔ NEVER recreate a hook that already exists. Check first!

───────────────────────────────────────────────────────────────────────────────
STEP 5: LAYOUTS (if work unit has frontend tasks)
───────────────────────────────────────────────────────────────────────────────

READ existing layouts:
- Glob: resources/js/Layouts/*.tsx

Use AuthenticatedLayout, GuestLayout, etc. - NEVER recreate layouts.

───────────────────────────────────────────────────────────────────────────────
STEP 6: PHP SERVICES (if work unit has backend tasks)
───────────────────────────────────────────────────────────────────────────────

Search existing services:
- Glob: app/Services/*.php

CRITICAL: READ app/Services/LogService.php - you MUST use LogService::store()
          NEVER use the Log:: facade.

Check for existing services before creating new ones.

───────────────────────────────────────────────────────────────────────────────
STEP 7: PHP ENUMS (if work unit has backend tasks)
───────────────────────────────────────────────────────────────────────────────

Search existing enums:
- Glob: app/Enums/*.php

Use existing status enums, type enums instead of string literals.

───────────────────────────────────────────────────────────────────────────────
STEP 8: MODEL TRAITS & SCOPES (if work unit creates/modifies models)
───────────────────────────────────────────────────────────────────────────────

Search existing traits:
- Glob: app/Traits/*.php
- Glob: app/Models/Traits/*.php

Check for:
- Organization scoping traits
- Reusable query scopes
- Common model behaviors

───────────────────────────────────────────────────────────────────────────────
STEP 9: FORM REQUEST PATTERNS (if work unit creates form requests)
───────────────────────────────────────────────────────────────────────────────

Before creating a Form Request, READ a sibling in the same domain:
- Glob: app/Http/Requests/{SameDomain}/*.php

Match:
- Validation rule style (array vs string format)
- Error message patterns
- Authorization patterns

───────────────────────────────────────────────────────────────────────────────
STEP 10: TEST HELPERS (if work unit includes tests)
───────────────────────────────────────────────────────────────────────────────

READ test infrastructure:
- tests/TestCase.php (custom assertions, helper methods)
- Glob: tests/Traits/*.php (helper traits)

Check factories for existing states:
- Glob: database/factories/*.php

Use existing factory states, don't recreate test setup patterns.

───────────────────────────────────────────────────────────────────────────────
STEP 11: SIBLING FILE PATTERNS (ALWAYS DO THIS)
───────────────────────────────────────────────────────────────────────────────

Before creating ANY file, READ a sibling file in the same directory:
- Creating a controller? Read another controller in same folder
- Creating a page? Read another page in same domain
- Creating a component? Read similar components
- Creating a test? Read tests for similar features

Match the EXACT patterns: imports, structure, naming, style.

───────────────────────────────────────────────────────────────────────────────
STEP 12: ROUTE NAMING CONVENTIONS (if work unit adds routes)
───────────────────────────────────────────────────────────────────────────────

Check existing routes in the same domain:
- READ: routes/web.php (or relevant route file)
- Match naming pattern (dashes, not dots: 'users-edit' not 'users.edit')
- Match URL structure patterns

╔══════════════════════════════════════════════════════════════════════════════╗
║  IF YOU SKIP CONTEXT EXPLORATION, YOU WILL CREATE DUPLICATE CODE.            ║
║  DUPLICATES WILL BE REJECTED. DO THE EXPLORATION FIRST.                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

CRITICAL RULES:
- Follow BudTags patterns strictly:
  - Organization scoping on ALL queries
  - snake_case method names (create, delete, fetch_all, not store, destroy)
  - request() helper instead of Request injection
  - LogService::store() instead of Log facade
  - Spread operator for array composition
  - Flash messages use 'message' key

- PHP conventions:
  - PHPStan level 10 compliance
  - Use imported class names in PHPDoc
  - request()->user()->active_org for organization scoping

- TypeScript conventions:
  - No `any` types
  - Proper interface definitions
  - Follow existing component patterns

- Testing:
  - Use PHPUnit (not Pest)
  - Use factories for model creation
  - Test organization scoping (users can't see other orgs' data)

DO NOT:
- Run verification commands (orchestrator handles this)
- Commit changes (orchestrator handles this)
- Push to remote (NEVER)
- Skip any tasks in the work unit
- Skip context exploration steps
- Use `any` types in TypeScript
- Use Log:: facade (use LogService::store)
- Create new Button components (use Button.tsx)
- Create new Input/TextArea/Select components (use Inputs.tsx)
- Create new Toggle components (use ToggleSwitch.tsx)
- Create new Table components (use DataTable.tsx)
- Create new Badge components (use Badge.tsx)
- Recreate ANY component, type, hook, service, or pattern that already exists
- CREATE STUBS OR PLACEHOLDER CODE (see ZERO TOLERANCE section above)
- Write "// TODO" comments anywhere
- Create empty method bodies
- Defer implementation with exceptions
- Leave any code incomplete

WHEN COMPLETE, report:
1. List of files created
2. List of files modified
3. Tasks completed (reference by number)
4. Any decisions made (also update the work unit file)
5. Any issues or concerns encountered
```

---

## Variable Substitution

When building the actual prompt, replace:

| Variable | Source |
|----------|--------|
| `{directory}` | Directory argument from command |
| `{N}` | Work unit number (01, 02, etc.) |
| `{slug}` | Work unit slug from MANIFEST |

**Example:**
```
WORK UNIT FILE: ADVERTISING/WU-01-database-models.md
```

---

## Context the Agent Receives

The Task agent with `fullstack-developer` type has access to:
- All tools (Read, Edit, Write, Bash, Glob, Grep, etc.)
- MCP tools (database-schema, tinker, search-docs, etc.)
- Full codebase access

The agent does NOT have:
- The conversation context (starts fresh)
- Knowledge of previous work units (must read from files)

This is intentional - each work unit is self-contained.

---

## Agent Type Selection

Use `subagent_type: fullstack-developer` because:
- Work units span frontend and backend
- Need access to all tools
- Complex implementation tasks
- Multi-file changes

Alternative considerations:
- `php-developer` - if work unit is backend-only
- `typescript-developer` - if work unit is frontend-only
- `test-engineer` - if work unit is test-focused

Default to `fullstack-developer` for safety.

---

## Handling Agent Response

After the agent completes:

1. **Parse response** for:
   - Files created/modified
   - Tasks completed
   - Issues encountered

2. **Verify files exist**:
   - Check all files from "Files" section exist
   - If missing, note in failure report

3. **Proceed to verification**:
   - Run commands from work unit's Verification section
   - Gate the commit on all passing
