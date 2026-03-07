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
$api = app(\App\Services\Api\MetrcApi::class);
$api->set_user(request()->user());
$license = session('license');
$facility = session('facility');

// Check license type
$licenseType = explode('-', $license)[1];
if ($licenseType !== 'C') {
    return redirect()->back()->with('message', 'Plant tags only available for cultivation licenses');
}

// Get available plant tags
$availableTags = $api->get("/tags/v2/plant/available?licenseNumber={$license}");

if (count($availableTags) === 0) {
    return redirect()->back()->with('message', 'No plant tags available. Order more from Metrc.');
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

    LogService::store(
        'plant_tags_replaced',
        "Replaced " . count($tagReplacements) . " plant tags",
        null,
        request()->user()->active_org_id
    );

    return redirect()->back()->with('message', count($tagReplacements) . ' tags replaced successfully');

} catch (\Exception $e) {
    LogService::store(
        'plant_tags_replacement_failed',
        "Tag replacement failed: " . $e->getMessage(),
        null,
        request()->user()->active_org_id
    );

    return redirect()->back()->with('message', 'Failed to replace tags: ' . $e->getMessage());
}
```

---

## Validation

```php
// Ensure new tags are available
$availableTagLabels = array_column($availableTags, 'Label');

foreach ($tagReplacements as $replacement) {
    if (!in_array($replacement['NewTag'], $availableTagLabels)) {
        return redirect()->back()->with('message', "Tag {$replacement['NewTag']} not available");
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
