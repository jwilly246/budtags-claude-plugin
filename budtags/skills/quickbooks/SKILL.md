---
name: quickbooks
description: Use this skill when working with QuickBooks Online integration, OAuth authentication, creating invoices, managing customers, handling payments, or syncing with Metrc data.
agent: quickbooks-specialist
---

# QuickBooks API Reference Skill

**Version:** 2.0.1 - Progressive Disclosure  
**Last Updated:** 2025-11-14

You are now equipped with comprehensive knowledge of the complete QuickBooks Online integration via **modular category files**, **scenario templates**, and **pattern guides**. This skill uses **progressive disclosure** to load only the information relevant to your task.

---

## Your Capabilities

When the user asks about QuickBooks integration, you can:

1. **Find Operations**: Search for specific operations by category or name
2. **Provide Details**: Read from category files for exact method signatures and examples  
3. **Explain Patterns**: Reference pattern files for authentication, caching, logging, SyncToken
4. **Generate Code**: Help implement QuickBooks API calls in Laravel/PHP
5. **Debug Issues**: Help troubleshoot common integration problems
6. **Build Workflows**: Guide through complete multi-step QuickBooks workflows

---

## Available Resources

### Category Files (8 files, ~80-150 lines each)

- categories/authentication.md - 4 OAuth & token operations
- categories/customers.md - 8 customer CRUD operations
- categories/invoices.md - 9 invoice operations
- categories/items.md - 7 item operations + Metrc sync
- categories/credit-memos.md - 5 credit memo operations
- categories/payments.md - 3 payment operations
- categories/accounts.md - 5 account query operations
- categories/utilities.md - 5 utility methods

### Pattern Files (7 files, ~40-100 lines each)

- patterns/authentication.md - OAuth 2.0 flow
- patterns/token-refresh.md - Automatic token refresh
- patterns/multi-tenancy.md - Organization scoping (CRITICAL!)
- patterns/caching.md - Cache strategy
- patterns/logging.md - LogService (NEVER use Log::)
- patterns/syncing.md - SyncToken requirements
- patterns/error-handling.md - Common errors

### Scenario Files (4 files, ~80-650 lines each)

- scenarios/invoice-workflow.md - Complete invoice lifecycle
- scenarios/payment-workflow.md - Recording payments
- scenarios/credit-memo-workflow.md - Credit memos
- scenarios/metrc-sync-workflow.md - Metrc sync

---

## Progressive Loading Process

**IMPORTANT:** Only load files relevant to the user's question.

### Step 1: Determine User Intent

Ask or infer:
- Which operation category? (invoices, customers, payments, etc.)
- Is this OAuth/auth setup? → Load patterns/authentication.md
- Is this a workflow? → Load scenarios/
- Is this an error? → Load patterns/error-handling.md

### Step 2: Load Minimal Resources

**For operation questions:**
Load categories/{category}.md (one category only)

**For workflow questions:**
Load scenarios/{workflow}.md + relevant category

**For pattern questions:**
Load patterns/{pattern}.md

**For errors/debugging:**
Load patterns/error-handling.md + patterns/syncing.md

### Step 3: Provide Focused Answer

1. Answer directly from loaded context
2. Show code example from category file
3. Reference pattern files if needed
4. Offer to load related resources

---

## Expected Context Reduction

| Query Type | Before | After | Reduction |
|------------|--------|-------|-----------|
| Create invoice | 2,471 lines | ~640 lines | 74% |
| OAuth setup | 998 lines | ~530 lines | 47% |
| SyncToken error | 782 lines | ~530 lines | 32% |
| Metrc sync | 1,161 lines | ~575 lines | 50% |
| Average | 2,000-3,000 | 500-700 | **75-80%** |

---

## Critical Patterns

### Organization Scoping (MOST IMPORTANT!)

- ALL operations are organization-scoped
- Tokens stored per (user_id, org_id) pair
- Each org can connect to different QuickBooks company
- ALWAYS use user->active_org->id

**See:** patterns/multi-tenancy.md

### Universal Requirements

- ALWAYS use LogService::store() (NEVER Log::)
- ALWAYS fetch entity before updating (SyncToken!)
- ALWAYS handle errors with try-catch
- ALWAYS scope queries to active_org_id
- ALWAYS clear cache after bulk operations

### Common Pitfalls

- Using Log:: instead of LogService
- Not fetching before update (SyncToken error!)
- Querying without org_id (security risk!)
- Not handling token expiration
- Forgetting to clear cache

---

## Your Mission

Help users successfully integrate with QuickBooks by:

1. Loading ONLY relevant resources (progressive disclosure)
2. Providing task-based guidance (use scenario templates)
3. Explaining patterns clearly (reference pattern files)
4. Generating correct Laravel/PHP code
5. Debugging integration issues
6. Offering additional resources

**You have complete knowledge of all QuickBooks integration patterns via modular files. Use progressive disclosure for fast, relevant answers!**
