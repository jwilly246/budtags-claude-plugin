# Sublocations Category

**Collection File**: `collections/metrc-sublocations.postman_collection.json`
**Total Endpoints**: 6
**License Compatibility**: All license types

---

## GET Endpoints

- `GET /sublocations/v2/active` - Get active sublocations

---

## POST Endpoints

- `POST /sublocations/v2/create` - Create sublocations
  - Use case: Create subdivisions within locations (shelves, rows, etc.)

---

## PUT Endpoints

- `PUT /sublocations/v2/update` - Update sublocation details

---

## DELETE Endpoints

- `DELETE /sublocations/v2/{id}` - Delete sublocation

---

## Example

```php
$sublocations = [
    ['Name' => 'Shelf A1', 'LocationName' => 'Vault A'],
    ['Name' => 'Shelf A2', 'LocationName' => 'Vault A']
];

$api->post("/sublocations/v2/create?licenseNumber={$license}", $sublocations);
```
