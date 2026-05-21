#!/usr/bin/env python3
"""
PreToolUse Hook: Destructive Bash Command Protection

Requires explicit user confirmation before running commands that
can destroy uncommitted work, untracked files, or project data.
"""

import json
import re
import sys

DANGEROUS_PATTERNS = [
    {
        "pattern": r"\bgit\s+clean\b",
        "message": "git clean deletes untracked files permanently",
    },
    {
        "pattern": r"\bgit\s+reset\s+--hard\b",
        "message": "git reset --hard discards all uncommitted changes",
    },
    {
        "pattern": r"\bgit\s+checkout\s+(--)?\s*\.\s*$",
        "message": "git checkout . discards all unstaged changes",
    },
    {
        "pattern": r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f",
        "message": "rm -rf permanently deletes files and directories",
    },
    {
        "pattern": r"\bgit\s+checkout\s+--\s+\S",
        "message": "git checkout -- <file> discards unstaged changes to specific files",
    },
    {
        "pattern": r"\bphp\s+-r\b",
        "message": "php -r executes arbitrary PHP code inline",
    },
]


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return

    command = input_data.get("tool_input", {}).get("command", "")
    if not command:
        return

    for entry in DANGEROUS_PATTERNS:
        if re.search(entry["pattern"], command, re.IGNORECASE):
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": f"⚠️ Destructive command: {entry['message']}",
                }
            }
            print(json.dumps(result))
            return


if __name__ == "__main__":
    main()
