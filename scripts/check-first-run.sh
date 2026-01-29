#!/bin/bash
# SessionStart hook - checks if setup has run
#
# If the plugin hasn't been configured yet, prompts the user to run /budtags-setup

# Get the plugin directory (parent of scripts directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="${PLUGIN_DIR:-$(dirname "$SCRIPT_DIR")}"

CONFIG_FLAG="$PLUGIN_DIR/.budtags-configured"

if [ ! -f "$CONFIG_FLAG" ]; then
    # First run - prompt user to run setup
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo "  🌿 BudTags Plugin - First Run Setup"
    echo "══════════════════════════════════════════════════════════════"
    echo ""
    echo "  Run /budtags-setup to configure which features to enable."
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo ""
fi

exit 0
