---
name: decompose-plan
description: Decomposes a plan file into BRANCH-SIZED work units (one review boundary each, 5-20 tasks, every task = one commit) with dependency tracking. FILE CREATION ONLY - does NOT implement or execute any code.
version: 4.0.0
category: workflow
auto_activate:
  keywords:
    - "decompose plan"
    - "split plan"
    - "create work units"
    - "break down plan"
    - "modularize plan"
---

# Decompose Plan Skill

**PURPOSE:** Create branch-sized work units from a plan. Nothing more.

## CRITICAL RULES

```
╔══════════════════════════════════════════════════════════════════╗
║  THIS SKILL CREATES FILES. IT DOES NOT IMPLEMENT CODE.           ║
║                                                                   ║
║  ✅ DO: Create markdown files (manifest + work units)             ║
║  ✅ DO: Analyze plan for intelligent decomposition                ║
║  ✅ DO: Determine dependencies between work units                 ║
║  ✅ DO: Include tests WITH each task (not separate)               ║
║  ✅ DO: Output list of created files                              ║
║                                                                   ║
║  ❌ DO NOT: Write any PHP, TypeScript, or application code        ║
║  ❌ DO NOT: Create migrations, models, controllers, or components ║
║  ❌ DO NOT: Run any commands besides file creation                ║
║  ❌ DO NOT: "Start implementing" or "begin execution"             ║
║  ❌ DO NOT: Ask "Ready to start WU-01?"                           ║
║                                                                   ║
║  YOUR JOB IS DONE WHEN THE MARKDOWN FILES EXIST.                 ║
╚══════════════════════════════════════════════════════════════════╝
```

## What This Skill Produces

Takes a plan file and creates a **subdirectory** with branch-sized work units:

```
{FEATURE}/
├── MANIFEST.md                      (Index, execution contract, dependencies, progress)
├── SHARED_CONTEXT.md                (Pre-populated research from create-plan)
├── WU-01-prefactor.md               (~120-200 lines, 5-20 tasks, one commit each)
├── WU-02-{description}.md
├── WU-03-{description}.md
└── ...                              (typically 3-8 units per plan)
```

**Sizing model (v4.0):** a work unit is a **branch-sized builder brief**, not a
context-window slice. The 200k-window era rule ("5-10 tasks, one session") is gone: a
modern builder executes 10-20 commits in one run with quality intact. The binding
constraints now are:

- **Reviewability** — the unit's commit range is one diff a reviewer audits at unit end,
  answering ONE review question ("nothing changed behaviourally", "the server contract is
  right", "the modal did not shift").
- **Blast radius** — schema, money math, prod-data operations and hot-file UI integration
  keep their own review boundary.

Each **task = one commit**: the task line's bold text is the commit subject; the builder
commits after every task; the repo's pre-commit hook runs Pint + PHPStan on the staged
PHP files; targeted tests ride in the same commit. The full `composer check` runs ONCE, at
the end of the branch, through review-branch. Never put it in a unit.

## Command

```
/decompose-plan <plan-file>
```

**Example:**
```
/decompose-plan ADVERTISING-FEATURE-PLAN.md
```

---

## Workflow

### Step 1: Read and Analyze the Plan

Read the entire plan file to understand:
- Feature name and scope
- Database work (tables, models, relationships)
- Backend work (controllers, services, routes)
- Frontend work (pages, components)
- Integration work (external APIs, Metrc, QuickBooks)
- What needs testing
- **Phase 0 research** (component inventory, type inventory, service inventory, patterns)
- **Prefactoring & Reuse Audit** (verdict table, Prefactoring Tasks, approved duplicates)

**Re-check the plan's branch facts against git before cutting.** A plan written for one
branch often lands on another. If the plan says "add the column to the branch's existing
migration", verify with `git branch --contains` that the migration is still unmerged;
once it is on main it has run on every developer database and the unit needs a NEW
migration file instead. Note every such correction in the MANIFEST and fix the plan in
place.

### Step 1.5: Extract Research into SHARED_CONTEXT.md

If the plan contains **Phase 0 Research** (component inventory, type inventory, service inventory, naming patterns), create `{FEATURE}/SHARED_CONTEXT.md` and pre-populate it.

Use the template from `../run-plan/prompts/shared-context-template.md` (the single
canonical copy lives in the run-plan skill — run-plan also uses it to create the file
in Phase 0 if decompose didn't). Fill in these EXACT section headings from the template:

| Plan Section | SHARED_CONTEXT Section (exact heading) |
|--------------|----------------------------------------|
| Component inventory | `## Domain-Specific Components (from create-plan)` |
| Type inventory | `## Existing TypeScript Types (from create-plan)` |
| Service inventory | `## Existing PHP Services (from create-plan)` |
| Naming patterns | `## Naming Conventions (Feature-Specific)` |
| Existing routes | `## Existing Routes (from create-plan)` |
| Prefactoring & Reuse Audit verdict table | `## Reuse Verdicts (from plan Prefactoring Audit)` |

Do NOT invent new section headings — run-plan's execute prompt and Orchestrator Review
audit specific tables by name (PHP Services & Classes, TypeScript Types, Routes Added,
Cache Keys, Enums Created, Database Columns & Naming, Implementation Decisions); those
"(created)" tables stay empty at decompose time and are filled by execution agents.

**Why this matters:** Work unit executors receive this content inline instead of re-discovering these components. This eliminates 30-50 redundant exploration tool calls per agent.

If the plan has NO Phase 0 research, create SHARED_CONTEXT.md with empty tables (using the template) so agents can populate it as they work.

### Step 2: Identify Work Domains

Determine which domains are needed (only create what's necessary):

| Domain | Indicators |
|--------|------------|
| Database | Tables to create, model relationships |
| Backend | Controllers, services, routes, APIs |
| Frontend | Pages, components, forms |
| Integration | Metrc sync, QuickBooks, LeafLink |

**Skip domains not in the plan.** Don't create empty work units.

### Step 2.5: The Prefactor Unit Comes FIRST

If the plan has a **Prefactoring & Reuse Audit** section (create-plan Phase 9.5):

1. Put ALL its Prefactoring Tasks (PF-*) into ONE `WU-01-prefactor` unit, one task
   (= one commit) per extraction. These are behavior-preserving refactors ONLY: extract
   shared cores, generalize near-copies, re-point EXISTING call sites. No feature code.
   Existing tests staying green with NO edits IS the verification. Split into two
   prefactor units only when blast radius demands it (e.g. a server extraction and a
   client extraction that different reviewers own).
2. Every feature unit that builds on an extracted/generalized artifact **depends on**
   the prefactor unit — it sits at the root of the dependency graph.
3. Copy the verdict table into SHARED_CONTEXT.md under
   `## Reuse Verdicts (from plan Prefactoring Audit)` so every executor sees
   "use THIS, do not create that" without re-discovering it.
4. Cross-check every WU's `### Create` list against the verdict table: a Create entry
   for an artifact the audit marked REUSE or EXTEND is a decomposition bug — fix the WU,
   don't ship the contradiction to run-plan.

If the plan has **NO** Prefactoring & Reuse Audit section: **STOP decomposing.** Run a
mini-audit first — for each file the plan proposes to create, hunt for an existing
near-duplicate (search by the job it does and its synonyms across `app/Services/`,
`app/Jobs/`, `resources/js/Components/`, `resources/js/hooks/`, and every sibling
integration). Report findings to the user and get verdicts before creating any work
units. Decomposing an un-audited plan bakes reinvention into every WU downstream.

### Step 3: Cut Units at Review Boundaries

Cut in this order of precedence. Each line is one unit unless there is nothing for it.

| # | Unit (typical slug) | Contains | Tasks (commits) | Review question at unit end |
|---|---------------------|----------|-----------------|-----------------------------|
| 1 | `prefactor` | PF-* extractions, call-site re-points | 3-10 | Did behaviour stay identical? (existing tests unchanged + green) |
| 2 | `foundations` / `schema-and-defaults` | the branch's ONE migration as task 1; model/settings plumbing; small independent primitives (reference reads, new API wrappers) | 4-10 | Is the schema right and are the primitives correct in isolation? |
| 3 | `server-core` | services, orchestration, endpoints, validation, the feature's server contract | 4-10 | Is the contract right, never-throw / org-scoped / audited? |
| 4 | `client-block` / `client-contracts` | types, hooks, new components that nothing mounts yet | 4-10 | Do the client contracts match the server and does the component behave alone? |
| 5 | `surfaces` | wiring into existing hot files: big modals, pages, tables, row menus | 3-8 | Did the surface integrate without regressions (layout, existing tests unchanged)? |
| 6 | `rollout` | backfill COMMANDS, feature gates, announcements, retirement of old rows | 2-6 | Is the prod-data operation rehearsed, dry-runnable and reversible? |

**Merge** two lines into one unit when they share the review question, the specialist and
the files (e.g. a plan with three routes and no client work = one server unit).
**Split** a line when: a different specialist owns half of it; it carries a migration or
money math the rest does not; it touches a hot file under a hard UI rule; or it would
exceed ~20 tasks.

**Never** cut a unit because "it would not fit in one session". **Never** go below one
unit per branch. **Never** merge a prod-data operation into a feature unit.

**Task = commit.** Each task line reads:

```
N. [ ] **Imperative commit subject** - what to build, the files, the tests that ride in
   this commit, the targeted checks to run green before committing.
```

- Tests ride in the SAME commit as the code they cover (never a separate "write tests" task).
- Hygiene is NOT a task: Pint + PHPStan run from the pre-commit hook on staged PHP files; the
  builder runs touched-dir vitest + eslint before TS commits; do not write "run pint" tasks.
- A task that only records something in SHARED_CONTEXT is not a commit; fold it into the
  task that created the thing.
- Read/plan-only tasks ("read X, note what moves") fold into the first real task.

Tests must follow the `budtags-testing` skill principles: test behaviors (not implementation), one reason to fail per test, self-contained data setup, and exact assertions. For frontend work, include Vitest tests alongside components.

### Step 3.5: Assign Agent Type to Each Work Unit

Based on work unit content, assign the best specialist agent. The agent type determines which skills are auto-loaded when the work unit is executed. A branch-sized unit may span PHP and TS; pick the primary and name an acceptable alternate for a task range (`fullstack-developer (metrc-specialist acceptable for tasks 4-8)`).

| Work Content | Agent Type | Auto-Loaded Skills |
|--------------|------------|-------------------|
| Metrc API calls, sync logic | `metrc-specialist` | metrc-api, verify-alignment |
| QuickBooks integration | `quickbooks-specialist` | quickbooks, verify-alignment |
| LeafLink marketplace | `leaflink-specialist` | leaflink, verify-alignment |
| TanStack Query/Table/Virtual | `tanstack-specialist` | 6 tanstack-* skills, verify-alignment |
| React components, modals, forms | `react-specialist` | verify-alignment |
| TypeScript types, utilities, non-React TS | `typescript-developer` | (none - reads patterns) |
| Backend controllers, services | `php-developer` | (none - reads patterns) |
| Database migrations, models | `php-developer` | (none - reads patterns) |
| Mixed frontend + backend | `fullstack-developer` | (none - fallback) |

**CRITICAL for Metrc work units:** Any work unit that involves MetrcApi controller methods MUST include, inside the relevant task, verifying `$api->set_user(request()->user())` is called before any API interaction. Queue jobs must accept User via constructor and call `$api->set_user($this->user)`. See `METRC_API_RULES.md` "User Context Management" section.

**Selection Priority:**
1. If work involves a specific integration (Metrc, QuickBooks, LeafLink), use that specialist
2. If work is TanStack-heavy (Query, Table, Virtual), use `tanstack-specialist`
3. If work is frontend-only (React/Inertia), use `react-specialist`
4. If work is backend-only (Laravel), use `php-developer`
5. If work spans frontend and backend, use `fullstack-developer`

Add `**Agent**:` and `**Skills**:` fields to each work unit's frontmatter.

### Step 4: Determine Dependencies

Build the (coarse) dependency graph:
- The prefactor unit has no dependencies; every unit that touches an extracted artifact depends on it
- Foundations and server-core are usually independent of each other (both need prefactor)
- Client units depend on the server contract they type
- Surfaces depend on the client block and on whatever default/setting they read
- Rollout depends on everything it gates or backfills

```
WU-01 (prefactor) ──┬──> WU-02 (foundations) ──┐
                    │                          ├──> WU-04 (client-block) ──> WU-05 (surfaces)
                    └──> WU-03 (server-core) ──┘
```

Note same-file collisions (two units editing `routes/web.php` or the same modal) in the
MANIFEST's Parallel Opportunities section; serial order makes them harmless.

### Step 5: Extract Context for Each Unit

For each work unit, include ONLY:
- Context directly relevant to that unit
- Decisions that affect implementation, grouped by the task range they govern
- Constraints to follow
- Pattern references (link to patterns/, don't embed)
- Anchors (file:line) from the plan's research, with the reminder that anchors are a map, not a contract

### Step 6: Create Files

Create all files in `{FEATURE}/` subdirectory:

1. **SHARED_CONTEXT.md** - Using `../run-plan/prompts/shared-context-template.md`, pre-populated with research from Step 1.5
2. **MANIFEST.md** - Using `MANIFEST_TEMPLATE.md` (its Execution Contract section is mandatory)
3. **WU-{N}-{description}.md** - Using `WORK_UNIT_TEMPLATE.md` for each unit (the `## Tasks (one commit each)` heading is the run-plan mode switch; keep it verbatim)

### Step 7: Output File List and STOP

```
## Files Created

📁 PRODUCT-FIRST-METRC-ITEM-CREATE/
  ├── ✅ SHARED_CONTEXT.md (pre-populated with research)
  ├── ✅ MANIFEST.md
  ├── ✅ WU-01-prefactor.md            (7 commits)
  ├── ✅ WU-02-metrc-foundations.md    (8 commits)
  ├── ✅ WU-03-product-first-server.md (5 commits)
  ├── ✅ WU-04-client-block.md         (5 commits)
  └── ✅ WU-05-client-surfaces.md      (5 commits)

Decomposition complete. 5 work units (30 commits) + SHARED_CONTEXT created.
```

**THEN STOP. DO NOT OFFER TO IMPLEMENT. DO NOT ASK ABOUT NEXT STEPS.**

---

## Work Unit Sizing Examples

### ❌ TOO SMALL (window-era cut)
```markdown
WU-00a  Extract the item create service            (8 tasks, 1 commit)
WU-00b  Extract the category fields component      (8 tasks, 1 commit)
WU-00c  Extract the brand modal + test helper      (7 tasks, 1 commit)
WU-01   Add the org default column                 (9 tasks, 1 commit)
WU-02   License param on strain/brand reads        (7 tasks, 1 commit)
WU-03   Metrc strain create                        (8 tasks, 1 commit)
...13 units, each ending with "record the signatures in SHARED_CONTEXT for the next unit"
```
Thirteen gate runs, thirteen handoffs, and conditional tasks like "if WU-09 extracted the
helper, reuse it, else extract it now". The seams exist for a context window, not a reviewer.

### ✅ RIGHT SIZE (branch-sized cut of the same plan)
```markdown
WU-01 prefactor            7 commits   behaviour preserving; existing tests unchanged
WU-02 metrc-foundations    8 commits   migration (task 1) + license param + strain create
WU-03 product-first-server 5 commits   readiness, orchestration, both endpoints, create arm
WU-04 client-block         5 commits   types, hooks, strain modal, the block (unmounted)
WU-05 client-surfaces      5 commits   product modal mode row (no-shift rule) + row action
```
Five review boundaries, thirty commits, one `composer check` at the end.

### ❌ STILL WRONG (too coarse)
```markdown
WU-01 everything           30 commits
```
One diff nobody can audit; the migration, the money math and the hot modal share a review.

---

## Pattern References

Work units should **reference** patterns, not embed them:

```markdown
## Patterns to Follow
- See: `patterns/backend-patterns.md` for controller structure
- See: `patterns/test-patterns.md` for organization scoping tests
```

Pattern files are in this skill's `patterns/` directory:
- `database-patterns.md` - Model and migration patterns
- `backend-patterns.md` - Controller and service patterns
- `frontend-patterns.md` - React/Inertia patterns
- `test-patterns.md` - PHPUnit + Vitest test patterns (references `budtags-testing` skill for full philosophy)

---

## Available Resources

- `MANIFEST_TEMPLATE.md` - Template for manifest file
- `WORK_UNIT_TEMPLATE.md` - Template for work units
- `../run-plan/prompts/shared-context-template.md` - Template for SHARED_CONTEXT.md (canonical copy lives in the run-plan skill)
- `patterns/*.md` - Lightweight pattern references

---

## What Happens After (the run-plan harness contract)

The output of this skill is consumed by `/run-plan {FEATURE}`, which acts as the
execution harness. Everything this skill writes must satisfy run-plan's parsing and
audit contract:

| Decompose output | How run-plan consumes it |
|------------------|--------------------------|
| MANIFEST work unit table (`ID / Unit / Description / Status / Depends On`) | Parsed to compute READY units (PENDING + all deps DONE). Description is the UNIT SUMMARY; commit subjects come from the task lines |
| MANIFEST `## Execution Contract` section | Tells the orchestrator (and any human) that tasks are commits and where the gates run; keep it |
| MANIFEST statuses | Only `PENDING / IN PROGRESS / DONE / BLOCKED` are stored; READY is computed, never written |
| WU `**Agent**:` field | Mapped to `subagent_type` for the execution subagent (must be one of the values in Step 3.5) |
| WU `## Tasks (one commit each)` heading | The mode switch: run-plan's builder commits after every task. A plain `## Tasks` heading means the legacy one-commit-per-unit mode |
| WU task lines (`**Bold subject** - details`) | The bold text is the commit subject, verbatim; the builder must not paraphrase it |
| WU `## Files` section (`### Create` / `### Modify`, backticked paths) | Parsed mechanically by `gate.sh --since <unit start>`: Create files must exist, and any file changed in the unit's commit range OR the working tree outside the declared set fails the scope audit — declare exhaustively |
| WU `## Verification` section | Run by the orchestrator at unit end — TARGETED commands only (filtered tests, per-file phpstan, touched-dir vitest, type-check, migration up/down). Never `composer check`: review-branch runs it once at the end of the branch |
| SHARED_CONTEXT.md | Read by the orchestrator and embedded **inline** into each subagent prompt (subagents never Read it); subagents append discoveries to the file; never committed |
| WU `## Decisions Made` / `## Notes for Next Unit` | Filled during execution; orchestrator audits alongside the Completion Report and propagates as-built facts into downstream units |

**This skill's job ends when the files are created.** Execution, verification, and
commits belong to run-plan; the branch's single full gauntlet belongs to review-branch.

---

## Anti-Patterns (DO NOT DO THESE)

❌ "Now let's start implementing WU-01..."
❌ "Ready to begin the first work unit?"
❌ "I'll create the migration for you..."
❌ Cutting units to fit a context window (the retired 5-10 task rule)
❌ One unit per file, per controller, or per component
❌ Putting `composer check` (or a bare full pint/phpstan/test run) in a WU's Verification or Done When
❌ A hygiene-only task ("run pint + phpstan", "type-check") as its own commit
❌ A "write tests" task separate from the code it tests
❌ Conditional handoffs between units ("if WU-09 extracted it, reuse it, else extract it now") — decide now and put the helper in one unit
❌ Telling the builder to edit a migration that is already on main
❌ Embedding 200-line checklists in each file
❌ A WU `### Create` entry for an artifact the audit marked REUSE or EXTEND
❌ Decomposing a plan that has no Prefactoring & Reuse Audit without running the mini-audit
❌ Scheduling feature units before the prefactor unit they build on

## Correct Behavior

✅ Cut at review boundaries: prefactor / foundations / server-core / client-block / surfaces / rollout
✅ 5-20 tasks per unit, each task = one commit with a bold imperative subject
✅ Tests ride in the commit that adds the code
✅ The branch's ONE migration is task 1 of the foundations unit, in a NEW file
✅ The MANIFEST carries the Execution Contract and the branch/migration grouping
✅ Prefactor unit first; feature units depend on it
✅ Copy the plan's reuse verdicts into SHARED_CONTEXT so executors inherit them
✅ Only create work units for domains in the plan
✅ Reference patterns instead of embedding them
✅ List the files created with their commit counts
✅ Say "Decomposition complete"
✅ Stop responding
