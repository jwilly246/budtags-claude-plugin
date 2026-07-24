# QBO Platform Changes (2025-2026)

Dated digest of Intuit platform changes affecting this integration, researched
2026-07-24 from Intuit primary sources (Intuit dev blog posts now live at
medium.com/intuitdev; the old blogs.intuit.com URLs redirect there).

Each item carries a **BudTags impact** verdict. Verified-in-code claims were checked
against `app/Services/Api/QuickBooksApi.php` on 2026-07-24.

---

## 1. Refresh tokens now hard-expire after 5 years

**The big one.** Previously refresh tokens were effectively permanent if used every
100 days. Announced 2025-11-12; live in production **2026-01-27**:

- Every refresh token now has a **5-year maximum lifespan** measured from initial
  authorization. Refreshing does NOT reset this clock (the 100-day inactivity rule
  still applies on top and DOES reset on each refresh).
- Apps on `com.intuit.quickbooks.accounting` scope (BudTags): earliest hard
  expirations begin **October 2028**. Apps on granular scopes: February 2027.
- QBO notifies the customer in-product 30 days before expiry, by email 7 days before.
- Optional token-endpoint request header `x-include-refresh-token-hard-expires-in: true`
  returns `x_refresh_token_hard_expires_in` (seconds remaining). PHP SDK >= v6.2.4
  exposes this (`includeRefreshTokenHardExpiresIn` -> `refreshTokenHardExpiresIn`).
- The developer portal now has a mandatory **Reconnect URL** field (Keys & Credentials,
  since 2026-02-24) - the page customers land on to re-authenticate.

**BudTags impact: ACTION EVENTUALLY REQUIRED.** The service-user token that powers
`qbo:sync-invoices` will hard-expire no earlier than Oct 2028 no matter how healthy
the refresh chain is. Plan: consume the hard-expiry field (SDK >= 6.2.4) and surface
a re-auth prompt, or calendar a manual re-auth. Also verify the Reconnect URL is set
in the Intuit portal. See `patterns/token-refresh.md`.

---

## 2. Minorversion policy is settled: 75 is final

- Minorversions 1-74 were deprecated **2025-08-01**. Passing an older value is
  silently ignored and served as minorversion 75. The parameter is still accepted.
- There is **no minorversion 76** and none is planned. New fields are now added to
  MV75 in place, WITHOUT a version bump.

**BudTags impact: none directly** (the integration never passes `minorversion`; the
SDK default applies). BUT the "fields added in place" policy is exactly why the
2026-07-23 schema-drift incident happened: Intuit adds fields to live responses and
older SDK versions choke deserializing them. See `patterns/error-handling.md`
("Exception appears in converting Response to XML"). Keep the SDK current.

---

## 3. PHP SDK releases (quickbooks/v3-php-sdk)

| Version | Date | Notes |
|---------|------|-------|
| v6.2.1 | 2025-09-22 | MV75 schema updates |
| v6.2.2 | 2025-11-07 | CloudEvents webhooks support (`GetWebhooksCloudEvents()`) |
| v6.2.3 | 2026-04-22 | Schema updates; `testingMigration` param for Reports v2 |
| v6.2.4 | 2026-05-28 | Refresh-token hard-expiry field support |
| v6.2.5 | 2026-07-15 | Adds `AllowOnlineAffirmPayment` to `IPPInvoice` |
| v6.3.1 | 2026-07-17 | **Latest.** Schema updates + PHP 8.4 support; new classes (TxnRetainageDetail, VendorPrepayment, BudgetCustomExtensions); `ignoreUnknownElements` XML option; min PHP raised to 7.2.5. No v6.3.0 exists. |

**BudTags impact:** composer.lock is on **v6.3.1** (updated 2026-07-23 after the
schema-drift incident). Constraint `^6.2` picks up 6.x patches on
`composer update quickbooks/v3-php-sdk`. Given Intuit's release-SDK-first,
backfill-data-later pattern, update the SDK promptly when Intuit ships schema
releases rather than waiting for breakage.

---

## 4. Query and entity behavior changes

Live in production **2026-01-27**:
- **`Id` is no longer sortable** in queries - `ORDERBY Id` is ignored/unsupported on
  every entity. Use `TxnDate` or `MetaData.LastUpdatedTime` instead.
  *BudTags impact: none - verified no ORDERBY usage in QuickBooksApi.php.*
- **Employee**: phone numbers return formatted values only; invalid home addresses
  return "Business Validation Error: INVALID_HOME_ADDRESS".
  *BudTags impact: none - Employee entity not used.*
- **CompanyInfo**: `NeoEnabled` NameValue pair no longer returned.
  *BudTags impact: none - get_company_info() does not read it.*

Live in production **2026-04-30**:
- **`AccountRef.name` (and all *AccountRef.name variants) now return the account's
  FullyQualifiedName** (e.g. "Utilities:Gas & Electric") instead of the short name.
  Writes passing only `AccountRef.value` are unaffected.
  *BudTags impact: none - verified all account refs are written with `value` only
  and nothing matches on account name.*
- **ExchangeRate**: only enabled currencies, only last 3 years of history.
  *BudTags impact: none - not used.*

New Invoice field: **`AllowOnlineAffirmPayment`** (plus the 2026-07-22 backfilled
`EInvoiceStatus`) - present in SDK >= 6.2.5 / 6.3.1.

---

## 5. Rate limits unchanged; reads are now metered money

- Published throttles are unchanged: **500 requests/min per realm per app**,
  **10 concurrent per realm**, HTTP 429 / error 3001 on throttle. (The old claim of
  "1000/min per company" that used to live in this skill was never right.)
- **Intuit App Partner Program** (live 2025-07-28, billed since 2025-11-01) replaced
  the legacy developer program. Data-out ("CorePlus") calls are metered: the free
  **Builder tier gets 500k CorePlus credits/month and BLOCKS reads beyond that**.
  Writes are unmetered. Paid tiers (Silver/Gold/Platinum) get more credits plus
  overage billing. Only 2xx responses are metered.

**BudTags impact: watch but no action.** Current volume (daily invoice sync +
dashboard reads across a handful of orgs) is far below 500k/month, but the
stale-while-revalidate cache layer is now also a cost control, not just a latency
one. If reads ever hard-fail near month-end, check quota before debugging code.

---

## 6. Webhooks: mandatory CloudEvents format (deadline 2026-07-31)

- Intuit rebuilt webhooks; all apps must consume the **CloudEvents (CNCF)** payload
  format by **2026-07-31** (extended from 2026-05-15). Legacy
  `eventNotifications[].dataChangeEvent.entities[]` payloads stop.
- New shape: array of CloudEvents objects (`type` like `qbo.account.created.v1`,
  extensions `intuitentityid`/`intuitaccountid`, payload under `data`). One
  notification can span MULTIPLE realms. Portal toggle switches format; PHP SDK
  >= 6.2.2 has `GetWebhooksCloudEvents()`. HMAC signature verification via
  `intuit-signature` is unchanged.

**BudTags impact: none today** - the integration polls; no QBO webhooks are
subscribed. If webhooks are ever added, build CloudEvents-only.

---

## 7. Reports API v1 -> v2 (deadline 2026-08-31)

All 29 documented report endpoints migrate to modernized-report responses: nulls
come back as `""`, row order is dynamic, child accounts nest under parents,
`qzurl` dropped, undocumented reports stop working. Test via `_testing_migration_`
query param (SDK >= 6.2.3: `testingMigration`).

**BudTags impact: none** - no QBO report endpoints are used.

---

## 8. No REST v3 sunset; premium APIs are GraphQL and tier-gated

- **No deprecation of the REST v3 Accounting API has been announced.** Intuit is
  actively shipping v3 schema updates (see SDK table).
- New premium APIs (Projects, Project Budget, Change Order, Custom Fields, Custom
  Dimensions, Sales Tax, Payroll Compensation) are GraphQL-first, live under
  `app-foundations.*` scopes, and mostly require Silver tier or above and/or
  QBO Advanced / Intuit Enterprise Suite.

**BudTags impact: none.** Everything BudTags needs stays on free REST v3.

---

## 9. New official tooling (optional)

- **Intuit QuickBooks CLI** (2026-06-08): `npm install -g intuit-cli` - OAuth flows,
  entity queries, webhook testing, JSON/CSV output. Handy for debugging outside
  tinker.
- **Official QuickBooks MCP server** (preview since Oct 2025): local MCP server,
  ~144 tools over 29 entities, OAuth authorization-code, one company at a time.

---

## Maintenance note

When something QBO-related breaks with no code change deployed, check in this order:
1. `patterns/error-handling.md` SDK schema-drift ladder (most likely).
2. This file - did a dated Intuit change just go live?
3. The Intuit dev blog (medium.com/intuitdev) for anything newer than this digest.

Digest current as of **2026-07-24**. Refresh it when Intuit announces dated changes.
