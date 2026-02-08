#!/bin/bash
# ui-scope-reminder.sh
# UserPromptSubmit hook: When user prompt contains UI/styling keywords,
# injects a reminder to clarify scope before implementing.

# Read the user's prompt from stdin
PROMPT=$(cat)

# Check for UI-related keywords (case-insensitive)
if echo "$PROMPT" | grep -iqE '(restyle|redesign|update the (look|ui|design|layout|style)|change the (layout|design|look|style)|make it look|visual(ly)?|breakpoint|responsive|mobile view|dark mode|theme|new design|ui change|styling change|move the|reposition|realign)'; then
  cat << 'EOF'
UI SCOPE REMINDER: Before implementing UI changes, clarify:
- Which specific components or pages are affected?
- Which states should change (hover, active, empty, loading, error)?
- Which breakpoints matter (mobile, tablet, desktop)?
- Should this match an existing pattern in the codebase, or is it a new design?
Ask the user if any of these are unclear from their request.
EOF
fi
