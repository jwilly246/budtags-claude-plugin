# Scenario: Import Sales Orders from Canix

This workflow imports sales orders (seller perspective) from Canix into BudTags `MarketplaceOrder` records with `source='canix'`.

## Prerequisites

- Canix API key configured in secrets table (`SecretType::lookup('Canix')`)
- Reference data already imported (customers, items/products)
- Entity caches populated: `canix_customer_id → uuid`, `canix_item_id → uuid`

## Workflow Steps

### Step 1: Fetch Sales Orders (Paginated)

```php
$all_orders = [];
$offset = 0;
$limit = 2000;

$where_clause = $modified_since
    ? "updated_at >= '{$modified_since}'"
    : null;

do {
    $params = array_filter([
        'limit'    => $limit,
        'offset'   => $offset,
        'order_by' => 'id asc',
        'where'    => $where_clause,
    ]);

    $page = $api->get('/sales_orders', $params);
    $all_orders = array_merge($all_orders, $page);
    $offset += $limit;
} while (count($page) === $limit);
```

**Key points**:
- Use `order_by=id asc` for deterministic pagination
- For incremental sync: `where=updated_at >= '{date}'` with last import's `started_at - 1 day`
- Sales order response includes embedded `customer`, `contents`, and `payments`
- No need to call `/contents` or `/payments` separately (they're embedded)

### Step 2: Process Each Order

```php
collect($all_orders)->each(function (array $order) use ($ctx) {
    // Check if order already exists
    $existing = $ctx->order_cache[$order['id']] ?? null;

    if ($existing && $existing->canix_updated_at === $order['updated_at']) {
        $ctx->stats['skipped']++;
        return; // Skip unchanged orders
    }

    $order_data = [
        'organization_id'    => $ctx->org_id,
        'canix_order_id'     => $order['id'],
        'order_number'       => $order['name'],
        'source'             => MarketplaceOrder::SOURCE_CANIX,
        'status'             => $this->map_status($order['status']),
        'customer_id'        => $ctx->customer_cache[$order['customer']['id']] ?? null,
        'subtotal'           => $order['subtotal'],
        'total'              => $order['total_price'],
        'total_paid'         => $order['total_paid'],
        'delivery_fee'       => $order['delivery_fee'],
        'local_tax_rate'     => $order['local_tax_rate'],
        'state_tax_rate'     => $order['state_tax_rate'],
        'other_tax_rate'     => $order['other_tax_rate'],
        'delivery_date'      => $order['delivery_date'],
        'payment_terms'      => $order['payment_terms'],
        'notes'              => $order['internal_notes'],
        'external_id_seller' => $order['external_identifier'],
    ];

    if ($existing) {
        $this->update_order($existing, $order_data, $order);
    } else {
        $ctx->orders_to_insert[] = $order_data;
        $this->collect_line_items($order, $ctx);
        $this->collect_payments($order, $ctx);
    }

    $ctx->increment_progress();
});
```

### Step 3: Map Order Status

```php
private function map_status(string $canix_status): string
{
    return match ($canix_status) {
        'created'   => 'pending',
        'approved'  => 'confirmed',
        'filled'    => 'confirmed',
        'shipped'   => 'shipped',
        'accepted'  => 'delivered',
        'archived'  => 'completed',
        'requested' => 'pending',
        'canceled'  => 'cancelled',
        default     => 'pending',
    };
}
```

### Step 4: Process Line Items

```php
private function collect_line_items(array $order, ImportContext $ctx): void
{
    collect($order['contents'] ?? [])->each(function (array $item) use ($order, $ctx) {
        $product_id = isset($item['item']['id'])
            ? ($ctx->product_cache[$item['item']['id']] ?? null)
            : null;

        $ctx->line_items_to_insert[] = [
            'organization_id'     => $ctx->org_id,
            'canix_line_item_id'  => $item['id'],
            'marketplace_order_id' => null, // Set after batch insert
            'product_id'          => $product_id,
            'name'                => $item['item']['name'] ?? 'Unknown',
            'sku'                 => $item['item']['sku'] ?? null,
            'quantity'            => $item['weight'],
            'unit_of_measure'     => $item['weight_unit'],
            'unit_price'          => $item['unit_price'] ?? null,
            'total_price'         => $item['total_price'],
            'position'            => $item['order'] ?? 0,
        ];
    });
}
```

### Step 5: Process Payments

```php
private function collect_payments(array $order, ImportContext $ctx): void
{
    collect($order['payments'] ?? [])->each(function (array $payment) use ($ctx) {
        $ctx->payments_to_insert[] = [
            'organization_id' => $ctx->org_id,
            'amount'          => $payment['amount'],
            'payment_date'    => $payment['date'],
        ];
    });
}
```

### Step 6: Batch Insert

```php
// Insert orders in 500-record chunks
collect($ctx->orders_to_insert)
    ->chunk(500)
    ->each(fn ($chunk) => MarketplaceOrder::insert($chunk->toArray()));

// Insert line items
collect($ctx->line_items_to_insert)
    ->chunk(500)
    ->each(fn ($chunk) => MarketplaceOrderLineItem::insert($chunk->toArray()));

// Insert payments
collect($ctx->payments_to_insert)
    ->chunk(500)
    ->each(fn ($chunk) => OrderPayment::insert($chunk->toArray()));
```

## Incremental Sync (Live Sync on Page Visit)

For the `useCanixSync` hook — called when user visits the orders page:

```php
public function sync_recent(string $org_id, int $facility_id, string $modified_since): ImportResult
{
    $orders = $this->api->get('/sales_orders', [
        'where'    => "updated_at >= '{$modified_since}'",
        'limit'    => 2000,
        'order_by' => 'updated_at desc',
    ]);

    // Process max 2 pages (same pattern as LeafLink sync_recent)
    // Returns stats: { created: N, updated: N, skipped: N }
}
```

## Discount Handling

Orders can have discounts at two levels:
- **Order-level**: `sales_order_credit` — applies to entire order
- **Line-item-level**: `contents[].discount` — applies per line item

Both use the same `{ type: "fixed"|"percentage", amount, reason }` schema.

## Error Handling

- If customer_id can't be resolved: log warning, set `customer_id = null`
- If product can't be resolved for line item: log warning, store name/sku only
- If order already exists and hasn't changed: skip (compare `updated_at`)
- Network errors: handled by job retry (4 attempts with 60/300/600s backoff)

---

**See:** `categories/sales-orders.md` for endpoint details and full schema
**See:** `patterns/pagination.md` for pagination patterns
**See:** `patterns/filtering.md` for incremental sync filtering
