#!/usr/bin/env python3
"""
PreToolUse Hook: Worktree Test-Database Isolation Guard

Parallel Claude sessions in git worktrees share the main tree's parallel test
databases (budtags_test, budtags_test_1..8), producing deadlocks, stale-schema
false positives, and gate re-runs that have nothing to do with the code under
test. This was the single most repeated infrastructure friction across sessions.

This hook DENIES test-suite invocations from inside a git worktree (where .git
is a file, not a directory) unless the command pins a worktree-specific database
via a leading `DB_DATABASE=` assignment, plus the worktree's own Redis test DB
pair (`REDIS_DB=` / `REDIS_CACHE_DB=`, recorded in its .env.testing by
setup.sh / assign-redis-db.sh). The deny message contains the exact
prefix to use, so the retry is mechanical. The main tree (.git is a directory)
is never touched by this hook.

Why a shell-exported DB_DATABASE is the ONE override that works:
  - phpunit.xml's <env name="DB_DATABASE"> is non-forced, so an already-set real
    environment variable wins over it.
  - phpdotenv is immutable, so .env.testing cannot override a real env var.
  - AppServiceProvider's ParallelTesting::setUpProcess and TestCase::setUp
    derive worker databases from the configured base name, so the whole
    <base>_1..8 fleet follows the export (auto-created and migrated on first
    run by setUpProcess).

Deny (not ask) on purpose: an ask would wedge unattended bypass-mode runs, and
the correct action is always the same mechanical retry.

Fail-open philosophy: if anything in this hook errors, it outputs nothing and
the tool call proceeds normally.
"""

import json
import os
import re
import sys

TEST_COMMAND = re.compile(
    r"(?:"
    r"composer\s+(?:run\s+)?(?:check|test|test-fast|test-parallel|migrate-test-dbs)(?!\S)"
    r"|artisan\s+test(?!\S)"
    r"|vendor/bin/(?:phpunit|paratest)\b"
    r")"
)

LEADING_CD = re.compile(r"^\s*cd\s+([^\s;&|]+)\s*&&")


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def worktree_root(start_dir: str):
    """Walk upward looking for .git; return the dir if .git is a FILE (worktree)."""
    current = os.path.abspath(start_dir)
    while True:
        git_path = os.path.join(current, ".git")
        if os.path.isdir(git_path):
            return None  # main tree
        if os.path.isfile(git_path):
            return current  # linked worktree
        parent = os.path.dirname(current)
        if parent == current:
            return None  # no repo at all
        current = parent


def db_slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug[:24].rstrip("_") or "wt"


def env_testing_value(root: str, name: str):
    """The worktree's own .env.testing value for `name`, or None."""
    try:
        with open(os.path.join(root, ".env.testing"), encoding="utf-8") as handle:
            for line in handle:
                if line.startswith(f"{name}="):
                    return line.split("=", 1)[1].strip() or None
    except OSError:
        return None
    return None


def pins(command: str, name: str, value: str) -> bool:
    return re.search(rf"\b{name}={re.escape(value)}(?!\S)", command) is not None


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return

    command = input_data.get("tool_input", {}).get("command", "")
    if not command or not TEST_COMMAND.search(command):
        return

    cd_match = LEADING_CD.match(command)
    effective_dir = os.path.expanduser(cd_match.group(1)) if cd_match else input_data.get("cwd", os.getcwd())

    root = worktree_root(effective_dir)
    if root is None:
        return  # main tree (or not a git repo): default DB names are correct

    # Name deliberately OUTSIDE the budtags_test% wildcard: stale-DB hygiene in
    # other sessions drops budtags_test_* and would take a worktree family named
    # budtags_test_<slug> mid-run (2026-08-06 incident: 302 tests died).
    database = f"budtags_{db_slug(os.path.basename(root))}_test"

    # Every suite's first worker FLUSHDBs its Redis cache DB at start, so a
    # worktree on the main tree's 14/15 wiped other running gates' keys
    # (2026-10-08). setup.sh / assign-redis-db.sh record the worktree's own
    # pair in its .env.testing; phpunit.xml's REDIS_CACHE_DB=15 beats that
    # file, so the command must export them like DB_DATABASE.
    redis_db = env_testing_value(root, "REDIS_DB")
    redis_cache_db = env_testing_value(root, "REDIS_CACHE_DB")
    if redis_db is None or redis_cache_db is None:
        deny(
            f"Worktree test-DB guard: worktree '{os.path.basename(root)}' has no "
            f"Redis test DB pair yet, so its suite would FLUSHDB the main tree's "
            f"Redis DB 15 under any other running gate. Assign one first: "
            f"`bash ~/Desktop/budtags-claude-plugin/budtags/skills/worktree/scripts/assign-redis-db.sh {root}` "
            f"(prints REDIS_DB=… REDIS_CACHE_DB=…), then re-run the SAME command "
            f"prefixed with DB_DATABASE={database} and those two."
        )
        return

    prefix = f"DB_DATABASE={database} REDIS_DB={redis_db} REDIS_CACHE_DB={redis_cache_db}"
    if (
        re.search(r"\bDB_DATABASE=", command)
        and pins(command, "REDIS_DB", redis_db)
        and pins(command, "REDIS_CACHE_DB", redis_cache_db)
    ):
        return  # pinned to its own databases

    deny(
        f"Worktree test-DB guard: this command runs inside git worktree "
        f"'{os.path.basename(root)}', which would collide with the main tree's "
        f"parallel test databases and Redis test DBs. Re-run the SAME command "
        f"prefixed with {prefix} (e.g. `{prefix} composer check`). "
        f"The {database}_1..14 worker databases are auto-created and migrated on "
        f"first run; create the base once if missing: "
        f"CREATE DATABASE IF NOT EXISTS `{database}` (creds in .env.testing)."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail open
