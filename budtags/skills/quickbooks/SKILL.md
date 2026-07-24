---
name: quickbooks
description: Use this skill when working with QuickBooks Online integration, OAuth authentication, creating invoices, managing customers, handling payments, or syncing with Metrc data.
agent: quickbooks-specialist
---

# QuickBooks API Reference Skill

**Version:** 3.0.0 - Verified against codebase + QBO platform changes
**Last Updated:** 2026-07-24
**SDK:** quickbooks/v3-php-sdk v6.3.1 (constraint ^6.2), QBO Accounting API v3, minorversion 75 (final)

You are now equipped with comprehensive knowledge of the complete QuickBooks Online integration via **modular category files**, **scenario templates**, and **pattern guides**. This skill uses **progressive disclosure** to load only the information relevant to your task.

The integration lives in `app/Services/Api/QuickBooksApi.php` (class `App\Services\Api\QuickBooksApi`), uses the official SDK's DataService exclusively (no raw HTTP), and is gated by the `quickbooks-features` feature flag middleware.

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

### Category Files (8 files - 56 operations total)

- categories/authentication.md - 7 OAuth & service-setup operations
- categories/customers.md - 8 customer operations
- categories/invoices.md - 11 invoice operations (incl. cached + overdue)
- categories/items.md - 8 item operations + Metrc sync
- categories/credit-memos.md - 6 credit memo operations
- categories/payments.md - 6 payment/deposit-account operations
- categories/accounts.md - 4 account query operations
- categories/utilities.md - 6 utility methods (company info, terms, cache clearing)

### Pattern Files (8 files)

- patterns/authentication.md - OAuth 2.0 flow (routes /quickbooks/login and /quickbooks/auth)
- patterns/token-refresh.md - Refresh-on-expiry + refresh-chain gotchas + 5-year hard cap
- patterns/multi-tenancy.md - Organization scoping via organization_id (CRITICAL!)
- patterns/caching.md - Cache::flexible() stale-while-revalidate layer
- patterns/logging.md - LogService (NEVER use Log::)
- patterns/syncing.md - SyncToken requirements
- patterns/error-handling.md - Common errors + SDK schema-drift diagnosis
- patterns/billing-invoice-sync.md - qbo:sync-invoices billing/overdue subsystem

### Scenario Files (4 files)

- scenarios/invoice-workflow.md - Complete invoice lifecycle
- scenarios/payment-workflow.md - Recording payments
- scenarios/credit-memo-workflow.md - Credit memos
- scenarios/metrc-sync-workflow.md - Metrc sync

### Platform Reference

- PLATFORM_CHANGES.md - Dated digest of Intuit platform changes 2025-2026 with
  BudTags impact verdicts (refresh-token 5-year cap, minorversion 75 final, SDK
  release table, read metering, CloudEvents webhooks, Reports v2). Load when
  debugging something that broke WITHOUT a code deploy, when advising on SDK
  upgrades, or when asked "what changed in QBO".
- ENTITY_TYPES.md - TypeScript types mirror of resources/js/Types/types-qbo.tsx

---

## Progressive Loading Process

**IMPORTANT:** Only load files relevant to the user's question.

### Step 1: Determine User Intent

Ask or infer:
- Which operation category? (invoices, customers, payments, etc.)
- Is this OAuth/auth setup? → Load patterns/authentication.md
- Is this a workflow? → Load scenarios/
- Is this an error? → Load patterns/error-handling.md
- Did it break with no code change? → Load patterns/error-handling.md + PLATFORM_CHANGES.md
- Billing/overdue/blocked orgs? → Load patterns/billing-invoice-sync.md

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

## Critical Patterns

### Organization Scoping (MOST IMPORTANT!)

- ALL operations are organization-scoped
- Tokens stored per (user_id, organization_id) pair in qbo_access_keys
- Each org can connect to a different QuickBooks company (realm)
- Setup idiom: `$qbo = new QuickBooksApi(); $qbo->set_service($user);`
  (set_service loads the token for the user's active org; there is no set_user)

**See:** patterns/multi-tenancy.md

### Universal Requirements

- ALWAYS use LogService::store() (NEVER Log::)
- ALWAYS fetch entity before updating (SyncToken!)
- ALWAYS handle errors with try-catch; classify auth failures with QuickBooksApi::is_oauth_error($e)
- ALWAYS scope queries and cache keys to the organization id
- ALWAYS clear cache after bulk operations (clear_cache($orgId) / clear_invoices_cache($orgId))

### Common Pitfalls

- Using Log:: instead of LogService
- Not fetching before update (SyncToken error!)
- Querying without organization scoping (security risk!)
- Copying a token chain to a second environment (rotation kills the original - see patterns/token-refresh.md)
- Treating "Exception appears in converting Response to XML" as an auth error (it is SDK schema drift - see patterns/error-handling.md)
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
