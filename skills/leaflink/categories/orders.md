# Orders - LeafLink API Category

Complete reference for order management endpoints - 21 total operations.

---

## Collection Reference

**OpenAPI Schema:** `schemas/openapi-orders.json`
**Total Endpoints:** 21
**Company Compatibility:**
- Seller companies: Use `/orders-received/*` endpoints
- Buyer companies: Use `/buyer/orders/*` endpoints

---

## Endpoint Overview

### GET Endpoints (List & Retrieve)

| Endpoint | Description | Company Type |
|----------|-------------|--------------|
| `GET /orders-received/` | List all received orders (seller) | Seller only |
| `GET /orders-received/{id}/` | Get order details | Seller only |
| `GET /buyer/orders/` | List buyer's placed orders | Buyer only |
| `GET /line-items/` | List line items | Both |
| `GET /line-items/{id}/` | Get line item details | Both |
| `GET /order-payments/` | List order payments | Both |
| `GET /order-payments/{id}/` | Get payment details | Both |
| `GET /order-sales-reps/` | List sales rep assignments | Both |
| `GET /order-sales-reps/{id}/` | Get sales rep assignment | Both |
| `GET /order-event-logs/` | List order event history | Both |
| `GET /order-event-logs/{id}/` | Get event log details | Both |

### POST Endpoints (Create)

| Endpoint | Description | Company Type |
|----------|-------------|--------------|
| `POST /orders-received/` | Create new order | Seller only |
| `POST /line-items/` | Add line item to order | Both |
| `POST /order-payments/` | Record payment | Both |
| `POST /order-sales-reps/` | Assign sales rep to order | Both |
| `POST /orders-received/{id}/transition/{action}/` | Transition order status | Seller only |

### PATCH Endpoints (Update)

| Endpoint | Description | Company Type |
|----------|-------------|--------------|
| `PATCH /orders-received/{id}/` | Update order | Seller only |
| `PATCH /line-items/{id}/` | Update line item | Both |

### DELETE Endpoints (Remove)

| Endpoint | Description | Company Type |
|----------|-------------|--------------|
| `DELETE /orders-received/{id}/` | Delete order | Seller only |
| `DELETE /line-items/{id}/` | Remove line item | Both |
| `DELETE /order-sales-reps/{id}/` | Remove sales rep assignment | Both |

---

## Common Use Cases

### 1. Fetch Orders with Filters

```php
// Get confirmed orders from January 2025
$orders = $api->get_orders(
    page: 1,
    status: 'confirmed',
    path: '/leaflink/orders',
    extraParams: [
        'created_date__gte' => '2025-01-01',
        'created_date__lte' => '2025-01-31',
        'customer' => 123  // Optional: filter by customer
    ]
);
```

### 2. Get Order Details

```php
// Fetch single order with full details
$response = $api->get_order($orderId);
$order = $response->json();

// Get line items for order
$lineItems = $api->get_order_line_items($orderId);
```

### 3. Transition Order Status

```php
// Transition order through lifecycle
$response = $api->transition_order(
    orderNumber: '12345',
    action: 'accept'  // 'accept', 'confirm', 'ship', 'deliver', 'cancel'
);

if ($response->successful()) {
    LogService::store(
        'LeafLink Order Transitioned',
        "Order #{$orderNumber} transitioned to {$action}"
    );
}
```

### 4. Update Order

```php
// Update order details
$response = $api->patch("/orders-received/{$orderId}/", [
    'delivery_date' => '2025-02-01',
    'notes' => 'Rush delivery requested'
]);
```

### 5. Add Line Item to Order

```php
// Add product to existing order
$response = $api->post('/line-items/', [
    'order' => $orderId,
    'product' => $productId,
    'quantity' => 10,
    'unit_price' => 25.00
]);
```

---

## Order Status Lifecycle

**For Seller Companies (`/orders-received/`):**
1. `draft` - Order created but not yet confirmed
2. `confirmed` - Order confirmed, ready to fulfill
3. `shipped` - Order shipped to buyer
4. `delivered` - Order received by buyer
5. `canceled` - Order canceled

**Transition Actions:**
- `accept` - Draft → Confirmed
- `confirm` - Draft → Confirmed (alternative)
- `ship` - Confirmed → Shipped
- `deliver` - Shipped → Delivered
- `cancel` - Any status → Canceled

---

## Available Filters

### Date Filters
- `created_date__gte`, `created_date__lte` - Order creation range
- `delivery_date__gte`, `delivery_date__lte` - Delivery date range
- `modified__gte`, `modified__lte` - Last modified range
- `shipped_date__gte`, `shipped_date__lte` - Ship date range

### Status Filters
- `status` - Single status exact match
- `status__in` - Multiple statuses (comma-separated)

### Relationship Filters
- `customer` - Filter by customer ID
- `sales_rep` - Filter by sales rep ID
- `product` - Filter line items by product (use on `/line-items/`)

### Numeric Filters
- `total__gte`, `total__lte` - Order total range
- `number` - Order number exact match

---

## Important Notes

### Company Scoping (CRITICAL!)

**Seller Companies:**
- Use `/orders-received/*` endpoints
- See incoming orders FROM buyers
- Can transition, update, and manage orders

**Buyer Companies:**
- Use `/buyer/orders/*` endpoints
- See outgoing orders TO sellers
- Limited management capabilities

**Common Mistake:**
```php
// ❌ Wrong: Buyer trying to access seller endpoint
$api->get('/orders-received/');  // Returns empty or 403

// ✅ Correct: Buyer using buyer endpoint
$api->get('/buyer/orders/');
```

### Trailing Slash Required

```php
// ❌ Wrong
$api->get('/orders-received')

// ✅ Correct
$api->get('/orders-received/')
```

### Line Items Are Separate

Line items are a separate resource with their own endpoints:
- List all: `GET /line-items/`
- Get one: `GET /line-items/{id}/`
- Create: `POST /line-items/`
- Update: `PATCH /line-items/{id}/`
- Delete: `DELETE /line-items/{id}/`

---

## Related Resources

- **Scenarios:** `scenarios/order-workflow.md` - Complete order lifecycle workflow
- **Patterns:** `patterns/company-scoping.md` - Understanding seller vs buyer context
- **Patterns:** `patterns/filtering.md` - Advanced filtering techniques
- **Patterns:** `patterns/pagination.md` - Handling large order lists
- **Schema:** `schemas/openapi-orders.json` - Full endpoint specifications

---

## Quick Reference

```php
// List orders
$orders = $api->get_orders(1, 'confirmed', '/leaflink/orders');

// Get single order
$order = $api->get_order($orderId);

// Get line items
$lineItems = $api->get_order_line_items($orderId);

// Transition order
$api->transition_order($orderNumber, 'accept');

// Add line item
$api->post('/line-items/', ['order' => $orderId, 'product' => $productId, 'quantity' => 10]);

// Update order
$api->patch("/orders-received/{$orderId}/", ['delivery_date' => '2025-02-01']);
```
