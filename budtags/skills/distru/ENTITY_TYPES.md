# Distru Entity Types

TypeScript type reference for entities returned by the Distru Public API v1. Organized by domain, mirroring the `categories/` structure.

> **Source-of-truth note:** Distru does not publish an OpenAPI spec, so these types are derived from observed responses and public documentation. As Phase B importers transcribe live samples, refine these definitions and keep them in sync.

---

## Core Types (shared primitives)

```ts
export type DistruId = string; // prefixed: "ord_...", "prd_...", "co_...", etc.
export type DistruTimestamp = string; // ISO 8601: "2026-05-16T14:42:00Z"
export type DistruDate = string;      // ISO 8601 date: "2026-05-16"

export interface DistruAddress {
    line_1: string;
    line_2?: string;
    city: string;
    state: string;
    postal_code: string;
    country?: string;
}

export interface DistruPaginatedResponse<T> {
    data: T[];
    next_page: number | null;
}

export interface DistruCustomFields {
    [key: string]: string | number | boolean | null;
}
```

---

## Sales Domain

```ts
export type DistruOrderStatus =
    | 'DRAFT'
    | 'CONFIRMED'
    | 'FULFILLED'
    | 'INVOICED'
    | 'PAID'
    | 'COMPLETED'
    | 'VOID';

export interface DistruOrderLineItem {
    id: DistruId;
    product_id: DistruId;
    batch_id?: DistruId;
    quantity: number;
    unit_price: number;
    subtotal: number;
    custom_fields?: DistruCustomFields;
}

export interface DistruCharge {
    label: string;
    amount: number;
}

export interface DistruOrder {
    id: DistruId;
    order_number: string;
    status: DistruOrderStatus;
    company_id: DistruId;
    billing_location_id?: DistruId;
    shipping_location_id?: DistruId;
    line_items: DistruOrderLineItem[];
    charges?: DistruCharge[];
    subtotal: number;
    total: number;
    due_datetime?: DistruTimestamp;
    completion_datetime?: DistruTimestamp;
    custom_fields?: DistruCustomFields;
    created_at: DistruTimestamp;
    updated_at: DistruTimestamp;
}

export interface DistruInvoicePayment {
    amount: number;
    method: string;        // 'ACH', 'Wire', 'Cash', etc.
    reference?: string;
    received_at: DistruTimestamp;
}

export interface DistruInvoice {
    id: DistruId;
    invoice_number: string;
    order_id: DistruId;
    company_id: DistruId;
    status: string;
    payments: DistruInvoicePayment[];
    subtotal: number;
    total: number;
    balance: number;
    created_at: DistruTimestamp;
    updated_at: DistruTimestamp;
}
```

---

## Purchasing Domain

```ts
export type DistruPurchaseStatus =
    | 'DRAFT'
    | 'CONFIRMED'
    | 'RECEIVED'
    | 'PAID'
    | 'COMPLETED'
    | 'VOID';

export interface DistruPurchaseLineItem {
    id: DistruId;
    product_id: DistruId;
    batch_id?: DistruId;
    quantity: number;
    unit_cost: number;
    subtotal: number;
}

export interface DistruPurchase {
    id: DistruId;
    purchase_number: string;
    status: DistruPurchaseStatus;
    company_id: DistruId; // vendor company
    line_items: DistruPurchaseLineItem[];
    payments: DistruInvoicePayment[];
    subtotal: number;
    total: number;
    received_datetime?: DistruTimestamp;
    custom_fields?: DistruCustomFields;
    created_at: DistruTimestamp;
    updated_at: DistruTimestamp;
}
```

---

## CRM Domain

```ts
export type DistruRelationshipType = 'CUSTOMER' | 'VENDOR' | 'CUSTOMER_AND_VENDOR' | 'NEITHER';

export interface DistruCompany {
    id: DistruId;
    name: string;
    dba?: string;
    license_number?: string;
    license_type?: string;
    relationship_type: DistruRelationshipType;
    category?: string;
    email?: string;
    phone?: string;
    billing_address?: DistruAddress;
    shipping_address?: DistruAddress;
    custom_fields?: DistruCustomFields;
    created_at: DistruTimestamp;
    updated_at: DistruTimestamp;
}

export interface DistruContact {
    id: DistruId;
    company_id: DistruId;
    name: string;
    role?: string;
    email?: string;
    phone?: string;
    custom_fields?: DistruCustomFields;
}
```

---

## Products Domain

```ts
export interface DistruPosMappings {
    blaze?: { product_id: string };
    dutchie?: { product_id: string };
    treez?: { product_id: string };
    [key: string]: { product_id: string } | undefined;
}

export interface DistruProduct {
    id: DistruId;
    name: string;
    sku: string;
    brand_id?: DistruId;
    brand_name?: string;
    category?: string;
    subcategory?: string;
    strain_id?: DistruId;
    strain_name?: string;
    unit_of_measure?: string;
    package_size?: number;
    price?: number;
    wholesale_price?: number;
    image_url?: string;
    pos_mappings?: DistruPosMappings;
    custom_fields?: DistruCustomFields;
    created_at: DistruTimestamp;
    updated_at: DistruTimestamp;
}

export interface DistruTestResultValue {
    field: string; // 'THC_PCT', 'CBD_PCT', 'PESTICIDE_MYCLOBUTANIL_PPB', etc.
    value: number | string | boolean;
    passed?: boolean;
}

export interface DistruTestResult {
    id: DistruId;
    batch_id: DistruId;
    lab_name?: string;
    sample_id?: string;
    tested_at: DistruTimestamp;
    values: DistruTestResultValue[];
    coa_url?: string;
}
```

---

## Inventory Domain

```ts
export interface DistruBatch {
    id: DistruId;
    product_id: DistruId;
    lot_number?: string;
    quantity_on_hand: number;
    unit_of_measure: string;
    location_id?: DistruId;
    received_at?: DistruTimestamp;
    expiration_date?: DistruDate;
    actual_cost?: number;   // only when include_costs=true
    default_cost?: number;  // only when include_costs=true
    custom_fields?: DistruCustomFields;
    test_result_ids?: DistruId[];
    created_at: DistruTimestamp;
    updated_at: DistruTimestamp;
}

export interface DistruPackage {
    id: DistruId;
    batch_id: DistruId;
    product_id: DistruId;
    metrc_package_tag?: string;
    quantity: number;
    unit_of_measure: string;
    location_id?: DistruId;
    status: string;
    created_at: DistruTimestamp;
    updated_at: DistruTimestamp;
}

export interface DistruStockAdjustment {
    id: DistruId;
    batch_id: DistruId;
    delta: number;
    reason: string;
    adjusted_by_user_id?: DistruId;
    adjusted_at: DistruTimestamp;
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

export interface DistruAssemblyBatchRef {
    batch_id: DistruId;
    quantity: number;
    unit_of_measure: string;
}

export interface DistruAssemblyWaste {
    amount: number;
    unit_of_measure: string;
    reason?: string;
}

export interface DistruAssembly {
    id: DistruId;
    completion_datetime: DistruTimestamp;
    creation_source: DistruAssemblyCreationSource;
    license_number?: string;
    input_batches: DistruAssemblyBatchRef[];
    output_batches: DistruAssemblyBatchRef[];
    waste?: DistruAssemblyWaste[];
    labor?: unknown[];        // shape not documented in public docs
    machine_info?: unknown;   // shape not documented
    custom_fields?: DistruCustomFields;
    created_at: DistruTimestamp;
    updated_at: DistruTimestamp;
}
```

---

## System Domain

```ts
export type DistruLocationType = 'WAREHOUSE' | 'FACILITY' | 'RETAIL' | string;

export interface DistruLocation {
    id: DistruId;
    name: string;
    address?: DistruAddress;
    license_number?: string;
    location_type: DistruLocationType;
    created_at: DistruTimestamp;
    updated_at: DistruTimestamp;
}

export interface DistruCustomField {
    id: DistruId;
    name: string;
    entity_type: string; // 'Order', 'Product', 'Company', etc.
    field_type: 'string' | 'number' | 'boolean' | 'date' | 'select';
    options?: string[];
}

export interface DistruUser {
    id: DistruId;
    name: string;
    email: string;
    role?: string;
}

export interface DistruRole {
    id: DistruId;
    name: string;
    permissions?: string[];
}

export interface DistruPaymentMethod {
    id: DistruId;
    name: string; // 'ACH', 'Wire', 'Cash', 'Check'
}
```

---

## Notes on Type Stability

- Field presence varies by tenant configuration; mark anything not in the core schema as **optional**.
- Custom fields are **always** an opaque key-value map in TypeScript — never tighten to a known schema.
- Distru may add fields without versioning. Keep types **forwards-compatible** by using `interface` (not `type`) and avoiding `exact` checks.
