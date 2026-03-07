# Metrc API Object Limiting

## Overview

The Metrc API enforces **object limiting** to ensure reliable performance and fair usage for all users. This critical constraint limits the number of objects that can be submitted in a single API request.

**⚠️ CRITICAL CONSTRAINT:**
- **Maximum 10 objects per request** for all POST, PUT, and DELETE operations
- Exceeding this limit results in **HTTP 413 "Request Entity Too Large"** error
- Applies to any endpoint that accepts an array of objects in the request body

---

## The 10 Object Limit

### Which Endpoints Are Affected?

Any API endpoint that accepts an **array of objects** in the request body:

- `POST /packages/v2/create` - Creating multiple packages
- `POST /packages/v2/adjust` - Adjusting multiple packages
- `POST /plants/v2/create/plantings` - Creating multiple plants
- `POST /sales/v2/receipts` - Recording multiple sales receipts
- `PUT /packages/v2/item` - Changing item for multiple packages
- `DELETE /plants/v2/{ids}` - Destroying multiple plants
- And many more...

### HTTP 413 Error Response

When you exceed the 10 object limit, Metrc returns:

```http
HTTP/1.1 413 Request Entity Too Large
Content-Type: application/json

{
  "Message": "The content being submitted is too large"
}
```

---

## Chunking Strategy (Required for Bulk Operations)

To process more than 10 objects, you must **chunk** your requests into batches of 10 or fewer.

### Example: Creating 35 Packages

**❌ WRONG - Will fail with HTTP 413:**
```php
$packages = [...]; // 35 packages

$api->post("/packages/v2/create?licenseNumber={$license}", $packages);
// ERROR: HTTP 413 - Request Entity Too Large
```

**✅ CORRECT - Chunk into batches of 10:**
```php
$packages = [...]; // 35 packages
$BATCH_SIZE = 10;

// Split into chunks of 10
$chunks = array_chunk($packages, $BATCH_SIZE);

// Process each chunk sequentially
foreach ($chunks as $chunk) {
    $api->post("/packages/v2/create?licenseNumber={$license}", $chunk);
}

// Result: 4 API calls (10 + 10 + 10 + 5 packages)
```

---

## Receiving Created Object IDs

**IMPORTANT:** When you make a successful POST request, Metrc now returns the newly created object IDs in the response.

### Response Format

```
Request: Create 3 packages
POST /packages/v2/create?licenseNumber=AU-R-000001
[
  { "Tag": "1A4000000000001", ... },
  { "Tag": "1A4000000000002", ... },
  { "Tag": "1A4000000000003", ... }
]

Response: Array of created IDs (order preserved)
HTTP 200 OK
[12345, 12346, 12347]
```

**Key Points:**
- **Order is preserved** - IDs correspond to the order of objects in your request
- Eliminates need for follow-up GET requests to find created records
- Available for all POST endpoints that create new records

### Example: Tracking Created Packages

```php
$packagesToCreate = [
    ['Tag' => '1A4000000000001', 'Item' => 'Flower', 'Quantity' => 10, ...],
    ['Tag' => '1A4000000000002', 'Item' => 'Edible', 'Quantity' => 5, ...],
    ['Tag' => '1A4000000000003', 'Item' => 'Concentrate', 'Quantity' => 2, ...],
];

$response = $api->post("/packages/v2/create?licenseNumber={$license}", $packagesToCreate);

// $response = [12345, 12346, 12347]
$createdIds = $response;

// Map tags to IDs
$tagToId = collect($packagesToCreate)->map(fn($pkg, $i) => [
    'tag' => $pkg['Tag'],
    'metrc_id' => $createdIds[$i],
])->all();
```

---

## Error Handling Best Practices

### Handle HTTP 413 Gracefully

```php
public function create_packages_safely(array $packages, string $license): array
{
    $BATCH_SIZE = 10;
    $createdIds = [];

    // Split into chunks
    $chunks = array_chunk($packages, $BATCH_SIZE);

    foreach ($chunks as $index => $chunk) {
        try {
            $response = $api->post("/packages/v2/create?licenseNumber={$license}", $chunk);
            $createdIds = array_merge($createdIds, $response);
        } catch (\Exception $e) {
            if (str_contains($e->getMessage(), '413')) {
                // This should never happen with proper chunking
                LogService::store('metrc_413_error', "HTTP 413 despite chunking to 10! Chunk size: " . count($chunk));
            }
            throw $e;
        }
    }

    return $createdIds;
}
```

---

## Common Pitfalls

### 1. Forgetting to Chunk Large Datasets

**Problem:**
```php
// User wants to create 100 packages at once
$packages = $this->generate_packages(100);
$api->post("/packages/v2/create?licenseNumber={$license}", $packages);
// ❌ Will fail with HTTP 413
```

**Solution:**
Always check array length before making requests:
```php
if (count($packages) > 10) {
    // Must chunk into batches
    return $this->create_packages_safely($packages, $license);
} else {
    // Can send directly
    return $api->post("/packages/v2/create?licenseNumber={$license}", $packages);
}
```

### 2. Not Handling Partial Success

**Problem:**
If you're chunking 35 packages (4 batches), and batch 3 fails, what happens to batches 1 and 2?

**Solution:**
Implement partial success handling:
```php
$results = [];
$failures = [];

foreach ($chunks as $index => $chunk) {
    try {
        $response = $api->post("/packages/v2/create?licenseNumber={$license}", $chunk);
        $results[] = ['batch' => $index + 1, 'ids' => $response, 'success' => true];
    } catch (\Exception $e) {
        $failures[] = ['batch' => $index + 1, 'error' => $e->getMessage(), 'packages' => $chunk];
        LogService::store('batch_chunk_failed', "Batch " . ($index + 1) . " failed: " . $e->getMessage());

        // Decision: Continue or stop?
        if ($stopOnFirstError) {
            break;
        }
    }
}

return ['results' => $results, 'failures' => $failures];
```

### 3. Not Accounting for Rate Limits

**Problem:**
Chunking helps with object limits, but you can still hit rate limits if you send chunks too fast.

**Solution:**
Handle 429 responses with Retry-After:
```php
foreach ($chunks as $chunk) {
    try {
        $api->post("/packages/v2/create?licenseNumber={$license}", $chunk);
    } catch (\Exception $e) {
        if (str_contains($e->getMessage(), '429')) {
            // Rate limit hit - wait for Retry-After header
            LogService::store('metrc_rate_limited', 'Rate limited during batch operation, retrying...');
            sleep(60); // Use Retry-After header value in practice
            // Retry this chunk...
        }
        throw $e;
    }
}
```

---

## Performance Implications

### API Call Overhead

When chunking, you trade object limit compliance for increased API calls:

| Objects | Without Chunking | With Chunking (10 max) | Overhead |
|---------|------------------|------------------------|----------|
| 10      | 1 API call       | 1 API call             | 0%       |
| 50      | 1 API call ❌    | 5 API calls ✅         | 400%     |
| 100     | 1 API call ❌    | 10 API calls ✅        | 900%     |

**Impact:**
- More API calls = more time (network latency per call)
- More API calls = higher rate limit risk
- But required for compliance with Metrc's object limiting

### Optimization Strategies

1. **Batch Smartly**: Group related operations (e.g., all packages for same harvest)
2. **Parallel Requests**: If rate limits allow, consider parallel batches (use with caution)
3. **Cache Results**: Avoid redundant operations by caching created IDs
4. **Use Webhooks**: Reduce polling needs (if your tier supports it)

---

## Related Patterns

- **[Error Handling](./error-handling.md)** - Comprehensive error handling strategies
- **[Batch Operations](./batch-operations.md)** - General batch processing patterns

---

## Quick Reference

```
✅ DO:
- Chunk arrays into batches of 10 or fewer
- Handle HTTP 413 errors gracefully
- Track created IDs from POST responses
- Implement partial success handling

❌ DON'T:
- Send more than 10 objects in a single request
- Ignore HTTP 413 errors
- Assume all objects succeed or fail together
```
