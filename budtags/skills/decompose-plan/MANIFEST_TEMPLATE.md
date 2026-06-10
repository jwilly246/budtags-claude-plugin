# Manifest Template

Use this template when creating a manifest for decomposed work units.

---

# {FEATURE_NAME} Implementation Manifest

**Source Plan**: `{ORIGINAL_PLAN_FILE.md}`
**Created**: {DATE}
**Status**: Not Started

## Overview

{2-3 sentences about what's being built and its business value}

---

## Work Units

> The **Description** column is used VERBATIM as the git commit subject by run-plan.
> Write each one like a commit subject: imperative mood, capitalized, no trailing
> period, no "WU-XX" references (e.g. "Create ads tables and models").

| ID | Unit | Description | Status | Depends On |
|----|------|-------------|--------|------------|
| WU-01 | {slug} | {Brief description} | PENDING | - |
| WU-02 | {slug} | {Brief description} | PENDING | WU-01 |
| WU-03 | {slug} | {Brief description} | PENDING | WU-01 |
| WU-04 | {slug} | {Brief description} | PENDING | WU-02 |
| WU-05 | {slug} | {Brief description} | PENDING | WU-03 |

**Status Legend** (run-plan's stored status model — write ONLY these four):
- `PENDING` - Not yet started
- `IN PROGRESS` - Currently being executed
- `DONE` - Completed, verified, committed
- `BLOCKED` - Failed verification, needs a fix before resuming

`READY` is **computed, never stored**: a unit is READY when its status is PENDING
and all of its dependencies are DONE. Do not write READY into the table.

---

## Dependency Graph

```
WU-01 (Database/Models)
  ├── WU-02 (Controller A) ──> WU-04 (UI A)
  │
  └── WU-03 (Controller B) ──> WU-05 (UI B)
```

## Parallel Opportunities

Work units that can run simultaneously after their dependencies:
- WU-02 and WU-03 can start in parallel after WU-01
- WU-04 and WU-05 can start in parallel after WU-02/WU-03 respectively

---

## File Manifest

### Files to Create

```
database/migrations/
  └── {timestamp}_create_{table}_table.php

app/Models/
  └── {Model}.php

app/Http/Controllers/
  └── {Feature}Controller.php

app/Http/Requests/
  └── {Action}{Feature}Request.php

resources/js/Pages/{Feature}/
  └── Index.tsx
  └── components/
      └── {Component}.tsx

tests/Unit/
  └── {Model}Test.php

tests/Feature/
  └── {Feature}ControllerTest.php
```

### Files to Modify

| File | Changes |
|------|---------|
| `routes/web.php` | Add {feature} routes |
| `app/Models/Organization.php` | Add {feature} relationship |
| `resources/js/types/index.d.ts` | Add TypeScript types |

---

## Key Decisions (from Plan)

Document important decisions from the original plan:

### Decision 1: {Title}
{Brief explanation of decision and rationale}

### Decision 2: {Title}
{Brief explanation of decision and rationale}

---

## Progress Log

Updated by run-plan after each unit's Gate Check (commit hash on DONE, failure
details on BLOCKED):

### WU-01: {description}
- **Status**: PENDING
- **Completed**: {DATE, filled by run-plan}
- **Commit**: {short hash, filled by run-plan}
- **Decisions Made**: {Any decisions during implementation}
- **Notes**: {Anything notable; on BLOCKED — which step failed, command output, fix required}

### WU-02: {description}
- **Status**: PENDING
- **Completed**:
- **Commit**:
- **Decisions Made**:
- **Notes**:

{Continue for each work unit...}

---

## Completion Checklist

Before marking the feature complete:

- [ ] All work units show DONE status
- [ ] Feature tests passing: `php artisan test --filter={Feature}`
- [ ] Full quality gauntlet green (run-plan's gate.sh runs this per-unit, but re-verify at the end)

**Final verification:**
```bash
composer check
```
