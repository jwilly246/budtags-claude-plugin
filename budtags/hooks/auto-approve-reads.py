#!/usr/bin/env python3
"""
PreToolUse Hook: Auto-Approve Safe Reads

Auto-approves Read tool calls for documentation and config files,
while blocking sensitive files like .env and lock files.
"""

import json
import re
import sys


# Patterns that are safe to auto-approve
SAFE_PATTERNS = [
    r'\.md$',                    # Markdown docs
    r'\.txt$',                   # Text files
    r'\.json$',                  # JSON configs (filtered below)
    r'\.ya?ml$',                 # YAML configs
    r'\.claude/',                # Claude config directory
    r'CLAUDE\.md$',              # Project instructions
    r'README',                   # README files
    r'/docs?/',                  # Documentation directories
    r'\.gitignore$',             # Git ignore
    r'\.editorconfig$',          # Editor config
    r'tsconfig.*\.json$',        # TypeScript configs
    r'phpunit\.xml$',            # PHPUnit config
    r'phpstan.*\.neon$',         # PHPStan config
    r'vite\.config\.',           # Vite config
    r'tailwind\.config\.',       # Tailwind config
    r'eslint\.config\.',         # ESLint config
]

# Patterns to never auto-approve (require confirmation)
BLOCK_PATTERNS = [
    r'\.env',                    # Environment files (.env, .env.local, etc.)
    r'package-lock\.json$',      # NPM lock file (too large)
    r'composer\.lock$',          # Composer lock file (too large)
    r'yarn\.lock$',              # Yarn lock file
    r'pnpm-lock\.yaml$',         # PNPM lock file
    r'/storage/',                # Storage directory
    r'/vendor/',                 # Vendor directory
    r'/node_modules/',           # Node modules
    r'\.pem$',                   # Certificates
    r'\.key$',                   # Private keys
    r'credentials',              # Credential files
    r'secrets?\.json$',          # Secret files
]


def is_safe_read(file_path: str) -> tuple[bool, str]:
    """
    Determine if a file read should be auto-approved.

    Returns:
        (should_approve, reason)
    """
    # First check block patterns - these are never auto-approved
    for pattern in BLOCK_PATTERNS:
        if re.search(pattern, file_path, re.IGNORECASE):
            return False, f"Sensitive file pattern: {pattern}"

    # Then check safe patterns
    for pattern in SAFE_PATTERNS:
        if re.search(pattern, file_path, re.IGNORECASE):
            # Determine a friendly reason
            if '.md' in pattern or 'README' in pattern:
                reason = "Safe read: documentation file"
            elif '.json' in pattern or '.yaml' in pattern or '.yml' in pattern:
                reason = "Safe read: configuration file"
            elif '.claude' in pattern or 'CLAUDE' in pattern:
                reason = "Safe read: Claude configuration"
            else:
                reason = "Safe read: safe file pattern"
            return True, reason

    # Not matched by any pattern - let Claude Code handle normally
    return False, "No safe pattern match"


def main():
    # Read tool input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If we can't parse input, don't interfere
        return

    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')

    if not file_path:
        # No file path provided, don't interfere
        return

    should_approve, reason = is_safe_read(file_path)

    if should_approve:
        # Output the permission decision to auto-approve
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": reason
            }
        }
        print(json.dumps(result))


if __name__ == "__main__":
    main()
