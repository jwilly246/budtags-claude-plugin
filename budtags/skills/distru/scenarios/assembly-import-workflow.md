# Scenario — Assembly Import Workflow

Import Distru Assemblies (manufacturing/processing events). Assemblies are **read-only** through the public API and **eventually consistent** with ~1s read-after-write lag.

## Prerequisites

- Distru API key configured.
- Batches already imported (or imported on-demand) so input/output batch references resolve locally.
- Decision on which `creation_source` values to import — most teams want `MANUALLY_CREATED` only; compliance imports include all four.

## Step 1 — Paginate `/assemblies`

```php
$page = 1;
do {
    $response = $api->get('/assemblies', [
        'page[number]' => $page,
        // page[size] is IGNORED — fixed at 500
        'completion_datetime_from' => $importJob->last_synced_at?->toIso8601String()
            ?? '1970-01-01T00:00:00Z',
        'creation_source' => 'MANUALLY_CREATED',  // optional filter
    ]);

    foreach ($response['data'] as $assembly) {
        $this->upsertAssembly($assembly);
    }

    $page++;
} while ($response['next_page'] !== null);
```

> **Reminder:** `page[size]` is **ignored** on this endpoint — Distru always returns up to 500/page. Do not assume it took effect.

## Step 2 — Upsert assembly with inputs/outputs

```php
protected function upsertAssembly(array $a): void
{
    $assembly = DistruAssembly::updateOrCreate(
        [
            'organization_id' => $this->org->id,
            'distru_assembly_id' => $a['id'],
        ],
        [
            'completion_datetime' => $a['completion_datetime'],
            'creation_source' => $a['creation_source'],
            'license_number' => $a['license_number'] ?? null,
            'machine_info' => $a['machine_info'] ?? null,
            'custom_fields' => $a['custom_fields'] ?? [],
            'last_synced_at' => now(),
        ],
    );

    // Sync input batches (replace strategy — assemblies are immutable on Distru side)
    $assembly->input_batches()->delete();
    foreach ($a['input_batches'] ?? [] as $ib) {
        $assembly->input_batches()->create([
            'distru_batch_id' => $ib['batch_id'],
            'quantity' => $ib['quantity'],
            'unit_of_measure' => $ib['unit_of_measure'],
        ]);
    }

    // Same for output batches and waste
    $assembly->output_batches()->delete();
    foreach ($a['output_batches'] ?? [] as $ob) {
        $assembly->output_batches()->create([
            'distru_batch_id' => $ob['batch_id'],
            'quantity' => $ob['quantity'],
            'unit_of_measure' => $ob['unit_of_measure'],
        ]);
    }

    $assembly->waste_entries()->delete();
    foreach ($a['waste'] ?? [] as $w) {
        $assembly->waste_entries()->create([
            'amount' => $w['amount'],
            'unit_of_measure' => $w['unit_of_measure'],
            'reason' => $w['reason'] ?? null,
        ]);
    }
}
```

## Step 3 — Resolve batch references

Assembly entries reference `batch_id`. If a batch hasn't been imported yet, mark the assembly entry as "unresolved" and let the next batch-import pass resolve it. Do **not** fetch on demand during assembly import — the volume can be high.

```php
$localBatch = DistruBatch::firstWhere([
    'organization_id' => $this->org->id,
    'distru_batch_id' => $ib['batch_id'],
]);

$assembly->input_batches()->create([
    'distru_batch_id' => $ib['batch_id'],
    'budtags_batch_id' => $localBatch?->local_batch_id,   // null if unresolved
    'quantity' => $ib['quantity'],
    'unit_of_measure' => $ib['unit_of_measure'],
]);
```

## Step 4 — Save the high-water mark with a buffer

```php
// 5-second buffer absorbs the documented ~1s eventual consistency lag
$importJob->update([
    'last_synced_at' => now()->subSeconds(5),
]);
```

Without the buffer, the next import may miss any assembly whose `completion_datetime` falls inside the consistency window.

## Eventual consistency gotchas

- A newly-created Assembly may not appear on the very next `GET /assemblies`. Trust write responses (when applicable) and back off 1.5s+ before re-fetching.
- For deletion detection: there is **no DELETE on assemblies**. Once imported, treat as immutable.

## Cross-references

- Endpoint details: `categories/manufacturing.md`
- Eventual consistency: `patterns/eventual-consistency.md`
- Pagination quirk: `patterns/pagination.md`
