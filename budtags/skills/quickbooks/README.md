# QuickBooks Integration Skill

Claude skill documenting the BudTags QuickBooks Online integration: operations,
workflows, patterns, and QBO platform knowledge. Lives in the BudTags plugin repo
(`budtags/skills/quickbooks/`) and loads via progressive disclosure - see SKILL.md
for the loading rules.

## Package Structure

```
quickbooks/
├── SKILL.md                    Main skill file (entry point, loading rules)
├── README.md                   This file
├── PLATFORM_CHANGES.md         Dated Intuit platform changes 2025-2026 + BudTags impact
├── ENTITY_TYPES.md             TypeScript types (mirror of resources/js/Types/types-qbo.tsx)
├── categories/                 8 files, 56 operations (verified against QuickBooksApi.php)
│   ├── authentication.md       OAuth & service setup (7)
│   ├── customers.md            Customer ops (8)
│   ├── invoices.md             Invoice ops incl. cached + overdue (11)
│   ├── items.md                Item ops + Metrc sync (8)
│   ├── credit-memos.md         Credit memo ops (6)
│   ├── payments.md             Payment/deposit-account ops (6)
│   ├── accounts.md             Account queries (4)
│   └── utilities.md            Company info, terms, cache clearing (6)
├── patterns/                   8 pattern guides
│   ├── authentication.md       OAuth 2.0 flow (routes /quickbooks/login, /quickbooks/auth)
│   ├── token-refresh.md        Refresh-on-expiry, rotation gotchas, 5-year hard cap
│   ├── multi-tenancy.md        organization_id scoping
│   ├── caching.md              Cache::flexible() stale-while-revalidate layer
│   ├── logging.md              LogService usage
│   ├── syncing.md              SyncToken / fetch-before-update
│   ├── error-handling.md       Error catalog + SDK schema-drift diagnosis
│   └── billing-invoice-sync.md qbo:sync-invoices billing/overdue subsystem
├── scenarios/                  4 end-to-end workflow guides
│   ├── invoice-workflow.md
│   ├── payment-workflow.md
│   ├── credit-memo-workflow.md
│   └── metrc-sync-workflow.md
└── backups/                    Historical v1.0 monolith files (superseded; do not load)
```

## Integration Facts

- **Code:** `app/Services/Api/QuickBooksApi.php` (`App\Services\Api\QuickBooksApi`)
- **SDK:** `quickbooks/v3-php-sdk`, composer constraint `^6.2`, currently locked at
  **v6.3.1** (2026-07-17; PHP >= 7.2.5, Guzzle ^7.9 required). Uses the SDK's
  DataService exclusively - no raw HTTP.
- **API:** QBO Accounting API v3, minorversion 75 (final - older values are ignored,
  new fields now land in 75 without a version bump; see PLATFORM_CHANGES.md)
- **Auth:** OAuth 2.0, scope `com.intuit.quickbooks.accounting`; config keys
  `budtags.qbo_client_id` / `budtags.qbo_client_secret` / `budtags.qbo_env` (env
  `QBO_ENV`, SDK environment string like `Production`)
- **Feature gate:** `quickbooks-features` flag via EnsureOrgHasQuickbooksFeatures
  middleware

## Database Models

- **QboAccessKey** - OAuth tokens per (user_id, organization_id); table
  `qbo_access_keys`; deleted on failed refresh (re-auth required)
- **QboItemMapping** - Maps Metrc items to QuickBooks items; unique
  (organization_id, metrc_item_id)
- **QboSyncLog** - Tracks sync operations; Prunable after 14 days
- Org billing columns (from the billing sync): `payment_blocked_at`,
  `payment_warning_at`, `oldest_overdue_date`, `total_overdue_amount`,
  `block_override`, `qbo_customer_id`

See `patterns/billing-invoice-sync.md` and `patterns/multi-tenancy.md`.

## Pricing Reference for Marketplace Invoices

When generating invoices from marketplace orders, be aware of currency conversion:

- **Products/Cart:** Prices stored in **CENTS** (e.g., 42000 = $420.00)
- **Order Line Items:** Prices stored in **DOLLARS** (e.g., 420.00)
- **QuickBooks Invoices:** Prices in **DOLLARS**

**IMPORTANT:** When creating QuickBooks invoices from marketplace orders, use the
dollar values from `marketplace_order_line_items` directly. Do NOT convert again!

## Keeping the Skill Updated

The categories/ and patterns/ files are verified against the codebase; when the
integration changes, update the matching file in the same PR mindset as code review.
PLATFORM_CHANGES.md is a dated digest - refresh it when Intuit announces dated
changes (their dev blog now lives at medium.com/intuitdev). Watch for the SDK
schema-drift pattern documented in patterns/error-handling.md: Intuit ships an SDK
release first, then backfills new fields into live data days later, breaking older
pinned SDKs.

## External References

- QBO API docs: https://developer.intuit.com/app/developer/qbo/docs/get-started
- Intuit dev blog: https://medium.com/intuitdev
- PHP SDK releases: https://github.com/intuit/QuickBooks-V3-PHP-SDK/releases

## Changelog

**v3.0.0 - 2026-07-24**
- Full verification pass against the current codebase: corrected every method
  name/signature in categories/ (set_service, oauth_complete, refresh_token,
  download_invoice_pdf, apply_credit_to_invoice, etc.); documented the cached
  read family, billing/overdue subsystem, and organization_id token scoping
- Added PLATFORM_CHANGES.md covering Intuit changes Oct 2025 - Jul 2026:
  refresh-token 5-year hard cap, minorversion 75 final, App Partner Program read
  metering, CloudEvents webhooks, Reports v2, SDK releases through v6.3.1
- Corrected rate-limit numbers (500/min per realm per app, 10 concurrent)
- Rewrote token-refresh.md around the real refresh-on-expiry behavior
- New pattern: billing-invoice-sync.md; README rewritten to match actual structure

**v2.0.1 - 2025-11-14**
- Progressive disclosure restructure (categories/patterns/scenarios); v1.0
  monolith files moved to backups/

**v1.0 - October 2025**
- Initial release: operations catalog, workflow guides, OAuth documentation,
  Metrc sync guide
