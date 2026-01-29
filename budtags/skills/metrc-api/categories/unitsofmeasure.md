# Units of Measure Category

**Collection File**: `collections/metrc-unitsofmeasure.postman_collection.json`
**Total Endpoints**: 2
**License Compatibility**: All license types

---

## GET Endpoints

- `GET /unitsofmeasure/v2/active` - Get all active units of measure
  - Returns: Grams, Ounces, Pounds, Each, Gallons, Milliliters, etc.
  - Use case: Validate UoM before creating packages/items

- `GET /unitsofmeasure/v2/types` - Get unit of measure types
  - Returns: Weight, Volume, Count

---

## Example

```php
$units = $api->get("/unitsofmeasure/v2/active?licenseNumber={$license}");

// Common units: Grams, Ounces, Pounds, Each, Milligrams
$validUnits = array_column($units, 'Name');

if (!in_array('Grams', $validUnits)) {
    throw new Exception("Grams not available as unit");
}
```

---

## Common Units

- **Weight**: Grams, Ounces, Pounds, Kilograms, Milligrams
- **Volume**: Milliliters, Liters, Fluid Ounces, Gallons
- **Count**: Each (for countable items like pre-rolls)
