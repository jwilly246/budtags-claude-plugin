---
name: metrc-tinker
description: Query any Metrc API endpoint via Laravel Tinker. Explore endpoints, test parameters, and inspect response data without writing code.
version: 2.0.0
category: testing
agent: metrc-specialist
auto_activate:
  keywords:
    - "tinker metrc"
    - "test metrc"
    - "query metrc"
    - "metrc endpoint"
    - "explore metrc"
    - "metrc response"
    - "metrc data"
    - "check metrc"
    - "verify metrc"
---

# Metrc Tinker - Live API Explorer

Query Metrc endpoints via `mcp__laravel-boost__tinker` to explore data, test parameters, and debug API issues — without writing application code.

**Companion to**: `metrc-api` skill (full endpoint reference — 258 endpoints across 26 categories)

---

## How to Execute

Use the **`mcp__laravel-boost__tinker`** MCP tool. Each code block below is a self-contained snippet to pass to tinker.

```
mcp__laravel-boost__tinker(code: "...", timeout: 30)
```

> **IMPORTANT**: Do NOT use `php artisan tinker` via Bash. The MCP tinker tool provides better output formatting and error handling.

---

## Step 1: Setup (Run Once Per Session)

```php
$org = \App\Models\Organization::whereHas('secrets', fn($q) =>
    $q->where('secret_type_id', \App\Models\SecretType::lookup('Metrc'))
      ->where('is_active', true)
)->first();

$user = \App\Models\User::where('active_org_id', $org->id)->first()
    ?: $org->users()->first();
$user->update(['active_org_id' => $org->id]);
$user->refresh();

$facility = \App\Models\MetrcFacility::where('organization_id', $org->id)->first();
$license = $facility->license_recreational ?: $facility->license_medical;

$api = (new \App\Services\Api\MetrcApi)->set_user($user);

return "Ready! Org: {$org->name} | License: {$license} | Facility: {$facility->name}";
```

---

## Step 2: Query Using Public Methods

MetrcApi has **147 public methods** — use these instead of raw endpoint access. They handle caching, rate limiting, and parameter formatting.

### Single Record Lookups

```php
// Package by label
$pkg = $api->package($facility->name, '1A400000000000000001234');
return $pkg;

// Plant by tag
$plant = $api->plant($facility->name, '1A400000000000000005678');
return $plant;
```

### List Endpoints (Reference Data)

```php
// Strains
return $api->strains($facility->name);

// Locations
return $api->locations($facility->name);

// Employees
return $api->employees($facility->name);

// Item categories
return $api->item_categories($facility->name);

// Units of measure
return $api->units_of_measure($facility->name);

// Harvest waste types
return $api->harvest_waste_types($facility->name);

// Package types
return $api->package_types($facility->name);

// Transfer types
return $api->transfer_types($facility->name);

// Transporter drivers
return $api->get_drivers($facility->name);

// Transporter vehicles
return $api->get_vehicles($facility->name);
```

### Day-Based Queries (Cached)

These methods use `fetch_from_cache_or_api` with proper caching:

```php
use Carbon\Carbon;

// One day of packages (today — always force-fetched)
$packages = $api->one_day_of_packages($facility->name, Carbon::today());
return count($packages) . ' packages';

// One day of plants
$plants = $api->one_day_of_plants($facility->name, Carbon::today());
return count($plants) . ' plants';

// One day of harvests
$harvests = $api->one_day_of_harvests($facility->name, Carbon::today());
return count($harvests) . ' harvests';

// Historical day (cached, won't re-fetch)
$old = $api->one_day_of_packages($facility->name, Carbon::parse('2025-06-15'));
return count($old) . ' packages on 2025-06-15';

// Force re-fetch a historical day
$fresh = $api->one_day_of_packages($facility->name, Carbon::parse('2025-06-15'), force_fetch: true);
return count($fresh) . ' packages (fresh)';
```

### Bulk/Cached Data

```php
// All cached active packages (from Redis)
$packages = $api->get_cached_packages($facility->name, 'active');
return count($packages) . ' cached active packages';

// All cached plants
$plants = $api->get_cached_plants($facility->name, 'vegetative');
return count($plants) . ' cached vegetative plants';

// Search cached packages
$results = $api->search_cached_packages_paginated(
    $facility->name,
    search: 'Blue Dream',
    status: 'active',
    page: 1,
    per_page: 25
);
return $results;
```

### Transfers

```php
// Incoming transfers
$transfers = $api->fetch_transfers_bulk($facility->name, 'incoming');
return count($transfers) . ' incoming transfers';

// Outgoing transfers
$transfers = $api->fetch_transfers_bulk($facility->name, 'outgoing');
return count($transfers) . ' outgoing transfers';
```

### Mutations (Use with caution!)

```php
// Adjust package quantity
$api->packages_adjust($facility->name, [
    [
        'Label' => '1A400000000000000001234',
        'Quantity' => -1.0,
        'UnitOfMeasure' => 'Grams',
        'AdjustmentReason' => 'Drying',
        'AdjustmentDate' => now()->format('m/d/Y'),
        'ReasonNote' => 'Weight loss during drying',
    ]
]);
```

> **WARNING**: Mutations write to Metrc's live system. Double-check labels and quantities.

---

## Step 3: Raw Endpoint Access (When No Public Method Exists)

For endpoints without a dedicated public method, use Reflection to call the protected `get()`/`post()` methods:

```php
$ref = new \ReflectionClass($api);
$get = $ref->getMethod('get');

// Query any GET endpoint
$response = $get->invoke($api, '/endpoint/v2/path', [
    'licenseNumber' => $license,
    'pageSize' => 10,
]);

return $response->json('Data');
```

> **Prefer public methods** (Step 2) whenever possible. They handle caching, rate limiting, and date formatting. Only fall back to Reflection for endpoints not yet wrapped.

### Inspecting Raw Responses

```php
$ref = new \ReflectionClass($api);
$get = $ref->getMethod('get');

$response = $get->invoke($api, '/packages/v2/active', [
    'licenseNumber' => $license,
    'pageSize' => 1,
]);

// Pagination info
$meta = [
    'Page' => $response->json('Page'),
    'PageSize' => $response->json('PageSize'),
    'TotalPages' => $response->json('TotalPages'),
    'TotalRecords' => $response->json('TotalRecords'),
];

// First record structure
$first = $response->json('Data.0');
$fields = array_keys($first ?? []);

return compact('meta', 'fields');
```

---

## Query Parameters Reference

### Pagination (1-indexed!)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `pageNumber` | int | 1 | **1-indexed**, NOT 0-indexed |
| `pageSize` | int | varies | Max typically 200 |

### Date Filtering

| Parameter | Format | Used By |
|-----------|--------|---------|
| `lastModifiedStart` | `YYYY-MM-DD` | Most endpoints |
| `lastModifiedEnd` | `YYYY-MM-DD` | Most endpoints |
| `salesDateStart` | `YYYY-MM-DD` | Sales only |
| `salesDateEnd` | `YYYY-MM-DD` | Sales only |
| `transferDateStart` | `YYYY-MM-DD` | Transfers only |
| `transferDateEnd` | `YYYY-MM-DD` | Transfers only |

---

## Common Exploration Patterns

### Discover Response Fields

```php
$ref = new \ReflectionClass($api);
$get = $ref->getMethod('get');

$response = $get->invoke($api, '/packages/v2/active', [
    'licenseNumber' => $license,
    'pageSize' => 1,
]);

$first = $response->json('Data.0');
return $first ? array_keys($first) : 'No records found';
```

### Count Records by Status

```php
$ref = new \ReflectionClass($api);
$get = $ref->getMethod('get');

$counts = [];
foreach (['active', 'inactive', 'onhold', 'intransit'] as $status) {
    $r = $get->invoke($api, "/packages/v2/{$status}", [
        'licenseNumber' => $license,
        'pageSize' => 1,
    ]);
    $counts[$status] = $r->json('TotalRecords') ?? 0;
    usleep(200_000); // Rate limit: ~5 req/sec
}
return $counts;
```

### Find a Specific Record

```php
$packages = $api->one_day_of_packages($facility->name, \Carbon\Carbon::today());
$found = collect($packages)->firstWhere('Label', '1A400000000000000001234');
return $found;
```

---

## License Type Quick Reference

| Prefix | Type | Has Access To |
|--------|------|---------------|
| `AU-C` | Cultivation | Plants, PlantBatches, Harvests, Packages, Items, Transfers |
| `AU-P` | Processing | Packages, Items, Harvests, ProcessingJobs, LabTests, Transfers |
| `AU-R` | Retail | Sales, Packages, Items, Transfers, Patients |
| `AU-L` | Lab | LabTests only |

**Always check license prefix before querying!** Retail can't access `/plants/*`, Cultivation can't access `/sales/*`.

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| Unauthorized | Bad credentials or wrong org | Verify `$user->active_org_id` matches org with active Metrc secret |
| 404 Not Found | Wrong endpoint path | Check `metrc-api` skill for correct path |
| 403 Forbidden | License type mismatch | E.g., retail license can't access `/plants/v2/*` |
| Rate Limited | Too many requests | Add `usleep(200_000)` between calls |
| Empty Data | No matching records | Try broader date range or different status |

---

## For Full Endpoint Reference

This skill covers **how to query**. For **what to query** (all 258 endpoints, request/response schemas, license restrictions), use the `metrc-api` skill:

```
Read budtags/skills/metrc-api/categories/*.md
```
