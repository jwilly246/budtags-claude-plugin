# Execute Work Unit Prompt

The prompt template for spawning Task agents. Execution-focused—all research was done in plan/decompose phases.

---

## Prompt Template

```
You are executing work unit {WU_ID} for the {FEATURE_NAME} feature.

## Your Task

Implement everything in: `{directory}/WU-{N}-{slug}.md`

## Before Writing Code

1. **Read the work unit file** - contains your tasks, files to create, and context
2. **Read `{directory}/SHARED_CONTEXT.md`** - contains all research from planning:
   - Available components (use these, don't search for others)
   - Existing types (use these, don't create duplicates)
   - Existing services (use these)
   - Naming conventions (follow these exactly)
   - Routes, cache keys, patterns from previous work units

**Trust SHARED_CONTEXT completely.** Do not re-explore the codebase. The planning phase already did that research.

## Execution Rules

| Rule | Pattern |
|------|---------|
| Organization scoping | `->where('organization_id', request()->user()->active_org_id)` |
| Logging | `LogService::store()` (never `Log::` facade) |
| Flash messages | `->with('message', '...')` (not `'success'`) |
| Method names | snake_case: `fetch_all`, `create`, `delete` |
| Forms | Inertia `useForm` (never useState/axios for mutations) |
| Types | No `any` in TypeScript |
| Tests | PHPUnit (not Pest) |

## Code Quality

Every method must be fully implemented. No stubs.

**These will cause rejection:**
- `// TODO`, `// FIXME`
- Empty method bodies
- `throw new Exception('Not implemented')`
- `any` types

If something is unclear: implement your best judgment and document it in "Decisions Made" section.

## When Done

1. Update `{directory}/SHARED_CONTEXT.md` with what you created (cache keys, routes, types, services)
2. Update the work unit's "Decisions Made" section if you made implementation choices
3. Report:

---
## Completion Report

### Files Created
- `path/to/file.php`

### Files Modified
- `path/to/file.php` - what changed

### Tasks Completed
- [x] Task 1
- [x] Task 2

### SHARED_CONTEXT Updates
- Added X to Y table

### Decisions Made
- Chose X because Y

### Issues
- None
---

Do NOT run verification or commit. The orchestrator handles that.
```

---

## Variable Substitution

| Variable | Source |
|----------|--------|
| `{directory}` | Plan directory (e.g., `ADVERTISING`) |
| `{N}` | Work unit number (e.g., `01`) |
| `{slug}` | Work unit slug (e.g., `database-models`) |
| `{WU_ID}` | Full ID (e.g., `WU-01`) |
| `{FEATURE_NAME}` | Feature name from directory |

---

## Agent Type Selection

Read `**Agent**:` field from work unit. **Always use `model: "opus"`** - execution requires deep reasoning.

| Agent Value | subagent_type |
|-------------|---------------|
| `metrc-specialist` | `budtags:metrc-specialist` |
| `quickbooks-specialist` | `budtags:quickbooks-specialist` |
| `leaflink-specialist` | `budtags:leaflink-specialist` |
| `tanstack-specialist` | `budtags:tanstack-specialist` |
| `react-specialist` | `budtags:react-specialist` |
| `php-developer` | `budtags:php-developer` |
| `typescript-developer` | `budtags:typescript-developer` |
| `fullstack-developer` | `budtags:fullstack-developer` (default) |

---

## Agent Capabilities

**Has:** Read, Edit, Write, Bash, Glob, Grep, MCP tools

**Does NOT have:** Conversation history, knowledge of other work units

Each work unit is self-contained via the work unit file and SHARED_CONTEXT.
