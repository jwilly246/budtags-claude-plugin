---
name: diagnose
description: Diagnosis-only investigation - root-cause a bug or behavior WITHOUT writing any code. Hard-stops after reporting findings. Use when the user asks WHY something happens, reports a problem without requesting a fix, or wants findings before deciding what to do.
version: 1.0.0
category: project
auto_activate:
  keywords:
    - "diagnose"
    - "root cause"
    - "why does"
    - "why is this"
    - "what causes"
    - "whats causing"
    - "investigate why"
---

# Diagnosis Only — No Code

You are investigating a problem, NOT fixing it. The deliverable is a diagnosis the user can act on. A question about why something happens is not a request to change it.

## The contract

- **No Edit, no Write, no migrations, no new tests.** Read-only Bash and MCP tools only.
- If you catch yourself about to modify a file, you have left the contract — stop and report instead.
- The user picks a fix AFTER reading your findings. Implementation then goes through `/budtags:fix` (small) or `/budtags:create-plan` (large), as a separate explicit step.

## Investigation

**Gather evidence first, hypothesize second:**

- `mcp__laravel-boost__last-error` / `read-log-entries` — what actually failed, with the real stack trace
- `mcp__laravel-boost__database-query` — verify actual data state; never assume what a table contains
- `mcp__laravel-boost__browser-logs` — frontend console errors
- Check the recent diff first (`git log`/`git diff`): a regression is more likely from yesterday's change than from year-old code
- Trace the code path from entry point to failure; read the relevant files fully — don't guess from function names

**Falsify before you conclude:**

State your root cause, then run one live probe whose output would look DIFFERENT if you're wrong (DB query, tinker call, log search). Show the raw output. A diagnosis that survives an attempt to disprove it is worth reporting; one that hasn't been challenged is a guess.

## Deliverable

```markdown
## Diagnosis

**Symptom**: {what the user observed}
**Root cause**: {one sentence}
**Evidence**: {file:line references + the probe output that confirms it}
**Falsification probe**: {what you ran to try to disprove it, and why it held}

**Candidate fixes**:
1. {option} — {tradeoff}
2. {option} — {tradeoff}

**Recommendation**: {which one and why, one sentence}
```

Then STOP. Do not start implementing the recommendation. Do not ask "want me to fix it?" and then fix it in the same turn — wait for the user's answer.
