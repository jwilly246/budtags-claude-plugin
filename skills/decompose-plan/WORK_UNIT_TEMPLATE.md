# Work Unit Template

Use this template when creating individual work unit files.

---

# {FEATURE} - Work Unit {N}: {Description}

**Status**: PENDING
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

### Required Context Exploration
Before writing code, the executor MUST:
- Search and READ existing components in `resources/js/Components/`
- Search and READ existing types in `resources/js/types/`
- Search and READ existing hooks in `resources/js/Hooks/`
- READ sibling files in the same directory as files being created
- NEVER recreate buttons, inputs, toggles, tables, badges, or any existing component

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

Run these commands when tasks are complete:

```bash
# 1. STUB DETECTION (must pass first)
# PHP stubs
grep -rn --include="*.php" -E "(// ?TODO|// ?FIXME|throw new \\\\Exception\('Not implemented|function \w+\([^)]*\)\s*\{\s*\})" path/to/new/files

# TypeScript stubs
grep -rn --include="*.tsx" --include="*.ts" -E "(// ?TODO|// ?FIXME|throw new Error\('Not implemented|\(\) => \{ ?\})" path/to/new/files

# If ANY matches found above, STOP - stubs must be removed

# 2. Static analysis
./vendor/bin/phpstan analyse path/to/new/files --memory-limit=512M

# 3. Run tests for this unit
php artisan test --filter=TestClassName

# 4. Code style
./vendor/bin/pint path/to/new/files
```

---

## Done When

All conditions must be true:

- [ ] All tasks above are checked
- [ ] **NO STUBS** - zero TODO/FIXME comments, no empty methods, no placeholder exceptions
- [ ] Verification commands pass (PHPStan, tests, Pint)
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
