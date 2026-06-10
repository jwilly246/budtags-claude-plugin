# Run Plan

Execute work units from a decomposed plan autonomously.

## Purpose

**AUTONOMOUS EXECUTION.** This command reads a MANIFEST, executes READY work units via Agent-tool subagents, runs verification gates, and commits after each successful unit—all without manual intervention.

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
3. **Execution Loop** (for each READY unit — serial by default: one dispatch at a time, review + commit before the next; parallel dispatch only on explicit user request):
   - Updates MANIFEST: PENDING → IN PROGRESS
   - **Reads SHARED_CONTEXT.md and embeds its full contents inline into the spawned prompt** (v1.9 gating change — replaces the old "tell the subagent to Read it" model)
   - Spawns subagent via the Agent tool (per-unit `**Agent**:` field; OMIT the model param — inherit session model) in fresh context
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

**Load the skill first:** invoke `budtags:run-plan` via the Skill tool (its SKILL.md lives in the
installed plugin at `~/.claude/plugins/marketplaces/budtags-claude-plugin/budtags/skills/run-plan/SKILL.md` —
there is NO repo-local `.claude/skills/run-plan/` copy).

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

### Layer 1 — Orchestrator judgment review (MANDATORY, main context)

Run after the subagent returns, before the mechanical gate:

1. `git diff --stat` + `git diff` on the subagent's changes — does the diff actually implement the WU's tasks? Style matches siblings? Tests assert real behavior? All "Modify" files actually modified?
2. Audit `{directory}/SHARED_CONTEXT.md` additions — did the subagent update the relevant tables (PHP Services, TypeScript Types, Routes, Decisions)? If blank where it shouldn't be, the orchestrator adds the obvious entries directly.
3. Audit the subagent's "Patterns Followed from Embedded Shared Context" section. At least 2 specific patterns with row references or quotes, and the diff must actually use them. Thin, generic, or fabricated entries = the embedded context was ignored.
4. Confirm the WU's task list is all checked off. If anything is unchecked, either finish it in the main context or mark the WU BLOCKED.

### Layer 2 — The mechanical gate (gate.sh) + WU-specific commands

```bash
"$HOME/.claude/plugins/marketplaces/budtags-claude-plugin/budtags/skills/run-plan/scripts/gate.sh" {directory}/WU-{N}-{slug}.md
```

One command: Create-files exist → scope audit vs the WU's Files section → stub detection → frontend pattern check → full `composer check`. Exit 0 = pass; exit 1 = fix every reported issue in main context and re-run; exit 2 = harness malfunction (report to user, don't mark BLOCKED). Then run the WU's own `## Verification` commands that gate.sh doesn't subsume (test --filter, migrate/rollback, etc.).

After committing a migration WU: `composer migrate-test-dbs` (parallel test DBs go stale and the next WU's tests fail confusingly otherwise).

On failure: ONE bounded re-spawn with the failure output embedded is allowed for implementation misses; plan defects or a second failure = BLOCKED at this WU, stop immediately.

### Execution order

Serial by default (operator preference): dispatch one WU's subagent, review, verify, and commit it before dispatching the next. Independent units MAY be dispatched in parallel ONLY when the user explicitly asks; review + commit is always one WU at a time, in sequence, regardless.

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

(all under `~/.claude/plugins/marketplaces/budtags-claude-plugin/budtags/skills/run-plan/`)

- `SKILL.md` - Full orchestration logic
- `prompts/execute-unit.md` - Execution subagent prompt template
- `prompts/shared-context-template.md` - SHARED_CONTEXT template
- `scripts/detect-stubs.sh`, `scripts/detect-wrong-patterns.sh` - verification scripts
