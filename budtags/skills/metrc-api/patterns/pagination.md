# Pagination Patterns

Metrc API uses **1-indexed pagination** with `pageNumber` and `pageSize` query parameters.

---

## Standard Pagination Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pageNumber` | integer | No | 1 | Page number (starts at 1, not 0) |
| `pageSize` | integer | No | Varies | Results per page (typically 50-200) |

**IMPORTANT**: `pageNumber` is **1-indexed** (first page is 1, not 0)

---

## Which Endpoints Support Pagination?

Most `GET` endpoints that return lists support pagination:

✅ **Support Pagination**:
- `/packages/v2/active`
- `/plants/v2/vegetative`
- `/harvests/v2/active`
- `/items/v2/active`
- `/sales/v2/receipts`
- `/transfers/v2/incoming`

❌ **No Pagination** (return fixed data):
- `/packages/v2/types` - Returns all package types
- `/items/v2/categories` - Returns all categories
- `/facilities/v2/` - Returns user's facilities

---

## Laravel/PHP Pagination Patterns

### Pattern 1: Iterate Until No More Results

```php
public function get_all_active_packages(string $license): array
{
    $allPackages = [];
    $pageNumber = 1;
    $pageSize = 50;
    $hasMore = true;

    while ($hasMore) {
        $response = $this->api->get("/packages/v2/active", [
            'licenseNumber' => $license,
            'pageNumber' => $pageNumber,
            'pageSize' => $pageSize
        ]);

        if (empty($response)) {
            $hasMore = false;
        } else {
            $allPackages = array_merge($allPackages, $response);

            // If we got fewer results than pageSize, we're on the last page
            if (count($response) < $pageSize) {
                $hasMore = false;
            } else {
                $pageNumber++;
            }
        }
    }

    return $allPackages;
}
```

### Pattern 2: Fetch Single Page (Most Common)

```php
public function get_packages_page(string $license, int $page = 1, int $perPage = 50): array
{
    return $this->api->get("/packages/v2/active", [
        'licenseNumber' => $license,
        'pageNumber' => $page,
        'pageSize' => $perPage
    ]);
}
```

### Pattern 3: Laravel Collection with Lazy Loading

```php
public function get_packages_lazy(string $license): \Generator
{
    $pageNumber = 1;
    $pageSize = 100;

    do {
        $results = $this->api->get("/packages/v2/active", [
            'licenseNumber' => $license,
            'pageNumber' => $pageNumber,
            'pageSize' => $pageSize
        ]);

        foreach ($results as $package) {
            yield $package; // Lazy load one at a time
        }

        $pageNumber++;
    } while (count($results) === $pageSize);
}

// Usage:
foreach ($api->get_packages_lazy($license) as $package) {
    // Process one package at a time without loading all into memory
    echo $package['Label'];
}
```

### Pattern 4: With Progress Tracking

```php
public function sync_packages_with_progress(string $license): void
{
    $pageNumber = 1;
    $pageSize = 50;
    $total = 0;

    do {
        Log::info("Fetching packages page {$pageNumber}...");

        $packages = $this->api->get("/packages/v2/active", [
            'licenseNumber' => $license,
            'pageNumber' => $pageNumber,
            'pageSize' => $pageSize
        ]);

        $count = count($packages);
        $total += $count;

        Log::info("Fetched {$count} packages (total: {$total})");

        // Process packages...
        foreach ($packages as $package) {
            Package::updateOrCreate(
                ['Label' => $package['Label']],
                $package
            );
        }

        $pageNumber++;
    } while ($count === $pageSize);

    Log::info("Sync complete. Total packages: {$total}");
}
```

---

## Recommended Page Sizes

| Endpoint | Recommended Size | Reasoning |
|----------|------------------|-----------|
| Packages | 50-100 | Moderate data size |
| Plants | 100-200 | Lightweight objects |
| Sales | 50 | Heavy objects with transactions |
| Transfers | 50 | Heavy objects with packages |
| Items | 100 | Moderate size |

**General Rule**: Start with 50, increase if performance is good and objects are lightweight.

---

## Common Pitfalls

### ❌ WRONG: Starting at page 0

```php
$pageNumber = 0; // ❌ WRONG - Metrc uses 1-indexed pagination
```

### ✅ CORRECT: Starting at page 1

```php
$pageNumber = 1; // ✅ CORRECT
```

### ❌ WRONG: Not checking for last page

```php
// Infinite loop if you don't check for last page!
while (true) {
    $results = $api->get("/packages/v2/active", [
        'pageNumber' => $pageNumber,
        'pageSize' => 50
    ]);
    $pageNumber++;
    // Missing break condition!
}
```

### ✅ CORRECT: Checking result count

```php
do {
    $results = $api->get("/packages/v2/active", [
        'pageNumber' => $pageNumber,
        'pageSize' => 50
    ]);
    $pageNumber++;
} while (count($results) === 50); // Break when fewer than pageSize
```

---

## Rate Limiting Considerations

Metrc enforces rate limits. When paginating large datasets:

1. **Add delays between requests** (100-500ms recommended)
2. **Handle 429 errors** with exponential backoff
3. **Cache results** when possible

```php
public function get_all_with_rate_limiting(string $endpoint, string $license): array
{
    $allResults = [];
    $pageNumber = 1;
    $pageSize = 50;

    do {
        try {
            $results = $this->api->get($endpoint, [
                'licenseNumber' => $license,
                'pageNumber' => $pageNumber,
                'pageSize' => $pageSize
            ]);

            $allResults = array_merge($allResults, $results);
            $pageNumber++;

            // Small delay to avoid rate limiting
            usleep(200000); // 200ms delay

        } catch (\Exception $e) {
            if (str_contains($e->getMessage(), '429')) {
                // Rate limited - wait longer and retry
                sleep(5);
                continue; // Retry same page
            }
            throw $e;
        }
    } while (count($results) === $pageSize);

    return $allResults;
}
```

---

## Frontend Pagination (React/Inertia)

```tsx
const PackagesTable: React.FC = () => {
    const [page, setPage] = useState(1);
    const [packages, setPackages] = useState([]);

    useEffect(() => {
        axios.get('/api/metrc/packages', {
            params: {
                page: page,
                per_page: 50
            }
        }).then(response => {
            setPackages(response.data);
        });
    }, [page]);

    return (
        <div>
            <table>{/* Render packages */}</table>
            <button onClick={() => setPage(p => p - 1)} disabled={page === 1}>
                Previous
            </button>
            <span>Page {page}</span>
            <button onClick={() => setPage(p => p + 1)}>
                Next
            </button>
        </div>
    );
};
```

---

## Summary

- ✅ Use `pageNumber` (1-indexed) and `pageSize` query parameters
- ✅ Iterate until `count(results) < pageSize`
- ✅ Add delays between requests to avoid rate limiting
- ✅ Use appropriate page sizes (50-200 depending on endpoint)
- ✅ Cache results when possible
- ❌ Don't start at page 0
- ❌ Don't fetch all pages if you only need recent data
- ❌ Don't hammer the API without delays
