# Cross-Importer Number/Term/Date/Charge Audit

> **What this is:** BudTags **integration-coverage** documentation — a code-verified comparison of how *our* Distru, LeafLink, and Canix order importers behave (identifier preservation, payment terms/dates, charge projection, write-back-loop suppression). This is NOT a Distru wire-contract reference; it audits BudTags importer code across three sources, with Distru as the reference implementation. For the Distru API contract see the sibling `categories/*.md` files; for per-field Distru coverage see `coverage/field-coverage-audit.md`.
>
> This document is the canonical home of the cross-importer audit. It was relocated verbatim into the skill from the BudTags repo's former native-conversion audit folder; the repo copy is retired.

Read-only comparison of Distru (reference), LeafLink, and Canix order importers on identifier preservation, payment terms/dates, charge projection, and write-back-loop suppression.

Verified against actual code on 2026-05-26.

## Matrix

| # | Concern | Distru (reference) | LeafLink | Canix |
|---|---------|--------------------|----------|-------|
| 1 | Preserves source order_number as-is? | ✅ `'order_number' => empty_to_null($distru_order['order_number'])` (`OrderImporter.php:639`). 2,038/2,038 rows preserve `SO-XXXX`. | ✅ `'order_number' => $data['number']` (`OrderImporter.php:141`, buyer path `:1166`). Stores LeafLink long order_number / UUID verbatim — but this is NOT the human ID. | ⚠️ `'order_number' => $data['name'] ?? $data['external_identifier'] ?? "CANIX-{$data['id']}"` (`OrderImporter.php:509`). Three-level fallback masks empty-name cases as synthesized IDs without a flag. |
| 2 | Customer-facing display identifier | `order_number` (e.g., `SO-1234`) — `OrderImporter.php:639` | `short_id` — captured at `OrderImporter.php:143` (seller) and `:1167` (buyer). `order_number` is a long UUID/number not meant for humans. | `order_number` (Canix `name`, e.g., `SO-XXX` from Canix UI) — `OrderImporter.php:509` |
| 3 | Synthesizes fallback when source order id empty? | ✅ Only when `order_number` is truly empty: `'DST-'.substr($distru_order['id'], 0, 8)` (`OrderImporter.php:581-583`). 0/2,038 occurrences in current data. | ⚠️ Falls back to `MarketplaceOrder::generate_order_number($orgId)` (`OrderImporter.php:141`) producing a BudTags-native `MKT-{ORG_PREFIX}-{SEQ}` or random `MKT-...` ID — indistinguishable from a hand-keyed order. Buyer path identical at `:1166`. | ⚠️ `"CANIX-{$data['id']}"` (`OrderImporter.php:509`) inline — third-tier fallback after `name`/`external_identifier`. No flag distinguishing real vs synthesized. |
| 4 | Preserves source invoice_number? | ✅ Separate `marketplace_invoices` table + `InvoiceImporter`. `'invoice_number' => empty_to_null($invoice['invoice_number'])` (`InvoiceImporter.php:514`); fallback `'DST-INV-'.substr($id, 0, 8)` (`:464-465`). | n/a — LeafLink data model has no separate invoice entity; orders ARE the invoice. No `invoice_number` column populated by LeafLink importer. | n/a — Canix data model has no separate invoice; `invoice_url` is captured (`OrderImporter.php:534`) but no `invoice_number` is parsed. |
| 5 | Preserves source PO number on buyer-side mirrors? | n/a — Distru orders are seller-side; `purchase_orders` table not touched by Distru `OrderImporter`. | ✅ Buyer path: `'customer_po_number' => $data['ext_acct_id']` (`OrderImporter.php:1175`). Seller path does NOT capture customer_po_number. | ✅ Sales-order side: `'customer_po_number' => $data['external_identifier']` (`OrderImporter.php:522`). PO side: `'po_number' => $data['name']` (`OrderImporter.php:574`) — goes to `purchase_orders` table. |
| 6 | Sets `marketplace_orders.payment_due_date` from source? | ✅ `'payment_due_date' => parse_distru_date($distru_order['due_datetime'])` (`OrderImporter.php:647`). | ✅ `'payment_due_date' => ImportUtils::parse_date($data['payment_due_date'])` (`OrderImporter.php:157`, seller only — buyer path does not set this). | ⚠️ `'payment_due_date' => parse_date($data['payment_date'])` (`OrderImporter.php:529`) — but `payment_date` is the date the order was PAID, not due. Wrong semantic mapping. |
| 7 | Sets `marketplace_orders.payment_term` from source? | ✅ `'payment_term' => empty_to_null($distru_order['payment_term_name'])` (`OrderImporter.php:643`); also propagates onto `Customer.payment_term` via `backfill_customer_payment_term` (`:433-460`). | ✅ `'payment_term' => ImportUtils::extract_order_payment_term_code($data)` (`OrderImporter.php:162` seller, `:1233` buyer). Normalizes nested-object / flat-string / selected_payment_option shapes to a canonical slug. | ✅ `'payment_term' => $data['payment_terms']` (`OrderImporter.php:523`). Raw passthrough, no normalization. |
| 8 | Projects shipping/discount/tax from source charges/totals to native columns? | ✅ `project_charges()` (`OrderImporter.php:747-829`) dispatches charges[] by type → tax/cultivation_tax/shipping/discount; preserves verbatim in `order_taxes` JSON. | ⚠️ Partial. `shipping` from `shipping_charge` (`:149`), `tax` from `final_tax`/`tax_amount` (`:124`), `discount` from `data['discount']` (`:151`), `order_taxes` JSON passthrough (`:197`). No charges[] decomposition — LeafLink ships pre-computed scalars, not an itemized charges array. | ⚠️ Backed-out math: `tax = total - subtotal - delivery_fee + discount + credits` (`OrderImporter.php:497-499`), `shipping = delivery_fee` (`:514`), `discount` direct (`:516`), `cultivation_tax` from `total_cultivation_tax` (`:533`). NO `order_taxes` JSON capture — verbatim source breakdown is lost. |
| 9 | Captures `marketplace_orders.ship_date` for due-date derivation? | ✅ `'ship_date' => parse_distru_date($distru_order['delivery_datetime'])` (`OrderImporter.php:646`). | ✅ `'ship_date' => parse_date($data['ship_date'])` (`OrderImporter.php:163` seller, `:1194` buyer). | ✅ `'ship_date' => parse_date($data['delivery_date'])` (`OrderImporter.php:536`). |
| 10 | Captures custom fields / external metadata? | ✅ `external_ids` JSON gets `distru_creator`, `distru_owner`, `distru_billing_location`, `distru_shipping_location`, `distru_custom_fields`, `distru_order_datetime`, `distru_company`, etc. (`OrderImporter.php:606-627`). Plus `DistruCustomFieldDefinitionService::record_sightings()` at `:384-388`. | ⚠️ `external_data` column dumps the whole payload minus `line_items` (`OrderImporter.php:189`) — verbatim but unstructured. Plus dedicated columns: `external_id_seller`, `external_id_buyer`, `external_ids`, `leaflink_created_by`, `external_brand_id`, `external_available_transitions` (`:180-206`). No custom-field-definition sightings recorder. | ❌ No structured external_ids JSON. No verbatim payload preservation. Selective columns (`canix_order_id`, `invoice_url`, `sales_reps`) only. Source-specific fields not on `marketplace_orders` are dropped. |
| 11 | Has `within_inbound` suppression to prevent write-back loops? | ✅ `import_orders()` wraps in `DistruInboundContext::within_inbound(...)` (`OrderImporter.php:180`). | ✅ At job level: `RunLeafLinkImport.php:69` wraps in `LeafLinkWebhookContext::within_inbound(...)`. NOT inside `OrderImporter` itself — the wrap is the caller's responsibility. | ❌ No `CanixInboundContext`, no `within_inbound` wrap in `OrderImporter::import_sales_orders()` or any Canix job. Currently safe only because `CanixOutboundSync` is invoked manually, but any future observer-driven push back to Canix would loop. |

## Discoverable Follow-Ups

### Gap A — LeafLink synthesizes `MKT-...` fallback indistinguishable from native (Row 3)
**Where:** `app/Services/LeafLink/OrderImporter.php:141` and `:1166` use `MarketplaceOrder::generate_order_number($orgId)` when `$data['number']` is missing.
**Risk:** Empty-source orders look identical to BudTags-native orders. Cannot detect/measure "how often did LeafLink ship us an empty order number?" without a flag.
**Fix:** Mirror Distru's `DST-` prefix pattern — synthesize `LL-{uuid8}` from `$data['short_id']` or `$data['id']` so synthesized vs source-native is distinguishable on inspection. Log a warning on synthesis.

### Gap B — Canix order_number fallback chain hides empty-source cases (Row 3)
**Where:** `app/Services/Canix/OrderImporter.php:509` chains `name → external_identifier → "CANIX-{id}"` silently.
**Fix:** Split into explicit precedence with a `was_synthesized` log: prefer `name`, never fall through to a synthesized format without `LogService::store(...)` recording the case.

### Gap C — Canix `payment_due_date` is wrong field (Row 6)
**Where:** `app/Services/Canix/OrderImporter.php:529` maps `payment_date` (date paid) into `payment_due_date` (date due). These are semantically opposite.
**Fix:** Use `due_date` / `payment_due_date` field from Canix if present; if Canix only ships `payment_date`, derive due date from `ship_date + payment_term` (consistent with Distru's `due_datetime` semantics). The current mapping makes paid-on-time orders appear "due in the past."

### Gap D — Canix loses verbatim tax/charges breakdown (Row 8)
**Where:** `app/Services/Canix/OrderImporter.php:497-499` backs out tax by arithmetic; no `order_taxes` JSON write. Distru's Decision #13 pattern preserves the source breakdown.
**Fix:** Capture Canix's tax-rate / cultivation_tax / discount source fields into `order_taxes` JSON verbatim for round-trip + forensic audit.

### Gap E — LeafLink seller path doesn't capture `customer_po_number` (Row 5)
**Where:** `app/Services/LeafLink/OrderImporter.php:135-207` (seller path) — no `customer_po_number` key. Buyer path (`:1175`) maps `ext_acct_id`.
**Fix:** Add `'customer_po_number' => $data['ext_acct_id'] ?? null` to the seller `$orderData` block. Buyer-placed PO ref is on the seller-received order envelope too.

### Gap F — Canix has no inbound-suppression wrap (Row 11)
**Where:** `app/Services/Canix/OrderImporter.php:109` (`import_sales_orders`) and the job/command that invokes it. No `CanixInboundContext::within_inbound(...)` equivalent.
**Risk:** Any future Canix outbound-sync observer (paralleling `SyncMarketplaceOrderToDistru`) would echo just-imported Canix data right back to Canix.
**Fix:** Build `CanixInboundContext` mirroring `DistruInboundContext` + `LeafLinkWebhookContext`, wrap `import_sales_orders()` and `import_purchase_orders()`.

### Gap G — Canix has no `external_ids` JSON, drops source-specific fields (Row 10)
**Where:** `app/Services/Canix/OrderImporter.php:508-540` — no JSON catch-all column write. Anything not on a named column is dropped.
**Fix:** Capture verbatim Canix payload sub-objects (sales_order_credit, customer, sales_representative, etc.) into a new `external_ids` JSON write — mirrors Distru's `distru_creator`/`distru_owner` retention pattern.

### Gap H — LeafLink has no custom-field-definition sightings recorder (Row 10)
**Where:** LeafLink dumps payload to `external_data` (`OrderImporter.php:189`) without inventorying which custom fields appeared.
**Fix:** Optional — add a LeafLink-equivalent of `DistruCustomFieldDefinitionService::record_sightings()` if LeafLink starts shipping `custom_data` on orders (currently unobserved; defer until evidence).
