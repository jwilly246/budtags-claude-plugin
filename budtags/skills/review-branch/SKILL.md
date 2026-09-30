---
name: review-branch
description: Pre-merge branch review. Invoke before merging any branch to main. Auto-detects what changed, runs deterministic quality gates, then performs domain-specific code review using BudTags patterns. Replaces manual review checklists.
version: 1.1.0
category: project
auto_activate:
  keywords:
    - "review branch"
    - "review-branch"
    - "pre-merge"
    - "before merge"
    - "ready to merge"
    - "merge review"
    - "branch review"
    - "review before merging"
    - "review my branch"
    - "check my branch"
---

# Pre-Merge Branch Review

You are conducting a comprehensive pre-merge review of the current branch. This skill replaces long typed review messages with a structured, repeatable process.

**Philosophy**: Deterministic gates first (cheap, fast, pass/fail), then AI-powered review (targeted to what actually changed).

**Role in the workflow**: this skill is THE end-of-branch gate. The repo's pre-commit hook covers each commit (Pint + PHPStan on the staged PHP files) and run-plan's `gate.sh` covers each unit (scope, stubs, patterns, targeted tests); neither runs the full gauntlet. Phase 2 below is the ONE `composer check` a branch gets, so it is never skipped here and never duplicated earlier. run-plan invokes this skill automatically after its last unit; a human invokes it before any merge to main.

---

## Phase 1: SCOPE

Determine what changed on this branch compared to main.

**Run these commands:**

```bash
# What branch are we on?
git branch --show-current

# Changed files summary
git diff main...HEAD --stat

# Full diff for review (read key files, don't dump everything)
git diff main...HEAD --name-only

# Commit history on this branch
git log main..HEAD --oneline
```

**Classify domains touched** based on changed files:

| File Pattern | Domain |
|---|---|
| `database/migrations/*` | DATABASE |
| `app/Models/*` | DATABASE |
| `app/Http/Controllers/*` | BACKEND |
| `app/Http/Requests/*` | BACKEND |
| `app/Services/*` | BACKEND |
| `routes/web.php` | BACKEND |
| `resources/js/Pages/*` | FRONTEND |
| `resources/js/Components/*` | FRONTEND |
| `resources/js/Types/*` | FRONTEND |
| `resources/js/Hooks/*` | FRONTEND |
| `app/**/Metrc*`, `app/**/metrc*` | METRC_INTEGRATION |
| `app/**/QuickBooks*`, `app/**/quickbooks*` | QUICKBOOKS_INTEGRATION |
| `app/**/LeafLink*`, `app/**/leaflink*` | LEAFLINK_INTEGRATION |
| `app/**/Unleashed*`, `app/**/unleashed*` | UNLEASHED_INTEGRATION |
| `tests/Feature/*` | TESTING |
| `tests/Unit/*` | TESTING |
| `tests/js/*`, `**/*.test.tsx` | TESTING |

Report the domains detected before proceeding.

---

## Phase 2: GATES (deterministic, pass/fail)

Run quality gates. If any fail, report failures and STOP — no point in AI review if the basics don't pass.

Never run this in the shared main tree while the user or another agent is working there: it holds the tree for minutes. Use an isolated worktree (the `worktree` skill), one gauntlet at a time. Exception: the user says no worktree, then run it in the main tree and check `git reflog` afterwards.

```bash
composer check
```

(Inside a git worktree prefix it with that worktree's database: `DB_DATABASE=budtags_<slug>_test composer check`. Never pipe it through `| tail`; the exit code is the result.)

This runs in order (see `composer.json` `scripts.check`):
1. Pint (PHP formatting)
2. npm lint (ESLint)
3. npm type-check (tsc)
4. PHP abbreviation check (`scripts/check-php-abbreviations.php`)
5. PHPStan level 10 (static analysis)
6. npm test (Vitest)
7. PHPUnit (parallel, 14 processes)

**If any gate fails:**
- Report which gate failed and the error output
- List the specific files/lines that need fixing
- Invoked by run-plan (end of a `/run-plan` run): the orchestrator fixes EVERYTHING surfaced in main context (pre-existing issues included; intentional WIP gets surfaced to the user instead), commits the fixes with whole-file commits and imperative subjects, and re-runs this skill from Phase 1
- Invoked by a human: STOP here — do not proceed to Phase 3 until the gates pass

Known non-code failure: PHPStan's result cache goes stale across branch switches AND after merging main into a branch and reports phantom `method.notFound` / `property.notFound` on trait-provided members in files the branch never touched. Run `vendor/bin/phpstan clear-result-cache` and re-run before treating those as defects.

**If all gates pass:** Proceed to Phase 3.

---

## Phase 3: DOMAIN REVIEW

For each domain detected in Phase 1, load the relevant verify-alignment patterns and check the diff against them. Read the pattern files listed below — do NOT guess at patterns from memory.

### DATABASE domain

**Read:** `../verify-alignment/patterns/database.md`

**Check:**
- [ ] New migrations include `organization_id` foreign key where applicable
- [ ] Proper indexes on foreign keys and frequently queried columns
- [ ] Single migration per branch (not multiple migration files)
- [ ] New models use `HasOrganization` trait
- [ ] Model `$casts` array properly typed
- [ ] Factory includes `forOrganization` state
- [ ] UUIDs used for primary keys (BudTags standard)

### BACKEND domain

**Read:** `../verify-alignment/patterns/backend-critical.md`, `../verify-alignment/patterns/backend-style.md`, `../verify-alignment/patterns/php8-brevity.md`

**Check:**
- [ ] All queries scoped to `request()->user()->active_org`
- [ ] Method names are `snake_case` verb-first (`fetch_all`, `create`, `delete` — not `index`, `store`, `destroy`)
- [ ] Uses `request()` helper, not injected `$request`
- [ ] Uses `LogService::store()`, not `Log::info()` or `Log::error()`
- [ ] Flash messages use `'message'` key, not `'success'`
- [ ] No premature constants — inline strings unless used 3+ times across files
- [ ] PHP 8 brevity: `??`, `?->`, `fn()`, `match()` where appropriate
- [ ] Form requests used for validation on create/update endpoints
- [ ] Functional style: `map`/`filter`/`reduce`/`keyBy`/`mapWithKeys`/`sum`/`groupBy`, never `foreach` to build data (accumulator var + loop = violation)
- [ ] No if/else that only assigns a variable — ternary / `match()` / `??` instead
- [ ] Guard clauses (early returns) for preconditions, never nested if pyramids
- [ ] Full descriptive variable names, no abbreviations

**If flash messages/redirects involved:**
**Read:** `../verify-alignment/patterns/backend-flash-messages.md`

### FRONTEND domain

**Read:** `../verify-alignment/patterns/frontend-critical.md`, `../verify-alignment/patterns/frontend-typescript.md`

**Check:**
- [ ] Forms use Inertia `useForm` — never `useState` for form fields, never `axios`/`fetch`
- [ ] Modals are self-contained (own form state, own submit handler)
- [ ] Types defined in `Types/` files — never inline in hooks or components, never re-exported. **HIGH**, not medium: every `export type|interface|enum` the branch adds outside `resources/js/Types/` must move to its domain type file before merge. Scan:
  ```bash
  git diff main...HEAD -- resources/js ':!resources/js/Types' ':!**/__tests__/**' ':!resources/js/testing/**' | grep -nE '^\+export (type|interface|enum) '
  ```
- [ ] No `as any` or `: any` type assertions
- [ ] No `useEffect` for syncing refs/values — reorganize code instead
- [ ] Functional style: `map`/`filter`/`reduce`/`flatMap`/`Object.fromEntries`, never `for`/`forEach` + `push` to build data
- [ ] No `let` + if/else branch assignment — ternary or lookup object, then `const`; early returns for handler preconditions
- [ ] No abbreviated variable names
- [ ] `AuthenticatedLayout` + `Head` on all pages

**If data fetching involved:**
**Read:** `../verify-alignment/patterns/frontend-data-fetching.md`

**Check React Query vs Inertia decision:**
- Inertia (useForm + router) for: forms, CRUD, navigation, page data
- React Query for: polling, dashboards, inline editing, data that refreshes without navigation

### METRC_INTEGRATION domain

**Read:** `../verify-alignment/patterns/integrations.md`

**Check:**
- [ ] `$api->set_user()` called before any API interaction in controllers
- [ ] Queue jobs accept `User` in constructor and call `$api->set_user($this->user)`
- [ ] Error handling follows Metrc patterns (graceful degradation, logging)
- [ ] API responses properly validated before use

### QUICKBOOKS_INTEGRATION, LEAFLINK_INTEGRATION, UNLEASHED_INTEGRATION domains

**Read:** `../verify-alignment/patterns/integrations.md`

**Check:**
- [ ] Service pattern followed (dedicated service class)
- [ ] Organization-scoped API credentials
- [ ] Proper error handling and logging

### TESTING domain

**Check:**
- [ ] Each test verifies ONE behavior (no bundled assertions testing multiple things)
- [ ] Each test builds its own data (no shared fixtures across tests)
- [ ] Assertions are exact: `assertEquals`, `assertCount` — not weak `assertNotNull`, `assertTrue`
- [ ] PHP tests use `: void` return type
- [ ] PHP tests use `$this->login()->mock_api_requests()` for auth setup — NOT `RefreshDatabase`
- [ ] Organization scoping tested: both inclusion AND exclusion (data from other orgs not visible)
- [ ] Vitest tests use custom `render` + `screen` queries

### ALWAYS CHECK (all domains)

- [ ] No stubs: `TODO`, `FIXME`, empty method bodies, `throw new \Exception('Not implemented')`
- [ ] No N+1 queries (use `->with()` eager loading)
- [ ] No hardcoded secrets or API keys
- [ ] New routes have proper middleware (auth, permission checks)
- [ ] No `console.log` or `dd()` or `dump()` left in code

---

## Phase 4: SECURITY SCAN

Regardless of domain, always check:

- [ ] **Organization scoping**: No cross-tenant data leaks. Every query that returns user-facing data must scope to `active_org`
- [ ] **Auth on routes**: New routes use `auth` middleware and appropriate permission checks
- [ ] **Input validation**: New endpoints validate user input (FormRequest or inline validation)
- [ ] **No mass assignment**: Models use `$fillable` or `$guarded`
- [ ] **File uploads**: If present, validated for type/size, stored in proper location

---

## Phase 5: REPORT

Generate a structured report. Use this exact format:

```markdown
## Branch Review: {branch-name}

**Commits**: {count} commits ({first}..{last})
**Files Changed**: {count}
**Domains**: {list of detected domains}
**Gates**: PASSED / FAILED at {gate name}

---

### CRITICAL (must fix before merge)
{numbered list with file:line references, or "None found"}

### HIGH (should fix before merge)
{numbered list with file:line references, or "None found"}

### MEDIUM (fix when convenient)
{numbered list with file:line references, or "None found"}

### SUGGESTIONS
{numbered list, or "None"}

---

**Verdict**: READY TO MERGE / NEEDS FIXES ({count} critical, {count} high)
```

**Severity guidelines:**
- **CRITICAL**: Security issues (missing org scoping, auth bypass), data corruption risks, broken functionality
- **HIGH**: Pattern violations that affect maintainability (wrong method names, Log facade instead of LogService, imperative style: foreach/forEach+push building data, if/else assignment instead of ternary/match, nested if pyramids instead of guard clauses, an exported TypeScript type declared outside `resources/js/Types/`)
- **MEDIUM**: Style issues, missing test edge cases, minor type safety gaps
- **SUGGESTION**: Opportunities for improvement, not blocking

---

## After the Report

1. If NEEDS FIXES: fix EVERY finding, all severities (CRITICAL through SUGGESTION), in one pass. Never trim the list to "confirmed damage" or ask which ones to fix. Only a finding that needs a business decision goes back to the user, with a recommended answer
2. If READY TO MERGE: Confirm the branch is clean and ready
3. Always note: "Run `/review-branch` again after fixes to verify"

---

## Your Mission

Conduct a thorough, structured pre-merge review that catches the issues the developer would manually check for. Be specific with file:line references. Don't pad the report with generic advice — only report actual findings from the diff. If the code is clean, say so and keep the report short.
