# Metrc Package Fetch Optimization

Technical findings and optimizations for high-volume Metrc package fetching.

---

## Problem Statement

The `find_earliest_package_date()` optimization in `app/Services/Api/MetrcApi.php` was not correctly finding the oldest LastModified date, resulting in:
- Only seeing ~28 packages (should be thousands)
- Incorrect date range calculations
- High-volume facilities not loading properly (~30k packages expected)

---

## Key Discoveries

### 1. Date Filter Behavior (Critical)

| Query Type | What Metrc Returns |
|------------|-------------------|
| WITHOUT `lastModifiedStart`/`End` | Only CURRENTLY active packages |
| WITH `lastModifiedStart`/`End` | ALL packages modified in range (including sold/finished) |

**Impact:** Without date filters, a facility with 30,000 packages may only show ~28 currently active ones.

**Fix:** Always include date filters when probing for total package counts.

```php
// WRONG - only sees currently active
$probe = $this->get('/packages/v2/active', [
    'licenseNumber' => $facility,
    'pageNumber' => 1,
    'pageSize' => 20,
]);

// CORRECT - sees all packages in date range
$probe = $this->get('/packages/v2/active', [
    'licenseNumber' => $facility,
    'lastModifiedStart' => $max_start->format('c'),
    'lastModifiedEnd' => $now->format('c'),
    'pageNumber' => 1,
    'pageSize' => 20,
]);
```

### 2. Metrc Sort Order (Critical)

**Metrc sorts by Package ID DESC (creation order), NOT by LastModified!**

| Page | Contains |
|------|----------|
| Page 1 | Newest created packages (highest IDs, recent LastModified) |
| Last page | Oldest created packages (lowest IDs, BUT mixed LastModified dates) |

**Implication:** The last page does NOT contain the oldest LastModified. Old packages may have been recently modified.

**Empirical testing across multiple facilities:**

| Facility Type | Total Pages | Oldest LastModified Found On | Pages From End |
|---------------|-------------|------------------------------|----------------|
| High-volume processing | 1514 | Page 1512 | 2 |
| Medium retail | 39 | Page 38 | 1 |
| Low-volume cultivation | 5 | Page 5 | 0 |
| Medium processing | 64 | Page 64 | 0 |

**Fix:** Scan the last 5 pages and find the minimum LastModified across all of them.

### 3. Pagination vs No-Pagination

| Query Params | Behavior |
|--------------|----------|
| WITHOUT `pageNumber`/`pageSize` | Returns ALL packages in single response |
| WITH `pageNumber`/`pageSize` | Returns paginated (e.g., 20 per page) |

**Impact:** Day-by-day queries (without pagination) get all packages for each day in one call. Bulk queries (with pagination) get 20 per page.

---

## Optimization: Hybrid Bulk/Day-by-Day Method

### The Problem

Day-by-day isn't always optimal. Analysis showed:

| Facility Type | Packages | Bulk Calls | Day-by-Day Calls | Best Method |
|---------------|----------|------------|------------------|-------------|
| Low-volume | 90 | **5** | 150 | BULK saves 145 |
| Medium-volume | 776 | **39** | 330 | BULK saves 291 |
| Medium-volume | 1,263 | **64** | 461 | BULK saves 397 |
| High-volume | 30,262 | 1,514 | **551** | DAY-BY-DAY saves 963 |

### The Rule

```
if (total_pages <= total_days) → use BULK
else → use DAY-BY-DAY
```

Crossover point: ~20 packages/day average

### Implementation

Added these methods to `MetrcApi.php`:

| Method | Purpose |
|--------|---------|
| `probe_package_totals()` | Get total_pages, total_records, and optimized_start date |
| `fetch_packages_bulk()` | Paginated fetch for low-volume facilities |
| `fetch_packages_day_by_day()` | Day-by-day fetch for high-volume facilities |
| `fetch_packages_with_progress()` | Automatically chooses optimal method |

---

## Code Patterns

### Probing for Package Totals

```php
protected function probe_package_totals(string $facility, Carbon $max_start): array {
    $now = Carbon::now();
    $probe = $this->get('/packages/v2/active', [
        'licenseNumber' => $facility,
        'lastModifiedStart' => $max_start->format('c'),
        'lastModifiedEnd' => $now->format('c'),
        'pageNumber' => 1,
        'pageSize' => 20,
    ]);

    $total_pages = $probe->json('TotalPages') ?? 0;
    $total_records = $probe->json('TotalRecords') ?? 0;

    // Scan last 5 pages to find true oldest LastModified
    // (because Metrc sorts by ID, not LastModified)
    $pages_to_scan = min(5, $total_pages);
    $start_page = max(1, $total_pages - $pages_to_scan + 1);

    $earliest = null;
    for ($page = $start_page; $page <= $total_pages; $page++) {
        // ... fetch page and track minimum LastModified
    }

    return [
        'total_pages' => $total_pages,
        'total_records' => $total_records,
        'optimized_start' => $earliest->startOfDay(),
    ];
}
```

### Choosing Optimal Fetch Method

```php
public function fetch_packages_with_progress(string $facility, callable $on_progress): int {
    $probe = $this->probe_package_totals($facility, $max_start);
    $total_days = (int) $probe['optimized_start']->diffInDays($end) + 1;

    // Choose optimal method
    if ($probe['total_pages'] <= $total_days) {
        return $this->fetch_packages_bulk(...);
    } else {
        return $this->fetch_packages_day_by_day(...);
    }
}
```

---

## Testing with Tinker

```php
// Set up API
$org = \App\Models\Organization::find($orgId);
$user = $org->users()->first();
$user->update(['active_org_id' => $org->id]);
$api = (new \App\Services\Api\MetrcApi)->set_user($user);

// Get license
$facility = \App\Models\MetrcFacility::where('organization_id', $org->id)->first();
$license = $facility->license_recreational ?: $facility->license_medical;

// Test the hybrid method (check logs for method selection)
$count = $api->fetch_packages_with_progress($license, fn($data, $current, $total) =>
    echo "Progress: {$current}/{$total}\n"
);

// Logs will show: "Using BULK method" or "Using DAY-BY-DAY method"
```

---

## Summary

| Optimization | Problem | Solution | Impact |
|--------------|---------|----------|--------|
| Date filter | Only saw ~28 packages | Add `lastModifiedStart`/`End` | See all 30k+ packages |
| Scan last 5 pages | Wrong oldest date | Find min across multiple pages | Correct start date |
| Hybrid method | Always used day-by-day | Auto-select based on volume | Save 100-900+ API calls |

---

## Files Modified

- `app/Services/Api/MetrcApi.php`:
  - `probe_package_totals()` - unified probe with date filter
  - `fetch_packages_bulk()` - paginated bulk fetch
  - `fetch_packages_day_by_day()` - extracted day-by-day logic
  - `fetch_packages_with_progress()` - hybrid method selection
