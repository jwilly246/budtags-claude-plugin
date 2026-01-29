# Harvests Category

**Collection File**: `collections/metrc-harvests.postman_collection.json`
**Total Endpoints**: 15
**License Compatibility**: Cultivation (full), Processing (limited)

---

## GET Endpoints

### Retrieve Harvests

- `GET /harvests/v2/{id}` - Get harvest by ID
- `GET /harvests/v2/active` - Get all active harvests
- `GET /harvests/v2/onhold` - Get harvests on hold
- `GET /harvests/v2/inactive` - Get inactive/finished harvests

### Waste Data

- `GET /harvests/v2/waste` - Get harvest waste records
- `GET /harvests/v2/waste/types` - Get harvest waste types

---

## POST Endpoints

### Create Packages from Harvest

- `POST /harvests/v2/packages` - Create packages from harvest
  - **Most common operation**: Convert harvest weight into sellable packages
  - Request body: Array of package objects with tags, items, weights

- `POST /harvests/v2/packages/testing` - Create testing packages from harvest
  - Use case: Create sample packages for lab testing/COA

### Waste Management

- `POST /harvests/v2/waste` - Record harvest waste
  - Use case: Record trim, stems, unusable material
  - Request body: Array with waste weight, method, reason

- `POST /harvests/v2/removewaste` - Remove previously recorded waste
  - Use case: Correct waste recording errors

---

## PUT Endpoints

### Harvest Management

- `PUT /harvests/v2/rename` - Rename harvest
  - Use case: Update harvest naming convention

- `PUT /harvests/v2/finish` - Finish harvest
  - Use case: Mark harvest as complete after all packages created

- `PUT /harvests/v2/unfinish` - Unfinish previously finished harvest
  - Use case: Reopen harvest to create additional packages

- `PUT /harvests/v2/move` - Move harvest to new location
  - Use case: Relocate drying/curing harvest

---

## Common Workflow

```php
// 1. Create harvest (done via plants/v2/harvestplants)
// 2. Wait for drying/curing period
// 3. Create packages from harvest weight
$packages = [
    [
        'Tag' => '1A4060300000001000000050',
        'Location' => 'Vault A',
        'Item' => 'Blue Dream Flower',
        'Quantity' => 450.5,
        'UnitOfMeasure' => 'Grams',
        'ActualDate' => '2025-01-15',
        'Ingredients' => [
            [
                'HarvestName' => 'Blue Dream Harvest 2025-01-15',
                'Weight' => 450.5,
                'UnitOfMeasure' => 'Grams'
            ]
        ]
    ]
];

$api->post("/harvests/v2/packages?licenseNumber={$license}", $packages);

// 4. Finish harvest when all packages created
$api->put("/harvests/v2/finish?licenseNumber={$license}", [
    ['Name' => 'Blue Dream Harvest 2025-01-15', 'ActualDate' => '2025-01-15']
]);
```

---

## Related Categories

- `categories/plants.md` - Harvesting plants creates harvests
- `categories/packages.md` - Harvest packages
- `scenarios/create-packages-from-harvest.md` - Complete workflow
