#!/usr/bin/env python3
"""
PreToolUse Hook: File Protection for Critical Files

Provides extra confirmation prompts before modifying sensitive files
like .env, config files, migrations, routes, and service providers.
"""

import json
import re
import sys


# Protected file patterns with their context messages
PROTECTED_PATTERNS = [
    {
        "pattern": r"\.env",
        "message": "⚠️ Environment file",
        "context": "Environment files contain sensitive credentials and configuration.\n"
                   "Changes affect all deployments using this file.\n"
                   "Consider: Is this change needed across all environments?"
    },
    {
        "pattern": r"composer\.json$",
        "message": "⚠️ PHP dependencies",
        "context": "composer.json controls PHP package dependencies.\n"
                   "Changes require `composer install` to take effect.\n"
                   "Ensure version constraints are appropriate."
    },
    {
        "pattern": r"package\.json$",
        "message": "⚠️ JavaScript dependencies",
        "context": "package.json controls JS/Node dependencies.\n"
                   "Changes require `npm install` to take effect.\n"
                   "Ensure version constraints are appropriate."
    },
    {
        "pattern": r"config/.*\.php$",
        "message": "⚠️ Laravel configuration file",
        "context": "Laravel config files affect all environments.\n"
                   "Changes may require: `php artisan config:clear`\n"
                   "Consider: Does this belong in .env instead?"
    },
    {
        "pattern": r"database/migrations/",
        "message": "⚠️ Database migration",
        "context": "Migrations are permanent once run in production.\n"
                   "Ensure proper rollback is possible (down() method).\n"
                   "Test migration: `php artisan migrate:refresh --step=1`"
    },
    {
        "pattern": r"routes/.*\.php$",
        "message": "⚠️ Route definitions",
        "context": "Route changes affect application URL structure.\n"
                   "Ensure middleware and route names are correct.\n"
                   "Run: `php artisan route:list` to verify."
    },
    {
        "pattern": r"app/Providers/",
        "message": "⚠️ Service provider",
        "context": "Service providers bootstrap the application.\n"
                   "Errors here can prevent the app from starting.\n"
                   "Test thoroughly before deploying."
    },
    {
        "pattern": r"bootstrap/",
        "message": "⚠️ Bootstrap file",
        "context": "Bootstrap files control application initialization.\n"
                   "Errors here can break the entire application.\n"
                   "Test locally before deploying."
    },
    {
        "pattern": r"app/Console/Kernel\.php$",
        "message": "⚠️ Console scheduler",
        "context": "The Console Kernel controls scheduled tasks.\n"
                   "Changes affect cron job execution.\n"
                   "Test with: `php artisan schedule:list`"
    },
    {
        "pattern": r"app/Http/Kernel\.php$",
        "message": "⚠️ HTTP middleware stack",
        "context": "The HTTP Kernel controls middleware execution order.\n"
                   "Changes affect all HTTP requests.\n"
                   "Middleware order is critical for security."
    },
    {
        "pattern": r"app/Exceptions/Handler\.php$",
        "message": "⚠️ Exception handler",
        "context": "The Exception Handler controls error handling.\n"
                   "Errors here can mask other issues.\n"
                   "Test error scenarios after changes."
    },
]


def check_protected_file(file_path: str) -> tuple[bool, str, str]:
    """
    Check if a file is protected and return info.

    Returns:
        (is_protected, message, context)
    """
    for entry in PROTECTED_PATTERNS:
        if re.search(entry["pattern"], file_path, re.IGNORECASE):
            return True, entry["message"], entry["context"]

    return False, "", ""


def main():
    # Read tool input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return

    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')

    if not file_path:
        return

    is_protected, message, context = check_protected_file(file_path)

    if is_protected:
        # Extract just the filename for the message
        filename = file_path.split('/')[-1] if '/' in file_path else file_path

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": f"{message}: {filename}",
                "additionalContext": context
            }
        }
        print(json.dumps(result))


if __name__ == "__main__":
    main()
