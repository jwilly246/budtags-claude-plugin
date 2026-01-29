#!/bin/bash
# skill-forced-eval-hook.sh
# Forced evaluation hook for Claude Code skill activation
# Based on Scott Spence's research showing 84% activation vs 20% with simple hooks
# Reference: https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably

# Plain text output is injected directly into Claude's context
cat << 'EOF'
MANDATORY SKILL EVALUATION PROTOCOL

Before proceeding with ANY implementation, you MUST complete this evaluation:

## Step 1 - EVALUATE each skill below:

1. **metrc-api** - Metrc cannabis tracking API, plants, packages, harvests, transfers, sales receipts, lab tests, plant batches, package tags
2. **verify-alignment** - BudTags coding standards, organization scoping, LogService, flash messages, React Query patterns, code review
3. **tanstack-query** - React Query, useQuery, useMutation, queryClient, query invalidation, optimistic updates, server state, stale time, prefetch
4. **tanstack-table** - Data tables, useReactTable, sorting, filtering, pagination, row selection, column visibility, column pinning
5. **tanstack-virtual** - Virtual scrolling, useVirtualizer, large lists, performance optimization, virtualized rendering, overscan
6. **leaflink** - LeafLink wholesale marketplace, orders, products, inventory sync, customers, companies, seller/buyer workflows

For EACH skill, state: "SKILL_NAME: YES/NO - [brief reason]"

## Step 2 - ACTIVATE matched skills:
For each YES above, use Skill(budtags:skill-name) tool NOW before implementing.
(If installed via symlink, use Skill(skill-name) without the budtags: prefix)

## Step 3 - IMPLEMENT:
Only after activation, proceed with the user's task.

CRITICAL: The evaluation is WORTHLESS unless you ACTIVATE the skills with the Skill() tool.
EOF
