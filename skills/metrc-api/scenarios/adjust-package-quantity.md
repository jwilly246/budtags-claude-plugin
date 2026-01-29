# Scenario: Adjust Package Quantity

**Goal**: Record inventory adjustments (waste, damage, drying loss, etc.)

**License Compatibility**: All license types

**Complexity**: Simple

**Prerequisites**:
- Active package
- Adjustment reason
- Quantity to adjust

---

## Workflow

1. Identify package to adjust
2. Determine adjustment amount (positive or negative)
3. Select adjustment reason
4. Submit adjustment

---

## Implementation

### Common Adjustment Scenarios

```php
$api = new MetrcApi();
$api->set_user($user);
$license = session('license');

// Scenario 1: Weight loss from drying
$dryingAdjustment = [
    [
        'Label' => '1A4060300000001000000050',
        'Quantity' => -15.5, // Negative = reduction
        'UnitOfMeasure' => 'Grams',
        'AdjustmentReason' => 'Drying',
        'AdjustmentDate' => now()->format('Y-m-d'),
        'ReasonNote' => 'Weight loss during drying process'
    ]
];

// Scenario 2: Damaged product
$damageAdjustment = [
    [
        'Label' => '1A4060300000001000000051',
        'Quantity' => -10.0,
        'UnitOfMeasure' => 'Grams',
        'AdjustmentReason' => 'Waste',
        'AdjustmentDate' => now()->format('Y-m-d'),
        'ReasonNote' => 'Product damaged during handling'
    ]
];

// Scenario 3: Inventory reconciliation (increase)
$reconciliationAdjustment = [
    [
        'Label' => '1A4060300000001000000052',
        'Quantity' => 2.5, // Positive = increase
        'UnitOfMeasure' => 'Grams',
        'AdjustmentReason' => 'Inventory Count Adjustment',
        'AdjustmentDate' => now()->format('Y-m-d'),
        'ReasonNote' => 'Found during physical inventory count'
    ]
];
```

### Submit Adjustment

**Endpoint**: `POST /packages/v2/adjust`

```php
try {
    $api->post("/packages/v2/adjust?licenseNumber={$license}", $dryingAdjustment);

    Log::info("Package adjusted: {$dryingAdjustment[0]['Label']}");

    return redirect()->back()->with('message', 'Package adjusted successfully');

} catch (\Exception $e) {
    Log::error("Package adjustment failed: " . $e->getMessage());
    return redirect()->back()->with('error', $e->getMessage());
}
```

---

## Batch Adjustments

```php
// Adjust multiple packages at once
$batchAdjustments = [
    ['Label' => 'TAG-001', 'Quantity' => -1.5, 'UnitOfMeasure' => 'Grams', 'AdjustmentReason' => 'Drying', 'AdjustmentDate' => now()->format('Y-m-d')],
    ['Label' => 'TAG-002', 'Quantity' => -2.0, 'UnitOfMeasure' => 'Grams', 'AdjustmentReason' => 'Drying', 'AdjustmentDate' => now()->format('Y-m-d')],
    ['Label' => 'TAG-003', 'Quantity' => -1.8, 'UnitOfMeasure' => 'Grams', 'AdjustmentReason' => 'Drying', 'AdjustmentDate' => now()->format('Y-m-d')],
];

$api->post("/packages/v2/adjust?licenseNumber={$license}", $batchAdjustments);
```

---

## Common Adjustment Reasons

- **Drying** - Weight loss during drying/curing
- **Waste** - Damaged, spoiled, or discarded product
- **Inventory Count Adjustment** - Reconciliation from physical count
- **Sampling** - Product removed for testing
- **Moisture Rehydration** - Weight gain from moisture
- **Scale Variance** - Correction from scale calibration

---

## Important Notes

- Negative quantities reduce inventory
- Positive quantities increase inventory (use sparingly)
- Always provide ReasonNote for audit trail
- Cannot adjust finished packages (must unfinish first)

---

## Related

- `categories/packages.md` - Package endpoints
- `patterns/batch-operations.md` - Batch processing
