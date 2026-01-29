#!/bin/bash
#
# Wrong Pattern Detection Script
# Detects common pattern violations in BudTags frontend code
#
# Usage: ./detect-wrong-patterns.sh <file1> <file2> ... OR ./detect-wrong-patterns.sh --dir <directory>
#
# Exit codes:
#   0 = No violations found
#   1 = Violations detected
#   2 = Usage error
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

VIOLATIONS_FOUND=0
VIOLATION_REPORT=""

check_file() {
    local file="$1"
    local ext="${file##*.}"
    local file_violations=""

    [[ ! -f "$file" ]] && return
    [[ "$ext" != "ts" && "$ext" != "tsx" ]] && return

    # Only check files with forms/modals
    grep -q -E "(useForm|Modal|form|submit|onChange)" "$file" 2>/dev/null || return

    # Check for react-hook-form
    matches=$(grep -n "from 'react-hook-form'" "$file" 2>/dev/null || true)
    if [[ -n "$matches" ]]; then
        file_violations+="[WRONG IMPORT] react-hook-form (use Inertia useForm):\n$matches\n"
    fi

    # Check for axios mutations in forms
    if grep -q "Modal\|Form\|submit\|handleSubmit" "$file" 2>/dev/null; then
        matches=$(grep -n -E "axios\.(post|put|delete|patch)\(" "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            file_violations+="[WRONG PATTERN] axios for mutations (use useForm methods):\n$matches\n"
        fi
    fi

    # Check for type on Button
    matches=$(grep -n '<Button.*type=' "$file" 2>/dev/null || true)
    if [[ -n "$matches" ]]; then
        file_violations+="[WRONG PATTERN] Button with type attribute:\n$matches\n"
    fi

    # Check for form state passed to modal
    matches=$(grep -n -E "Modal.*formData=|Modal.*setFormData=" "$file" 2>/dev/null || true)
    if [[ -n "$matches" ]]; then
        file_violations+="[WRONG PATTERN] Form state passed to modal:\n$matches\n"
    fi

    if [[ -n "$file_violations" ]]; then
        VIOLATIONS_FOUND=1
        VIOLATION_REPORT+="${YELLOW}$file:${NC}\n$file_violations\n"
    fi
}

FILES=()
DIRECTORY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dir|-d) DIRECTORY="$2"; shift 2 ;;
        --help|-h) echo "Usage: $0 [--dir <dir>] [files...]"; exit 0 ;;
        *) FILES+=("$1"); shift ;;
    esac
done

if [[ -n "$DIRECTORY" ]]; then
    while IFS= read -r -d '' file; do
        FILES+=("$file")
    done < <(find "$DIRECTORY" -type f \( -name "*.ts" -o -name "*.tsx" \) -print0 2>/dev/null)
fi

[[ ${#FILES[@]} -eq 0 ]] && { echo "No files to check"; exit 2; }

for file in "${FILES[@]}"; do check_file "$file"; done

if [[ $VIOLATIONS_FOUND -eq 1 ]]; then
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  PATTERN VIOLATIONS DETECTED                                      ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo -e "$VIOLATION_REPORT"
    echo -e "Reference: .claude/skills/decompose-plan/patterns/frontend-patterns.md"
    exit 1
else
    echo -e "${GREEN}✓ No pattern violations detected${NC}"
    exit 0
fi
