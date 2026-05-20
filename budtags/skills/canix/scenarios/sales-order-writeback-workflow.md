# Scenario: Write Back Sales Orders to Canix

This workflow pushes BudTags MarketplaceOrder changes back to Canix when Canix is the source of truth (bidirectional sync). This is unique to Canix — LeafLink does not support write-back for invoices.

## Prerequisites

- Canix API key configured
- Order has `source='canix'` and `canix_order_id` set
- Write-back is only active when Canix is source of truth

## When Write-Back Triggers

1. **User edits an order** with `source='canix'` in BudTags UI
2. **Status change** on a Canix-sourced order
3. **New order created** in BudTags that should be pushed to Canix

## Step 1: Build Request Body from BudTags Order

```php
private function build_sales_order_body(MarketplaceOrder $order): array
{
    return array_filter([
        'customer_id'         => $this->resolve_canix_customer_id($order->customer_id),
        'name'                => $order->order_number,
        'external_identifier' => "BT-{$order->id}",
        'status'              => $this->map_status_to_canix($order->status),
        'delivery_date'       => $order->delivery_date?->toIso8601String(),
        'payment_date'        => $order->payment_date?->toIso8601String(),
        'payment_terms'       => $order->payment_terms,
        'delivery_fee'        => $order->delivery_fee,
        'local_tax_rate'      => $order->local_tax_rate ?? 0,
        'state_tax_rate'      => $order->state_tax_rate ?? 0,
        'other_tax_rate'      => $order->other_tax_rate ?? 0,
        'internal_notes'      => $order->notes,
        'contents'            => $this->build_contents($order),
        'payments'            => $this->build_payments($order),
    ]);
}
```

### Map BudTags Status to Canix

```php
private function map_status_to_canix(string $budtags_status): string
{
    return match ($budtags_status) {
        'pending'   => 'created',
        'confirmed' => 'approved',
        'shipped'   => 'shipped',
        'delivered' => 'accepted',
        'completed' => 'archived',
        'cancelled' => 'canceled',
        default     => 'created',
    };
}
```

### Build Contents Array

```php
private function build_contents(MarketplaceOrder $order): array
{
    return $order->line_items->map(fn (MarketplaceOrderLineItem $item) => array_filter([
        'item_id'     => $this->resolve_canix_item_id($item->product_id),
        'total_price' => $item->total_price,
        'weight'      => $item->quantity,
        'weight_unit' => $item->unit_of_measure ?? 'Each',
        'notes'       => $item->notes,
    ]))->toArray();
}
```

## Step 2: Create New Order in Canix

```php
public function push_new_order(MarketplaceOrder $order): void
{
    $body = $this->build_sales_order_body($order);

    $response = $this->api->post('/sales_orders', $body);

    // Canix returns the created order with its ID
    $order->update([
        'canix_order_id' => $response['id'],
    ]);

    LogService::store(
        'Canix Write-Back',
        "Created sales order #{$response['id']} in Canix",
        $order,
    );
}
```

## Step 3: Update Existing Order in Canix

```php
public function push_order_update(MarketplaceOrder $order): void
{
    $canix_id = $order->canix_order_id;

    if (!$canix_id) {
        LogService::store('Canix Write-Back', 'No canix_order_id — skipping update', $order);
        return;
    }

    $body = $this->build_sales_order_body($order);
    $this->api->put("/sales_orders/{$canix_id}", $body);

    LogService::store(
        'Canix Write-Back',
        "Updated sales order #{$canix_id} in Canix",
        $order,
    );
}
```

## Step 4: Status Transition

For status changes, use the dedicated status endpoint instead of PUT:

```php
public function push_status_change(MarketplaceOrder $order, string $new_status): void
{
    $canix_id = $order->canix_order_id;
    $canix_status = $this->map_status_to_canix($new_status);

    $response = $this->api->put("/sales_orders/{$canix_id}/status/{$canix_status}");

    LogService::store(
        'Canix Write-Back',
        "Status: {$response['previous_status']} → {$response['new_status']}",
        $order,
    );
}
```

### Status Transition Restrictions

Cannot cancel if status is: `shipped`, `accepted`, `returned`, `archived`

```php
private function can_cancel(string $current_canix_status): bool
{
    return !in_array($current_canix_status, ['shipped', 'accepted', 'returned', 'archived']);
}
```

## Conflict Detection

Use `updated_at` comparison for optimistic locking:

```php
public function detect_conflict(MarketplaceOrder $order): bool
{
    $canix_order = $this->api->get("/sales_orders/{$order->canix_order_id}");

    $canix_updated = Carbon::parse($canix_order['updated_at']);
    $local_synced = $order->canix_synced_at; // Timestamp of last sync

    // If Canix was modified after our last sync, there's a conflict
    return $canix_updated->isAfter($local_synced);
}
```

**Strategy**: Last-write-wins with logging. If conflict detected, log both versions and proceed with the write.

## Write-Back for Other Entities

### Items → Canix

```php
$this->api->put("/items/{$product->canix_item_id}", [
    'name'        => $product->name,
    'sku'         => $product->sku,
    'description' => $product->description,
    'brand_id'    => $product->canix_brand_id,
]);
```

### Vendors → Canix

```php
$this->api->put("/vendors/{$vendor->canix_id}", [
    'name'  => $vendor->name,
    'email' => $vendor->email,
    'phone' => $vendor->phone,
]);
```

### Strains → Canix (limited update fields)

```php
// Note: UpdateStrainRequestBody is slimmer than Create
$this->api->put("/strains/{$strain->canix_id}", [
    'name'        => $strain->name,
    'description' => $strain->description,
    'active'      => true,
]);
```

## Safety Considerations

1. **All writes are irreversible** — test on sandbox first
2. **Log every write** via LogService for audit trail
3. **Disable editing of synced fields** when Canix is source of truth (same as LeafLink pattern)
4. **Dry-run mode** — validate payload without actually sending
5. **Never auto-delete** — only manual deletion with user confirmation
6. **Required fields validation** — check locally before sending to avoid 400 errors

## Error Handling

```php
try {
    $this->push_order_update($order);
} catch (CanixApiException $e) {
    LogService::store('Canix Write-Back Error', $e->getMessage(), $order);
    // Don't throw — write-back failures should not block local operations
}
```

---

**See:** `categories/sales-orders.md` for SalesOrderRequestBody details
**See:** `patterns/write-safety.md` for write safety guidelines
**See:** `patterns/async-submissions.md` for Metrc-bound async operations
