#!/usr/bin/env bash
# Give a worktree its own pair of Redis test databases.
#
# Usage: assign-redis-db.sh <worktree-path>     (setup.sh calls it; run it by
#        hand for a worktree made before this existed)
#
# Why: every test suite's first worker FLUSHDBs its Redis cache DB at start
# (AppServiceProvider ParallelTesting::setUpProcess). With every worktree on
# the main tree's 14/15, starting a gate in one worktree wiped the keys of a
# gate already running in another, and its tests failed on missing stamps.
#
# Pairs come from 16-63 (local Redis runs `databases 64`); the main tree keeps
# 14 (default connection) / 15 (cache connection), dev keeps 0-3. The pair is
# written to the worktree's .env.testing as REDIS_DB / REDIS_CACHE_DB. That
# file is the record: the next free pair is the lowest one no other worktree's
# .env.testing names, so removing a worktree frees its pair.
#
# phpunit.xml's non-forced <env REDIS_CACHE_DB=15> is set before phpdotenv
# reads .env.testing, so the numbers only take effect when the test command
# exports them; the worktree-test-db hook requires that and names the prefix.
set -euo pipefail

worktree="$(cd "${1:?usage: assign-redis-db.sh <worktree-path>}" && pwd)"
env_file="$worktree/.env.testing"
[ -f "$env_file" ] || { echo "ERROR: $env_file not found" >&2; exit 1; }

existing="$(sed -n 's/^REDIS_CACHE_DB=//p' "$env_file")"
if [ -n "$existing" ]; then
    echo "REDIS_DB=$(sed -n 's/^REDIS_DB=//p' "$env_file") REDIS_CACHE_DB=$existing (already assigned)"
    exit 0
fi

databases="$(redis-cli CONFIG GET databases 2>/dev/null | sed -n 2p)"
if [ "${databases:-16}" -lt 64 ]; then
    echo "ERROR: local Redis has ${databases:-16} databases; set 'databases 64' in /opt/homebrew/etc/redis.conf and run 'brew services restart redis'" >&2
    exit 1
fi

taken="$(git -C "$worktree" worktree list --porcelain \
    | sed -n 's/^worktree //p' \
    | while read -r path; do
        [ "$path" = "$worktree" ] && continue
        sed -n 's/^REDIS_CACHE_DB=//p' "$path/.env.testing" 2>/dev/null || true
    done)"

cache_db=""
for candidate in $(seq 17 2 63); do
    if ! printf '%s\n' "$taken" | grep -qx "$candidate"; then
        cache_db="$candidate"
        break
    fi
done
[ -n "$cache_db" ] || { echo "ERROR: all 24 worktree Redis pairs are taken; remove a finished worktree" >&2; exit 1; }
default_db=$((cache_db - 1))

# Start the pair empty: a pair freed by a removed worktree may hold its keys.
redis-cli -n "$default_db" FLUSHDB > /dev/null
redis-cli -n "$cache_db" FLUSHDB > /dev/null

printf 'REDIS_DB=%s\nREDIS_CACHE_DB=%s\n' "$default_db" "$cache_db" >> "$env_file"
echo "REDIS_DB=$default_db REDIS_CACHE_DB=$cache_db"
