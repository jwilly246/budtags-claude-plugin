# LeafLink Entity Types Reference

TypeScript type definitions for all LeafLink Marketplace entities used in BudTags frontend.

## Core Types

### LeafLinkOrder

```typescript
export interface LeafLinkOrder {
    id: number;
    number: string;                  // Order number (unique identifier)
    status: 'draft' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
    customer: LeafLinkCustomer;      // Customer who placed order
    seller: LeafLinkCompany;         // Seller company
    total: number;                   // Total order amount
    subtotal: number;                // Subtotal before tax
    tax_total: number;               // Total tax amount
    discount_total: number;          // Total discounts applied
    created_date: string;            // ISO 8601 datetime
    modified: string;                // ISO 8601 datetime
    order_date: string;              // ISO 8601 date
    delivery_date: string | null;   // Requested delivery date
    shipped_date: string | null;    // Actual ship date
    delivery_address: Address | null;
    notes: string | null;
    line_items: LeafLinkLineItem[];
    payments: LeafLinkPayment[];
    sales_reps: LeafLinkSalesRep[];
}
```

### LeafLinkLineItem

```typescript
export interface LeafLinkLineItem {
    id: number;
    order: number;                   // Order ID
    product: number;                 // Product ID
    product_name: string;
    quantity: number;
    unit_price: number;
    total: number;                   // quantity * unit_price
    discount_percent: number | null;
    discount_amount: number | null;
    tax_percent: number | null;
    tax_amount: number | null;
    notes: string | null;
}
```

### LeafLinkProduct

```typescript
export interface LeafLinkProduct {
    id: number;
    seller: number;                  // Seller company ID
    brand: number | null;            // Brand ID
    brand_name?: string;             // Enriched field
    category: number;                // Category ID
    category_name?: string;          // Enriched field
    sub_category: number | null;     // Subcategory ID
    subcategory_name?: string;       // Enriched field
    product_line: number | null;     // Product line ID
    product_line_name?: string;      // Enriched field
    name: string;                    // Product name
    display_name: string;            // Display name (may include variant info)
    sku: string;                     // SKU code
    unit_price: number;
    unit_denomination: 'each' | 'gram' | 'ounce' | 'pound' | 'kilogram';
    inventory_quantity: number;      // Available quantity
    min_order_quantity: number | null;
    max_order_quantity: number | null;
    description: string | null;
    images: LeafLinkProductImage[];
    batches: LeafLinkBatch[];
    strain: number | null;           // Strain ID
    active: boolean;
    created_on: string;              // ISO 8601 datetime
    modified: string;                // ISO 8601 datetime
}
```

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
    name: string;
    email: string | null;
    phone: string | null;
    address: Address | null;
    city: string | null;
    state: string | null;
    zip_code: string | null;
    customer_status: number | null;  // Customer status ID
    customer_tier: number | null;    // Customer tier ID
    licenses: LeafLinkLicense[];
    contacts: LeafLinkContact[];
    created_date: string;            // ISO 8601 datetime
    modified: string;                // ISO 8601 datetime
}
```

### LeafLinkContact

```typescript
export interface LeafLinkContact {
    id: number;
    customer: number;                // Customer ID
    first_name: string;
    last_name: string;
    email: string | null;
    phone: string | null;
    title: string | null;
    is_primary: boolean;
}
```

### LeafLinkCompany

```typescript
export interface LeafLinkCompany {
    id: number;
    name: string;
    company_type: 'seller' | 'buyer';
    email: string | null;
    phone: string | null;
    address: Address | null;
    city: string | null;
    state: string | null;
    zip_code: string | null;
    website: string | null;
    licenses: LeafLinkLicense[];
    brands: LeafLinkBrand[];
    created_on: string;
    modified: string;
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
    address: Address;
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
    order: number;                   // Order ID
    amount: number;
    payment_method: 'cash' | 'check' | 'wire' | 'ach' | 'credit_card';
    payment_date: string;            // ISO 8601 date
    reference_number: string | null;
    notes: string | null;
}
```

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

### Address

```typescript
export interface Address {
    street: string;
    street2?: string | null;
    city: string;
    state: string;                   // State abbreviation
    zip_code: string;
    country?: string;                // Default: 'US'
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
                <div key={order.id}>
                    <h3>Order #{order.number}</h3>
                    <p>Customer: {order.customer.name}</p>
                    <p>Status: {order.status}</p>
                    <p>Total: ${order.total.toFixed(2)}</p>
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
        typeof obj.id === 'number' &&
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
        typeof obj.unit_price === 'number'
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
- `CODE_EXAMPLES.md` - Usage examples with these types
