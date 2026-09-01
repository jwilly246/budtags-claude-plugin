# Distru Entity Types

TypeScript type reference for entities returned by the Distru Public API v1. **Phase 0.5-audited (2026-05-21)** against live API responses + user-supplied docs pastes. All interfaces below reflect verified live shapes.

> **Source-of-truth note:** This file is the **secondary** source. The canonical reference is `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md`. If the two ever conflict, the mapping doc wins.

---

## Core Types (shared primitives)

```ts
export type DistruId = string; // UUID format (except ProductPosMapping and CustomFieldDefinition which use INTEGER)
export type DistruTimestamp = string; // ISO 8601: "2026-05-16T14:42:00Z"
export type DistruDate = string;      // ISO 8601 date: "2026-05-16"
export type DistruDecimalString = string; // Decimal values arrive as STRINGS (e.g., "10.000000000", "-0.3")

/**
 * Distru's pagination envelope.
 *
 * - `next_page` is a FULL URL STRING when present, not an integer
 * - The `next_page` key may be ABSENT (not null) when no more pages
 *
 * Phase 0.5 verified: terminal check should be `! empty($body['next_page'])`.
 */
export interface DistruPaginatedResponse<T> {
    data: T[];
    next_page?: string | null;
}

/**
 * Address shape used as a NESTED OBJECT on Company.billing_address/shipping_address (if exposed).
 * NOTE: On /locations, `address` is a FLAT STRING, not this object. Per-endpoint shape varies.
 */
export interface DistruAddress {
    line_1: string;
    line_2?: string;
    city: string;
    state: string;
    postal_code: string;
    country?: string;
}

/**
 * Custom field VALUE shape on entity read responses.
 *
 * - READ shape: array of {id, name, value} objects
 * - WRITE shape: object map {"id_as_string": "value"} — DIFFERENT from read
 *
 * Importer's read-parser and write-builder need separate code paths.
 */
export interface DistruCustomFieldValue {
    id: number;          // INTEGER, not UUID
    name: string;
    value: string | number | boolean | null;
}
```

---

## Sales Domain

```ts
/**
 * Order status enum — 7 values per Distru docs.
 * NOTE: filter input AND response output both use UPPERCASE on /orders direct response.
 * BUT when embedded in /invoices.order.status, the value is returned in Title Case.
 * Spelling: `CANCELED` with SINGLE L. `CANCELLED` (double L) returns HTTP 400.
 */
export type DistruOrderStatus =
    | 'PENDING'
    | 'PROCESSING'
    | 'READY_TO_SHIP'
    | 'DELIVERING'
    | 'DELIVERED'
    | 'COMPLETED'
    | 'CANCELED';   // single L!

/**
 * Embedded reduced refs (sub-objects with minimal fields).
 * Distru returns many entities as `{id, name, ...}` rather than the full object when embedded.
 */
export interface DistruEntityRef {
    id: DistruId;
    name?: string;
    updated_datetime?: DistruTimestamp;
}

/**
 * Charge embedded in orders/invoices/purchases.
 * Charges have nested tax {id, name, percent} when applicable.
 */
export interface DistruCharge {
    id?: DistruId;
    name: string;
    type: string;                          // CHARGE, DISCOUNT, etc.
    unit_type: 'PERCENT' | 'PRICE';
    percent?: DistruDecimalString;
    price?: DistruDecimalString;
    tax?: { id: DistruId; name: string; percent: DistruDecimalString } | null;
}

/**
 * SalesOrderItem — line item on /orders response.
 * 15 fields. Cost field uses `cost_per_unit` (NO `_actual` suffix), but `cost_per_unit_default`,
 * `total_cost_actual`, `total_cost_default` all have suffixes. Distru's naming is inconsistent
 * within this single object.
 */
export interface DistruOrderLineItem {
    id: DistruId;
    product: DistruEntityRef;              // {id, name, sku, updated_datetime}
    batch?: { id: DistruId; name: string; batch_number?: string | null } | null;
    package?: {
        id: DistruId;
        batch_number?: string | null;
        compliance_label?: string;
        metrc_label?: string;
        status?: string;
    } | null;
    location?: {
        id: DistruId;
        name: string;
        address: string;                    // FLAT STRING
        company_id: DistruId;
        license_id: DistruId | null;
    } | null;
    quantity: DistruDecimalString;
    compliance_quantity: DistruDecimalString | null;
    price: DistruDecimalString;
    price_base: DistruDecimalString;       // pre-discount unit price
    returned_quantity: DistruDecimalString;
    cost_per_unit: DistruDecimalString | null;    // NOTE: no _actual suffix!
    cost_per_unit_default: DistruDecimalString | null;
    total_cost_actual: DistruDecimalString | null;
    total_cost_default: DistruDecimalString | null;
    is_sample: boolean;
}

/**
 * Full Order — 23 top-level fields. List endpoint and detail endpoint return same 23-field shape.
 * NO subtotal/tax/shipping/discount/cultivation_tax at top level — those come via charges[].
 * NO completion_datetime, currency, customer_po_number — none exist on Distru's Order.
 */
export interface DistruOrder {
    id: DistruId;
    order_number: string;
    status: DistruOrderStatus;
    company: DistruEntityRef;
    creator: DistruUser | null;            // Full User object when present
    owner: DistruUser | null;
    billing_location: DistruLocation | null;
    shipping_location: DistruLocation | null;
    order_datetime: DistruTimestamp;
    delivery_datetime: DistruTimestamp | null;
    due_datetime: DistruTimestamp;
    inserted_datetime: DistruTimestamp;
    updated_datetime: DistruTimestamp;
    payment_term_name: string | null;
    internal_notes: string | null;
    external_notes: string | null;         // NEW Phase 0.5 — not in Distru's Models doc
    metrc_transfer_id: number | null;      // INTEGER on Distru
    biotrack_id: string | null;
    leaflink_order_number: string | null;
    total: DistruDecimalString;
    items: DistruOrderLineItem[];
    charges: DistruCharge[];
    custom_data: DistruCustomFieldValue[];
}

/**
 * Invoice status enum — Title Case INPUT in filter, UPPERCASE_UNDERSCORE in response field.
 * Examples:
 *   filter: `?status[]=Not Paid`        →  response: `"status": "NOT_PAID"`
 *   filter: `?status[]=Fully Paid`      →  response: `"status": "FULLY_PAID"`
 */
export type DistruInvoiceStatus = 'NOT_PAID' | 'PARTIALLY_PAID' | 'FULLY_PAID' | 'OVER_PAID';

/**
 * InvoiceItem — 12 fields. Has `order_item_id` back-link to SalesOrderItem.
 * Like SalesOrderItem, uses `cost_per_unit` (no _actual suffix).
 * Lacks: location, is_sample, compliance_quantity, price_base (which SalesOrderItem has).
 */
export interface DistruInvoiceItem {
    id: DistruId;
    order_item_id: DistruId;               // back-link to source order line
    product: DistruEntityRef;
    batch?: { id: DistruId; name: string } | null;
    package?: object | null;
    quantity: DistruDecimalString;
    price: DistruDecimalString;
    returned_quantity: DistruDecimalString;
    cost_per_unit: DistruDecimalString | null;
    cost_per_unit_default: DistruDecimalString | null;
    total_cost_actual: DistruDecimalString | null;
    total_cost_default: DistruDecimalString | null;
}

/**
 * Full Invoice — 17 fields. List and detail return same shape.
 * NO `payments` field — payments are WRITE-ONLY via POST /invoices/{id}/payments.
 * `order` sub-object is REDUCED to 4 fields (id, order_number, status [TITLE CASE], total).
 */
export interface DistruInvoice {
    id: DistruId;
    invoice_number: string;
    status: DistruInvoiceStatus;
    company: DistruEntityRef;
    creator: DistruUser;
    owner: DistruUser;
    order: {
        id: DistruId;
        order_number: string;
        status: string;                    // Title Case here! E.g. "Pending", "Completed"
        total: DistruDecimalString;
    };
    invoice_datetime: DistruTimestamp;
    due_datetime: DistruTimestamp;
    inserted_datetime: DistruTimestamp;
    updated_datetime: DistruTimestamp;
    total: DistruDecimalString;
    paid_amount: DistruDecimalString;      // aggregate only — line-item payments not exposed
    remaining_amount: DistruDecimalString;
    items: DistruInvoiceItem[];
    charges: DistruCharge[];
    custom_data: DistruCustomFieldValue[];
    // payments: NOT EXPOSED — write-only via POST /invoices/{id}/payments
}

/**
 * InvoicePayment — only accessible via POST response (no GET endpoint).
 * Customer's historical payments cannot be retrieved via the API.
 */
export interface DistruInvoicePayment {
    id: DistruId;
    invoice_id: DistruId;
    amount: DistruDecimalString;
    description: string;
    payment_date: DistruTimestamp;
    payment_number: string;
    inserted_datetime: DistruTimestamp;
    payment_method: { id: DistruId; name: string; deleted_at: DistruTimestamp | null };
    quickbooks_deposit_account_id: string | null;
}
```

---

## Purchasing Domain

```ts
/**
 * Purchase status enum — Title Case input, UPPERCASE response (like Invoice).
 * 5 documented values per Distru docs.
 */
export type DistruPurchaseStatusInput =
    | 'Completed'
    | 'Delivering'
    | 'Partially Received'
    | 'Pending'
    | 'Processing';

/**
 * PurchaseOrderItem — 11 fields. NO cost fields (cost lives on linked Batch/Package).
 * Has compliance_quantity, location, is_sample, price_base (matches SalesOrderItem additions).
 * Has received_quantity (tracks delivery progress).
 */
export interface DistruPurchaseLineItem {
    id: DistruId;
    product: DistruEntityRef;
    batch?: { id: DistruId; name: string } | null;
    package?: object | null;
    location?: DistruLocation | null;
    quantity: DistruDecimalString;
    compliance_quantity: DistruDecimalString | null;
    received_quantity: DistruDecimalString;
    price: DistruDecimalString;
    price_base: DistruDecimalString;
    is_sample: boolean;
    // NO cost_per_unit_actual / cost_per_unit_default — cost lives on linked Batch/Package
}

/**
 * Purchase — 12 top-level fields at the 2026-05-26 probe. NO creator/owner/payments then.
 * 2026-09-01 CORRECTION (live re-probe, Evo, 500 records): 25 keys — creator (500/500, DistruUser),
 * owner (495/500), payments, billing_location, supplier_location, location, metrc_transfer_id,
 * biotrack_id, qb_bill_id, paid, payment_status, description, tasks are now emitted.
 * Cannot update PO past Pending status — Distru returns 400.
 */
export interface DistruPurchase {
    id: DistruId;
    purchase_number: string;
    status: string;                        // UPPERCASE in response (e.g. "PENDING", "COMPLETED")
    company: DistruEntityRef;
    order_datetime: DistruTimestamp;
    due_datetime: DistruTimestamp;
    inserted_datetime: DistruTimestamp;
    updated_datetime: DistruTimestamp;
    total: DistruDecimalString;
    items: DistruPurchaseLineItem[];
    charges: DistruCharge[];
    custom_data: DistruCustomFieldValue[];
    // 2026-09-01: creator/owner/payments (and more) ARE emitted now — see the interface docblock
    creator?: DistruUser;
    owner?: DistruUser | null;
}

/**
 * PurchasePayment — write-only via POST /purchases/{id}/payments.
 * Same shape as InvoicePayment but with purchase_id instead of invoice_id.
 */
export interface DistruPurchasePayment {
    id: DistruId;
    purchase_id: DistruId;
    amount: DistruDecimalString;
    description: string;
    payment_date: DistruTimestamp;
    payment_number: string;
    inserted_datetime: DistruTimestamp;
    payment_method: { id: DistruId; name: string; deleted_at: DistruTimestamp | null };
    quickbooks_deposit_account_id: string | null;
    // QB account type must be "Bank" or "Credit Card" (different from Invoice which requires "Bank" or "Other Current Asset")
}
```

---

## CRM Domain

```ts
/**
 * Company's relationship_type field is TENANT-CUSTOMIZABLE.
 * Distru's Models doc claims fixed enum (CUSTOMER/VENDOR/CUSTOMER_AND_VENDOR/NEITHER),
 * but live tenants have their own labels.
 *
 * Test org observed: `Current Customer`, `Current Supplier`, `Brand`, `Potential Customer`, null
 *
 * NO `relationship_type` filter exists on /companies — must fetch all and bucket client-side.
 */
export type DistruRelationshipType = string;  // tenant-customizable

/**
 * Full Company — 22 top-level fields.
 * NO flat address fields — addresses live in the embedded `locations[]` array.
 * NO discount_percent, credit_limit, payment_term, payment_methods, etc. — those don't exist on Distru's Company.
 *
 * 5 separate email fields: default_email, sales_order_email, purchase_order_email, invoice_email, order_shipment_email.
 * outstanding_balance_threshold is in CENTS (not dollars).
 */
export interface DistruCompany {
    id: DistruId;
    name: string;
    legal_business_name: string;            // can be empty string ("") — distinct from null
    category: string | null;                // OPEN STRING — tenants define values like Dispensary, Manufacturer, Retail, etc.
    phone_number: string | null;
    website: string | null;
    default_email: string | null;
    sales_order_email: string | null;
    purchase_order_email: string | null;
    invoice_email: string | null;
    order_shipment_email: string | null;
    default_sales_order_notes: string | null;
    default_purchase_order_notes: string | null;
    outstanding_balance_threshold: number | null;  // INTEGER, in CENTS
    owner_id: DistruId | null;
    group: { id: DistruId; name: string } | null;          // CompanyGroup
    relationship_type: { id: DistruId; name: string } | null;  // TENANT-CUSTOMIZABLE; can be null
    locations: DistruLocation[];           // EMBEDDED full Location objects
    licenses: Array<{ id: DistruId; license_number: string }>;
    custom_data: DistruCustomFieldValue[];
    deleted_at: DistruTimestamp | null;
    inserted_datetime: DistruTimestamp;    // ADDED after 2026-05-25 — 830/830 live Evo companies (2026-09-01)
    updated_datetime: DistruTimestamp;
    // Also on the 2026-09-01 wire (population not audited): tasks, outstanding_balance,
    // default_payment_term, qb_customer_id, qb_vendor_id, leaflink_customer_id, leaflink_brand_id
}

/**
 * Contact — 15 fields (17 as of 2026-09-01: inserted_datetime + updated_datetime now emitted). Has BOTH first_name AND last_name AND full_name (3 separate name fields).
 * full_name is SERVER-DERIVED from first+last — write only accepts first/last; full_name in response only.
 *
 * Company and owner are REDUCED to {id} only in API responses (no embedded user details).
 *
 * NO `secondary_email`, `phone_extension`, `is_primary` — those phantom fields don't exist on Distru's Contact.
 * NO `company_id` filter on /contacts.
 */
export interface DistruContact {
    id: DistruId;
    first_name: string;
    last_name: string;
    full_name: string;                     // server-derived
    email: string | null;
    phone_number: string | null;
    work_phone_number: string | null;
    title: string | null;                  // Distru's "role" equivalent
    description: string | null;
    driver_license_number: string | null;
    driver_license_issuing_state: string | null;
    company: { id: DistruId };             // REDUCED to just id
    owner: { id: DistruId };               // REDUCED to just id
    custom_data: DistruCustomFieldValue[];
    deleted_at: DistruTimestamp | null;
    inserted_datetime: DistruTimestamp;    // ADDED after 2026-05-25 — 454/454 live Evo contacts (2026-09-01)
    updated_datetime: DistruTimestamp;     // ADDED — same probe
}

/**
 * Location — 7 fields. `address` is a FLAT STRING here (NOT a DistruAddress nested object).
 * This is a per-endpoint shape choice; address shape varies across the API.
 */
export interface DistruLocation {
    id: DistruId;
    name: string;
    address: string;                       // FLAT STRING, not nested object
    company_id: DistruId | null;
    license_id: DistruId | null;
    license: { id: DistruId; license_number: string } | null;  // null when no license tied
    deleted_at: DistruTimestamp | null;
}
```

---

## Products Domain

```ts
/**
 * Brand — RICHER shape than Distru's Models page claims.
 * Models page said `{name}` only; live shows `{id, name, updated_datetime}` — 3 fields.
 * Same shape as Vendor — both reference the same underlying Company entity.
 */
export interface DistruBrand {
    id: DistruId;
    name: string;
    updated_datetime: DistruTimestamp;
}

/**
 * ProductCategory — `{id, name, type}` — 3 fields.
 * Categories ARE objects (not strings) on Product response.
 */
export interface DistruProductCategory {
    id: DistruId;
    name: string;
    type: string;                          // observed: OTHER, etc. (open string)
}

export interface DistruProductSubcategory {
    id: DistruId;
    name: string;
}

/**
 * ProductGroup — Distru's equivalent of "ProductLine."
 * Phase 0.5 finding — we previously thought this didn't exist on Distru's side.
 * `{id, name}` — populated on ~35% of products in the audited org.
 */
export interface DistruProductGroup {
    id: DistruId;
    name: string;
}

export interface DistruUnitType {
    id: DistruId;
    name: string;                          // e.g., "Gram", "Ounce", "Unit"
}

export interface DistruImage {
    id: DistruId;
    name: string;
    url: string;
    rank: number;
}

/**
 * Product — 26 top-level fields.
 * Distru's docs call the parent-company-of-product field `company`, but live returns `vendor`.
 * NEW field `product_group` exists (not in Models doc).
 *
 * Live `unit_net_weight_serving_size_unit_type` — note: docs Models page calls this
 * `unit_net_weight_and_serving_size_unit_type_id` (with `_and_`) for write. Read/write naming inversion.
 *
 * Read shape on `is_active: boolean`. Write expects `is_inactive: boolean` (NEGATED) — semantic inversion.
 *
 * Write-only fields not exposed in GET (as of 2026-05-25): is_featured, wholesale_unit_price, total_thc, total_cbd,
 * quantity_available_threshold_min/max, tags[], upc, menu_visibility, inventory_tracking_method, etc.
 * 2026-09-01 CORRECTION: every one of those IS emitted on GET now, plus inserted_datetime, creator, owner,
 * leaflink_product_id, quantity_* rollups, tasks, gross_weight(_unit_type), total_cannabinoid_unit,
 * treez_wholesale_price — 49 top-level keys, live-verified on Evo. See categories/products.md.
 */
export interface DistruProduct {
    id: DistruId;
    name: string;
    sku: string;
    external_name: string | null;          // customer-facing
    description: string | null;
    description_markdown: string | null;
    brand: DistruBrand | null;             // 3 fields, not just name
    category: DistruProductCategory | null;  // OBJECT, not string
    subcategory: DistruProductSubcategory | null;
    strain: DistruStrain | null;
    product_group: DistruProductGroup | null;  // NEW Phase 0.5
    unit_type: DistruUnitType;
    unit_net_weight_serving_size_unit_type: DistruUnitType | null;  // note: NO `_and_` on read; write uses `_and_`
    unit_price: DistruDecimalString;
    unit_cost: DistruDecimalString | null;
    msrp: DistruDecimalString | null;
    units_per_case: DistruDecimalString | null;
    unit_net_weight: DistruDecimalString | null;
    unit_serving_size: DistruDecimalString | null;
    is_active: boolean;                    // NOTE: read=is_active, write=is_inactive (negated semantics)
    images: DistruImage[];
    menus: Array<{ menu_id: DistruId; menu_name: string }>;  // membership references
    custom_data: DistruCustomFieldValue[];
    vendor: { id: DistruId; name: string; updated_datetime: DistruTimestamp } | null;  // Distru docs say "company"
    updated_datetime: DistruTimestamp;
    deleted_at: DistruTimestamp | null;
    // ── ADDED after 2026-05-25, live-verified 2026-09-01 (population on 4,495 active Evo products) ──
    inserted_datetime: DistruTimestamp;    // 4,495/4,495 — true creation stamp
    creator: DistruUser;                   // 4,495/4,495
    owner: DistruUser;                     // 4,495/4,495
    inventory_tracking_method: string;     // 4,495/4,495, e.g. "PRODUCT"
    is_featured: boolean;
    menu_visibility: 'DO_NOT_INCLUDE' | 'INCLUDE_IN_ALL' | 'INCLUDE_IN_SELECT';
    quantity_available: DistruDecimalString;
    quantity_active: DistruDecimalString;
    quantity_reserved: DistruDecimalString;
    quantity_active_by_location: unknown[];          // 1,140/4,495 non-empty
    quantity_available_threshold_min: DistruDecimalString | null;  // 445/4,495
    quantity_available_threshold_max: DistruDecimalString | null;  // always null on Evo
    wholesale_unit_price: number | null;   // JSON NUMBER, not a decimal-string — 452/4,495
    treez_wholesale_price: unknown | null; // always null on Evo
    leaflink_product_id: number | null;    // 240/4,495
    tags: string[];                        // 25/4,495 non-empty
    upc: string | null;                    // always null on Evo
    tasks: unknown | null;                 // always null on Evo
    gross_weight: unknown | null;          // always null on Evo
    gross_weight_unit_type: unknown | null;
    total_thc: DistruDecimalString | null; // 1/4,495
    total_cbd: DistruDecimalString | null; // 1/4,495
    total_cannabinoid_unit: string | null; // 3/4,495, e.g. "PERCENT"
}

/**
 * TestResult — Decision #5 REVERSED Phase 0.5 round 2.
 * Live endpoint `/test-results` (HYPHEN slug, NOT underscore).
 * Test data IS importable; was previously incorrectly marked as 404.
 *
 * 19 fields. `additional_test_results` is OPEN OBJECT MAP — keys come from the documented
 * 300+ field catalog (cannabinoids, terpenes, pesticides, heavy metals, mycotoxins, microbials,
 * residual solvents). Tenant configures which fields are tracked via "test result settings."
 *
 * package_id XOR batch_id — mutually exclusive entity refs.
 */
export interface DistruTestResult {
    id: DistruId;
    name: string;
    lab_name: string | null;
    lab_license_number: string | null;
    release_date: DistruDate | null;
    is_primary: boolean;                   // propagates to child packages when true on a batch
    mg_per_unit_type: 'mg/g' | 'mg/mL';
    thc_percentage: DistruDecimalString | null;        // max 4 decimal places
    total_thc_percentage: DistruDecimalString | null;
    thc_mg_per_unit: DistruDecimalString | null;       // must be >= 0 (no negatives)
    total_thc_mg_per_unit: DistruDecimalString | null;
    cbd_percentage: DistruDecimalString | null;
    total_cbd_percentage: DistruDecimalString | null;
    cbd_mg_per_unit: DistruDecimalString | null;
    total_cbd_mg_per_unit: DistruDecimalString | null;
    package_id: DistruId | null;           // MUTEX with batch_id
    batch_id: DistruId | null;             // MUTEX with package_id
    additional_test_results: Record<string, DistruDecimalString>;  // open object map — ~100 keys typical
    inserted_datetime: DistruTimestamp;    // ADDED after 2026-05-25 — 4,297/4,297 live Evo results (2026-09-01)
    updated_datetime: DistruTimestamp;
    // Also on the 2026-09-01 wire (population not audited): coa_url, metrc_id, biotrack_id
}

/**
 * ProductPosMapping — only endpoint with INTEGER id (not UUID).
 * POLYMORPHIC response by pos_type: only relevant POS's fields are populated; others absent.
 * The only endpoint with DELETE in the entire API.
 *
 * Uses `inserted_at`/`updated_at` (NOT `_datetime` suffix) — different from every other endpoint.
 */
export interface DistruProductPosMapping {
    id: number;                            // INTEGER, not UUID
    pos_type: 'BLAZE' | 'DUTCHIE' | 'TREEZ';
    product_id: DistruId;
    blaze_asset_id?: string | null;
    blaze_product_id?: string | null;
    blaze_retailer_id?: string | null;
    dutchie_product_id?: number | null;    // INTEGER too
    dutchie_retailer_id?: string | null;
    treez_product_id?: string | null;
    treez_retailer_id?: string | null;
    inserted_at: DistruTimestamp;          // note: _at suffix, not _datetime
    updated_at: DistruTimestamp;
}
```

---

## Inventory Domain

```ts
/**
 * Strain — 3 fields. strain_type is enum-constrained but often null.
 * Observed values in audited org: SATIVA, INDICA, HYBRID — 94% null.
 */
export interface DistruStrain {
    id: DistruId;
    name: string;
    strain_type: 'SATIVA' | 'INDICA' | 'HYBRID' | null;
}

/**
 * Batch — 11 fields without include_costs, 15 with (cost fields gated).
 * Importer MUST pass `?include_costs=true` to get cost fields.
 *
 * `primary_test_result` field exists but is null on this audited org's batch samples.
 */
export interface DistruBatch {
    id: DistruId;
    name: string;
    batch_number: string | null;
    product_id: DistruId;
    description: string | null;
    manufactured_datetime: DistruTimestamp;
    expiration_date: DistruDate | null;
    owner_id: DistruId;
    primary_test_result: Partial<DistruTestResult> | null;
    custom_data: DistruCustomFieldValue[];
    deleted_at: DistruTimestamp | null;
    // GATED behind ?include_costs=true:
    cost_per_unit_actual?: DistruDecimalString | null;     // has _actual suffix here!
    cost_per_unit_default?: DistruDecimalString | null;
    total_cost_actual?: DistruDecimalString | null;
    total_cost_default?: DistruDecimalString | null;
}

/**
 * Package — 21 fields without include_costs, 25 with (cost fields gated).
 *
 * `compliance_label` and `metrc_label` BOTH present (always equal in samples) — `metrc_label`
 * is the Metrc-specific projection; `compliance_label` is the generic compliance tag.
 *
 * `primary_test_result` embedded — same shape as on Batch. Provides cannabinoid summary
 * (THC/CBD percentage + mg/unit, with _total variants). This is our path to lab data on packages.
 *
 * No `batch_id` field — link via `batch_number` string match.
 */
export interface DistruPackage {
    id: DistruId;
    batch_number: string | null;
    compliance_label: string | null;       // generic compliance tag (Metrc/BioTrack/etc.)
    metrc_label: string | null;            // Metrc-specific (typically mirrors compliance_label)
    product_id: DistruId;
    quantity: DistruDecimalString;
    quantity_available: DistruDecimalString;
    quantity_assembling: DistruDecimalString;
    product_unit_quantity: DistruDecimalString;
    unit_type: DistruUnitType;             // OBJECT not string
    product_unit_type: DistruUnitType;
    packaged_date: DistruDate | null;
    harvest_date: DistruDate | null;
    expiration_date: DistruDate | null;
    lab_testing_state: string;             // enum: NotSubmitted, TestPassed, RetestPassed (more likely)
    is_trade_sample: boolean;
    license: { id: DistruId; license_number: string } | null;
    location: { id: DistruId; name: string } | null;
    status: string;                        // observed: active, transferred, sold, finished
    primary_test_result: Partial<DistruTestResult> | null;  // 10-field cannabinoid summary
    custom_data: DistruCustomFieldValue[];
    // GATED behind ?include_costs=true:
    cost_per_unit_actual?: DistruDecimalString | null;
    cost_per_unit_default?: DistruDecimalString | null;
    total_cost_actual?: DistruDecimalString | null;
    total_cost_default?: DistruDecimalString | null;
}

/**
 * Adjustment (Phase 0 deep-audited).
 * Endpoint slug: `/adjustments` (NOT `/stock_adjustments` which 404s).
 *
 * Three mutually-exclusive entity references — exactly ONE of package_id/batch_id/product_id is set,
 * the other two are null per row.
 *
 * Reason field is NOT a fixed enum — tenant-customizable. Observed in audited org:
 * revaluation (75%), write-off (22%), Entry Error (1.5%), other (1.3%), waste (0.5%), lab-testing (0.1%).
 * Docs sample also shows: Voluntary Surrender, Damage (BCC), expired, compliance.
 * Mixed casing patterns confirm it's open text + state-compliance enum hybrid.
 *
 * unit_type / compliance_unit_type are {id, name} OBJECTS, not strings.
 * quantity / compliance_quantity / total_cost are SIGNED STRING DECIMALS.
 */
export interface DistruAdjustment {
    id: DistruId;
    package_id: DistruId | null;           // ~1.5% populated (Entry Error)
    batch_id: DistruId | null;             // revaluation/waste route here
    product_id: DistruId | null;           // write-off entirely + some other
    quantity: DistruDecimalString;         // signed
    compliance_quantity: DistruDecimalString;
    unit_type: { id: DistruId; name: string };          // OBJECT
    compliance_unit_type: { id: DistruId; name: string } | null;
    reason: string;                        // OPEN string; tenant-customizable
    description: string | null;            // free text; ~27% of records populated
    total_cost: DistruDecimalString;
    completion_datetime: DistruTimestamp;  // filter on IS NOT NULL — pending have null
    inserted_at: DistruTimestamp;          // note: _at suffix
    license_id: DistruId | null;
    location_id: DistruId | null;
    owner_id: DistruId | null;
}

/**
 * Inventory snapshot record — from /inventory endpoint.
 * Requires `?grouping[]=PRODUCT` (and optionally LOCATION, BATCH_NUMBER).
 * NOTE field name `cost_default_per_unit` (word order REVERSED from other endpoints' `cost_per_unit_default`).
 */
export interface DistruInventory {
    product_id: DistruId;
    location_id?: DistruId;                // present when LOCATION in grouping
    batch_number?: string | null;          // present when BATCH_NUMBER in grouping
    active: DistruDecimalString;
    available: DistruDecimalString;
    reserved: DistruDecimalString;
    cost_default_per_unit: DistruDecimalString | null;   // NOTE: word order reversed
    cost_per_unit_actual: DistruDecimalString | null;
    total_cost_actual: DistruDecimalString | null;
    total_cost_default: DistruDecimalString | null;
    updated_datetime: DistruTimestamp;
}
```

---

## Manufacturing Domain

```ts
export type DistruAssemblyCreationSource =
    | 'MANUALLY_CREATED'
    | 'SPLIT_PACKAGE'
    | 'SALES_ORDER'
    | 'LAB_TESTING';

export type DistruAssemblyComplianceType = 'METRC' | 'BIOTRACK' | 'NONE';

/**
 * Assembly input (an "ingredient" — confusingly nested INSIDE outputs[]).
 * Same shape pattern as outputs, just no nested sub-arrays.
 */
export interface DistruAssemblyInput {
    product: DistruEntityRef;
    batch: { id: DistruId; name: string; batch_number?: string | null };
    package?: object | null;
    location: DistruLocation;
    quantity: DistruDecimalString;
    compliance_quantity: DistruDecimalString | null;
    cost_per_unit: DistruDecimalString | null;     // no _actual suffix
    cost_per_unit_default: DistruDecimalString | null;
    total_cost_actual: DistruDecimalString | null;
    total_cost_default: DistruDecimalString | null;
}

export interface DistruAdditionalCost {
    name: string;
    description: string | null;
    quantity: DistruDecimalString;
    cost_per_unit: DistruDecimalString;            // can be NEGATIVE (refunds/credits)
    total_cost_actual: DistruDecimalString;
    total_cost_default: DistruDecimalString;
    unit_type: DistruUnitType;
}

/**
 * Assembly output.
 * NOTE: expiration_DATETIME (not expiration_DATE) — naming differs from /batches.
 */
export interface DistruAssemblyOutput {
    product: DistruEntityRef;
    batch: { id: DistruId; name: string };
    package?: object | null;
    location: DistruLocation;
    package_unit_type: DistruUnitType | null;
    quantity: DistruDecimalString;
    compliance_quantity: DistruDecimalString | null;
    cost_per_unit: DistruDecimalString | null;
    cost_per_unit_default: DistruDecimalString | null;
    total_cost_actual: DistruDecimalString | null;
    total_cost_default: DistruDecimalString | null;
    is_finished_good: boolean;
    is_production_batch: boolean;
    expiration_datetime: DistruTimestamp | null;   // _datetime suffix here, vs /batches uses expiration_date
    compliance_label: string | null;
    package_datetime: DistruDate | null;
    ingredients: DistruAssemblyInput[];            // NESTED INSIDE outputs — Distru's structural choice
    additional_costs: DistruAdditionalCost[];
}

/**
 * Assembly — 16 top-level fields. Filter by completion_datetime (NOT updated_datetime — doesn't exist).
 * creation_source filter is SCALAR (single value), not bracket array.
 *
 * Eventually consistent (~1s lag).
 *
 * NO machine_info field exists (was a phantom in pre-Phase-0.5 documentation).
 */
export interface DistruAssembly {
    id: DistruId;
    assembly_number: string;
    status: string;                        // observed: COMPLETED, PENDING
    completion_datetime: DistruTimestamp | null;   // null = pending; filter on IS NOT NULL
    estimated_start_date: DistruTimestamp | null;
    estimated_work_hours: number | null;
    estimated_work_minutes: number | null;
    description: string | null;
    owner_id: DistruId;
    license: { id: DistruId; license_number: string } | null;
    is_metrc_processing_job: boolean;
    compliance_type: DistruAssemblyComplianceType;
    creation_source: DistruAssemblyCreationSource;
    fulfilled: boolean;
    custom_data: DistruCustomFieldValue[];
    outputs: DistruAssemblyOutput[];       // contains nested ingredients[] and additional_costs[]
}
```

---

## System Domain

```ts
/**
 * User — 6 fields. Role is an OBJECT, not a string enum.
 * Tenant-customizable role names — observed: Admin, 3PL Partner, Employee.
 */
export interface DistruUser {
    id: DistruId;
    full_name: string;
    email: string;
    role: { id: DistruId; name: string };
    banned: boolean;
    deleted_at: DistruTimestamp | null;
}

/**
 * Menu — 8 fields. visibility enum: PUBLIC, PRIVATE, PASSCODE_PROTECTED.
 * Menu→Product membership lives on Product.menus[], not Menu itself.
 */
export interface DistruMenu {
    id: DistruId;
    internal_name: string;
    external_name: string;
    visibility: 'PUBLIC' | 'PRIVATE' | 'PASSCODE_PROTECTED';
    active: boolean;
    product_count: number;
    inserted_datetime: DistruTimestamp;
    updated_datetime: DistruTimestamp;
}

/**
 * PaymentMethod — 3 fields. From /payment-methods (HYPHEN slug).
 */
export interface DistruPaymentMethod {
    id: DistruId;
    name: string;
    deleted_at: DistruTimestamp | null;
}

/**
 * CustomFieldDefinition — INTEGER id (only ProductPosMapping and this one use INTEGER).
 * Created via POST /custom-fields (HYPHEN slug). No GET endpoint exists.
 *
 * Field type vocabulary inconsistency between Models page and POST endpoint:
 *   POST values: text, date, dropdown, checkbox
 *   Models page values: string, number, boolean, date, select
 * Live POST values win.
 */
export interface DistruCustomFieldDefinition {
    id: number;                            // INTEGER
    name: string;
    description: string | null;
    parent_object: string;                 // entity type ("product", "company", "contact", etc.)
    field_type: 'text' | 'date' | 'dropdown' | 'checkbox';
    filterable: boolean;
    field_options: string[];               // populated for dropdown/checkbox types
}

/**
 * FileAttachment — POST-only.
 * Multipart/form-data upload with 15 mutually-exclusive parent reference fields.
 * HTTP 422 on quota exceeded (first endpoint we've seen using 422).
 *
 * Response surfaces 8 entity types Distru has but doesn't expose via GET:
 * Request, Task, StockTransfer, Return, OrderShipment, AgentChatThread,
 * AIOrderIntake, AIPurchaseIntake.
 */
export interface DistruFileAttachment {
    id: DistruId;
    name: string;
    mime_type: string;
    size_in_bytes: number;
    upload_datetime: DistruTimestamp;
    uploader: { id: DistruId; name: string };
    url: string;                           // /tmp/<uuid>/<filename> staging path; file on S3
    // Exactly one of the following 15 ref IDs is non-null:
    product_id: DistruId | null;
    order_id: DistruId | null;
    purchase_id: DistruId | null;
    invoice_id: DistruId | null;
    batch_id: DistruId | null;
    contact_id: DistruId | null;
    company_relationship_id: DistruId | null;  // Distru's internal name for Company
    assembly_id: DistruId | null;
    license_id: DistruId | null;
    request_id: DistruId | null;               // NEW hidden entity type — no GET endpoint
    task_id: DistruId | null;                  // NEW hidden entity type
    stock_transfer_id: DistruId | null;        // NEW hidden entity type
    return_id: DistruId | null;                // NEW hidden entity type
    order_shipment_id: DistruId | null;        // NEW hidden entity type
    agent_chat_thread_id: DistruId | null;     // NEW hidden entity type (AI workflows)
    ai_order_intake_id: DistruId | null;       // NEW hidden entity type (AI workflows)
    ai_purchase_intake_id: DistruId | null;    // NEW hidden entity type (AI workflows)
}
```

---

## Notes on Type Stability

- Field presence varies by tenant configuration; mark anything not in the core schema as **optional**.
- Custom fields are **always** an opaque key-value structure — never tighten to a known schema.
- "Enum" fields are sometimes tenant-customizable strings (Company.relationship_type, Company.category, Product.category, Adjustment.reason) — never treat them as closed sets.
- Distru may add fields without versioning. Keep types **forwards-compatible** by using `interface` (not `type`) and avoiding `exact` checks.
- **Distinguish read shape from write shape** for the same conceptual entity — they're not always identical (Product is_active vs is_inactive; product_group vs group_id; custom_data array vs object map).

## Cross-references

- Canonical mapping: `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md`
- Per-endpoint detail: `categories/*.md`
- Cross-cutting quirks: `SKILL.md` "Critical conventions" section
