#!/bin/bash
#
# Stub Detection Script
# Usage: ./detect-stubs.sh <file1> <file2> ... OR ./detect-stubs.sh --dir <directory>
#
# Exit codes:
#   0 = No stubs found
#   1 = Stubs detected
#   2 = Usage error
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

STUBS_FOUND=0
STUB_REPORT=""

# Function to check a single file
check_file() {
    local file="$1"
    local ext="${file##*.}"
    local file_stubs=""

    if [[ ! -f "$file" ]]; then
        return
    fi

    # PHP stub patterns
    if [[ "$ext" == "php" ]]; then
        # TODO/FIXME comments
        matches=$(grep -n -E "//\s*(TODO|FIXME|IMPLEMENT)" "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            file_stubs+="$matches"$'\n'
        fi

        # Not implemented exceptions
        matches=$(grep -n -E "throw new \\\\?(Runtime)?Exception\(['\"]Not implemented" "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            file_stubs+="$matches"$'\n'
        fi

        # Empty method bodies (function name() { } on same line)
        matches=$(grep -n -E "function \w+\([^)]*\)(\s*:\s*\w+)?\s*\{\s*\}" "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            file_stubs+="$matches"$'\n'
        fi

        # Placeholder comments (in code comments only, not HTML/JSX attributes)
        matches=$(grep -n -E "(//|/\*|\*).*\b(placeholder|stub|temporary|implement later|add logic here|needs implementation)\b" "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            file_stubs+="$matches"$'\n'
        fi

        # Ellipsis placeholders
        matches=$(grep -n -E "//\s*\.\.\." "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            file_stubs+="$matches"$'\n'
        fi
    fi

    # TypeScript/JavaScript stub patterns
    if [[ "$ext" == "ts" || "$ext" == "tsx" || "$ext" == "js" || "$ext" == "jsx" ]]; then
        # TODO/FIXME comments
        matches=$(grep -n -E "//\s*(TODO|FIXME|IMPLEMENT)" "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            file_stubs+="$matches"$'\n'
        fi

        # Not implemented errors
        matches=$(grep -n -E "throw new Error\(['\"]Not implemented" "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            file_stubs+="$matches"$'\n'
        fi

        # Empty arrow functions
        matches=$(grep -n -E "\(\)\s*=>\s*\{\s*\}" "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            file_stubs+="$matches"$'\n'
        fi

        # Empty function bodies
        matches=$(grep -n -E "function\s*\w*\s*\([^)]*\)\s*\{\s*\}" "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            file_stubs+="$matches"$'\n'
        fi

        # JSX TODO comments
        matches=$(grep -n -E "\{/\*\s*TODO" "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            file_stubs+="$matches"$'\n'
        fi

        # 'any' type - but exclude common valid uses like catch(e: any) or event handlers
        # Only flag standalone `: any` that looks like a lazy type escape
        matches=$(grep -n -E ":\s*any\s*[;,\)]" "$file" 2>/dev/null | grep -v -E "(catch|error|err|event|e|evt).*:\s*any" || true)
        if [[ -n "$matches" ]]; then
            file_stubs+="[any type] $matches"$'\n'
        fi

        # Placeholder comments (in code comments only, not HTML/JSX attributes)
        matches=$(grep -n -E "(//|/\*|\*).*\b(placeholder|stub|temporary|implement later|add logic here|needs implementation)\b" "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            file_stubs+="$matches"$'\n'
        fi
    fi

    # If stubs found in this file, add to report
    if [[ -n "$file_stubs" ]]; then
        STUBS_FOUND=1
        STUB_REPORT+="${YELLOW}$file:${NC}"$'\n'
        STUB_REPORT+="$file_stubs"$'\n'
    fi
}

# Parse arguments
FILES=()
DIRECTORY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dir|-d)
            DIRECTORY="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 <file1> <file2> ... OR $0 --dir <directory>"
            echo ""
            echo "Scans files for stub patterns (TODO, FIXME, empty methods, etc.)"
            echo "Exit code 0 = clean, 1 = stubs found, 2 = usage error"
            exit 0
            ;;
        *)
            FILES+=("$1")
            shift
            ;;
    esac
done

# Collect files to check
if [[ -n "$DIRECTORY" ]]; then
    while IFS= read -r -d '' file; do
        FILES+=("$file")
    done < <(find "$DIRECTORY" -type f \( -name "*.php" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) -print0 2>/dev/null)
fi

if [[ ${#FILES[@]} -eq 0 ]]; then
    echo "No files to check"
    exit 2
fi

# Check each file
for file in "${FILES[@]}"; do
    check_file "$file"
done

# Report results
if [[ $STUBS_FOUND -eq 1 ]]; then
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  STUBS DETECTED - INCOMPLETE IMPLEMENTATIONS FOUND               ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "$STUB_REPORT"
    echo -e "${RED}All stubs must be replaced with complete implementations.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ No stubs detected${NC}"
    exit 0
fi
