---
name: whats-next
description: Analyze the current conversation and create a handoff document for continuing this work in a fresh context
allowed-tools:
  - Read
  - Write
  - Bash
  - WebSearch
  - WebFetch
---

Analyze the current conversation and create a handoff document for continuing this work in a fresh context.

## Instructions

1. Identify the **original task** - what was initially requested (not new scope or side tasks)
2. Determine what has been **completed** toward that original task
3. Determine what **remains** to complete that same task
4. Note **essential context**: decisions made, approaches chosen, blockers encountered, gotchas discovered
5. Be specific about file paths, line numbers, function names where relevant
6. If the original task is complete, state that clearly in `work_remaining`
7. Write to `whats-next.md` in the current working directory using the format below

## Output Format

```xml
<original_task>
[The specific task that was requested]
</original_task>

<work_completed>
[What has been accomplished toward completing that task]
</work_completed>

<work_remaining>
[What still needs to be done to finish the original task]
</work_remaining>

<context>
[Essential context, decisions, constraints, or gotchas]
</context>
```
