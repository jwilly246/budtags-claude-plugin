# Patient Check-Ins Category

**Collection File**: `collections/metrc-patientcheckins.postman_collection.json`
**Total Endpoints**: 5
**License Compatibility**: Retail (Medical States)

---

## GET Endpoints

- `GET /patients/v2/checkins` - Get patient check-in records

---

## POST Endpoints

- `POST /patients/v2/checkins` - Record patient check-in
  - Use case: Track patient visits to dispensary
  - Request body: Patient license, check-in date/time

---

## Example

```php
$checkins = [
    [
        'PatientLicenseNumber' => 'MMJ-12345',
        'CheckInDateTime' => '2025-01-15T14:30:00Z'
    ]
];

$api->post("/patients/v2/checkins?licenseNumber={$license}", $checkins);
```
