# Run Plan

Execute work units from a decomposed plan autonomously.

## Purpose

**AUTONOMOUS EXECUTION.** This command reads a MANIFEST, executes READY work units via Task agents, runs verification gates, and commits after each successful unit—all without manual intervention.

## Usage

```
/run-plan <directory>              # Run all READY units until done/blocked
/run-plan <directory> WU-03        # Run specific unit only
```

**Example:**
```
/run-plan ADVERTISING
/run-plan ADVERTISING WU-02
```

## What It Does

1. **Branch Safety**: Creates feature branch if on main/master
2. **Parse Manifest**: Finds READY work units from MANIFEST.md
3. **Execution Loop** (for each READY unit):
   - Updates MANIFEST: PENDING → IN PROGRESS
   - Spawns Task agent (fullstack-developer) in fresh context
   - Agent reads WU file and implements all tasks
   - Runs verification commands from WU file
   - On success: commits changes, marks DONE, moves to next
   - On failure: marks BLOCKED, stops, reports what failed
4. **Completion Report**: Lists commits created (local only)

## Key Behaviors

| Feature | Behavior |
|---------|----------|
| Commits | **LOCAL ONLY** - never pushes to remote |
| On failure | Stops immediately, preserves state |
| Context | Fresh agent context per work unit |
| Verification | Gate check with PHPStan/tests/Pint |

## Instructions

**Read the skill file first:** `.claude/skills/run-plan/skill.md`

Then execute the orchestration workflow.

## Critical Rules

```
╔════════════════════════════════════════════════════════════════╗
║  GIT SAFETY: LOCAL COMMITS ONLY - NEVER PUSH                   ║
║                                                                 ║
║  ✅ git checkout -b {branch}     (create local branch)         ║
║  ✅ git add {files}              (stage specific files)        ║
║  ✅ git commit -m "..."          (local commit)                ║
║                                                                 ║
║  ❌ git push                     (NEVER - user pushes later)   ║
║  ❌ git push -u origin           (NEVER)                       ║
║  ❌ Any remote operations        (NEVER)                       ║
╚════════════════════════════════════════════════════════════════╝
```

## Verification Gate

Each work unit's Verification section contains commands that MUST pass:
- PHPStan static analysis
- PHPUnit tests
- Pint code style

All must exit with code 0 to proceed. Any failure = BLOCKED.

## Commit Message Format

```
WU-{N}: {Work unit title}

{Brief summary - 2-3 lines max}
```

No "Co-Authored-By" attribution line.

## Example Output

```
## Run Plan: ADVERTISING

🔀 Branch: Created advertising-feature (was on main)

### WU-01: database-models
⏳ Spawning agent...
✅ Agent complete
⏳ Running verification...
   ✅ phpstan: PASS
   ✅ tests: PASS
   ✅ pint: PASS
✅ Committed: abc1234

### WU-02: admin-controller
⏳ Spawning agent...
✅ Agent complete
⏳ Running verification...
   ❌ phpstan: FAIL (3 errors)

🛑 BLOCKED at WU-02

## Summary
- Completed: 1 work unit
- Commits: abc1234
- Status: BLOCKED (WU-02 failed verification)
- Remaining: 4 work units

Commits are local. When ready: git push -u origin advertising-feature
```

## Resources

- `.claude/skills/run-plan/skill.md` - Full orchestration logic
- `.claude/skills/run-plan/prompts/execute-unit.md` - Task agent prompt
