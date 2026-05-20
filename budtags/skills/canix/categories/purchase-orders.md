# Purchase Orders

Purchase orders represent incoming orders placed by the Canix user to vendors/suppliers. This is the **buyer perspective** — equivalent to LeafLink's `/buyer/orders/` endpoints.

## Endpoints (6 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/purchase_orders` | List purchase orders | Paginated, filterable |
| POST | `/purchase_orders` | Create purchase order | ⚠️ WRITE |
| GET | `/purchase_orders/{id}` | Get single PO | Includes embedded vendor |
| GET | `/purchase_orders/{id}/contents` | Get line items | Returns PurchaseOrderItem[] |
| GET | `/purchase_orders/{id}/payments` | Get payments | Returns PurchaseOrderPayment[] |

**Note**: No PUT or DELETE endpoints — purchase orders can only be created, not updated or deleted via API.

## Status Lifecycle

```
CREATED → RELEASED → REQUESTED → PARTIALLY_RECEIVED → RECEIVED → PAID → ARCHIVED
```

**Status values**: `CREATED`, `RELEASED`, `REQUESTED`, `PARTIALLY_RECEIVED`, `RECEIVED`, `PAID`, `ARCHIVED`

**Note**: Statuses are UPPERCASE (unlike sales order statuses which are lowercase).

## PurchaseOrder Response Schema

```json
{
  "id": 350,
  "facility_id": 1,
  "name": "PO 00001",
  "status": "CREATED",
  "vendor": {
    "id": 123,
    "name": "Canna Cones",
    "contact_name": "John Smith",
    "license_number": "X-000012",
    ...
  },
  "requested_delivery_date": "2021-06-07T07:00:00.000Z",
  "internal_notes": "Follow up",
  "payment_terms": "NET15",
  "payment_date": "2021-06-22",
  "delivery_fee": 1.50,
  "local_tax_rate": 0.01,
  "state_tax_rate": 0.01,
  "other_tax_rate": 0.01,
  "subtotal": 1500.00,
  "total_price": 1545.00,
  "total_paid": 500.00,
  "contents": [
    {
      "id": 13,
      "weight": 200,
      "weight_unit": "Grams",
      "total_price": 10.25,
      "item": { "id": 7036, "name": "Blue Dream - Trim", ... },
      "non_cannabis_product": null
    }
  ],
  "payments": [
    { "amount": 500.00, "date": "2025-02-04" }
  ],
  "created_at": "2021-05-24T19:58:00.000Z",
  "updated_at": "2018-11-06T08:00:00.000Z"
}
```

### Key Fields

- **`vendor`** — Embedded Vendor object (not Customer like sales orders)
- **`contents`** — Line items reference either `item` (cannabis) OR `non_cannabis_product` (NCI), never both
- **`payment_terms`** — Must start with `NET`, `COD`, `CONSIGNMENT`, or `PREPAYMENT`
- **`tax rates`** — Decimal format: 0.01 = 1% (enables excise_tax if > 0)

## CreatePurchaseOrderRequestBody

```json
{
  "facility_id": 1,
  "vendor_id": 123,
  "status": "CREATED",
  "requested_delivery_date": "2021-06-07",
  "payment_terms": "NET15",
  "name": "PO 00001",
  "internal_notes": "Follow up",
  "payment_date": "2021-06-22",
  "delivery_fee": 1.50,
  "local_tax_rate": 0.01,
  "state_tax_rate": 0.01,
  "other_tax_rate": 0.01,
  "purchase_order_items_attributes": [
    {
      "item_id": 7036,
      "weight": 200,
      "weight_unit_id": 15,
      "price": 10.25,
      "notes": "my notes for this order item"
    }
  ]
}
```

**Required fields**: `facility_id`, `vendor_id`, `status`, `requested_delivery_date`, `payment_terms`

**Payment terms pattern**: Must match `^(NET|COD|CONSIGNMENT|PREPAYMENT)`. Examples: `NET15`, `NET30`, `COD`, `PREPAYMENT`

**Line items key**: `purchase_order_items_attributes` (not `contents`) — requires `item_id`, `weight`, `weight_unit_id`, `price`

**Note**: `payment_date` is required if `payment_terms` is `PREPAYMENT`.

## PurchaseOrderItem vs SalesOrderItem

| Aspect | Sales Order Item | Purchase Order Item |
|--------|-----------------|---------------------|
| References | `item` only | `item` OR `non_cannabis_product` |
| Price field | `unit_price` + `total_price` | `total_price` only |
| Discount | Yes (Discount object) | No |
| Package IDs | Yes | No |
| Order position | Yes (`order` field) | No |

## Common Queries

```php
// Fetch recent purchase orders
$api->get('/purchase_orders', [
    'where' => "updated_at >= '2024-01-01'",
    'order_by' => 'id desc',
    'limit' => 2000,
]);

// Fetch PO with details
$po = $api->get("/purchase_orders/{$id}");
// Vendor, contents, and payments are embedded

// Get contents separately (same data as embedded)
$contents = $api->get("/purchase_orders/{$id}/contents");
```

## BudTags Mapping

| Canix Field | BudTags Field | Model |
|-------------|---------------|-------|
| `id` | `canix_order_id` | MarketplaceOrder |
| `name` | `order_number` | MarketplaceOrder |
| `status` | `status` (mapped) | MarketplaceOrder |
| `total_price` | `total` | MarketplaceOrder |
| `vendor.id` | `vendor_id` (via Vendor model) | MarketplaceOrder |
| — | `source = 'canix'` | MarketplaceOrder |
| — | buyer perspective flag | MarketplaceOrder |

---

**See:** `categories/crm.md` for vendor details and CRUD operations
**See:** `patterns/write-safety.md` for write operation precautions
