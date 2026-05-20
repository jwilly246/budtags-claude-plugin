# Scenario: Import Products/Items from Canix

This workflow imports Canix items into BudTags `Product` records and reference data (item types, sub-types, brands) into their respective tables.

## Prerequisites

- Canix API key configured
- Organization context established

## Import Order (Dependencies)

Reference data must be imported first:

```
1. item_types      → CanixItemType (no dependencies)
2. item_sub_types  → CanixItemSubType (links to item_types)
3. brands          → CanixBrand (no dependencies)
4. strains         → Strain with canix_id (no dependencies)
5. items           → Product with canix_item_id (depends on above)
6. non_cannabis    → NonMetrcItem with canix_id (no dependencies)
```

## Step 1: Import Reference Data

### Item Types

```php
$types = $api->get('/item_types', [
    'facility_id' => $facility_id,
    'limit' => 2000,
]);

collect($types)->each(function (array $type) {
    CanixItemType::updateOrCreate(
        ['id' => $type['id']],
        ['name' => $type['name']],
    );
});
```

### Item Sub-Types

```php
$sub_types = $api->get('/item_sub_types', [
    'facility_id' => $facility_id,
    'limit' => 2000,
]);

collect($sub_types)->each(function (array $sub) {
    CanixItemSubType::updateOrCreate(
        ['id' => $sub['id']],
        [
            'name' => $sub['name'],
            'canix_item_type_id' => $sub['category']['id'] ?? null,
        ],
    );
});
```

### Brands

```php
$brands = $api->get('/brands', ['limit' => 2000]);

collect($brands)->each(function (array $brand) {
    CanixBrand::updateOrCreate(
        ['id' => $brand['id']],
        ['name' => $brand['name']],
    );
});
```

### Strains

```php
$strains = $api->get('/strains', [
    'facility_id' => $facility_id,
    'limit' => 2000,
]);

collect($strains)->each(function (array $strain) use ($org_id) {
    Strain::updateOrCreate(
        ['organization_id' => $org_id, 'canix_id' => $strain['id']],
        [
            'name' => $strain['name'],
            'indica_percent' => $strain['indica_percent'] ?? null,
            'sativa_percent' => $strain['sativa_percent'] ?? null,
        ],
    );
});
```

## Step 2: Import Items → Products

```php
$offset = 0;
$limit = 2000;

do {
    $items = $api->get('/items', array_filter([
        'facility_id' => $facility_id,
        'limit' => $limit,
        'offset' => $offset,
        'where' => $modified_since ? "updated_at >= '{$modified_since}'" : null,
        'order_by' => 'id asc',
    ]));

    collect($items)->each(function (array $item) use ($ctx) {
        $this->process_item($item, $ctx);
        $ctx->increment_progress();
    });

    $offset += $limit;
} while (count($items) === $limit);
```

### Process Individual Item

```php
private function process_item(array $item, ImportContext $ctx): void
{
    $existing = $ctx->product_cache[$item['id']] ?? null;

    $product_data = [
        'organization_id'        => $ctx->org_id,
        'canix_item_id'          => $item['id'],
        'name'                   => $item['name'],
        'sku'                    => $item['sku'] ?? null,
        'description'            => $item['description'] ?? null,
        'canix_brand_id'         => $item['brand']['id'] ?? null,
        'canix_item_type_id'     => $item['type']['id'] ?? null,
        'canix_item_sub_type_id' => $item['sub_type']['id'] ?? null,
        'strain_name'            => $item['strain']['name'] ?? null,
        'unit_weight'            => $item['unit_weight'] ?? null,
        'unit_weight_uom'        => $item['unit_weight_unit'] ?? null,
        'thc_mg'                 => $item['unit_thc_weight'] ?? null,
        'cbd_mg'                 => $item['unit_cbd_weight'] ?? null,
        // Product metadata (Canix-specific)
        'allergens'              => $item['allergens'] ?? null,
        'phenotype'              => $item['phenotype'] ?? null,
        'administration_method'  => $item['administration_method'] ?? null,
        'public_ingredients'     => $item['public_ingredients'] ?? null,
        'supply_duration_days'   => $item['supply_duration_days'] ?? null,
    ];

    if ($existing) {
        $existing->update($product_data);
        $ctx->stats['updated']++;
    } else {
        $ctx->products_to_insert[] = $product_data;
        $ctx->stats['created']++;
    }
}
```

### Key Field Mappings

| Canix Item Field | BudTags Product Field | Notes |
|------------------|----------------------|-------|
| `id` | `canix_item_id` | Integer FK |
| `name` | `name` | Direct |
| `sku` | `sku` | Direct |
| `description` | `description` | Direct |
| `brand.id` | `canix_brand_id` | FK to CanixBrand |
| `type.id` | `canix_item_type_id` | FK to CanixItemType |
| `sub_type.id` | `canix_item_sub_type_id` | FK to CanixItemSubType |
| `strain.name` | `strain_name` | String (not FK) |
| `unit_weight` | `unit_weight` | Numeric |
| `unit_weight_unit` | `unit_weight_uom` | String |
| `unit_thc_weight` | `thc_mg` | Numeric (THC per unit) |
| `unit_cbd_weight` | `cbd_mg` | Numeric (CBD per unit) |
| `allergens` | `allergens` | New column |
| `phenotype` | `phenotype` | New column |
| `administration_method` | `administration_method` | New column |
| `public_ingredients` | `public_ingredients` | New column |
| `supply_duration_days` | `supply_duration_days` | New column |

### Skipped Item Fields

These fields are available but not imported:
- `unit_thc_percent` / `unit_cbd_percent` — No matching column, and Metrc provides this
- `accounting_inventory_type` — Internal Canix classification
- `sage_item` / `leaflink_item` / `dutchie_product` — External integrations irrelevant to BudTags
- `total_for_sale` / `ordered` / `backordered` / `unordered` — Dynamic quantities (not persisted)
- `transfer_source_license` — Metrc domain
- `serving_size` / `number_of_doses` — Future consideration

## Step 3: Import Non-Cannabis Products → NonMetrcItem

```php
$nci_products = $api->get('/non_cannabis_products', [
    'facility_ids' => [$facility_id],
    'limit' => 2000,
]);

collect($nci_products)->each(function (array $nci) use ($org_id) {
    NonMetrcItem::updateOrCreate(
        ['organization_id' => $org_id, 'canix_id' => $nci['id']],
        [
            'name'             => $nci['name'],
            'category'         => $this->map_nci_category($nci['category']['name'] ?? 'Other'),
            'current_quantity' => $nci['available_quantity'] ?? 0,
            'min_quantity'     => $nci['par'] ?? 0,
            'cost_per_unit'    => $nci['current_standard_costing']['standard_cost_amount'] ?? 0,
            'unit_of_measure'  => $this->map_weight_unit($nci['weight_unit']),
            'description'      => $nci['notes'] ?? null,
        ],
    );
});
```

### NCI Category Mapping

```php
private function map_nci_category(string $canix_category): string
{
    // BudTags categories: Packaging, Labels, Papers, Tubes, Bags, Boxes, Stickers, Other
    return match (true) {
        str_contains($canix_category, 'Preroll')    => 'Packaging',
        str_contains($canix_category, 'Packaging')  => 'Packaging',
        str_contains($canix_category, 'Label')      => 'Labels',
        str_contains($canix_category, 'Paper')      => 'Papers',
        str_contains($canix_category, 'Tube')       => 'Tubes',
        str_contains($canix_category, 'Bag')        => 'Bags',
        str_contains($canix_category, 'Box')        => 'Boxes',
        str_contains($canix_category, 'Sticker')    => 'Stickers',
        default                                      => 'Other',
    };
}
```

## Error Handling

- Missing `type` on item: log warning, set `canix_item_type_id = null`
- Duplicate SKU: updateOrCreate handles this via `canix_item_id` unique index
- `facility_ids` (plural!) for non-cannabis products — note the different param name

---

**See:** `categories/products-items.md` for complete endpoint details
**See:** `categories/cultivation.md` for strain details
**See:** `patterns/facility-scoping.md` for facility_id usage
