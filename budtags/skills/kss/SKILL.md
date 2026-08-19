---
name: kss
description: Use this skill when working with the KSS API (kssdata.com) — the Kiva / Encompass distribution data API — importing products, inventory, customers, invoices, payments, pricing, promotions, purchases, or suppliers from Kiva/Encompass into Budtags.
version: 1.0.0
---

# KSS API (Kiva / Encompass) Reference Skill

You are now equipped with comprehensive knowledge of the **KSS API v1** via **verbatim category files** and **pattern guides**. This skill uses **progressive disclosure** to load only the information relevant to your task.

**Source of truth:** every file under `categories/` and `patterns/` is a 1:1 mechanical transcription of https://kssdata.com/docs/v1 retrieved 2026-08-19 (all 40 endpoints, all parameters, all enum values, all example responses byte-for-byte). When implementing an importer, ALWAYS open the category file and copy field names from it — never from memory. If this SKILL.md summary ever disagrees with a category file, the category file wins.

**Context:** KSS is the data API in front of Encompass, the ERP that Kiva-network distributors run. The one write endpoint queues work that is "exported to Encompass on the next export run". Budtags orgs using Distru + Kiva (e.g. the California org) import from both.

---

## Critical conventions (read first)

### Everything is PascalCase

Response fields (`CustomerID`, `LicenseNum`, `TimeUpdated`), query parameters (`CustomerIDs`, `States`, `Page`, `PageSize`), and envelope keys (`Data`, `HasNextPage`) are all PascalCase. The ONLY camelCase names in the API are path parameters (`/customers/:customerID`). Do not snake_case or camelCase anything when building requests or reading responses.

### Read-only API with exactly ONE write endpoint

39 of 40 endpoints are GET. The only write is `POST /payments/applications` (payment allocation request; not available to Supplier keys; queued as `Pending`, exported to Encompass on the next export run — i.e., writes are eventually consistent with Encompass and confirmed later via `GET /payments/applications` status `Confirmed`/`Rejected`).

### Auth is `x-api-key`; keys are environment-scoped

```
x-api-key: your-api-key
```

Two environments, each with its own isolated database and separate keys:

| Environment | Base host | Notes |
|---|---|---|
| Production | `api.kssdata.com` | Live data, updated continuously |
| Test | `api.test.kssdata.com` | Data refreshed every Sunday morning |

A production key is rejected by test and vice versa. **Our sandbox key is a TEST key and is a Supplier-type key scoped to SupplierID 61 = "Gelato" (CA)** (live-verified 2026-08-19; see `coverage/live-probe-2026-08-19.md`) → `https://api.test.kssdata.com/api/v1/...`. All endpoints are versioned under `/api/v1` — a category-file path like `/customers` means `https://api.test.kssdata.com/api/v1/customers`. Being a Supplier key, it cannot call `POST /payments/applications` and sees data filtered to Gelato's supplier scope. Observed rate limit: 1028 requests/hour.

### Three key types with different data visibility

| Key type | Scope |
|---|---|
| Employee | Full access to all endpoints and all data across any state or customer |
| Customer | Scoped to the customer accounts on the key; out-of-scope requests are **silently filtered** or return `403` |
| Supplier | Scoped to the supplier accounts on the key; some endpoints unavailable entirely |

Endpoints restricted by key type (from the docs' badges/callouts):

- **Not available to Customer keys:** `GET /inventory`, `GET /inventory/batches`, `GET /purchases`, `GET /purchases/:purchaseID`, `GET /purchaseTrans`, `GET /suppliers/creditTerms`, `GET /vendors`
- **Not available to Supplier keys:** `POST /payments/applications`

### SILENT DEFAULT FILTERS — the #1 import gotcha

Several list endpoints filter results by default when a parameter is omitted. An importer that doesn't pass these params will silently miss records:

| Endpoint | Omitted param | Default behavior |
|---|---|---|
| `GET /invoices` | `Statuses` | Returns ONLY New (`1`) status invoices |
| `GET /customers` | `AccountStatuses` | Returns ONLY `Active` customers |
| `GET /products` | `Statuses` | Returns ONLY Active (`1`) products (skipped entirely when `ProductIDs` is provided) |
| `GET /suppliers` | `Active` | Active only, for Customer and Supplier keys |
| `GET /users` | `Active` | Active = true only, for Customer and Supplier keys |
| `GET /vendors` | `Active` | Active = true; only Employee keys may request inactive |
| `GET /payments/types` | `Active` | Active suppliers only; only Employee keys may override |
| `GET /invoiceTransactions` | `Statuses` | If provided WITHOUT Verified (`7`), verified invoices are excluded |

### Required parameters (400/403 if missing)

- `GET /invoiceTransactions` — `InvoiceIDs` required (400 if not provided)
- `GET /invoiceCOAs` — `InvoiceIDs` required (400 if not provided)
- `GET /customerPricing` — `CustomerIDs` required (403 if none are accessible)
- `GET /purchaseTrans` — `PurchaseIDs` required

### Pagination: `Page` / `PageSize` / `Data` envelope

All list endpoints: default page size **50**, maximum **500** (larger values silently reduced to 500). Responses wrap results:

```json
{ "Data": [ ... ], "Page": 2, "PageSize": 100, "HasNextPage": true }
```

`HasNextPage` boolean indicates more results exist — live-verified present on every list response (the per-endpoint doc examples omit it, but the Pagination section's contract governs). Detail GETs (`/:customerID` etc.) ALSO return the full envelope — the single record wrapped in a `Data` **array** plus `Page`/`PageSize`/`HasNextPage` (live-verified) — never expect a bare object.

### Array filters are comma-separated single params

`?CustomerIDs=1,2,3&States=CA,NJ` — typed `number[]`/`string[]`/`boolean[]` in the docs, always passed as one comma-separated query value. No `[]` bracket syntax anywhere.

### Error body key is `Error` (PascalCase) — live-confirmed

The Errors section prose says `error`, but the wire truth (live-verified 2026-08-19) matches the documented example: `{ "Error": "InvoiceIDs parameter is required" }`. Read `Error`. Status codes: 400 (missing/invalid parameter), 401 (missing/invalid key), 403 (no access), 404 (endpoint does not exist), 429 (rate limited), 500 (server error).

### Rate limiting is per key, per hour

Configurable max requests/hour per key. Headers on every response: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` (seconds until recovery). On 429 only: `Retry-After` (seconds) — wait that long, don't hammer.

### Conditional requests + tracing

Every response carries an `ETag`; send it back via `If-None-Match` to get `304 Not Modified` with an empty body when data is unchanged. Responses are `private` — never share a downstream cache between API keys. Every response also carries `X-Request-Id` (echoed back if you send a short alphanumeric token) — include it when contacting KSS support.

### Incremental sync

Most records carry a `TimeUpdated` timestamp, but there is **no generic updated-since filter** documented. Date-window params exist only on: `GET /invoices` (`StartDate`/`EndDate`, invoice date), `GET /purchases` (`StartDate`/`EndDate` on PostDate), `GET /menuPromotions` (`StartDate`/`EndDate` on promotion validity), `GET /customerPricing` (`EffectiveDate`). Everything else must be walked in full and diffed on `TimeUpdated`, or fetched via targeted ID filters. Use ETag/`If-None-Match` to make full re-walks cheap.

### Known doc bugs (kept verbatim in category files)

- `GET /users` lists the `States` parameter **twice** in its Parameters table (source doc bug).
- Invoice `Statuses` enum skips 6: documented values are `1,2,3,4,5,7` (7 = Verified). There is no documented 6.
- Errors prose says `error`; the real key is `Error` (see above).

### Live records are SPARSE — treat every field as optional

Live-verified 2026-08-19: across 500 live `/customers` records, 10 doc-example fields (`OnHold`, `SalesRep*`, `ProfilePictureURL`, `CollectionAgent*`, `NextDeliveryDates`, `DeliveryMinimum`) never appeared — not even as `null` — possibly gated by our Supplier key type. Conversely `/purchases` returned 5 fields the docs don't document (`PurchaseGlobalID`, `PurchaseGlobalIDExportedAt`, `PurchasePDFURLAPIKeyID`, `ReceivingNum`, `TimeCreated`). `/products` matched its doc example perfectly (32/32 across 434 records). Importers must read with `?? null` and never assume the doc example's full shape. Details: `coverage/live-probe-2026-08-19.md`.

---

## Enum reference (exact values)

| Enum | Values |
|---|---|
| Customer `AccountStatuses` | `Active`, `Inactive`, `OutOfBus` (Out of Business) |
| Customer `OnHold` | `true` (On Hold), `false` (Not On Hold) |
| Invoice `Statuses` | `1` New, `2` Locked for Routing, `3` Loaded, `4` Returned, `5` Balanced, `7` Verified |
| Product `Statuses` | `0` Discontinued, `1` Active, `2` Pre-order, `3` Manufacture, `4` Unavailable, `5` Close Out |
| Purchase `Statuses` | `New`, `Accepted`, `Received`, `Confirmed`, `Verified` |
| Payment application `Statuses` | `Pending` (queued for export to Encompass), `Exported` (sent, awaiting confirmation), `Confirmed` (applied in Encompass), `Rejected` (not confirmed within the timeout window) |
| User `Roles` | `Customer`, `Supplier`, `Admin`, `DistributorRep` (Distributor Rep) |

---

## Available Resources

### Category files (verbatim, one per docs group — 40 endpoints total)

- `categories/allocations.md` — GET /allocations (unique key is [Allocation, ProductID, CustomerID])
- `categories/ar-aging.md` — GET /arAging (recalculated once per day at end of day)
- `categories/pricing.md` — GET /customerPricing (CustomerIDs required; EffectiveDate for promo validity)
- `categories/customers.md` — GET /customers, /customers/creditTerms, /customers/:customerID, /deliveryDays (DeliveryDays: 1 = Monday … 7 = Sunday)
- `categories/inventory.md` — GET /inventory, /inventory/batches, /retailerInventory. **The only endpoint group with a response Field Definitions table** (Inventory, Loaded, Picked, Delivered, Unsellable, OnFloorInventory, PreSales, Allocated, AvailableUnits, Received, NotAuthorized, PurchaseTransID — FIFO layer semantics)
- `categories/invoices.md` — GET /invoices, /invoices/:invoiceID, /invoiceTransactions(+/:invoiceID), /invoiceCOAs(+/:invoiceID), /invoices/creditTerms
- `categories/locations.md` — GET /locations, /locations/:locationID
- `categories/promotions.md` — GET /menuPromotions, /promotionsProducts
- `categories/products.md` — GET /productCategories (no params), /products, /products/:productID
- `categories/states.md` — GET /states
- `categories/suppliers.md` — GET /suppliers, /suppliers/creditTerms, /suppliers/:supplierID
- `categories/users.md` — GET /users, /users/:userID
- `categories/payments.md` — GET /payments/types, /payments, /payments/openInvoices, /payments/applications, **POST /payments/applications** (the API's only write)
- `categories/vendors.md` — GET /vendors
- `categories/purchases.md` — GET /purchases, /purchases/:purchaseID
- `categories/purchase-transactions.md` — GET /purchaseTrans (line items for purchases; PurchaseIDs required)
- `categories/sales-reps.md` — GET /salesReps (ProductGroups filter: 'Supplier' for Supplier Reps, or product-line names e.g. 'Cookies')

### Coverage (Budtags-specific live findings, NOT wire-contract docs)

- `coverage/live-probe-2026-08-19.md` — live verification against the test key: key type/scope, confirmed envelope + error casing + ETag/304, live-vs-doc field diffs per endpoint, unresolved questions

### Pattern files (verbatim transcriptions of the docs' intro sections)

- `patterns/getting-started.md` — environments, base URLs, versioning
- `patterns/authentication.md` — x-api-key header, Employee/Customer/Supplier key types
- `patterns/rate-limiting.md` — per-key hourly limits, RateLimit-* headers, Retry-After
- `patterns/pagination.md` — Page/PageSize/Data/HasNextPage envelope
- `patterns/errors.md` — status codes, error body
- `patterns/response-headers.md` — X-Request-Id tracing, ETag/If-None-Match conditional requests

---

## Domain Routing

| User's topic | Keywords | Load |
|---|---|---|
| Product catalog | product, SKU, category, supplier product number, discontinued | `categories/products.md` |
| Stock levels | inventory, on floor, available, batch, FIFO, warehouse, retailer inventory | `categories/inventory.md`, `categories/allocations.md` |
| Customers / retailers | customer, retailer, license, account status, on hold, delivery days, chain | `categories/customers.md` |
| Sales / billing | invoice, line item, transaction, COA, credit terms | `categories/invoices.md` |
| Money / AR | payment, allocation, application, open invoice, AR account, aging | `categories/payments.md`, `categories/ar-aging.md` |
| Pricing / promos | price, customer pricing, promotion, menu promotion | `categories/pricing.md`, `categories/promotions.md` |
| Procurement | purchase, vendor, purchase transaction, receiving | `categories/purchases.md`, `categories/purchase-transactions.md`, `categories/vendors.md` |
| Reference data | state, location, user, sales rep, supplier | `categories/states.md`, `categories/locations.md`, `categories/users.md`, `categories/sales-reps.md`, `categories/suppliers.md` |
| Auth / plumbing | api key, 401, 403, 429, rate limit, pagination, ETag, request id | `patterns/*.md` |

---

## Complete Endpoint Index (40)

```
GET  /allocations                        Paginated
GET  /arAging                            Paginated
GET  /customerPricing                    Paginated · CustomerIDs REQUIRED
GET  /customers                          Paginated · defaults to Active
GET  /customers/creditTerms              Paginated
GET  /customers/:customerID
GET  /deliveryDays                       Paginated
GET  /inventory                          Paginated · NOT for Customer keys
GET  /inventory/batches                  Paginated · NOT for Customer keys
GET  /retailerInventory                  Paginated
GET  /invoices                           Paginated · defaults to Statuses=1 (New)
GET  /invoices/:invoiceID
GET  /invoiceTransactions                Paginated · InvoiceIDs REQUIRED
GET  /invoiceTransactions/:invoiceID     Paginated
GET  /invoiceCOAs                        Paginated · InvoiceIDs REQUIRED
GET  /invoiceCOAs/:invoiceID             Paginated
GET  /invoices/creditTerms               Paginated
GET  /locations                          Paginated
GET  /locations/:locationID
GET  /menuPromotions                     Paginated
GET  /promotionsProducts                 Paginated
GET  /productCategories                  Paginated · no parameters
GET  /products                           Paginated · defaults to Statuses=1 (Active)
GET  /products/:productID
GET  /states                             Paginated
GET  /suppliers                          Paginated · defaults to Active
GET  /suppliers/creditTerms              Paginated · NOT for Customer keys
GET  /suppliers/:supplierID
GET  /users                              Paginated · defaults to Active
GET  /users/:userID
GET  /payments/types                     Paginated
GET  /payments                           Paginated
GET  /payments/openInvoices              Paginated
GET  /payments/applications              Paginated
POST /payments/applications              NOT for Supplier keys · THE ONLY WRITE
GET  /vendors                            Paginated · NOT for Customer keys
GET  /purchases                          Paginated · NOT for Customer keys
GET  /purchases/:purchaseID              NOT for Customer keys
GET  /purchaseTrans                      Paginated · NOT for Customer keys · PurchaseIDs REQUIRED
GET  /salesReps                          Paginated
```

---

## Progressive Loading Process

**IMPORTANT:** Only load files relevant to the question. DO NOT load all categories.

1. **Identify the domain** from the table above and load that category file.
2. **Copy field names, parameter names, and enum values directly from the category file** — they are verbatim from the KSS docs. Never reconstruct a field name from memory.
3. For plumbing questions (auth, paging, errors, caching, rate limits), load the matching `patterns/` file.
4. When implementing a Budtags importer, follow the house rule: translate KSS data to **native Budtags primitives** at the import boundary (see `integration_translate_to_native` conventions), and resolve partners through the shared partner-resolution layer — never a new bespoke copy.

---

## Quick Reference

### A full request

```
GET https://api.test.kssdata.com/api/v1/products?States=CA&Statuses=1&Page=1&PageSize=500
x-api-key: your-api-key
```

### Walking a paginated list

```
Page=1, PageSize=500 → read Data[], check HasNextPage → Page=2 … until HasNextPage=false
```

### Common pitfalls

```
Forgetting Statuses on /invoices — you only get New (1) invoices
Forgetting AccountStatuses on /customers — you only get Active customers
Forgetting Statuses on /products — you only get Active products
Expecting a bare object from /:id detail endpoints — Data is still an ARRAY
Sending snake_case or camelCase params — everything is PascalCase (CustomerIDs, PageSize)
Using bracket-array syntax (IDs[]=1&IDs[]=2) — KSS wants comma-separated (IDs=1,2)
Using the prod host with the sandbox key — our key is TEST; api.test.kssdata.com
Assuming test data is current — the test DB refreshes every Sunday morning
Treating POST /payments/applications as synchronous — it queues Pending and exports to Encompass later
Retrying a 429 immediately — honor Retry-After seconds
Expecting an updated-since filter — only TimeUpdated on records + ETag re-walks
Reading the error message from body.error — the live key is "Error" (PascalCase)
Assuming doc-example fields always arrive — live records omit fields entirely; read with ?? null
Treating numeric-looking values as numbers — e.g. inventory DOI/AvgDailySales90d are string decimals
Calling POST /payments/applications with our key — Supplier keys get 403
```

---

## Your Mission

Help users integrate Budtags with the KSS (Kiva/Encompass) API by:

1. **Loading ONLY the relevant category/pattern file** (progressive disclosure)
2. **Copying field and parameter names verbatim from the category files** — never from memory
3. **Warning about silent default filters** (invoices/customers/products/active-flags)
4. **Respecting key-type restrictions** (Customer vs Supplier vs Employee)
5. **Using the test host** for our sandbox key until a production key exists
6. **Flagging the doc bugs** (duplicate States on /users; Error/error casing) instead of tripping over them

**Every wire-level fact in categories/ and patterns/ is a mechanical 1:1 transcription of the KSS docs. Trust the files, not recollection.**
