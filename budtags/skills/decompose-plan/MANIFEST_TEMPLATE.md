# Manifest Template

Use this template when creating a manifest for decomposed work units.

---

# {FEATURE_NAME} Implementation Manifest

**Source Plan**: `{ORIGINAL_PLAN_FILE.md}`
**Created**: {DATE}
**Status**: Not Started

## Execution Environment

| Item | Value |
|------|-------|
| Tree | {MAIN tree `/path` (no worktree)  /  worktree `/path` with test DB `budtags_<slug>_test`} |
| Branch | {ONE new branch off `origin/main` with `--no-track`: `feature/{slug}`; note any branch that must merge first, and whether it already has} |
| Test DB | {default `budtags_test` family / the worktree's `DB_DATABASE=budtags_<slug>_test` prefix on EVERY test command} |
| Migration | {ONE NEW file on this branch: `database/migrations/{date}_{slug}.php` (WU-02 task 1) / none. Name any merged migration the plan mentioned that must NOT be edited} |
| After the migration commit | `composer migrate-test-dbs` |
| Working tree | {Any pre-existing uncommitted change that belongs to no unit: stash it before the first gate run or the scope audit fails} |
| End | `/review-branch` (its `composer check` is the branch's ONE full gauntlet) |

## Execution Contract

Units are BRANCH-SIZED builder briefs (one review boundary each):

- **Each task in a unit = one commit.** The task line's bold text is the imperative
  commit subject. The builder commits after every task; the repo's pre-commit hook runs
  Pint + PHPStan on the staged PHP files; the builder runs touched-dir vitest + eslint
  before TS commits; the task's targeted tests ride in the same commit. Whole-file
  commits only.
- **The orchestrator reviews at UNIT end**, not per task: `gate.sh {FEATURE}/WU-XX.md
  --since <unit start>` (Create files exist, scope audit of the commit range and the
  working tree, stubs, frontend patterns), the unit's Verification block (targeted
  commands only), a read of `git diff <unit start>..HEAD`, and the SHARED_CONTEXT audit.
  Then the unit is marked DONE below with its branch tip.
- **No `composer check` between commits or units.** It runs ONCE, at the end of the
  branch, inside `/review-branch`, whose report is the branch's merge gate.
- One migration per branch, in a NEW file (a merged migration has already run on every
  developer database and must never be edited).
- Exhaustive `### Create` / `### Modify` declarations bind the scope audit per unit.
- Execution is SERIAL. Never pipe a gate command through `| tail` (it eats the exit code).

## Overview

{2-3 sentences about what's being built and its business value}

---

## Work Units

> The **Description** column is the UNIT SUMMARY (imperative, no trailing period, no
> "WU-XX" reference). Commit subjects come from the task lines inside each unit.

| ID | Unit | Description (unit summary; commits come from task lines) | Status | Depends On |
|----|------|-------------|--------|------------|
| WU-01 | prefactor | Extract the shared cores the feature builds on | PENDING | - |
| WU-02 | foundations | {Add the schema and the small primitives the feature needs} | PENDING | WU-01 |
| WU-03 | server-core | {Build the server contract} | PENDING | WU-01 |
| WU-04 | client-block | {Build the client contracts and the component nothing mounts yet} | PENDING | WU-02, WU-03 |
| WU-05 | surfaces | {Wire the component into the existing surfaces} | PENDING | WU-04 |

**Status Legend** (run-plan's stored status model — write ONLY these four):
- `PENDING` - Not yet started
- `IN PROGRESS` - Currently being executed
- `DONE` - Completed, reviewed; branch tip recorded
- `BLOCKED` - Failed review/verification, needs a fix before resuming

`READY` is **computed, never stored**: a unit is READY when its status is PENDING
and all of its dependencies are DONE. Do not write READY into the table.

---

## Dependency Graph

```
WU-01 (prefactor) ──┬──> WU-02 (foundations) ──┐
                    │                          ├──> WU-04 (client-block) ──> WU-05 (surfaces)
                    └──> WU-03 (server-core) ──┘
```

## Parallel Opportunities

Serial execution is the rule; the graph only says what MAY reorder.
- {WU-02 and WU-03 are independent of each other; WU-04 needs both}
- Same-file notes: {which units both edit `routes/web.php` or the same modal; serial order makes it harmless}

---

## Branch / Migration Grouping (ONE migration per branch)

| Branch | Units | Migration |
|--------|-------|-----------|
| `feature/{slug}` | WU-01 .. WU-05 | {NEW file in WU-02 task 1 / none} |

{Multi-branch programs: one row per branch. Backfills are COMMANDS in a rollout unit, never inside migrations; rehearse on a prod dump.}

---

## File Manifest

### Files to Create

```
app/Services/{Domain}/
  └── {Service}.php                          (WU-03)

database/migrations/
  └── {date}_{slug}.php                      (WU-02, the branch's only migration)

resources/js/Components/{Feature}/
  └── {Component}.tsx                        (WU-04)

tests/Feature/
  ├── {Service}Test.php                      (WU-03)
  └── {Feature}ControllerTest.php            (WU-03)

Vitest (beside their components under __tests__/):
  {Component}.test.tsx (WU-04), {Surface}.test.tsx (WU-05)
```

### Files to Modify

| File | Changes |
|------|---------|
| `routes/web.php` | Add {feature} routes (WU-03) |
| `app/Models/Organization.php` | Add {feature} relationship (WU-02) |
| `resources/js/Types/types-marketplace.tsx` | Add TypeScript types (WU-04) |

---

## Key Decisions (from Plan)

Document important decisions from the original plan:

### Decision 1: {Title}
{Brief explanation of decision and rationale}

### Decision 2: {Title}
{Brief explanation of decision and rationale}

---

## Progress Log

Updated by run-plan after each unit's review (start SHA when IN PROGRESS, branch tip and
commit list on DONE, failure details on BLOCKED):

### WU-01: {unit summary}
- **Status**: PENDING
- **Started at**: {SHA at unit start, filled by run-plan}
- **Completed**: {DATE, filled by run-plan}
- **Branch tip**: {short hash + commit count, filled by run-plan}
- **Decisions Made**: {Any decisions during implementation}
- **Notes**: {Anything notable; on BLOCKED — which step failed, command output, fix required, tasks committed so far}

### WU-02: {unit summary}
- **Status**: PENDING
- **Started at**:
- **Completed**:
- **Branch tip**:
- **Decisions Made**:
- **Notes**:

{Continue for each work unit...}

---

## Completion Checklist

Before marking the feature complete:

- [ ] All work units show DONE status with a branch tip
- [ ] Feature tests passing: `php artisan test --filter={Feature}`
- [ ] {Regression filters that must stay green: `...`}
- [ ] Exactly ONE migration file on the branch (if any), and no merged migration edited
- [ ] `/review-branch` verdict READY TO MERGE (its `composer check` is the branch's only full gauntlet; fix everything it surfaces, re-run)
- [ ] {Any manual smoke the plan's Verification Plan asks for}
