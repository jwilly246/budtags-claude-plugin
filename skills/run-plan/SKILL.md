---
name: run-plan
description: Autonomously executes decomposed work units, committing after each successful verification, until complete or blocked.
version: 1.0.0
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
╔══════════════════════════════════════════════════════════════════╗
║  GIT SAFETY: LOCAL COMMITS ONLY - NEVER PUSH                     ║
║                                                                   ║
║  ✅ git checkout -b {branch}     (create local branch)           ║
║  ✅ git add {files}              (stage specific files)          ║
║  ✅ git commit -m "..."          (local commit)                  ║
║                                                                   ║
║  ❌ git push                     (NEVER - user pushes later)     ║
║  ❌ git push -u origin           (NEVER)                         ║
║  ❌ Any remote operations        (NEVER)                         ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Architecture Overview

```
Orchestrator (this skill - lightweight, runs in main context)
     │
     ├─→ Phase 0: Branch Safety Check
     │      └─→ Create/verify feature branch
     │
     └─→ Phase 1-3: Execution Loop
            │
            FOR each READY work unit:
            ├─→ Update MANIFEST: status → IN PROGRESS
            ├─→ Spawn Task agent (fullstack-developer)
            │      └─→ Fresh context, reads WU file, executes tasks
            ├─→ Run verification commands (from WU file)
            ├─→ Gate Check:
            │      ├─→ PASS: git commit → MANIFEST: DONE
            │      └─→ FAIL: MANIFEST: BLOCKED → STOP
            └─→ Next unit (or finish)
```

---

## Command Usage

```
/run-plan <directory>              # Run all READY units
/run-plan <directory> WU-03        # Run specific unit only
```

---

## Phase 0: Branch Safety

Before any work, ensure we're on a feature branch:

```bash
# Check current branch
git branch --show-current
```

**If on main or master:**
1. Extract feature name from directory (e.g., `ADVERTISING` → `advertising-feature`)
2. Create and switch to feature branch:
   ```bash
   git checkout -b {feature-name}
   ```
3. Confirm branch before proceeding

**If already on feature branch:**
- Continue (just verify we're not on main/master)

---

## Phase 1: Parse Manifest

Read `{directory}/MANIFEST.md` and extract:

### 1.1 Parse Work Unit Table

Find the table that looks like:
```markdown
| ID | Unit | Description | Status | Depends On |
|----|------|-------------|--------|------------|
| WU-01 | database-models | Create tables and models | PENDING | - |
| WU-02 | admin-controller | Admin CRUD endpoints | PENDING | WU-01 |
```

Extract for each row:
- **id**: WU-01, WU-02, etc.
- **slug**: database-models, admin-controller, etc.
- **status**: PENDING, READY, IN PROGRESS, DONE, BLOCKED
- **depends_on**: List of WU IDs or "-" for none

### 1.2 Build Dependency Graph

For each unit, determine if it's READY:
- Status is PENDING
- All dependencies have status DONE

### 1.3 Determine Execution Order

If specific unit requested (e.g., `WU-03`):
- Verify its dependencies are DONE
- Only execute that unit

If no specific unit:
- Find all READY units
- Execute in ID order (WU-01 before WU-02)

### 1.4 Handle Edge Cases

| Scenario | Action |
|----------|--------|
| No READY units, not all DONE | Report blocked state, list blockers |
| All units DONE | Report completion, final summary |
| Requested unit not READY | Report which dependencies are missing |

---

## Phase 2: Execution Loop

For each READY work unit:

### 2.1 Update Manifest Status

Read the MANIFEST file, find the work unit row, change status:
```
PENDING → IN PROGRESS
```

Use Edit tool to update the MANIFEST.md file.

### 2.2 Spawn Task Agent

Use the Task tool with:
- **subagent_type**: `fullstack-developer`
- **prompt**: Built from `prompts/execute-unit.md` template

The agent will:
1. Read the work unit file completely
2. Execute each task in the Tasks section
3. Create/modify files listed in the Files section
4. Follow BudTags patterns (org scoping, snake_case, etc.)
5. Update "Decisions Made" section if any choices were made
6. NOT run verification (orchestrator handles this)
7. NOT commit (orchestrator handles this)

### 2.3 Run Stub Detection (MANDATORY)

**Before running any other verification**, scan ALL files created/modified for stubs:

```bash
# Scan for PHP stubs
grep -rn --include="*.php" -E "(// ?TODO|// ?FIXME|// ?IMPLEMENT|throw new \\\\(Runtime)?Exception\('Not implemented|// \.\.\.|\{ ?\}$)" {files}

# Scan for TypeScript stubs
grep -rn --include="*.tsx" --include="*.ts" -E "(// ?TODO|// ?FIXME|throw new Error\('Not implemented|// \.\.\.|\{ ?\};?$|\(\) => \{ ?\})" {files}

# Scan for empty method bodies (PHP)
grep -Pzo "function \w+\([^)]*\)(?::\s*\w+)?\s*\{\s*\}" {php_files}

# Scan for placeholder comments
grep -rn --include="*.php" --include="*.tsx" --include="*.ts" -iE "(placeholder|stub|temporary|implement later|add logic|needs implementation)" {files}
```

**If ANY stub patterns are found:**
1. **FAIL IMMEDIATELY** - do not proceed to other verification
2. Update MANIFEST: status → BLOCKED
3. Report:
   - File and line number of each stub
   - The stub pattern found
   - Clear message: "STUBS DETECTED - work unit incomplete"

**Stub Detection Patterns:**

| Pattern | Type | Example |
|---------|------|---------|
| `// TODO` | Comment | `// TODO: implement validation` |
| `// FIXME` | Comment | `// FIXME: handle edge case` |
| `throw new Exception('Not implemented')` | PHP | Placeholder exception |
| `throw new Error('Not implemented')` | TS | Placeholder exception |
| `{ }` | Both | Empty method/function body |
| `() => { }` | TS | Empty arrow function |
| `// ...` | Both | Ellipsis placeholder |
| `return null;` (in non-nullable context) | PHP | Deferred implementation |
| `any` type | TS | Type escape hatch |

### 2.4 Run Form Pattern Check (if frontend files exist)

**For any .tsx files created/modified**, check for wrong patterns:

```bash
# Check for react-hook-form (should use Inertia useForm)
grep -rn --include="*.tsx" "from 'react-hook-form'" {tsx_files}

# Check for axios/fetch mutations in form files (should use useForm)
grep -rn --include="*.tsx" -E "axios\.(post|put|delete)\(" {tsx_files}

# Check for type attribute on Button (BudTags Button doesn't use this)
grep -rn --include="*.tsx" '<Button.*type=' {tsx_files}

# Check for form state passed to modal (modal should own its form)
grep -rn --include="*.tsx" -E "Modal.*formData=|Modal.*setFormData=" {tsx_files}
```

**If ANY form pattern violations found:**
1. **FAIL IMMEDIATELY** - do not proceed
2. Update MANIFEST: status → BLOCKED
3. Report:
   - The wrong pattern detected
   - Reference: `.claude/skills/decompose-plan/patterns/frontend-patterns.md`
   - Clear instruction: "Use Inertia useForm, not useState/axios/react-hook-form"

**Correct Form Patterns:**

| Wrong | Correct |
|-------|---------|
| `useState` for form fields | `useForm` from `@inertiajs/react` |
| `axios.post('/url', data)` | `post(route('route-name'))` from useForm |
| `react-hook-form` | Inertia `useForm` |
| `<Button type="submit">` | `<Button primary>` |
| `<Modal formData={data}>` | Modal contains its own useForm |

### 2.5 Run Verification Commands

After stub detection AND pattern check pass, parse the work unit's Verification section:

```markdown
## Verification

```bash
./vendor/bin/phpstan analyse app/Models/Ad.php --memory-limit=512M
php artisan test --filter=AdTest
./vendor/bin/pint app/Models/Ad.php
```
```

For each command:
1. Execute via Bash tool
2. Capture exit code
3. Record result (PASS/FAIL)

### 2.6 Gate Check

**If stub detection, pattern check, AND all verification commands pass:**
1. Stage files from WU "Files" section:
   ```bash
   git add path/to/file1.php path/to/file2.tsx
   ```
2. Commit with structured message:
   ```bash
   git commit -m "WU-{N}: {Work unit title}

   {Brief 2-3 line summary of what was done}"
   ```
3. Update MANIFEST: status → DONE
4. Add entry to Progress Log section with date
5. Continue to next READY unit

**If stub detection fails:**
1. Update MANIFEST: status → BLOCKED
2. Add stub locations to Progress Log
3. **STOP execution immediately**
4. Report:
   - "STUBS DETECTED" as the failure type
   - Each stub location (file:line)
   - The stub content found
   - Clear instruction: "All stubs must be replaced with complete implementations"

**If ANY verification command fails:**
1. Update MANIFEST: status → BLOCKED
2. Add failure details to Progress Log
3. **STOP execution immediately**
4. Report:
   - Which command failed
   - Error output
   - Which work unit was blocked
   - What remains to be done

---

## Phase 3: Completion

After execution loop ends (success or blocked), report:

### Success Report (all units done)
```markdown
## Run Complete: {DIRECTORY}

🎉 All work units completed successfully!

### Commits Created (local)
- abc1234: WU-01: database-models
- def5678: WU-02: admin-controller
- ghi9012: WU-03: admin-ui
- jkl3456: WU-04: seller-controller
- mno7890: WU-05: seller-ui

### Final Verification
All tests passing, PHPStan clean, Pint formatted.

📌 Commits are local. When ready: git push -u origin {branch}
```

### Blocked Report
```markdown
## Run Stopped: {DIRECTORY}

🛑 BLOCKED at WU-{N}: {description}

### Failure Details
Command: ./vendor/bin/phpstan analyse app/Models/Ad.php
Exit code: 1
Output:
{error output}

### Progress
- ✅ WU-01: database-models (abc1234)
- ❌ WU-02: admin-controller (BLOCKED)
- ⏸️ WU-03: admin-ui (PENDING)
- ⏸️ WU-04: seller-controller (PENDING)

### To Resume
1. Fix the issues reported above
2. Run: /run-plan {DIRECTORY} WU-{N}

📌 Existing commits are local. Do not push until issues resolved.
```

---

## Commit Message Format

```
WU-{N}: {Work unit title}

{Brief summary of what was done - 2-3 lines max}
```

**Example:**
```
WU-01: Create Ad and AdPlacement models

Added migrations for ads and ad_placements tables.
Created models with organization scoping.
Added factories and feature tests.
```

**NO** "Co-Authored-By: Claude" attribution.

---

## MANIFEST Status Updates

When updating MANIFEST.md, edit the status column:

**Status Transitions:**
```
PENDING → READY (when dependencies complete - automatic)
PENDING → IN PROGRESS (when starting execution)
IN PROGRESS → DONE (when verification passes)
IN PROGRESS → BLOCKED (when verification fails)
```

**Also update Progress Log section:**
```markdown
### WU-01: database-models
- **Completed**: 2026-01-27
- **Decisions Made**: Used string column for status instead of enum
- **Notes**: All tests passing
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Verification fails | Mark BLOCKED, stop, report failure details |
| Task agent errors | Mark BLOCKED, stop, report agent error |
| Git commit fails | Stop, report git error, don't update MANIFEST |
| File not found | Report missing file, suggest resolution |
| No READY units | Report blocked dependencies or completion |
| Invalid work unit ID | Report error, list valid IDs |

---

## Files Section Parsing

Work units have a Files section like:
```markdown
## Files

### Create
- `app/Models/Ad.php` - Ad model
- `database/migrations/2026_01_27_000001_create_ads_table.php` - Migration

### Modify
- `routes/web.php` - Add ad routes
- `app/Models/Organization.php` - Add ads relationship
```

Use this to:
1. Know what files the agent should create/modify
2. Stage the correct files for commit
3. Verify files exist after agent completes

---

## Dependency Unblocking

When WU-01 completes:
1. Find all units that depend on WU-01
2. Check if those units now have all dependencies DONE
3. Those units become READY for next iteration

Example:
- WU-02 depends on WU-01
- WU-03 depends on WU-01
- When WU-01 → DONE: both WU-02 and WU-03 become READY
- Execute WU-02 first (lower ID)

---

## Task Agent Prompt

See `prompts/execute-unit.md` for the full prompt template.

Key points for agent:
- Read work unit file completely before starting
- Execute tasks in order
- Create all files listed
- Follow BudTags patterns strictly
- Update "Decisions Made" section
- Do NOT run verification
- Do NOT commit

---

## Resume After Failure

When `/run-plan` is called after a previous BLOCKED state:

1. Read MANIFEST
2. Find BLOCKED unit(s)
3. Those units are the starting point
4. User should have fixed the issue
5. Resume execution from that unit

The BLOCKED status indicates "needs attention" - the orchestrator will attempt it again when resumed.

---

## Anti-Patterns

❌ Pushing to remote (NEVER)
❌ Running all verifications after all units (gate each unit)
❌ Continuing after a failure
❌ Skipping verification commands
❌ Skipping stub detection
❌ Using --force or --amend git flags
❌ Committing unrelated files
❌ Committing files with TODO/FIXME comments
❌ Committing files with empty method bodies
❌ Committing files with placeholder exceptions
❌ Accepting "I'll finish this later" from agents

---

## Correct Behavior

✅ Create feature branch if on main
✅ Execute one unit at a time in fresh context
✅ Run stub detection BEFORE other verification
✅ Run all verification commands for each unit
✅ Commit immediately after each success
✅ Stop immediately on any failure (including stubs)
✅ Update MANIFEST status throughout
✅ Report clear summary at end
✅ Remind user commits are local
✅ Reject incomplete implementations immediately
