# Facilities Category

**Collection File**: `collections/metrc-facilities.postman_collection.json`
**Total Endpoints**: 1
**License Compatibility**: All license types

---

## GET Endpoints

- `GET /facilities/v2/` - Get all facilities for your API account
  - **No licenseNumber required** (unique endpoint!)
  - Returns: All facilities associated with your API credentials
  - Use case: Get available licenses, facility names, addresses

---

## Example

```php
// Note: No licenseNumber parameter!
$facilities = $api->get("/facilities/v2/");

foreach ($facilities as $facility) {
    echo "{$facility['License']['Number']} - {$facility['Name']}\n";
    // AU-R-000001 - Main Retail Location
    // AU-C-000002 - Cultivation Facility
}

// Use to populate license dropdown
$licenses = array_column(array_column($facilities, 'License'), 'Number');
```

---

## Important Notes

- **Only endpoint that doesn't require licenseNumber**
- Use this to discover available licenses
- Facility data includes license type, address, phone, etc.
- Critical for multi-license account management

---

## Related

- `patterns/license-types.md` - Understanding license types
- Session management for switching between facilities
