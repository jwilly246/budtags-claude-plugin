# Live probe findings — 2026-08-19 (test environment, Supplier key)

Budtags-specific live verification, distinct from the verbatim wire docs in `categories/`/`patterns/`. ~14 GET requests against `https://api.test.kssdata.com/api/v1` with the sandbox key (no writes attempted). Raw captures lived in the probing session's scratchpad; re-run cheaply with any HTTP client.

## Our key (the sandbox key Jason got from Kiva)

- **Type: Supplier key, scoped to SupplierID 61 = "Gelato" (State: CA, Active: true).**
  Evidence: `/suppliers` returns exactly 1 supplier; `Active=false` override is ignored (docs: only Employee keys may request inactive); all Customer-key-blocked endpoints (`/inventory`, `/purchases`, `/suppliers/creditTerms`) return 200.
- Consequences: `POST /payments/applications` will 403 (Supplier keys blocked). Data is silently filtered to Gelato's authorized supplier scope where scoping applies.
- Key file location: `meeting-plans-endo-2026-08-12/ksskey` in the budtags repo working tree (untracked).
- Observed rate limit: `RateLimit-Limit: 1028`/hour, `RateLimit-Reset: 3600`.

## Confirmed wire facts

| Question | Live answer |
|---|---|
| Auth | `x-api-key` works on test host; 200s across the board |
| Envelope | Every list response: `{ Data, Page, PageSize, HasNextPage }` — `HasNextPage` present on ALL list endpoints (per-endpoint doc examples simply omit it) |
| Detail endpoints | `GET /customers/:id` returns the FULL envelope too: `Data` (array of 1), `Page: 1`, `PageSize: 50`, `HasNextPage: false` — doc example showing only `Data` is abbreviated |
| Error body | `{"Error":"InvoiceIDs parameter is required"}` — **PascalCase `Error` confirmed**; the Errors section prose saying `error` is wrong |
| ETag / 304 | Weak ETag (`W/"..."`) on responses; `If-None-Match` replay returns **304** — confirmed working |
| Tracing | `x-request-id` UUID on every response; `cache-control: private, no-cache` |
| Numbers as strings | Inventory `DOI` and `AvgDailySales90d` arrive as **string decimals** (`"5.60"`, `"201.49"`) — do not assume numeric JSON types |
| Infra | Served from Google Frontend (GCP); CSP references `encompass8.com` (the Encompass connection is visible in headers) |

## Field-set diffs: live union vs doc-example JSON

Method: union of keys across all live records fetched vs keys in the category file's example response.

| Endpoint | Live sample | Verdict |
|---|---|---|
| `/products` | 434 records | **Perfect match** — all 32 doc fields, nothing extra |
| `/states` | 1 record | Perfect match (6/6) |
| `/inventory` | 1 record | Perfect match (17/17). Note: the docs' Field Definitions table defines only 12 of the 17 example fields — `DOI`, `AvgDailySales90d`, `LocationID`, `ProductID`, `TimeUpdated` have no definitions |
| `/purchases` | 1 record | **5 UNDOCUMENTED live fields**: `PurchaseGlobalID`, `PurchaseGlobalIDExportedAt`, `PurchasePDFURLAPIKeyID`, `ReceivingNum`, `TimeCreated` |
| `/customers` | 500 records | **10 doc-example fields NEVER appear live**: `OnHold`, `SalesRepEmail`, `SalesRepName`, `SalesRepPhone`, `SalesRepUserID`, `ProfilePictureURL`, `CollectionAgentFullName`, `CollectionAgentEmail`, `NextDeliveryDates`, `DeliveryMinimum` |

## Interpretation of the /customers gap (unresolved)

Across 500 live customer records, none of the 10 fields above is present even as `null` — yet the doc example shows them (including an explicit `"CollectionAgentFullName": null`). Hypotheses, undecided:

1. **Key-type gating** — sales-rep/collections/hold data hidden from Supplier keys (most likely; it is customer-relationship data)
2. Sparse serialization — keys omitted when valueless in the test DB

Either way the importer rule is the same: **treat every response field as optional** (`$record['Field'] ?? null`), never assume the doc example's full shape arrives. Re-check against a production or Employee key before relying on those 10 fields.

## Still unverified

- Production host behavior (we only have the test key; prod key owed from Kiva when going live)
- `POST /payments/applications` (would 403 for this key type; untestable until a Customer/Employee key exists)
- Whether the 10 missing customer fields appear for other key types
- Max-PageSize clamping behavior above 500 (not probed; docs say reduced to 500)
