# LeafLink Order Workflow

Complete guide for managing the LeafLink order lifecycle from fetching to fulfillment.

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
draft → accept → confirm → ship → deliver
          ↓
       cancel (can cancel from any status)
```

**Status Definitions:**
- **draft**: Order created but not yet accepted by seller
- **confirmed**: Seller accepted, ready for fulfillment
- **shipped**: Order has been shipped
- **delivered**: Order received by customer
- **cancelled**: Order cancelled (can happen from any status)

---

## Step 1: Fetch Orders

### Basic Order List

```php
use App\Services\Api\LeafLinkApi;

$api = new LeafLinkApi();

// Get all confirmed orders
$orders = $api->get_orders(
    page: 1,
    status: 'confirmed',
    path: route('leaflink.orders')
);

// Iterate through orders
foreach ($orders as $order) {
    echo "Order #{$order['number']}: \${$order['total']}\n";
}
```

### Filter by Date Range

```php
// Orders from the last 30 days
$orders = $api->get_orders(
    page: 1,
    status: 'all',
    path: route('leaflink.orders'),
    extraParams: [
        'created_date__gte' => now()->subDays(30)->toDateString(),
        'created_date__lte' => now()->toDateString()
    ]
);
```

### Advanced Filtering

```php
// Complex query: confirmed orders from specific customer for next week
$response = $api->get('/orders-received/', [
    'status' => 'confirmed',
    'customer' => 123,                          // Customer ID
    'delivery_date__gte' => now()->toDateString(),
    'delivery_date__lte' => now()->addDays(7)->toDateString(),
    'limit' => 100,
    'offset' => 0
]);

$orders = $response->json('results');
$totalCount = $response->json('count');
```

### Available Order Filters

| Filter | Example | Description |
|--------|---------|-------------|
| `status` | `'confirmed'` | Exact status match |
| `status__in` | `'confirmed,shipped'` | Multiple statuses |
| `customer` | `123` | Customer ID |
| `created_date__gte` | `'2025-01-01'` | Created after date |
| `created_date__lte` | `'2025-01-31'` | Created before date |
| `delivery_date__gte` | `'2025-02-01'` | Delivery after date |
| `delivery_date__lte` | `'2025-02-15'` | Delivery before date |
| `modified__gte` | `'2025-01-15'` | Modified after date |
| `order_date__gte` | `'2025-01-01'` | Order placed after date |
| `number__icontains` | `'ABC'` | Order number contains |

---

## Step 2: View Order Details

### Get Single Order

```php
$response = $api->get_order('12345');

if ($response->successful()) {
    $order = $response->json();

    echo "Order #{$order['number']}\n";
    echo "Customer: {$order['customer']['name']}\n";
    echo "Status: {$order['status']}\n";
    echo "Total: \${$order['total']}\n";
    echo "Subtotal: \${$order['subtotal']}\n";
    echo "Tax: \${$order['tax_total']}\n";
    echo "Delivery: {$order['delivery_date']}\n";
}
```

### Get Order with Line Items

```php
$orderId = '12345';

// Get order
$order = $api->get_order($orderId)->json();

// Get line items
$lineItems = $api->get_order_line_items($orderId);

echo "Order #{$order['number']}\n";
echo "Line Items:\n";

foreach ($lineItems as $item) {
    echo "- {$item['product_name']} x {$item['quantity']} = \${$item['total']}\n";
}

echo "\nTotal: \${$order['total']}\n";
```

---

## Step 3: Process Line Items

### List All Line Items for Order

```php
$lineItems = $api->get_order_line_items('12345');

foreach ($lineItems as $item) {
    echo "{$item['product_name']}\n";
    echo "Quantity: {$item['quantity']}\n";
    echo "Unit Price: \${$item['unit_price']}\n";
    echo "Total: \${$item['total']}\n";
    echo "---\n";
}
```

### Add Line Item to Order

```php
$response = $api->post('/line-items/', [
    'order' => 12345,
    'product' => 456,
    'quantity' => 10,
    'unit_price' => 25.00,
    'notes' => 'Special packaging requested'
]);

if ($response->successful()) {
    $lineItem = $response->json();
    LogService::store(
        'LeafLink Line Item Added',
        "Order #12345: Added {$lineItem['product_name']} x {$lineItem['quantity']}"
    );
}
```

### Update Line Item Quantity

```php
$response = $api->patch('/line-items/789/', [
    'quantity' => 15
]);

if ($response->successful()) {
    $lineItem = $response->json();
    echo "Updated quantity to {$lineItem['quantity']}\n";
    echo "New total: \${$lineItem['total']}\n";
}
```

### Delete Line Item

```php
$response = $api->delete('/line-items/789/');

if ($response->status() === 204) {
    LogService::store('LeafLink Line Item Deleted', "Line item #789 removed");
}
```

---

## Step 4: Transition Orders

### Accept Order (Draft → Confirmed)

```php
public function accept_order(string $orderId)
{
    $api = new LeafLinkApi();
    $response = $api->transition_order($orderId, 'accept');

    if ($response->successful()) {
        $order = $response->json();

        LogService::store(
            'LeafLink Order Accepted',
            "Order #{$order['number']}\n" .
            "Customer: {$order['customer']['name']}\n" .
            "Status: {$order['status']}\n" .
            "Total: \${$order['total']}"
        );

        return redirect()->back()->with('success', 'Order accepted');
    }

    $error = $response->json('detail') ?? 'Failed to accept order';
    return redirect()->back()->with('error', $error);
}
```

### Confirm Order (Accepted → Confirmed)

```php
$response = $api->transition_order('12345', 'confirm');

if ($response->successful()) {
    // Order is now confirmed and ready for fulfillment
    $order = $response->json();

    // Trigger fulfillment process
    dispatch(new ProcessOrderFulfillment($order['id']));
}
```

### Ship Order (Confirmed → Shipped)

```php
public function ship_order(Request $request)
{
    $orderId = $request->input('order_id');
    $trackingNumber = $request->input('tracking_number');

    // Update order notes with tracking
    $api = new LeafLinkApi();
    $api->patch("/orders-received/{$orderId}/", [
        'notes' => "Tracking: {$trackingNumber}"
    ]);

    // Transition to shipped
    $response = $api->transition_order($orderId, 'ship');

    if ($response->successful()) {
        // Send shipping notification to customer
        $order = $response->json();

        Mail::to($order['customer']['email'])->send(
            new OrderShipped($order, $trackingNumber)
        );

        return redirect()->back()->with('success', 'Order marked as shipped');
    }

    return redirect()->back()->with('error', 'Failed to ship order');
}
```

### Deliver Order (Shipped → Delivered)

```php
$response = $api->transition_order('12345', 'deliver');

if ($response->successful()) {
    LogService::store(
        'LeafLink Order Delivered',
        "Order #12345 marked as delivered"
    );

    // Trigger post-delivery actions
    // - Request review
    // - Update inventory
    // - Generate analytics
}
```

### Cancel Order

```php
$response = $api->transition_order('12345', 'cancel');

if ($response->successful()) {
    $order = $response->json();

    LogService::store(
        'LeafLink Order Cancelled',
        "Order #{$order['number']} cancelled"
    );

    // Restore inventory quantities
    foreach ($order['line_items'] as $item) {
        // Restore stock...
    }
}
```

---

## Step 5: Handle Payments

### List Order Payments

```php
$response = $api->get('/order-payments/', [
    'order' => 12345
]);

$payments = $response->json('results');

foreach ($payments as $payment) {
    echo "Payment: \${$payment['amount']}\n";
    echo "Method: {$payment['payment_method']}\n";
    echo "Date: {$payment['payment_date']}\n";
}
```

### Record Payment

```php
$response = $api->post('/order-payments/', [
    'order' => 12345,
    'amount' => 500.00,
    'payment_method' => 'ach',
    'payment_date' => now()->toDateString(),
    'reference_number' => 'ACH123456',
    'notes' => 'First installment payment'
]);

if ($response->successful()) {
    $payment = $response->json();

    LogService::store(
        'LeafLink Payment Recorded',
        "Order #12345: \${$payment['amount']} via {$payment['payment_method']}"
    );
}
```

### Check Payment Status

```php
// Get order with payments
$order = $api->get_order('12345')->json();

$totalPaid = collect($order['payments'])->sum('amount');
$balance = $order['total'] - $totalPaid;

if ($balance <= 0) {
    echo "Order fully paid\n";
} else {
    echo "Balance remaining: \${$balance}\n";
}
```

---

## Step 6: Manage Sales Reps

### Assign Sales Rep to Order

```php
$response = $api->post('/order-sales-reps/', [
    'order' => 12345,
    'sales_rep' => 789,              // Company staff ID
    'commission_percent' => 5.0
]);

if ($response->successful()) {
    LogService::store(
        'LeafLink Sales Rep Assigned',
        "Order #12345: Assigned sales rep #789 (5% commission)"
    );
}
```

### List Sales Reps for Order

```php
$response = $api->get('/order-sales-reps/', [
    'order' => 12345
]);

$salesReps = $response->json('results');

foreach ($salesReps as $rep) {
    echo "{$rep['sales_rep_name']}: {$rep['commission_percent']}% commission\n";
}
```

---

## Step 7: View Order History

### Get Order Event Logs

```php
$response = $api->get('/order-event-logs/', [
    'order' => 12345,
    'limit' => 100
]);

$events = $response->json('results');

foreach ($events as $event) {
    echo "[{$event['date']}] {$event['event_type']}: {$event['description']}\n";
}
```

**Event Types:**
- Order created
- Order accepted
- Order confirmed
- Order shipped
- Order delivered
- Order cancelled
- Payment received
- Line item added/modified
- Status changed

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

        $status = $request->input('status', 'confirmed');
        $page = $request->input('page', 1);

        $orders = $api->get_orders(
            page: $page,
            status: $status,
            path: route('leaflink.orders'),
            extraParams: [
                'created_date__gte' => $request->input('date_from', now()->subDays(30)->toDateString()),
                'created_date__lte' => $request->input('date_to', now()->toDateString())
            ]
        );

        return Inertia::render('Leaflink/Orders', [
            'orders' => $orders,
            'filters' => [
                'status' => $status,
                'date_from' => $request->input('date_from'),
                'date_to' => $request->input('date_to')
            ]
        ]);
    }

    public function show(string $id)
    {
        $api = new LeafLinkApi();

        $order = $api->get_order($id)->json();
        $lineItems = $api->get_order_line_items($id);

        return Inertia::render('Leaflink/OrderDetails', [
            'order' => $order,
            'lineItems' => $lineItems
        ]);
    }

    public function transition(Request $request)
    {
        $values = $request->validate([
            'order_id' => 'required|string',
            'action' => 'required|in:accept,confirm,ship,deliver,cancel'
        ]);

        $api = new LeafLinkApi();
        $response = $api->transition_order($values['order_id'], $values['action']);

        if ($response->successful()) {
            $order = $response->json();

            LogService::store(
                'LeafLink Order Transitioned',
                "Order #{$order['number']}: {$values['action']}"
            );

            return redirect()->back()->with('success', 'Order transitioned successfully');
        }

        $error = $response->json('detail') ?? 'Failed to transition order';
        return redirect()->back()->with('error', $error);
    }
}
```

---

## Best Practices

### 1. Always Check Response Status

```php
$response = $api->get_order('12345');

if (!$response->successful()) {
    LogService::store(
        'LeafLink Order Error',
        "Status: {$response->status()}\nBody: {$response->body()}"
    );
    return redirect()->back()->with('error', 'Failed to fetch order');
}

$order = $response->json();
```

### 2. Log All Transitions

```php
// Log before transition
LogService::store(
    'LeafLink Order Transition Attempted',
    "Order #{$orderId}: Attempting {$action}"
);

$response = $api->transition_order($orderId, $action);

// Log result
if ($response->successful()) {
    LogService::store('LeafLink Order Transition Success', "Order #{$orderId}: {$action} succeeded");
} else {
    LogService::store('LeafLink Order Transition Failed', "Order #{$orderId}: {$action} failed");
}
```

### 3. Handle Partial Payments

```php
$order = $api->get_order('12345')->json();
$totalPaid = collect($order['payments'])->sum('amount');
$balance = $order['total'] - $totalPaid;

if ($balance > 0) {
    // Send payment reminder
    // Don't ship until fully paid
}
```

### 4. Validate Transitions

```php
$validTransitions = [
    'draft' => ['accept', 'cancel'],
    'confirmed' => ['ship', 'cancel'],
    'shipped' => ['deliver', 'cancel'],
    'delivered' => [],
    'cancelled' => []
];

$currentStatus = $order['status'];
$action = $request->input('action');

if (!in_array($action, $validTransitions[$currentStatus])) {
    return redirect()->back()->with('error', 'Invalid transition');
}
```

---

## Troubleshooting

### Order Not Found (404)

**Cause:** Order doesn't belong to your company or doesn't exist.

**Solution:** Verify you're using the correct company context and order ID.

### Cannot Transition (400)

**Cause:** Invalid transition for current status.

**Solution:** Check order's current status and valid transitions.

### Payment Total Mismatch

**Cause:** Payments don't add up to order total.

**Solution:** Reconcile payments, add partial payment if needed.

---

**See Also:**
- `OPERATIONS_CATALOG.md` - Complete order operations reference
- `ERROR_HANDLING.md` - Error troubleshooting
- `CODE_EXAMPLES.md` - Code snippets
