#!/bin/bash
# skill-forced-eval-hook.sh v2
# Agent-first routing hook - routes tasks to specialist agents with auto-loaded skills
# Replaces skill-eval v1 which had reliability issues with Skill() tool activation

# Plain text output is injected directly into Claude's context
cat << 'EOF'
MANDATORY DOMAIN EVALUATION PROTOCOL

Before proceeding with implementation, evaluate which specialist agent to use:

## Step 1 - IDENTIFY the primary domain:

| Domain | Indicators | Specialist Agent | Auto-Loaded Skills |
|--------|------------|------------------|-------------------|
| Metrc API | plants, packages, harvests, transfers, sales, lab tests, license types | `budtags:metrc-specialist` | metrc-api, verify-alignment |
| QuickBooks | invoices, customers, payments, OAuth, SyncToken | `budtags:quickbooks-specialist` | quickbooks, verify-alignment |
| LeafLink | orders, products, inventory sync, wholesale | `budtags:leaflink-specialist` | leaflink, verify-alignment |
| TanStack | useQuery, useMutation, useReactTable, useVirtualizer | `budtags:tanstack-specialist` | tanstack-*, verify-alignment |
| React/Inertia | modals, forms, toasts, TypeScript components | `budtags:react-specialist` | verify-alignment |
| Backend Laravel | controllers, services, migrations (no integration) | `budtags:php-developer` | (reads patterns) |
| Mixed/Unclear | spans frontend + backend, multiple domains | `budtags:fullstack-developer` | (generic fallback) |

## Step 2 - ROUTE to specialist:

If task matches a domain above, use Task tool with that specialist:

```
Task(subagent_type: "budtags:metrc-specialist", prompt: "...")
```

The specialist agent will have domain skills AUTO-LOADED via its `skills:` frontmatter.

## Step 3 - ALWAYS use an agent:

Even for simple tasks, spawn the appropriate specialist agent. This ensures:
- Skills are ALWAYS loaded (no forgetting)
- Consistent workflow for all tasks
- Agents can handle simple tasks quickly

For quick fixes without a clear domain:
- Backend fix → `budtags:php-developer`
- Frontend fix → `budtags:react-specialist`

CRITICAL: Specialist agents have skills built-in. Using the right agent = automatic skill loading. NEVER skip the agent step.
EOF
