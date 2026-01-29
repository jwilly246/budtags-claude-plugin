#!/bin/bash
# BudTags Plugin Setup Wizard
#
# Interactive TUI wizard for configuring which skills, agents, and hooks to enable.
# Uses 'gum' for beautiful terminal UI, falls back gracefully if unavailable.
# Uses jq for JSON processing, with Python as a fallback.

set -e

# Get the plugin directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="${PLUGIN_DIR:-$(dirname "$SCRIPT_DIR")}"

CONFIG_FILE="$PLUGIN_DIR/.budtags-config.json"
CONFIG_FLAG="$PLUGIN_DIR/.budtags-configured"
ITEMS_FILE="$PLUGIN_DIR/config/items.json"

# Colors for non-gum output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Determine JSON processor (jq or python)
JSON_PROCESSOR=""

setup_json_processor() {
    if command -v jq &> /dev/null; then
        JSON_PROCESSOR="jq"
    elif command -v python3 &> /dev/null; then
        JSON_PROCESSOR="python3"
    elif command -v python &> /dev/null; then
        JSON_PROCESSOR="python"
    else
        echo -e "${RED}Error: Neither 'jq' nor 'python3' is available.${NC}"
        echo "Install one of:"
        echo "  - jq: brew install jq  OR  apt install jq"
        echo "  - python3: usually pre-installed on most systems"
        exit 1
    fi
}

# JSON query using available processor
json_query() {
    local query="$1"
    local file="$2"

    if [ "$JSON_PROCESSOR" = "jq" ]; then
        jq -r "$query" "$file"
    else
        $JSON_PROCESSOR -c "
import json
import sys

with open('$file') as f:
    data = json.load(f)

query = '''$query'''

# Simple jq-like query parser for common patterns
if query.startswith('[.'):
    # Array query like [.skills[] | select(.default == true) | .id]
    parts = query.strip('[]').split(' | ')
    category = parts[0].split('[]')[0][1:]  # Extract 'skills' from '.skills[]'

    result = data.get(category, [])

    for part in parts[1:]:
        if 'select(.default == true)' in part:
            result = [item for item in result if item.get('default', False)]
        elif part.startswith('.'):
            field = part[1:]
            result = [item.get(field, '') for item in result]

    print(','.join(str(r) for r in result))
elif '[]' in query:
    # Query like .skills[] | \"\\(.id):\\(.name) - \\(.description)\"
    parts = query.split(' | ')
    category = parts[0].split('[]')[0][1:]

    for item in data.get(category, []):
        if 'select(.default == true)' in query and not item.get('default', False):
            continue
        print(f\"{item['id']}:{item['name']} - {item['description']}\")
"
    fi
}

# Get default items as JSON array
get_defaults_json() {
    local category="$1"

    if [ "$JSON_PROCESSOR" = "jq" ]; then
        jq -c "[.${category}[] | select(.default == true) | .id]" "$ITEMS_FILE"
    else
        $JSON_PROCESSOR -c "
import json
with open('$ITEMS_FILE') as f:
    data = json.load(f)
result = [item['id'] for item in data.get('$category', []) if item.get('default', False)]
print(json.dumps(result))
"
    fi
}

# Check for gum availability
has_gum() {
    command -v gum &> /dev/null
}

# Fallback mode without gum - enable all defaults
fallback_mode() {
    echo ""
    echo -e "${YELLOW}Note: 'gum' is not installed. Using default configuration.${NC}"
    echo -e "Install gum for interactive setup: ${CYAN}brew install gum${NC}"
    echo ""

    # Extract default items as JSON arrays
    local skills_json=$(get_defaults_json "skills")
    local agents_json=$(get_defaults_json "agents")
    local hooks_json=$(get_defaults_json "hooks")

    # Create config with defaults
    cat > "$CONFIG_FILE" << EOF
{
  "version": "1.0.0",
  "configured_at": "$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S%z)",
  "mode": "defaults",
  "skills": $skills_json,
  "agents": $agents_json,
  "hooks": $hooks_json
}
EOF

    touch "$CONFIG_FLAG"

    echo -e "${GREEN}Default configuration saved to .budtags-config.json${NC}"
    echo ""
    echo "To re-run setup interactively:"
    echo -e "  1. Install gum: ${CYAN}brew install gum${NC}"
    echo -e "  2. Remove flag: ${CYAN}rm $CONFIG_FLAG${NC}"
    echo -e "  3. Start a new Claude session"
    echo ""
}

# Show header with gum
show_header() {
    gum style \
        --border normal \
        --margin "1" \
        --padding "1 2" \
        --border-foreground 212 \
        "🌿 BudTags Plugin Setup Wizard"
    echo ""
}

# Check for laravel-simplifier dependency
check_laravel_simplifier() {
    local laravel_path
    laravel_path=$(eval echo "~/.claude/plugins/laravel-simplifier")

    if [ ! -d "$laravel_path" ]; then
        gum style --foreground 214 "⚠️  Optional: laravel-simplifier plugin not found"
        echo ""
        echo "Some agents work better with laravel-simplifier installed."
        echo "To install, run:"
        echo ""
        gum style --foreground 39 "  cd ~/.claude && git clone https://github.com/laravel/claude-code laravel-simplifier"
        echo ""

        if ! gum confirm "Continue setup without it?"; then
            echo "Setup cancelled. Install laravel-simplifier and try again."
            exit 0
        fi
        echo ""
    fi
}

# Build choices string for gum choose
# Format: "id:Name - Description"
build_choices() {
    local category="$1"

    if [ "$JSON_PROCESSOR" = "jq" ]; then
        jq -r ".${category}[] | \"\(.id):\(.name) - \(.description)\"" "$ITEMS_FILE"
    else
        $JSON_PROCESSOR -c "
import json
with open('$ITEMS_FILE') as f:
    data = json.load(f)
for item in data.get('$category', []):
    print(f\"{item['id']}:{item['name']} - {item['description']}\")
"
    fi
}

# Get default items for a category (formatted for gum --selected)
get_defaults() {
    local category="$1"

    if [ "$JSON_PROCESSOR" = "jq" ]; then
        jq -r ".${category}[] | select(.default == true) | \"\(.id):\(.name) - \(.description)\"" "$ITEMS_FILE"
    else
        $JSON_PROCESSOR -c "
import json
with open('$ITEMS_FILE') as f:
    data = json.load(f)
for item in data.get('$category', []):
    if item.get('default', False):
        print(f\"{item['id']}:{item['name']} - {item['description']}\")
"
    fi
}

# Extract IDs from selection and format as JSON array
extract_ids() {
    local selection="$1"
    if [ -z "$selection" ]; then
        echo "[]"
        return
    fi

    if [ "$JSON_PROCESSOR" = "jq" ]; then
        echo "$selection" | cut -d: -f1 | jq -R . | jq -s .
    else
        echo "$selection" | cut -d: -f1 | $JSON_PROCESSOR -c "
import json
import sys
ids = [line.strip() for line in sys.stdin if line.strip()]
print(json.dumps(ids))
"
    fi
}

# Interactive selection with gum
select_items() {
    local category="$1"
    local display_name="$2"
    local emoji="$3"

    echo "$emoji Select $display_name to enable:"
    echo ""

    local choices
    choices=$(build_choices "$category")

    local defaults
    defaults=$(get_defaults "$category")

    # Use gum choose with defaults pre-selected
    local selected
    if [ -n "$defaults" ]; then
        selected=$(echo "$choices" | gum choose --no-limit --header "$display_name (space to toggle, enter to confirm)" --selected="$defaults" 2>/dev/null || echo "$defaults")
    else
        selected=$(echo "$choices" | gum choose --no-limit --header "$display_name (space to toggle, enter to confirm)" 2>/dev/null || echo "")
    fi

    echo "$selected"
}

# Main wizard flow with gum
run_wizard() {
    show_header
    check_laravel_simplifier

    # Skills selection
    local selected_skills
    selected_skills=$(select_items "skills" "Skills" "📚")
    echo ""

    # Agents selection
    local selected_agents
    selected_agents=$(select_items "agents" "Agents" "🤖")
    echo ""

    # Hooks selection
    local selected_hooks
    selected_hooks=$(select_items "hooks" "Hooks" "🪝")
    echo ""

    # Extract IDs and build config
    local skills_json
    local agents_json
    local hooks_json

    skills_json=$(extract_ids "$selected_skills")
    agents_json=$(extract_ids "$selected_agents")
    hooks_json=$(extract_ids "$selected_hooks")

    # Write config file
    cat > "$CONFIG_FILE" << EOF
{
  "version": "1.0.0",
  "configured_at": "$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S%z)",
  "mode": "custom",
  "skills": $skills_json,
  "agents": $agents_json,
  "hooks": $hooks_json
}
EOF

    # Mark as configured
    touch "$CONFIG_FLAG"

    # Show completion message
    gum style \
        --border normal \
        --margin "1" \
        --padding "1" \
        --border-foreground 46 \
        "✅ Setup complete! Config saved to .budtags-config.json"

    echo ""
    echo "To re-run setup: rm $CONFIG_FLAG && start a new Claude session"
    echo ""
}

# Main entry point
main() {
    setup_json_processor

    # Check if items.json exists
    if [ ! -f "$ITEMS_FILE" ]; then
        echo -e "${RED}Error: Items registry not found at $ITEMS_FILE${NC}"
        exit 1
    fi

    if has_gum; then
        run_wizard
    else
        fallback_mode
    fi
}

main "$@"
