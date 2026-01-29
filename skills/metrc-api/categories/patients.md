# Patients Category

**Collection File**: `collections/metrc-patients.postman_collection.json`
**Total Endpoints**: 5
**License Compatibility**: ⚠️ **RETAIL LICENSES ONLY** (Medical States)

---

## ⚠️ MEDICAL STATE ONLY

**Patient endpoints are only for retail licenses in medical cannabis states.**

---

## GET Endpoints

- `GET /patients/v2/active` - Get active patients

---

## POST Endpoints

- `POST /patients/v2/add` - Add new patients
  - Use case: Register medical cannabis patients
  - Request body: Patient license number, expiration date

---

## PUT Endpoints

- `PUT /patients/v2/update` - Update patient details

---

## DELETE Endpoints

- `DELETE /patients/v2/{id}` - Delete/deactivate patient

---

## Example

```php
$patients = [
    [
        'LicenseNumber' => 'MMJ-12345',
        'LicenseEffectiveStartDate' => '2025-01-01',
        'LicenseEffectiveEndDate' => '2026-01-01'
    ]
];

$api->post("/patients/v2/add?licenseNumber={$license}", $patients);
```

---

## Related

- `categories/sales.md` - Medical sales require patient tracking
- `categories/patientcheckins.md` - Patient check-in tracking
