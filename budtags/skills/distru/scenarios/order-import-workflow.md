# Scenario — Order Import Workflow

Import Distru orders into Budtags `MarketplaceOrder` rows (or the equivalent table you use for `source='distru'`).

## Prerequisites

- Distru API key configured.
- Companies already imported (or imported on-demand during this run) so order `company_id` references resolve to local Customers.
- Products already imported so order line-item `product_id` references resolve to local Items.

## Step 1 — Paginate `/orders` with incremental sync

```php
$page = 1;
do {
    $response = $api->get('/orders', [
        'page[number]' => $page,
        'page[size]'   => 100,
        'updated_at_from' => $importJob->last_synced_at?->toIso8601String() ?? '1970-01-01T00:00:00Z',
    ]);

    foreach ($response['data'] as $distruOrder) {
        $this->upsertOrder($distruOrder);
    }

    $page++;
} while ($response['next_page'] !== null);
```

## Step 2 — Lazy-resolve Companies

If an order references a `company_id` you haven't imported yet:

```php
$company = DistruCompany::firstWhere([
    'organization_id' => $this->org->id,
    'distru_company_id' => $distruOrder['company_id'],
]);

if (!$company) {
    // Fetch on demand
    $companyData = $api->get("/companies/{$distruOrder['company_id']}");
    $company = $this->upsertCompany($companyData['data']);
}
```

## Step 3 — Upsert the Order with inline line items

```php
$order = MarketplaceOrder::updateOrCreate(
    [
        'organization_id' => $this->org->id,
        'source' => 'distru',
        'external_id' => $distruOrder['id'],
    ],
    [
        'order_number' => $distruOrder['order_number'],
        'status' => $this->mapDistruStatus($distruOrder['status']),
        'customer_id' => $company->customer_id,
        'subtotal' => $distruOrder['subtotal'],
        'total' => $distruOrder['total'],
        'due_at' => $distruOrder['due_datetime'] ?? null,
        'completed_at' => $distruOrder['completion_datetime'] ?? null,
        'distru_updated_at' => $distruOrder['updated_at'],   // for conflict detection on write-back
        'last_synced_at' => now(),
    ],
);

// Line items are inline — replace
$order->line_items()->delete();
foreach ($distruOrder['line_items'] as $li) {
    $order->line_items()->create([
        'external_line_item_id' => $li['id'],
        'product_external_id' => $li['product_id'],
        'batch_external_id' => $li['batch_id'] ?? null,
        'quantity' => $li['quantity'],
        'unit_price' => $li['unit_price'],
        'subtotal' => $li['subtotal'],
    ]);
}
```

## Step 4 — Charges and Payments

Charges (delivery, tax adjustments) are inline on the order:

```php
foreach ($distruOrder['charges'] ?? [] as $charge) {
    $order->charges()->updateOrCreate(
        ['label' => $charge['label']],
        ['amount' => $charge['amount']],
    );
}
```

Payments live on the related Invoice. If you need payment data, fetch the Invoice separately by linking via the order:

```php
$invoices = $api->get('/invoices', ['order_id' => $distruOrder['id']]);
```

## Step 5 — Save the high-water mark

```php
$importJob->update(['last_synced_at' => now()->subSeconds(5)]);
```

## Status mapping

Distru's order status names should be mapped to Budtags' `MarketplaceOrderStatus` enum. Build the mapping table once and persist as a config constant:

```php
protected function mapDistruStatus(string $distruStatus): string
{
    return match ($distruStatus) {
        'DRAFT'      => 'pending',
        'CONFIRMED'  => 'approved',
        'FULFILLED'  => 'shipped',
        'INVOICED'   => 'invoiced',
        'PAID'       => 'paid',
        'COMPLETED'  => 'completed',
        'VOID'       => 'cancelled',
        default      => 'unknown',
    };
}
```

## Progress events

```php
if ($processed % 50 === 0) {
    DistruImportUpdate::dispatch($importJob, 'progress', [
        'entity' => 'orders',
        'processed' => $processed,
    ]);
}
```

## Cross-references

- Endpoint details: `categories/sales-orders.md`
- Write-back to Distru: `scenarios/order-writeback-workflow.md`
- Company resolution: `scenarios/customer-import-workflow.md`
