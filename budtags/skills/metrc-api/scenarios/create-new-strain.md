# Scenario: Create New Strain

**Goal**: Add custom strain genetics to facility

**License Compatibility**: All license types

**Complexity**: Simple

**Prerequisites**:
- Strain name
- Indica/Sativa percentages
- Optional: THC/CBD levels

---

## Implementation

### Step 1: Prepare Strain Data

```php
$api = app(\App\Services\Api\MetrcApi::class);
$api->set_user(request()->user());
$license = session('license');

$newStrains = [
    [
        'Name' => 'Blue Dream',
        'TestingStatus' => 'None', // or 'ThirdParty'
        'ThcLevel' => 0.22, // 22% THC
        'CbdLevel' => 0.01, // 1% CBD
        'IndicaPercentage' => 0.4, // 40% Indica
        'SativaPercentage' => 0.6  // 60% Sativa
    ],
    [
        'Name' => 'OG Kush',
        'TestingStatus' => 'None',
        'ThcLevel' => 0.24,
        'CbdLevel' => 0.01,
        'IndicaPercentage' => 0.75,
        'SativaPercentage' => 0.25
    ]
];
```

### Step 2: Submit to Metrc

**Endpoint**: `POST /strains/v2/create`

```php
try {
    $api->post("/strains/v2/create?licenseNumber={$license}", $newStrains);

    LogService::store(
        'strains_created',
        "Created " . count($newStrains) . " new strains",
        null,
        request()->user()->active_org_id
    );

    return redirect()->back()->with('message', count($newStrains) . ' strains created successfully');

} catch (\Exception $e) {
    LogService::store(
        'strains_creation_failed',
        "Strain creation failed: " . $e->getMessage(),
        null,
        request()->user()->active_org_id
    );

    return redirect()->back()->with('message', 'Failed to create strains: ' . $e->getMessage());
}
```

---

## Validation

```php
// Check if strain already exists
$existingStrains = $api->strains(session('facility'));
$existingNames = array_column($existingStrains, 'Name');

foreach ($newStrains as $strain) {
    if (in_array($strain['Name'], $existingNames)) {
        return redirect()->back()->with('message', "Strain '{$strain['Name']}' already exists");
    }

    // Validate percentages sum to 1.0 (100%)
    $total = $strain['IndicaPercentage'] + $strain['SativaPercentage'];
    if (abs($total - 1.0) > 0.01) {
        return redirect()->back()->with('message', 'Indica + Sativa must equal 100%');
    }
}
```

---

## Strain Types

- **Indica-Dominant**: `IndicaPercentage > 0.5`
- **Sativa-Dominant**: `SativaPercentage > 0.5`
- **Hybrid**: `IndicaPercentage ≈ SativaPercentage`

---

## Related

- `categories/strains.md` - Strain endpoints
