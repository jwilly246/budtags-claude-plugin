# Tags Category

**Collection File**: `collections/metrc-tags.postman_collection.json`
**Total Endpoints**: 3
**License Compatibility**: Varies by tag type

---

## GET Endpoints

- `GET /tags/v2/package/available` - Get available package tags
  - **All license types**
  - Use case: Find tags before creating packages

- `GET /tags/v2/plant/available` - Get available plant tags
  - ⚠️ **CULTIVATION LICENSES ONLY**
  - Use case: Find tags before creating plants/plant batches

- `GET /tags/v2/location/available` - Get available location tags
  - **All license types**

---

## Important Notes

- Tags must be ordered from Metrc
- Once assigned to a package/plant, tags are consumed
- Finishing/archiving packages frees up tags for reuse
- Always check availability before operations requiring tags

---

## Example

```php
// Check available package tags before creating packages
$availableTags = $api->get("/tags/v2/package/available?licenseNumber={$license}");

if (count($availableTags) < 10) {
    throw new Exception("Not enough tags. Order more from Metrc.");
}

// Use first 10 tags for new packages
$tagsToUse = array_slice($availableTags, 0, 10);
```

---

## Related

- All package/plant creation endpoints require tags
- `scenarios/replace-plant-tags.md` - Tag replacement workflow
