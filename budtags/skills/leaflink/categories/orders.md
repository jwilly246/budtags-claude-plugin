# Orders - LeafLink API Category

Reference for order management endpoints: orders, line items, payments, sales reps, event logs.

Behaviour lines tagged "verified 2026-10-16 (sandbox, file)" cite raw files in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/`. `patterns/verified-behavior.md` is the canonical list and wins on any conflict.

---

## Collection Reference

**OpenAPI Schema:** `schemas/openapi-orders.json` (official spec: `~/budtags-audits/2026-10-15/leaflink_docs_gap_audit/official_openapi.json`)
**Company Compatibility:**
- Seller companies: Use `/orders-received/*` endpoints
- Buyer companies: Use `/buyer/orders/` (list only)

Orders are addressed by `number` (a uuid), not an integer id. `short_id` is the human number.

---

## Endpoint Overview

### GET Endpoints (List & Retrieve)

| Endpoint | Description | Company Type |
|----------|-------------|--------------|
| `GET /orders-received/` | List received orders | Seller only |
| `GET /orders-received/{number}/` | Get order details | Seller only |
| `GET /orders-received/{number}/line-items/` | List an order's line items | Seller only |
| `GET /orders-received/{number}/payments/` | List an order's payments | Seller only |
| `GET /orders-received/{number}/comments/` | List an order's comments | Seller only |
| `GET /orders/{order_number}/delivery-information/` | Delivery information | Seller |
| `GET /buyer/orders/` | List buyer's placed orders | Buyer only |
| `GET /line-items/` | List line items | Both |
| `GET /line-items/{id}/` | Get line item details | Both |
| `GET /order-payments/` | List payments (filters: `limit`, `offset` only) | Both |
| `GET /order-payments/{id}/` | Get payment details | Both |
| `GET /order-sales-reps/` | List sales rep assignments | Both |
| `GET /order-sales-reps/{id}/` | Get sales rep assignment | Both |
| `GET /order-event-logs/` | List order event history | Both |
| `GET /order-event-logs/{id}/` | Get event log details | Both |
| `GET /credits/`, `GET /credits/{id}/` | Customer credits | Seller |

### POST Endpoints (Create)

| Endpoint | Description | Company Type |
|----------|-------------|--------------|
| `POST /orders-received/` | Create order (BETA, "subject to change") | Seller only |
| `POST /line-items/` | Add line item to order | Both |
| `POST /order-payments/` | Record payment | Both |
| `POST /order-sales-reps/` | Assign sales rep (`order`, `rep`) | Both |
| `POST /orders-received/{number}/transition/{action}/` | Transition order status | Seller only |

### PATCH Endpoints (Update)

| Endpoint | Description | Company Type |
|----------|-------------|--------------|
| `PATCH /orders-received/{number}/` | Update order | Seller only |
| `PATCH /line-items/{id}/` | Update line item | Both |

### DELETE Endpoints (Remove)

| Endpoint | Description | Company Type |
|----------|-------------|--------------|
| `DELETE /orders-received/{number}/` | Delete a **Draft** order only | Seller only |
| `DELETE /line-items/{id}/` | Remove line item (works on every status, see below) | Both |
| `DELETE /order-sales-reps/{id}/` | Remove sales rep assignment | Both |

---

## Common Use Cases

### 1. Fetch Orders with Filters

```php
// Accepted orders created in January 2025
$orders = $api->get_orders(
    page: 1,
    status: 'Accepted',
    path: '/leaflink/orders',
    extraParams: [
        'created_on__gte' => '2025-01-01T00:00:00Z',
        'created_on__lte' => '2025-01-31T23:59:59Z',
        'customer' => 123,  // Optional
    ]
);
```

### 2. Get Order Details

```php
$order = $api->get_order($orderNumber)->json();

// Line items come back on list rows even without include_children
// (verified 2026-10-16 (sandbox, r3_a_param_sweep.txt))
$lineItems = $api->get_order_line_items($orderNumber);
```

### 3. Transition Order Status

```php
// Actions: submit, accept, fulfill, cancel, reject, ship, complete
$response = $api->transition_order(
    orderNumber: $orderNumber,
    action: 'fulfill'
);
```

### 4. Update Order

```php
// PATCH is partial. Send date-only fields at 17:00Z.
$response = $api->patch("/orders-received/{$orderNumber}/", [
    'ship_date' => '2025-02-01T17:00:00Z',
    'notes' => 'Rush delivery requested',
]);
```

There is no `delivery_date` field. `external_id_seller` is create-only (not in `OrderUpdate`). `payment_term` is deprecated on update; use `selected_payment_option` (`{"payment_term_id": n, "payment_method_id": n}`, works after create, verified 2026-10-16 (sandbox, r2_t11_order_create_shape.txt)).

### 5. Add Line Item to Order

```php
// quantity counts listing units; prices are per sold-in unit (per case when unit_multiplier > 1)
$response = $api->post('/line-items/', [
    'order' => $orderNumber,
    'product' => $productId,
    'quantity' => '28',
    'ordered_unit_price' => ['amount' => '300.00', 'currency' => 'USD'],
    'sale_price' => ['amount' => '0.00', 'currency' => 'USD'],  // 0 = not on sale
]);
```

Line quantity 28 on a multiplier-28 listing = 1 case (`bulk_units` 1); price 300 is per case, so the line totals 300. Verified 2026-10-16 (sandbox, w_b_inventory.txt).

---

## Order Status Lifecycle

**Statuses** (spec enum): `Draft`, `Submitted`, `Accepted`, `Backorder`, `Fulfilled`, `Shipped`, `Complete`, `Rejected`, `Combined`, `Cancelled`. Create accepts only `Draft` or `Submitted`.

**Transition actions** (spec): `submit`, `accept`, `fulfill`, `cancel`, `reject`, `ship`, `complete`. POST, no body.

**`available_transitions` read back** (verified 2026-10-16 (sandbox, w_b_inventory.txt, r3_c_line_delete.txt)):

| Status | available_transitions |
|--------|-----------------------|
| Submitted | accepted, cancelled, rejected |
| Accepted | fulfilled, rejected |
| Fulfilled | shipped, accepted, rejected |
| Shipped | complete, rejected, fulfilled |
| Complete | shipped |
| Cancelled, Rejected | (none) |

- **Shipped -> Rejected works** (200), also when partly or fully paid. It clears `ship_date` and `payment_due_date`; `paid` and `payment_balance` stay. Verified 2026-10-16 (sandbox, r2_t15_transitions.txt, r3_i_reject_shipped_paid.txt). The older "reject on Shipped 500s" note is out of date.
- **Complete -> Rejected = 400** `["Cannot perform reject action on an order in complete state."]`. Verified 2026-10-16 (sandbox, r2_t15_transitions.txt).
- Inventory: Submitted reserves, Accept no change, Fulfil deducts quantity and releases the reserve, Ship no change, Reject after Fulfil gives the quantity back. Verified 2026-10-16 (sandbox, w_b_inventory.txt).

---

## Money Rules

Verified 2026-10-16 (sandbox, w_d_discount_tax.txt, r2_t2_shipping_tax.txt):

- **Tax = rate x (line subtotal + shipping), before discount.** $300 line + $50 shipping at 0.24 -> tax 84; adding a 10% discount leaves tax at 84.
- **Discount applies to lines only**: 300 x 0.9 + 50 + 84 = 404.
- **`tax_type` is `%` only, `tax_amount` is a 0-1 fraction.** `"$"` -> 400 `"Fixed ($) tax amounts are not supported..."`; `24` -> 400 `"Tax rate must be between 0 and 1"`.
- **`discount_type: "%"` takes a 0-1 fraction** (0.3 = 30%; 10 = 1000%, total goes negative).
- **`discount_type` alone flips the stored value's meaning** (10 `$` -> 1000%). `discount` alone keeps the old type. Always send `discount` and `discount_type` together.
- `shipping_charge` accepts `{"amount": "50.00", "currency": "USD"}` or a bare number.

### sale_price

Verified 2026-10-16 (sandbox, w_a_sale_price.txt):
- Clear with `{"amount": "0.00", "currency": "USD"}`. `null` -> 400 `"This field may not be null."`. `on_sale` -> 400 `"Forbidden fields in update operation: on_sale"` (read-only; true when sale_price > 0).
- A line sent with `sale_price` = ordered price reads `on_sale: true`. Send 0 when the line is not on sale.
- An on-sale line is billed at `sale_price` and ignores later `ordered_unit_price` edits (ordered 330 / sale 300 still bills 300).

---

## Line Item Rules

- **Order PATCH `line_items` is an UPSERT keyed by line `id`** (verified 2026-10-16 (sandbox, r2_t1_line_semantics.txt)): key omitted -> lines untouched; entry with `id` -> that line updated; a subset -> other lines KEPT; entry **without** `id` -> a NEW line (duplicates the same product, total goes up); `[]` -> 400 `"This list may not be empty."`. Save each new line's id before the next push; a retried PATCH with id-less entries duplicates lines. `OrderUpdate` in the spec has no `line_items` key; the guide's example is the only documentation.
- **`DELETE /line-items/{id}/` returns 204 on every status** (Submitted, Accepted, Fulfilled, Shipped, Complete, Cancelled, Rejected); GET afterwards 404s, and the order total changes. Verified 2026-10-16 (sandbox, r3_c_line_delete.txt).
- **`PATCH /line-items/{id}/` works on every status**; **nested order PATCH is refused on Cancelled and Rejected** (400 `"Order cannot be edited."`) and works on Submitted and Shipped. Verified 2026-10-16 (sandbox, w_a_sale_price.txt, r2_t7_sale_clear.txt, w_a_nested_order_patch.txt).
- `LineItemUpdate` does not accept `unit_multiplier` (spec).
- `is_sample: true` on create is kept. Verified 2026-10-16 (sandbox, r2_t11_order_create_shape.txt).

---

## Payments

Verified 2026-10-16 (sandbox, w_e_payments.txt, r2_t15_transitions.txt):
- `POST /order-payments/` requires `order` (number), `recorded_by` (company-staff id), `total` (money), `payment_date` (send `T17:00:00Z`); optional `payment_type` (`other`, `cash`, `check`, `credit`, `trade`, `ach`, `wire`, `cashier`), `reason`.
- **`paid` cannot be PATCHed**: 400 `"Forbidden fields in update operation: {'paid'}"`. `paid_date` takes a plain date (datetime -> 400).
- **A payment for the exact balance settles the order** (`paid` true, `paid_date` set, balance 0).
- **Overpay -> 400** `"You cannot overpay for an invoice."`.
- **POST is NOT idempotent**: the same body twice = two payments. Never auto-retry; read `/orders-received/{number}/payments/` first.
- **Payments are accepted on Cancelled and Rejected orders.** Guard on our side.

---

## Other Fields

- Dates: send `YYYY-MM-DDT17:00:00Z` (reads back 11:00 Mountain, same day). Date-only = midnight Mountain (same day). Midnight Detroit (`T00:00:00-04:00`) reads back as 22:00 the **previous** day. Verified 2026-10-16 (sandbox, w_f_dates.txt).
- `shipping_details`: `""` -> 400 `"This field may not be blank."`; `null` clears; omitted keeps it. `notes` / `internal_notes` accept `""` and `null`. Verified 2026-10-16 (sandbox, r3_b_shipping_details.txt).
- `sales_reps` sent on create or PATCH came back `[]` with a 200 in the sandbox. Read back; never trust the 200. Verified 2026-10-16 (sandbox, r2_t11_order_create_shape.txt).
- `external_id_seller` on create becomes the `short_id`. Verified 2026-10-16 (sandbox, w_b_inventory.txt).

---

## Available Filters

From the spec for `GET /orders-received/`. "Honoured" / "IGNORED" = verified 2026-10-16 (sandbox, r3_a_param_sweep.txt); an ignored parameter returns the whole list with a 200.

### Date Filters
- `created_on__gte`, `__lte`, `__gt`, `__lt` - Order creation range (honoured)
- `modified__gte`, `__lte`, `__gt`, `__lt` - Last modified range (honoured)

### Status Filters
- `status` - One status or a comma-separated list, case-insensitive (honoured; `rejected` = `Rejected`)
- `status__not` - Exclude statuses (comma-separated)

### Relationship / Other Filters
- `customer` - spec: "customer name or nickname"; a customer id also worked in the sandbox (honoured)
- `customer_id`, `customer__id` - **IGNORED**
- `sales_rep` - company-staff id of the assigned rep
- `external_id_seller` (honoured), `external_id_seller__icontains`
- `number`, `order_id`, `brand`, `brand__in`, `buyer`, `paid`, `classification`, `user`, `connected_to_metrc`, `manual`, `external_id_key` / `external_id_values`
- `include_children=line_items,sales_reps` (honoured)
- `fields_include` takes order field names: `fields_include=id` -> 400 `"Fields `id` do not exist on this endpoint."`; use `number`. Verified 2026-10-16 (sandbox, r2_t9_pagination.txt)

There is no `status__in`, `total__gte`, `delivery_date__*` or `created_date__*`.

### Other endpoints
- `/line-items/`: `order` (honoured), `product_id`, `is_sample`, `order__created_on__*`, `order__modified__*`, `order__ship_date__*`. `ordering` is IGNORED.
- `/order-payments/`: `order=` and `modified__gte` are **IGNORED**. Use `GET /orders-received/{number}/payments/`.
- `/order-event-logs/`: `order` and `ordering` honoured; `modified__gte` **IGNORED**.

---

## Important Notes

### Company Scoping (CRITICAL!)

**Seller Companies:** `/orders-received/*`; see incoming orders FROM buyers; can transition, update and manage them.

**Buyer Companies:** `GET /buyer/orders/`; see outgoing orders TO sellers.

```php
// ❌ Wrong: Buyer trying to access seller endpoint
$api->get('/orders-received/');

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

---

## Related Resources

- **Patterns:** `patterns/verified-behavior.md` - Sandbox-proven write semantics (wins on conflict)
- **Scenarios:** `scenarios/order-workflow.md` - Order lifecycle workflow
- **Patterns:** `patterns/company-scoping.md` - Seller vs buyer context
- **Patterns:** `patterns/filtering.md` - Honoured/ignored parameter table
- **Patterns:** `patterns/pagination.md` - Handling large order lists
- **Schema:** `schemas/openapi-orders.json` - Endpoint specifications

---

## Quick Reference

```php
// List orders
$orders = $api->get_orders(1, 'Accepted', '/leaflink/orders');

// Get single order
$order = $api->get_order($orderNumber);

// Get line items
$lineItems = $api->get_order_line_items($orderNumber);

// Transition order (submit, accept, fulfill, cancel, reject, ship, complete)
$api->transition_order($orderNumber, 'accept');

// Add line item
$api->post('/line-items/', [
    'order' => $orderNumber,
    'product' => $productId,
    'quantity' => '28',
    'ordered_unit_price' => ['amount' => '300.00', 'currency' => 'USD'],
    'sale_price' => ['amount' => '0.00', 'currency' => 'USD'],
]);

// Update order
$api->patch("/orders-received/{$orderNumber}/", ['ship_date' => '2025-02-01T17:00:00Z']);
```
