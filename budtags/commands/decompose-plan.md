# Decompose Plan

Split a plan file into branch-sized work units (one review boundary each; every task = one commit).

## Purpose

**FILE CREATION ONLY.** This command creates a subdirectory with a manifest and work unit files. It does NOT implement any code.

## Usage

```
/decompose-plan <plan-file>
```

**Example:**
```
/decompose-plan ADVERTISING-FEATURE-PLAN.md
```

## What It Creates

A subdirectory named after the feature containing:

```
ADVERTISING/
├── MANIFEST.md              (Index, dependencies, progress tracking)
├── SHARED_CONTEXT.md        (Pre-populated research for execution agents)
├── WU-01-prefactor.md        (Branch-sized: 5-20 tasks, one commit each)
├── WU-02-foundations.md
├── WU-03-server-core.md
├── WU-04-client-block.md
├── WU-05-surfaces.md
└── ...
```

**Key Design:**
- Each work unit is ONE REVIEW BOUNDARY (prefactor / foundations / server-core / client-block / surfaces / rollout), 5-20 tasks, **every task = one commit** (the bold task text is the commit subject)
- Tests ride **in the commit** that adds the code (never a separate unit or task)
- No `composer check` per unit: the branch's one full gauntlet is `/review-branch` at the end
- Only necessary domains are created (smart detection)
- Dependencies are tracked; `/run-plan` computes which units are READY
- Output is the input contract for `/run-plan`, which executes, verifies, and commits each unit

## Instructions

**Load the skill first:** invoke `budtags:decompose-plan` via the Skill tool (its SKILL.md lives in the installed plugin at `~/.claude/plugins/marketplaces/budtags-claude-plugin/budtags/skills/decompose-plan/SKILL.md` — there is NO repo-local `.claude/skills/decompose-plan/` copy).

Then:

1. Read the provided plan file completely
2. Identify which domains are needed (database, backend, frontend, integration)
3. Cut units at review boundaries (5-20 commit-sized tasks each; the MANIFEST carries the Execution Contract)
4. Determine dependencies between units
5. Create subdirectory with MANIFEST.md, SHARED_CONTEXT.md (pre-populated from the plan's Phase 0 research), and WU-*.md files
6. Output the list of created files
7. **STOP. Do not implement anything.**

## Work Unit Sizing

| Unit (review boundary) | Typical scope | Commits |
|------------------------|---------------|---------|
| prefactor | behaviour-preserving extractions + call-site re-points | 3-10 |
| foundations | the branch's ONE migration (task 1, NEW file) + models/settings + small primitives | 4-10 |
| server-core | services, orchestration, endpoints, validation | 4-10 |
| client-block | types, hooks, components nothing mounts yet | 4-10 |
| surfaces | wiring into existing modals/pages/tables | 3-8 |
| rollout | backfill commands, gates, announcements | 2-6 |

## Critical Rules

```
╔════════════════════════════════════════════════════════════════╗
║  CREATE MARKDOWN FILES ONLY. DO NOT WRITE APPLICATION CODE.    ║
║                                                                 ║
║  After creating files:                                          ║
║  - List the files you created                                   ║
║  - Say "Decomposition complete"                                 ║
║  - STOP                                                         ║
║                                                                 ║
║  DO NOT:                                                        ║
║  - Offer to start implementation                                ║
║  - Ask "Ready for WU-01?"                                       ║
║  - Write any PHP/TypeScript code                                ║
║  - Create migrations, models, or controllers                    ║
╚════════════════════════════════════════════════════════════════╝
```

## Resources

(all under `~/.claude/plugins/marketplaces/budtags-claude-plugin/budtags/skills/decompose-plan/`)

- `SKILL.md` - Full skill documentation
- `MANIFEST_TEMPLATE.md` - Manifest template (Execution Contract section is mandatory)
- `WORK_UNIT_TEMPLATE.md` - Work unit template (`## Tasks (one commit each)`)
- `patterns/` - Lightweight pattern references

## Example Output

For `ADVERTISING-FEATURE-PLAN.md`:

```
## Files Created

📁 ADVERTISING/
  ├── ✅ MANIFEST.md
  ├── ✅ SHARED_CONTEXT.md (pre-populated with research)
  ├── ✅ WU-01-prefactor.md          (4 commits)
  ├── ✅ WU-02-foundations.md        (6 commits)
  ├── ✅ WU-03-server-core.md        (7 commits)
  ├── ✅ WU-04-client-block.md       (5 commits)
  └── ✅ WU-05-surfaces.md           (4 commits)

Decomposition complete. 5 work units (26 commits) + SHARED_CONTEXT created.
```
