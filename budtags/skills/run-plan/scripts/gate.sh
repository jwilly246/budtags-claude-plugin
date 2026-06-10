#!/bin/bash
#
# Work Unit Gate — the single mechanical verification command for run-plan.
#
# Usage: gate.sh <path/to/WU-file.md> [--skip-composer]
#   Run from the PROJECT REPO ROOT (where composer.json lives).
#
# Performs, in order:
#   1. Parse the WU's "## Files" section (backticked paths under ### Create / ### Modify)
#   2. Verify every "Create" file actually exists
#   3. Scope audit: tracked files modified outside the declared set = FAIL;
#      pre-existing untracked clutter outside the plan dir = WARN only
#   4. Stub detection (detect-stubs.sh) on declared code files
#   5. Frontend pattern check (detect-wrong-patterns.sh) on declared ts/tsx files
#   6. composer check (full quality gauntlet) unless --skip-composer
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
SKIP_COMPOSER=0

for arg in "$@"; do
    case "$arg" in
        --skip-composer) SKIP_COMPOSER=1 ;;
        --help|-h)
            sed -n '2,22p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *) WU_FILE="$arg" ;;
    esac
done

if [[ -z "$WU_FILE" || ! -f "$WU_FILE" ]]; then
    echo "Usage: gate.sh <path/to/WU-file.md> [--skip-composer]" >&2
    [[ -n "$WU_FILE" ]] && echo "WU file not found: $WU_FILE" >&2
    exit 2
fi
if [[ ! -f "composer.json" ]]; then
    echo "gate.sh must run from the project repo root (composer.json not found in $(pwd))" >&2
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

is_declared() {
    local f="$1"
    for d in "${DECLARED[@]}"; do
        [[ "$f" == "$d" ]] && return 0
    done
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
# 3. Scope audit
#    - tracked modifications outside the declared set  -> FAIL
#    - untracked files outside plan dir / declared set -> WARN (pre-existing clutter)
# ---------------------------------------------------------------------------
while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    status="${line:0:2}"
    f="${line:3}"
    # strip rename "old -> new" syntax
    f="${f##* -> }"

    # exemptions: the plan directory itself, .claude/
    case "$f" in
        "$PLAN_DIR"/*|.claude/*) continue ;;
    esac

    if is_declared "$f"; then
        continue
    fi

    if [[ "$status" == "??" ]]; then
        WARNINGS+=("undeclared untracked file: $f (pre-existing clutter? not staged, not failing the gate)")
    else
        FAILURES+=("OUT OF SCOPE: tracked file modified but not declared in WU Files section: $f (status '$status')")
    fi
done < <(git status --porcelain -uall)

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
# 6. composer check (the full project quality gauntlet)
# ---------------------------------------------------------------------------
if [[ $SKIP_COMPOSER -eq 0 ]]; then
    echo "Running composer check (pint, eslint, type-check, phpstan, vitest, phpunit)..."
    COMPOSER_OUT="$(composer check 2>&1)"
    COMPOSER_CODE=$?
    if [[ $COMPOSER_CODE -ne 0 ]]; then
        FAILURES+=("composer check FAILED (exit $COMPOSER_CODE) — last 60 lines:"$'\n'"$(echo "$COMPOSER_OUT" | tail -60)")
    fi
else
    WARNINGS+=("composer check SKIPPED (--skip-composer) — it must still pass before commit")
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
    echo -e "${RED}║  GATE FAILED — ${#FAILURES[@]} issue(s). DO NOT COMMIT THIS WORK UNIT  ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    for fail in "${FAILURES[@]}"; do
        echo ""
        echo -e "${RED}✗${NC} $fail"
    done
    exit 1
fi

echo -e "${GREEN}✓ GATE PASSED${NC} — create-files exist, scope clean, no stubs, no pattern violations$( [[ $SKIP_COMPOSER -eq 0 ]] && echo ', composer check green' )"
exit 0
