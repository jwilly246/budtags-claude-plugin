#!/usr/bin/env python3
"""
PreToolUse Hook: Block Git Commit Without Validation

Blocks `git commit` commands unless /pre-commit has been run recently.
Checks for .claude/.pre-commit-passed state file with a 10-minute validity window.
"""

import json
import os
import re
import sys
import time


# How long the pre-commit pass is valid (in seconds)
VALIDITY_WINDOW = 600  # 10 minutes

STATE_FILE = ".claude/.pre-commit-passed"


def is_git_commit_command(command: str) -> bool:
    """Check if the command is a git commit."""
    # Match various git commit patterns
    patterns = [
        r'\bgit\s+commit\b',           # git commit
        r'\bgit\s+.*\s+commit\b',      # git -c ... commit
    ]

    for pattern in patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True

    return False


def check_pre_commit_state() -> tuple[bool, str]:
    """
    Check if pre-commit has been run recently.

    Returns:
        (is_valid, message)
    """
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    state_path = os.path.join(project_dir, STATE_FILE)

    if not os.path.exists(state_path):
        return False, "Run /pre-commit first. Modified files need PHPStan/Pint validation."

    try:
        # Check file modification time
        mtime = os.path.getmtime(state_path)
        age = time.time() - mtime

        if age > VALIDITY_WINDOW:
            minutes_ago = int(age / 60)
            return False, f"Pre-commit validation expired ({minutes_ago} min ago). Run /pre-commit again."

        # Read the state file for additional context
        with open(state_path, 'r') as f:
            content = f.read().strip()

        return True, f"Pre-commit passed: {content}"

    except (IOError, OSError) as e:
        return False, f"Error checking pre-commit state: {e}"


def main():
    # Read tool input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return

    tool_input = input_data.get('tool_input', {})
    command = tool_input.get('command', '')

    if not command:
        return

    # Only check git commit commands
    if not is_git_commit_command(command):
        return

    is_valid, message = check_pre_commit_state()

    if not is_valid:
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": message
            }
        }
        print(json.dumps(result))
    # If valid, output nothing to allow the command to proceed


if __name__ == "__main__":
    main()
