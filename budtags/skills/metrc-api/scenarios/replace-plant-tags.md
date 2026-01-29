# Scenario: Replace Plant Tags

**Goal**: Replace damaged or lost plant RFID tags

**License Compatibility**: ⚠️ **CULTIVATION LICENSES ONLY** (AU-C-######)

**Complexity**: Simple

**Prerequisites**:
- Plants with damaged/lost tags
- Available replacement plant tags

---

## Workflow

1. Get available plant tags
2. Identify plants needing tag replacement
3. Submit tag replacement request

---

## Implementation

### Step 1: Get Available Tags

```php
$api = new MetrcApi();
$api->set_user($user);
$license = session('license');

// Check license type
$licenseType = explode('-', $license)[1];
if ($licenseType !== 'C') {
    throw new Exception("Plant tags only available for cultivation licenses");
}

// Get available plant tags
$availableTags = $api->get("/tags/v2/plant/available?licenseNumber={$license}");

if (count($availableTags) === 0) {
    throw new Exception("No plant tags available. Order more from Metrc.");
}
```

### Step 2: Prepare Tag Replacements

```php
$tagReplacements = [
    [
        'PlantLabel' => '1A4060300000001000000010', // Old/damaged tag
        'NewTag' => $availableTags[0]['Label'], // New tag
        'TagDate' => now()->format('Y-m-d')
    ],
    [
        'PlantLabel' => '1A4060300000001000000011',
        'NewTag' => $availableTags[1]['Label'],
        'TagDate' => now()->format('Y-m-d')
    ]
];
```

### Step 3: Submit Replacements

**Endpoint**: `PUT /plants/v2/tag`

```php
try {
    $api->put("/plants/v2/tag?licenseNumber={$license}", $tagReplacements);

    Log::info("Replaced " . count($tagReplacements) . " plant tags");

    return redirect()->back()->with('message', count($tagReplacements) . ' tags replaced successfully');

} catch (\Exception $e) {
    Log::error("Tag replacement failed: " . $e->getMessage());
    return redirect()->back()->with('error', $e->getMessage());
}
```

---

## Validation

```php
// Ensure new tags are available
$availableTagLabels = array_column($availableTags, 'Label');

foreach ($tagReplacements as $replacement) {
    if (!in_array($replacement['NewTag'], $availableTagLabels)) {
        throw new Exception("Tag {$replacement['NewTag']} not available");
    }
}

// Ensure old tags exist
$allPlants = $api->get("/plants/v2/vegetative?licenseNumber={$license}");
$plantLabels = array_column($allPlants, 'Label');

foreach ($tagReplacements as $replacement) {
    if (!in_array($replacement['PlantLabel'], $plantLabels)) {
        throw new Exception("Plant {$replacement['PlantLabel']} not found");
    }
}
```

---

## Important Notes

- Old tag is consumed/retired
- New tag takes its place
- Plant history preserved with new tag
- Cannot reuse old tags

---

## Related

- `categories/plants.md` - Plant endpoints
- `categories/tags.md` - Tag management
- `patterns/license-types.md` - Cultivation license requirements
