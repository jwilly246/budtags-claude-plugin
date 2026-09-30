---
name: run-plan
description: Autonomously executes decomposed work units. Units are branch-sized builder briefs; the builder commits once per task (the repo's pre-commit hook runs Pint + PHPStan on the staged PHP files); the orchestrator reviews each unit's commit range (gate.sh + diff audit + SHARED_CONTEXT audit) and the ONE full quality gauntlet runs at the end of the branch through review-branch. Never composer check in between.
version: 3.0.0
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
|  COMMIT MESSAGE PURITY                                           |
|                                                                   |
|  Subject = the task line's bold text, verbatim (task-per-commit  |
|  units), or the MANIFEST Description, verbatim (legacy units)    |
|  NEVER prefix the subject with "WU-XX:"                          |
|  NEVER include "Co-Authored-By:" (git-safety.py denies it)       |
|  NEVER include "Generated with Claude Code" (denied as well)     |
|  NEVER append boilerplate nobody wrote                           |
|                                                                   |
|  OK: HEREDOC for multi-line bodies                               |
|  OK: 2-3 line body summarizing what the commit implements        |
+------------------------------------------------------------------+
```

```
+------------------------------------------------------------------+
|  THE GATES: PER COMMIT, PER UNIT, PER BRANCH.                    |
|  NEVER `composer check` IN BETWEEN.                              |
|                                                                   |
|  Per COMMIT (builder): the repo's Husky pre-commit hook runs     |
|    Pint + PHPStan on the staged PHP files automatically. It does |
|    NOT cover TypeScript, so before a TS commit the builder runs  |
|    vitest on the touched dirs + eslint on the changed files.     |
|    Plus the task's own targeted tests, in the same commit.       |
|  Per UNIT (orchestrator, main context, MANDATORY):              |
|    1. gate.sh {WU} --since {unit start}  (Create files exist,   |
|       range + working-tree scope audit, stubs, frontend         |
|       patterns, exported types outside resources/js/Types/)     |
|       - fix ALL findings in main context                        |
|    2. Read the unit's commit-range diff; audit vs the WU         |
|    3. Audit SHARED_CONTEXT.md; populate if the builder skipped   |
|    4. Confirm every task is checked off AND committed            |
|    5. Run the WU's Verification block (targeted commands only)   |
|  Per BRANCH (ONCE, after the LAST unit): invoke review-branch.   |
|    Its Phase 2 `composer check` is the ONLY full gauntlet in     |
|    the run. Fix everything it surfaces, re-run until READY.      |
|                                                                   |
|  Do NOT delegate the unit review to a subagent.                  |
|  The git invariants (no push, no bulk add, no deploy-branch      |
|  commits, no commit boilerplate) are ALSO enforced mechanically  |
|  by the plugin's git-safety.py hook - do not fight it.           |
+------------------------------------------------------------------+
```

---

## Execution Contract (v3.0)

A work unit is a **branch-sized builder brief**: one review boundary, 5-20 tasks, each
task one commit. The builder executes the whole unit in one run and commits after
every task. The orchestrator reviews the unit's commit range at unit end. The full
quality gauntlet runs once per branch, at the very end, through `review-branch`.

Two commit modes exist because older decompositions are still on disk:

| The WU file's Tasks heading | Mode | Who commits | When |
|-----------------------------|------|-------------|------|
| `## Tasks (one commit each)` (decompose-plan >= 4.0) | task-per-commit | the builder, after each task | per task |
| plain `## Tasks` (older decompositions) | legacy single-commit | the orchestrator, after the unit passes review | per unit |

Detect the mode from the WU file before spawning; the spawned prompt carries the
same rule so the builder reads it off the file too. In BOTH modes:
- No `composer check` between commits or units. Per-file Pint + PHPStan come from
  the pre-commit hook; targeted tests ride with each commit.
- The end of the branch is `review-branch`, nothing else.

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
     |      FOR each READY work unit (sequential review):
     |      +-> Update MANIFEST: status -> IN PROGRESS
     |      +-> Record UNIT_START=$(git rev-parse HEAD)
     |      +-> Parse work unit for Agent type + commit mode
     |      +-> Read SHARED_CONTEXT.md, embed inline into prompt
     |      +-> Spawn subagent via Agent tool (specialist per Agent field)
     |      |      +-> Fresh context with SHARED_CONTEXT embedded inline,
     |      |          reads only the WU file, implements the tasks,
     |      |          commits after each task (task-per-commit mode),
     |      |          returns Completion Report incl. "Patterns Followed"
     |      +-> Orchestrator Review (main context, MANDATORY, judgment layer):
     |      |      +-> Read git log/diff UNIT_START..HEAD; audit vs WU tasks/files
     |      |      +-> Audit SHARED_CONTEXT.md updates; populate if needed
     |      |      +-> Audit "Patterns Followed" substance
     |      |      +-> Confirm WU task list checked off and committed
     |      +-> Run gate.sh --since UNIT_START (mechanical layer: files/scope/
     |      |   stubs/patterns; NO composer check) + WU Verification block
     |      +-> Gate Check:
     |      |      +-> PASS: MANIFEST: DONE (+ branch tip)
     |      |      |        (legacy mode: stage + commit first)
     |      |      +-> FAIL: fix in main context / one bounded retry /
     |      |               else MANIFEST: BLOCKED -> STOP
     |      +-> Next unit (or finish)
     |
     +-> Phase 2: End of branch
            +-> Invoke review-branch (the ONE composer check + domain review)
            +-> Fix what it surfaces (commits), re-run until READY TO MERGE
            +-> Report summary (success or blocked)
```

**Execution is serial by default** (operator preference: one dispatch per message, every subagent "green" claim independently re-verified before the unit is marked DONE). Dispatch ONE work unit's subagent, complete its full Review + Gate Check, then dispatch the next. Concurrent dispatch of independent units is permitted ONLY if the user explicitly asks for it in this session — and even then, Orchestrator Review + Gate Check remain **one WU at a time, sequentially**, in deterministic order.

---

## Command Usage

```
/run-plan <directory>              # Run all READY units, then review-branch
/run-plan <directory> WU-03        # Run specific unit only (no end-of-branch review)
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
4. AUDIT new additions via `git diff`
5. NEVER commit, this file stays local as working context only

---

## Phase 0: Setup

### 0.1 Branch Safety

```bash
git branch --show-current
```

If on main/master:
1. Create feature branch: `git checkout -b {feature-name}` (from `origin/main` with `--no-track` when the MANIFEST says so)
2. Confirm before proceeding

If on `deploy-to-staging` or `deploy-to-production`: **STOP and ask the user.** These are
deploy branches (deploy.sh switches HEAD there) — NEVER create commits on them and never
branch off them; the feature branch must come from main.

**Re-check before EVERY orchestrator commit:** run `git branch --show-current` immediately
before any `git commit` the orchestrator makes (legacy-mode unit commits, fix commits after
a review). A deploy or branch switch mid-run must never result in a commit landing on the
wrong branch. The builder's per-task commits are covered by git-safety.py's deploy-branch
denial.

### 0.2 Initialize SHARED_CONTEXT

If `{directory}/SHARED_CONTEXT.md` doesn't exist, create from template.

### 0.2b Where the run lives

A run holds its tree for hours. Run it in an isolated worktree (`worktree` skill), never
the shared main tree, unless the user explicitly says no worktree. At the end, remove
finished worktrees you created and confirm with `git worktree list` that the main tree is
free and still on the branch the user left it on.

### 0.3 Working tree hygiene

`git status --short`. Any pre-existing uncommitted change to a tracked file that belongs to
no unit will fail every unit's scope audit. Stash it (`git stash push <file>`) and note it
in the MANIFEST; never sweep it into a unit's commit.

---

## Phase 1: Execution Loop

### 1.1 Parse Manifest

Read `{directory}/MANIFEST.md`. Find the work unit table:

```markdown
| ID | Unit | Description | Status | Depends On |
|----|------|-------------|--------|------------|
| WU-01 | prefactor | Extract the shared cores the feature builds on | PENDING | - |
| WU-02 | server-core | Create mapped Metrc items from a product | PENDING | WU-01 |
```

Determine READY units: status is PENDING AND all dependencies are DONE.

**Edge cases:**

| Scenario | Action |
|----------|--------|
| No READY units, not all DONE | Report blocked state, list blockers |
| All units DONE | Run Phase 2 (end of branch) if not yet done, then report completion |
| Requested unit not READY | Report missing dependencies |

### 1.2 Update Status and record the unit start

Change status in MANIFEST: `PENDING -> IN PROGRESS`.

```bash
UNIT_START=$(git rev-parse HEAD)
```

Write it into the unit's Progress Log entry (`Started at: <sha>`). Every review command
below is relative to it, and it is the rollback anchor for the unit.

### 1.3 Determine Agent Type and commit mode

Parse the work unit file for `**Agent**:`:

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

Then the commit mode from the Tasks heading (see Execution Contract): `## Tasks (one commit
each)` = task-per-commit; plain `## Tasks` = legacy single-commit.

### 1.4 Spawn Execution Subagent (Agent tool)

**Pre-spawn step (orchestrator, MANDATORY):**

Before calling the Agent tool, the orchestrator personally reads `{directory}/SHARED_CONTEXT.md` and embeds its full contents into the spawned prompt at the `{SHARED_CONTEXT_INLINE}` placeholder. This is the central gating change in v1.9.

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

**Gate false-positive prevention:** tell the builder up front to avoid the stub
detector's banned comment words (`temporary`, `placeholder`, `stub`, `implement later`)
and single-line empty `{}` bodies, and to keep `axios` calls out of component files
(data-layer modules only). It saves a gate round-trip at unit end.

**SHARED_CONTEXT size discipline:** the file is re-embedded into EVERY spawn. When
updating it after a WU, prune entries that no longer earn their tokens (superseded
decisions, scaffolding notes) instead of appending forever. Target: keep it under
~250 lines; the patterns that matter must not drown.

Use the Agent tool with:
- **prompt**: From `prompts/execute-unit.md`, with `{SHARED_CONTEXT_INLINE}` substituted for the actual SHARED_CONTEXT.md contents read in the pre-spawn step
- **model**: OMIT — the subagent then runs on the model declared in its agent definition frontmatter (`model: opus` on every specialist in the 1.3 table). This split is deliberate (decided 2026-08-25): the session model (Fable-tier) is reserved for orchestration — spawning, diff review, gating, SHARED_CONTEXT curation — and is never spent on execution; Opus executes. Do NOT pass the session model explicitly to a spawn. If a WU ever maps to a built-in agent type with no frontmatter model (e.g. `general-purpose`), pass `model: "opus"` explicitly — built-ins otherwise inherit the session model. Only deviate if the user asks for an override.
- **subagent_type**: From the agent type table in 1.3

### 1.5 Orchestrator Review (MANDATORY, runs in main context — do NOT delegate)

After the subagent returns a Completion Report and before running the WU's own verification, the orchestrator personally does the JUDGMENT review (the mechanical checks — file existence, scope, stubs, patterns — are gate.sh's job in 1.6; don't duplicate them by hand, and don't skip gate.sh because you eyeballed them):

**Step A: Read the commit range**

```bash
git log --oneline $UNIT_START..HEAD
git status --short
git diff --stat $UNIT_START..HEAD
git diff $UNIT_START..HEAD
```

(Legacy single-commit units have an empty range; review the working tree with
`git diff` / `git diff --stat` instead.)

| Audit question | If answer is "no" |
|---|---|
| Task-per-commit mode: is there exactly one commit per task, with the task line's bold text as the subject, and nothing left uncommitted? | Squash/split is NOT allowed; if a task is uncommitted, commit it (whole files) in main context; if commits are mislabeled, note it in the Progress Log and continue (never amend) |
| Does the diff actually implement the WU's tasks (not adjacent busywork)? | Mark BLOCKED, report drift |
| Are all files in "Modify" actually modified (gate.sh only checks Create existence)? | Mark BLOCKED, report missing modifications |
| Does the code match the pattern/style in sibling files? | If not, fix directly in main context (a fix commit in task-per-commit mode) |
| Does the diff introduce a NEW helper/component/service/type that near-duplicates something existing, something an earlier WU created, or something the "Reuse Verdicts" table said to reuse/extend? | Fix in main context: swap to the existing/shared artifact; if a true extraction is needed, extract and re-point rather than accept the copy |
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
"$HOME/.claude/plugins/marketplaces/budtags-claude-plugin/budtags/skills/run-plan/scripts/gate.sh" {directory}/WU-{N}-{slug}.md --since $UNIT_START
```

gate.sh performs, in one shot: WU Files-section parsing → every Create file exists →
scope audit of BOTH the working tree and the commit range `$UNIT_START..HEAD` (any file
changed but not declared = FAIL; pre-existing untracked clutter = warn only) → stub
detection → frontend pattern check → type placement (an `export type|interface|enum`
the unit ADDED to a ts/tsx file outside `resources/js/Types/` = FAIL; only added lines are
judged, tests exempt; fix = move the type to its domain type file and import it). **It does
not run `composer check`** (the
`--composer` flag exists, but the workflow never uses it; `--skip-composer` from older WU
files is accepted and ignored).

- Exit 0 = mechanical layer passed.
- Exit 1 = FAIL; the report lists EVERY issue (not just the first). Fix all issues in
  main context (as a fix commit in task-per-commit mode), re-run gate.sh until clean.
  Known detector false positives (the word "temporary" in a comment, a one-line
  `{}` constructor body, `axios` in a component file) get the established rewording /
  extraction fix, never a suppression.
- Exit 2 = the SCRIPT could not do its job (bad WU path, unparseable Files section,
  bad `--since` ref, detector malfunction). That is a harness problem, not a code
  failure — report to the user; do NOT mark the WU BLOCKED over it.

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

Parse the work unit's `## Verification` section and run each command. These are the
unit's TARGETED checks (`php artisan test --filter=X`, `npx vitest run <dir>`, per-file
`vendor/bin/phpstan analyse`, `npm run type-check`, a migration up/down, a tinker probe).
Run every one of them, one command per message, unpiped (never `| tail`, it eats the
exit code). If a WU file from an older decomposition lists a bare `composer check`,
SKIP that line: the gauntlet runs once at the end of the branch.

**Step 5: Test-DB refresh after migration units (KNOWN FAILURE MODE)**

If this unit added or changed a migration, the parallel test databases
(`budtags_test_1..N`) are now migration-stale, and the NEXT unit's tests will fail with
confusing schema errors that look like code bugs. After the migration commit:

```bash
composer migrate-test-dbs
```

If parallel tests still fail with schema errors while a single-process run passes,
drop the `budtags_test_*` databases manually (the `--recreate-databases` flag is
unreliable) and re-run. NEVER diagnose post-migration parallel-test failures as code
regressions before ruling out DB staleness.

**Worktree runs:** if this plan executes inside a git worktree, EVERY test invocation
(including `composer migrate-test-dbs` and review-branch's `composer check` at the end)
must be prefixed with that worktree's database: `DB_DATABASE=budtags_<slug>_test ...`
(named OUTSIDE the `budtags_test%` wildcard so stale-DB hygiene sweeps can't take it).
The `worktree-test-db` hook denies unprefixed runs and echoes the exact prefix to
use. Stale-DB recovery then targets `budtags_<slug>_test_*` only — never drop the
main tree's `budtags_test_*` family, another session may be mid-gate on it. See
the `worktree` skill for provisioning.

### 1.7 Gate Check

**If both the Orchestrator Review (1.5) and Verification (1.6) passed:**

Task-per-commit mode (the commits already exist):
1. Nothing to stage. Any orchestrator fix made during review is its own commit
   (subject: what it fixes, imperative; body 2-3 lines; whole files; branch check first).
2. Update MANIFEST: status -> DONE, with the branch tip (`git rev-parse --short HEAD`)
   and the list of the unit's commits (`git log --oneline $UNIT_START..HEAD`).

Legacy single-commit mode:
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
4. Update MANIFEST: status -> DONE, with the commit hash

Then, in both modes:
5. Update MANIFEST Progress Log section
6. **Propagate as-built facts downstream**: read the finished WU's "Notes for Next Unit"
   and "Decisions Made"; apply anything that changes a DOWNSTREAM WU's assumptions
   (final signatures, renamed files, changed approach) directly into those WU files'
   Required Context / Tasks. Stale WU files are how later subagents re-implement
   against assumptions that no longer hold.
7. Continue to the next READY unit, or to Phase 2 when none remain

**If either review (1.5) or verification (1.6) failed:**

Small fixes (a few lines) are faster to apply directly in main context as a fix commit —
prefer that. **Bounded retry (exactly one):** if the failure looks like a fixable
implementation miss (failed test, missed task, stub) rather than a plan defect, the
orchestrator may re-spawn the SAME work unit ONCE, embedding the verbatim failure output
and what must change into the new prompt; the builder adds fix commits on top (never
amend, never reset). If the retry also fails, or the failure indicates the WU itself is
wrong (missing dependency, wrong assumption about the codebase):

1. Update MANIFEST: status -> BLOCKED
2. Update MANIFEST Progress Log with failure details (which step failed, the command output, the fix required) and the unit's commit list so far
3. STOP immediately — do not attempt the next unit
4. Report failure details to the user

---

## Phase 2: End of Branch

Runs once, after the LAST unit is DONE (not when a single unit was requested with
`/run-plan <dir> WU-XX`, unless it was the last one).

### 2.1 review-branch (the ONE full gauntlet)

Invoke the `budtags:review-branch` skill via the Skill tool. Its Phase 2 runs
`composer check` (pint, eslint, type-check, abbreviations, phpstan, vitest, parallel
phpunit) — this is the only time the full gauntlet runs in the whole run — and its
Phases 3-5 do the domain review of the branch diff against main.

- Start it immediately after the last unit; do not ask, do not wait for the user.
- If a gate fails: fix EVERYTHING it surfaces in main context (also pre-existing issues
  it trips over; if one looks like intentional WIP, surface it to the user instead),
  commit the fixes (whole files, imperative subjects), and re-run review-branch.
- If the report says NEEDS FIXES: fix EVERY finding, all severities, in main context,
  commit, re-run. Never park MEDIUM/SUGGESTION findings in the report for later.
- Stop when the verdict is READY TO MERGE, or when a finding needs a decision only the
  user can make (report it, do not guess).
- Worktree: prefix with the worktree's `DB_DATABASE=budtags_<slug>_test`.

### 2.2 Success Report

```
## Run Complete: {DIRECTORY}

All work units completed; review-branch verdict: READY TO MERGE.

### Commits Created (local), per unit
- WU-01 prefactor (3 commits): abc1234 Extract the Metrc item create core into a shared service; ...
- WU-02 server-core (5 commits): ...

### End-of-branch review
composer check green (the run's only full gauntlet). Domain review: {N} MEDIUM / {M} SUGGESTION findings, listed below.

Commits are local. When ready: git push -u origin {branch}
```

### 2.3 Blocked Report

```
## Run Stopped: {DIRECTORY}

BLOCKED at WU-{N}: {description}

### Failure Details
Command: php artisan test --filter=ProductMetrcItemCreateEndpoint
Exit code: 1
Output:
{error output}

### Progress
- [DONE] WU-01 prefactor (3 commits, tip abc1234)
- [BLOCKED] WU-02 server-core (2 of 5 tasks committed, tip def5678)
- [PENDING] WU-03 client-block

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

### WU-01: prefactor
- **Status**: DONE
- **Started at**: 9f22def04
- **Completed**: 2026-09-02
- **Branch tip**: abc1234 (3 commits)
- **Notes**: existing tests unchanged and green

### WU-02: server-core
- **Status**: BLOCKED
- **Started at**: abc1234
- **Failed**: 2026-09-02
- **Reason**: ProductMetrcItemCreateEndpointTest 403 case failing; 2 of 5 tasks committed
```

---

## Rollback Guidance

If execution fails partway through:

1. **Committed work stays committed** - reviewed units passed their gates
2. **BLOCKED unit needs manual fix** - user fixes, then resumes; the builder's partial
   commits for that unit are on the branch and are the base for the fix
3. **To undo a whole unit** (only with the user's go-ahead): its start SHA is in the
   Progress Log: `git reset --hard <Started at>` discards every commit of that unit
   and everything after it; `git revert <Started at>..HEAD` keeps history instead
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
| Verification fails | Fix in main context or one bounded retry; else mark BLOCKED, stop, report |
| Subagent errors | Mark BLOCKED, stop, report agent error |
| Git commit fails (hook denial: Pint/PHPStan on staged PHP, git-safety) | Fix the flagged files, re-commit; never bypass the hook |
| File not found | Report missing file, suggest resolution |
| No READY units | Report blocked dependencies or completion |
| review-branch gate fails at the end | Fix everything surfaced, commit, re-run |

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
2. Bound the scope audit (gate.sh, working tree AND commit range)
3. Verify files exist after agent completes
4. Stage the correct files (legacy single-commit mode only)

---

## Anti-Patterns

- Pushing to remote (NEVER — also mechanically asked/denied by git-safety.py)
- **Running `composer check` between commits or between units** — the gauntlet runs once, at the end of the branch, inside review-branch
- **Ending a run without review-branch** — that is the branch's only full gate
- Skipping the per-unit review because "the builder committed already" (the commits are the input to the review, not a substitute for it)
- Continuing after a failure (one bounded retry is allowed; a second failure = BLOCKED + stop)
- Skipping verification commands
- Skipping gate.sh, or hand-waving its checks because you "already eyeballed the diff"
- Running gate.sh without `--since $UNIT_START` on a task-per-commit unit (the working tree is clean; the range is where the scope drift lives)
- Marking a WU BLOCKED on gate.sh exit 2 (that's a harness malfunction — report it instead)
- Diagnosing post-migration parallel-test failures as code bugs before refreshing test DBs
- **Skipping Orchestrator Review (1.5)** — agents do not self-review; the orchestrator must
- **Delegating the unit review or the end-of-branch fixes to a subagent** — they run in main context
- **Committing with "WU-XX:" prefix** on the subject line — the subject is the task line (or the MANIFEST description in legacy mode) as-is
- **Adding "Co-Authored-By:" or "Generated with Claude Code"** lines to commit messages
- Using --force, --amend, or reset on a builder's commits
- Committing unrelated files; sweeping a pre-existing working-tree change into a unit
- Committing plan files (MANIFEST.md, WU-*.md, SHARED_CONTEXT.md, plan directory files)
- Using `git add .` or `git add -A` (always stage specific files only)
- Accepting incomplete implementations from agents
- Accepting a diff that reinvents an existing component/service/helper instead of reusing or extending it (the Reuse Verdicts table in SHARED_CONTEXT says which — check it during Step A)
- Trusting that SHARED_CONTEXT.md was updated without verifying the diff
- **Spawning an execution subagent without embedding SHARED_CONTEXT inline** (since v1.9, the orchestrator MUST read the file in the pre-spawn step and substitute `{SHARED_CONTEXT_INLINE}` in the prompt; never rely on the subagent to Read it themselves)
- **Telling the subagent to Read SHARED_CONTEXT.md** (since v1.9, the file is embedded in the prompt; asking the agent to Read it is wasted tool calls and signals the orchestrator skipped the pre-spawn step)
- **Accepting a thin or generic "Patterns Followed" section** in the Completion Report (it is the leading indicator that the embedded context was ignored; treat fabricated row references the same way)

---

## Correct Behavior

- Create feature branch if on main; stash unrelated working-tree changes first
- Record `UNIT_START` before every spawn; review and gate against that range
- Execute one unit at a time in fresh context, serially — dispatch the next subagent only after the previous unit is reviewed and DONE (parallel dispatch only on explicit user request)
- **Run Orchestrator Review (1.5) BEFORE the WU's own verification** — range diff audit, SHARED_CONTEXT audit, patterns-substance audit, task-list + commit check
- **Reject reinvention in Step A** — any new artifact duplicating an existing one (or violating a Reuse Verdict) gets swapped to the shared thing in main context
- **Run gate.sh --since for every unit** and fix ALL issues it reports in main context — not via subagent
- **Never run `composer check` per unit**; rely on the pre-commit hook (Pint + PHPStan on staged PHP), the builder's touched-dir vitest + eslint for TS, and the unit's targeted Verification block
- **Populate SHARED_CONTEXT.md in main context** if the subagent left relevant tables empty
- **Inject verified schema** into spawn prompts for DB-touching WUs (subagents fabricate columns)
- **Refresh parallel test DBs after migration commits** (`composer migrate-test-dbs`; drop `budtags_test_*` manually if still stale)
- **Propagate "Notes for Next Unit" into downstream WU files** after each unit
- Run all WU-specific verification commands for each unit, one per message, unpiped
- **Commit subjects = task lines verbatim** (builder) or MANIFEST description verbatim (legacy) — no WU-XX prefix, no Co-Authored-By, no auto-attribution
- **After the last unit, invoke review-branch immediately** — fix everything it surfaces, re-run until READY TO MERGE
- Stop immediately on any unrecoverable failure
- Update MANIFEST status throughout (with start SHA and branch tip per unit)
- Report clear summary at end: commits per unit + the review verdict
- Verify no plan directory files are committed
- Remind user commits are local
- **Read SHARED_CONTEXT.md in the orchestrator before each Agent spawn** and embed its full contents into the prompt at the `{SHARED_CONTEXT_INLINE}` placeholder (v1.9)
- **Audit the subagent's "Patterns Followed" section for substance** as part of Orchestrator Review Step C.2 (v1.9)
