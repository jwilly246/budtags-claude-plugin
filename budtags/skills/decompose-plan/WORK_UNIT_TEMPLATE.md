# Work Unit Template

Use this template when creating individual work unit files.

---

# {FEATURE} - Work Unit {N}: {Description}

**Agent**: {agent_type}
**Skills**: {List skills agent will have auto-loaded}
**Estimated Tasks**: {5-10}
**Patterns**: {Link to relevant pattern files}

## Context

{Essential context from plan needed for THIS unit only. Keep it focused.}

### What This Unit Accomplishes
{2-3 bullet points on what will be built/completed}

### Key Decisions Affecting This Work
{Only decisions that impact THIS specific unit}

### Constraints
{Any constraints to follow - org scoping, naming conventions, etc.}

### Required Context
The run-plan orchestrator embeds the full contents of `{FEATURE}/SHARED_CONTEXT.md` inline
into the executor's prompt. Do NOT call Read on SHARED_CONTEXT.md — it is already in your
context window. Before writing code, the executor MUST:
1. **USE the embedded shared context** for pre-discovered:
   - Available UI components (don't search, they're documented)
   - Existing TypeScript types (don't search, they're documented)
   - Existing PHP services (don't search, they're documented)
   - Naming conventions already established by previous work units
2. **Only explore further** if building something NOT documented in the embedded context
3. **UPDATE the `{FEATURE}/SHARED_CONTEXT.md` file** with any new discoveries (components, types, services, patterns) — updating the file is still your job even though reading it is not
4. READ sibling files in the same directory as files being created
5. NEVER recreate buttons, inputs, toggles, tables, badges, or any existing component

---

## Dependencies

- **Requires**: {List work units that must be complete first, or "-" if none}
- **Enables**: {List work units that can start after this completes}

---

## Tasks

Complete these in order:

1. [ ] {Specific actionable task}
2. [ ] {Specific actionable task}
3. [ ] {Specific actionable task}
4. [ ] {Specific actionable task}
5. [ ] {Specific actionable task}
6. [ ] {Test task - always include tests with the code}
7. [ ] {Verification task}

**Keep to 5-10 tasks.** If you need more, this unit should be split.

---

## Files

> **Format contract:** run-plan's `gate.sh` parses this section mechanically. Each entry
> must be a `- ` bullet with the file path backticked (extension required), under a
> `### Create` or `### Modify` heading. Every backticked extension-bearing span on a
> bullet is treated as a declared path — so do NOT backtick file names inside the
> description text. Declare EVERY file this unit will touch: any tracked file modified
> but not declared here FAILS the gate's scope audit.

### Create
- `path/to/NewFile.php` - {Brief description}
- `path/to/AnotherFile.tsx` - {Brief description}
- `tests/Feature/NewFileTest.php` - {Tests for the above}

### Modify
- `routes/web.php` - Add {specific} routes
- `app/Models/Organization.php` - Add {relationship} relationship

---

## Patterns to Follow

Reference the pattern files - don't repeat their content here:

- See: `patterns/{relevant}-patterns.md` for {what to reference}

### Quick Reference
{Only include 2-3 critical patterns specific to this unit}

```php
// Example: If this is a controller unit, show the key pattern
public function fetch_all(): Response
{
    $org = request()->user()->active_org;
    // ... org-scoped query
}
```

---

## Verification

> The mechanical layer — Create-file existence, scope audit, stub detection, frontend
> pattern check, and the full `composer check` gauntlet (pint, eslint, type-check,
> phpstan, vitest, phpunit) — is run by run-plan's `gate.sh`. Do NOT duplicate those
> commands here; embedded copies drift from the canonical detectors. List ONLY
> verification specific to this unit.

Run these commands when tasks are complete:

```bash
# Tests for this unit (fast feedback before the full gate)
php artisan test --filter=TestClassName

# {Any unit-specific checks: an artisan command to exercise, a tinker probe,
#  a route to hit, a migration to run — things gate.sh cannot know about}
```

---

## Done When

All conditions must be true:

- [ ] All tasks above are checked
- [ ] **NO STUBS** - zero TODO/FIXME comments, no empty methods, no placeholder exceptions
- [ ] run-plan `gate.sh` passes (scope, stubs, patterns, composer check) plus the unit-specific commands above
- [ ] Files listed above exist and work
- [ ] No `any` types in TypeScript (if frontend)
- [ ] Organization scoping verified (if applicable)
- [ ] Every method has complete, functional implementation

---

## Decisions Made

{Fill this section DURING implementation - document any decisions or deviations}

### Decision: {Title}
- **Context**: {Why this came up}
- **Choice**: {What was decided}
- **Rationale**: {Why}

---

## Notes for Next Unit

{Any context that the next work unit should know about}
