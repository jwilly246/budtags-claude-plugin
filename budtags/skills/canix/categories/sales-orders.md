# Sales Orders

Sales orders represent outgoing orders from the Canix user's company to customers. This is the **seller perspective** — equivalent to LeafLink's `/orders-received/` endpoints.

## Endpoints (8 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/sales_orders` | List sales orders | Paginated, filterable |
| POST | `/sales_orders` | Create sales order | ⚠️ WRITE |
| GET | `/sales_orders/{id}` | Get single order | Includes embedded customer |
| PUT | `/sales_orders/{id}` | Update sales order | ⚠️ WRITE |
| GET | `/sales_orders/{id}/contents` | Get line items | Returns SalesOrderItem[] with weight_unit |
| GET | `/sales_orders/{id}/payments` | Get payments | Returns SalesOrderPayment[] |
| PUT | `/sales_orders/{id}/status/{status_name}` | Transition status | ⚠️ WRITE, no request body |

## Status Lifecycle

```
created → approved → filled → shipped → accepted → archived
                                                  → requested
           ↓ (any non-terminal)
         canceled
```

**Valid status values**: `created`, `approved`, `filled`, `shipped`, `accepted`, `archived`, `requested`, `canceled`

**Cancellation restriction**: Cannot cancel orders that are `shipped`, `accepted`, `returned`, or `archived`.

**Status transition endpoint**: `PUT /sales_orders/{id}/status/{status_name}`
- No request body needed — status is in the URL path
- Returns `{ previous_status, new_status }`

## SalesOrder Response Schema

```json
{
  "id": 84,
  "facility_id": 14,
  "name": "0000002062",
  "external_identifier": "SAP-ORDER-12345",
  "status": "created",
  "display_status": "Pending Review",
  "customer": { "id": 345, "contact_name": "John Smith", "company_name": "Zen Ltd", ... },
  "delivery_date": "2021-05-24T19:58:00.000Z",
  "delivery_fee": 2000,
  "payment_date": "2021-05-24T19:58:00.000Z",
  "payment_terms": "NET-14",
  "local_tax_rate": 0,
  "state_tax_rate": 0.27,
  "other_tax_rate": 0,
  "subtotal": 2124.22,
  "total_cultivation_tax": 0,
  "total_price": 2697.76,
  "total_paid": 100.00,
  "credits": 0,
  "discount": 0,
  "remaining_balance": 2597.76,
  "internal_notes": "",
  "contents": [
    {
      "id": 100,
      "weight": 20,
      "weight_unit": "Each",
      "weight_unit_id": 15,
      "weight_unit_name": "Each",
      "unit_price": 20,
      "total_price": 400,
      "item": { "id": 7036, "name": "Blue Dream - Trim", "sku": "22657" },
      "package_ids": [123, 456],
      "discount": { "type": "fixed", "amount": 10.0, "reason": "10$ off" },
      "updated_at": "2021-05-24T19:58:00.000Z",
      "order": 1
    }
  ],
  "payments": [
    { "date": "2021-05-24T19:58:00.000Z", "amount": 100 }
  ],
  "sales_representative": { "id": 123, "name": "John Doe", "email": "j@d.com" },
  "sales_order_credit": { "type": "percentage", "amount": 25.0, "reason": "25% off" },
  "invoice_url": "https://www.app.canix.com/sales/invoice/view/123456",
  "created_at": "2021-05-24T19:58:00.000Z",
  "updated_at": "2021-05-24T19:58:00.000Z"
}
```

### Key Fields

- **`customer`** — Embedded Customer object (id, contact_name, company_name, license, address)
- **`contents`** — Array of line items with item reference, quantities, prices, discounts
- **`payments`** — Array of payments with amount and date
- **`display_status`** — Custom status name if set, otherwise standard status value
- **`external_identifier`** — External ID from partner systems (not unique)
- **`sales_representative`** — User object with id, name, email
- **`sales_order_credit`** — Order-level discount/credit
- **`invoice_url`** — URL to the latest invoice (if exists)

## SalesOrderRequestBody (Create/Update)

```json
{
  "customer_id": 2,
  "name": "Order #123",
  "external_identifier": "BT-ORDER-001",
  "status": "created",
  "delivery_fee": 15.99,
  "delivery_date": "2025-02-04T14:00:00Z",
  "payment_date": "2025-02-04T14:00:00Z",
  "payment_terms": "Net 30",
  "local_tax_rate": 2.5,
  "state_tax_rate": 7.0,
  "other_tax_rate": 5.0,
  "internal_notes": "Handle with care",
  "sales_rep_email": "john.doe@example.com",
  "return_policy": "30-day return policy",
  "terms_and_conditions": "Standard terms apply",
  "sales_order_credit": { "type": "percentage", "amount": 25.0, "reason": "25% off" },
  "contents": [
    {
      "item_id": 123,
      "total_price": 25.99,
      "weight": 1.5,
      "weight_unit": "grams",
      "notes": "Special handling",
      "package_ids": [1, 2, 3],
      "discount": { "type": "fixed", "amount": 10.0, "reason": "10$ off" }
    }
  ],
  "payments": [
    { "amount": 100.00, "date": "2025-02-04", "reference_number": "PAY-123" }
  ]
}
```

**Required fields**: `customer_id`, `name`, `status`, `delivery_date`, `other_tax_rate`, `local_tax_rate`, `state_tax_rate`

**Content items**: Can reference `item_id` (cannabis) OR `non_cannabis_product_id` (NCI)

## Discount Object

Used at both order-level (`sales_order_credit`) and line-item-level (`discount`):

```json
{ "type": "fixed"|"percentage", "amount": 10.0, "reason": "Promo" }
```

## Common Queries

```php
// Fetch recent orders
$api->get('/sales_orders', [
    'where' => "updated_at >= '2024-01-01'",
    'order_by' => 'updated_at desc',
    'limit' => 2000,
]);

// Fetch orders by status
$api->get('/sales_orders', [
    'where' => "status IN ('created', 'approved', 'filled')",
]);

// Fetch specific order with full details
$order = $api->get("/sales_orders/{$id}");
// Customer, contents, and payments are embedded in response
```

## BudTags Mapping

| Canix Field | BudTags Field | Model |
|-------------|---------------|-------|
| `id` | `canix_order_id` | MarketplaceOrder |
| `name` | `order_number` | MarketplaceOrder |
| `status` | `status` (mapped) | MarketplaceOrder |
| `total_price` | `total` | MarketplaceOrder |
| `customer.id` | `customer_id` (via cache) | MarketplaceOrder |
| — | `source = 'canix'` | MarketplaceOrder |
| `contents[].id` | `canix_line_item_id` | MarketplaceOrderLineItem |
| `payments[].amount` | `amount` | OrderPayment |

---

**See:** `patterns/write-safety.md` for write operation precautions
**See:** `scenarios/sales-order-import-workflow.md` for complete import workflow
**See:** `scenarios/sales-order-writeback-workflow.md` for push-back workflow
