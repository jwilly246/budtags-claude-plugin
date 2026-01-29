#!/bin/bash
# SessionStart hook - checks if setup has run
#
# This script runs on every Claude Code session start.
# If the plugin hasn't been configured yet, it launches the setup wizard.

# Get the plugin directory (parent of scripts directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="${PLUGIN_DIR:-$(dirname "$SCRIPT_DIR")}"

CONFIG_FLAG="$PLUGIN_DIR/.budtags-configured"

if [ ! -f "$CONFIG_FLAG" ]; then
    # First run - launch wizard
    exec "$PLUGIN_DIR/scripts/setup-wizard.sh"
fi

# Already configured - exit silently
exit 0
