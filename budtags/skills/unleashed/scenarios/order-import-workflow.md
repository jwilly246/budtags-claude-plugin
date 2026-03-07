# Order Import Workflow

Import sales orders from Unleashed into BudTags for listing alongside LeafLink orders and QuickBooks invoices.

---

## Goal
Fetch sales orders from Unleashed and create/update local records for display on the orders page.

## Prerequisites
- Unleashed API credentials configured (Secret model)
- Customer mappings between Unleashed and BudTags
- Product mappings established

## Complexity
Medium - pagination, customer matching, incremental sync

---

## Workflow Overview

```
1. Authenticate (HMAC-SHA256)
2. Fetch orders (paginated, filtered by modifiedSince)
3. Map customers to BudTags organizations
4. Create/update local order records
5. Log sync results
```

---

## Step 1: Fetch Orders with Incremental Sync

Use `modifiedSince` to only fetch orders changed since last sync.

```php
public function import_orders(): void
{
    $org = request()->user()->active_org->model()->get();
    $last_sync = $org->unleashed_last_sync ?? now()->subDays(30);

    $page = 1;
    $all_orders = [];

    do {
        $response = $this->api->get('/SalesOrders', [
            'modifiedSince' => $last_sync->format('Y-m-d'),
            'orderStatus' => 'Placed,Completed',
            'pageSize' => 200,
            'pageNumber' => $page,
        ]);

        $data = $response->json();
        $all_orders = array_merge($all_orders, $data['Items']);
        $total_pages = $data['Pagination']['NumberOfPages'];
        $page++;
    } while ($page <= $total_pages);

    foreach ($all_orders as $order) {
        $this->process_order($order, $org);
    }

    $org->update(['unleashed_last_sync' => now()]);

    LogService::store(
        type: 'unleashed_order_import',
        message: "Imported " . count($all_orders) . " orders from Unleashed",
    );
}
```

---

## Step 2: Process Individual Order

Map Unleashed order data to local model.

```php
private function process_order(array $order, Organization $org): void
{
    $unleashed_order = UnleashedOrder::updateOrCreate(
        [
            'organization_id' => $org->id,
            'unleashed_guid' => $order['Guid'],
        ],
        [
            'order_number' => $order['OrderNumber'],
            'order_date' => $order['OrderDate'],
            'status' => $order['OrderStatus'],
            'customer_code' => $order['Customer']['CustomerCode'] ?? null,
            'customer_name' => $order['Customer']['CustomerName'] ?? null,
            'subtotal' => $order['SubTotal'],
            'tax_total' => $order['TaxTotal'],
            'total' => $order['Total'],
            'comments' => $order['Comments'] ?? null,
            'warehouse_code' => $order['Warehouse']['WarehouseCode'] ?? null,
            'raw_data' => $order,
        ]
    );

    // Sync line items
    foreach ($order['SalesOrderLines'] ?? [] as $line) {
        UnleashedOrderLine::updateOrCreate(
            [
                'unleashed_order_id' => $unleashed_order->id,
                'unleashed_guid' => $line['Guid'],
            ],
            [
                'line_number' => $line['LineNumber'],
                'product_code' => $line['Product']['ProductCode'] ?? null,
                'product_description' => $line['Product']['ProductDescription'] ?? null,
                'quantity' => $line['OrderQuantity'],
                'unit_price' => $line['UnitPrice'],
                'line_total' => $line['LineTotal'],
            ]
        );
    }
}
```

---

## Step 3: Display on Orders Page

Orders are displayed alongside LeafLink and QuickBooks data on the integrated orders page.

```php
public function index()
{
    $org = request()->user()->active_org->model()->get();

    return Inertia::render('Orders/Index', [
        'unleashed_orders' => $org->unleashed_orders()
            ->with('lines')
            ->latest('order_date')
            ->paginate(50),
    ]);
}
```

---

## Common Issues

### 1. Customer Not Found
**Problem**: Unleashed customer code doesn't match any BudTags customer
**Solution**: Create a mapping table or match by name/code

### 2. Duplicate Orders
**Problem**: Same order imported twice
**Solution**: Use `updateOrCreate` with `unleashed_guid` as unique key

### 3. Large Initial Import
**Problem**: First sync fetches thousands of orders
**Solution**: Use date range filters (`startDate`/`endDate`) to batch the initial import

---

## Related Resources

- `categories/sales-orders.md` - Full endpoint details
- `patterns/pagination.md` - Pagination iteration
- `patterns/authentication.md` - HMAC-SHA256 setup
