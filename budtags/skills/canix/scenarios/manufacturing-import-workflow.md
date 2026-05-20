# Scenario: Import Manufacturing Data from Canix

This workflow imports manufacturing batches, runs, and bills of materials from Canix. This maps to BudTags' recipe and packaging materials system.

**Status**: Deferred to future PR. This scenario documents the workflow for planning purposes.

## Prerequisites

- Canix API key configured
- Non-cannabis products already imported (referenced by BOM and run NCI inputs)
- Items already imported (referenced by BOM source cannabis items and run inputs/outputs)

## Import Order

```
1. bills_of_materials → Maps to PackageRecipeTemplate (recipe templates)
2. manu_batches       → Container entity (batch metadata)
3. manu_batch_runs    → Detail entity (inputs, outputs, labor, waste)
```

## Step 1: Import Bills of Materials → Recipes

```php
$boms = $api->get('/bills_of_materials');

collect($boms)->each(function (array $bom) use ($org_id) {
    // Map to PackageRecipeTemplate
    $template = PackageRecipeTemplate::updateOrCreate(
        ['organization_id' => $org_id, 'canix_bom_id' => $bom['id']],
        [
            'name'        => $bom['name'],
            'description' => "Imported from Canix. Proportion: {$bom['proportion_type']}",
        ],
    );

    // Map source_non_cannabis_products → PackageRecipeTemplateComponent
    collect($bom['source_non_cannabis_products'] ?? [])->each(function (array $source) use ($template, $org_id) {
        $nci = NonMetrcItem::where('organization_id', $org_id)
            ->where('canix_id', $source['non_cannabis_product_id'])
            ->first();

        if ($nci) {
            PackageRecipeTemplateComponent::updateOrCreate(
                ['recipe_template_id' => $template->id, 'non_metrc_item_id' => $nci->id],
                [
                    'quantity_needed' => $source['quantity'],
                    'deduction_type'  => $source['application_setting'] === 'proportional' ? 'per_unit' : 'per_case',
                ],
            );
        }
    });
});
```

### BOM Mapping Details

| Canix BOM | BudTags | Notes |
|-----------|---------|-------|
| `name` | `PackageRecipeTemplate.name` | Direct |
| `proportion_type` | — | `single_instance` ≈ per_unit, `all_instances` ≈ per_case |
| `active_date` / `expiration_date` | — | Not supported in BudTags (gap) |
| `source_non_cannabis_products[]` | `PackageRecipeTemplateComponent` | Direct mapping |
| `source_cannabis_items[]` | — | **NOT supported** (BudTags BOMs are NCI-only) |
| `output_items[]` | — | **NOT modeled** (output is the Metrc package) |

### Gaps to Address in Future PR

1. BudTags has no date range on recipe templates (`active_date` / `expiration_date`)
2. BudTags BOMs don't track cannabis input items (only NCI components)
3. BudTags doesn't model explicit output items
4. The `application_setting` (proportional vs fixed) maps approximately to `deduction_type` but isn't exactly 1:1

## Step 2: Import Manufacturing Batches

```php
$batches = $api->get('/manu_batches');

collect($batches)->each(function (array $batch) {
    // Store batch metadata — may need a new model or JSON storage
    // Key data: template_name, status, date range, manufacturing_run_ids
    // Currently no BudTags equivalent for the batch container entity
});
```

### Batch Storage Options (Future Decision)

1. **New `CanixManuBatch` model** — dedicated table for manufacturing batch tracking
2. **JSON field on existing model** — store batch data as structured JSON
3. **Skip batch, import runs only** — batch is just a container

## Step 3: Import Manufacturing Runs

Manufacturing runs are the most complex entity in the Canix API:

```php
$runs = $api->get('/manu_batch_runs');

collect($runs)->each(function (array $run) use ($org_id) {
    // Cannabis inputs: package_id, tag, quantity, weight_unit, psi, cost
    $cannabis_inputs = collect($run['cannabis_inputs'] ?? []);

    // Non-cannabis inputs: product_id, lot, quantity, weight_unit, cost
    $nci_inputs = collect($run['non_cannabis_inputs'] ?? []);

    // Cannabis outputs: package_id, tag, quantity, weight_unit
    $cannabis_outputs = collect($run['cannabis_outputs'] ?? []);

    // Labor: employee_name, hours_worked, cost
    $labors = collect($run['labors'] ?? []);

    // Waste: package_id, tag, quantity, weight_unit, reason, date, notes
    $wastes = collect($run['wastes'] ?? []);

    // Machine info: temperature, solvent, time
    $machine = $run['machine_info'] ?? null;

    // Cost breakdown
    $total_cost = ($run['total_cannabis_costs'] ?? 0)
                + ($run['total_nci_costs'] ?? 0)
                + ($run['total_labor_costs'] ?? 0);

    // Storage TBD — needs new models or JSON storage
});
```

### Run Data That Has No BudTags Equivalent

| Canix Run Data | BudTags Status |
|----------------|---------------|
| `cannabis_inputs` (with PSI, cost per input) | Not tracked — only `production_batch_number` string |
| `non_cannabis_inputs` (with lot tracking) | Partially: `NonMetrcInventoryLog` tracks NCI deductions |
| `cannabis_outputs` | Not tracked separately |
| `labors` (employee, hours, cost) | Not tracked |
| `wastes` (reason, date, notes) | Not tracked |
| `machine_info` (temp, solvent, time) | Not tracked |
| Cost breakdown by type | Not tracked at this granularity |

## Recommended Approach for Future PR

1. **Phase 1**: Import BOMs → `PackageRecipeTemplate` + components (NCI portion only)
2. **Phase 2**: New model(s) for manufacturing batch tracking
3. **Phase 3**: Integrate cannabis inputs/outputs with Metrc package data
4. **Phase 4**: Labor and waste tracking (if business need exists)

## Data Volume Considerations

Manufacturing data can be very large for processing facilities:
- Hundreds of BOMs
- Thousands of manufacturing runs
- Each run may have 10-50 cannabis inputs
- Import pagination is critical

---

**See:** `categories/manufacturing.md` for complete endpoint details and schemas
**See:** `categories/products-items.md` for items and NCI referenced by manufacturing
**See:** `categories/inventory.md` for packages referenced as inputs/outputs
