# Scenario: Move Plants to Flowering Phase

**Goal**: Transition vegetative plants to flowering phase (change growth phase and location)

**License Compatibility**: ⚠️ **CULTIVATION LICENSES ONLY** (AU-C-######)

**Complexity**: Moderate

**Prerequisites**:
- Vegetative plants ready for flowering
- Flowering room/location configured in Metrc
- Available plant tags (for phase change)

---

## Workflow Overview

```
1. Get vegetative plants
2. Verify flowering location exists
3. Prepare phase change data
4. Submit phase change request
5. Verify plants moved successfully
```

---

## Step-by-Step Implementation

### Step 1: Get Vegetative Plants

```php
$api = new MetrcApi();
$api->set_user($user);
$license = session('license');

// Check license type first!
$licenseType = explode('-', $license)[1];
if ($licenseType !== 'C') {
    throw new Exception("Plant operations require cultivation license");
}

// Get all vegetative plants
$vegetativePlants = $api->get("/plants/v2/vegetative", [
    'licenseNumber' => $license
]);

// Filter plants ready for flowering (e.g., 30+ days old)
$readyPlants = array_filter($vegetativePlants, function($plant) {
    $plantedDate = Carbon::parse($plant['PlantedDate']);
    $daysOld = $plantedDate->diffInDays(now());
    return $daysOld >= 30;
});
```

---

### Step 2: Verify Flowering Location

```php
// Get all locations
$locations = $api->get("/locations/v2/active", [
    'licenseNumber' => $license
]);

// Find flowering room
$floweringRoom = collect($locations)->firstWhere('Name', 'Flowering Room A');

if (!$floweringRoom) {
    throw new Exception("Flowering location not found. Create it in Metrc first.");
}
```

---

### Step 3: Prepare Phase Change Data

```php
$phaseChanges = [];

foreach ($readyPlants as $plant) {
    $phaseChanges[] = [
        'Id' => $plant['Id'],
        'Label' => $plant['Label'],
        'NewLocation' => 'Flowering Room A',
        'GrowthPhase' => 'Flowering',
        'NewTag' => null, // Use same tag, or assign new tag if needed
        'GrowthDate' => now()->format('Y-m-d')
    ];
}

// Limit batch size
if (count($phaseChanges) > 100) {
    $phaseChanges = array_slice($phaseChanges, 0, 100);
    Log::warning("Processing first 100 plants only. Remaining plants will need separate batch.");
}
```

---

### Step 4: Submit Phase Change Request

**Endpoint**: `POST /plants/v2/changegrowthphases`

```php
try {
    $api->post("/plants/v2/changegrowthphases?licenseNumber={$license}", $phaseChanges);

    Log::info("Moved " . count($phaseChanges) . " plants to flowering");

    return redirect()->back()->with('message', count($phaseChanges) . ' plants moved to flowering successfully');

} catch (\Exception $e) {
    Log::error("Phase change failed: " . $e->getMessage());
    Log::error("Phase change data: " . json_encode($phaseChanges));

    return redirect()->back()->with('error', 'Failed to move plants: ' . $e->getMessage());
}
```

---

### Step 5: Verify Plants Moved

```php
// Wait for Metrc to process
sleep(2);

// Get flowering plants to verify
$floweringPlants = $api->get("/plants/v2/flowering?licenseNumber={$license}");

// Check if our plants are now in flowering
$movedPlantIds = array_column($phaseChanges, 'Id');
$floweringPlantIds = array_column($floweringPlants, 'Id');

$successCount = count(array_intersect($movedPlantIds, $floweringPlantIds));

Log::info("Verified {$successCount} of " . count($movedPlantIds) . " plants in flowering phase");

if ($successCount < count($movedPlantIds)) {
    Log::warning("Not all plants transitioned successfully");
}
```

---

## Complete Controller Example

```php
class PlantController extends Controller
{
    public function move_to_flowering(Request $request)
    {
        $validated = $request->validate([
            'plant_ids' => 'required|array|min:1',
            'plant_ids.*' => 'required|integer',
            'new_location' => 'required|string',
            'growth_date' => 'nullable|date'
        ]);

        $api = new MetrcApi();
        $api->set_user($request->user());
        $license = session('license');

        // Check license type
        $licenseType = explode('-', $license)[1];
        if ($licenseType !== 'C') {
            return redirect()->back()->with('error', 'Plant operations require cultivation license');
        }

        // Build phase change data
        $phaseChanges = [];
        foreach ($validated['plant_ids'] as $plantId) {
            $phaseChanges[] = [
                'Id' => $plantId,
                'NewLocation' => $validated['new_location'],
                'GrowthPhase' => 'Flowering',
                'NewTag' => null,
                'GrowthDate' => $validated['growth_date'] ?? now()->format('Y-m-d')
            ];
        }

        // Submit to Metrc
        try {
            $api->post("/plants/v2/changegrowthphases?licenseNumber={$license}", $phaseChanges);

            LogService::store(
                'move_plants_to_flowering',
                "Moved " . count($phaseChanges) . " plants to flowering in {$validated['new_location']}",
                null,
                $request->user()->active_org_id
            );

            return redirect()->back()->with('message', count($phaseChanges) . " plants moved to flowering");

        } catch (\Exception $e) {
            Log::error("Phase change failed", [
                'plants' => $phaseChanges,
                'error' => $e->getMessage()
            ]);

            return redirect()->back()->with('error', 'Failed to move plants: ' . $e->getMessage());
        }
    }
}
```

---

## Common Issues & Solutions

### Issue 1: "Invalid growth phase transition"

**Solution**: Can't skip phases. If plants are in Clone phase, must go to Seedling → Vegetative → Flowering

```php
// Check current phase first
if ($plant['GrowthPhase'] === 'Clone') {
    // Must go to Seedling first, then Vegetative, then Flowering
}
```

### Issue 2: "Location not found"

**Solution**: Ensure location exists and is active

```php
$locations = $api->get("/locations/v2/active?licenseNumber={$license}");
$locationNames = array_column($locations, 'Name');

if (!in_array($newLocation, $locationNames)) {
    throw new Exception("Location '{$newLocation}' not found");
}
```

### Issue 3: "Plant already in flowering"

**Solution**: Filter out plants already in flowering phase

```php
$vegetativePlants = array_filter($allPlants, function($plant) {
    return $plant['GrowthPhase'] === 'Vegetative';
});
```

---

## Related Resources

- `categories/plants.md` - Plant endpoints
- `categories/locations.md` - Location management
- `patterns/license-types.md` - Cultivation license requirements
- `patterns/batch-operations.md` - Batch processing best practices

---

**For complete endpoint details**, see `collections/metrc-plants.postman_collection.json`
