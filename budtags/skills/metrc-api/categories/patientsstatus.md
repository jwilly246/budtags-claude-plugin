# Patients Status Category

**Collection File**: `collections/metrc-patientsstatus.postman_collection.json`
**Total Endpoints**: 1
**License Compatibility**: Retail (Medical States)

---

## GET Endpoints

- `GET /patients/v2/status/{license}` - Get patient status by license number
  - Use case: Verify patient license is valid before sale
  - Returns: Active/Inactive status, expiration date

---

## Example

```php
$patientLicense = 'MMJ-12345';
$status = $api->get("/patients/v2/status/{$patientLicense}?licenseNumber={$license}");

if ($status['Status'] !== 'Active') {
    throw new Exception("Patient license is not active");
}
```
