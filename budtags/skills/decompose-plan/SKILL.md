---
name: decompose-plan
description: Decomposes a plan file into context-window-sized work units with dependency tracking. FILE CREATION ONLY - does NOT implement or execute any code.
version: 3.3.1
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

**PURPOSE:** Create context-window-sized work units from a plan. Nothing more.

## CRITICAL RULES

```
╔══════════════════════════════════════════════════════════════════╗
║  THIS SKILL CREATES FILES. IT DOES NOT IMPLEMENT CODE.           ║
║                                                                   ║
║  ✅ DO: Create markdown files (manifest + work units)             ║
║  ✅ DO: Analyze plan for intelligent decomposition                ║
║  ✅ DO: Determine dependencies between work units                 ║
║  ✅ DO: Include tests WITH each work unit (not separate)          ║
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

Takes a plan file and creates a **subdirectory** with context-window-sized work units:

```
{FEATURE}/
├── MANIFEST.md                      (Index, dependencies, progress)
├── SHARED_CONTEXT.md                (Pre-populated research from create-plan)
├── WU-01-{description}.md           (~150-250 lines)
├── WU-02-{description}.md           (~150-250 lines)
├── WU-03-{description}.md           (~150-250 lines)
└── ...
```

**Key Change:** Work units are sized for ONE context window session (5-10 tasks each), not large phases.

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

### Step 1.5: Extract Research into SHARED_CONTEXT.md

If the plan contains **Phase 0 Research** (component inventory, type inventory, service inventory, naming patterns), create `{FEATURE}/SHARED_CONTEXT.md` and pre-populate it.

Use the template from `prompts/shared-context-template.md` and fill in:

| Plan Section | SHARED_CONTEXT Section |
|--------------|------------------------|
| Component inventory | Available UI Components (from create-plan) |
| Type inventory | Existing TypeScript Types (from create-plan) |
| Service inventory | Existing PHP Services (from create-plan) |
| Naming patterns | Naming Conventions |
| Existing routes | Routes (existing) |

**Example pre-population:**

```markdown
## Available UI Components (from create-plan)

| Component | Location | Key Props |
|-----------|----------|-----------|
| Button | resources/js/Components/Button.tsx | primary, secondary, disabled, loading |
| TextInput | resources/js/Components/Inputs.tsx | value, onChange, errors |
| DataTable | resources/js/Components/DataTable.tsx | columns, data, pagination |
```

**Why this matters:** Work unit executors will READ this file instead of re-discovering these components. This eliminates 30-50 redundant exploration tool calls per agent.

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

### Step 3: Size Work Units

Each work unit should be **5-10 actionable tasks** completable in one context window.

| Work Type | Scope per Work Unit |
|-----------|---------------------|
| Database | 1-2 migrations + 1-2 models + factories + tests |
| Controller | 1 controller with methods + form requests + tests |
| Service | 1 service class + tests |
| Page | 1 Inertia page + key components |
| Components | 2-3 related components |
| Integration | 1 integration endpoint/flow + tests |

**Include tests WITH each work unit, not as separate units.**

Tests must follow the `budtags-testing` skill principles: test behaviors (not implementation), one reason to fail per test, self-contained data setup, and exact assertions. For frontend work units, include Vitest tests alongside components.

### Step 3.5: Assign Agent Type to Each Work Unit

Based on work unit content, assign the best specialist agent. The agent type determines which skills are auto-loaded when the work unit is executed.

| Work Content | Agent Type | Auto-Loaded Skills |
|--------------|------------|-------------------|
| Metrc API calls, sync logic | `metrc-specialist` | metrc-api, verify-alignment |
| QuickBooks integration | `quickbooks-specialist` | quickbooks, verify-alignment |
| LeafLink marketplace | `leaflink-specialist` | leaflink, verify-alignment |
| TanStack Query/Table/Virtual | `tanstack-specialist` | 6 tanstack-* skills, verify-alignment |
| React components, modals, forms | `react-specialist` | verify-alignment |
| Backend controllers, services | `php-developer` | (none - reads patterns) |
| Database migrations, models | `php-developer` | (none - reads patterns) |
| Mixed frontend + backend | `fullstack-developer` | (none - fallback) |

**CRITICAL for Metrc work units:** Any work unit that involves MetrcApi controller methods MUST include a task to verify `$api->set_user(request()->user())` is called before any API interaction. Queue jobs must accept User via constructor and call `$api->set_user($this->user)`. See `METRC_API_RULES.md` "User Context Management" section.

**Selection Priority:**
1. If work involves a specific integration (Metrc, QuickBooks, LeafLink), use that specialist
2. If work is TanStack-heavy (Query, Table, Virtual), use `tanstack-specialist`
3. If work is frontend-only (React/Inertia), use `react-specialist`
4. If work is backend-only (Laravel), use `php-developer`
5. If work spans frontend and backend, use `fullstack-developer`

Add `**Agent**:` and `**Skills**:` fields to each work unit's frontmatter.

### Step 4: Determine Dependencies

Build dependency graph:
- Database work has no dependencies
- Models depend on migrations
- Controllers depend on models
- Pages depend on controllers
- Integration depends on relevant backend

```
WU-01 (Database/Models)
  └── WU-02 (Admin Controller)
        └── WU-04 (Admin UI)
  └── WU-03 (Seller Controller)  [parallel with WU-02]
        └── WU-05 (Seller UI)
```

### Step 5: Extract Context for Each Unit

For each work unit, include ONLY:
- Context directly relevant to that unit
- Decisions that affect implementation
- Constraints to follow
- Pattern references (link to patterns/, don't embed)

### Step 6: Create Files

Create all files in `{FEATURE}/` subdirectory:

1. **SHARED_CONTEXT.md** - Using `prompts/shared-context-template.md`, pre-populated with research from Step 1.5
2. **MANIFEST.md** - Using `MANIFEST_TEMPLATE.md`
3. **WU-{N}-{description}.md** - Using `WORK_UNIT_TEMPLATE.md` for each unit

### Step 7: Output File List and STOP

```
## Files Created

📁 ADVERTISING/
  ├── ✅ SHARED_CONTEXT.md (pre-populated with research)
  ├── ✅ MANIFEST.md
  ├── ✅ WU-01-database-models.md
  ├── ✅ WU-02-admin-controller.md
  ├── ✅ WU-03-admin-ui.md
  ├── ✅ WU-04-seller-controller.md
  ├── ✅ WU-05-seller-ui.md
  └── ✅ WU-06-analytics-integration.md

Decomposition complete. 6 work units + SHARED_CONTEXT created.
```

**THEN STOP. DO NOT OFFER TO IMPLEMENT. DO NOT ASK ABOUT NEXT STEPS.**

---

## Work Unit Sizing Examples

### ❌ TOO LARGE (old approach)
```markdown
# Phase 2: Backend
- AdminAdController (5 methods)
- SellerAdController (4 methods)
- AnalyticsService
- 8 route definitions
- 6 form requests
```
This is ~500+ lines and multiple context windows.

### ✅ RIGHT SIZE (new approach)
```markdown
# WU-02: Admin Controller

## Tasks
1. [ ] Create AdminAdController with fetch_all, fetch_one
2. [ ] Create StoreAdRequest with validation
3. [ ] Add routes for admin ad management
4. [ ] Write AdminAdControllerTest for all methods
5. [ ] Run PHPStan on new files

## Files
- app/Http/Controllers/Admin/AdController.php
- app/Http/Requests/Admin/StoreAdRequest.php
- routes/admin.php (modify)
- tests/Feature/Admin/AdControllerTest.php
```
This is ~150 lines and one focused session.

---

## Pattern References

Work units should **reference** patterns, not embed them:

```markdown
## Patterns to Follow
- See: `patterns/backend-patterns.md` for controller structure
- See: `patterns/test-patterns.md` for organization scoping tests
```

Pattern files are in `.claude/skills/decompose-plan/patterns/`:
- `database-patterns.md` - Model and migration patterns
- `backend-patterns.md` - Controller and service patterns
- `frontend-patterns.md` - React/Inertia patterns
- `test-patterns.md` - PHPUnit + Vitest test patterns (references `budtags-testing` skill for full philosophy)

---

## Available Resources

- `MANIFEST_TEMPLATE.md` - Template for manifest file
- `WORK_UNIT_TEMPLATE.md` - Template for work units
- `prompts/shared-context-template.md` - Template for SHARED_CONTEXT.md (from run-plan skill)
- `patterns/*.md` - Lightweight pattern references

---

## What Happens After

The user will:
1. Review the created MANIFEST and work units
2. Pick an available (READY) work unit to start
3. Complete one work unit per session
4. Mark units complete in MANIFEST as they progress
5. Check MANIFEST for next available work

**This skill's job ends when the files are created.**

---

## Anti-Patterns (DO NOT DO THESE)

❌ "Now let's start implementing WU-01..."
❌ "Ready to begin the first work unit?"
❌ "I'll create the migration for you..."
❌ Creating 4 rigid phases regardless of plan content
❌ Embedding 200-line checklists in each file
❌ Separating tests into their own work units

## Correct Behavior

✅ Create appropriately-sized work units (5-10 tasks each)
✅ Include tests WITH the code they test
✅ Only create work units for domains in the plan
✅ Reference patterns instead of embedding them
✅ List the files created
✅ Say "Decomposition complete"
✅ Stop responding
