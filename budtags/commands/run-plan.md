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
3. **Execution Loop** (for each READY unit — may run independent units in parallel, but review + commit is always sequential per unit):
   - Updates MANIFEST: PENDING → IN PROGRESS
   - **Reads SHARED_CONTEXT.md and embeds its full contents inline into the spawned prompt** (v1.9 gating change — replaces the old "tell the subagent to Read it" model)
   - Spawns Task agent (per-unit `**Agent**:` field) in fresh context
   - Agent reads ONLY the WU file (SHARED_CONTEXT is already in its context window), implements all tasks, returns a Completion Report including a mandatory "Patterns Followed from Embedded Shared Context" section
   - **Orchestrator quality review (MANDATORY — runs in main context, NOT a subagent)**:
     - Run `composer check` — fix **all** issues found, not just ones from this WU's changes
     - Read `git diff` of the subagent's work — verify they stayed on track per the WU's task list and Files section
     - Verify `SHARED_CONTEXT.md` was actually updated — if the subagent skipped it, populate it directly before committing
     - Confirm no surprise files touched, no stubs, no half-done work
   - Run verification commands from the WU file (stub detection, phpstan, pint, tests)
   - On success: stage only listed WU files, commit, mark DONE, move to next
   - On failure: mark BLOCKED, stop, report what failed
4. **Completion Report**: Lists commits created (local only)

## Key Behaviors

| Feature | Behavior |
|---------|----------|
| Commits | **LOCAL ONLY** - never pushes to remote |
| On failure | Stops immediately, preserves state |
| Context | Fresh agent context per work unit |
| Continuity | SHARED_CONTEXT.md maintains naming/patterns across agents |
| Verification | Gate check with PHPStan/tests/Pint |

## Shared Context (v1.9)

Each agent starts fresh. `SHARED_CONTEXT.md` maintains continuity across them:
- Cache key naming patterns
- TypeScript types created
- PHP services created
- Route naming conventions
- Implementation decisions

**Gating change (v1.9):** The orchestrator reads SHARED_CONTEXT.md in a pre-spawn step and embeds its full contents inline into the spawned prompt. Subagents do NOT call Read on this file. They receive it as part of their context window. This eliminates the "subagent skipped the Read instruction" failure mode that motivated the change (subagents have their own auto-loaded skill prompts that compete with the user-message instruction to Read).

Each subagent's Completion Report now includes a mandatory "Patterns Followed from Embedded Shared Context" section listing at least 2 specific patterns reused, with row references or quotes. The orchestrator audits this section for substance during Orchestrator Review Step C.2 (in addition to the existing diff-based audit of new additions).

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

Every unit must pass TWO layers before committing. The orchestrator runs BOTH personally — do not delegate:

### Layer 1 — Orchestrator quality review (new, MANDATORY)

Run IN THE MAIN CONTEXT after the subagent returns, before running the WU's own verification:

1. `composer check` — fix every issue surfaced, regardless of whether the WU caused it (project rule: fix all). If `composer check` fails after the subagent's work, the orchestrator's job is to fix it directly, not punt back to a subagent.
2. `git diff --stat` + `git diff` on the subagent's changes — skim for: files outside the WU's declared Files section, stubs, TODO/FIXME, half-finished methods, tests that don't actually assert behavior.
3. Audit `{directory}/SHARED_CONTEXT.md` additions — did the subagent update the relevant tables (PHP Services, TypeScript Types, Routes, Decisions)? If blank where it shouldn't be, the orchestrator adds the obvious entries directly. If the subagent skipped it without reason, flag it in the progress log.
4. Audit the subagent's "Patterns Followed from Embedded Shared Context" section in the Completion Report. It must list at least 2 specific patterns with row references or quotes from the embedded SHARED_CONTEXT, and the diff must actually use them. Thin, generic, or fabricated entries = BLOCK and re-spawn (this is the v1.9 gating check that proves the embedded context was read).
5. Confirm the WU's task list is all checked off. If anything is unchecked, either finish it in the main context or mark the WU BLOCKED.

### Layer 2 — WU's own verification commands

Runs after Layer 1 passes. The commands specified in the WU's `## Verification` section:
- PHPStan static analysis
- PHPUnit tests
- Pint code style
- Any WU-specific extras (vitest, stub detection scripts, etc.)

All must exit with code 0 to proceed. Any failure = BLOCKED at this WU, stop immediately.

### Parallel execution

Independent units (per MANIFEST dependencies) MAY have their subagents dispatched in parallel. But review + commit is always one WU at a time, in sequence — the orchestrator reviews each WU's diff, fixes issues, runs verification, and commits before moving to the next review slot.

## Commit Message Format

Subject line = the work unit's **Description** column from MANIFEST.md, verbatim.
Body = 2-3 line summary of what was actually implemented.

```
{Work unit description from MANIFEST, as-is}

{2-3 line summary of what was implemented}
```

### Hard rules (applied to every commit — no exceptions)

- ❌ NEVER prefix the subject with "WU-01:", "WU-{N}:", or any work-unit identifier. The MANIFEST description stands alone.
- ❌ NEVER include a "Co-Authored-By:" trailer line.
- ❌ NEVER include a "🤖 Generated with Claude Code" line or any auto-attribution.
- ❌ NEVER append any boilerplate the orchestrator didn't explicitly write.
- ✅ Use a HEREDOC for multi-line commit bodies to preserve formatting.
- ✅ Stage ONLY the files listed in the WU's Files section — never `git add .` / `git add -A`.

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
- `.claude/skills/run-plan/prompts/shared-context-template.md` - SHARED_CONTEXT template
