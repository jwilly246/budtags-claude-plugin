---
name: worktree
description: Create and provision a git worktree for parallel work - depth-1 at repo root, isolated per-worktree test databases, correct IDE expectations. Use when the main tree is occupied by other agents or the user explicitly asks for a worktree.
version: 1.0.0
category: project
auto_activate:
  keywords:
    - "worktree"
    - "work tree"
    - "new worktree"
---

# Git Worktree Provisioning

Default for SMALL changes is still a branch in the MAIN tree (`git checkout -b <name>`). Reach for a worktree when:

1. The work is LONG: run-plan builders, cutover rehearsals, the full `composer check` gauntlet, anything that holds the tree for more than a few minutes. The user works in the main tree; tying it up all day is the failure mode, or
2. The main tree is OCCUPIED — live agents or uncommitted tracked changes on the checked-out branch, or
3. The user explicitly asks for one.

Never for URGENT prod incidents: work directly, no worktree, unless asked.

Never switch branches in the main tree when other agents are active there.

---

## Setup: one command

From the main tree root:

```bash
bash "${CLAUDE_PLUGIN_ROOT:-$HOME/Desktop/budtags-claude-plugin/budtags}/skills/worktree/scripts/setup.sh" <branch-name> [base-ref]
```

`base-ref` defaults to `origin/main` (fetched fresh, branched `--no-track` — there is deliberately NO local main branch). The script prints the worktree path, the isolated test database name, and the exact test command. **Relay all three to the user verbatim.**

What it provisions and why (if doing it by hand, every step is mandatory):

| Step | Why |
|------|-----|
| Folder directly at repo root (depth-1) | Deeper paths (`worktrees/x`, `.claude/worktrees/x`) are invisible to the IDE — verified failure mode |
| `.git/info/exclude` line | Keeps the main tree's changes list clean without touching tracked files |
| Copy `.env` + `.env.testing` | Gitignored — a fresh worktree has neither; every DB test dies without them |
| Rewrite `DB_DATABASE` to `budtags_<slug>_test`, create + migrate it | Isolated test DB family; workers `<base>_1..14` auto-provision on first parallel run |
| `cp -Rc vendor` (APFS clone) | Instant; NEVER symlink vendor (breaks the PHP autoloader) |
| `cp -Rc public/build` | Tests rendering Blade/Inertia views 500 without built assets |
| `ln -s node_modules` | Symlink is fine here; `rm` the link (never `rm -rf`) before removal |

---

## Running tests in a worktree

Always prefix with the worktree's database (the `worktree-test-db` hook denies unprefixed runs):

```bash
DB_DATABASE=budtags_<slug>_test composer check
```

- The shell export is the ONE override that works: `phpunit.xml`'s `<env>` is non-forced (real env wins) and dotenv is immutable (`.env.testing` can't override a real env var). Editing `.env.testing` alone does NOT change the phpunit DB.
- The name sits OUTSIDE the `budtags_test%` wildcard on purpose: stale-DB hygiene in other sessions drops `budtags_test_*`, and a family named inside the wildcard gets taken mid-run (2026-08-06: 302 tests died on Unknown database). Never name a worktree DB `budtags_test_<anything>`.
- Worker DBs `<base>_1..14` are created and migrated automatically on first run — a fresh worktree can never hit the stale-schema failure mode. First run is slower (8 fresh migrations); that is normal.
- After a migration lands in THIS worktree, stale-DB recovery targets `budtags_<slug>_test_*` only — never touch the main tree's `budtags_test_*`.

---

## IDE visibility (set expectations BEFORE creating it)

- Auto-detection CANNOT be promised even at depth-1. The only verified way the user gets a separate changes list is opening the folder in its own window (File → New Window → Open Folder).
- Tell the user the exact folder path and let THEM wire up visibility. NEVER run `cursor --add` / `code --add` — it converted the window to a multi-root workspace, killed terminals, and double-indexed the codebase (2026-07-28 incident).

---

## Cleanup after merge

1. Stop any agent still working in the worktree FIRST (removing the dir under a live agent is the failure mode).
2. **Back up untracked plan files** (`*-PLAN.md`, plan dirs) — `git worktree remove` destroys them.
3. `rm <worktree>/node_modules` (symlink — `rm`, never `rm -rf`).
4. `git worktree remove <path>`, then `cd` out of the removed directory.
5. Drop the `/<name>/` line from `.git/info/exclude`.
6. Drop the DB family: `budtags_<slug>_test` and `budtags_<slug>_test_1..14`.
7. Confirm the main tree is free: `git worktree list`, and `git -C <main tree> branch --show-current` still shows the branch the user left it on.

## Never copy files across branches

Build a worktree's files from its own base ref. Never `cp` a file from another branch or the main tree into it: a stale copy silently reverts other work (TerpeneData.php, 2026-09). Need a change from elsewhere? `git merge` or `git cherry-pick` it.
