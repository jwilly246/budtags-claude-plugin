# Mapping-session findings (running log)

Budtags-specific findings from the KSS mapping project, written here as they land (Jason's standing
instruction 2026-08-19: findings go into the skill as we discover them). Authority for field-by-field
dispositions: `KSS-INTEGRATION-MAPPING.md` at the budtags repo root. This file carries the durable
principles and gotchas an implementer must know even without the mapping doc open.

## Semantics of the supplier-side view (Gelato org, CA)

- KSS "customers" = retailers buying our product; "purchases" = KSS buying FROM our contract
  manufacturers (the mirror of OUR outbound Distru/Metrc transfers to Kiva); "invoices" = KSS's sales
  to retailers = DEPLETIONS of our brand. Gelato is not a party to KSS invoices - they must NEVER land
  in marketplace_orders/marketplace_invoices.
- CA operating model is consignment-like: Gelato ships everything to KSS and may never hold sellable
  Metrc inventory in-house (unconfirmed - open question). KSS stock numbers are plausibly the org's
  PRIMARY inventory view, so inventory UI is in scope, not optional.

## Cardinal mapping principles (Jason-ratified)

1. **Ownership isolation**: KSS's numbers about our product never share our first-party columns
   (products.quantity, marketplace_invoices, seller_credits...). Mirror/snapshot tables or JSON.
2. **First-party ledgers are never landing zones for third-party observations** (2026-08-19, on
   payments -> seller_credits): seller_credits/credit_applications are OUR operational ledgers - our
   promo settlement already writes seller_credits via promo_deals.seller_credit_id, and
   credit_applications.marketplace_order_id can only reference our orders. KSS SupplierCredit rows are
   reconciliation EVIDENCE matched against those ledgers, never rows in them. Same logic bans KSS
   invoices from marketplace_invoices.
3. **No silent discarding**: every KSS field with operational meaning is displayed somewhere or
   deliberately parked with Jason's sign-off (the mapping doc's NOUSE report). JSON blobs are for
   plumbing only, never display candidates.
4. **Zero of the NEW fields are conceptually new** (verified against all 191 tables): every one is a
   rename, grain difference, or derivation. "New" = ownership isolation only.

## Metrc joins (the structural gold)

- `GET /inventory/batches` field `UID` = Metrc package tag (1A40603...) + full lab data + COA URL.
- `GET /purchaseTrans` field `PalletTag` = Metrc tag of pallets we shipped; `FOB`/`LaidInCost` = what
  KSS paid per unit. Chain: our Metrc transfer -> PalletTag -> PurchaseID -> KSS receipt status/costs.

## Existing tables an implementer might miss (twin-audit finds)

- `promo_deal_verified_sales` - near column-for-column fit for a KSS invoice line (invoice_number,
  quantity_sold, unit_price, original_price, discount_amount, sub_total) with multi-source
  `match_source`; promo-relevant depletion lines can land there (match_source='kss') with existing UI.
- `credit_applications` + `seller_credits` - concept twins for supplier-credit flows;
  RECONCILIATION TARGETS ONLY (principle 2).
- `metrc_package_local_metadata` (tag -> batch code, source varchar) - the batch/tag join spot.
- `product_batches` / `product_batch_links` / `batch_documents` - lab potency, COA PDFs.
- `customer_inventory_snapshots` - concept twin of /retailerInventory.
- `business_partners.payment_term` - candidate for retailer KSS credit terms (semantic caveat: means
  OUR terms; under full consignment the KSS term is the only one).

## Wire gotchas discovered while mapping (beyond the live-probe file)

- Silent default filters hide data from importers: /invoices returns ONLY Statuses=1 (New);
  /customers only Active; /products only Active; /users//vendors//suppliers//payments/types
  Active-only. Pass explicit full status lists ALWAYS.
- `payments.PaymentTypeID = -1` is an undocumented sentinel: PaymentTypeName 'SupplierCredit'
  (100% of rows visible to our Supplier key).
- Sentinel values: retailerInventory.LastInventoryDate '2000-01-01' = never counted;
  customerPricing.EndDate '3000-12-31' = open-ended; customers hold 'LIC-99999-FAKE' and '#N/A'
  test garbage - sanitize.
- /inventory `Inventory` can be NEGATIVE (derived sum; live: -7025). AvailableUnits is a JSON number
  while sibling buckets are string decimals.
- invoices' update stamp is named `InvoiceLastUpdated` (not TimeUpdated like everywhere else).
- PDF links (invoices.PDFURL, purchases.PublicPDFLink) embed an Encompass APIKeyID - treat as
  sensitive; do not persist (recommendation pending Jason).
- /promotionsProducts: HTTP 500 on every test attempt - KSS support ticket owed.
- Empty on test DB: /allocations, /customers/creditTerms; /invoiceCOAs detail for a specific invoice
  can be empty while the bulk query returns rows.
- purchases 'Terms' includes 'Interco Transfer' (intra-Kiva moves) - filter from revenue recon.
- Bulk-stamped TimeUpdated values on test (whole pages share one stamp) - page-level freshness only.
