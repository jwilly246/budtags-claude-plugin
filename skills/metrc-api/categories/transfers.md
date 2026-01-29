# Transfers Category

**Collection File**: `collections/metrc-transfers.postman_collection.json`
**Total Endpoints**: 28
**License Compatibility**: All license types

---

## GET Endpoints

### Transfer Lists

- `GET /transfers/v2/hub` - Get transfer hub shipments for a facility
  - **Filters**: Either `lastModifiedStart/End` OR `estimatedArrivalStart/End` (mutually exclusive!)
  - **Pagination**: pageSize max 20
  - **Permissions**: Manage Transfers, View Transfers

- `GET /transfers/v2/incoming` - Get incoming transfers to your facility

- `GET /transfers/v2/outgoing` - Get outgoing transfers from your facility

- `GET /transfers/v2/rejected` - Get rejected transfers

### Transfer Details

- `GET /transfers/v2/{id}/deliveries` - Get deliveries for a transfer

- `GET /transfers/v2/deliveries/{id}/packages` - Get packages in a delivery

- `GET /transfers/v2/deliveries/{id}/packages/wholesale` - Get wholesale packages in a delivery

- `GET /transfers/v2/deliveries/{id}/transporters` - Get transporters for a delivery
  - Note: `{id}` = Transfer Delivery Id, NOT Manifest Number

- `GET /transfers/v2/deliveries/{id}/transporters/details` - Get detailed transporter info
  - Returns: Driver name, license numbers, vehicle make/model/plate
  - Note: `{id}` = Transfer Delivery Id, NOT Manifest Number
  - **Permissions**: Manage Transfers, View Transfers

- `GET /transfers/v2/deliveries/package/{id}/requiredlabtestbatches` - Get required lab tests for a package
  - Returns: `[{ PackageId, LabTestBatchId, LabTestBatchName }]`
  - Note: `{id}` = Transfer Delivery Package Id
  - **Permissions**: Manage Transfers, View Transfers

### Reference Data

- `GET /transfers/v2/deliveries/packages/states` - Get available package states
  - Returns: `["Shipped", "Rejected", "Accepted", "Returned"]`
  - **Permissions**: None required
  - **No parameters**

- `GET /transfers/v2/types` - Get transfer types

### Transfer Hubs

- `GET /transfers/v2/hub` - Get transfer hub shipments for a facility
  - Use case: List all shipments going through transfer hubs
  - **Filters**: Either `lastModifiedStart/End` OR `estimatedArrivalStart/End` (mutually exclusive!)
  - **Pagination**: pageSize max 20
  - **Permissions**: Manage Transfers, View Transfers

### Manifest

- `GET /transfers/v2/manifest/{id}/html` - Get print-ready HTML manifest for a transfer
  - Returns complete HTML document with embedded styling and Metrc branding
  - Use case: Print physical manifests for transport compliance
  - Parameters: `licenseNumber` (required), `external` (optional)
  - **Permissions**: Manage Transfers, View Transfers

- `GET /transfers/v2/manifest/{id}/pdf` - Get PDF manifest for a transfer
  - Returns PDF document for manifest
  - Use case: Download/archive manifests as PDF
  - Parameters: `licenseNumber` (required)
  - **Permissions**: Manage Transfers, View Transfers

### Outgoing Templates

- `GET /transfers/v2/templates/outgoing` - Get outgoing transfer templates
  - **Filters**: Optional `lastModifiedStart/End`
  - **Pagination**: pageSize max 20
  - **Permissions**: Manage Transfer Templates, View Transfer Templates

- `GET /transfers/v2/templates/outgoing/{id}/deliveries` - Get deliveries for a template
  - **Permissions**: Manage Transfer Templates, View Transfer Templates

- `GET /transfers/v2/templates/outgoing/deliveries/{id}/transporters` - Get transporters for a template delivery
  - Returns: `[{ TransporterFacilityLicenseNumber, TransporterFacilityName, TransporterDirection }]`
  - Note: `{id}` = Transfer Template Delivery Id
  - **Permissions**: Manage Transfer Templates, View Transfer Templates

- `GET /transfers/v2/templates/outgoing/deliveries/{id}/transporters/details` - Get detailed transporter info for template
  - Returns: Driver details, vehicle info (same format as non-template version)
  - Note: `{id}` = Transfer Template Delivery Id
  - **Permissions**: Manage Transfer Templates, View Transfer Templates

- `GET /transfers/v2/templates/outgoing/deliveries/{id}/packages` - Get packages for a template delivery
  - Returns: Full package details including THC/CBD content, lab testing state
  - Note: `{id}` = Transfer Template Delivery Id
  - **Permissions**: Manage Transfer Templates, View Transfer Templates

---

## POST Endpoints

- `POST /transfers/v2/external/incoming` - Create external incoming transfer
  - Use case: Receive shipments from other facilities

- `POST /transfers/v2/templates/outgoing` - Create outgoing transfer template
  - Use case: Create reusable transfer configurations

### Hub Operations

- `POST /transfers/v2/hub/arrive` - Mark transfer as arrived at hub
  - Use case: Record arrival of shipment at transfer hub
  - Request body: Array with `ShipmentDeliveryId`, `TransporterDirection` ("Outbound" or "Return")

- `POST /transfers/v2/hub/checkin` - Check in transfer at hub
  - Use case: Begin processing shipment at hub
  - Request body: Array with `ShipmentDeliveryId`, `TransporterDirection`

- `POST /transfers/v2/hub/checkout` - Check out transfer from hub
  - Use case: Complete processing at hub, ready for departure
  - Request body: Array with `ShipmentDeliveryId`, `TransporterDirection`

- `POST /transfers/v2/hub/depart` - Mark transfer as departed from hub
  - Use case: Record departure from hub facility
  - Request body: Array with `ShipmentDeliveryId`, `TransporterDirection`

**Hub Operations Request Body Example**:
```php
$hubOperation = [
    [
        'ShipmentDeliveryId' => 111,
        'TransporterDirection' => 'Outbound'
    ],
    [
        'ShipmentDeliveryId' => 112,
        'TransporterDirection' => 'Return'
    ]
];

$api->post("/transfers/v2/hub/arrive?licenseNumber={$license}", $hubOperation);
```

---

## PUT Endpoints

- `PUT /transfers/v2/external/incoming` - Update external incoming transfer

- `PUT /transfers/v2/templates/outgoing` - Update outgoing transfer template

---

## DELETE Endpoints

- `DELETE /transfers/v2/external/incoming/{id}` - Void incoming transfer

- `DELETE /transfers/v2/templates/outgoing/{id}` - Delete outgoing transfer template

---

## Common Workflow

```php
// Check incoming transfers
$incoming = $api->get("/transfers/v2/incoming?licenseNumber={$license}");

// Get packages in a delivery
$deliveryId = $incoming[0]['DeliveryId'];
$packages = $api->get("/transfers/v2/deliveries/{$deliveryId}/packages?licenseNumber={$license}");

// Get required lab tests for a package
$packageId = $packages['Data'][0]['PackageId'];
$requiredTests = $api->get("/transfers/v2/deliveries/package/{$packageId}/requiredlabtestbatches?licenseNumber={$license}");

// Get printable manifest
$transferId = $incoming[0]['Id'];
$manifestHtml = $api->get("/transfers/v2/manifest/{$transferId}/html?licenseNumber={$license}");
```

---

## Hub Workflow (New)

```php
// Get hub shipments by estimated arrival
$hubShipments = $api->get("/transfers/v2/hub?licenseNumber={$license}&estimatedArrivalStart=2025-01-01T00:00:00Z&estimatedArrivalEnd=2025-01-31T23:59:59Z");

// OR by last modified (cannot combine with arrival dates!)
$hubShipments = $api->get("/transfers/v2/hub?licenseNumber={$license}&lastModifiedStart=2025-01-01T00:00:00Z&lastModifiedEnd=2025-01-31T23:59:59Z");
```

---

## Related

- `scenarios/check-in-incoming-transfer.md` - Complete check-in workflow
