# Waste Methods Category

**Collection File**: `collections/metrc-wastemethods.postman_collection.json`
**Total Endpoints**: 1
**License Compatibility**: All license types

---

## GET Endpoints

- `GET /wastemethods/v2/all` - Get all waste methods
  - Returns: Compost, Grinder/Garbage Disposal, etc.
  - Use case: Validate waste method before recording waste

---

## Example

```php
$wasteMethods = $api->get("/wastemethods/v2/all?licenseNumber={$license}");

// Common methods: Compost, Grinder/Garbage Disposal, Landfill
$methodNames = array_column($wasteMethods, 'Name');
```

---

## Related

- Plant waste, harvest waste, package waste all require waste methods
- Different from waste_reasons (cultivation-specific)
