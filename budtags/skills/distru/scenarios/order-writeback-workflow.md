# Scenario — Order Write-Back Workflow

Push Budtags-originated order changes back to Distru via `PUT /public/v1/orders/{id}`. This is the bidirectional half of the integration — when a Budtags user marks an order shipped, the status should propagate to Distru.

## Prerequisites

- Order has already been imported from Distru and has a mapped `external_id` (Distru order id).
- Budtags-side `distru_updated_at` was captured at the last import (for conflict detection).
- The Distru API key has write permission on Orders.

## Step 1 — Detect a local change requiring write-back

```php
$orders = MarketplaceOrder::where('source', 'distru')
    ->where('needs_writeback', true)
    ->where('writeback_attempts', '<', 3)
    ->limit(100)
    ->get();
```

The `needs_writeback` flag is set by Budtags business logic (e.g., a status transition handler).

## Step 2 — Conflict detection via `updated_at`

Before pushing, **re-fetch the Distru order** and compare `updated_at`. If Distru has been modified since the last import, abort the write-back and surface a conflict for the user.

```php
$current = $api->get("/orders/{$order->external_id}");
$distruUpdatedAt = $current['data']['updated_at'];

if ($distruUpdatedAt > $order->distru_updated_at) {
    $order->update([
        'writeback_status' => 'conflict',
        'writeback_error' => 'Distru order modified at ' . $distruUpdatedAt,
    ]);
    DistruImportUpdate::dispatch($order->importJob, 'conflict', ['order_id' => $order->id]);
    return;
}
```

## Step 3 — Build the PUT payload

```php
$payload = [
    'status' => $this->mapBudtagsStatusToDistru($order->status),
    'due_datetime' => $order->due_at?->toIso8601String(),
    'completion_datetime' => $order->completed_at?->toIso8601String(),
    'line_items' => $order->line_items->map(fn ($li) => [
        'id' => $li->external_line_item_id,        // preserve existing line-item ids
        'product_id' => $li->product_external_id,
        'quantity' => $li->quantity,
        'unit_price' => $li->unit_price,
    ])->all(),
];
```

> **Critical:** Echo the **full line-items array**, including unchanged lines. Distru's PUT semantics on partial line-item arrays are not documented, so a full replacement is the safe default.

## Step 4 — Execute the PUT

```php
try {
    $response = $api->put("/orders/{$order->external_id}", $payload);

    $order->update([
        'needs_writeback' => false,
        'writeback_status' => 'synced',
        'writeback_error' => null,
        'distru_updated_at' => $response['data']['updated_at'],
        'last_synced_at' => now(),
    ]);
} catch (\Throwable $e) {
    $order->increment('writeback_attempts');
    $order->update([
        'writeback_status' => 'error',
        'writeback_error' => Str::limit($e->getMessage(), 500),
    ]);

    // Idempotency recovery: re-fetch and inspect (writes may have committed despite the error)
    sleep(2);
    $verify = $api->get("/orders/{$order->external_id}");
    if ($verify['data']['updated_at'] > $order->distru_updated_at) {
        // Write actually committed; treat as success
        $order->update([
            'needs_writeback' => false,
            'writeback_status' => 'synced',
            'writeback_error' => null,
            'distru_updated_at' => $verify['data']['updated_at'],
        ]);
    } else {
        throw $e;
    }
}
```

## Status mapping (Budtags → Distru)

```php
protected function mapBudtagsStatusToDistru(string $bs): string
{
    return match ($bs) {
        'pending'   => 'DRAFT',
        'approved'  => 'CONFIRMED',
        'shipped'   => 'FULFILLED',
        'invoiced'  => 'INVOICED',
        'paid'      => 'PAID',
        'completed' => 'COMPLETED',
        'cancelled' => 'VOID',
        default     => throw new InvalidArgumentException("No Distru mapping for {$bs}"),
    };
}
```

## Cross-references

- Write semantics: `patterns/write-safety.md`
- Error and retry handling: `patterns/error-handling.md`
- Endpoint details: `categories/sales-orders.md`
