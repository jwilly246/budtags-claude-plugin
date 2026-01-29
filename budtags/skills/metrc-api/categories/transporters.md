# Transporters Category

**Collection File**: `collections/metrc-transporters.postman_collection.json`
**Total Endpoints**: 10
**License Compatibility**: All license types with transfer permissions

---

## Overview

The Transporters category manages **drivers** and **vehicles** used for cannabis transfers. This is separate from the transfer-specific transporter details - these endpoints manage the master list of available drivers and vehicles for your facility.

---

## GET Endpoints

### Drivers

- `GET /transporters/v2/drivers` - Get list of all drivers for the facility
  - **Parameters**: `licenseNumber` (required), `pageNumber`, `pageSize` (optional)
  - **Permissions**: Manage Transfers, View Transfers

- `GET /transporters/v2/drivers/{id}` - Get a specific driver by ID
  - **Parameters**: `licenseNumber` (required)
  - **Permissions**: Manage Transfers, View Transfers

### Vehicles

- `GET /transporters/v2/vehicles` - Get list of all vehicles for the facility
  - **Parameters**: `licenseNumber` (required), `pageNumber`, `pageSize` (optional)
  - **Permissions**: Manage Transfers, View Transfers

- `GET /transporters/v2/vehicles/{id}` - Get a specific vehicle by ID
  - **Parameters**: `licenseNumber` (required)
  - **Permissions**: Manage Transfers, View Transfers

---

## POST Endpoints

- `POST /transporters/v2/drivers` - Create new driver(s)
  - **Permissions**: Manage Transfers
  - Use case: Register drivers authorized to transport cannabis

- `POST /transporters/v2/vehicles` - Create new vehicle(s)
  - **Permissions**: Manage Transfers
  - Use case: Register vehicles approved for cannabis transport

---

## PUT Endpoints

- `PUT /transporters/v2/drivers` - Update existing driver(s)
  - **Permissions**: Manage Transfers

- `PUT /transporters/v2/vehicles` - Update existing vehicle(s)
  - **Permissions**: Manage Transfers

---

## DELETE Endpoints

- `DELETE /transporters/v2/drivers/{id}` - Delete a driver
  - **Permissions**: Manage Transfers

- `DELETE /transporters/v2/vehicles/{id}` - Delete a vehicle
  - **Permissions**: Manage Transfers

---

## Common Workflow

```php
// Get all drivers for the facility
$drivers = $api->get("/transporters/v2/drivers?licenseNumber={$license}");

// Get all vehicles for the facility
$vehicles = $api->get("/transporters/v2/vehicles?licenseNumber={$license}");

// Create a new driver
$api->post("/transporters/v2/drivers?licenseNumber={$license}", [
    [
        'Name' => 'John Smith',
        'OccupationalLicenseNumber' => 'DRV-12345',
        'VehicleLicenseNumber' => 'ABC123',
    ]
]);

// Create a new vehicle
$api->post("/transporters/v2/vehicles?licenseNumber={$license}", [
    [
        'Make' => 'Ford',
        'Model' => 'Transit',
        'LicensePlateNumber' => 'XYZ-789',
    ]
]);
```

---

## Use Cases

1. **Driver Management**: Maintain a roster of approved drivers for cannabis transport
2. **Vehicle Fleet**: Track all vehicles approved for transporting cannabis products
3. **Transfer Setup**: Select from pre-registered drivers/vehicles when creating transfers
4. **Compliance**: Ensure only authorized personnel and vehicles are used for transport

---

## Related

- `categories/transfers.md` - Transfer operations that use these drivers/vehicles
- `patterns/transfer-workflows.md` - Complete transfer workflow patterns
