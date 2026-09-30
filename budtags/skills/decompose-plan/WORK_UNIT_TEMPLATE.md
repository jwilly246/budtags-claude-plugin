# Work Unit Template

Use this template when creating individual work unit files. A unit is a BRANCH-SIZED
builder brief: one review boundary, 5-20 tasks, every task = one commit.

---

# {FEATURE} - Work Unit {N}: {Unit summary, imperative}

**Agent**: {agent_type} ({alternate specialist} acceptable for tasks {a-b})
**Skills**: {List skills agent will have auto-loaded}
**Estimated Tasks**: {5-20} (one commit each)
**Patterns**: {Link to relevant pattern files}

## Context

{Essential context from plan needed for THIS unit only. Say which review boundary this
unit is (behaviour-preserving prefactor / schema + foundations / server core / client
block / surfaces / rollout) and what question the reviewer answers at unit end.}

### What This Unit Accomplishes
{2-5 bullet points on what will exist when the last task is committed}

### Key Decisions Affecting This Work
{Only decisions that impact THIS unit, grouped by the task range they govern, e.g.
"Server (tasks 1-3): ..." / "Client (tasks 4-7): ..."}

### Constraints
{Any constraints to follow - org scoping, naming conventions, existing tests that must
stay byte-identical, etc.}

### Required Context
The orchestrator embeds SHARED_CONTEXT.md inline - do NOT Read it, USE it (anchors for
{the symbols this unit touches}), UPDATE the file with discoveries ({which tables}),
HONOR the Reuse Verdicts. READ sibling files in {dirs} before creating; NEVER
{the reinvention this unit is most at risk of}. Execution contract: EACH TASK BELOW IS
ONE COMMIT (imperative subject from the bold text; the pre-commit hook runs Pint +
PHPStan on staged PHP files; touched-dir vitest + eslint before each TS commit; the
task's targeted tests ride with the commit). gate.sh --since + range diff read +
orchestrator review at unit end. Never `composer check`.

---

## Dependencies

- **Requires**: {List work units that must be complete first, or "-" if none}
- **Enables**: {List work units that can start after this completes}

---

## Tasks (one commit each)

1. [ ] **{Imperative commit subject}** - {What to build: the class/component and its methods or props; the files; the test file and the cases it covers; the targeted checks to run green before committing}
2. [ ] **{Imperative commit subject}** - {...}
3. [ ] **{Imperative commit subject}** - {...}
4. [ ] **{Imperative commit subject}** - {...}
5. [ ] **{Imperative commit subject}** - {...}

**Rules for task lines:** the bold text IS the commit subject (verbatim, no `WU-XX:`
prefix). Tests ride in the same commit as the code they cover. No hygiene-only tasks
(pint/phpstan/type-check are part of every commit, not a task). No "record it in
SHARED_CONTEXT" tasks (fold into the task that created the thing). 5-20 tasks; if you
need more, the unit spans two review boundaries — split it.

---

## Files

> **Format contract:** run-plan's `gate.sh` parses this section mechanically. Each entry
> must be a `- ` bullet with the file path backticked (extension required), under a
> `### Create` or `### Modify` heading. Every backticked extension-bearing span on a
> bullet is treated as a declared path — so do NOT backtick file names inside the
> description text. Declare EVERY file this unit will touch across ALL its commits:
> `gate.sh --since <unit start>` fails the scope audit on any file changed in the
> unit's commit range (or left in the working tree) that is not declared here.

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

> Run by the orchestrator at UNIT END, after `gate.sh --since <unit start>` (Create-file
> existence, range + working-tree scope audit, stub detection, frontend pattern check).
> List ONLY targeted commands: filtered test classes, per-file phpstan, touched-dir
> vitest, type-check, a migration up/down, a tinker probe. NEVER `composer check` or a
> bare full-suite run here — the full gauntlet runs once, at the end of the branch,
> through review-branch.

```bash
php artisan test --filter='{TestClassA}|{TestClassB}|{RegressionClassThatMustStayGreen}'
vendor/bin/phpstan analyse {the PHP files this unit creates or modifies}
npx vitest run {the dirs this unit touches}
npm run type-check
# {Any unit-specific checks: an artisan command to exercise, a route to hit, a migration
#  to run + roll back — things gate.sh cannot know about}
```

---

## Done When

All conditions must be true:

- [ ] Every task committed (one commit per task, subjects from the bold task text)
- [ ] **NO STUBS** - zero TODO/FIXME comments, no empty methods, no placeholder exceptions
- [ ] `gate.sh {FEATURE}/WU-{N}-{slug}.md --since <unit start>` passes plus the Verification block above
- [ ] {Unit-specific invariant, e.g. "existing X tests byte-identical and green", "still exactly ONE migration file on the branch", "`set_user` precedes every MetrcApi call"}
- [ ] No `any` types in TypeScript (if frontend)
- [ ] Organization scoping verified (if applicable)

---

## Decisions Made

{Fill this section DURING implementation - document any decisions or deviations}

### Decision: {Title}
- **Context**: {Why this came up}
- **Choice**: {What was decided}
- **Rationale**: {Why}

---

## Notes for Next Unit

{Any as-built fact the next unit must know: final signatures, prop contracts, renamed
files. The orchestrator propagates these into the downstream WU files.}
