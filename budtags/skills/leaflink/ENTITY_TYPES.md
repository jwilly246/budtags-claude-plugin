# LeafLink Entity Types Reference

TypeScript type definitions for all LeafLink Marketplace entities used in BudTags frontend.

## Core Types

Field names below are checked against the official spec (`official_openapi.json`: ProductResponse, OrderResponse, LineItemResponse, CustomerResponse, Contact, CompanyResponse). Behaviour notes tagged "verified 2026-10-16 (sandbox, <file>)" come from `patterns/verified-behavior.md`, which wins on behaviour.

### Shared money object

```typescript
export interface LeafLinkMoney {
    amount: number;                  // reads as a number (300.0); send a string "300.00"
    currency: string;                // 'USD'
}
```

### LeafLinkOrder

Orders have no `id`; the key is `number` (uuid). `fields_include=id` on `/orders-received/` returns 400 (verified 2026-10-16 (sandbox, r2_t9_pagination.txt)).

```typescript
export interface LeafLinkOrder {
    number: string;                  // uuid, read-only, the order key
    short_id: string;                // "Order No." in the UI; = external_id_seller when one is sent on create
    external_id_seller: string | null;  // create-only
    external_id_buyer: string | null;
    created_on: string;              // ISO 8601, Mountain offset (-06:00/-07:00)
    modified: string;
    seller: number;                  // company id
    buyer: number | null;
    customer: { id: number; display_name: string; ext_acct_id: string | null; delinquent: boolean };
    brand: number | null;
    status: 'Draft' | 'Submitted' | 'Accepted' | 'Backorder' | 'Fulfilled'
          | 'Shipped' | 'Complete' | 'Rejected' | 'Combined' | 'Cancelled';
    available_transitions: string[]; // read-only, e.g. ['accepted','cancelled','rejected']
    manual: boolean;
    discount: number;                // with discount_type '%': a 0-1 fraction (0.3 = 30%)
    discount_type: '%' | '$';        // sending the type alone re-reads the stored value
    tax_amount: number;              // a 0-1 rate (0.24)
    tax_type: '%';                   // '%' only; '$' is refused
    final_tax: string;               // tax total = rate x (lines + shipping), before discount
    shipping_charge: LeafLinkMoney;
    total: LeafLinkMoney;
    payment_balance: string;         // read-only (reads as a number in practice)
    credits: string;                 // read-only
    selected_payment_option: object | null;  // {payment_term_id, payment_method_id} on write
    payment_term: string | null;     // deprecated, read-only
    payment_due_date: string | null; // datetime; send YYYY-MM-DDT17:00:00Z
    ship_date: string | null;        // datetime; send YYYY-MM-DDT17:00:00Z
    paid: boolean;                   // cannot be PATCHed; set by a full payment
    paid_date: string | null;        // plain date YYYY-MM-DD
    shipping_details: string | null;
    notes: string | null;
    internal_notes: string | null;
    delivery_preferences: string | null;
    sales_reps: object[];            // read-only on the response
    corporate_address: object;       // read-only, as given at order creation
    delivery_address: object;        // read-only, as given at order creation
    external_ids: { [key: string]: string };
    line_items?: LeafLinkLineItem[]; // returned on /orders-received/ even without include_children
}
```

- Tax = `tax_amount` x (line subtotal + shipping), BEFORE discount; the discount comes off the lines only. verified 2026-10-16 (sandbox, r2_t2_shipping_tax.txt)
- `discount_type` alone flips the meaning of the stored `discount` (10 `$` became 1000%). Always send both. verified 2026-10-16 (sandbox, w_d_discount_tax.txt)
- `paid` PATCH -> 400 "Forbidden fields in update operation"; an exact-balance payment sets `paid` + `paid_date`. verified 2026-10-16 (sandbox, w_e_payments.txt)
- Reject on a Shipped order clears `ship_date` and `payment_due_date`. verified 2026-10-16 (sandbox, r3_i_reject_shipped_paid.txt)
- Spec on `payment_due_date`: "It is best practice to include a time (e.g. 2024-01-15T17:00:00Z). If a time is not provided, it will default to the server's time zone which is UTC."

### LeafLinkLineItem

```typescript
export interface LeafLinkLineItem {
    id: number;
    order: string;                   // order number (uuid)
    product: number;                 // listing id
    quantity: string;                // decimal string, in LISTING UNITS (not cases)
    bulk_units: number;              // quantity / unit_multiplier (cases)
    unit_multiplier: number;         // not accepted on LineItemUpdate
    unit_of_measure: string;         // read-only
    ordered_unit_price: LeafLinkMoney;  // per SOLD-IN unit (per case when multiplier > 1)
    sale_price: LeafLinkMoney;       // per sold-in unit; 0.00 = not on sale
    on_sale: boolean;                // read-only, derived from sale_price > 0
    is_sample: boolean;
    notes: string | null;
    is_packed: boolean;
    position: number | null;
    batch: number | null;
    package_tags: string[];          // read-only
    frozen_data: object;             // product snapshot at order time
}
```

- Clear a sale with `sale_price: {"amount": "0.00", "currency": "USD"}`; `null` -> 400, `on_sale` -> 400 (forbidden field). An on-sale line keeps billing the sale price when `ordered_unit_price` changes. verified 2026-10-16 (sandbox, w_a_sale_price.txt)
- A line sent with `sale_price` = ordered price reads `on_sale: true`; send 0 when the line is not on sale. verified 2026-10-16 (sandbox, w_b_inventory.txt)
- Line quantity 28 at multiplier 28 = `bulk_units` 1, billed at 1 x `ordered_unit_price`. verified 2026-10-16 (sandbox, w_b_inventory.txt)
- Order PATCH `line_items` is an upsert by `id`: an entry without `id` adds a new line. Delete with `DELETE /line-items/{id}/`. verified 2026-10-16 (sandbox, r2_t1_line_semantics.txt, r3_c_line_delete.txt)

### LeafLinkProduct

> **`unit_of_measure` and `unit_denomination` are TWO fields.** Store both. Never send one without the other and the price/multiplier. `unit_denomination` is WRITTEN as an integer id (11 = "28"); `"Gram"` or `"28"` -> 400 "Value must be id of an existing UnitDenomination." Id table: `patterns/verified-behavior.md`. verified 2026-10-16 (sandbox, w_c_units.txt)

```typescript
export interface LeafLinkProduct {
    id: number;
    seller: number;                  // company id
    manufacturer: number | null;     // company id
    brand: number | null;
    product_line: number | null;
    category: number;
    sub_category: number | null;     // must belong to category (400 otherwise)
    parent: { id: number } | null;   // set on varieties (child products)
    children_count: string;
    name: string;
    display_name: string;            // parent name + name for varieties
    sku: string;
    description: string | null;
    license: { id: number; number: string; type: string; classification: string } | null;

    // Unit group: send together
    unit_of_measure: 'Milligram' | 'Gram' | 'Kilogram' | 'Ounce' | 'Pound' | 'Unit' | 'Liter' | 'Milliliter';
    unit_denomination: { id: number; value: string; name: string; label: string };  // read; write the integer id
    unit_multiplier: number;         // units per case; 1 if not sold in cases
    sell_in_unit_of_measure: 'Case' | null;  // cleared only by null or ""
    base_units_per_unit: string;     // decimal; base unit by category (grams for carts, concentrates,
                                     // flower, pre-rolls; mg of cannabinoids for topicals, edibles)

    // Inventory: decimal strings, counted in LISTING UNITS (1 unit = denomination x unit_of_measure)
    quantity: string;
    reserved_qty: string;            // sum of open Submitted/Accepted/Backorder line quantities
    available_inventory: number | string;   // quantity - reserved_qty; writable on PATCH
    inventory_management: '1' | '2' | '3';  // 1 Managed, 2 Unlimited, 3 Inherited
    show_quantity: boolean;

    // Prices: money objects, per sold-in unit (per case when unit_multiplier > 1)
    wholesale_price: LeafLinkMoney;
    sale_price: LeafLinkMoney;
    retail_price: LeafLinkMoney;     // MSRP
    discount_percent: number;

    minimum_order: string;
    maximum_order: string | null;    // key REQUIRED on create; send null for no maximum

    listing_state: 'Available' | 'Archived' | 'Sample' | 'Backorder' | 'Internal' | 'Unavailable';
    display_listing_state: string;

    strain_classification: 'sativa' | 'indica' | 'hybrid' | 'na' | '11-cbd' | 'high-cbd'
                         | 'sativa-hybrid' | 'indica-hybrid';
    strains: number[] | { id: number; name: string; strain_classification: string }[];
                                     // write int[]; read objects with include_children=strains
    product_data_items: {
        spec_type: string;           // thc, cbd, total-thc, ...
        dosage_unit: 'mg' | '%' | null;
        decimal_value: string | null;
        max_decimal_value: string | null;
        text_value: string | null;
    }[];

    // Thresholds (flip listing_state on quantity changes)
    threshold_value: number;
    threshold_action: 'default' | 'backorder' | 'unavailable' | 'internal';
    reverse_threshold_value: number | null;
    reverse_threshold_action: string;        // 'default' | 'available'
    should_alert_on_low_inventory?: boolean;  // not in the spec; seen on reads
    low_inventory_alert_threshold?: string;   // not in the spec; seen on reads

    external_ids: { [key: string]: string }; // values up to 36 chars
    image_count: string;
    created_on: string;
    last_edit: string;               // "last edited by a user"
    modified: string;                // "product data was last modified"
}
```

- PATCH is partial: omitted fields are kept, `unit_multiplier` is not reset when omitted, and multiplier 1 alone keeps `sell_in_unit_of_measure: "Case"`. verified 2026-10-16 (sandbox, w_c_units.txt, w_c_sellin_clear.txt)
- `strains` is a whole-list replace (`[]` clears, omitted keeps). verified 2026-10-16 (sandbox, w_h_strains.txt). Spec: `product_data_items` "will replace any existing product data items".
- Quantity 140 on a Gram / 28 / multiplier 28 listing = 140 units of 28 g; one order line of quantity 28 = 1 case. verified 2026-10-16 (sandbox, w_b_inventory.txt, w_c_units.txt)
- Thresholds: quantity at or below `threshold_value` -> the action's state; above `reverse_threshold_value` -> Available; the PATCH response already shows it. verified 2026-10-16 (sandbox, r2_t3_thresholds.txt, r3_g_threshold_response.txt)
- `modified` and `last_edit` both move on API price and quantity edits; order-driven inventory changes did not move `modified`. verified 2026-10-16 (sandbox, w_c_units.txt, w_b_inventory.txt)
- Listings cannot be deleted; archive with `listing_state: "Archived"`.

### LeafLinkProductImage

```typescript
export interface LeafLinkProductImage {
    id: number;
    product: number;                 // Product ID
    image_url: string;
    thumbnail_url: string | null;
    is_primary: boolean;
    display_order: number;
}
```

### LeafLinkBatch

```typescript
export interface LeafLinkBatch {
    id: number;
    product: number;                 // Product ID
    batch_number: string;
    quantity: number;
    unit: string;
    harvest_date: string | null;    // ISO 8601 date
    test_date: string | null;        // ISO 8601 date
    test_results: {
        thc_percent?: number;
        cbd_percent?: number;
        total_cannabinoids?: number;
        terpenes?: { [key: string]: number };
    } | null;
    documents: LeafLinkBatchDocument[];
    created_on: string;
    modified: string;
}
```

### LeafLinkBatchDocument

```typescript
export interface LeafLinkBatchDocument {
    id: number;
    batch: number;                   // Batch ID
    document_type: 'coa' | 'msds' | 'other';  // Certificate of Analysis, Material Safety Data Sheet
    document_url: string;
    uploaded_date: string;           // ISO 8601 datetime
}
```

### LeafLinkCustomer

```typescript
export interface LeafLinkCustomer {
    id: number;
    owner: number;                   // seller company this record belongs to
    partner: number | null;          // read-only: linked LeafLink buyer company
    name: string;
    nickname: string | null;
    dba: string | null;
    license_number: string | null;   // filter is exact AND case-sensitive
    license_type: number | null;
    ein: string | null;              // read-only (inherited from the buyer company)
    email: string | null;
    phone: string | null;
    phone_extension: string | null;
    address: string | null;          // top-level address mirrors delivery_address
    unit_number: string | null;
    city: string | null;
    county: string | null;
    state: string | null;
    zipcode: string | null;
    country: string | null;
    corporate_address: LeafLinkAddress;
    delivery_address: LeafLinkAddress;
    archived: boolean;
    delinquent: boolean;
    status: number | null;           // customer status id
    tier: number | null;             // customer tier id
    managers: number[];              // sales rep ids
    available_payment_options: object[];
    payment_term: number | null;     // deprecated
    discount_percent: string | null;
    shipping_charge: string | null;
    delivery_preferences: string | null;
    external_id: string | null;
    external_ids: { [key: string]: string };
    created_on: string;
    modified: string;
}
```

- PATCH is partial. A top-level `address`/`city`/`zipcode` PATCH overwrites BOTH `corporate_address` and `delivery_address`; a partial nested object (`{"corporate_address": {"city": "Warren"}}`) blanks the rest of that address. Send full nested objects. verified 2026-10-16 (sandbox, g_customers.txt)
- `archived: false` un-archives; never send `archived` unless you mean it. `ein` on PATCH is ignored (reads null). verified 2026-10-16 (sandbox, g_customers.txt)
- Contacts come from `/customers/?include_children=contacts`; there is no `customer` field on a contact.

### LeafLinkContact

```typescript
export interface LeafLinkContact {
    id: number;                      // read-only
    owner: number;                   // required on create
    first_name: string;              // required, max 30
    last_name: string | null;        // max 30
    email: string | null;
    secondary_email: string | null;
    role: string | null;
    description: string | null;
    phone: string | null;            // write 10 bare digits: "3135550100"
    phone_extension: string | null;
    secondary_phone: string | null;
    secondary_phone_extension: string | null;
    delete: boolean;                 // true = deleted; the row stays
    created_on: string;
    modified: string;
}
```

- `phone` must be 10 bare digits; `(313) 555-0100`, `+13135550100` and `313.555.0100` -> 400. `first_name` over 30 chars -> 400. verified 2026-10-16 (sandbox, r2_t12_contact_patch.txt)
- DELETE sets `delete: true`; the default `/contacts/` list INCLUDES deleted rows. Filter with `delete=false`. verified 2026-10-16 (sandbox, r2_t8_contacts.txt)

### LeafLinkCompany

There is no `company_type`. Use the `seller` / `buyer` booleans.

```typescript
export interface LeafLinkCompany {
    id: number;
    name: string;
    dba: string | null;
    slug: string;
    seller: boolean;                 // sells on the marketplace
    buyer: boolean;                  // buys on the marketplace
    address: string | null;
    city: string | null;
    state: string | null;
    zipcode: string | null;
    description: string | null;
    image: string | null;
    business_identifier: string | null;
    business_license_name: string | null;
    batch_enabled: boolean;
    has_accting: boolean;            // QuickBooks Online enabled
    sts_enabled: boolean;            // Metrc integration enabled
}
```

### LeafLinkBrand

```typescript
export interface LeafLinkBrand {
    id: number;
    company: number;                 // Company ID
    name: string;
    logo_url: string | null;
    description: string | null;
    website: string | null;
}
```

### LeafLinkLicense

```typescript
export interface LeafLinkLicense {
    id: number;
    company: number;                 // Company ID
    license_number: string;
    license_type: number;            // License type ID
    license_type_name?: string;
    state: string;                   // State abbreviation (e.g., 'CA', 'CO')
    status: 'active' | 'inactive' | 'pending' | 'expired';
    issue_date: string | null;       // ISO 8601 date
    expiration_date: string | null;  // ISO 8601 date
}
```

### LeafLinkLicenseType

```typescript
export interface LeafLinkLicenseType {
    id: number;
    name: string;                    // e.g., 'Retail', 'Cultivation', 'Manufacturing'
    description: string | null;
}
```

### LeafLinkInventoryItem

```typescript
export interface LeafLinkInventoryItem {
    id: number;
    product: number;                 // Product ID
    facility: number | null;         // Facility ID
    quantity: number;
    unit: string;
    last_updated: string;            // ISO 8601 datetime
}
```

### LeafLinkFacility

```typescript
export interface LeafLinkFacility {
    id: number;
    company: number;                 // Company ID
    name: string;
    address: LeafLinkAddress;
    license: number | null;          // License ID
}
```

### LeafLinkRetailerInventory

```typescript
export interface LeafLinkRetailerInventory {
    id: number;
    company: number;                 // Company ID
    source: string;                  // POS system name (e.g., 'BioTrack', 'METRC')
    name: string;                    // Product name from POS
    sku: string;                     // SKU from POS
    brand: string;                   // Brand name
    quantity: number;
    unit_of_measure: string;
    is_low: boolean;                 // Is inventory running low?
    created_on: string;
    modified: string;
}
```

### LeafLinkPayment

```typescript
export interface LeafLinkPayment {
    id: number;
    order: string;                   // order number (uuid)
    recorded_by: number;             // company staff id
    recorder_name: string;           // read-only
    total: LeafLinkMoney;
    payment_date: string;            // datetime; send YYYY-MM-DDT17:00:00Z
    payment_type: 'other' | 'cash' | 'check' | 'credit' | 'trade' | 'ach' | 'wire' | 'cashier';
    reason: string | null;
    created_on: string;
    modified: string;
}
```

- `POST /order-payments/` is NOT idempotent (same body twice = two payments); overpaying -> 400 "You cannot overpay for an invoice."; payments are accepted on Cancelled and Rejected orders. verified 2026-10-16 (sandbox, w_e_payments.txt, r2_t15_transitions.txt)
- List one order's payments with `/orders-received/{number}/payments/`; `order=` and `modified__gte` on `/order-payments/` are ignored. verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)

### LeafLinkSalesRep

```typescript
export interface LeafLinkSalesRep {
    id: number;
    order: number;                   // Order ID
    sales_rep: number;               // Company staff ID
    sales_rep_name: string;
    commission_percent: number | null;
}
```

### LeafLinkActivityEntry

```typescript
export interface LeafLinkActivityEntry {
    id: number;
    customer: number;                // Customer ID
    entry: string;                   // Activity description
    date: string;                    // ISO 8601 datetime
    created_by: number | null;       // Staff member ID
    modified: string;
}
```

### LeafLinkPromoCode

```typescript
export interface LeafLinkPromoCode {
    id: number;
    code: string;
    discount_type: 'percentage' | 'fixed_amount';
    discount_value: number;
    start_date: string;              // ISO 8601 date
    end_date: string;                // ISO 8601 date
    max_uses: number | null;
    current_uses: number;
    active: boolean;
    created_on: string;
    modified: string;
}
```

### LeafLinkStrain

```typescript
export interface LeafLinkStrain {
    id: number;
    name: string;
    strain_type: 'indica' | 'sativa' | 'hybrid';
    description: string | null;
    genetics: string | null;
    effects: string[] | null;
}
```

### LeafLinkProductCategory

```typescript
export interface LeafLinkProductCategory {
    id: number;
    name: string;                    // e.g., 'Flower', 'Concentrates', 'Edibles'
    description: string | null;
}
```

### LeafLinkProductSubcategory

```typescript
export interface LeafLinkProductSubcategory {
    id: number;
    category: number;                // Category ID
    name: string;                    // e.g., 'Vape Cartridges', 'Gummies'
    description: string | null;
}
```

### LeafLinkProductLine

```typescript
export interface LeafLinkProductLine {
    id: number;
    company: number;                 // Company ID
    name: string;                    // e.g., 'Premium Reserve', 'Budget Line'
    description: string | null;
}
```

## Shared Types

### LeafLinkAddress

```typescript
export interface LeafLinkAddress {
    address: string;
    unit_number: string;
    city: string;
    county: string;
    state: string | null;            // state abbreviation
    zipcode: string;
}
```

## API Response Types

### Paginated Response

```typescript
export interface LeafLinkPaginatedResponse<T> {
    count: number;                   // Total number of results
    next: string | null;             // Next page URL
    previous: string | null;         // Previous page URL
    results: T[];                    // Array of results
}
```

### Error Response

```typescript
export interface LeafLinkErrorResponse {
    detail?: string;                 // General error message
    [field: string]: string | string[];  // Field-specific errors
}
```

## Usage Examples

### In React Components

```typescript
import type { LeafLinkOrder, LeafLinkProduct, LeafLinkCustomer } from '@/Types/types-leaflink';

export default function OrdersPage() {
    const { orders } = usePage<{
        orders: LeafLinkPaginatedResponse<LeafLinkOrder>
    }>().props;

    return (
        <div>
            {orders.results.map(order => (
                <div key={order.number}>
                    <h3>Order #{order.number}</h3>
                    <p>Customer: {order.customer.display_name}</p>
                    <p>Status: {order.status}</p>
                    <p>Total: ${order.total.amount.toFixed(2)}</p>
                </div>
            ))}
        </div>
    );
}
```

### In Inertia Controllers

```php
return Inertia::render('Leaflink/Orders', [
    'orders' => $orders,  // Laravel Paginator automatically serializes
    'customers' => $customers,
    'products' => $products
]);
```

### Type Guards

```typescript
export function isLeafLinkOrder(obj: any): obj is LeafLinkOrder {
    return (
        typeof obj === 'object' &&
        obj !== null &&
        typeof obj.number === 'string' &&
        typeof obj.status === 'string'
    );
}

export function isLeafLinkProduct(obj: any): obj is LeafLinkProduct {
    return (
        typeof obj === 'object' &&
        obj !== null &&
        typeof obj.id === 'number' &&
        typeof obj.display_name === 'string' &&
        typeof obj.unit_of_measure === 'string'
    );
}
```

## Complete Type File Location

All LeafLink types should be defined in:
```
resources/js/Types/types-leaflink.tsx
```

**Note:** Follow the same pattern as `types-metrc.tsx` - centralized type definitions, never duplicate types across files.

---

**See Also:**
- `types-metrc.tsx` - Metrc API types
- `types-qbo.tsx` - QuickBooks types
- `patterns/verified-behavior.md` - sandbox-proven write and read behaviour
