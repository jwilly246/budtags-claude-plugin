# Employees Category

**Collection File**: `collections/metrc-employees.postman_collection.json`
**Total Endpoints**: 2
**License Compatibility**: All license types

---

## GET Endpoints

- `GET /employees/v2/` - Get all employees for facility
  - Use case: List staff with Metrc access

- `GET /employees/v2/{id}/permissions` - Get employee permissions
  - Use case: View employee's Metrc role permissions

---

## Example

```php
$employees = $api->get("/employees/v2/?licenseNumber={$license}");

foreach ($employees as $employee) {
    echo "{$employee['FullName']} - {$employee['LicenseNumber']}\n";
}

// Get specific employee permissions
$employeeId = $employees[0]['Id'];
$permissions = $api->get("/employees/v2/{$employeeId}/permissions?licenseNumber={$license}");
```

---

## Important Notes

- Read-only endpoints (cannot create/update employees via API)
- Employee management done through Metrc web interface
- Useful for audit logging, permission verification
