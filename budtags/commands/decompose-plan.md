# Decompose Plan

Split a plan file into context-window-sized work units.

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
├── WU-01-database-models.md (Context-window-sized work)
├── WU-02-admin-controller.md
├── WU-03-admin-ui.md
├── WU-04-seller-controller.md
├── WU-05-seller-ui.md
└── ...
```

**Key Design:**
- Each work unit is sized for **one context window** (5-10 tasks)
- Tests are included **with** each unit (not separate)
- Only necessary domains are created (smart detection)
- Dependencies are tracked; `/run-plan` computes which units are READY
- Output is the input contract for `/run-plan`, which executes, verifies, and commits each unit

## Instructions

**Read the skill file first:** `.claude/skills/decompose-plan/skill.md`

Then:

1. Read the provided plan file completely
2. Identify which domains are needed (database, backend, frontend, integration)
3. Size work units appropriately (5-10 tasks each)
4. Determine dependencies between units
5. Create subdirectory with MANIFEST.md, SHARED_CONTEXT.md (pre-populated from the plan's Phase 0 research), and WU-*.md files
6. Output the list of created files
7. **STOP. Do not implement anything.**

## Work Unit Sizing

| Domain | Typical Scope per Unit |
|--------|------------------------|
| Database | 1-2 migrations + models + factories + tests |
| Controller | 1 controller + form requests + tests |
| Service | 1 service class + tests |
| Page | 1 Inertia page + components |
| Integration | 1 integration flow + tests |

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

- `.claude/skills/decompose-plan/skill.md` - Full skill documentation
- `.claude/skills/decompose-plan/MANIFEST_TEMPLATE.md` - Manifest template
- `.claude/skills/decompose-plan/WORK_UNIT_TEMPLATE.md` - Work unit template
- `.claude/skills/decompose-plan/patterns/` - Lightweight pattern references

## Example Output

For `ADVERTISING-FEATURE-PLAN.md`:

```
## Files Created

📁 ADVERTISING/
  ├── ✅ MANIFEST.md
  ├── ✅ SHARED_CONTEXT.md (pre-populated with research)
  ├── ✅ WU-01-database-models.md
  ├── ✅ WU-02-admin-controller.md
  ├── ✅ WU-03-admin-ui.md
  ├── ✅ WU-04-seller-controller.md
  ├── ✅ WU-05-seller-ui.md
  └── ✅ WU-06-analytics-integration.md

Decomposition complete. 6 work units + SHARED_CONTEXT created.
```
