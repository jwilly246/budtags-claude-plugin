# Scenario — Product Import Workflow

Import Distru products into Budtags as `Item` / marketplace product rows. Covers the catalog (Products) and optionally the COA layer (Test Results).

## Prerequisites

- Distru API key stored in the org's Secrets table as `SecretType::Distru`.
- `DistruApi` client configured (`set_user($user)`).
- Budtags-side product mapping table (mirroring `LeafLinkItemMapping` / Canix item mapping) ready to accept rows.

## Step 1 — Paginate `/products`

```php
$page = 1;
do {
    $response = $api->get('/products', [
        'page[number]' => $page,
        'page[size]'   => 100,
        'updated_at_from' => $importJob->last_synced_at?->toIso8601String() ?? '1970-01-01T00:00:00Z',
    ]);

    foreach ($response['data'] as $distruProduct) {
        $this->upsertProduct($distruProduct);
    }

    $page++;
} while ($response['next_page'] !== null);
```

## Step 2 — Map each Distru Product to a Budtags Item

```php
protected function upsertProduct(array $distruProduct): void
{
    $mapping = DistruItemMapping::updateOrCreate(
        [
            'organization_id' => $this->org->id,
            'distru_product_id' => $distruProduct['id'],
        ],
        [
            'sku' => $distruProduct['sku'],
            'name' => $distruProduct['name'],
            'brand' => $distruProduct['brand_name'] ?? null,
            'category' => $distruProduct['category'] ?? null,
            'price' => $distruProduct['price'] ?? null,
            'pos_mappings' => $distruProduct['pos_mappings'] ?? [],
            'last_synced_at' => now(),
        ],
    );

    // Optionally link to an existing Budtags Item via SKU
    if (!$mapping->item_id) {
        $item = Item::firstWhere([
            'organization_id' => $this->org->id,
            'sku' => $distruProduct['sku'],
        ]);
        if ($item) $mapping->update(['item_id' => $item->id]);
    }
}
```

## Step 3 — Cache reference data (Brands, Strains)

Brands and Strains are usually returned inline in product payloads. Cache them as you encounter them to avoid extra lookups:

```php
if (!empty($distruProduct['brand_id']) && !empty($distruProduct['brand_name'])) {
    DistruBrand::updateOrCreate(
        ['organization_id' => $this->org->id, 'distru_brand_id' => $distruProduct['brand_id']],
        ['name' => $distruProduct['brand_name']],
    );
}
```

## Step 4 — Optionally pull Test Results

If COA data is needed, paginate `/test_results` similarly. Test results link to a Batch; the Batch links to a Product. Three-step join:

```php
$testResults = $api->get('/test_results', ['updated_at_from' => $lastSync, 'page[number]' => 1]);
foreach ($testResults['data'] as $tr) {
    DistruTestResult::updateOrCreate(
        ['organization_id' => $this->org->id, 'distru_test_result_id' => $tr['id']],
        ['batch_id' => $tr['batch_id'], 'values' => $tr['values'], 'coa_url' => $tr['coa_url'] ?? null],
    );
}
```

## Step 5 — Save the high-water mark

```php
$importJob->update(['last_synced_at' => now()->subSeconds(5)]);  // small buffer for consistency
```

## Strain eventual consistency

Strains have ~1s read-after-write lag. If the import creates products that reference a brand-new strain, the strain itself may not yet appear in a separate `/strains` lookup. Strategies:

- Pull strain inline from the product payload rather than calling `/strains` separately.
- If a strain lookup is required, retry with a 1.5s backoff.

See `patterns/eventual-consistency.md`.

## Progress events

Mirror `CanixImportUpdate` — emit progress every N products:

```php
if ($processed % 100 === 0) {
    DistruImportUpdate::dispatch($importJob, 'progress', [
        'entity' => 'products',
        'processed' => $processed,
        'page' => $page,
    ]);
}
```

## Cross-references

- Endpoint details: `categories/products.md`
- Pagination: `patterns/pagination.md`
- Eventual consistency: `patterns/eventual-consistency.md`
