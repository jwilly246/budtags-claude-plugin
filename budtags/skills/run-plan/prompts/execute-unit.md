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

## Commit Mode (read it off the WU file)

**If the WU's Tasks heading is `## Tasks (one commit each)`:** you commit after EVERY task.
- Do the task, run its targeted checks (below), then commit ONLY the files that task touched, by explicit path (`git add path/a.php path/b.tsx`; never `git add .` / `-A`; whole files, never partial staging).
- Subject line = the task's bold text, verbatim. Body = 2-3 lines saying what the commit implements. Use a HEREDOC. No `WU-XX:` prefix, no `Co-Authored-By:`, no "Generated with Claude Code" (the git-safety hook denies those).
- The repo's pre-commit hook runs Pint and PHPStan on the staged PHP files and may reformat them; if it aborts the commit, fix what it reports and commit again. Never `--no-verify`.
- Before a commit that touches TypeScript, the hook does nothing for you: run `npx vitest run <the touched dirs>` and `npx eslint <the changed .ts/.tsx files>` yourself. Before a PHP commit also run the task's `php artisan test --filter=...`. Tests ride in the same commit as the code they cover.
- Never run `composer check`, `npm run lint` on the whole tree, or the full test suite. The full gauntlet runs once at the end of the branch, by the orchestrator, through review-branch.
- Never push, never amend, never reset, never rebase. Never commit files under `{directory}/`.
- If a task cannot be finished, stop, leave the branch clean (no half-committed task), and explain under "Issues".

**If the heading is plain `## Tasks`:** do NOT commit and do NOT run verification. The orchestrator handles that after your report.

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
| Gate hygiene | No comment containing the bare words `temporary`, `placeholder`, `stub` or `implement later`; no single-line empty `{}` method/constructor body; no `axios.*(` calls inside component files (put them in a data-layer module); no `export type` / `export interface` / `export enum` in any ts/tsx file outside `resources/js/Types/` (declare shared types in the domain type file and import them; components, hooks and pages hold local, non-exported types only) — the orchestrator's gate rejects all four |

## Code Quality

Every method must be fully implemented. No stubs.

**These will cause rejection:**
- `// TODO`, `// FIXME`
- Empty method bodies
- `throw new Exception('Not implemented')`
- `any` types
- An exported type declared outside `resources/js/Types/` (the gate fails the unit; put it in `types.tsx` / `types-metrc.tsx` / `types-marketplace.tsx` / the matching domain file)
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

### Commits (task-per-commit mode)
One line per task, in order: `<short sha> <subject>` plus the targeted checks that ran green before it (e.g. `MetrcItemCreateService filter 6/6; pint+phpstan via hook`). Omit this section in legacy mode.

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

The orchestrator will read your full commit range (`git diff <unit start>..HEAD`), run gate.sh over it (Create files exist, scope audit of every committed file against the WU's Files list, stub and pattern detectors), run the WU's Verification block, audit the "Patterns Followed" section for substance, and audit your SHARED_CONTEXT additions against your Completion Report before marking the unit DONE. The full `composer check` runs once, at the end of the branch, through review-branch. A thin "Patterns Followed" section, fabricated row references, an undeclared file in a commit, or silently-skipped SHARED_CONTEXT updates will block the unit.
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

Read `**Agent**:` field from work unit. **OMIT the `model` parameter** — every specialist in the table declares `model: opus` in its frontmatter, and that is the execution model by policy (the session model orchestrates, Opus executes). Only override if the user explicitly asks.

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

**Has:** Read, Edit, Write, Bash, Glob, Grep, MCP tools, the WU file path, the SHARED_CONTEXT content embedded inline in the prompt, git commit rights on the feature branch (task-per-commit mode; the git-safety hook still denies pushes, bulk adds, deploy-branch commits and boilerplate trailers)

**Does NOT have:** Conversation history, knowledge of other work units, the SHARED_CONTEXT file path (it should not Read the file, the contents are already in context)

Each work unit is self-contained via the WU file (read by the agent) and the SHARED_CONTEXT content (embedded by the orchestrator into the spawned prompt).
