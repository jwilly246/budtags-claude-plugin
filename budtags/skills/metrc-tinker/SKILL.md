---
name: metrc-tinker
description: Query any Metrc API endpoint via Laravel Tinker. Explore endpoints, test parameters, and inspect response data without writing code.
version: 1.0.0
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
---

# Metrc Tinker - Live API Explorer

Query ANY Metrc endpoint directly via Laravel Tinker. Test endpoints, explore parameters, and inspect response data.

**Companion to**: `metrc-api` skill (use that for full endpoint reference - 258 endpoints across 26 categories)

**For complete endpoint documentation**: Read `budtags/skills/metrc-api/categories/*.md`

---

## Quick Start

### Step 1: Setup (Run Once Per Session)

```php
// Get org with Metrc credentials
$org = \App\Models\Organization::whereHas('secrets', fn($q) =>
    $q->where('secret_type_id', \App\Models\SecretType::lookup('Metrc'))
      ->where('is_active', true)
)->first();

// Get user and set active org
$user = \App\Models\User::where('active_org_id', $org->id)->first() ?: $org->users()->first();
$user->update(['active_org_id' => $org->id]);
$user->refresh();

// Get license
$facility = \App\Models\MetrcFacility::where('organization_id', $org->id)->first();
$license = $facility->license_recreational ?: $facility->license_medical;

// Create API instance
$api = (new \App\Services\Api\MetrcApi)->set_user($user);

// Setup reflection for raw endpoint access
$ref = new \ReflectionClass($api);
$get = $ref->getMethod('get');
$post = $ref->getMethod('post');

echo "Ready! License: {$license}\n";
```

### Step 2: Query Any GET Endpoint

```php
// Generic pattern - replace {endpoint} and {params}
$response = $get->invoke($api, '{endpoint}', [
    'licenseNumber' => $license,
    // Add other params as needed
]);

// Inspect response
$response->json();           // Full response
$response->json('Data');     // Data array only
$response->json('TotalPages'); // Pagination info
```

---

## Endpoint Quick Reference

All endpoints require `licenseNumber` parameter. Use the metrc-api skill for full parameter details.

### Packages (All Licenses) - 11 GET Endpoints

```php
// Active packages
$get->invoke($api, '/packages/v2/active', ['licenseNumber' => $license]);

// Inactive packages
$get->invoke($api, '/packages/v2/inactive', ['licenseNumber' => $license]);

// On-hold packages
$get->invoke($api, '/packages/v2/onhold', ['licenseNumber' => $license]);

// In-transit packages
$get->invoke($api, '/packages/v2/intransit', ['licenseNumber' => $license]);

// Single package by ID
$get->invoke($api, '/packages/v2/{id}', ['licenseNumber' => $license]);

// Package by label
$get->invoke($api, '/packages/v2/{label}', ['licenseNumber' => $license]);

// Package types (reference data)
$get->invoke($api, '/packages/v2/types', ['licenseNumber' => $license]);

// Adjustment history
$get->invoke($api, '/packages/v2/adjustments', ['licenseNumber' => $license]);

// Adjustment reasons (for dropdowns)
$get->invoke($api, '/packages/v2/adjust/reasons', ['licenseNumber' => $license]);

// Transferred packages
$get->invoke($api, '/packages/v2/transferred', ['licenseNumber' => $license]);

// Lab test results for package
$get->invoke($api, '/packages/v2/{id}/labtestresults', ['licenseNumber' => $license]);
```

### Plants (Cultivation Only - AU-C)

```php
// Vegetative plants
$get->invoke($api, '/plants/v2/vegetative', ['licenseNumber' => $license]);

// Flowering plants
$get->invoke($api, '/plants/v2/flowering', ['licenseNumber' => $license]);

// Inactive plants
$get->invoke($api, '/plants/v2/inactive', ['licenseNumber' => $license]);

// Single plant by ID
$get->invoke($api, '/plants/v2/{id}', ['licenseNumber' => $license]);
```

### Plant Batches (Cultivation Only - AU-C)

```php
// Active batches
$get->invoke($api, '/plantbatches/v2/active', ['licenseNumber' => $license]);

// Inactive batches
$get->invoke($api, '/plantbatches/v2/inactive', ['licenseNumber' => $license]);

// Batch types
$get->invoke($api, '/plantbatches/v2/types', ['licenseNumber' => $license]);
```

### Harvests (Cultivation + Processing)

```php
// Active harvests
$get->invoke($api, '/harvests/v2/active', ['licenseNumber' => $license]);

// On-hold harvests
$get->invoke($api, '/harvests/v2/onhold', ['licenseNumber' => $license]);

// Inactive harvests
$get->invoke($api, '/harvests/v2/inactive', ['licenseNumber' => $license]);

// Harvest waste types
$get->invoke($api, '/harvests/v2/waste/types', ['licenseNumber' => $license]);
```

### Sales (Retail Only - AU-R)

```php
// Sales receipts
$get->invoke($api, '/sales/v2/receipts', ['licenseNumber' => $license]);

// Active receipts
$get->invoke($api, '/sales/v2/receipts/active', ['licenseNumber' => $license]);

// Inactive receipts
$get->invoke($api, '/sales/v2/receipts/inactive', ['licenseNumber' => $license]);

// Customer types
$get->invoke($api, '/sales/v2/customertypes', ['licenseNumber' => $license]);
```

### Transfers (All Licenses)

```php
// Incoming transfers
$get->invoke($api, '/transfers/v2/incoming', ['licenseNumber' => $license]);

// Outgoing transfers
$get->invoke($api, '/transfers/v2/outgoing', ['licenseNumber' => $license]);

// Rejected transfers
$get->invoke($api, '/transfers/v2/rejected', ['licenseNumber' => $license]);

// Transfer templates
$get->invoke($api, '/transfers/v2/templates', ['licenseNumber' => $license]);

// Transfer types
$get->invoke($api, '/transfers/v2/types', ['licenseNumber' => $license]);
```

### Items (All Licenses)

```php
// Active items
$get->invoke($api, '/items/v2/active', ['licenseNumber' => $license]);

// Item categories
$get->invoke($api, '/items/v2/categories', ['licenseNumber' => $license]);

// Brands (if applicable)
$get->invoke($api, '/items/v2/brands', ['licenseNumber' => $license]);
```

### Lab Tests (All Licenses)

```php
// Lab test states
$get->invoke($api, '/labtests/v2/states', ['licenseNumber' => $license]);

// Lab test types
$get->invoke($api, '/labtests/v2/types', ['licenseNumber' => $license]);
```

### Locations & Strains (All Licenses)

```php
// Active locations
$get->invoke($api, '/locations/v2/active', ['licenseNumber' => $license]);

// Location types
$get->invoke($api, '/locations/v2/types', ['licenseNumber' => $license]);

// Active strains
$get->invoke($api, '/strains/v2/active', ['licenseNumber' => $license]);
```

### Facilities & Employees

```php
// Facilities (no license needed)
$get->invoke($api, '/facilities/v2', []);

// Employees
$get->invoke($api, '/employees/v2', ['licenseNumber' => $license]);
```

### Processing Jobs (Processing Only - AU-P)

```php
// Active jobs
$get->invoke($api, '/processingjob/v2/active', ['licenseNumber' => $license]);

// Job types
$get->invoke($api, '/processingjob/v2/types', ['licenseNumber' => $license]);
```

### Tags

```php
// Available package tags
$get->invoke($api, '/tags/v2/package/available', ['licenseNumber' => $license]);

// Used package tags
$get->invoke($api, '/tags/v2/package/used', ['licenseNumber' => $license]);

// Voided package tags
$get->invoke($api, '/tags/v2/package/voided', ['licenseNumber' => $license]);

// Available plant tags (cultivation only)
$get->invoke($api, '/tags/v2/plant/available', ['licenseNumber' => $license]);
```

### Patients (Retail/Medical Only)

```php
// Active patients
$get->invoke($api, '/patients/v2/active', ['licenseNumber' => $license]);

// Patient by ID
$get->invoke($api, '/patients/v2/{id}', ['licenseNumber' => $license]);
```

### Units of Measure & Reference Data

```php
// Units of measure
$get->invoke($api, '/unitsofmeasure/v2/active', ['licenseNumber' => $license]);

// Waste methods
$get->invoke($api, '/wastemethods/v2', ['licenseNumber' => $license]);

// Additives templates
$get->invoke($api, '/additivestemplates/v2', ['licenseNumber' => $license]);
```

### Transporters (for Transfers)

```php
// Transporter details
$get->invoke($api, '/transporters/v2/details', ['licenseNumber' => $license]);

// Transporter drivers
$get->invoke($api, '/transporters/v2/drivers', ['licenseNumber' => $license]);

// Transporter vehicles
$get->invoke($api, '/transporters/v2/vehicles', ['licenseNumber' => $license]);
```

---

## All Query Parameters

### Universal (All Endpoints)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `licenseNumber` | string | YES | License number (e.g., AU-C-000001) |

### Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pageNumber` | integer | 1 | Page number (1-indexed, NOT 0-indexed) |
| `pageSize` | integer | varies | Results per page (typically 50-200 max) |

```php
$get->invoke($api, '/packages/v2/active', [
    'licenseNumber' => $license,
    'pageNumber' => 1,      // 1-indexed!
    'pageSize' => 100,
]);

// Response pagination info
$response->json('Page');
$response->json('PageSize');
$response->json('TotalPages');
$response->json('TotalRecords');
```

### Date Filtering (Most GET Endpoints)

| Parameter | Type | Format | Description |
|-----------|------|--------|-------------|
| `lastModifiedStart` | string | YYYY-MM-DD | Filter from this date |
| `lastModifiedEnd` | string | YYYY-MM-DD | Filter to this date |

```php
// Filter by last modified date range
$get->invoke($api, '/packages/v2/active', [
    'licenseNumber' => $license,
    'lastModifiedStart' => '2025-01-01',
    'lastModifiedEnd' => '2025-01-31',
]);
```

### Sales-Specific Parameters

| Parameter | Type | Format | Description |
|-----------|------|--------|-------------|
| `salesDateStart` | string | YYYY-MM-DD | Filter by sale date start |
| `salesDateEnd` | string | YYYY-MM-DD | Filter by sale date end |

```php
$get->invoke($api, '/sales/v2/receipts', [
    'licenseNumber' => $license,
    'salesDateStart' => '2025-01-01',
    'salesDateEnd' => '2025-01-31',
]);
```

### Transfer-Specific Parameters

| Parameter | Type | Format | Description |
|-----------|------|--------|-------------|
| `transferDateStart` | string | YYYY-MM-DD | Filter by transfer date start |
| `transferDateEnd` | string | YYYY-MM-DD | Filter by transfer date end |

### Without Pagination (Get All at Once)

```php
// Omit pageNumber/pageSize to get ALL records in single response
// Use with date filter for manageable results
$get->invoke($api, '/packages/v2/active', [
    'licenseNumber' => $license,
    'lastModifiedStart' => '2025-01-15',
    'lastModifiedEnd' => '2025-01-15',
]);
```

### Date Format Reference

| Format | Example | Use For |
|--------|---------|---------|
| Date only | `2025-01-15` | Most date parameters |
| DateTime UTC | `2025-01-15T13:30:00Z` | SalesDateTime, transfer times |
| DateTime with TZ | `2025-01-15T13:30:00-08:00` | Timestamped events |

---

## Inspecting Responses

### View Data Structure

```php
$response = $get->invoke($api, '/packages/v2/active', ['licenseNumber' => $license, 'pageSize' => 1]);

// Get first item to see structure
$first = $response->json('Data.0');
print_r(array_keys($first));  // List all fields

// Pretty print full structure
echo json_encode($first, JSON_PRETTY_PRINT);
```

### Count Records

```php
$response = $get->invoke($api, '/packages/v2/active', ['licenseNumber' => $license]);
echo "Total: " . $response->json('TotalRecords') . "\n";
echo "Pages: " . $response->json('TotalPages') . "\n";
```

### Find Specific Record

```php
$data = $response->json('Data');
$found = collect($data)->firstWhere('Label', '1A400000000000000001234');
```

---

## POST Endpoints

### Generic POST Pattern

```php
$response = $post->invoke($api, '{endpoint}', [
    'licenseNumber' => $license,
], [
    // Request body - usually an array of objects
    [
        'Field1' => 'value1',
        'Field2' => 'value2',
    ]
]);
```

### Example: Adjust Package

```php
$post->invoke($api, '/packages/v2/adjust', [
    'licenseNumber' => $license,
], [
    [
        'Label' => '1A400000000000000001234',
        'Quantity' => -1.0,
        'UnitOfMeasure' => 'Grams',
        'AdjustmentReason' => 'Drying',
        'AdjustmentDate' => '2025-01-15',
        'ReasonNote' => 'Weight loss during drying',
    ]
]);
```

---

## Rate Limiting

```php
// Metrc allows ~5 requests/second
// Add delay between calls when looping
foreach ($items as $item) {
    $response = $get->invoke($api, '/packages/v2/' . $item['Id'], ['licenseNumber' => $license]);
    usleep(200000);  // 200ms delay
}
```

---

## License Type Quick Reference

| License Prefix | Type | Can Access |
|----------------|------|------------|
| `AU-C-######` | Cultivation | Plants, PlantBatches, Harvests, Packages, Items, Transfers |
| `AU-P-######` | Processing | Packages, Items, Harvests, ProcessingJobs, LabTests, Transfers |
| `AU-R-######` | Retail | Sales, Packages, Items, Transfers, Patients |
| `AU-L-######` | Lab | LabTests only |

**Check your license prefix before querying plant endpoints!**

---

## Troubleshooting

### "Unauthorized" Error
- User's org doesn't have active Metrc credentials
- License doesn't belong to user's active_org
- Check: `$user->active_org_id` matches org with Metrc secret

### "404 Not Found"
- Endpoint path is wrong
- Check metrc-api skill for correct endpoint

### "403 Forbidden"
- License type doesn't have access to endpoint
- Example: Retail license can't access `/plants/v2/*`

### Rate Limited
- Too many requests too fast
- Add `usleep(200000)` between calls

### Empty Data Array
- No records match the query
- Try different date range or remove filters

---

---

## All 26 Endpoint Categories

For complete documentation, see `budtags/skills/metrc-api/categories/`:

| Category | Endpoints | License Types |
|----------|-----------|---------------|
| packages | 32 | All |
| plants | 36 | Cultivation |
| plantbatches | 21 | Cultivation |
| harvests | 15 | Cultivation, Processing |
| sales | 36 | Retail |
| transfers | 28 | All |
| items | 16 | All |
| labtests | 8 | All |
| locations | 7 | All |
| sublocations | 6 | All |
| strains | 6 | All |
| facilities | 3 | All |
| employees | 2 | All |
| tags | 8 | All |
| patients | 6 | Retail/Medical |
| patientcheckins | 4 | Retail/Medical |
| processingjob | 17 | Processing |
| transporters | 6 | All |
| unitsofmeasure | 2 | All |
| wastemethods | 1 | All |
| additivestemplates | 1 | All |
| retailid | 3 | Retail |
| caregiversstatus | 2 | Medical |
| patientsstatus | 2 | Medical |
| webhooks | 4 | All |
| sandbox | 1 | Sandbox |

---

## Your Mission

Help users:
1. Set up Metrc API access in Tinker
2. Query any endpoint to explore data
3. Understand response structures
4. Test parameters before implementing
5. Debug API integration issues

**Pair with `metrc-api` skill for endpoint reference and implementation patterns.**
