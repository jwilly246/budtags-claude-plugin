#!/bin/bash
#
# Work Unit Gate — the single mechanical verification command for run-plan.
#
# Usage: gate.sh <path/to/WU-file.md> [--since <ref>] [--composer]
#   Run from the PROJECT REPO ROOT (where composer.json lives).
#
# Performs, in order:
#   1. Parse the WU's "## Files" section (backticked paths under ### Create / ### Modify)
#   2. Verify every "Create" file actually exists
#   3. Scope audit:
#        - uncommitted tracked changes outside the declared set = FAIL
#        - with --since <ref>: files changed by the commits in <ref>..HEAD outside the
#          declared set = FAIL (this is the audit that matters for task-per-commit
#          units, whose working tree is clean by the time the orchestrator reviews)
#        - pre-existing untracked clutter outside the plan dir = WARN only
#   4. Stub detection (detect-stubs.sh) on declared code files
#   5. Frontend pattern check (detect-wrong-patterns.sh) on declared ts/tsx files
#   6. Type placement: every `export type|interface|enum` a unit ADDS to a ts/tsx
#      file outside resources/js/Types/ is a failure (components, hooks and pages
#      may hold local, non-exported types only). Checks the added lines of the
#      --since range plus the working tree, so pre-existing exports in a touched
#      file do not fire; a brand-new untracked file is checked whole.
#
# It does NOT run `composer check`. The full gauntlet runs ONCE per branch, at the
# end, through the review-branch skill (project rule: no composer check between
# commits or units). `--composer` opts in for the rare case a human wants it here;
# `--skip-composer` is accepted and ignored so older WU files keep working.
#
# Exit codes:
#   0 = gate PASSED
#   1 = gate FAILED (report printed — every failure, not just the first)
#   2 = usage / parse error (script could not do its job; NOT a code failure)
#
# Deliberately NOT using `set -e`: grep/test failures are data here, not errors.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

WU_FILE=""
SINCE_REF=""
RUN_COMPOSER=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --since)
            SINCE_REF="$2"
            shift 2
            ;;
        --since=*)
            SINCE_REF="${1#--since=}"
            shift
            ;;
        --composer)
            RUN_COMPOSER=1
            shift
            ;;
        --skip-composer)
            # Backward compatibility: composer check no longer runs here at all.
            shift
            ;;
        --help|-h)
            sed -n '2,31p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            WU_FILE="$1"
            shift
            ;;
    esac
done

if [[ -z "$WU_FILE" || ! -f "$WU_FILE" ]]; then
    echo "Usage: gate.sh <path/to/WU-file.md> [--since <ref>] [--composer]" >&2
    [[ -n "$WU_FILE" ]] && echo "WU file not found: $WU_FILE" >&2
    exit 2
fi
if [[ ! -f "composer.json" ]]; then
    echo "gate.sh must run from the project repo root (composer.json not found in $(pwd))" >&2
    exit 2
fi
if [[ -n "$SINCE_REF" ]] && ! git rev-parse --verify --quiet "${SINCE_REF}^{commit}" >/dev/null; then
    echo "--since ref is not a commit: $SINCE_REF" >&2
    exit 2
fi

PLAN_DIR="$(dirname "$WU_FILE")"
FAILURES=()
WARNINGS=()

# ---------------------------------------------------------------------------
# 1. Parse the Files section: backticked paths under ### Create / ### Modify
# ---------------------------------------------------------------------------
extract_section_paths() {
    # $1 = section heading text (Create|Modify)
    awk -v section="### $1" '
        $0 == section { active=1; next }
        /^###/ || /^## / { if (active) active=0 }
        active && /^- / { print }
    ' "$WU_FILE" | grep -o '`[^`]*`' | tr -d '`' | grep -E '\.[a-zA-Z]+$' || true
}

CREATE_FILES=()
while IFS= read -r line; do [[ -n "$line" ]] && CREATE_FILES+=("$line"); done < <(extract_section_paths "Create")
MODIFY_FILES=()
while IFS= read -r line; do [[ -n "$line" ]] && MODIFY_FILES+=("$line"); done < <(extract_section_paths "Modify")

DECLARED=("${CREATE_FILES[@]}" "${MODIFY_FILES[@]}")

if [[ ${#DECLARED[@]} -eq 0 ]]; then
    echo "Could not parse any file paths from the '## Files' section of $WU_FILE" >&2
    echo "(expected backticked paths in bullets under '### Create' / '### Modify')" >&2
    exit 2
fi

echo "WU file:   $WU_FILE"
echo "Declared:  ${#CREATE_FILES[@]} create, ${#MODIFY_FILES[@]} modify"
if [[ -n "$SINCE_REF" ]]; then
    RANGE_COMMITS=$(git rev-list --count "${SINCE_REF}..HEAD")
    echo "Range:     ${SINCE_REF}..HEAD (${RANGE_COMMITS} commit(s))"
    if [[ "$RANGE_COMMITS" -eq 0 ]]; then
        WARNINGS+=("--since $SINCE_REF is HEAD: no commits to audit in the range (expected only for a legacy single-commit unit reviewed before its commit)")
    fi
fi

is_declared() {
    local f="$1"
    for d in "${DECLARED[@]}"; do
        [[ "$f" == "$d" ]] && return 0
    done
    return 1
}

is_exempt() {
    case "$1" in
        "$PLAN_DIR"/*|.claude/*) return 0 ;;
    esac
    return 1
}

# ---------------------------------------------------------------------------
# 2. Every Create file must exist
# ---------------------------------------------------------------------------
for f in "${CREATE_FILES[@]}"; do
    if [[ ! -f "$f" ]]; then
        FAILURES+=("MISSING CREATE: $f was declared under '### Create' but does not exist")
    fi
done

# ---------------------------------------------------------------------------
# 3a. Scope audit of the working tree
#    - tracked modifications outside the declared set  -> FAIL
#    - untracked files outside plan dir / declared set -> WARN (pre-existing clutter)
# ---------------------------------------------------------------------------
while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    status="${line:0:2}"
    f="${line:3}"
    # strip rename "old -> new" syntax
    f="${f##* -> }"

    is_exempt "$f" && continue
    is_declared "$f" && continue

    if [[ "$status" == "??" ]]; then
        WARNINGS+=("undeclared untracked file: $f (pre-existing clutter? not staged, not failing the gate)")
    else
        FAILURES+=("OUT OF SCOPE (working tree): tracked file modified but not declared in WU Files section: $f (status '$status')")
    fi
done < <(git status --porcelain -uall)

# ---------------------------------------------------------------------------
# 3b. Scope audit of the commit range (--since)
#    Every file touched by a commit in <ref>..HEAD must be declared.
# ---------------------------------------------------------------------------
if [[ -n "$SINCE_REF" ]]; then
    while IFS= read -r f; do
        [[ -z "$f" ]] && continue
        is_exempt "$f" && continue
        is_declared "$f" && continue
        FAILURES+=("OUT OF SCOPE (committed): $f changed in ${SINCE_REF}..HEAD but is not declared in the WU Files section")
    done < <(git diff --name-only "${SINCE_REF}..HEAD")
fi

# ---------------------------------------------------------------------------
# 4 & 5. Stub + pattern detection on declared files that exist
# ---------------------------------------------------------------------------
CODE_FILES=()
TSX_FILES=()
for f in "${DECLARED[@]}"; do
    [[ -f "$f" ]] || continue
    case "$f" in
        *.php|*.ts|*.tsx|*.js|*.jsx) CODE_FILES+=("$f") ;;
    esac
    case "$f" in
        *.ts|*.tsx) TSX_FILES+=("$f") ;;
    esac
done

if [[ ${#CODE_FILES[@]} -gt 0 ]]; then
    STUB_OUT="$("$SCRIPT_DIR/detect-stubs.sh" "${CODE_FILES[@]}" 2>&1)"
    STUB_CODE=$?
    if [[ $STUB_CODE -eq 1 ]]; then
        if [[ -z "$STUB_OUT" ]]; then
            echo "detect-stubs.sh exited 1 with no output — script malfunction, not a code failure" >&2
            exit 2
        fi
        FAILURES+=("STUBS DETECTED:"$'\n'"$STUB_OUT")
    fi
fi

if [[ ${#TSX_FILES[@]} -gt 0 ]]; then
    PAT_OUT="$("$SCRIPT_DIR/detect-wrong-patterns.sh" "${TSX_FILES[@]}" 2>&1)"
    PAT_CODE=$?
    if [[ $PAT_CODE -eq 1 ]]; then
        if [[ -z "$PAT_OUT" ]]; then
            echo "detect-wrong-patterns.sh exited 1 with no output — script malfunction, not a code failure" >&2
            exit 2
        fi
        FAILURES+=("PATTERN VIOLATIONS:"$'\n'"$PAT_OUT")
    fi
fi

# ---------------------------------------------------------------------------
# 6. Type placement: exported types belong in resources/js/Types/.
#    Only the lines this unit ADDED are judged (range diff + working tree), so a
#    pre-existing export in a file the unit merely touched is not its problem;
#    a brand-new untracked file is read whole. Tests and the testing helpers are
#    exempt.
# ---------------------------------------------------------------------------
TYPE_PLACEMENT=()
for f in "${TSX_FILES[@]}"; do
    case "$f" in
        resources/js/Types/*|*/__tests__/*|*.test.ts|*.test.tsx|resources/js/testing/*) continue ;;
    esac

    added_names=""
    if [[ -n "$SINCE_REF" ]]; then
        added_names+=$(git diff "${SINCE_REF}..HEAD" -- "$f" | grep -E '^\+export (type|interface|enum) ' | sed -E 's/^\+export (type|interface|enum) ([A-Za-z0-9_]+).*/\2/' || true)$'\n'
    fi
    added_names+=$(git diff HEAD -- "$f" | grep -E '^\+export (type|interface|enum) ' | sed -E 's/^\+export (type|interface|enum) ([A-Za-z0-9_]+).*/\2/' || true)$'\n'
    if ! git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
        added_names+=$(grep -E '^export (type|interface|enum) ' "$f" | sed -E 's/^export (type|interface|enum) ([A-Za-z0-9_]+).*/\2/' || true)$'\n'
    fi

    hits=""
    while IFS= read -r name; do
        [[ -z "$name" ]] && continue
        line=$(grep -n -E "^export (type|interface|enum) ${name}\b" "$f" | head -1 || true)
        [[ -n "$line" ]] && hits+="    $f:$line"$'\n'
    done < <(printf '%s\n' "$added_names" | sed '/^$/d' | sort -u)

    [[ -n "$hits" ]] && TYPE_PLACEMENT+=("$hits")
done

if [[ ${#TYPE_PLACEMENT[@]} -gt 0 ]]; then
    FAILURES+=("EXPORTED TYPES OUTSIDE resources/js/Types/ (move each to its domain type file: types.tsx, types-metrc.tsx, types-marketplace.tsx, ...; components, hooks and pages may declare local, non-exported types only and never re-export):"$'\n'"$(printf '%s' "${TYPE_PLACEMENT[@]}")")
fi

# ---------------------------------------------------------------------------
# 7. composer check — opt-in ONLY (--composer). The workflow runs the full
#    gauntlet once per branch through review-branch, never per unit.
# ---------------------------------------------------------------------------
if [[ $RUN_COMPOSER -eq 1 ]]; then
    echo "Running composer check (opt-in; pint, eslint, type-check, abbreviations, phpstan, vitest, phpunit)..."
    COMPOSER_OUT="$(composer check 2>&1)"
    COMPOSER_CODE=$?
    if [[ $COMPOSER_CODE -ne 0 ]]; then
        FAILURES+=("composer check FAILED (exit $COMPOSER_CODE) — last 60 lines:"$'\n'"$(echo "$COMPOSER_OUT" | tail -60)")
    fi
fi

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
echo ""
if [[ ${#WARNINGS[@]} -gt 0 ]]; then
    echo -e "${YELLOW}Warnings (${#WARNINGS[@]}):${NC}"
    for w in "${WARNINGS[@]}"; do echo -e "  ${YELLOW}-${NC} $w"; done
    echo ""
fi

if [[ ${#FAILURES[@]} -gt 0 ]]; then
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  GATE FAILED — ${#FAILURES[@]} issue(s). FIX BEFORE MARKING THE UNIT DONE  ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    for fail in "${FAILURES[@]}"; do
        echo ""
        echo -e "${RED}✗${NC} $fail"
    done
    exit 1
fi

echo -e "${GREEN}✓ GATE PASSED${NC} — create-files exist, scope clean$( [[ -n "$SINCE_REF" ]] && echo " (working tree + ${SINCE_REF}..HEAD)" ), no stubs, no pattern violations, exported types in Types/$( [[ $RUN_COMPOSER -eq 1 ]] && echo ', composer check green' )"
exit 0
