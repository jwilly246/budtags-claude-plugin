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

## Value-level join verification (script-only, test key)

- ID graph is SOUND: inventory/batches/purchaseTrans/invoiceTransactions ProductID -> products all 100%
  (products + inventory sets fully paginated).
- batches.UID: 100% valid Metrc tag format (500/500 non-null). purchaseTrans.PalletTag: 100% valid where
  present (26/500 null). The Metrc bridge and reconciliation joins are REAL, not doc claims.
- BatchCode cross-joins measured 67-77% only because the batch walk was sample-limited - re-run full-walk
  before quoting a rate.
- customers.LicenseNum: 90.6% valid CA format on page 1 (44 null + LIC-99999-FAKE garbage) - importers
  tolerate missing/garbage licenses.

## Dual-source requirement (customer statement 2026-08-19)

~25% of orders in Distru, ~75% in KSS; Budtags = single combined view. Consequences: Decision C is half
the order universe, not analytics; union-at-view-layer recommended over ingesting KSS invoices into
marketplace_orders; CRITICAL double-count firewall - the Gelato->KSS bulk leg (Distru order) depletes as
KSS invoices, so combined retailer-order views must EXCLUDE the bulk leg (it reconciles via PalletTag /
Decision D); same retailer in both sources resolves to ONE business_partner via partner resolution +
integration_company_mappings; same product carries both external_ids keys.

Keys still owed for the next verification rounds: Gelato Distru key (overlap study), CA Metrc key
(PalletTag/UID vs actual transfers), production KSS key (true fill rates).

## Dual-source overlap study - MEASURED (Gelato Distru key arrived 2026-08-19)

90-day window (2026-05-21..08-19), Distru live vs KSS test snapshot, script-only:
- Split: 12.4%/87.6% by order count, 9.9%/90.1% by dollars (Distru direct $1.06M vs KSS $9.71M).
  Customer estimated 25/75 - KSS even more dominant.
- Bulk leg Gelato->Kiva: 25 Distru orders, $2.47M = 70% of Distru dollars. Naive union inflates
  revenue ~19%. Double-count firewall is MANDATORY.
- Retailer dedup: 97% (130/134) of Distru direct-order licenses exist as KSS customers; +492
  exact-name overlaps. License-first partner resolution validated with real data.
- Product dedup BROKEN as designed: 0 SKU matches (SupplierProductNumber garbage), 2/778 exact-name.
  Fix: Metrc-tag bridge bootstrap (KSS batches.UID and Distru package tags are both Metrc tags ->
  package->product each side -> product pairs), residue manual.
- Gelato owns retail stores ('Gelato Retail - Lake Elsinore' among top direct companies) - own-store
  transfers need their own classification in combined views.
- Gelato Distru tenant: 1,253 companies, 1,840 products, 2 locations; 'Kiva Sales and Service Inc'
  is the bulk-leg company (relationship_type null).

## Probe gotchas (Distru)

- Distru's edge returns **403 for Python-urllib User-Agent** - looks exactly like an RBAC failure
  (we nearly misdiagnosed). curl or a real User-Agent works. An intermittent 500 also appeared once
  on /companies; retry succeeded.
- Gelato Distru API key lives on line 3 of budtags repo meeting-plans-endo-2026-08-12/ksskey
  (line 1 = KSS test key). JWT, exp ~2027-08.

## Jason's NOUSE rulings (2026-08-19) - keep-everything

- AR/collections (60 fields) + depletion-mirror riders (13) + printed-label potency (4): ALL promoted
  NOUSE -> NEW with named tables/columns. New stores: kss_ar_aging + kss_ar_aging_invoices,
  kss_payments, kss_payment_applications, kss_credit_terms; kss_invoices rider columns; product_batches
  label_thc/label_cbd/label_total_cannabinoids/coa_expiration_date. First-party-ledger principle stands
  (all reconcile against, never write into, seller_credits/credit_applications).
- Matrix now: MAP:55 NEW:128 REPORT:13 JOIN:114 NOUSE:53 BLOCKED:54 (of 417).
- Every kept group is UI-classified in the mapping doc: UI SURFACE (KSS inventory, retailer inventory,
  combined orders) vs DASHBOARD/REPORT (AR health, credit recon, label audit, purchase recon) vs
  EXISTING UI (promos, partners, products) vs PLUMBING (reference maps).
- kss_invoices.pdf_url: stored but SENSITIVE (embeds Encompass APIKeyID) - internal fetch only.

## customerPricing semantics (live-verified explainer)

Three price layers, same product ('Last Bite 100mg' example): products/customerPricing.FullPrice =
LIST price ($8.00, same for all); customerPricing.UnitPrice = that RETAILER's effective price TODAY
(list minus their active promo: $4.90-$7.30 across 60 customers, 7 distinct prices, PromotionID
attached); invoiceTransactions.UnitPrice = REALIZED price frozen on each past sale. customerPricing is
the forward-looking per-retailer quote sheet; invoices are backward-looking history. Only
customerPricing answers "what would retailer X pay today".

## Audit COMPLETE + paid-status semantics (2026-08-19)

- NOUSE audit finished across five Jason rulings: final matrix MAP:54 NEW:193 JOIN:114 BLOCKED:56 NOUSE:0
  (of 417). End-state architecture = a full kss_* mirror layer (distru_* precedent): kss_invoices(+lines),
  kss_purchases(+lines), kss_ar_aging(+invoices), kss_payments, kss_payment_applications, kss_credit_terms,
  kss_customer_pricing, kss_inventory_snapshots, kss_retailer_inventory, kss_customers, kss_vendors,
  kss_users, kss_sales_reps, kss_products, kss_product_categories, kss_locations, kss_states, kss_suppliers.
  Decision D resolved: kss_purchases mirror + recon report (REPORT status retired). Decision G promoted.
- PAID-STATUS: derive kss_invoices paid from OpenBalance==0, NEVER from Status - live-verified that
  Verified (7) invoices average $2,425 still owed; Balanced (5) unused on test. Retailer cash payments are
  invisible to Supplier keys (only SupplierCredit rows). KSS AP to suppliers not in the API - Gelato's own
  receivables stay on the Distru/QBO path. No KSS writes into order_payments ever.
- Money fields: string decimals -> integer cents (no-floats rule), never floats.

## THE SINGLE MIGRATION (Jason 2026-08-19)

One all-encompassing consolidated migration (`kss_integration_schema`) - the Distru convention, planned
upfront this time: 21 kss_* tables (158 data columns + keys/links) AND the 4 alters
(organizations.kss_supplier_id, product_batches label/units columns, promo_deals.external_ids,
integration_sync_events enum) all in ONE file with idempotent guards; iterate in place until shipped, then
locked. Money columns decimal(14,6) preserving wire precision (sub-cent values occur live); app arithmetic
per integer-cents rule. kss_time_updated/kss_time_created datetime(3) on every mirror row as the diff cursor.
kss_purchase_lines.pallet_tag stored AND indexed (the Metrc join). Reserved for prod data: kss_allocations,
kss_promotions_products, kss_customer_credit_terms. Full spec: THE SINGLE MIGRATION section of
KSS-INTEGRATION-MAPPING.md.

## Verification sweep (2026-08-19, "any rocks unturned" pass)

- Doc consistency: CLEAN - every NEW row lands in the single-migration spec (or is a declared echo); every
  MAP row's cited Budtags column exists in the schema. Verified mechanically.
- **`/inventory/batches` is CURRENT-INVENTORY-SCOPED, not batch history.** Full walk: 1,117 rows / 434
  batch codes. Recent invoice lines -> batches join 99.7%; all-history purchase lines only 18.5% because
  sold-out batches VANISH from the endpoint. Importer rule: harvest batches continuously, retain forever
  (last_seen_at, never delete on absence); the mirror is the only history. Open: do cdn.e8.co COA links
  outlive the listing? If not, archive PDFs at harvest.
- Users full walk (5,354): 13 Role=Supplier users exist with SupplierIDs FILLED (the always-null finding
  was a first-1000-pages artifact); field shape identical. Customers full walk (2,575): 12-field sparse
  shape confirmed at full scale.
- Mirror-convention alignment with distru_* tables: adopted `raw_payload` json (distru_batches precedent -
  fidelity backstop) + `last_seen_at` on every kss_* table. Importers log via existing
  `integration_import_jobs` (source='kss' fits, no schema change).
- Tables examined late and cleared: integration_import_jobs, leaflink_item_mappings (product-mapping
  precedent), distru_batches/distru_packages (conventions), retailer_onboardings (irrelevant -
  storefront), transporter_companies (not needed now), order_scanned_packages + transfer_logs (recon join
  sources for PalletTag matching, no schema impact).

## COA URL longevity - RESOLVED (live-tested)

cdn.e8.co COA links OUTLIVE the batch listing: 2024-era invoices' COAs (batches long vanished from
/inventory/batches) still serve PDFs (200, application/pdf, ~0.5MB). Store the URL; archiving PDFs is
optional robustness. Bonus: /invoiceCOAs works for OLD invoices, so batch->COA mapping is recoverable
historically; lab POTENCY fields exist only on /inventory/batches and remain harvest-or-lose.
