---
name: fix
description: Lightweight bug fix workflow for ad-hoc issues that don't warrant full plan/decompose/run. Enforces investigate → implement → verify flow. Use when fixing a bug, resolving an error, or making a targeted correction.
version: 1.1.0
category: project
auto_activate:
  keywords:
    - "fix bug"
    - "fix issue"
    - "quick fix"
    - "bug fix"
    - "fix this"
    - "fix error"
    - "resolve error"
    - "hotfix"
---

# Lightweight Bug Fix

You are fixing a bug or resolving an issue using a structured but lightweight workflow. This is for ad-hoc fixes that don't need the full create-plan → decompose-plan → run-plan pipeline.

**When to use this skill:** Single bugs, error fixes, targeted corrections, small behavioral changes.
**When NOT to use this skill:** New features, multi-file refactors, anything requiring database migrations or new pages. Use `/create-plan` for those.

## Urgent mode

If the user says urgent, a customer is blocked, or prod is down (OOM, 500s, orders not syncing): skip the ceremony. No worktree, no plan doc, no decomposition, no side work. Diagnose on prod, unblock the customer with a data patch first (through the `backfill` skill's dry-run, then apply), then make the code fix on a branch. Every tool call serves the incident.

---

## Phase 1: INVESTIGATE

Before writing any code, understand the problem.

**1.1 Gather information:**
- What is the bug? (user description, error message, unexpected behavior)
- Can you reproduce it? (check logs, trace the code path)
- Where in the code does this happen? (search for relevant files)

**1.2 Use available tools:**
- `mcp__laravel-boost__last-error` — check recent Laravel error logs
- `mcp__laravel-boost__read-log-entries` — search log entries
- `mcp__laravel-boost__browser-logs` — check browser console errors
- `mcp__laravel-boost__database-query` — verify data state if relevant
- Grep for the error message, function name, or route

**1.3 Identify root cause:**
- Trace the code path from entry point to failure
- Read the relevant files fully — don't guess from function names
- State the root cause clearly before proceeding

**1.4 Falsify before you fix (adversarial probe):**
Before touching code, try to DISPROVE your own root cause with one live probe whose output would look DIFFERENT if the diagnosis is wrong:

- A DB query (`mcp__laravel-boost__database-query`), a tinker call, a log search, or a targeted grep proving the code path actually executes the way you claim
- Show the raw probe output in the conversation — not a paraphrase
- If the probe contradicts the diagnosis, go back to 1.3. Do not implement a fix for a disproven cause.

Skip this only when the root cause is directly visible in the failing line itself (a typo, a null deref proven by the stack trace). A plausible story about an API's behavior, data shape, or timing is exactly the kind of claim that has been wrong before — probe it.

**1.5 State your reading, then your fix approach:**
When the request uses a domain term that could mean two things ("method", "cost", "line", "source") or touches which system owns a value (LeafLink, Distru, Metrc, Budtags), first state your interpretation in ONE line: "Reading 'method' as the mixed material field, not Metrc's Method column." If a wrong reading means rework, ask with AskUserQuestion before building.

Then a brief statement (2-3 sentences max) of what you'll change and why. Change only what was asked: add a variant or option instead of changing a shared component's default.

**If the root cause is unclear or the fix touches more than 3-4 files:** Stop and tell the user this may need `/create-plan` instead.

---

## Phase 2: IMPLEMENT

Make the fix directly. No agents, no work units, no MANIFEST.

**Follow BudTags patterns:**
- Organization scoping on all queries
- `snake_case` method names
- `LogService::store()` for logging
- `request()` helper, not `$request`
- Flash messages with `'message'` key
- Functional style (`map`/`filter`), not `foreach` to build data
- Full descriptive variable names, no abbreviations
- Inertia `useForm` for any form mutations
- Types in `Types/` files, not inline

**Include tests:**
- Add or update tests for the fixed behavior
- Each test verifies one behavior
- Self-contained data setup (no shared fixtures)
- Exact assertions (`assertEquals`, `assertCount`)
- PHP tests: `$this->login()->mock_api_requests()`, NOT `RefreshDatabase`
- Test both the fix (it works now) and the original bug condition (it fails correctly)

---

## Phase 3: VERIFY

The gate matches the size of the fix. The full `composer check` gauntlet belongs to `review-branch` at the end of a branch, in a worktree, never in the shared main tree.

- **Every fix:** the pre-commit hook (Pint + PHPStan on staged PHP), plus the tests for the files you touched: `php artisan test --filter=<TestClass>` and/or `npx vitest run <path>`. Frontend: `npm run type-check` and `npx eslint <files>`.
- **Small UI fix the user deploys from the main tree:** targeted tests + the hook ARE the gate.
- **Anything touching shared services, migrations, or sync/write paths:** hand off to `review-branch` for the full gauntlet.

Vitest deletes `public/hot` on exit. Only if vite is actually running on :5173 (`lsof -i :5173`), restore it with `printf 'http://127.0.0.1:5173' > public/hot`. If vite is not running, leave it deleted: a stale `public/hot` breaks the page.

**If any check fails:** Fix the issue and re-run. Do not skip.

**After checks pass, verify:**
- [ ] The original bug is fixed (the behavior described by the user works correctly)
- [ ] No stubs left (`TODO`, `FIXME`, empty methods)
- [ ] No `console.log`, `dd()`, `dump()` left in code
- [ ] No unrelated changes snuck in

---

## Report

After verification passes, provide a brief summary:

```markdown
## Fix Summary

**Bug**: {one-line description of the issue}
**Root Cause**: {what was wrong}
**Fix**: {what was changed}
**Files Modified**: {list}
**Tests**: {added/updated, count}
**Verification**: {exact commands run} PASSED
```

Do NOT commit automatically — the user will commit when ready.

---

## Your Mission

Fix the bug thoroughly but minimally. Don't refactor surrounding code, don't add features, don't clean up things that aren't broken. Fix the bug, add tests, verify, report. That's it.
