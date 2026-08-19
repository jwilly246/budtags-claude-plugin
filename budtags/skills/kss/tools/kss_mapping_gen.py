#!/usr/bin/env python3
"""Generate KSS-INTEGRATION-MAPPING.md.

Wire columns (fill, types, examples) are injected mechanically from
inventory/wire-inventory.json (live harvest 2026-08-19). The mapping columns
(status, parking spot, note) are authored. A bidirectional completeness check
asserts every live field has a mapping row and every mapping row matches a
live field (or a declared doc-only field).

Statuses:
  MAP     - parking spot exists in Budtags today
  NEW     - needs new schema (column/table/enum) -> Schema Plan section
  JOIN    - identity/join/scope/cursor key; drives resolution, or persisted
            only inside an external_ids JSON map
  NOUSE   - interesting but no Budtags use case yet -> full audit report
  BLOCKED - cannot verify live (hidden from Supplier key, empty test data,
            or endpoint broken)
"""
import json
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
INV = json.load(open(os.path.join(HERE, 'inventory', 'wire-inventory.json')))
OUT = '/Users/budtags/Desktop/budtags/KSS-INTEGRATION-MAPPING.md'

BP = 'business_partners'
ICM = 'integration_company_mappings'

# ---------------------------------------------------------------------------
# Authored mapping: endpoint -> field -> (status, parking spot, note)
# ---------------------------------------------------------------------------
M = OrderedDict()

M['states'] = {
    '_intro': ("Reference row for each state KSS operates in (test shows CA only). "
               "Order cut-off rules are KSS operational config, not Budtags data."),
    'StateAbbreviation': ('JOIN', 'org scope', 'Matches organizations.state for the CA org; used only to scope other calls (States filter).'),
    'StateName': ('NOUSE', '', 'Display name of the state; we already know it.'),
    'OrderCutOffTime': ('NOUSE', '', 'KSS order cut-off time (e.g. 2:30 PM). Only relevant if we ever automate order placement INTO KSS.'),
    'OrderCutOffDaysInAdvance': ('NOUSE', '', 'Same as above; KSS ordering logistics.'),
    'TimeZone': ('NOUSE', '', 'IANA timezone of the state ops; no consumer.'),
    'TimeUpdated': ('JOIN', 'sync cursor', 'Standard KSS updated stamp.'),
}

M['locations'] = {
    '_intro': ("KSS's own warehouses (test: Alameda LocationID 1, Van Nuys LocationID 3, DBA 'Kiva Sales & Service'). "
               "No license numbers exposed. Proposal: cache the LocationID->name map in integration_company_mappings.metadata "
               "on the KSS partner row so inventory/purchases rows can be labeled; no dedicated table for 2 rows."),
    'LocationID': ('JOIN', f'{ICM}.metadata (kss locations map)', 'Join key referenced by inventory, customers, purchases, vendors.'),
    'Location': ('MAP', f'{ICM}.metadata', 'Warehouse display name (Alameda / Van Nuys); cached in the KSS partner mapping metadata JSON.'),
    'DBA': ('NOUSE', '', "KSS's DBA ('Kiva Sales & Service'); static identity of the distributor."),
    'Address': ('NOUSE', '', 'Warehouse street address; no consumer (we do not ship to these via Budtags today - Distru handles the transfer leg).'),
    'Address2': ('NOUSE', '', 'Warehouse address line 2.'),
    'Address3': ('NOUSE', '', "Warehouse address line 3 (live shows 'N/A' filler)."),
    'City': ('NOUSE', '', 'Warehouse city.'),
    'State': ('JOIN', 'org scope', 'CA.'),
    'PostalCode': ('NOUSE', '', 'Warehouse zip.'),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['salesReps'] = {
    '_intro': ("KSS's sales reps (kivaconfections.com emails) with their retailer assignments. "
               "The one valuable output: which KSS rep covers which retailer -> business_partners.assigned_rep on that retailer's partner row."),
    'UserID': ('JOIN', 'external_ids', 'KSS user id of the rep.'),
    'Name': ('MAP', f'{BP}.assigned_rep', "Written onto each retailer partner named in Customers[] (varchar rep name column exists today)."),
    'Email': ('NOUSE', '', "Rep's KSS email; assigned_rep is a plain name column. Would need a contacts-level home to keep it."),
    'Type': ('NOUSE', '', "Rep type ('Territory Manager' / 'Supplier Rep'); qualifies the assignment but has no column."),
    'ProductGroups': ('JOIN', 'filter semantics', "Values like ['Supplier'] / ['KSS Pro'] / product-line names; drives which reps are Gelato-relevant (filter ProductGroups='Supplier'/'Cookies'-style lines)."),
    'Customers': ('JOIN', 'container', 'Array of retailer assignments; consumed via its sub-fields.'),
    'Customers[].CustomerID': ('JOIN', f'{ICM} lookup', 'Resolves to the retailer partner that receives assigned_rep.'),
    'Customers[].CustomerName': ('JOIN', 'resolution aid', 'Fallback name matching only.'),
    'Suppliers': ('JOIN', 'container', 'Array of supplier scopes (always Gelato/61 for our key).'),
    'Suppliers[].Supplier': ('JOIN', 'scope', 'Always Gelato for our key.'),
    'Suppliers[].SupplierID': ('JOIN', 'scope', 'Always 61 for our key.'),
}

M['users'] = {
    '_intro': ("KSS portal users. With our key everything visible is Role=Customer: real buyer/AP contacts AT the retailers "
               "(names, emails, job titles). That is CRM gold -> customer_contacts + business_partner_contacts link, source-tagged kss."),
    'UserID': ('JOIN', 'customer_contacts.external_ids', "KSS user id, stored under the 'kss' key of the contact's external_ids JSON."),
    'FullName': ('MAP', 'customer_contacts.first_name/last_name', 'Split on first whitespace; keep raw in external_data.'),
    'Email': ('MAP', 'customer_contacts.email', '12/1000 null live.'),
    'JobTitle': ('MAP', 'customer_contacts.role', "Buyer / GM / AP etc. 502/1000 null live."),
    'Department': ('MAP', 'customer_contacts.description', '997/1000 null live; append when present.'),
    'CustomerIDs': ('JOIN', 'business_partner_contacts', 'Links the contact to retailer partner(s) via the kss CustomerID mapping.'),
    'Role': ('JOIN', 'import filter', "Only Role=Customer visible to our key; import those as retailer contacts, skip others."),
    'UserActive': ('JOIN', 'import filter', 'Import active only by default (pass Active=true,false explicitly when auditing).'),
    'KSSLiveAccess': ('NOUSE', '', 'Whether the user has KSS Live portal access; KSS-internal permission.'),
    'PowerUser': ('NOUSE', '', 'KSS portal permission flag.'),
    'LocationIDs': ('NOUSE', '', 'Which KSS warehouses serve the user; derivable from the customer row.'),
    'SiteUserID': ('NOUSE', '', 'Second KSS-internal user id (site-level); no documented consumer.'),
    'States': ('JOIN', 'org scope', 'Always [CA] for this org.'),
    'SupplierIDs': ('BLOCKED', '', '1000/1000 null with our Supplier key; presumably populated for supplier-role users we cannot see.'),
}

M['suppliers'] = {
    '_intro': ("Exactly one row for our key: Gelato itself (SupplierID 61). This is our org's identity AT KSS -> org-level config, "
               "precedent organizations.leaflink_seller_company_id. See Schema Plan (kss_supplier_id)."),
    'SupplierID': ('NEW', 'organizations.kss_supplier_id (proposed)', 'Load-bearing scope id for every other call; must be stored org-level. Alternative: org ui_settings JSON, but a typed column follows the leaflink_seller_company_id precedent.'),
    'Supplier': ('JOIN', 'sanity check', "Assert it equals 'Gelato' on sync to catch key mixups."),
    'Active': ('JOIN', 'sanity check', 'Alert if our supplier account goes inactive.'),
    'State': ('JOIN', 'org scope', 'CA.'),
    'Description': ('NOUSE', '', 'Our own marketing copy as KSS displays it.'),
    'BrandAssetsURL': ('NOUSE', '', 'Null live; brandfolder-style asset link about ourselves.'),
    'SupplierWebsiteURL': ('NOUSE', '', 'Null live.'),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['suppliers_creditTerms'] = {
    '_intro': ("Credit-term catalog rows for supplier 61 (NET 7/14/30...). Pure reference; terms that matter arrive "
               "denormalized on purchases (Terms/TermID) and invoices (TermID)."),
    'SupplierID': ('JOIN', 'scope', 'Always 61.'),
    'TermID': ('JOIN', 'lookup key', 'Referenced by purchases.TermID / invoices.TermID; resolve to Term text at import time.'),
    'Term': ('JOIN', 'lookup value', "Term display text ('NET 14'); written into purchase_orders/marketplace context where those rows land."),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['vendors'] = {
    '_intro': ("Gelato's contract manufacturers as KSS sees them, WITH license numbers (e.g. 'Urban Therapies, LLC (Gelato)' C11-0001454-LIC). "
               "These are existing/known supplier partners -> partner resolution on license number, never a new bespoke copy."),
    'VendorID': ('JOIN', f'{ICM}', "integration_source='kss', integration_company_id='vendor:{VendorID}' on the resolved supplier partner."),
    'VendorName': ('MAP', f'{BP}.name', 'Via partner resolution (license first, then name); do not overwrite an existing partner name, resolution layer rules apply.'),
    'VendorLicenseNumber': ('MAP', f'{BP}.license_number', 'PRIMARY resolution key; C11 manufacturer licenses.'),
    'VendorAddress': ('MAP', f'{BP}.address', 'Only fill blanks on guarded writes (convergence-guard pattern).'),
    'VendorAddress2': ('MAP', f'{BP}.unit_number', '1/2 null live.'),
    'VendorCity': ('MAP', f'{BP}.city', ''),
    'VendorState': ('MAP', f'{BP}.state', ''),
    'VendorPostalCode': ('MAP', f'{BP}.zipcode', ''),
    'LeadTimeDays': ('MAP', f'{BP}.lead_time_days', 'Column exists (smallint); 21 in live sample.'),
    'Active': ('JOIN', 'import filter', 'Defaults to Active=true; only Employee keys may request inactive - our key cannot.'),
    'SupplierID': ('JOIN', 'scope', 'Always 61.'),
    'LocationID': ('JOIN', 'kss locations map', 'Destination KSS warehouse for this vendor relationship.'),
    'MaxDOI': ('NOUSE', '', "KSS's max days-of-inventory target for this vendor; KSS purchasing policy."),
    'TargetDOI': ('NOUSE', '', "KSS's target DOI; purchasing policy."),
    'PickupDates': ('NOUSE', '', 'Scheduled pickup dates from the vendor; KSS logistics (could matter if we ever schedule freight).'),
    'RequirePOBatchCodes': ('NOUSE', '', 'KSS receiving rule flag for the vendor.'),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['productCategories'] = {
    '_intro': ("KSS's category taxonomy (10 rows: Flower, Edibles/Ingestibles...). product_categories is a GLOBAL shared table with "
               "distru_category_id and leaflink_category_id columns; kss id needs the same treatment (Schema Plan) or a code-level name map."),
    'ProductCategoryID': ('NEW', 'product_categories.kss_category_id (proposed)', 'Follows distru/leaflink precedent. Cheaper alternative: static name map in the importer, no migration.'),
    'CategoryName': ('MAP', 'product_categories.name', 'Match/attach by name; taxonomy memory: storefront category taxonomy is curated, never auto-create.'),
    'Sequence': ('NOUSE', '', "KSS's menu ordering of categories."),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['products'] = {
    '_intro': ("Gelato's catalog as sold through KSS (778 live rows incl. discontinued). Parking = products table (marketplace product), "
               "keyed products.external_ids['kss'] = ProductID (no migration; distru/leaflink used dedicated columns, external_ids is the "
               "current pattern - decision noted in Schema Plan). SupplierProductNumber is OUR item number at KSS and is the natural "
               "resolution key to existing products, but test data holds 'N/A'/'0' garbage - resolution likely falls back to name matching."),
    'ProductID': ('JOIN', "products.external_ids['kss']", 'Primary KSS product key; referenced by inventory, batches, invoices, purchases, pricing.'),
    'ProductName': ('MAP', 'products.name', "Full name e.g. 'Gelato Last Bite 100mg Hybrid Birthday Cake 10pc'."),
    'BrandName': ('MAP', 'products.external_name', "KSS's display-name variant of the product."),
    'BrandFamily': ('MAP', 'product_lines.name -> products.product_line_id', "Line grouping ('Gelato Chocolate', 'Neon Habits Flower'); resolve-or-create product_line under the Gelato brand partner."),
    'BrandID': ('JOIN', 'product_lines (name-keyed)', 'KSS numeric id per BrandName variant; product_lines has no kss column - join by BrandFamily name, keep BrandID in external_data if needed.'),
    'BrandStyle': ('BLOCKED', '', 'Null in all 778 live rows; meaning unknown, cannot map.'),
    'Description': ('MAP', 'products.description', '2/778 null.'),
    'Ingredients': ('MAP', 'products.public_ingredients', '65/778 null.'),
    'Flavor': ('MAP', "product_specifications (spec_type='flavor')", "Variant descriptor ('hybrid purple aurora'); specifications table fits, text_value."),
    'Blend': ('MAP', 'products.strain_classification', 'Hybrid/Indica/Sativa maps onto the enum exactly.'),
    'StrainName': ('MAP', 'products.strain_name (+ strains resolve)', '625/778 null; resolve to strains row when present.'),
    'StrainID': ('JOIN', 'external_data', 'KSS strain id; no strains.kss column - keep alongside for round-trip.'),
    'KSSMenuCategory': ('MAP', 'products.product_category_id', 'Via productCategories name map.'),
    'KSSLiveCategoryID': ('JOIN', 'category lookup', 'Numeric twin of KSSMenuCategory.'),
    'ProductTypeName': ('MAP', 'products.product_subcategory_id (name map)', "'Flower: Full Oz', 'Edible: Chocolate' - finer than category; map to subcategories where names align, else external_data."),
    'ProductTypeID': ('JOIN', 'external_data', 'Numeric twin of ProductTypeName.'),
    'StatusID': ('MAP', 'products.listing_state / archived', 'Enum 0-5: 1 Active -> Available; 0 Discontinued -> Archived+archived=1; 2 Pre-order -> Backorder; 4 Unavailable -> Unavailable; 3 Manufacture / 5 Close Out -> decision at import (suggest Internal / Unavailable).'),
    'IsSample': ('MAP', "products.listing_state='Sample'", 'Boolean; sample SKUs exist in catalog.'),
    'UnitNetWeight': ('MAP', 'products.unit_weight + unit_weight_uom', "String '28g'/'80g' - parse number+uom."),
    'WholesaleUnitsPerCase': ('MAP', 'products.unit_multiplier', 'Units per wholesale case (4/8/10). VERIFY semantics against the LeafLink import convention (wholesale price is per CASE across all sources) before wiring.'),
    'PackageName': ('NOUSE', '', "KSS pack-config label ('4/28g Pouch') - redundant encoding of units-per-case + unit weight which arrive structured in other fields."),
    'PackageID': ('NOUSE', '', 'KSS pack-config id behind PackageName.'),
    'PotencyTHC': ('MAP', 'products.external_data', "Marketing potency string '32.87% THC' (186/778 null). NOT for labels (label potency = LAB results only, standing rule); real lab potency arrives per-batch on /inventory/batches."),
    'Potency': ('BLOCKED', '', 'Null in all 778 live rows.'),
    'ThumbnailImageURL': ('MAP', 'product_images.url', 'cdn.e8.co asset; import as non-primary image.'),
    'FullSizeImageURL': ('MAP', 'product_images.url (is_primary)', 'Primary image.'),
    'SupplierProductNumber': ('MAP', 'products.sku (resolution key)', "OUR item number at KSS; the natural join to existing products. Test data is 'N/A'/'0'/'NA' garbage (3 null) - confirm quality on prod before trusting as key."),
    'ProductGroupID': ('NOUSE', '', 'Constant 12 across all 778 live rows; opaque KSS grouping.'),
    'Supplier': ('JOIN', 'scope', 'Always Gelato.'),
    'SupplierID': ('JOIN', 'scope', 'Always 61.'),
    'State': ('JOIN', 'org scope', 'CA; multi-state selector context.'),
    'TimeUpdated': ('JOIN', 'sync cursor', 'Bulk-stamped on test (all rows same value) - do not assume per-row granularity.'),
}

M['customers'] = {
    '_intro': ("Retailers KSS sells Gelato to (1000+ live rows, incl. big names and Metrc C10 licenses). Parking = business_partners "
               "(is_customer) through the deployed partner-resolution layer, license-first; kss CustomerID recorded in "
               "integration_company_mappings. Convergence-guard rules apply (created_at preserved, guarded writes, no dup forks). "
               "10 documented fields never appear for our Supplier key (SalesRep*, OnHold, CollectionAgent*, DeliveryMinimum, "
               "NextDeliveryDates, ProfilePictureURL) - listed BLOCKED below."),
    'CustomerID': ('JOIN', f'{ICM}', "integration_source='kss', integration_company_id=CustomerID."),
    'CustomerName': ('MAP', f'{BP}.name', "Resolution fallback key; 'KSS Live Test Customer' etc. are test noise."),
    'CustomerNameAlt': ('MAP', f'{BP}.nickname', "457/1000 null; live shows '#N/A' filler - sanitize."),
    'ChainName': ('MAP', f'{BP}.group_name', "615/1000 null; chain grouping ('Eaze', 'Erba')."),
    'LicenseNum': ('MAP', f'{BP}.license_number', "PRIMARY resolution key (C10 retail licenses). 140/1000 null + 'LIC-99999-FAKE' test rows - importer must tolerate missing/garbage licenses (Zippys placeholder-license precedent)."),
    'Address': ('MAP', f'{BP}.address/city/state/zipcode', "SINGLE comma-joined string ('123 Main St, Los Angeles, CA 90001') - needs a parser; keep raw copy in external_data."),
    'AccountStatus': ('MAP', f'{BP}.status', "Active -> active, Inactive -> inactive, OutOfBus -> churned. NEVER delete partners (standing rule) - status flips only."),
    'LocationID': ('JOIN', 'kss locations map', 'Which KSS warehouse serves this retailer.'),
    'State': ('MAP', f'{BP}.state', 'CA.'),
    'DeliveryDays': ('NOUSE', '', 'KSS delivery weekday (1=Mon..7=Sun); KSS routing logistics. 448/1000 null.'),
    'DeliveryDates': ('NOUSE', '', 'Next 4 concrete KSS delivery dates; same logistics data. 519/1000 null.'),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
    # Doc-only fields, hidden from our Supplier key:
    'OnHold': ('BLOCKED', f'{BP}.delinquent (candidate)', 'Doc-only for our key. Credit-hold flag; would map to delinquent if an Employee/prod key exposes it.'),
    'SalesRepName': ('BLOCKED', f'{BP}.assigned_rep (candidate)', 'Hidden from Supplier keys; /salesReps endpoint supplies the same assignment and is our actual source.'),
    'SalesRepEmail': ('BLOCKED', '', 'Hidden from Supplier keys.'),
    'SalesRepPhone': ('BLOCKED', '', 'Hidden from Supplier keys.'),
    'SalesRepUserID': ('BLOCKED', '', 'Hidden from Supplier keys.'),
    'ProfilePictureURL': ('BLOCKED', '', 'Hidden from Supplier keys; rep avatar, would be NOUSE anyway.'),
    'CollectionAgentFullName': ('BLOCKED', '', "Hidden from Supplier keys; KSS collections ops, would be NOUSE."),
    'CollectionAgentEmail': ('BLOCKED', '', 'Hidden from Supplier keys; would be NOUSE.'),
    'NextDeliveryDates': ('BLOCKED', '', 'Hidden from Supplier keys; semicolon-joined twin of DeliveryDates, would be NOUSE.'),
    'DeliveryMinimum': ('BLOCKED', '', 'Hidden from Supplier keys; KSS order minimum for the retailer (500 in doc example). Possible future pricing-intel interest.'),
}

M['deliveryDays'] = {
    '_intro': "Per-retailer KSS delivery schedule; pure KSS routing logistics, fully redundant with fields already on /customers.",
    'CustomerID': ('JOIN', f'{ICM}', ''),
    'DeliveryDays': ('NOUSE', '', 'Weekday 1=Mon..7=Sun (per docs callout).'),
    'DeliveryDates': ('NOUSE', '', 'Next concrete delivery dates.'),
}

M['allocations'] = {
    '_intro': ("EMPTY on the test DB (0 rows) - all mappings provisional from doc examples. Allocations reserve product units for "
               "specific retailers; inventory.NotAuthorized flags fully-allocated products. Unique key per docs callout: "
               "[Allocation, ProductID, CustomerID]. Revisit with prod data; if Gelato runs allocations, this feeds availability logic."),
    'AllocationID': ('BLOCKED', '', 'Doc-only until prod data exists.'),
    'ProductID': ('BLOCKED', "products.external_ids['kss'] (candidate)", ''),
    'CustomerID': ('BLOCKED', f'{ICM} (candidate)', ''),
    'Units': ('BLOCKED', '', 'Reserved unit count.'),
    'AllocationTypeID': ('BLOCKED', '', 'Undocumented enum.'),
    'StartDate': ('BLOCKED', '', ''),
    'EndDate': ('BLOCKED', '', ''),
    'TimeUpdated': ('BLOCKED', '', ''),
}

M['arAging'] = {
    '_intro': ("KSS's accounts-receivable aging against retailers (KSS is the creditor, not Gelato). Recalculated once daily per docs. "
               "No Budtags home today; possible future use is credit-exposure context before running promos with a struggling retailer. "
               "Whole endpoint parked NOUSE for your audit."),
    'ARAccountID': ('NOUSE', '', "KSS AR account id (retailer-side ledger key; note: NOT CustomerID)."),
    'SupplierID': ('JOIN', 'scope', 'Always 61.'),
    'TotalBalanceOutstanding': ('NOUSE', '', 'Retailer total owed to KSS (string decimal).'),
    'CurrentDue': ('NOUSE', '', 'Not-yet-aged balance.'),
    'Due_1_30': ('NOUSE', '', 'Aged 1-30 days bucket.'),
    'Due_31_60': ('NOUSE', '', 'Aged 31-60 bucket.'),
    'Due_61_90': ('NOUSE', '', 'Aged 61-90 bucket.'),
    'Due_91': ('NOUSE', '', 'Aged 91+ bucket.'),
    'OpenCredit': ('NOUSE', '', 'Unapplied credit on the account.'),
    'CloseDate': ('NOUSE', '', '18/358 null.'),
    'StatementDate': ('NOUSE', '', '18/358 null.'),
    'CurrentInvoices': ('NOUSE', '', 'Invoice refs behind CurrentDue (array).'),
    'CurrentInvoices[].InvoiceID': ('NOUSE', '', ''),
    'CurrentInvoices[].InvoiceNum': ('NOUSE', '', "'X-' prefixed invoice numbers."),
    'CurrentInvoices[].OpenBalance': ('NOUSE', '', ''),
    'Invoices_1_30': ('NOUSE', '', 'Invoice refs behind Due_1_30.'),
    'Invoices_1_30[].InvoiceID': ('NOUSE', '', ''),
    'Invoices_1_30[].InvoiceNum': ('NOUSE', '', ''),
    'Invoices_1_30[].OpenBalance': ('NOUSE', '', ''),
    'Invoices_31_60': ('NOUSE', '', ''),
    'Invoices_31_60[].InvoiceID': ('NOUSE', '', ''),
    'Invoices_31_60[].InvoiceNum': ('NOUSE', '', ''),
    'Invoices_31_60[].OpenBalance': ('NOUSE', '', ''),
    'Invoices_61_90': ('NOUSE', '', ''),
    'Invoices_61_90[].InvoiceID': ('NOUSE', '', ''),
    'Invoices_61_90[].InvoiceNum': ('NOUSE', '', ''),
    'Invoices_61_90[].OpenBalance': ('NOUSE', '', ''),
    'Invoices_91': ('NOUSE', '', ''),
    'Invoices_91[].InvoiceID': ('NOUSE', '', ''),
    'Invoices_91[].InvoiceNum': ('NOUSE', '', ''),
    'Invoices_91[].OpenBalance': ('NOUSE', '', ''),
    'CreditInvoices': ('NOUSE', '', 'Credit-memo invoice refs (X- numbers, negative paper).'),
    'CreditInvoices[].InvoiceID': ('NOUSE', '', ''),
    'CreditInvoices[].InvoiceNum': ('NOUSE', '', ''),
    'CreditInvoices[].OpenBalance': ('NOUSE', '', ''),
    'TimeCreated': ('NOUSE', '', 'Daily recalc stamp.'),
    'TimeUpdated': ('JOIN', 'sync cursor', 'Daily recalc stamp.'),
}

M['inventory'] = {
    '_intro': ("KSS warehouse stock of OUR products by warehouse (484 live rows), with FIFO layer pointer and velocity. No native home: "
               "products.quantity is our own listing stock, not distributor stock. DECISION: proposed kss_inventory_snapshots table "
               "(Schema Plan) - the use case is production planning / DOI visibility. Negative Inventory values appear live (-134, -7025): "
               "per the docs' field definitions Inventory is a derived sum, so negatives are KSS data artifacts to tolerate."),
    'ProductID': ('JOIN', "products.external_ids['kss']", ''),
    'LocationID': ('JOIN', 'kss locations map', 'Alameda vs Van Nuys stock.'),
    'Inventory': ('NEW', 'kss_inventory_snapshots.inventory', 'Total owned (derived sum; can be negative in live data).'),
    'OnFloorInventory': ('NEW', 'kss_inventory_snapshots.on_floor', 'Sellable warehouse stock.'),
    'AvailableUnits': ('NEW', 'kss_inventory_snapshots.available_units', 'On floor minus presales/allocated - the number that matters. NUMBER type (not string) unlike siblings.'),
    'PreSales': ('NEW', 'kss_inventory_snapshots.pre_sales', 'On future-dated orders.'),
    'Allocated': ('NEW', 'kss_inventory_snapshots.allocated', 'Reserved via allocations.'),
    'Picked': ('NEW', 'kss_inventory_snapshots.picked', ''),
    'Loaded': ('NEW', 'kss_inventory_snapshots.loaded', 'On trucks.'),
    'Delivered': ('NEW', 'kss_inventory_snapshots.delivered', 'Delivered, still on open load sheets.'),
    'Received': ('NEW', 'kss_inventory_snapshots.received', 'Received, not yet shelved.'),
    'Unsellable': ('NEW', 'kss_inventory_snapshots.unsellable', 'Damaged/expired/hold stock - early warning on our product.'),
    'DOI': ('NEW', 'kss_inventory_snapshots.days_of_inventory', 'String decimal. Undocumented in the Field Definitions table.'),
    'AvgDailySales90d': ('NEW', 'kss_inventory_snapshots.avg_daily_sales_90d', 'String decimal; undocumented in Field Definitions.'),
    'NotAuthorized': ('NEW', 'kss_inventory_snapshots.not_authorized', 'True = fully allocated to specific accounts (see /allocations).'),
    'PurchaseTransID': ('JOIN', 'purchaseTrans link', 'Current FIFO cost layer being sold - joins to /purchaseTrans for the live COGS layer.'),
    'TimeUpdated': ('JOIN', 'sync cursor', 'Near-real-time stamp observed.'),
}

M['inventory_batches'] = {
    '_intro': ("THE Metrc bridge (1000+ live rows): per-batch stock with UID = Metrc package tag (1A406030...) plus full lab data and COA URL. "
               "Parking: product_batches (batch_number=BatchCode, potency decimals, expiration, external_ids['kss'], testing_source) "
               "+ product_batch_links to the product + batch_documents for the COA + metrc_package_local_metadata "
               "(tag -> BatchCode, source='kss') for the Metrc join. This endpoint alone links KSS commerce to our entire native package/COA world."),
    'BatchCode': ('MAP', 'product_batches.batch_number + metrc_package_local_metadata.local_production_batch_number', "Gelato batch codes (BULK-480, GC-2842)."),
    'UID': ('MAP', 'metrc_package_local_metadata.metrc_package_tag', "METRC PACKAGE TAG - hard join to native packages. 6/1000 null."),
    'ProductID': ('JOIN', "products.external_ids['kss'] -> product_batch_links", ''),
    'THCPotency': ('MAP', 'product_batches.total_thc', 'String decimal %, e.g. 25.0787.'),
    'CBDPotency': ('MAP', 'product_batches.cbd', 'String decimal %.'),
    'TotalCannabinoids': ('MAP', 'product_batches.total_cannabinoids', ''),
    'PotencyType': ('MAP', 'product_batches.cannabinoid_unit', "'Percentage' -> unit %."),
    'LabelTHCPotency': ('NOUSE', '', 'Potency as printed on the physical label (rounded). Our labels derive from LAB COA data (standing rule); keeping the printed-label historical value has no consumer yet. Cross-check candidate against our COA extraction.'),
    'LabelCBDPotency': ('NOUSE', '', 'Printed-label CBD; same reasoning.'),
    'LabelTotalCannabinoids': ('NOUSE', '', 'Printed-label total; same reasoning.'),
    'Laboratory': ('MAP', 'product_batches.testing_source', "Lab name; live data mixes names ('Excelbis Labs') and license numbers ('C8-0000133-LIC') - normalize."),
    'COAURL': ('MAP', 'batch_documents.file_url (document_type=coa)', 'cdn.e8.co PDF; candidate input to the COA-extraction pipeline later (separate project).'),
    'COAExpirationDate': ('NOUSE', '', 'COA validity end; we track batch expiration instead.'),
    'ExpirationDate': ('MAP', 'product_batches.expiration_date', '0 null live.'),
    'PackDate': ('MAP', 'product_batches.batch_date', '6/1000 null.'),
    'BestByDate': ('BLOCKED', '', 'Null in all 1000 live rows.'),
    'HarvestDate': ('BLOCKED', '', 'Null in all 1000 live rows.'),
    'ManufactureDate': ('BLOCKED', '', 'Null in all 1000 live rows.'),
    'Vintage': ('BLOCKED', '', 'Null in all 1000 live rows.'),
    'InventoryUnits': ('NEW', 'kss_inventory_snapshots (batch grain, optional)', 'Units on hand for THIS batch - finer grain than /inventory; include if the snapshot table gets a batch dimension, else NOUSE.'),
    'PurchaseTransID': ('JOIN', 'purchaseTrans link', 'Receipt line that brought the batch in - cost linkage.'),
    'LocationID': ('JOIN', 'kss locations map', ''),
    'State': ('JOIN', 'org scope', ''),
    'SupplierID': ('JOIN', 'scope', ''),
    'TimeCreated': ('JOIN', 'record stamp', ''),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['retailerInventory'] = {
    '_intro': ("Per-retailer on-hand + velocity of OUR products as KSS tracks it (1000+ rows). Seller-side sell-through intel: powers promo "
               "verification and reorder conversations. Nearest natives are buyer_item_sell_through / customer_inventory_snapshots, but both "
               "are Metrc-derived with different grain. DECISION: proposed kss_retailer_inventory table (Schema Plan) vs extending "
               "customer_inventory_snapshots with a source column. Sentinel date 2000-01-01 appears in LastInventoryDate."),
    'ID': ('JOIN', 'row id', 'KSS row id (upsert key).'),
    'CustomerID': ('JOIN', f'{ICM}', ''),
    'ProductID': ('JOIN', "products.external_ids['kss']", ''),
    'Inventory': ('NEW', 'kss_retailer_inventory.on_hand', 'String decimal.'),
    'DailySales': ('NEW', 'kss_retailer_inventory.daily_sales', 'String decimal velocity.'),
    'LastInventoryDate': ('NEW', 'kss_retailer_inventory.last_inventory_date', "2000-01-01 sentinel = never counted; treat as null."),
    'TimeCreated': ('JOIN', 'record stamp', ''),
    'TimeUpdated': ('JOIN', 'sync cursor', 'Stale stamps live (2025 dates) - data is only as fresh as retailer reporting.'),
}

M['invoices'] = {
    '_intro': ("KSS's sales invoices TO retailers - i.e. depletions of Gelato product (1000+ live rows). Gelato is not a party to these "
               "invoices (KSS is seller of record), so they must NOT land in marketplace_orders/marketplace_invoices. DECISION: proposed "
               "kss_invoices + kss_invoice_lines depletion mirror (Schema Plan) powering sell-through, promo verification, and the "
               "SupplierCredit trail. Statuses are numeric (1 New..7 Verified; silent default returns ONLY status 1 - importer must pass "
               "Statuses=1,2,3,4,5,7 explicitly)."),
    'InvoiceID': ('NEW', 'kss_invoices.kss_invoice_id', 'Upsert key.'),
    'InvoiceNum': ('NEW', 'kss_invoices.invoice_num', "'X-843083' style."),
    'CustomerID': ('NEW', 'kss_invoices.business_partner_id (via ICM)', 'Resolved retailer partner.'),
    'CustomerName': ('JOIN', 'resolution aid', 'Denormalized name.'),
    'Status': ('NEW', 'kss_invoices.status', 'Numeric enum 1,2,3,4,5,7 (no 6 documented).'),
    'Date': ('NEW', 'kss_invoices.invoice_date', 'Future-dated invoices appear (scheduled delivery).'),
    'DueDate': ('NEW', 'kss_invoices.due_date', ''),
    'InvoiceTotal': ('NEW', 'kss_invoices.total', 'String decimal.'),
    'TotalExtPrice': ('NEW', 'kss_invoices.subtotal', 'Extended (post-discount) product total.'),
    'TotalFullPrice': ('NEW', 'kss_invoices.full_price_total', 'Pre-discount total.'),
    'TotalDiscount': ('NEW', 'kss_invoices.discount_total', 'Promo spend visibility per invoice.'),
    'TotalNumUnits': ('NEW', 'kss_invoices.total_units', 'Depletion volume.'),
    'TotalCases': ('NEW', 'kss_invoices.total_cases', 'Fractional cases appear (4.8).'),
    'OpenBalance': ('NOUSE', '', "KSS's AR balance on the invoice; collections is KSS's business."),
    'OpenDebit': ('NOUSE', '', 'AR mechanics.'),
    'OpenCredit': ('NOUSE', '', 'AR mechanics.'),
    'ARNote': ('NOUSE', '', 'KSS collections annotations (931/1000 null).'),
    'TermID': ('NOUSE', '', 'Retailer credit term with KSS.'),
    'PONum': ('NEW', 'kss_invoices.retailer_po_num', "Retailer's PO reference (774/1000 null); useful when a retailer disputes."),
    'PODate': ('BLOCKED', '', 'Null in all 1000 live rows.'),
    'Memo': ('NOUSE', '', "Order-submission note ('Order Submitted by ...'); attribution noise. 25/1000 null."),
    'BuiltByUserID': ('NOUSE', '', 'KSS/portal user who built the order.'),
    'BuiltByUserName': ('NOUSE', '', ''),
    'BuiltByUserEmail': ('NOUSE', '', 'Note: retailer buyer emails appear here - /users already provides contacts.'),
    'SubmittedByUserID': ('NOUSE', '', ''),
    'SubmittedByUserName': ('NOUSE', '', ''),
    'SubmittedByUserEmail': ('NOUSE', '', ''),
    'PDFURL': ('NOUSE', '', 'encompass8.com API link WITH embedded APIKeyID (904/1000 null) - treat as sensitive, do not persist third-party keyed URLs.'),
    'InvoiceTimeCreated': ('NEW', 'kss_invoices.kss_created_at', ''),
    'InvoiceLastUpdated': ('JOIN', 'sync cursor', "Named differently from every other endpoint's TimeUpdated - watch the name."),
}

M['invoiceTransactions'] = {
    '_intro': ("Invoice line items (requires InvoiceIDs param; silently drops Verified invoices unless Statuses includes 7). "
               "Lines carry BatchCode - depletions at BATCH grain, which chains through /inventory/batches.UID to Metrc tags. "
               "Parking: kss_invoice_lines (same DECISION as kss_invoices)."),
    'InvoiceTransID': ('NEW', 'kss_invoice_lines.kss_trans_id', 'Upsert key.'),
    'InvoiceID': ('NEW', 'kss_invoice_lines.kss_invoice_id', 'Parent.'),
    'CustomerID': ('JOIN', 'denormalized parent', ''),
    'SupplierID': ('JOIN', 'scope', ''),
    'ProductID': ('NEW', 'kss_invoice_lines.product_id (via external_ids)', ''),
    'ProductName': ('JOIN', 'resolution aid', 'Denormalized.'),
    'BatchCode': ('NEW', 'kss_invoice_lines.batch_code', 'Joins to product_batches/Metrc via /inventory/batches. 48/500 null.'),
    'COA_URL': ('JOIN', 'covered by /inventory/batches.COAURL', 'Same COA PDF, denormalized per line.'),
    'NumUnits': ('NEW', 'kss_invoice_lines.units', 'Eaches.'),
    'Cases': ('NEW', 'kss_invoice_lines.cases', 'String decimal; case/unit semantics per LL convention (qty=eaches).'),
    'Ordered': ('NEW', 'kss_invoice_lines.ordered_units', 'Ordered vs shipped delta = fill rate.'),
    'BackOrder': ('NEW', 'kss_invoice_lines.backorder_units', 'Unfilled demand for OUR product - reorder signal.'),
    'UnitPrice': ('NEW', 'kss_invoice_lines.unit_price', 'String decimal; KSS sell price per unit.'),
    'FullPrice': ('NEW', 'kss_invoice_lines.full_price', 'Pre-discount unit price.'),
    'Discount': ('NEW', 'kss_invoice_lines.discount', 'Per-unit promo discount.'),
    'ExtPrice': ('NEW', 'kss_invoice_lines.ext_price', 'Line total.'),
    'PromotionID': ('NEW', 'kss_invoice_lines.kss_promotion_id', 'Links depletion lines to promos - the promo-verification join.'),
    'TimeCreated': ('JOIN', 'record stamp', ''),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['invoiceCOAs'] = {
    '_intro': ("COA PDF per invoice line (requires InvoiceIDs). Strict subset of /invoiceTransactions (BatchCode+COA_URL) - "
               "redundant once lines are imported; the batch-level COA from /inventory/batches is the canonical copy."),
    'InvoiceID': ('JOIN', 'redundant with invoiceTransactions', ''),
    'InvoiceTransID': ('JOIN', 'redundant', ''),
    'ProductID': ('JOIN', 'redundant', ''),
    'BatchCode': ('JOIN', 'redundant', 'Same as line BatchCode.'),
    'COA_URL': ('JOIN', 'redundant', 'Same PDF as /inventory/batches.COAURL.'),
    'TimeCreated': ('JOIN', '', ''),
    'TimeUpdated': ('JOIN', '', ''),
}

M['invoices_creditTerms'] = {
    '_intro': "Credit-term catalog as used on retailer invoices (41 rows). Reference only; KSS's AR domain.",
    'TermID': ('JOIN', 'lookup key', ''),
    'Term': ('JOIN', 'lookup value', "'Upon Receipt', 'NET 14'..."),
    'DaysOfCredit': ('NOUSE', '', 'Numeric days behind the term.'),
    'AccountOnHold': ('NOUSE', '', 'Odd placement: a hold flag on a term row; KSS AR mechanics.'),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['customers_creditTerms'] = {
    '_intro': ("EMPTY on the test DB (0 rows) - mappings provisional from doc example. Per-customer-per-supplier negotiated terms; "
               "KSS's AR domain, expect NOUSE once verifiable."),
    'CustomerID': ('BLOCKED', '', 'Doc-only until data exists.'),
    'SupplierID': ('BLOCKED', '', ''),
    'TermID': ('BLOCKED', '', ''),
    'Term': ('BLOCKED', '', ''),
    'TimeUpdated': ('BLOCKED', '', ''),
}

M['customerPricing'] = {
    '_intro': ("Effective per-retailer price of each Gelato product (requires CustomerIDs; promo overlay included via PromotionID). "
               "This is KSS->retailer street pricing - price intelligence, not our price book (retailer-pricing scope rule: only the "
               "MARKETPLACE tab is ours). Parked NOUSE for your audit; would become a snapshot table if we decide to track street pricing."),
    'CustomerID': ('JOIN', f'{ICM}', ''),
    'ProductID': ('JOIN', "products.external_ids['kss']", ''),
    'UnitPrice': ('NOUSE', '', 'Effective sell price to this retailer today (string decimal; one live value shows 2dp vs 6dp formatting drift).'),
    'FullPrice': ('NOUSE', '', 'List price before promo.'),
    'Discount': ('NOUSE', '', 'Active promo discount amount.'),
    'PromotionID': ('NOUSE', '', 'Which promo produces the discount (439/500 null = no promo).'),
    'StartDate': ('NOUSE', '', 'Promo window start (null when no promo).'),
    'EndDate': ('NOUSE', '', "Promo window end; sentinel 3000-12-31 for open-ended."),
    'TimeUpdated': ('JOIN', 'sync cursor', '439/500 null - only promo rows carry it.'),
}

M['menuPromotions'] = {
    '_intro': ("Promotions Gelato runs through KSS (2 live rows, free-text description e.g. 'Buy 4 cases, get 2 for 1 penny'). "
               "Natural counterpart is promo_deals, but promo_deals has no external linkage column (Schema Plan) and KSS promos are "
               "unstructured text. DECISION: link-by-reference for promo verification vs NOUSE."),
    'MenuPromotionID': ('NEW', 'promo_deals.external_ids (proposed column)', 'Or a kss_promotion_id column; needed only if we link promos for verification.'),
    'Description': ('NEW', 'promo_deals.description (reference copy)', 'Free text terms of the deal.'),
    'StartDate': ('NEW', 'promo_deals.start_date', ''),
    'EndDate': ('NEW', 'promo_deals.end_date', ''),
    'State': ('JOIN', 'org scope', ''),
    'SupplierID': ('JOIN', 'scope', ''),
    'TimeCreated': ('JOIN', 'record stamp', ''),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['promotionsProducts'] = {
    '_intro': ("BROKEN on test: HTTP 500 on every attempt (reported below; needs a KSS support ticket with X-Request-Id). "
               "All mappings provisional from doc example. Structured promo definitions (product lists, override prices) - "
               "the machine-readable half of menuPromotions."),
    'PromotionID': ('BLOCKED', 'promo link (candidate)', 'Matches invoiceTransactions.PromotionID - the verification join, once the endpoint works.'),
    'PromotionTypeID': ('BLOCKED', '', 'Undocumented enum.'),
    'PromotionName': ('BLOCKED', '', ''),
    'ProductOverrideType': ('BLOCKED', '', "'none' in doc example; undocumented enum."),
    'UnitPrice': ('BLOCKED', '', 'Promo price; doc example shows a NUMBER (15.5) unlike the string decimals elsewhere.'),
    'StartDate': ('BLOCKED', '', ''),
    'EndDate': ('BLOCKED', '', ''),
    'AllProducts': ('BLOCKED', '', ''),
    'ProductIDs': ('BLOCKED', '', 'Product list for the promo.'),
    'States': ('BLOCKED', '', ''),
    'TimeUpdated': ('BLOCKED', '', ''),
}

M['payments_types'] = {
    '_intro': "KSS payment-method catalog (NorCal Cash/Check/EFT...). KSS AR reference data.",
    'PaymentTypeID': ('JOIN', 'lookup key', "Note: /payments rows show an undocumented sentinel -1 = SupplierCredit."),
    'Name': ('JOIN', 'lookup value', ''),
    'SupplierID': ('JOIN', 'scope', '1/7 null (shared types).'),
    'TimeCreated': ('JOIN', '', ''),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['payments'] = {
    '_intro': ("Retailer payments into KSS AR - except our key's live sample is 100% PaymentTypeID=-1 'SupplierCredit' rows: "
               "credit memos funded by Gelato (memos read 'Credit Submitted by Yolanda Gelato'). That slice IS our business - it is the "
               "money Gelato grants against retailer invoices (promo credits, spoils). DECISION: ingest SupplierCredit rows for "
               "reconciliation against promo_deals/seller_credits; ordinary retailer payments (invisible or irrelevant to us) stay NOUSE."),
    'PaymentID': ('NEW', 'kss credit ingest (upsert key)', 'Only for SupplierCredit rows if the DECISION lands yes.'),
    'PaymentTypeID': ('JOIN', 'filter', '-1 sentinel = SupplierCredit (undocumented); filter on it.'),
    'PaymentTypeName': ('JOIN', 'filter', "'SupplierCredit' in all 1000 live rows for our key."),
    'Amount': ('NEW', 'credit amount', 'String decimal.'),
    'AvailableAmount': ('NOUSE', '', 'Unapplied remainder (KSS AR mechanics).'),
    'AvailableBalance': ('NOUSE', '', 'Duplicate of AvailableAmount in all live rows.'),
    'ARAccountID': ('NOUSE', '', 'KSS AR ledger key.'),
    'PaymentInvoiceID': ('NEW', 'credit memo invoice ref', 'Credit memos are themselves X- invoices.'),
    'PaymentInvoiceNum': ('NEW', 'credit memo number', ''),
    'Memo': ('NEW', 'credit reason text', "Free text carries submitter + reason ('Credit Submitted by ...')."),
    'ARNote': ('NOUSE', '', 'KSS collections annotation (993/1000 null).'),
    'LoadSheetStatusID': ('NOUSE', '', 'Undocumented KSS logistics status on the payment row.'),
    'PostDate': ('NEW', 'credit post date', ''),
    'SupplierID': ('JOIN', 'scope', ''),
    'TimeCreated': ('JOIN', 'record stamp', ''),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['payments_openInvoices'] = {
    '_intro': "Open retailer invoices from the AR perspective (what a retailer still owes KSS). KSS collections domain; redundant with /invoices totals for our purposes.",
    'InvoiceID': ('NOUSE', '', ''),
    'InvoiceNum': ('NOUSE', '', ''),
    'CustomerID': ('JOIN', f'{ICM}', ''),
    'ARAccountID': ('NOUSE', '', ''),
    'InvoiceTotal': ('NOUSE', '', ''),
    'OpenBalance': ('NOUSE', '', ''),
    'Date': ('NOUSE', '', ''),
    'DueDate': ('NOUSE', '', ''),
    'PONum': ('NOUSE', '', "Free-text PO/attribution ('Jesse Logue / SoCal'). 672/1000 null."),
    'TermID': ('NOUSE', '', ''),
    'CreditTermID': ('NOUSE', '', 'Duplicate of TermID in all live rows.'),
}

M['payments_applications'] = {
    '_intro': ("Ledger of payment->invoice allocations (how credits/payments got applied). Useful only if the SupplierCredit ingest "
               "DECISION lands yes - then it shows WHERE Gelato-funded credits were applied. Otherwise KSS AR mechanics. "
               "RequestID/TimeRequested/TimeExported all null live = none of these came through the API request flow."),
    'PaymentApplicationID': ('NOUSE', '', 'Upsert key if credit-application tracking lands.'),
    'PaymentInvoiceNum': ('NOUSE', '', 'Source credit/payment memo number.'),
    'TargetInvoiceNum': ('NOUSE', '', 'Invoice the money was applied to.'),
    'ARAccountID': ('NOUSE', '', ''),
    'Amount': ('NOUSE', '', 'String decimal.'),
    'Status': ('NOUSE', '', 'Pending/Exported/Confirmed/Rejected lifecycle (all Confirmed live).'),
    'AppliedBy': ('NOUSE', '', 'KSS clerk name, concatenated without spaces live (AlinePerez).'),
    'TimeApplied': ('NOUSE', '', ''),
    'RequestID': ('BLOCKED', '', 'Null in all 1000 live rows (populated only for API-requested allocations).'),
    'RequestedByUserID': ('BLOCKED', '', 'Null in all live rows.'),
    'TimeRequested': ('BLOCKED', '', 'Null in all live rows.'),
    'TimeExported': ('BLOCKED', '', 'Null in all live rows.'),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['payments_applications_POST'] = {
    '_intro': ("The API's ONLY write: request a payment allocation (queued Pending, exported to Encompass async). "
               "403 for Supplier keys - unusable with our key, and requesting allocations is retailer/AR business anyway."),
    'PaymentInvoiceNum': ('BLOCKED', '', 'Write param; 403 for our key type.'),
    'TargetInvoiceNum': ('BLOCKED', '', 'Write param.'),
    'ARAccountID': ('BLOCKED', '', 'Write param.'),
    'Amount': ('BLOCKED', '', 'Write param.'),
}

M['purchases'] = {
    '_intro': ("KSS's purchase orders FROM Gelato's manufacturers (219 live rows; vendors are 'Urban Therapies, LLC (Gelato)' etc.) - "
               "the KSS-side mirror of OUR outbound sales/transfers to Kiva. The CA org's actual sales to KSS already land as "
               "marketplace_orders via Distru; this endpoint provides independent reconciliation (receive dates, KSS-side totals, and "
               "via /purchaseTrans the Metrc pallet tags). DECISION: reconciliation-report-only vs stamping matched marketplace_orders "
               "(external_ids['kss_purchase'], received confirmation). Negative totals appear live (returns/corrections)."),
    'PurchaseID': ('NEW', "marketplace_orders.external_ids['kss_purchase'] (on match)", 'Match via PalletTag -> our package tags -> order; unmatched purchases go to the reconciliation report.'),
    'PONum': ('MAP', 'match aid', "'Gelato PO 105160' - often contains our order reference."),
    'Status': ('NEW', 'reconciliation status', 'New/Accepted/Received/Confirmed/Verified; Received = KSS acknowledged our delivery.'),
    'ReceiveDate': ('NEW', 'reconciliation: received-at', "KSS's receive date vs our transfer date."),
    'PostDate': ('NEW', 'reconciliation date', '18/219 null.'),
    'InvoiceDate': ('NOUSE', '', "Vendor invoice date KSS recorded."),
    'DueDate': ('NOUSE', '', 'When KSS owes payment to the vendor (their AP).'),
    'Terms': ('NOUSE', '', "Payment terms incl. 'Interco Transfer' (intra-Kiva moves - filter these out of revenue reconciliation)."),
    'TermID': ('NOUSE', '', ''),
    'Total': ('NEW', 'reconciliation total', 'What KSS records paying - compare to our order total (penny-pricing tolling precedent). Negative values = returns/corrections.'),
    'TotalCases': ('NEW', 'reconciliation cases', 'Negative allowed.'),
    'Freight': ('NOUSE', '', '0.00 in all live rows.'),
    'Tax': ('NOUSE', '', '0.00 in all live rows.'),
    'OtherCost': ('NOUSE', '', '0.00 in all live rows.'),
    'VendorID': ('JOIN', f'{ICM} (vendor mapping)', 'Which Gelato manufacturer shipped.'),
    'VendorName': ('JOIN', 'resolution aid', ''),
    'ToLocationID': ('JOIN', 'kss locations map', 'Receiving warehouse.'),
    'ToLocationName': ('JOIN', 'display', ''),
    'ShipmentID': ('NOUSE', '', 'KSS shipment grouping id.'),
    'ShipmentNum': ('NOUSE', '', 'Usually mirrors PONum. 11/219 null.'),
    'ReceivingNum': ('BLOCKED', '', 'Null in all 219 live rows; undocumented field.'),
    'Memo': ('NOUSE', '', "Ops notes ('sku correction', 'Convert $ products to xT'). 187/219 null."),
    'PublicPDFLink': ('NOUSE', '', 'encompass8.com link with embedded APIKeyID - sensitive, do not persist. 10/219 null.'),
    'PurchasePDFURLAPIKeyID': ('NOUSE', '', 'The embedded key id for the PDF link; undocumented field.'),
    'PurchaseGlobalID': ('BLOCKED', '', 'Undocumented ULID, 214/219 null; purpose unknown.'),
    'PurchaseGlobalIDExportedAt': ('BLOCKED', '', 'Undocumented, 217/219 null.'),
    'LastEditTime': ('BLOCKED', '', 'Null in all 219 live rows despite the name.'),
    'LastCalcTime': ('NOUSE', '', 'KSS recost stamp.'),
    'TimeCreated': ('JOIN', 'record stamp', ''),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

M['purchaseTrans'] = {
    '_intro': ("Purchase line items (requires PurchaseIDs) - the reconciliation goldmine: PalletTag = METRC TAG of the pallet we shipped, "
               "FOB/LaidInCost = what KSS paid per unit (our wholesale revenue), plus batch codes and expiry. Chains: our Metrc transfer -> "
               "PalletTag -> PurchaseID -> KSS receipt status/costs. Same DECISION as /purchases (reconciliation scope)."),
    'PurchaseTransID': ('NEW', 'reconciliation line key', 'Also the FIFO layer id referenced by /inventory.PurchaseTransID.'),
    'PurchaseID': ('JOIN', 'parent', ''),
    'ProductID': ('JOIN', "products.external_ids['kss']", ''),
    'PalletTag': ('MAP', 'metrc package tag join', 'METRC TAG (1A40603...) - hard join to our packages/transfers. 24/196 null.'),
    'BatchCode': ('JOIN', 'product_batches.batch_number', '19/196 null.'),
    'NumUnits': ('NEW', 'reconciliation units', 'Negative = returns.'),
    'Cases': ('NEW', 'reconciliation cases', ''),
    'Ordered': ('NEW', 'reconciliation ordered', 'Equals NumUnits in live sample.'),
    'Weight': ('NOUSE', '', 'Line weight; uom undocumented.'),
    'FOB': ('NEW', 'reconciliation unit price', 'Per-unit price KSS paid = our sell price. String decimal; 0.01 penny rows appear (tolling-style pricing precedent).'),
    'LaidInCost': ('NEW', 'reconciliation landed cost', 'Equals FOB in live sample (no freight uplift).'),
    'ExtPrice': ('NEW', 'reconciliation line total', 'Negative = returns.'),
    'DepositCost': ('NOUSE', '', '0.00 in all live rows (beverage-world deposit concept).'),
    'ExpirationDate': ('JOIN', 'batch enrich', 'Cross-check against /inventory/batches expiration. 17/196 null.'),
    'CodeDate': ('NOUSE', '', 'Batch code date (149/196 null); duplicative of batch data.'),
    'TimeCreated': ('JOIN', 'record stamp', ''),
    'TimeUpdated': ('JOIN', 'sync cursor', ''),
}

# ---------------------------------------------------------------------------
# Endpoint metadata: wire-inventory key, path, doc-only marker
# ---------------------------------------------------------------------------
ENDPOINTS = [
    # (mapping key, inventory key or None, display path, detail inventory keys)
    ('states', 'states', 'GET /states', []),
    ('locations', 'locations', 'GET /locations (+ /locations/:locationID)', ['locations_detail']),
    ('salesReps', 'salesReps', 'GET /salesReps', []),
    ('users', 'users', 'GET /users (+ /users/:userID)', ['users_detail']),
    ('suppliers', 'suppliers', 'GET /suppliers (+ /suppliers/:supplierID)', ['suppliers_detail']),
    ('suppliers_creditTerms', 'suppliers_creditTerms', 'GET /suppliers/creditTerms', []),
    ('vendors', 'vendors', 'GET /vendors', []),
    ('productCategories', 'productCategories', 'GET /productCategories', []),
    ('products', 'products', 'GET /products (+ /products/:productID)', ['products_detail']),
    ('customers', 'customers', 'GET /customers (+ /customers/:customerID)', ['customers_detail']),
    ('deliveryDays', 'deliveryDays', 'GET /deliveryDays', []),
    ('allocations', 'allocations', 'GET /allocations', []),
    ('arAging', 'arAging', 'GET /arAging', []),
    ('inventory', 'inventory', 'GET /inventory', []),
    ('inventory_batches', 'inventory_batches', 'GET /inventory/batches', []),
    ('retailerInventory', 'retailerInventory', 'GET /retailerInventory', []),
    ('invoices', 'invoices', 'GET /invoices (+ /invoices/:invoiceID)', ['invoices_detail']),
    ('invoiceTransactions', 'invoiceTransactions', 'GET /invoiceTransactions (+ /:invoiceID)', ['invoiceTransactions_detail']),
    ('invoiceCOAs', 'invoiceCOAs', 'GET /invoiceCOAs (+ /:invoiceID)', ['invoiceCOAs_detail']),
    ('invoices_creditTerms', 'invoices_creditTerms', 'GET /invoices/creditTerms', []),
    ('customers_creditTerms', 'customers_creditTerms', 'GET /customers/creditTerms', []),
    ('customerPricing', 'customerPricing', 'GET /customerPricing', []),
    ('menuPromotions', 'menuPromotions', 'GET /menuPromotions', []),
    ('promotionsProducts', 'promotionsProducts', 'GET /promotionsProducts', []),
    ('payments_types', 'payments_types', 'GET /payments/types', []),
    ('payments', 'payments', 'GET /payments', []),
    ('payments_openInvoices', 'payments_openInvoices', 'GET /payments/openInvoices', []),
    ('payments_applications', 'payments_applications', 'GET /payments/applications', []),
    ('payments_applications_POST', None, 'POST /payments/applications (write params)', []),
    ('purchases', 'purchases', 'GET /purchases (+ /purchases/:purchaseID)', ['purchases_detail']),
    ('purchaseTrans', 'purchaseTrans', 'GET /purchaseTrans', []),
]

STATUS_ORDER = ['MAP', 'NEW', 'JOIN', 'NOUSE', 'BLOCKED']


def esc(text):
    return str(text).replace('|', '\\|')


def wire_cols(inv_ep, field):
    if inv_ep is None:
        return 'write param', '-', '-'
    info = inv_ep['fields'].get(field)
    if info is None:
        return 'doc-only', '-', '-'
    fill = f"{info['present'] - info['nulls']}/{info['of']}"
    types = '/'.join(info['types'])
    ex = '; '.join(info['examples'])[:48]
    return fill, types, ex


def main():
    problems = []
    counts = {s: 0 for s in STATUS_ORDER}
    lines = []
    nouse_report = []
    checklist = []

    lines.append('# KSS INTEGRATION MAPPING (Kiva / Encompass -> Budtags)')
    lines.append('')
    lines.append('> **Planning document - no code yet.** Field-by-field mapping of every KSS API endpoint to its Budtags')
    lines.append('> parking spot, built from a LIVE wire inventory (2026-08-19, test env `api.test.kssdata.com`, Supplier key')
    lines.append('> scoped to Gelato / SupplierID 61) cross-checked against the verbatim docs skill (`budtags/skills/kss/`).')
    lines.append('> Wire columns (fill = non-null/sampled, types, examples) are generated mechanically from the harvest;')
    lines.append('> mapping columns are authored. Regenerate: `kss_mapping_gen.py` in the planning session scratchpad.')
    lines.append('>')
    lines.append('> **Context:** the CA org (Gelato) sells through KSS (Kiva Sales & Service, an Encompass ERP shop). Our key')
    lines.append("> sees KSS's world from the supplier side: their 'customers' are retailers buying our product, their")
    lines.append("> 'purchases' are them buying FROM our manufacturers (= the mirror of our outbound Distru/Metrc transfers),")
    lines.append("> their 'invoices' are depletions of our brand to retail.")
    lines.append('')
    lines.append('## Status legend')
    lines.append('')
    lines.append('| Status | Meaning |')
    lines.append('|---|---|')
    lines.append('| **MAP** | Parking spot exists in Budtags today; importer writes it directly |')
    lines.append('| **NEW** | Needs new schema (column / table / enum) - collected in the Schema Plan |')
    lines.append('| **JOIN** | Identity, scope, cursor, or lookup key - drives resolution or lives inside an external_ids JSON; not its own column |')
    lines.append('| **NOUSE** | Interesting but no Budtags use case yet - full audit report at the bottom |')
    lines.append('| **BLOCKED** | Cannot verify live (hidden from our Supplier key, empty test data, broken endpoint, or always-null) |')
    lines.append('')
    lines.append('## Global wire conventions (apply to every endpoint)')
    lines.append('')
    lines.append('- Everything is PascalCase; array filters are comma-separated; envelope is `{Data, Page, PageSize, HasNextPage}` (detail GETs included).')
    lines.append('- Money/quantity fields arrive as STRING decimals (`"250.000000"`, `"5.60"`) with one exception noted per-field; cast deliberately.')
    lines.append('- `TimeUpdated` exists on almost every record but there is NO updated-since filter: incremental sync = full walk + `TimeUpdated` diff, made cheap by ETag/If-None-Match (304 verified live). Test data shows bulk-stamped TimeUpdated values - treat as page-level freshness, not per-field.')
    lines.append('- `SupplierID`/`Supplier`/`State` appear everywhere as scope echoes (always 61/Gelato/CA for our key) - JOIN columns, never persisted per-row.')
    lines.append('- Silent default filters (invoices Statuses=1, customers Active, products Active, users/vendors/suppliers Active) MUST be overridden explicitly by every importer.')
    lines.append('')

    # checklist placeholder (filled after loop)
    checklist_index = len(lines)
    lines.append('')

    for mkey, ikey, display, detail_keys in ENDPOINTS:
        mapping = M[mkey]
        inv_ep = INV.get(ikey) if ikey else None
        sampled = inv_ep['sampled'] if inv_ep else 0
        intro = mapping.get('_intro', '')
        fields = [f for f in mapping if f != '_intro']

        # completeness: every live field must be mapped
        if inv_ep:
            for f in inv_ep['fields']:
                if f not in mapping:
                    problems.append(f'{mkey}: live field {f} has NO mapping row')
            for f in fields:
                info = inv_ep['fields'].get(f)
                if info is None and mapping[f][0] != 'BLOCKED':
                    problems.append(f"{mkey}: mapped field {f} not seen live and not BLOCKED")
        # detail endpoints: verify field subset
        detail_note = ''
        for dk in detail_keys:
            dep = INV.get(dk)
            if not dep or dep['sampled'] == 0:
                continue
            extra = set(dep['fields']) - set(INV[ikey]['fields'])
            missing = set(INV[ikey]['fields']) - set(dep['fields'])
            if extra:
                problems.append(f'{mkey}: detail {dk} has EXTRA fields {sorted(extra)}')
            if missing:
                detail_note = (f' Detail response verified as the same shape'
                               f' (fields absent in the single sampled record: {", ".join(sorted(missing))}).')
            else:
                detail_note = ' Detail response verified: identical field set.'

        anchor = display.split(' ')[1].strip('/').replace('/', '').replace(':', '').lower()
        stats = {s: sum(1 for f in fields if mapping[f][0] == s) for s in STATUS_ORDER}
        stat_str = ' '.join(f'{s}:{n}' for s, n in stats.items() if n)
        checklist.append(f'- [ ] `{display}` - {len(fields)} fields ({stat_str})')

        lines.append(f'## {display}')
        lines.append('')
        lines.append(f'*Live sample: {sampled} records.*{detail_note}')
        lines.append('')
        if intro:
            lines.append(intro)
            lines.append('')
        lines.append('| KSS field | Fill | Live type | Example | Status | Budtags parking spot | Notes |')
        lines.append('|---|---|---|---|---|---|---|')
        for f in fields:
            status, spot, note = mapping[f]
            counts[status] += 1
            fill, types, ex = wire_cols(inv_ep, f)
            lines.append(f'| `{esc(f)}` | {fill} | {types} | {esc(ex)} | **{status}** | {esc(spot) or "-"} | {esc(note)} |')
            if status == 'NOUSE':
                nouse_report.append((display, f, note or spot or ''))
        lines.append('')

    # checklist injection
    total_fields = sum(counts.values())
    header = ['## Endpoint checklist (your point-by-point pass)', '',
              f'**{total_fields} fields across {len(ENDPOINTS)} endpoint groups** - '
              f"MAP:{counts['MAP']} NEW:{counts['NEW']} JOIN:{counts['JOIN']} "
              f"NOUSE:{counts['NOUSE']} BLOCKED:{counts['BLOCKED']}", '']
    lines[checklist_index:checklist_index] = header + checklist + ['']

    # ------------------------------------------------------------------
    lines.append('---')
    lines.append('')
    lines.append('## Schema Plan (the migration foundation)')
    lines.append('')
    lines.append('Everything marked NEW rolls up here. Per standing migration rules: one migration per branch, no backfills,')
    lines.append('rehearse on a prod dump. Items 1-2 are required for ANY import; 3+ are per-DECISION.')
    lines.append('')
    lines.append("1. **`integration_sync_events.source` enum** currently `enum('distru','leaflink','canix')` - add `'kss'`. Required for audit logging of any KSS import (ERP-grade who/why/when rule).")
    lines.append("2. **`organizations.kss_supplier_id`** (unsigned int, nullable) - our SupplierID (61) at KSS, precedent `organizations.leaflink_seller_company_id`. The API key itself goes in `secrets` with a new `secret_types` row ('KSS API Key') - data, not schema.")
    lines.append("3. **`product_categories.kss_category_id`** (nullable int) - OPTIONAL; a static name map in the importer avoids the migration (only 10 categories).")
    lines.append('4. **DECISION A - `kss_inventory_snapshots`** (org, product_id, kss_product_id, location_id, the 10 stock buckets, doi, avg_daily_sales_90d, not_authorized, captured_at). Distributor warehouse stock; use case = production planning. Optionally a batch grain for InventoryUnits.')
    lines.append('5. **DECISION B - `kss_retailer_inventory`** (org, business_partner_id, kss_customer_id, product_id, on_hand, daily_sales, last_inventory_date, kss_row_id, captured_at) OR extend `customer_inventory_snapshots` with a source column. Retail sell-through intel.')
    lines.append('6. **DECISION C - `kss_invoices` + `kss_invoice_lines`** depletion mirror (headers: id/num/partner/status/dates/totals; lines: product/batch/units/cases/ordered/backorder/prices/discount/promotion_id). Powers sell-through analytics, promo verification, backorder signals. Mirror is load-bearing because KSS has no updated-since filter (Distru adjustments precedent).')
    lines.append('7. **DECISION D - purchases reconciliation**: report-only (no schema) vs stamping matched `marketplace_orders.external_ids[\'kss_purchase\']` + a small `kss_purchase_recon` results table. Joins on purchaseTrans.PalletTag = Metrc tag.')
    lines.append("8. **DECISION E - promo linkage**: `promo_deals` has no external-id column; add `promo_deals.external_ids` (json) if promo verification lands. Blocked anyway until KSS fixes /promotionsProducts (500).")
    lines.append("9. **DECISION F - SupplierCredit ingest** from /payments (PaymentTypeID=-1 rows): reconcile Gelato-funded credits against `promo_deals`/`seller_credits`. Could ride on DECISION C's tables or a small `kss_supplier_credits` table.")
    lines.append('')
    lines.append('No migration needed for: partners (business_partners + integration_company_mappings, source varchar fits), products')
    lines.append("(external_ids json), batches (product_batches/product_batch_links/batch_documents external_ids + metrc_package_local_metadata.source varchar), contacts (customer_contacts.external_ids), sync cursors (integration_sync_cursors.source varchar).")
    lines.append('')

    lines.append('---')
    lines.append('')
    lines.append(f"## FULL NOUSE AUDIT REPORT ({counts['NOUSE']} fields) - for Jason's review before anything is written")
    lines.append('')
    lines.append('Every field parked as "interesting but no Budtags use case yet", with the reasoning. Overrule any row and it')
    lines.append('moves to MAP/NEW in this document first, code second.')
    lines.append('')
    cur = None
    for display, f, note in nouse_report:
        if display != cur:
            lines.append(f'### {display}')
            lines.append('')
            cur = display
        lines.append(f'- **`{f}`** - {note}' if note else f'- **`{f}`**')
    lines.append('')

    lines.append('---')
    lines.append('')
    lines.append('## Open questions / blockers')
    lines.append('')
    lines.append('1. **/promotionsProducts returns HTTP 500 on test** (every attempt) - needs a KSS support ticket (include X-Request-Id). Blocks promo verification (DECISION E).')
    lines.append('2. **Production key owed from Kiva** - everything here is test-env; test DB refreshes Sundays and holds fake rows (LIC-99999-FAKE, KSS Live Test Customer, N/A SKUs). Field-fill numbers must be re-checked on prod before importers ship.')
    lines.append('3. **10 customer fields hidden from our Supplier key** (SalesRep*, OnHold, CollectionAgent*, DeliveryMinimum, NextDeliveryDates, ProfilePictureURL) - ask KSS whether a supplier key can be granted these, or accept /salesReps as the rep source.')
    lines.append('4. **SupplierProductNumber quality** - the natural product-resolution key holds N/A/0 garbage on test; confirm on prod, else resolution falls back to name matching.')
    lines.append('5. **Empty-on-test endpoints**: /allocations, /customers/creditTerms - provisional mappings only.')
    lines.append('6. **WholesaleUnitsPerCase vs unit_multiplier semantics** - verify against the LeafLink case/unit convention before wiring (wholesale price is per CASE across all sources; Canix NULL).')
    lines.append('7. **Undocumented fields KSS should confirm**: purchases.PurchaseGlobalID(+ExportedAt), ReceivingNum, PurchasePDFURLAPIKeyID, LastEditTime(always null), payments.LoadSheetStatusID, PaymentTypeID=-1 sentinel; inventory DOI/AvgDailySales90d lack Field-Definitions entries.')
    lines.append('8. **PDF links embed an APIKeyID** (invoices.PDFURL, purchases.PublicPDFLink) - decide whether fetching/storing these is acceptable; recommendation: do not persist.')
    lines.append('')

    out_text = '\n'.join(lines) + '\n'

    if problems:
        print('=== COMPLETENESS PROBLEMS ===')
        for p in problems:
            print(' -', p)
        sys.exit(1)

    with open(OUT, 'w') as f:
        f.write(out_text)
    print(f'Wrote {OUT}')
    print(f'Total fields: {total_fields}  ' + '  '.join(f'{s}:{counts[s]}' for s in STATUS_ORDER))


if __name__ == '__main__':
    main()
