---
name: run-plan
description: Autonomously executes decomposed work units, committing after each successful verification, until complete or blocked.
version: 1.4.0
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

---

## Architecture Overview

```
Orchestrator (this skill - lightweight, runs in main context)
     |
     +-> Phase 0: Setup
     |      +-> Verify/create feature branch
     |      +-> Create SHARED_CONTEXT.md if missing
     |
     +-> Phase 1: Execution Loop
     |      |
     |      FOR each READY work unit:
     |      +-> Update MANIFEST: status -> IN PROGRESS
     |      +-> Parse work unit for Agent type
     |      +-> Spawn Task agent (specialist per Agent field)
     |      |      +-> Fresh context, reads WU file, executes tasks
     |      +-> Run verification (scripts + WU commands)
     |      +-> Gate Check:
     |      |      +-> PASS: git commit -> MANIFEST: DONE
     |      |      +-> FAIL: MANIFEST: BLOCKED -> STOP
     |      +-> Next unit (or finish)
     |
     +-> Phase 2: Completion
            +-> Report summary (success or blocked)
```

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

Each Task agent starts fresh. Use `{directory}/SHARED_CONTEXT.md` for cross-agent continuity.

**Setup:** If missing, create from `prompts/shared-context-template.md` in Phase 0.

**Agent responsibilities:**
1. READ before starting
2. FOLLOW established patterns
3. UPDATE after completing (cache keys, types, routes, decisions)

**Orchestrator responsibilities:**
1. Create from template if missing
2. Stage in commits alongside work unit files

---

## Phase 0: Setup

### 0.1 Branch Safety

```bash
git branch --show-current
```

If on main/master:
1. Create feature branch: `git checkout -b {feature-name}`
2. Confirm before proceeding

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

### 1.4 Spawn Task Agent

Use Task tool with prompt from `prompts/execute-unit.md`.

### 1.5 Run Verification

**Step 1: Stub Detection (MANDATORY)**

Run the stub detection script on all files created/modified:

```bash
./budtags/skills/run-plan/scripts/detect-stubs.sh {file1} {file2} ...
```

Exit code 1 = stubs found = FAIL IMMEDIATELY.

**Step 2: Pattern Check (for .tsx files)**

```bash
./budtags/skills/run-plan/scripts/detect-wrong-patterns.sh {tsx_files}
```

Exit code 1 = violations found = FAIL IMMEDIATELY.

**Step 3: Work Unit Verification Commands**

Parse the work unit's `## Verification` section and run each command.

### 1.6 Gate Check

**If all verification passes:**
1. Stage files: `git add {files from WU "Files" section}`
2. Commit:
   ```
   WU-{N}: {Work unit title}

   {Brief 2-3 line summary}
   ```
3. Update MANIFEST: status -> DONE
4. Update MANIFEST Progress Log section
5. Continue to next READY unit

**If verification fails:**
1. Update MANIFEST: status -> BLOCKED
2. Update MANIFEST Progress Log with failure details
3. STOP immediately
4. Report failure details

---

## Phase 2: Completion

### Success Report

```
## Run Complete: {DIRECTORY}

All work units completed successfully.

### Commits Created (local)
- abc1234: WU-01: database-models
- def5678: WU-02: admin-controller

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
- [DONE] WU-01: database-models (abc1234)
- [BLOCKED] WU-02: admin-controller
- [PENDING] WU-03: admin-ui

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
| Task agent errors | Mark BLOCKED, stop, report agent error |
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

- Pushing to remote (NEVER)
- Running all verifications after all units (gate each unit)
- Continuing after a failure
- Skipping verification commands
- Skipping stub detection
- Using --force or --amend git flags
- Committing unrelated files
- Accepting incomplete implementations from agents

---

## Correct Behavior

- Create feature branch if on main
- Execute one unit at a time in fresh context
- Run stub detection BEFORE other verification
- Run all verification commands for each unit
- Commit immediately after each success
- Stop immediately on any failure
- Update MANIFEST status throughout
- Report clear summary at end
- Remind user commits are local
