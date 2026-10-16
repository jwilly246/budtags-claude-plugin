# LeafLink Order Workflow

Guide for managing the LeafLink order lifecycle from fetching to fulfillment (seller side, `/orders-received/`).

Behaviour lines tagged "verified 2026-10-16 (sandbox, file)" cite raw files in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/`. `patterns/verified-behavior.md` wins on any conflict.

## Overview

This workflow covers:
- Fetching orders with filtering
- Viewing order details
- Processing line items
- Transitioning orders through lifecycle
- Handling payments
- Managing sales rep assignments

---

## Order Lifecycle

```
Draft -> submit -> Submitted -> accept -> Accepted -> fulfill -> Fulfilled -> ship -> Shipped -> complete -> Complete
                       |                     |                      |                    |
                    cancel / reject       reject                 reject               reject (allowed)
```

**Statuses** (spec): `Draft`, `Submitted`, `Accepted`, `Backorder`, `Fulfilled`, `Shipped`, `Complete`, `Rejected`, `Combined`, `Cancelled`.
- **Submitted**: buyer placed the order, or the seller created it on the buyer's behalf
- **Accepted**: seller accepted it and is prepping
- **Fulfilled**: picked, packed, staged
- **Shipped**: left the facility
- **Complete**: retailer received it
- **Rejected**: seller cancelled it
- **Cancelled**: retailer cancelled it

Actions (spec): `submit`, `accept`, `fulfill`, `cancel`, `reject`, `ship`, `complete`. There is no `confirm` or `deliver`.

**What LeafLink allows** (verified 2026-10-16 (sandbox, w_b_inventory.txt, r2_t15_transitions.txt, r3_c_line_delete.txt, r3_i_reject_shipped_paid.txt)):

| Status | available_transitions |
|--------|-----------------------|
| Submitted | accepted, cancelled, rejected |
| Accepted | fulfilled, rejected |
| Fulfilled | shipped, accepted, rejected |
| Shipped | complete, rejected, fulfilled |
| Complete | shipped (Complete -> Rejected = 400) |
| Cancelled, Rejected | (none) |

Shipped -> Rejected returns 200 (paid or not) and clears `ship_date` + `payment_due_date`; `paid` and `payment_balance` stay.

---

## Step 1: Fetch Orders

### Basic Order List

```php
use App\Services\Api\LeafLinkApi;

$api = new LeafLinkApi();

// Accepted orders
$orders = $api->get_orders(
    page: 1,
    status: 'Accepted',   // case-insensitive; comma list allowed
    path: '/leaflink/orders'
);

foreach ($orders as $order) {
    echo "Order {$order['short_id']}: \${$order['total']['amount']}\n";
}
```

### Filter by Date Range

```php
// Orders created in the last 30 days
$orders = $api->get_orders(
    page: 1,
    status: 'all',
    path: '/leaflink/orders',
    extraParams: [
        'created_on__gte' => now()->subDays(30)->utc()->toIso8601ZuluString(),
        'created_on__lte' => now()->utc()->toIso8601ZuluString(),
    ]
);
```

### Advanced Filtering

```php
// Open orders for one customer changed since yesterday
$response = $api->get('/orders-received/', [
    'status' => 'Submitted,Accepted',
    'customer' => 123,
    'modified__gte' => now()->subDay()->utc()->toIso8601ZuluString(),
    'include_children' => 'line_items',
    'limit' => 100,
    'offset' => 0,
]);

$orders = $response->json('results');
$totalCount = $response->json('count');
```

### Available Order Filters

From the spec; honoured/ignored verified 2026-10-16 (sandbox, r3_a_param_sweep.txt).

| Filter | Example | Description |
|--------|---------|-------------|
| `status` | `'Accepted'` or `'Submitted,Accepted'` | Case-insensitive, comma list (honoured) |
| `status__not` | `'Cancelled,Rejected'` | Exclude statuses |
| `customer` | `123` | Spec: customer name/nickname; an id also worked (honoured) |
| `created_on__gte` / `__lte` | `'2025-01-01T00:00:00Z'` | Created range (honoured) |
| `modified__gte` / `__lte` | `'2025-01-15T00:00:00Z'` | Modified range (honoured) |
| `external_id_seller` | `'ZZ-1001'` | Seller's own number (honoured) |
| `paid` | `'true'` | Paid flag |
| `sales_rep` | `789` | Company-staff id |
| `number` | uuid | Order number |

`customer_id` and `customer__id` are IGNORED. There is no `status__in`, `delivery_date__*`, `created_date__*`, `order_date__*` or `number__icontains`.

---

## Step 2: View Order Details

### Get Single Order

```php
$response = $api->get_order($orderNumber);   // uuid

if ($response->successful()) {
    $order = $response->json();

    echo "Order {$order['short_id']} ({$order['number']})\n";
    echo "Customer: {$order['customer']['display_name']}\n";
    echo "Status: {$order['status']}\n";
    echo "Total: \${$order['total']['amount']}\n";
    echo "Tax: \${$order['final_tax']} at {$order['tax_amount']} ({$order['tax_type']})\n";
    echo "Balance: \${$order['payment_balance']}\n";
    echo "Ship date: {$order['ship_date']}\n";   // Mountain offset
}
```

There is no `subtotal`, `tax_total` or `delivery_date` field.

### Get Order with Line Items

```php
$order = $api->get_order($orderNumber)->json();
$lineItems = $api->get_order_line_items($orderNumber);

foreach ($lineItems as $item) {
    $price = $item['on_sale'] ? $item['sale_price'] : $item['ordered_unit_price'];
    // quantity = listing units; bulk_units = cases; price is per sold-in unit (per case)
    echo "- product {$item['product']} x {$item['bulk_units']} cases @ \${$price['amount']}\n";
}
```

---

## Step 3: Process Line Items

Prices are per sold-in unit (per case when `unit_multiplier` > 1); `quantity` counts listing units. Quantity 28 on a multiplier-28 listing at 300 = 1 case, line total 300. Verified 2026-10-16 (sandbox, w_b_inventory.txt).

### Add Line Item to Order

```php
$response = $api->post('/line-items/', [
    'order' => $orderNumber,
    'product' => 456,
    'quantity' => '28',
    'ordered_unit_price' => ['amount' => '300.00', 'currency' => 'USD'],
    'sale_price' => ['amount' => '0.00', 'currency' => 'USD'],
    'notes' => 'Special packaging requested',
]);

if ($response->successful()) {
    $lineItem = $response->json();
    // Save $lineItem['id'] NOW: a retried create duplicates the line.
}
```

Adding lines through the order PATCH is an UPSERT keyed by `id`: an entry without `id` always adds a new line (even for the same product), omitted lines are kept, `[]` -> 400. Verified 2026-10-16 (sandbox, r2_t1_line_semantics.txt).

### Update Line Item Quantity

```php
$response = $api->patch('/line-items/789/', [
    'quantity' => '56',
]);
```

`PATCH /line-items/{id}/` works on every status. A nested `line_items` order PATCH is refused on Cancelled/Rejected (400 `"Order cannot be edited."`). Verified 2026-10-16 (sandbox, r2_t7_sale_clear.txt).

### Clear a Sale Price

```php
// Clear with 0.00; null -> 400, on_sale -> 400 (read-only)
$api->patch('/line-items/789/', [
    'sale_price' => ['amount' => '0.00', 'currency' => 'USD'],
]);
```

An on-sale line keeps billing its `sale_price` even after `ordered_unit_price` is changed. Verified 2026-10-16 (sandbox, w_a_sale_price.txt).

### Delete Line Item

```php
$response = $api->delete('/line-items/789/');

if ($response->status() === 204) {
    LogService::store('LeafLink Line Item Deleted', "Line item #789 removed");
}
```

DELETE returns 204 on every status, Complete/Cancelled/Rejected included, and the order total changes. Gate it on our side. Verified 2026-10-16 (sandbox, r3_c_line_delete.txt).

---

## Step 4: Transition Orders

### Accept Order (Submitted -> Accepted)

```php
public function accept_order(string $orderNumber)
{
    $api = new LeafLinkApi();
    $response = $api->transition_order($orderNumber, 'accept');

    if ($response->successful()) {
        $order = $response->json();

        LogService::store(
            'LeafLink Order Accepted',
            "Order {$order['short_id']}\n" .
            "Customer: {$order['customer']['display_name']}\n" .
            "Status: {$order['status']}\n" .
            "Total: \${$order['total']['amount']}"
        );

        return redirect()->back()->with('message', 'Order accepted');
    }

    return redirect()->back()->with('error', 'Failed to accept order');
}
```

### Fulfill Order (Accepted -> Fulfilled)

```php
$response = $api->transition_order($orderNumber, 'fulfill');
// LeafLink now deducts the line quantities from the listing's quantity
// and releases the reserve (verified 2026-10-16 (sandbox, w_b_inventory.txt)).
```

### Ship Order (Fulfilled -> Shipped)

```php
public function ship_order(Request $request)
{
    $orderNumber = $request->input('order_number');
    $trackingNumber = $request->input('tracking_number');

    $api = new LeafLinkApi();
    $api->patch("/orders-received/{$orderNumber}/", [
        'shipping_details' => "Tracking: {$trackingNumber}",   // "" -> 400; null clears
        'ship_date' => now()->toDateString() . 'T17:00:00Z',
    ]);

    $response = $api->transition_order($orderNumber, 'ship');

    if ($response->successful()) {
        return redirect()->back()->with('message', 'Order marked as shipped');
    }

    return redirect()->back()->with('error', 'Failed to ship order');
}
```

### Complete Order (Shipped -> Complete)

```php
$response = $api->transition_order($orderNumber, 'complete');
```

### Reject / Cancel Order

```php
// reject = seller cancels; cancel = only offered on Submitted
$response = $api->transition_order($orderNumber, 'reject');
```

Reject after Fulfilled gives the quantity back to the listing; reject on Shipped clears `ship_date` and `payment_due_date`. Complete cannot be rejected. Verified 2026-10-16 (sandbox, w_b_inventory.txt, r3_i_reject_shipped_paid.txt, r2_t15_transitions.txt).

---

## Step 5: Handle Payments

### List Order Payments

```php
// /order-payments/?order= is IGNORED (returns every payment); use the order's own list
$response = $api->get("/orders-received/{$orderNumber}/payments/");

foreach ($response->json('results') as $payment) {
    echo "Payment: \${$payment['total']['amount']} ({$payment['payment_type']}) on {$payment['payment_date']}\n";
}
```

Verified 2026-10-16 (sandbox, r3_a_param_sweep.txt).

### Record Payment

```php
$response = $api->post('/order-payments/', [
    'order' => $orderNumber,                        // uuid
    'recorded_by' => $companyStaffId,
    'total' => ['amount' => '500.00', 'currency' => 'USD'],
    'payment_date' => now()->toDateString() . 'T17:00:00Z',
    'payment_type' => 'ach',                        // other, cash, check, credit, trade, ach, wire, cashier
    'reason' => 'ACH123456 first installment',
]);
```

Payment rules (verified 2026-10-16 (sandbox, w_e_payments.txt, r2_t15_transitions.txt)):
- NOT idempotent: the same body twice records two payments. Never auto-retry; re-read the order's payments first.
- Overpay -> 400 `"You cannot overpay for an invoice."`.
- A payment for the exact balance sets `paid` true and `paid_date`; `paid` itself cannot be PATCHed (400).
- Payments are accepted on Cancelled and Rejected orders. Refuse them on our side.

### Check Payment Status

```php
$order = $api->get_order($orderNumber)->json();

if ($order['paid']) {
    echo "Order fully paid on {$order['paid_date']}\n";
} else {
    echo "Balance remaining: \${$order['payment_balance']}\n";
}
```

---

## Step 6: Manage Sales Reps

### Assign Sales Rep to Order

```php
$response = $api->post('/order-sales-reps/', [
    'order' => $orderNumber,
    'rep' => 789,              // company-staff id
]);
```

`sales_reps` sent inside the order create or PATCH came back `[]` with a 200 in the sandbox. Read back after any rep write. Verified 2026-10-16 (sandbox, r2_t11_order_create_shape.txt).

### List Sales Reps

```php
// /order-sales-reps/ takes only limit/offset (spec); filter by order client-side,
// or read sales_reps on the order with include_children=sales_reps
$order = $api->get("/orders-received/{$orderNumber}/", ['include_children' => 'sales_reps'])->json();
```

---

## Step 7: View Order History

### Get Order Event Logs

```php
$response = $api->get('/order-event-logs/', [
    'order' => $orderNumber,   // honoured; modified__gte is IGNORED
    'limit' => 100,
]);

foreach ($response->json('results') as $event) {
    echo "[{$event['created_on']}] {$event['event_type']} by {$event['author_name']} ({$event['source']})\n";
}
```

**Event types** (spec): `accepted`, `backordered`, `cancelled`, `completed`, `created`, `edited`, `fulfilled`, `rejected`, `combined`, `rep_edited`, `shipped`, `shipping_edited`, `submitted`, `unaccepted`. `source` is `app`, `api` or `other`.

---

## Complete Controller Example

```php
namespace App\Http\Controllers;

use App\Services\Api\LeafLinkApi;
use App\Services\LogService;
use Illuminate\Http\Request;
use Inertia\Inertia;

class LeafLinkOrderController extends Controller
{
    public function index(Request $request)
    {
        $api = new LeafLinkApi();

        $status = $request->input('status', 'Accepted');
        $page = $request->input('page', 1);

        $orders = $api->get_orders(
            page: $page,
            status: $status,
            path: '/leaflink/orders',
            extraParams: [
                'created_on__gte' => $request->input('date_from', now()->subDays(30)->toDateString()) . 'T00:00:00Z',
                'created_on__lte' => $request->input('date_to', now()->toDateString()) . 'T23:59:59Z',
            ]
        );

        return Inertia::render('Leaflink/Orders', [
            'orders' => $orders,
            'filters' => [
                'status' => $status,
                'date_from' => $request->input('date_from'),
                'date_to' => $request->input('date_to'),
            ],
        ]);
    }

    public function show(string $number)
    {
        $api = new LeafLinkApi();

        return Inertia::render('Leaflink/OrderDetails', [
            'order' => $api->get_order($number)->json(),
            'lineItems' => $api->get_order_line_items($number),
        ]);
    }

    public function transition(Request $request)
    {
        $values = $request->validate([
            'order_number' => 'required|string',
            'action' => 'required|in:submit,accept,fulfill,ship,complete,reject,cancel',
        ]);

        $api = new LeafLinkApi();
        $response = $api->transition_order($values['order_number'], $values['action']);

        if ($response->successful()) {
            $order = $response->json();

            LogService::store(
                'LeafLink Order Transitioned',
                "Order {$order['short_id']}: {$values['action']}"
            );

            return redirect()->back()->with('message', 'Order transitioned successfully');
        }

        return redirect()->back()->with('error', 'Failed to transition order');
    }
}
```

---

## Best Practices

### 1. Always Check Response Status

```php
$response = $api->get_order($orderNumber);

if (!$response->successful()) {
    LogService::store(
        'LeafLink Order Error',
        "Status: {$response->status()}\nBody: {$response->body()}"
    );
    return redirect()->back()->with('error', 'Failed to fetch order');
}
```

### 2. Send Money Fields Together

- Tax = rate x (lines + shipping), before discount; discount hits lines only.
- `tax_type` `%` only, rate 0-1 (0.24). `discount_type` `%` = 0-1 fraction.
- Sending `discount_type` alone re-reads the stored `discount` in the new type (10 `$` becomes 1000%). Always send `discount` + `discount_type` together.

Verified 2026-10-16 (sandbox, w_d_discount_tax.txt, r2_t2_shipping_tax.txt).

### 3. Send Dates at 17:00Z

`ship_date` / `payment_due_date` as `YYYY-MM-DDT17:00:00Z`. Midnight Detroit lands on the previous day in LeafLink's Mountain time. Verified 2026-10-16 (sandbox, w_f_dates.txt).

### 4. Validate Transitions from LeafLink

Use the order's own `available_transitions` instead of a hard-coded map:

```php
$order = $api->get_order($orderNumber)->json();
$target = ['accept' => 'accepted', 'fulfill' => 'fulfilled', 'ship' => 'shipped',
           'complete' => 'complete', 'reject' => 'rejected', 'cancel' => 'cancelled'][$action] ?? null;

if (!in_array($target, $order['available_transitions'] ?? [], true)) {
    return redirect()->back()->with('error', 'Invalid transition');
}
```

### 5. Never Auto-Retry Writes

Payment POSTs and id-less line entries duplicate on retry. Read back first.

---

## Troubleshooting

### Order Not Found (404)

**Cause:** Order doesn't belong to your company, or an integer id was used instead of the `number` uuid.

### Cannot Transition (400)

**Cause:** Action not in the order's `available_transitions` (e.g. reject on Complete).

### "Order cannot be edited." (400)

**Cause:** Nested order PATCH on a Cancelled or Rejected order. Use `PATCH /line-items/{id}/`.

### Payment Total Mismatch

**Cause:** A retried payment POST recorded twice, or a payment was recorded on a Cancelled/Rejected order. Compare `/orders-received/{number}/payments/` with `payment_balance`.

---

**See Also:**
- `categories/orders.md` - Endpoint and filter reference
- `patterns/verified-behavior.md` - Sandbox-proven behaviour
- `patterns/error-handling.md` - Error troubleshooting
