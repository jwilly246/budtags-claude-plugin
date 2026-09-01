# Execute Work Unit Prompt

The prompt template for spawning execution subagents (Agent tool). Execution-focused—all research was done in plan/decompose phases.

---

## Prompt Template

```
You are executing work unit {WU_ID} for the {FEATURE_NAME} feature.

## Your Task

Implement everything in: `{directory}/WU-{N}-{slug}.md`

## Step 0 (MANDATORY, do this FIRST)

Your first tool call MUST be `Read` on `{directory}/WU-{N}-{slug}.md`. Read the full file before invoking any Edit, Write, or MultiEdit tool.

## Embedded Shared Context

The orchestrator has read `{directory}/SHARED_CONTEXT.md` and embedded its full contents inline below. Treat this as authoritative. Do NOT call Read on SHARED_CONTEXT.md (the contents are already in your context window). Do NOT re-explore the codebase to rediscover patterns documented here.

NOTE: your WU file's "Required Context" section may begin with an instruction like "READ SHARED_CONTEXT.md" — that instruction predates this embedding mechanism. SKIP that read; everything it refers to is the block below. Follow the REST of the Required Context reading list normally.

You will reference these embedded patterns in your Completion Report's "Patterns Followed" section, so read this block carefully.

---

{SHARED_CONTEXT_INLINE}

---

## Execution Rules

| Rule | Pattern |
|------|---------|
| Organization scoping | `->where('organization_id', request()->user()->active_org_id)` |
| Logging | `LogService::store()` (never `Log::` facade) |
| Flash messages | `->with('message', '...')` (not `'success'`) |
| Method names | snake_case: `fetch_all`, `create`, `delete` |
| Forms | Inertia `useForm` (never useState/axios for mutations) |
| Types | No `any` in TypeScript |
| Tests | PHPUnit (not Pest) |
| Reuse first | Never create a helper/component/service/type that near-duplicates one in the embedded context or the codebase — use or extend the existing one. The embedded "Reuse Verdicts" table is binding |

## Code Quality

Every method must be fully implemented. No stubs.

**These will cause rejection:**
- `// TODO`, `// FIXME`
- Empty method bodies
- `throw new Exception('Not implemented')`
- `any` types
- New code that duplicates an existing component/service/helper/type, or that creates a parallel copy of anything the embedded "Reuse Verdicts" table marked REUSE or EXTEND — the orchestrator's diff audit checks for this

If something is unclear: implement your best judgment and document it in "Decisions Made" section.

## When Done

1. **MANDATORY: Update `{directory}/SHARED_CONTEXT.md`.** For each of these categories, either add the entries you created OR write "None added this WU" with a one-line reason. Do NOT leave silent gaps — the orchestrator audits this file via `git diff` and will mark the WU BLOCKED if updates are missing without explanation:
   - PHP Services & Classes (created)
   - TypeScript Types (created)
   - Routes Added
   - Cache Keys (created)
   - Enums Created
   - Database Columns & Naming
   - Implementation Decisions
2. Update the work unit's "Decisions Made" section if you made implementation choices
3. Check every `- [ ]` task in the WU — they must all be `- [x]` before you report done
4. Report using the template below

---
## Completion Report

### Patterns Followed from Embedded Shared Context (MANDATORY, falsifiable)

List at least 2 specific patterns, components, types, services, or conventions from the embedded shared context (the block above between the `---` separators) that you actually used in this WU. Reference the table row or quote the line directly. Examples:

- **Component reused:** Used `Modal` from the "Available UI Components (Core)" table (row: `@/Components/Modal`) instead of creating a new modal wrapper.
- **Convention followed:** Method naming snake_case verb-first per "Critical Patterns > Method Naming" (`create()` not `store()`).
- **Service reused:** Called `LogService::store()` per the "Core PHP Services" table.

If you genuinely reused nothing from the embedded context (rare, requires justification), write a paragraph explaining why this WU is orthogonal to every entry. The orchestrator treats thin or generic answers (e.g. "followed conventions", "used existing components") as evidence the embedded context was not read, and will mark the WU BLOCKED.

### Files Created
- `path/to/file.php` — what it contains

### Files Modified
- `path/to/file.php` — what changed and why

### Tasks Completed
- [x] Task 1
- [x] Task 2
(If any are still `- [ ]`, explain why under "Issues")

### SHARED_CONTEXT Updates (EXPLICIT — required)
List exact entries added to each table. Example:
- **PHP Services & Classes:** added `LeafLinkWebhookContext` (app/Services/LeafLink/LeafLinkWebhookContext.php, "scoped E2 flag", WU-01)
- **Routes Added:** none (no route changes this WU)
- **Implementation Decisions:** added "Used Laravel Context facade over custom static — rationale: request-scoped cleanup"

If a category genuinely has nothing, write `none (reason)` — do NOT omit the category heading.

### Decisions Made
- Chose X because Y

### Issues
- None
---

Do NOT run verification or commit. The orchestrator handles that.

The orchestrator will personally run `composer check`, read your full diff, audit the "Patterns Followed" section for substance, audit your SHARED_CONTEXT additions against your Completion Report, and verify every task is checked before committing. A thin "Patterns Followed" section, fabricated row references, or silently-skipped SHARED_CONTEXT updates will block the commit.
```

---

## Variable Substitution

| Variable | Source |
|----------|--------|
| `{directory}` | Plan directory (e.g., `ADVERTISING`) |
| `{N}` | Work unit number (e.g., `01`) |
| `{slug}` | Work unit slug (e.g., `database-models`) |
| `{WU_ID}` | Full ID (e.g., `WU-01`) |
| `{FEATURE_NAME}` | Feature name from directory |

---

## Agent Type Selection

Read `**Agent**:` field from work unit. **OMIT the `model` parameter** — the subagent inherits the session model (the strongest available). Only override if the user explicitly asks. (The old `model: "opus"` hard-code silently downgraded execution agents once newer session models shipped.)

| Agent Value | subagent_type |
|-------------|---------------|
| `metrc-specialist` | `budtags:metrc-specialist` |
| `quickbooks-specialist` | `budtags:quickbooks-specialist` |
| `leaflink-specialist` | `budtags:leaflink-specialist` |
| `tanstack-specialist` | `budtags:tanstack-specialist` |
| `react-specialist` | `budtags:react-specialist` |
| `php-developer` | `budtags:php-developer` |
| `typescript-developer` | `budtags:typescript-developer` |
| `fullstack-developer` | `budtags:fullstack-developer` (default) |

---

## Agent Capabilities

**Has:** Read, Edit, Write, Bash, Glob, Grep, MCP tools, the WU file path, the SHARED_CONTEXT content embedded inline in the prompt

**Does NOT have:** Conversation history, knowledge of other work units, the SHARED_CONTEXT file path (it should not Read the file, the contents are already in context)

Each work unit is self-contained via the WU file (read by the agent) and the SHARED_CONTEXT content (embedded by the orchestrator into the spawned prompt).
