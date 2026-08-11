#!/usr/bin/env python3
"""
PreToolUse Hook: Git Safety Rails

Mechanically enforces the git invariants that skills (run-plan, review-branch)
previously stated only as prose:

  1. DENY  `git commit` while on a deploy branch
     (deploy-to-staging, deploy-to-production — deploy.sh switches HEAD there;
     commits get lost or accidentally deployed. NOTE: main is NOT protected —
     direct commits to main are part of the normal workflow here; run-plan
     enforces its own feature-branch rule at the skill level.)
  2. DENY  `git add .` / `git add -A` / `git add --all`  (stage specific files)
  3. DENY  commit messages containing "Co-Authored-By" or "Generated with
     Claude Code" boilerplate
  4. DENY  force pushes (`git push --force` / `-f`)
  5. ASK   on any other `git push` (pushes are normally user-performed;
     an explicit approval is required when Claude is asked to push)

Fail-open philosophy: if anything in this hook errors (git missing, JSON
parse failure), it outputs nothing and the tool call proceeds normally.
"""

import json
import os
import re
import subprocess
import sys

PROTECTED_BRANCHES = {"deploy-to-staging", "deploy-to-production"}


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def ask(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))


def current_branch() -> str:
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    try:
        out = subprocess.run(
            ["git", "-C", project_dir, "branch", "--show-current"],
            capture_output=True, text=True, timeout=5,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return

    command = input_data.get("tool_input", {}).get("command", "")
    if not command or "git" not in command:
        return

    # --- 4 & 5: pushes ---------------------------------------------------
    # The token walk refuses to step over "stash" so `git stash push` (and
    # `git -C /path stash push`) never trips the remote-push rule.
    if re.search(r"\bgit\s+(?:(?!stash\b)\S+\s+)*push\b", command):
        if re.search(r"\bpush\b[^|;&]*(\s--force\b|\s-f\b|\s--force-with-lease\b)", command):
            deny("Force pushes are not allowed from Claude. If genuinely needed, the user runs it themselves.")
            return
        if input_data.get("permission_mode") == "bypassPermissions":
            # An "ask" would wedge unattended bypass-mode runs on a dialog
            # nobody is watching. Deny outright: pushes stay user-performed.
            deny("git push is denied in bypass-permissions mode (no prompt possible). Pushes are user-performed; the user runs them directly.")
        else:
            ask("git push detected. Pushes are normally user-performed (local commits only); approve only if you explicitly asked Claude to push.")
        return

    # --- 2: bulk staging --------------------------------------------------
    if re.search(r"\bgit\s+add\s+(-A\b|--all\b)", command) \
            or re.search(r"\bgit\s+add\s+\.(?![\w/])", command):
        deny("Bulk staging (git add . / -A / --all) is not allowed. Stage the specific files for this change.")
        return

    # --- 1 & 3: commits ---------------------------------------------------
    if re.search(r"\bgit\s+(\S+\s+)*commit\b", command):
        if re.search(r"Co-Authored-By", command, re.IGNORECASE) \
                or re.search(r"Generated with \[?Claude", command, re.IGNORECASE):
            deny("Commit message contains forbidden boilerplate (Co-Authored-By / Generated with Claude Code). Rewrite the message without it.")
            return

        branch = current_branch()
        if branch in PROTECTED_BRANCHES:
            deny(f"Refusing to commit on protected branch '{branch}'. Create/switch to a feature branch first (deploy.sh switches HEAD on deploy-to-* branches; commits there get lost or deployed accidentally).")
            return


if __name__ == "__main__":
    main()
