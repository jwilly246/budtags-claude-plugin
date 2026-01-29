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
$api = new MetrcApi();
$api->set_user($user);
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

    Log::info("Created " . count($newStrains) . " new strains");

    return redirect()->back()->with('message', count($newStrains) . ' strains created successfully');

} catch (\Exception $e) {
    Log::error("Strain creation failed: " . $e->getMessage());
    return redirect()->back()->with('error', $e->getMessage());
}
```

---

## Validation

```php
// Check if strain already exists
$existingStrains = $api->get("/strains/v2/active?licenseNumber={$license}");
$existingNames = array_column($existingStrains, 'Name');

foreach ($newStrains as $strain) {
    if (in_array($strain['Name'], $existingNames)) {
        throw new Exception("Strain '{$strain['Name']}' already exists");
    }

    // Validate percentages sum to 1.0 (100%)
    $total = $strain['IndicaPercentage'] + $strain['SativaPercentage'];
    if (abs($total - 1.0) > 0.01) {
        throw new Exception("Indica + Sativa must equal 100%");
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
