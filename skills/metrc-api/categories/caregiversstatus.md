# Caregivers Status Category

**Collection File**: `collections/metrc-caregiversstatus.postman_collection.json`
**Total Endpoints**: 1
**License Compatibility**: Retail (Medical States)

---

## GET Endpoints

- `GET /caregivers/v2/status/{license}` - Get caregiver status by license number
  - Use case: Verify caregiver can purchase on behalf of patient
  - Returns: Active/Inactive status, associated patients

---

## Example

```php
$caregiverLicense = 'CG-12345';
$status = $api->get("/caregivers/v2/status/{$caregiverLicense}?licenseNumber={$license}");

if ($status['Status'] !== 'Active') {
    throw new Exception("Caregiver license is not active");
}
```
