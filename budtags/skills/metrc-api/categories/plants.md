# Plants Category

**Collection File**: `collections/metrc-plants.postman_collection.json`
**Total Endpoints**: 36
**License Compatibility**: ⚠️ **CULTIVATION LICENSES ONLY** (AU-C-######)

---

## ⚠️ CRITICAL WARNING

**Plant endpoints are ONLY accessible to Cultivation licenses.**

Processing (AU-P-######) and Retail (AU-R-######) licenses will receive:
- HTTP 401 Unauthorized or 403 Forbidden
- Error: "No valid endpoint found" or "Insufficient permissions"

**Before using any plant endpoint, verify the license type starts with `AU-C-`**

---

## GET Endpoints (16 endpoints)

### Retrieve Plants

- `GET /plants/v2/{id}` - Get plant by Metrc ID
- `GET /plants/v2/{label}` - Get plant by tag/label
- `GET /plants/v2/vegetative` - Get all vegetative phase plants (clones, seedlings)
- `GET /plants/v2/flowering` - Get all flowering phase plants
- `GET /plants/v2/onhold` - Get on-hold plants
- `GET /plants/v2/inactive` - Get inactive plants

### Mother Plants

- `GET /plants/v2/mother` - Get active mother plants
- `GET /plants/v2/mother/inactive` - Get inactive mother plants
- `GET /plants/v2/mother/onhold` - Get on-hold mother plants

### Waste & Reference Data

- `GET /plants/v2/waste` - Get plant waste records
- `GET /plants/v2/waste/{id}/plants` - Get plants associated with specific waste record
- `GET /plants/v2/waste/{id}/package` - Get packages associated with specific waste record
- `GET /plants/v2/growthphases` - Get available growth phases (Clone, Seedling, Vegetative, Flowering)
- `GET /plants/v2/additives/types` - Get additive types (fertilizers, pesticides)
- `GET /plants/v2/additives` - Get recorded additive applications
- `GET /plants/v2/waste/reasons` - Get waste reasons for plants

**Common Query Parameters**: `licenseNumber` (required), `pageNumber`, `pageSize`, `lastModifiedStart`, `lastModifiedEnd`

---

## POST Endpoints (10 endpoints)

### Plant Lifecycle

- `POST /plants/v2/plantings` - Create plant batches from individual plants
  - Use case: Group plants into batches
  - Request body: Array with plant labels, batch name, strain

- `POST /plants/v2/moveplants` - Move plants to new location
  - Use case: Relocate plants to different room/area
  - Request body: Array with `Id` or `Label`, `Location`, `ActualDate`

- `POST /plants/v2/changegrowthphases` - Change plant growth phases
  - Use case: Move plants from vegetative to flowering
  - Request body: Array with plant labels, new growth phase, date

- `POST /plants/v2/destroyplants` - Destroy/waste plants
  - Use case: Remove plants due to disease, males, etc.
  - Request body: Array with plant labels, waste method, reason, weight

- `POST /plants/v2/manicureplants` - Record plant manicuring/trimming
  - Use case: Record wet weight after harvest/manicure
  - Request body: Array with plant labels, wet weight, date

- `POST /plants/v2/harvestplants` - Harvest plants
  - Use case: Harvest flowering plants for drying
  - Request body: Array with plant labels, harvest name, wet weight, date

### Additives

- `POST /plants/v2/additives` - Record additive applications
  - Use case: Log fertilizer/pesticide applications
  - Request body: Array with additive details, application date

- `POST /plants/v2/additives/byplants` - Record additives by plant tags
  - Use case: Apply additives to specific plants (vs. all in location)
  - Request body: Array with plant labels, additive type, amount

- `POST /plants/v2/additives/usingtemplate` - Record additives using template
  - Use case: Apply additives using predefined template
  - Request body: Array with template ID, plant labels, application date

- `POST /plants/v2/additives/bylocation/usingtemplate` - Record additives by location using template
  - Use case: Apply additives to all plants in location using template
  - Request body: Array with template ID, location, application date

---

## PUT Endpoints (4 endpoints)

### Plant Management

- `PUT /plants/v2/tag` - Replace plant tags
  - Use case: Replace damaged/lost RFID tags
  - Request body: Array with `PlantLabel`, `NewTag`, `TagDate`

- `PUT /plants/v2/split` - Split plant groups
  - Use case: Separate grouped plants into individuals
  - Request body: Array with source plants, split count, new tags

- `PUT /plants/v2/merge` - Merge plants
  - Use case: Combine multiple plants into one record
  - Request body: Array with plant labels to merge

- `PUT /plants/v2/strain` - Change plant strain
  - Use case: Correct strain assignment errors
  - Request body: Array with plant labels and new strain info

---

## Common Use Cases

### 1. Move Plants to Flowering Phase

```php
$plants = [
    [
        'Id' => 12345,
        'Label' => '1A4060300000001000000020',
        'NewLocation' => 'Flowering Room A',
        'GrowthPhase' => 'Flowering',
        'NewTag' => '1A4060300000001000000030',
        'GrowthDate' => '2025-01-15'
    ]
];

$api->post("/plants/v2/changegrowthphases?licenseNumber={$license}", $plants);
```

### 2. Harvest Flowering Plants

```php
$harvests = [
    [
        'Plant' => '1A4060300000001000000030',
        'Weight' => 450.5,
        'UnitOfMeasure' => 'Grams',
        'DryingLocation' => 'Drying Room 1',
        'HarvestName' => 'Blue Dream Harvest 2025-01-15',
        'ActualDate' => '2025-01-15'
    ]
];

$api->post("/plants/v2/harvestplants?licenseNumber={$license}", $harvests);
```

### 3. Destroy Male Plants

```php
$destroys = [
    [
        'Id' => 12345,
        'Label' => '1A4060300000001000000025',
        'WasteMethod' => 'Compost',
        'WasteReason' => 'Male',
        'ActualDate' => '2025-01-15'
    ]
];

$api->post("/plants/v2/destroyplants?licenseNumber={$license}", $destroys);
```

### 4. Check License Type Before Calling

```php
// ALWAYS check license type first!
$licenseType = explode('-', $license)[1]; // Extract 'C', 'P', or 'R'

if ($licenseType !== 'C') {
    throw new Exception("Plant endpoints require cultivation license. Current license: {$license}");
}

// Safe to call plant endpoints
$plants = $api->get("/plants/v2/flowering?licenseNumber={$license}");
```

---

## Important Notes

- **License verification**: ALWAYS check license type before calling any plant endpoint
- **Growth phases**: Clone → Seedling → Vegetative → Flowering (can skip intermediate)
- **Waste reasons**: Only available for cultivation licenses (not processing/retail)
- **Tags**: Must use available plant tags from `/tags/v2/plant/available`
- **Batch operations**: All POST/PUT accept arrays for efficiency
- **Harvest workflow**: Harvest plants → Create harvest → Create packages from harvest

---

## Related Categories

- `categories/plantbatches.md` - Plant batch endpoints (also cultivation-only)
- `categories/harvests.md` - Harvest endpoints
- `categories/tags.md` - Tag availability endpoints
- `patterns/license-types.md` - Complete license compatibility matrix

---

**For complete request/response details**, read `collections/metrc-plants.postman_collection.json`
