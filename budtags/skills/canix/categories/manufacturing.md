# Manufacturing — Batches, Runs, Bills of Materials

Manufacturing endpoints cover the production side of cannabis operations — tracking batches, individual production runs (with inputs, outputs, labor, waste), and bills of materials (recipes). All endpoints are **read-only**.

**Note for BudTags integration**: Manufacturing data is deferred to a future PR. BudTags has `PackageRecipeTemplate` and `NonMetrcItem` which partially overlap with Canix's BOM and NCI concepts.

## Manufacturing Batch Endpoints (2 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/manu_batches` | List all manufacturing batches | Paginated |
| GET | `/manu_batches/{id}` | Get single batch | Includes run IDs |

## Manufacturing Run Endpoints (2 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/manu_batch_runs` | List all manufacturing runs | Paginated |
| GET | `/manu_batch_runs/{id}` | Get single run | MOST COMPLEX entity in Canix |

## Bill of Materials Endpoints (2 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/bills_of_materials` | List all BOMs | Paginated |
| GET | `/bills_of_materials/{id}` | Get single BOM | Source items + outputs |

## Manufacturing Batch Schema

A manufacturing batch is a container for one or more manufacturing runs.

```json
{
  "id": 2,
  "name": "Batch 2023-001",
  "template_name": "Standard Process Template",
  "status": "Run 3 of 3",
  "current_location": "processing room",
  "start_date": "2022-05-01",
  "end_date": "2022-05-30",
  "created_at": "2022-04-15T12:33:00.000Z",
  "updated_at": "2022-05-22T07:21:00.000Z",
  "notes": "notes about this batch",
  "manufacturing_run_ids": [8, 9, 10]
}
```

### Key Batch Fields

- **`template_name`** — Name of the template used to create this batch
- **`manufacturing_run_ids`** — Array of run IDs (fetch each via `/manu_batch_runs/{id}`)
- **`status`** — Free-form string (e.g., "Run 3 of 3")

## Manufacturing Run Schema (Most Complex Entity)

A single production run within a batch. Contains everything: cannabis inputs/outputs, non-cannabis inputs, labor, waste, and machine info.

```json
{
  "id": 10,
  "facility_id": 14,
  "name": "Stage 2",
  "status": "OPEN",
  "start_date": "2022-05-24",
  "end_date": "2022-05-30",
  "created_at": "2022-05-22T19:58:00.000Z",
  "updated_at": "2021-05-23T05:12:01.000Z",
  "location_id": 2,
  "bill_of_materials_id": 12,
  "manufacturing_batch_id": 9,
  "order": 2,
  "notes": "",
  "total_cannabis_costs": 14.30,
  "total_nci_costs": 2.50,
  "total_labor_costs": 9.05,
  "yield": 75.0,

  "machine_info": {
    "temperature": 20.1,
    "temperature_unit": "Celcius",
    "solvent_id": 150,
    "solvent_quantity": 10.5,
    "solvent_weight_unit": "Grams",
    "time_in_solvent_ms": 2400,
    "time_in_solvent_display_units": "Second"
  },

  "cannabis_inputs": [
    {
      "package_id": 3501,
      "package_tag": "1A4FF0000000022000000719",
      "quantity": 2.54,
      "weight_unit": "Grams",
      "psi": 600.0,
      "cost": 14.30
    }
  ],

  "non_cannabis_inputs": [
    {
      "non_cannabis_product_name": "Fertilizer",
      "non_cannabis_product_id": 145,
      "lot": "DL21309",
      "lot_id": 253,
      "quantity": 100.5,
      "weight_unit": "Grams",
      "cost": 2.50
    }
  ],

  "cannabis_outputs": [
    {
      "package_id": 5200,
      "package_tag": "1A4FF0000000022000001419",
      "quantity": 500,
      "weight_unit": "Grams"
    }
  ],

  "labors": [
    { "employee_name": "Jane Doe", "hours_worked": 0.5, "cost": 10 },
    { "employee_name": "John Doe", "hours_worked": 1, "cost": 20 }
  ],

  "wastes": [
    {
      "package_id": 4601,
      "package_tag": "1A4FF0000000022000004423",
      "quantity": 50,
      "weight_unit": "Grams",
      "reason": "Waste Destruction",
      "date": "2022-05-24",
      "notes": "waste from production"
    }
  ]
}
```

### Run Status Values

`OPEN`, `SUBMITTED`, `SUBMITTED_FOR_APPROVAL`, `ERRORED`

### Machine Info

| Field | Description |
|-------|-------------|
| `temperature` | Processing temperature |
| `temperature_unit` | `Celcius` or `Fahrenheit` (note: Canix spells it "Celcius") |
| `solvent_id` | NCI product ID used as solvent |
| `solvent_quantity` / `solvent_weight_unit` | Amount of solvent used |
| `time_in_solvent_ms` | Time in solvent (milliseconds) |
| `time_in_solvent_display_units` | `Week`, `Day`, `Hour`, `Minute`, `Second` |

### Cost Breakdown

| Field | Description |
|-------|-------------|
| `total_cannabis_costs` | Sum of `cannabis_inputs[].cost` |
| `total_nci_costs` | Sum of `non_cannabis_inputs[].cost` |
| `total_labor_costs` | Sum of `labors[].cost` |
| `yield` | Yield percentage |

## Bill of Materials Schema

BOMs define the recipe for a production run — what goes in (sources) and what comes out (outputs).

```json
{
  "id": 12,
  "name": "Bulk - Dark Chocolate Peaks - 10mg",
  "active_date": "2023-01-01",
  "expiration_date": "2023-12-31",
  "proportion_type": "single_instance",
  "last_updated_at": "2023-01-15T10:30:00.000Z",

  "source_non_cannabis_products": [
    {
      "name": "1/8th Jar",
      "non_cannabis_product_id": 24,
      "quantity": 1,
      "weight_unit": "Each",
      "application_setting": "proportional"
    },
    {
      "name": "Gloves - Large",
      "non_cannabis_product_id": 56,
      "quantity": 2,
      "weight_unit": "Each",
      "application_setting": "fixed"
    }
  ],

  "source_cannabis_items": [
    {
      "quantity": 20,
      "weight_unit": "Grams",
      "item": { "id": 242, "name": "Hammer Bud" },
      "item_category": null,
      "item_sub_category": null
    },
    {
      "quantity": 25,
      "weight_unit": "Grams",
      "item": null,
      "item_category": { "id": 98, "name": "B Buds" },
      "item_sub_category": null
    }
  ],

  "output_items": [
    {
      "name": "Jarred Flower",
      "item_id": 370,
      "quantity": 50,
      "weight_unit": "Grams"
    }
  ]
}
```

### BOM Key Concepts

- **`proportion_type`**: `single_instance` (materials per output) vs `all_instances` (materials across all outputs)
- **`application_setting`** on NCI sources: `proportional` (scales with output qty) vs `fixed` (constant regardless of qty)
- **Cannabis source items** can reference a specific `item` OR an `item_category`/`item_sub_category` (flexible sourcing)
- **Output items** define what the run produces

### BudTags Mapping (Future PR)

| Canix Concept | BudTags Equivalent |
|---------------|-------------------|
| `BillOfMaterials` | `PackageRecipeTemplate` |
| `source_non_cannabis_products` | `PackageRecipeTemplateComponent` |
| `proportion_type` | `deduction_type` (per_unit / per_case) |
| `NonCannabisProduct` | `NonMetrcItem` |
| `source_cannabis_items` | Not supported (BudTags BOMs are NCI-only) |
| `output_items` | Not modeled (output is the Metrc package) |

---

**See:** `categories/products-items.md` for items and non-cannabis products referenced by manufacturing
**See:** `scenarios/manufacturing-import-workflow.md` for import workflow
