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
$api = app(\App\Services\Api\MetrcApi::class);
$api->set_user(request()->user());
$license = session('license');
$facility = session('facility');

// Check license type first!
$licenseType = explode('-', $license)[1];
if ($licenseType !== 'C') {
    return redirect()->back()->with('message', 'Plant operations require cultivation license');
}

// Get vegetative plants using public method
$vegetativePlants = $api->one_day_of_plants($facility, \Carbon\Carbon::today());

// Filter plants ready for flowering (e.g., vegetative phase, 30+ days old)
$readyPlants = collect($vegetativePlants)->filter(function ($plant) {
    return $plant['GrowthPhase'] === 'Vegetative'
        && \Carbon\Carbon::parse($plant['PlantedDate'])->diffInDays(now()) >= 30;
});
```

---

### Step 2: Verify Flowering Location

```php
// Get all locations using public method
$locations = $api->locations($facility);

// Find flowering room
$floweringRoom = collect($locations)->firstWhere('Name', 'Flowering Room A');

if (!$floweringRoom) {
    return redirect()->back()->with('message', 'Flowering location not found. Create it in Metrc first.');
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
```

---

### Step 4: Submit Phase Change Request

**Endpoint**: `POST /plants/v2/changegrowthphases`

```php
try {
    // Chunk into batches of 10 (Metrc limit)
    $chunks = array_chunk($phaseChanges, 10);

    foreach ($chunks as $chunk) {
        $api->change_plant_growth_phase($facility, $chunk);
    }

    LogService::store(
        'move_plants_to_flowering',
        "Moved " . count($phaseChanges) . " plants to flowering",
        null,
        request()->user()->active_org_id
    );

    return redirect()->back()->with('message', count($phaseChanges) . ' plants moved to flowering successfully');

} catch (\Exception $e) {
    LogService::store(
        'move_plants_to_flowering_failed',
        "Phase change failed: " . $e->getMessage(),
        null,
        request()->user()->active_org_id
    );

    return redirect()->back()->with('message', 'Failed to move plants: ' . $e->getMessage());
}
```

---

## Complete Controller Example

```php
class PlantController extends Controller
{
    public function move_to_flowering()
    {
        $validated = request()->validate([
            'plant_ids' => 'required|array|min:1',
            'plant_ids.*' => 'required|integer',
            'new_location' => 'required|string',
            'growth_date' => 'nullable|date'
        ]);

        $api = app(\App\Services\Api\MetrcApi::class);
        $api->set_user(request()->user());
        $license = session('license');
        $facility = session('facility');

        // Check license type — only cultivation can access plant endpoints
        $licenseType = explode('-', $license)[1];
        if ($licenseType !== 'C') {
            return redirect()->back()->with('message', 'Plant operations require cultivation license');
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

        // Submit to Metrc (chunks of 10)
        try {
            $chunks = array_chunk($phaseChanges, 10);
            foreach ($chunks as $chunk) {
                $api->change_plant_growth_phase($facility, $chunk);
            }

            LogService::store(
                'move_plants_to_flowering',
                "Moved " . count($phaseChanges) . " plants to flowering in {$validated['new_location']}",
                null,
                request()->user()->active_org_id
            );

            return redirect()->back()->with('message', count($phaseChanges) . " plants moved to flowering");

        } catch (\Exception $e) {
            LogService::store(
                'move_plants_to_flowering_failed',
                "Phase change failed: " . $e->getMessage(),
                null,
                request()->user()->active_org_id
            );

            return redirect()->back()->with('message', 'Failed to move plants: ' . $e->getMessage());
        }
    }
}
```

---

## Common Issues & Solutions

### Issue 1: "Invalid growth phase transition"

**Solution**: Can't skip phases. Clone → Seedling → Vegetative → Flowering

### Issue 2: "Location not found"

**Solution**: Ensure location exists and is active

```php
$locations = $api->locations($facility);
$locationNames = array_column($locations, 'Name');

if (!in_array($newLocation, $locationNames)) {
    return redirect()->back()->with('message', "Location '{$newLocation}' not found");
}
```

### Issue 3: "Plant already in flowering"

**Solution**: Filter out plants already in flowering phase

---

## Related Resources

- `categories/plants.md` - Plant endpoints
- `categories/locations.md` - Location management
- `patterns/license-types.md` - Cultivation license requirements
- `patterns/batch-operations.md` - Batch processing best practices

---

**For complete endpoint details**, see `collections/metrc-plants.postman_collection.json`
