# Locations Category

**Collection File**: `collections/metrc-locations.postman_collection.json`
**Total Endpoints**: 7
**License Compatibility**: All license types

---

## GET Endpoints

- `GET /locations/v2/active` - Get all active locations
- `GET /locations/v2/types` - Get location types (Default, Planting, etc.)

---

## POST Endpoints

- `POST /locations/v2/create` - Create new locations
  - Use case: Add rooms, vaults, growing areas
  - Request body: Array with location name and type

---

## PUT Endpoints

- `PUT /locations/v2/update` - Update location details

---

## DELETE Endpoints

- `DELETE /locations/v2/{id}` - Delete location

---

## Example

```php
$newLocations = [
    ['Name' => 'Flowering Room A', 'LocationTypeName' => 'Planting'],
    ['Name' => 'Vault A', 'LocationTypeName' => 'Default']
];

$api->post("/locations/v2/create?licenseNumber={$license}", $newLocations);
```
