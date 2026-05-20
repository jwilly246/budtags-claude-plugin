# Products & Items

Items are Canix's equivalent of BudTags Products — they represent cannabis and non-cannabis products tracked in the system. This category also covers item types, sub-types, brands, and non-cannabis products.

## Item Endpoints (10 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/items` | List items | Supports `facility_id` filter |
| POST | `/items` | Create item | ⚠️ WRITE |
| GET | `/items/{id}` | Get single item | Rich schema with strain, type, brand |
| PUT | `/items/{id}` | Update item | ⚠️ WRITE |
| DELETE | `/items/{id}` | Delete item | ⚠️ WRITE, returns 204 |
| POST | `/items/{id}/standard_cost` | Add standard cost | ⚠️ WRITE |
| POST | `/items/photos` | Upload METRC photos | ⚠️ ASYNC (Submissions) |
| POST | `/items/files` | Upload METRC files | ⚠️ ASYNC (Submissions) |

## Reference Data Endpoints (4 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/item_types` | List item types | Supports `facility_id`, includes requirement flags |
| GET | `/item_sub_types` | List sub-types | Supports `facility_id` |
| GET | `/brands` | List brands | Simple id/name |

## Non-Cannabis Product Endpoints (3 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/non_cannabis_products` | List NCIs | Supports `facility_ids` (plural, array) |
| GET | `/non_cannabis_products/{id}` | Get single NCI | Category, standard costing |
| GET | `/non_cannabis_products/{id}/boms` | Get BOMs for NCI | Bill of materials |

## Item Response Schema

```json
{
  "id": 7036,
  "name": "Blue Dream - Trim",
  "is_active": true,
  "sku": "22657",
  "facility_id": 14,
  "item_type": "Clone - Cutting",
  "quantity_type": "CountBased",
  "notes": "",
  "accounting_inventory_type": "raw_materials",
  "description": "Clone",
  "phenotype": "Indica",
  "allergens": "Can s 2",
  "transfer_source_license": "1234567890",
  "weight_unit": "Each",
  "unit_weight": 10,
  "unit_weight_unit": "Grams",
  "case_quantity": 100,
  "case_unit": "Each",
  "unit_thc_weight": 5.0,
  "unit_thc_weight_unit": "mg",
  "unit_cbd_weight": 10.5,
  "unit_cbd_weight_unit": "mg",
  "unit_thc_percent": 20.0,
  "unit_cbd_percent": 15.5,
  "serving_size": "1g",
  "number_of_doses": 10,
  "public_ingredients": "Cannabis extract, MCT oil",
  "supply_duration_days": 30,
  "administration_method": "oral",
  "type": {
    "id": 884,
    "name": "Clone - Cutting",
    "quantity_type": "CountBased",
    "product_category": "Plants"
  },
  "sub_type": null,
  "brand": null,
  "strain": null,
  "current_standard_cost": {
    "id": 123,
    "standard_cost_amount": 12.11,
    "standard_cost_currency": "USD",
    "start_date": "2023-04-19",
    "end_date": "2023-05-19"
  },
  "total_for_sale": 100,
  "ordered": 25,
  "backordered": 10,
  "unordered": 75,
  "sage_item": { "external_id": "...", "name": "..." },
  "leaflink_item": null,
  "dutchie_product": null,
  "bills_of_materials": [
    { "url": "...", "name": "...", "package_weight": 10, "unit": "g" }
  ],
  "updated_at": "2021-03-16T23:49:03.175Z"
}
```

### Key Item Fields

- **Quantity tracking**: `total_for_sale`, `ordered`, `backordered`, `unordered`
- **External integrations**: `sage_item`, `leaflink_item`, `dutchie_product` (nullable objects)
- **THC/CBD at item level**: `unit_thc_weight`, `unit_thc_percent`, `unit_cbd_weight`, `unit_cbd_percent`
- **Product metadata**: `phenotype`, `allergens`, `administration_method`, `public_ingredients`, `supply_duration_days`
- **`transfer_source_license`** — Originating facility license (non-editable)
- **`accounting_inventory_type`** — e.g., `raw_materials`, `finished_good`

## CreateItemRequestBody

**Required fields**: `name`, `item_type_id`, `weight_unit`

```json
{
  "name": "Blue Dream",
  "item_type_id": 1,
  "weight_unit": "g",
  "is_active": true,
  "strain_id": 1,
  "item_sub_type_id": 2,
  "brand_id": 3,
  "sku": "BD001",
  "unit_weight": 1.5,
  "unit_weight_unit": "mg",
  "description": "High quality strain",
  "notes": "Special handling",
  "serving_size": "1 capsule",
  "number_of_doses": 30,
  "unit_thc_weight": 5.0,
  "unit_cbd_weight": 10.5,
  "unit_thc_percent": 20.0,
  "unit_cbd_percent": 15.5,
  "public_ingredients": "Cannabis extract, MCT oil",
  "supply_duration_days": 30,
  "administration_method": "oral",
  "unit_thc_weight_unit": "mg",
  "unit_cbd_weight_unit": "mg",
  "accounting_inventory_type": "finished_good",
  "photo_ids": [1, 2, 3],
  "metrc_item_brand": "Brand #1"
}
```

## UpdateItemRequestBody

Same fields as create but **nothing is required** — only send fields you want to change. Note: uses `item_category_id` and `item_sub_category_id` (not `item_type_id` / `item_sub_type_id`).

## ItemType Schema

```json
{
  "id": 884,
  "name": "Clone - Cutting",
  "quantity_type": "CountBased",
  "requires_strain": true,
  "requires_unit_volume": false,
  "requires_unit_weight": true,
  "requires_unit_thc_weight": false,
  "requires_unit_cbd_weight": false,
  "requires_unit_thc_percent": false,
  "requires_unit_cbd_percent": false,
  "requires_public_ingredients": false,
  "requires_administration_method": false,
  "requires_serving_size": false,
  "requires_supply_duration_days": false,
  "requires_number_of_doses": false,
  "updated_at": "2018-11-06T08:00:00.000Z"
}
```

The `requires_*` flags indicate which fields are mandatory when creating items of this type.

## ItemSubType Schema

```json
{
  "id": 1,
  "name": "Indica",
  "weight_unit": "Grams",
  "category": { "id": 884, "name": "Clone - Cutting", ... },
  "updated_at": "2018-11-06T08:00:00.000Z"
}
```

## Brand Schema

```json
{ "id": 1, "name": "Premium Brand", "updated_at": "2018-11-06T08:00:00.000Z" }
```

## NonCannabisProduct Schema

```json
{
  "id": 123,
  "name": "1/8th Jar",
  "is_active": true,
  "sku": "0.5EC",
  "notes": "Special handling",
  "available_quantity": 196,
  "weight_unit": "Each",
  "par": 100,
  "category": { "id": 1, "name": "Preroll Materials" },
  "location": { "id": 5, "name": "Storage" },
  "facilities": [...],
  "current_standard_costing": {
    "id": 123, "standard_cost_amount": 12.11,
    "standard_cost_currency": "USD", "start_date": "2023-04-19"
  },
  "submits_to_metrc": false,
  "additive_type": "fertilizer",
  "product_trade_name": "...",
  "epa_registration_name": "...",
  "product_supplier": "...",
  "application_device": "...",
  "active_ingredients": [{ "name": "...", "percentage": 0.5 }],
  "updated_at": "2018-11-06T08:00:00.000Z"
}
```

**BudTags mapping**: NonCannabisProduct → `NonMetrcItem` (packaging materials/supplies)

## METRC Item Photos Upload

```json
{
  "facility_id": 123,
  "photos": [
    {
      "attachment_type": "product",
      "filename": "photo.jpg",
      "encoded_image_base64": "base64string..."
    }
  ]
}
```

`attachment_type` must be one of: `product`, `label`, `packaging`

Returns `{ photo_ids: [1, 2, 3] }` — these IDs can be used in `CreateItemRequestBody.photo_ids`.

**Note**: This is an async operation that goes through Metrc. Poll the returned submission UUID.

## Standard Cost

```json
{
  "cost": 10.50,
  "start_date": "2024-02-03T00:00:00Z",
  "end_date": "2024-12-31T23:59:59Z"
}
```

**Required fields**: `cost`, `start_date`. `end_date` is optional.

Also see: `GET/PUT/DELETE /standard_costs/{id}` in `categories/logistics-system.md`

---

**See:** `scenarios/product-import-workflow.md` for complete import workflow
**See:** `categories/cultivation.md` for strains (referenced by items)
**See:** `patterns/facility-scoping.md` for facility_id filtering on items
