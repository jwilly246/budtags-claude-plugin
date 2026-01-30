#!/bin/bash
# SessionStart hook - checks if setup has run
#
# If the plugin hasn't been configured yet, prompts the user to run /budtags-setup

# Get the plugin directory from Claude's environment variable
# Falls back to determining from script location if not set
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$SCRIPT_DIR")}"

CONFIG_FLAG="$PLUGIN_ROOT/.budtags-configured"

if [ ! -f "$CONFIG_FLAG" ]; then
    # First run - prompt user to run setup
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo "  🌿 BudTags Plugin - First Run Setup"
    echo "══════════════════════════════════════════════════════════════"
    echo ""
    echo "  Configure which features to enable by running:"
    echo "    /budtags-setup       (if symlinked)"
    echo "    /budtags:budtags-setup  (if installed as plugin)"
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo ""
fi

exit 0
