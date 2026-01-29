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

| ID | Unit | Description | Status | Depends On |
|----|------|-------------|--------|------------|
| WU-01 | {slug} | {Brief description} | PENDING | - |
| WU-02 | {slug} | {Brief description} | PENDING | WU-01 |
| WU-03 | {slug} | {Brief description} | PENDING | WU-01 |
| WU-04 | {slug} | {Brief description} | PENDING | WU-02 |
| WU-05 | {slug} | {Brief description} | PENDING | WU-03 |

**Status Legend:**
- `PENDING` - Not started, dependencies incomplete
- `READY` - Dependencies complete, can start now
- `IN PROGRESS` - Currently being worked on
- `DONE` - Completed and verified

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

Track completion as you work:

### WU-01: {description}
- **Completed**: {DATE or "Not started"}
- **Decisions Made**: {Any decisions during implementation}
- **Notes**: {Anything notable for future reference}

### WU-02: {description}
- **Completed**: {DATE or "Not started"}
- **Decisions Made**:
- **Notes**:

{Continue for each work unit...}

---

## Completion Checklist

Before marking the feature complete:

- [ ] All work units show DONE status
- [ ] All tests passing: `php artisan test --filter={Feature}`
- [ ] PHPStan passing: `./vendor/bin/phpstan analyse`
- [ ] TypeScript check passing: `npm run type-check`
- [ ] Pre-commit checks passing

**Final verification:**
```bash
php artisan test --filter={Feature} && ./vendor/bin/phpstan analyse --level=5 && npm run type-check
```
