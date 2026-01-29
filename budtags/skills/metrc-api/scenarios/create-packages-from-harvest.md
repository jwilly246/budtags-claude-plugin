> **⚠️ BudTags Payload Optimization Note**
>
> BudTags optimizes Package payloads by excluding 22 rarely-used fields for performance (27.5% reduction).
> The examples below show the **complete Metrc API format** (all fields supported by Metrc).
>
> **Excluded fields in BudTags responses:**
> - `IsProductionBatch`, `ProductionBatchNumber` (lines 72-73, 97-98)
> - `IsTradeSample`, `IsDonation` (lines 74-75, 99-100)
> - `ProductRequiresRemediation` (lines 76, 101)
> - Plus 17 other rarely-used fields
>
> **Why this matters:** When working with Package data from BudTags controllers, these fields won't be present in the response. To access complete Package data, query the Metrc API directly.
>
> **See:** `.claude/docs/performance/payload-field-optimization-measurement-code.md`

# Scenario: Create Packages from Harvest

**Goal**: Create finished packages (flower, trim, shake) from a completed harvest

**License Compatibility**: All license types (cultivation, processing, retail)

**Complexity**: Moderate

**Prerequisites**:
- Completed harvest with available weight
- Available package tags
- Items (products) created in Metrc
- Location for packages

---

## Workflow Overview

```
1. Get available package tags
2. Prepare package data (items, weights, tags)
3. Submit package creation request
4. Verify packages were created
5. (Optional) Finish harvest
```

---

## Step-by-Step Implementation

### Step 1: Get Available Package Tags

**Endpoint**: `GET /tags/v2/package/available`

```php
$api = new MetrcApi();
$api->set_user($user);
$license = session('license');

// Get available tags
$availableTags = $api->get("/tags/v2/package/available", [
    'licenseNumber' => $license
]);

// Ensure we have enough tags
$requiredTags = count($packagesToCreate);
if (count($availableTags) < $requiredTags) {
    throw new Exception("Not enough package tags available. Need: {$requiredTags}, Have: " . count($availableTags));
}

// Take tags we need
$tagsToUse = array_slice($availableTags, 0, $requiredTags);
```

---

### Step 2: Prepare Package Data

```php
$harvestName = 'Blue Dream Harvest 2025-01-15';
$packages = [];

// Example: Create flower package
$packages[] = [
    'Tag' => $tagsToUse[0]['Label'], // '1A4060300000001000000050'
    'Location' => 'Vault A', // Where package will be stored
    'Item' => 'Blue Dream Flower', // Must exist in Metrc items
    'Quantity' => 450.5,
    'UnitOfMeasure' => 'Grams',
    'PatientLicenseNumber' => null, // Only for medical
    'Note' => 'Top shelf flower',
    'IsProductionBatch' => false,
    'ProductionBatchNumber' => null,
    'IsTradeSample' => false,
    'IsDonation' => false,
    'ProductRequiresRemediation' => false,
    'UseSameItem' => false,
    'ActualDate' => now()->format('Y-m-d'), // Date packages created
    'Ingredients' => [
        [
            'HarvestName' => $harvestName, // Source harvest
            'Weight' => 450.5,
            'UnitOfMeasure' => 'Grams'
        ]
    ]
];

// Example: Create trim package
$packages[] = [
    'Tag' => $tagsToUse[1]['Label'],
    'Location' => 'Vault A',
    'Item' => 'Blue Dream Trim',
    'Quantity' => 120.0,
    'UnitOfMeasure' => 'Grams',
    'PatientLicenseNumber' => null,
    'Note' => 'Premium trim',
    'IsProductionBatch' => false,
    'ProductionBatchNumber' => null,
    'IsTradeSample' => false,
    'IsDonation' => false,
    'ProductRequiresRemediation' => false,
    'UseSameItem' => false,
    'ActualDate' => now()->format('Y-m-d'),
    'Ingredients' => [
        [
            'HarvestName' => $harvestName,
            'Weight' => 120.0,
            'UnitOfMeasure' => 'Grams'
        ]
    ]
];

// Example: Create shake package
$packages[] = [
    'Tag' => $tagsToUse[2]['Label'],
    'Location' => 'Vault A',
    'Item' => 'Blue Dream Shake',
    'Quantity' => 80.0,
    'UnitOfMeasure' => 'Grams',
    'PatientLicenseNumber' => null,
    'Note' => null,
    'IsProductionBatch' => false,
    'ProductionBatchNumber' => null,
    'IsTradeSample' => false,
    'IsDonation' => false,
    'ProductRequiresRemediation' => false,
    'UseSameItem' => false,
    'ActualDate' => now()->format('Y-m-d'),
    'Ingredients' => [
        [
            'HarvestName' => $harvestName,
            'Weight' => 80.0,
            'UnitOfMeasure' => 'Grams'
        ]
    ]
];
```

---

### Step 3: Submit Package Creation

**Endpoint**: `POST /harvests/v2/packages`

```php
try {
    $response = $api->post("/harvests/v2/packages?licenseNumber={$license}", $packages);

    Log::info("Created {count($packages)} packages from harvest: {$harvestName}");

    return redirect()->back()->with('message', count($packages) . ' packages created successfully');

} catch (\Exception $e) {
    Log::error("Package creation failed: " . $e->getMessage());
    Log::error("Packages data: " . json_encode($packages));

    return redirect()->back()->with('error', 'Failed to create packages: ' . $e->getMessage());
}
```

---

### Step 4: Verify Packages Created

```php
// Wait a moment for Metrc to process
sleep(2);

// Fetch packages by tags to verify
$createdPackages = [];
foreach ($tagsToUse as $tag) {
    try {
        $package = $api->get("/packages/v2/{$tag['Label']}?licenseNumber={$license}");
        $createdPackages[] = $package;
    } catch (\Exception $e) {
        Log::warning("Package not found yet: {$tag['Label']}");
    }
}

if (count($createdPackages) === count($packages)) {
    Log::info("All packages verified successfully");
} else {
    Log::warning("Expected " . count($packages) . " packages, found " . count($createdPackages));
}
```

---

### Step 5: (Optional) Finish Harvest

After all packages are created, you can finish the harvest:

**Endpoint**: `PUT /harvests/v2/finish`

```php
$finishData = [
    [
        'Id' => $harvestId, // or use 'Name' => $harvestName
        'ActualDate' => now()->format('Y-m-d')
    ]
];

$api->put("/harvests/v2/finish?licenseNumber={$license}", $finishData);

Log::info("Harvest finished: {$harvestName}");
```

---

## Complete Controller Example

```php
class HarvestController extends Controller
{
    public function create_packages(Request $request)
    {
        $validated = $request->validate([
            'harvest_name' => 'required|string',
            'packages' => 'required|array|min:1',
            'packages.*.item' => 'required|string',
            'packages.*.quantity' => 'required|numeric|min:0.01',
            'packages.*.unit' => 'required|string',
            'packages.*.location' => 'required|string',
            'packages.*.note' => 'nullable|string',
        ]);

        $api = new MetrcApi();
        $api->set_user($request->user());
        $license = session('license');

        // Get available tags
        $availableTags = $api->get("/tags/v2/package/available", [
            'licenseNumber' => $license
        ]);

        $packagesNeeded = count($validated['packages']);
        if (count($availableTags) < $packagesNeeded) {
            return redirect()->back()->with('error', "Not enough tags. Need {$packagesNeeded}, have " . count($availableTags));
        }

        // Build package data
        $metrcPackages = [];
        foreach ($validated['packages'] as $index => $package) {
            $metrcPackages[] = [
                'Tag' => $availableTags[$index]['Label'],
                'Location' => $package['location'],
                'Item' => $package['item'],
                'Quantity' => (float)$package['quantity'],
                'UnitOfMeasure' => $package['unit'],
                'PatientLicenseNumber' => null,
                'Note' => $package['note'] ?? null,
                'IsProductionBatch' => false,
                'ProductionBatchNumber' => null,
                'IsTradeSample' => false,
                'IsDonation' => false,
                'ProductRequiresRemediation' => false,
                'UseSameItem' => false,
                'ActualDate' => now()->format('Y-m-d'),
                'Ingredients' => [
                    [
                        'HarvestName' => $validated['harvest_name'],
                        'Weight' => (float)$package['quantity'],
                        'UnitOfMeasure' => $package['unit']
                    ]
                ]
            ];
        }

        // Submit to Metrc
        try {
            $api->post("/harvests/v2/packages?licenseNumber={$license}", $metrcPackages);

            LogService::store(
                'create_packages_from_harvest',
                "Created {$packagesNeeded} packages from harvest: {$validated['harvest_name']}",
                null,
                $request->user()->active_org_id
            );

            return redirect()->back()->with('message', "{$packagesNeeded} packages created successfully");

        } catch (\Exception $e) {
            Log::error("Harvest package creation failed", [
                'harvest' => $validated['harvest_name'],
                'packages' => $metrcPackages,
                'error' => $e->getMessage()
            ]);

            return redirect()->back()->with('error', 'Failed to create packages: ' . $e->getMessage());
        }
    }
}
```

---

## Common Issues & Solutions

### Issue 1: "Not enough tags available"

**Solution**: Order more package tags from Metrc or finish/archive old packages to free up tags

```php
// Check tag availability first
$neededTags = 10;
$availableTags = $api->get("/tags/v2/package/available?licenseNumber={$license}");

if (count($availableTags) < $neededTags) {
    // Alert user or order more tags
}
```

### Issue 2: "Item not found"

**Solution**: Ensure items exist in Metrc before creating packages

```php
// Verify items exist
$items = $api->get("/items/v2/active?licenseNumber={$license}");
$itemNames = array_column($items, 'Name');

foreach ($packages as $package) {
    if (!in_array($package['Item'], $itemNames)) {
        throw new Exception("Item not found in Metrc: {$package['Item']}");
    }
}
```

### Issue 3: "Harvest weight exceeded"

**Solution**: Total package weights cannot exceed harvest total weight

```php
$totalPackageWeight = array_sum(array_column($packages, 'Quantity'));
$harvestWeight = $harvest['TotalWetWeight'];

if ($totalPackageWeight > $harvestWeight) {
    throw new Exception("Package total ({$totalPackageWeight}g) exceeds harvest weight ({$harvestWeight}g)");
}
```

---

## Related Resources

- `categories/harvests.md` - Harvest endpoints
- `categories/packages.md` - Package endpoints
- `categories/tags.md` - Tag management
- `patterns/batch-operations.md` - Batch operation best practices
- `patterns/error-handling.md` - Error handling patterns

---

**For complete endpoint details**, see:
- `collections/metrc-harvests.postman_collection.json`
- `collections/metrc-packages.postman_collection.json`
