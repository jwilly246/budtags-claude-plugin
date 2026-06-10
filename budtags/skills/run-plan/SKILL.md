---
name: run-plan
description: Autonomously executes decomposed work units, committing after each successful verification, until complete or blocked. Orchestrator personally reviews each subagent's work (composer check + diff audit + SHARED_CONTEXT audit) before committing.
version: 2.0.0
category: workflow
auto_activate:
  keywords:
    - "run plan"
    - "execute plan"
    - "run work units"
    - "execute work units"
---

# Run Plan Skill

**PURPOSE:** Autonomously execute work units from a decomposed plan.

## CRITICAL RULES

```
+------------------------------------------------------------------+
|  GIT SAFETY: LOCAL COMMITS ONLY - NEVER PUSH                     |
|                                                                   |
|  OK: git checkout -b {branch}     (create local branch)          |
|  OK: git add {files}              (stage specific files)         |
|  OK: git commit -m "..."          (local commit)                 |
|                                                                   |
|  NEVER: git push                  (user pushes later)            |
|  NEVER: git push -u origin                                       |
|  NEVER: Any remote operations                                    |
+------------------------------------------------------------------+
```

```
+------------------------------------------------------------------+
|  COMMIT MESSAGE PURITY - ORCHESTRATOR WRITES EVERY LINE          |
|                                                                   |
|  NEVER prefix subject with "WU-XX:" - use MANIFEST description   |
|  NEVER include "Co-Authored-By:" trailer, ever                   |
|  NEVER include "Generated with Claude Code" line                 |
|  NEVER append any boilerplate the orchestrator did not write     |
|                                                                   |
|  OK: HEREDOC for multi-line bodies                               |
|  OK: 2-3 line body summarizing what was implemented              |
+------------------------------------------------------------------+
```

```
+------------------------------------------------------------------+
|  ORCHESTRATOR IS THE QUALITY GATE - NOT JUST THE SUBAGENTS       |
|                                                                   |
|  After every subagent returns, BEFORE committing, the            |
|  orchestrator MUST personally (in the main context):             |
|    1. Read `git diff` of subagent work; verify on-track vs WU    |
|    2. Verify SHARED_CONTEXT.md was updated; populate if skipped  |
|    3. Confirm WU task list is fully checked off                  |
|    4. Run gate.sh (mechanical: file existence, scope, stubs,     |
|       patterns, composer check) and fix ALL issues found         |
|                                                                   |
|  Do NOT delegate any of these back to a subagent.                |
|  The git invariants (no push, no bulk add, no deploy-branch      |
|  commits, no commit boilerplate) are ALSO enforced mechanically  |
|  by the plugin's git-safety.py hook - do not fight it.           |
+------------------------------------------------------------------+
```

---

## Architecture Overview

```
Orchestrator (this skill - main-context agent, does real work)
     |
     +-> Phase 0: Setup
     |      +-> Verify/create feature branch
     |      +-> Create SHARED_CONTEXT.md if missing
     |
     +-> Phase 1: Execution Loop
     |      |
     |      FOR each READY work unit (sequential review/commit):
     |      +-> Update MANIFEST: status -> IN PROGRESS
     |      +-> Parse work unit for Agent type
     |      +-> Read SHARED_CONTEXT.md, embed inline into prompt
     |      +-> Spawn subagent via Agent tool (specialist per Agent field)
     |      |      +-> Fresh context with SHARED_CONTEXT embedded inline,
     |      |          reads only the WU file, implements tasks,
     |      |          returns Completion Report incl. "Patterns Followed"
     |      +-> Orchestrator Review (main context, MANDATORY, judgment layer):
     |      |      +-> Read git diff; audit vs WU tasks/files
     |      |      +-> Audit SHARED_CONTEXT.md updates; populate if needed
     |      |      +-> Audit "Patterns Followed" substance
     |      |      +-> Confirm WU task list checked off
     |      +-> Run gate.sh (mechanical layer: files/scope/stubs/patterns/
     |      |   composer check) + WU-specific verification commands
     |      +-> Gate Check:
     |      |      +-> PASS: git commit -> MANIFEST: DONE
     |      |      +-> FAIL: MANIFEST: BLOCKED -> STOP
     |      +-> Next unit (or finish)
     |
     +-> Phase 2: Completion
            +-> Report summary (success or blocked)
```

**Execution is serial by default** (operator preference: one dispatch per message, every subagent "green" claim independently re-verified before committing). Dispatch ONE work unit's subagent, complete its full Review + Gate Check + commit, then dispatch the next. Concurrent dispatch of independent units is permitted ONLY if the user explicitly asks for it in this session — and even then, Orchestrator Review + Gate Check + commit remain **one WU at a time, sequentially**, in deterministic order. Never commit two units in one atomic step.

---

## Command Usage

```
/run-plan <directory>              # Run all READY units
/run-plan <directory> WU-03        # Run specific unit only
```

---

## Status Model

**Stored statuses** (written to MANIFEST.md):
- `PENDING` - Not yet started
- `IN PROGRESS` - Currently being executed
- `DONE` - Completed and committed
- `BLOCKED` - Failed verification, needs fix

**Computed state** (not stored):
- A unit is **READY** when: status is PENDING AND all dependencies are DONE

---

## Shared Context

Each execution subagent starts fresh. Use `{directory}/SHARED_CONTEXT.md` for cross-agent continuity.

**Setup:** If missing, create from `prompts/shared-context-template.md` in Phase 0.

**Gating model (v1.9):** SHARED_CONTEXT is NOT a file the subagent is told to Read. The orchestrator reads it and embeds the full contents inline into the spawned prompt at the `{SHARED_CONTEXT_INLINE}` placeholder. The subagent receives the patterns as part of its context window, not as a file path to follow. This eliminates the "subagent ignored the Read instruction" failure mode that motivated the change.

**Agent responsibilities:**
1. USE the embedded patterns (the agent does NOT Read SHARED_CONTEXT, it is already in their prompt)
2. FOLLOW the patterns from the embedded content
3. REFERENCE them in the mandatory "Patterns Followed" Completion Report section (with row references or quotes, falsifiable)
4. UPDATE the SHARED_CONTEXT.md file with anything they ADD (services, types, routes, decisions)

**Orchestrator responsibilities:**
1. Create from template if missing
2. READ and embed contents into the prompt before each Agent spawn (substitute `{SHARED_CONTEXT_INLINE}`)
3. AUDIT the "Patterns Followed" section for substance after each spawn (Step C of Orchestrator Review)
4. AUDIT new additions via `git diff SHARED_CONTEXT.md`
5. NEVER commit, this file stays local as working context only

---

## Phase 0: Setup

### 0.1 Branch Safety

```bash
git branch --show-current
```

If on main/master:
1. Create feature branch: `git checkout -b {feature-name}`
2. Confirm before proceeding

If on `deploy-to-staging` or `deploy-to-production`: **STOP and ask the user.** These are
deploy branches (deploy.sh switches HEAD there) — NEVER create commits on them and never
branch off them; the feature branch must come from main.

**Re-check before EVERY commit:** run `git branch --show-current` immediately before each
`git commit` in the Gate Check (1.7). A deploy or branch switch mid-run must never result
in a commit landing on the wrong branch.

### 0.2 Initialize SHARED_CONTEXT

If `{directory}/SHARED_CONTEXT.md` doesn't exist, create from template.

---

## Phase 1: Execution Loop

### 1.1 Parse Manifest

Read `{directory}/MANIFEST.md`. Find the work unit table:

```markdown
| ID | Unit | Description | Status | Depends On |
|----|------|-------------|--------|------------|
| WU-01 | database-models | Create tables and models | PENDING | - |
| WU-02 | admin-controller | Admin CRUD endpoints | PENDING | WU-01 |
```

Determine READY units: status is PENDING AND all dependencies are DONE.

**Edge cases:**

| Scenario | Action |
|----------|--------|
| No READY units, not all DONE | Report blocked state, list blockers |
| All units DONE | Report completion |
| Requested unit not READY | Report missing dependencies |

### 1.2 Update Status

Change status in MANIFEST: `PENDING -> IN PROGRESS`

### 1.3 Determine Agent Type

Parse work unit file for `**Agent**:` field:

| Agent Field Value | subagent_type |
|-------------------|---------------|
| `metrc-specialist` | `budtags:metrc-specialist` |
| `quickbooks-specialist` | `budtags:quickbooks-specialist` |
| `leaflink-specialist` | `budtags:leaflink-specialist` |
| `tanstack-specialist` | `budtags:tanstack-specialist` |
| `react-specialist` | `budtags:react-specialist` |
| `php-developer` | `budtags:php-developer` |
| `typescript-developer` | `budtags:typescript-developer` |
| `fullstack-developer` | `budtags:fullstack-developer` (default) |

### 1.4 Spawn Execution Subagent (Agent tool)

**Pre-spawn step (orchestrator, MANDATORY):**

Before calling the Agent tool (formerly named "Task" — same `subagent_type` parameter), the orchestrator personally reads `{directory}/SHARED_CONTEXT.md` and embeds its full contents into the spawned prompt at the `{SHARED_CONTEXT_INLINE}` placeholder. This is the central gating change in v1.9.

Why inline rather than asking the subagent to Read it:
1. Subagents routinely skip "Read file X" instructions, especially specialist subagents whose own auto-loaded skills (from frontmatter `skills:` field) compete for prompt priority.
2. Verifying "did the agent read it" requires transcript inspection. Verifying "is it in the prompt" is trivial.
3. The subagent's "Patterns Followed" Completion Report section becomes falsifiable: they can only reference rows they have seen, and the orchestrator can cross-check against the embedded content.

**Schema injection (for WUs that write SQL/Eloquent against existing tables):**
subagents fabricate column names that pass PHPStan but fail at SQL runtime. Before
spawning such a WU, the orchestrator verifies the relevant tables' actual columns
(laravel-boost `database-schema` MCP tool, or the table's migration) and appends a
short "## Verified Schema (orchestrator-provided)" section to the spawn prompt listing
table -> column names. Also instruct: do NOT narrow SELECTs to assumed columns.

**SHARED_CONTEXT size discipline:** the file is re-embedded into EVERY spawn. When
updating it after a WU, prune entries that no longer earn their tokens (superseded
decisions, scaffolding notes) instead of appending forever. Target: keep it under
~250 lines; the patterns that matter must not drown.

Use the Agent tool with:
- **prompt**: From `prompts/execute-unit.md`, with `{SHARED_CONTEXT_INLINE}` substituted for the actual SHARED_CONTEXT.md contents read in the pre-spawn step
- **model**: OMIT — the subagent inherits the session model, which is the strongest available. Only pass a model if the user explicitly asks for an override. (Historical `"opus"` hard-code removed: it silently downgraded execution agents once newer session models shipped.)
- **subagent_type**: From the agent type table in 1.3

### 1.5 Orchestrator Review (MANDATORY, runs in main context — do NOT delegate)

After the subagent returns a Completion Report and before running the WU's own verification, the orchestrator personally does the JUDGMENT review (the mechanical checks — file existence, scope, stubs, patterns, composer check — are gate.sh's job in 1.6; don't duplicate them by hand, and don't skip gate.sh because you eyeballed them):

**Step B: Read the diff and audit quality**

```bash
git status --short
git diff --stat
git diff
```

| Audit question | If answer is "no" |
|---|---|
| Does the diff actually implement the WU's tasks (not adjacent busywork)? | Mark BLOCKED, report drift |
| Are all files in "Modify" actually modified (gate.sh only checks Create existence)? | Mark BLOCKED, report missing modifications |
| Does the code match the pattern/style in sibling files? | If not, fix directly in main context |
| Do the tests actually assert behavior (not just "assertNotNull")? | Strengthen the tests in main context |

**Step C: Audit SHARED_CONTEXT additions AND "Patterns Followed" substance**

Two checks here. Both are required before proceeding to Step D.

**C.1 SHARED_CONTEXT additions (diff-based):**

```bash
git diff {directory}/SHARED_CONTEXT.md
```

Check the subagent updated the relevant tables:
- PHP Services & Classes (created)
- TypeScript Types (created)
- Routes Added
- Database Columns & Naming
- Implementation Decisions
- Cache Keys
- Enums Created

If the subagent skipped updating SHARED_CONTEXT for something they clearly created (e.g. they added a new service class but the table is empty), **the orchestrator populates it directly in main context** — do not send back to a subagent.

**C.2 "Patterns Followed" section substance (Completion Report based):**

Open the subagent's Completion Report and find the "Patterns Followed from Embedded Shared Context" section. Cross-check it against the SHARED_CONTEXT.md content that was embedded in the spawned prompt.

| Check | If "no" |
|-------|---------|
| Are at least 2 specific patterns listed, with row references or quotes? | Mark WU BLOCKED, log that the embedded context was likely ignored |
| Do the referenced rows actually exist in the embedded SHARED_CONTEXT? | Mark WU BLOCKED, the subagent fabricated references |
| Are the entries specific (named component / row / convention) rather than generic ("followed conventions", "used components")? | Mark WU BLOCKED, same signal as fabrication |
| Does the code in the diff actually use the patterns the subagent claims to have followed? | Mark WU BLOCKED, the report contradicts the diff |

A thin or generic "Patterns Followed" section is the **leading indicator** that the subagent ignored the embedded context. Catching it here prevents drift-prone code from reaching Verification (Layer 2), where the failure mode would be much harder to diagnose (looks like a "stylistic" miss rather than a "didn't read context" miss).

**Step D: Task-list completion check**

Open the WU file. Every `- [ ]` should be `- [x]`. If any are unchecked, either complete them in main context or mark the WU BLOCKED.

If any of Steps A–D fail irrecoverably, mark the WU BLOCKED in MANIFEST and stop. Do NOT proceed to the Verification layer.

### 1.6 Run Verification

**Step 1: THE GATE (MANDATORY — one command, runs the whole mechanical layer)**

From the project repo root:

```bash
"$HOME/.claude/plugins/marketplaces/budtags-claude-plugin/budtags/skills/run-plan/scripts/gate.sh" {directory}/WU-{N}-{slug}.md
```

gate.sh performs, in one shot: WU Files-section parsing → every Create file exists →
scope audit (tracked changes outside the declared set = FAIL; pre-existing untracked
clutter = warn only) → stub detection → frontend pattern check → `composer check`
(full gauntlet: pint, eslint, type-check, phpstan, vitest, parallel phpunit).

- Exit 0 = mechanical layer passed.
- Exit 1 = FAIL; the report lists EVERY issue (not just the first). Fix all issues in
  main context, re-run gate.sh until clean. Project rule: fix every `composer check`
  issue surfaced, not just ones this WU caused (if one looks like intentional WIP,
  stop and surface to the user).
- Exit 2 = the SCRIPT could not do its job (bad WU path, unparseable Files section,
  detector malfunction). That is a harness problem, not a code failure — report to
  the user; do NOT mark the WU BLOCKED over it.
- `--skip-composer` exists for iterating on the cheap checks; the final pre-commit
  gate.sh run must NOT use it.

**Step 2: MetrcApi set_user() Check (for PHP files touching MetrcApi)**

If any modified PHP controller files use `MetrcApi`, verify that every public controller method calls `$api->set_user()` before any API interaction. This prevents a subtle bug class where `MetrcApi::headers()` has a fallback to `request()->user()` masking the missing `set_user()`, but deeper internal methods access `$this->user` directly and crash. Queue jobs must accept User via constructor and call `$api->set_user($this->user)` in `handle()`.

**Step 3: Test Quality Check**

If the work unit includes test files, verify they follow `budtags-testing` skill principles:
- Each test method verifies ONE behavior (no bundled assertions testing multiple unrelated things)
- Tests assert outputs/behavior, not implementation details (no unnecessary spies on internal methods)
- Each test builds its own data (no shared class-property fixtures that cascade-break)
- Assertions are exact (`assertEquals`, `assertCount`) not weak (`assertNotNull`, `assertTrue` for value checks)
- PHP tests use `: void` return type and inline comments documenting each step
- PHP tests use `$this->login()->mock_api_requests()` for auth context, NOT `RefreshDatabase`
- Vitest tests use the custom `render` from `@/testing` and `screen` queries from Testing Library

**Step 4: Work Unit Verification Commands**

Parse the work unit's `## Verification` section and run each command — EXCEPT commands
fully subsumed by gate.sh's `composer check` (a bare full-suite phpstan/pint/test run).
WU-specific commands like `php artisan test --filter=X`, `php artisan migrate &&
migrate:rollback`, or targeted greps are NOT subsumed — always run those.

**Step 5: Test-DB refresh after migration WUs (KNOWN FAILURE MODE)**

If this WU added or changed a migration, the parallel test databases
(`budtags_test_1..N`) are now migration-stale, and the NEXT WU's tests will fail with
confusing schema errors that look like code bugs. After committing a migration WU:

```bash
composer migrate-test-dbs
```

If parallel tests still fail with schema errors while a single-process run passes,
drop the `budtags_test_*` databases manually (the `--recreate-databases` flag is
unreliable) and re-run. NEVER diagnose post-migration parallel-test failures as code
regressions before ruling out DB staleness.

### 1.7 Gate Check

**If both the Orchestrator Review (1.5) and Verification (1.6) passed:**

0. Branch check: `git branch --show-current` — must be the feature branch (never main or a
   `deploy-to-*` branch); if not, STOP and report
1. Stage files: `git add {files from WU "Files" section}` — enumerate explicitly, no `git add .` or `git add -A`
2. Safety: unstage any plan files that may have been caught:
   `git reset HEAD {directory}/` (unstages everything in the plan directory)
3. Commit using a HEREDOC so the body preserves newlines:

   ```bash
   git commit -m "$(cat <<'EOF'
   {Work unit description from MANIFEST table, verbatim — NO "WU-XX:" prefix}

   {2-3 line summary of what was implemented}
   EOF
   )"
   ```

   **Forbidden in the commit message** (enforced by CRITICAL RULES box above):
   - No `WU-01:` or `WU-{N}:` or any work-unit-identifier prefix on the subject
   - No `Co-Authored-By:` trailer line
   - No `🤖 Generated with Claude Code` line
   - No other boilerplate the orchestrator did not explicitly write

4. Update MANIFEST: status -> DONE
5. Update MANIFEST Progress Log section
6. **Propagate as-built facts downstream**: read the finished WU's "Notes for Next Unit"
   and "Decisions Made"; apply anything that changes a DOWNSTREAM WU's assumptions
   (final signatures, renamed files, changed approach) directly into those WU files'
   Required Context / Tasks. Stale WU files are how later subagents re-implement
   against assumptions that no longer hold.
7. Continue to next READY unit

**If either review (1.5) or verification (1.6) failed:**

**Bounded retry (exactly one):** if the failure looks like a fixable implementation
miss (failed test, missed task, stub) rather than a plan defect, the orchestrator may
re-spawn the SAME work unit ONCE, embedding the verbatim failure output and what must
change into the new prompt. Small fixes (a few lines) are faster to apply directly in
main context — prefer that. If the retry also fails, or the failure indicates the WU
itself is wrong (missing dependency, wrong assumption about the codebase):

1. Update MANIFEST: status -> BLOCKED
2. Update MANIFEST Progress Log with failure details (which step failed, the command output, the fix required)
3. STOP immediately — do not attempt the next unit
4. Report failure details to the user

---

## Phase 2: Completion

### Success Report

```
## Run Complete: {DIRECTORY}

All work units completed successfully.

### Commits Created (local)
- abc1234: Create database tables and models
- def5678: Admin CRUD endpoints

### Final Verification
All tests passing, PHPStan clean, Pint formatted.

Commits are local. When ready: git push -u origin {branch}
```

### Blocked Report

```
## Run Stopped: {DIRECTORY}

BLOCKED at WU-{N}: {description}

### Failure Details
Command: ./vendor/bin/phpstan analyse app/Models/Ad.php
Exit code: 1
Output:
{error output}

### Progress
- [DONE] Create database tables and models (abc1234)
- [BLOCKED] Admin CRUD endpoints
- [PENDING] Admin UI components

### To Resume
1. Fix the issues reported above
2. Run: /run-plan {DIRECTORY} WU-{N}

Commits are local. Do not push until issues resolved.
```

---

## MANIFEST Structure

The MANIFEST.md should include a Progress Log section:

```markdown
## Progress Log

### WU-01: database-models
- **Status**: DONE
- **Completed**: 2026-01-27
- **Commit**: abc1234
- **Notes**: All tests passing

### WU-02: admin-controller
- **Status**: BLOCKED
- **Failed**: 2026-01-27
- **Reason**: PHPStan error on line 45
```

---

## Rollback Guidance

If execution fails partway through:

1. **Committed work units stay committed** - they passed verification
2. **BLOCKED unit needs manual fix** - user fixes, then resumes
3. **To undo a committed unit** (if needed):
   ```bash
   git reset --soft HEAD~1  # Undo last commit, keep changes staged
   git reset HEAD           # Unstage changes
   ```
4. **To restart from scratch**:
   ```bash
   git checkout main
   git branch -D {feature-branch}
   ```
   Then update MANIFEST statuses back to PENDING.

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Verification fails | Mark BLOCKED, stop, report failure details |
| Subagent errors | Mark BLOCKED, stop, report agent error |
| Git commit fails | Stop, report git error, don't update MANIFEST |
| File not found | Report missing file, suggest resolution |
| No READY units | Report blocked dependencies or completion |

---

## Files Section Parsing

Work units have a Files section:

```markdown
## Files

### Create
- `app/Models/Ad.php` - Ad model
- `database/migrations/2026_01_27_000001_create_ads_table.php`

### Modify
- `app/Models/Organization.php` - Add ads relationship
```

Use this to:
1. Know what files the agent should create/modify
2. Stage the correct files for commit
3. Verify files exist after agent completes

---

## Anti-Patterns

- Pushing to remote (NEVER — also mechanically asked/denied by git-safety.py)
- Running all verifications after all units (gate each unit)
- Continuing after a failure (one bounded retry is allowed; a second failure = BLOCKED + stop)
- Skipping verification commands
- Skipping gate.sh, or hand-waving its checks because you "already eyeballed the diff"
- Marking a WU BLOCKED on gate.sh exit 2 (that's a harness malfunction — report it instead)
- Diagnosing post-migration parallel-test failures as code bugs before refreshing test DBs
- **Skipping Orchestrator Review (1.5)** — agents do not self-review; the orchestrator must
- **Delegating composer check to a subagent** — it runs in main context, issues fixed in main context
- **Committing with "WU-XX:" prefix** on the subject line — use MANIFEST description as-is
- **Adding "Co-Authored-By:" or "Generated with Claude Code"** lines to commit messages
- Using --force or --amend git flags
- Committing unrelated files
- Committing plan files (MANIFEST.md, WU-*.md, SHARED_CONTEXT.md, plan directory files)
- Using `git add .` or `git add -A` (always stage specific files only)
- Accepting incomplete implementations from agents
- Trusting that SHARED_CONTEXT.md was updated without verifying the diff
- **Spawning an execution subagent without embedding SHARED_CONTEXT inline** (since v1.9, the orchestrator MUST read the file in the pre-spawn step and substitute `{SHARED_CONTEXT_INLINE}` in the prompt; never rely on the subagent to Read it themselves)
- **Telling the subagent to Read SHARED_CONTEXT.md** (since v1.9, the file is embedded in the prompt; asking the agent to Read it is wasted tool calls and signals the orchestrator skipped the pre-spawn step)
- **Accepting a thin or generic "Patterns Followed" section** in the Completion Report (it is the leading indicator that the embedded context was ignored; treat fabricated row references the same way)

---

## Correct Behavior

- Create feature branch if on main
- Execute one unit at a time in fresh context, serially — dispatch the next subagent only after the previous WU is reviewed and committed (parallel dispatch only on explicit user request)
- **Run Orchestrator Review (1.5) BEFORE the WU's own verification** — diff audit, SHARED_CONTEXT audit, patterns-substance audit, task-list check
- **Run gate.sh for every WU** and fix ALL issues it reports in main context — not via subagent
- **Populate SHARED_CONTEXT.md in main context** if the subagent left relevant tables empty
- **Inject verified schema** into spawn prompts for DB-touching WUs (subagents fabricate columns)
- **Refresh parallel test DBs after migration WUs** (`composer migrate-test-dbs`; drop `budtags_test_*` manually if still stale)
- **Propagate "Notes for Next Unit" into downstream WU files** after each commit
- Run all WU-specific verification commands for each unit (skip only ones gate.sh's composer check fully subsumes)
- **Commit with the MANIFEST description verbatim** — no WU-XX prefix
- **Commit with 2-3 line body describing what was implemented** — no Co-Authored-By, no auto-attribution
- Commit immediately after each success
- Stop immediately on any failure
- Update MANIFEST status throughout
- Report clear summary at end
- Verify no plan directory files are staged before committing
- Remind user commits are local
- **Read SHARED_CONTEXT.md in the orchestrator before each Agent spawn** and embed its full contents into the prompt at the `{SHARED_CONTEXT_INLINE}` placeholder (v1.9)
- **Audit the subagent's "Patterns Followed" section for substance** as part of Orchestrator Review Step C.2 (v1.9)
