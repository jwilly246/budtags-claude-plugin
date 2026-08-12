#!/usr/bin/env bash
# Provision a depth-1 git worktree with an isolated parallel-test database family.
#
# Usage: setup.sh <branch-name> [base-ref]     (run from the MAIN budtags tree)
#   base-ref defaults to origin/main (fetched first, branched with --no-track).
#
# What it does, and why each step exists:
#   - Worktree folder DIRECTLY at the repo root (depth-1): the only layout the
#     IDE can even theoretically auto-detect; deeper paths are invisible.
#   - .git/info/exclude line: keeps the main tree's changes list clean without
#     touching tracked files.
#   - Copies .env and .env.testing (gitignored, so a fresh worktree has neither).
#   - Rewrites the worktree's .env.testing DB_DATABASE to budtags_<slug>_test,
#     creates that base database, and migrates it. Parallel workers derive
#     <base>_1..8 automatically (auto-created + migrated on first test run).
#   - APFS-clones vendor and public/build (cp -Rc: instant, copy-on-write) and
#     symlinks node_modules. Never symlink vendor (breaks the PHP autoloader).
set -euo pipefail

branch="${1:?usage: setup.sh <branch-name> [base-ref]}"
base_ref="${2:-origin/main}"

main_root="$(git rev-parse --show-toplevel)"
if [ -f "$main_root/.git" ]; then
    echo "ERROR: run this from the MAIN tree, not from inside a worktree" >&2
    exit 1
fi

dir_name="${branch//\//-}"
worktree="$main_root/$dir_name"
if [ -e "$worktree" ]; then
    echo "ERROR: $worktree already exists" >&2
    exit 1
fi

# Slug for the isolated DB family. The name sits deliberately OUTSIDE the
# budtags_test% wildcard: other sessions' stale-DB hygiene drops budtags_test_*
# and would take a family named budtags_test_<slug> mid-run (2026-08-06
# incident: 302 tests died on Unknown database).
db_slug="$(printf '%s' "$dir_name" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/_/g; s/^_+//; s/_+$//' \
    | cut -c1-24)"
test_db="budtags_${db_slug:-wt}_test"

if [ "$base_ref" = "origin/main" ]; then
    git -C "$main_root" fetch origin main
fi
git -C "$main_root" worktree add "$worktree" --no-track -b "$branch" "$base_ref"

grep -qxF "/$dir_name/" "$main_root/.git/info/exclude" 2>/dev/null \
    || echo "/$dir_name/" >> "$main_root/.git/info/exclude"

cp "$main_root/.env" "$worktree/.env"
sed -E "s/^DB_DATABASE=.*/DB_DATABASE=${test_db}/" "$main_root/.env.testing" > "$worktree/.env.testing"

db_host="$(sed -n 's/^DB_HOST=//p' "$main_root/.env.testing")"
db_user="$(sed -n 's/^DB_USERNAME=//p' "$main_root/.env.testing")"
db_pass="$(sed -n 's/^DB_PASSWORD=//p' "$main_root/.env.testing")"
mysql -h "${db_host:-127.0.0.1}" -u "${db_user:-root}" -p"$db_pass" \
    -e "CREATE DATABASE IF NOT EXISTS \`$test_db\`"

cp -Rc "$main_root/vendor" "$worktree/vendor"
if [ -d "$main_root/public/build" ]; then
    mkdir -p "$worktree/public"
    cp -Rc "$main_root/public/build" "$worktree/public/build"
fi
ln -s "$main_root/node_modules" "$worktree/node_modules"

(cd "$worktree" && DB_DATABASE="$test_db" php -d memory_limit=2G artisan migrate --env=testing --force)

cat <<SUMMARY

Worktree ready.
  path:      $worktree
  branch:    $branch (from $base_ref, --no-track)
  test DB:   $test_db  (workers ${test_db}_1..8 auto-provision on first run)

Run tests from the worktree as:
  DB_DATABASE=$test_db composer check

Cleanup after merge (from the main tree):
  rm "$worktree/node_modules"            # symlink — rm, NEVER rm -rf
  git worktree remove "$worktree"        # back up untracked plan files FIRST
  sed -i '' '\\|^/$dir_name/\$|d' .git/info/exclude
  mysql: DROP DATABASE ${test_db}; plus its _1..8 workers
SUMMARY
