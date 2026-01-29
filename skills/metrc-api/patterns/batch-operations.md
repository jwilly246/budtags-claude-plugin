# Batch Operations

Most Metrc POST/PUT endpoints accept **arrays of objects** for batch operations, allowing multiple entities to be created/updated in a single API call.

**⚠️ CRITICAL CONSTRAINT: 10 Object Maximum Per Request**

Metrc enforces a **hard limit of 10 objects per request** for all batch operations. Exceeding this limit results in **HTTP 413 "Request Entity Too Large"** error.

See [Object Limiting Pattern](./object-limiting.md) for comprehensive details.

---

## Why Use Batch Operations?

✅ **Fewer API Calls**: Reduce HTTP overhead (up to 10 items per call)
✅ **Better Performance**: Process multiple items together
✅ **Transactional**: All succeed or all fail together
✅ **Rate Limit Friendly**: Fewer requests = less likely to hit rate limits

---

## Standard Batch Pattern

### Single Request Format
```json
[
  {
    "Field1": "value1",
    "Field2": "value2"
  },
  {
    "Field1": "value3",
    "Field2": "value4"
  }
]
```

**Key Point**: Request body is an **array**, even for single items.

---

## Laravel/PHP Examples

### Example 1: Batch Adjust Multiple Packages

```php
// ❌ INEFFICIENT - 3 separate API calls
foreach ($packages as $package) {
    $api->post("/packages/v2/adjust?licenseNumber={$license}", [
        [
            'Label' => $package->Label,
            'Quantity' => -0.5,
            'UnitOfMeasure' => 'Grams',
            'AdjustmentReason' => 'Drying',
            'AdjustmentDate' => now()->format('Y-m-d')
        ]
    ]);
}

// ✅ EFFICIENT - 1 batch API call
$adjustments = [];
foreach ($packages as $package) {
    $adjustments[] = [
        'Label' => $package->Label,
        'Quantity' => -0.5,
        'UnitOfMeasure' => 'Grams',
        'AdjustmentReason' => 'Drying',
        'AdjustmentDate' => now()->format('Y-m-d'),
        'ReasonNote' => 'Weight loss during drying process'
    ];
}

// Send all adjustments in one request
$api->post("/packages/v2/adjust?licenseNumber={$license}", $adjustments);
```

### Example 2: Batch Create Packages

```php
$newPackages = [];

foreach ($harvestItems as $item) {
    $newPackages[] = [
        'Tag' => $item['tag'],
        'Item' => $item['item_name'],
        'Quantity' => $item['quantity'],
        'UnitOfMeasure' => $item['unit'],
        'ActualDate' => now()->format('Y-m-d'),
        'Ingredients' => [
            [
                'Package' => $item['source_package'],
                'Quantity' => $item['quantity'],
                'UnitOfMeasure' => $item['unit']
            ]
        ]
    ];
}

// Create all packages in one batch
$api->post("/packages/v2/create?licenseNumber={$license}", $newPackages);
```

### Example 3: Batch Move Plants

```php
$moves = $plants->map(fn($plant) => [
    'Id' => $plant->Id,
    'Label' => $plant->Label,
    'Location' => 'Flowering Room A',
    'ActualDate' => now()->format('Y-m-d')
])->toArray();

$api->post("/plants/v2/moveplants?licenseNumber={$license}", $moves);
```

---

## Batch Size Requirements

**⚠️ METRC ENFORCES A HARD LIMIT: Maximum 10 objects per request**

| Operation | Maximum Batch Size | Recommendation |
|-----------|-------------------|----------------|
| Package Adjustments | **10** | Use 10 (maximum allowed) |
| Package Creation | **10** | Use 10 (maximum allowed) |
| Plant Moves | **10** | Use 10 (maximum allowed) |
| Sales Receipts | **10** | Use 5-10 (complex objects) |
| Tag Replacements | **10** | Use 10 (maximum allowed) |

**Critical Rules:**
- Never send more than 10 objects in a single request
- HTTP 413 error returned if limit exceeded
- Must chunk larger datasets into batches of 10 or fewer

**See Also:** [Object Limiting Pattern](./object-limiting.md) for chunking strategies.

---

## Error Handling

### Transactional Behavior

Metrc batch operations are typically **all-or-nothing**:

```php
$adjustments = [
    ['Label' => 'VALID-TAG-1', 'Quantity' => 5, ...],
    ['Label' => 'INVALID-TAG', 'Quantity' => 5, ...], // This will fail
    ['Label' => 'VALID-TAG-2', 'Quantity' => 5, ...],
];

try {
    $api->post("/packages/v2/adjust?licenseNumber={$license}", $adjustments);
} catch (\Exception $e) {
    // ALL adjustments failed (including valid ones)
    // Error message will indicate which item failed
    Log::error("Batch adjustment failed: " . $e->getMessage());
}
```

### Handling Partial Failures

```php
public function batch_with_retry(array $items, string $endpoint, string $license): array
{
    try {
        // Try full batch first
        $api->post("{$endpoint}?licenseNumber={$license}", $items);
        return ['success' => count($items), 'failed' => 0];
    } catch (\Exception $e) {
        // Batch failed - try items individually
        Log::warning("Batch failed, retrying individually: " . $e->getMessage());

        $success = 0;
        $failed = 0;

        foreach ($items as $item) {
            try {
                $api->post("{$endpoint}?licenseNumber={$license}", [$item]);
                $success++;
            } catch (\Exception $itemError) {
                $failed++;
                Log::error("Item failed: " . json_encode($item) . " - " . $itemError->getMessage());
            }
        }

        return ['success' => $success, 'failed' => $failed];
    }
}
```

---

## Chunking Large Batches (Required for >10 Items)

**⚠️ MANDATORY: Must chunk into batches of 10 or fewer objects**

```php
public function process_in_batches(array $items, string $endpoint, string $license): array
{
    $BATCH_SIZE = 10; // Metrc maximum
    $chunks = array_chunk($items, $BATCH_SIZE);
    $totalChunks = count($chunks);
    $allCreatedIds = [];

    foreach ($chunks as $index => $chunk) {
        $chunkNumber = $index + 1;
        Log::info("Processing batch {$chunkNumber}/{$totalChunks} ({count($chunk)} items)...");

        try {
            $response = $api->post("{$endpoint}?licenseNumber={$license}", $chunk);

            // Metrc returns array of created IDs (order preserved)
            if (!empty($response)) {
                $allCreatedIds = array_merge($allCreatedIds, $response);
            }

            Log::info("Batch {$chunkNumber} completed successfully");

            // Add delay to avoid rate limiting
            if ($chunkNumber < $totalChunks) {
                sleep(1); // 1 second between batches
            }

        } catch (\Exception $e) {
            // Check if it's a 413 error (shouldn't happen with proper chunking)
            if (str_contains($e->getMessage(), '413')) {
                Log::critical("HTTP 413 despite chunking to 10! Chunk size: " . count($chunk));
            }

            Log::error("Batch {$chunkNumber} failed: " . $e->getMessage(), [
                'chunk' => $chunk
            ]);

            throw $e;
        }
    }

    Log::info("All batches completed", [
        'total_items' => count($items),
        'total_batches' => $totalChunks,
        'created_ids' => count($allCreatedIds)
    ]);

    return $allCreatedIds;
}

// Usage:
$createdIds = $this->process_in_batches($adjustments, '/packages/v2/adjust', $license);
```

---

## Best Practices

1. **Never exceed 10 objects per request** (HTTP 413 error)
2. **Always use arrays**: Even for single items, wrap in array
3. **Validate before sending**: Check all items are valid before batch
4. **Log batch details**: Record what you're sending for debugging
5. **Chunk into batches of 10**: Required for datasets larger than 10
6. **Add delays between batches**: Avoid rate limiting (500-1000ms)
7. **Track created IDs**: Metrc returns IDs in order matching your request
8. **Handle failures gracefully**: Log which items failed
9. **Consider retrying individually**: If batch fails, retry items one-by-one

---

## Anti-Patterns

### ❌ WRONG: Looping individual requests

```php
foreach ($packages as $package) {
    $api->post("/packages/v2/finish", [['Label' => $package->Label, 'ActualDate' => now()]]);
    // 100 packages = 100 API calls!
}
```

### ❌ ALSO WRONG: Sending more than 10 at once

```php
$finishes = $packages->map(fn($p) => [
    'Label' => $p->Label,
    'ActualDate' => now()->format('Y-m-d')
])->toArray();

$api->post("/packages/v2/finish?licenseNumber={$license}", $finishes);
// 100 packages = HTTP 413 ERROR!
```

### ✅ CORRECT: Chunk into batches of 10

```php
$finishes = $packages->map(fn($p) => [
    'Label' => $p->Label,
    'ActualDate' => now()->format('Y-m-d')
])->toArray();

// Split into chunks of 10
$chunks = array_chunk($finishes, 10);

foreach ($chunks as $chunk) {
    $api->post("/packages/v2/finish?licenseNumber={$license}", $chunk);
    sleep(1); // Delay between batches
}
// 100 packages = 10 API calls (manageable)
```

---

## Performance Comparison

| Approach | Items | API Calls | Avg Time | Status |
|----------|-------|-----------|----------|--------|
| Individual | 100 | 100 | ~50 seconds | ✅ Works but slow |
| Batches of 10 | 100 | 10 | ~12 seconds | ✅ **REQUIRED** |
| Single Batch | 100 | 1 | N/A | ❌ HTTP 413 Error |

**Result**: Batching in groups of 10 is **~4x faster** than individual requests and **required** by Metrc!

---

## Summary

✅ **Use batch operations whenever possible**
✅ **Maximum 10 objects per request** (Metrc enforced limit)
✅ **All-or-nothing**: Entire batch fails if any item fails
✅ **Chunk large datasets**: Process in batches of 10 or fewer
✅ **Add delays**: 500-1000ms between batches to avoid rate limits
✅ **Track created IDs**: Metrc returns IDs in request order
✅ **Validate first**: Check all items before sending
✅ **Log everything**: Record batches for debugging
✅ **Handle HTTP 413**: Means you exceeded 10 object limit

**See Also:** [Object Limiting Pattern](./object-limiting.md) for comprehensive chunking strategies.
