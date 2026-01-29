# Strains Category

**Collection File**: `collections/metrc-strains.postman_collection.json`
**Total Endpoints**: 6
**License Compatibility**: All license types

---

## GET Endpoints

- `GET /strains/v2/active` - Get all active strains
- `GET /strains/v2/{id}` - Get strain by ID

---

## POST Endpoints

- `POST /strains/v2/create` - Create new strains
  - Use case: Add custom strain genetics to facility
  - Request body: Array with strain name, type (Indica/Sativa/Hybrid)

---

## PUT Endpoints

- `PUT /strains/v2/update` - Update strain details

---

## DELETE Endpoints

- `DELETE /strains/v2/{id}` - Delete strain

---

## Example

```php
$newStrains = [
    [
        'Name' => 'Blue Dream',
        'TestingStatus' => 'None',
        'ThcLevel' => 0.22,
        'CbdLevel' => 0.01,
        'IndicaPercentage' => 0.4,
        'SativaPercentage' => 0.6
    ]
];

$api->post("/strains/v2/create?licenseNumber={$license}", $newStrains);
```

---

## Related

- `scenarios/create-new-strain.md` - Strain creation workflow
