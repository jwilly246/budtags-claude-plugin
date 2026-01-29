# Sales Category

**Collection File**: `collections/metrc-sales.postman_collection.json`
**Total Endpoints**: 35
**License Compatibility**: ⚠️ **RETAIL LICENSES ONLY** (AU-R-######)

---

## ⚠️ CRITICAL WARNING

**Sales endpoints are ONLY accessible to Retail licenses.**

Cultivation (AU-C-######) and Processing (AU-P-######) licenses will receive:
- HTTP 401 Unauthorized or 403 Forbidden
- Error: "No valid endpoint found"

**Before using any sales endpoint, verify the license type starts with `AU-R-`**

---

## GET Endpoints (16 endpoints)

### Sales Receipts

- `GET /sales/v2/receipts/{id}` - Get receipt by ID
- `GET /sales/v2/receipts/external/{externalNumber}` - Get receipt by external ID
  - Use case: Lookup receipt using POS/ERP external reference number
- `GET /sales/v2/receipts/active` - Get active receipts
- `GET /sales/v2/receipts/inactive` - Get inactive receipts

### Deliveries (Hub-Based)

- `GET /sales/v2/deliveries/{id}` - Get delivery by ID
- `GET /sales/v2/deliveries/active` - Get active deliveries
- `GET /sales/v2/deliveries/inactive` - Get inactive deliveries
- `GET /sales/v2/deliveries/returnreasons` - Get valid return reasons
  - Use case: Populate dropdown for package return reasons

### Retailer Deliveries

- `GET /sales/v2/deliveries/retailer/active` - Get active retailer deliveries
  - Use case: Track ongoing delivery routes
- `GET /sales/v2/deliveries/retailer/inactive` - Get inactive retailer deliveries
- `GET /sales/v2/deliveries/retailer/{id}` - Get specific retailer delivery
  - Use case: Get full details of a delivery including destinations and packages

### Reference Data

- `GET /sales/v2/customertypes` - Get customer types (Consumer, Patient, Caregiver)
- `GET /sales/v2/paymenttypes` - Get payment types (Cash, Debit, Credit, Electronic)
- `GET /sales/v2/counties` - Get counties for delivery addresses
- `GET /sales/v2/patientregistration/locations` - Get patient registration locations

**Common Query Parameters**: `licenseNumber` (required), `salesDateStart`, `salesDateEnd`, `pageNumber`, `pageSize`

---

## POST Endpoints (7 endpoints)

### Receipts

- `POST /sales/v2/receipts` - Create sales receipts
  - Use case: Record retail sales to customers
  - Request body: Array with receipt details, customer info, items sold

### Deliveries

- `POST /sales/v2/deliveries` - Record deliveries
  - Use case: Record delivery-based sales

### Retailer Deliveries

- `POST /sales/v2/deliveries/retailer` - Record retailer deliveries
  - Use case: Create delivery routes with multiple destinations
  - Request body: Array with driver info, vehicle info, destinations
  - Fields: `DateTime`, `DriverEmployeeId`, `DriverName`, `DriversLicenseNumber`, `PhoneNumberForQuestions`, `VehicleMake`, `VehicleModel`, `VehicleLicensePlateNumber`, `EstimatedDepartureDateTime`, `Destinations`

- `POST /sales/v2/deliveries/retailer/depart` - Depart retailer delivery
  - Use case: Mark delivery route as departed from facility
  - Request body: Array with `RetailerDeliveryId`

- `POST /sales/v2/deliveries/retailer/restock` - Restock retailer delivery
  - Use case: Add packages to an existing delivery route
  - Request body: Array with `RetailerDeliveryId`, `DateTime`, `EstimatedDepartureDateTime`, `Packages` (array of package details)

- `POST /sales/v2/deliveries/retailer/sale` - Record sale from retailer delivery
  - Use case: Record individual sales made during delivery route
  - Request body: Array with `RetailerDeliveryId`, `SalesDateTime`, `SalesCustomerType`, `PatientLicenseNumber`, `ConsumerId`, `RecipientName`, `RecipientAddress*` fields

- `POST /sales/v2/deliveries/retailer/end` - End retailer delivery
  - Use case: Complete delivery route and record remaining inventory
  - Request body: Array with `RetailerDeliveryId`, `ActualArrivalDateTime`, `Packages` (array with ending quantities)

---

## PUT Endpoints (10 endpoints)

### Receipts

- `PUT /sales/v2/receipts` - Update sales receipts
  - Use case: Modify existing receipt details
  - Request body: Array with receipt ID and updated fields

- `PUT /sales/v2/receipts/finalize` - Finalize receipts
  - Use case: Lock receipts from further modifications
  - Request body: Array with `Id`

- `PUT /sales/v2/receipts/unfinalize` - Unfinalize receipts
  - Use case: Reopen finalized receipts for editing
  - Request body: Array with `Id`

### Deliveries (Hub Operations)

- `PUT /sales/v2/deliveries` - Update deliveries
  - Use case: Modify existing delivery details

- `PUT /sales/v2/deliveries/hub` - Update hub transporters
  - Use case: Update transporter info for hub deliveries
  - Request body: Array with `Id`, `TransporterFacilityId`, `DriverEmployeeId`, `DriverName`, `DriversLicenseNumber`, `PhoneNumberForQuestions`, `VehicleMake`, `VehicleModel`, `VehicleLicensePlateNumber`, `PlannedRoute`, `EstimatedDepartureDateTime`, `EstimatedArrivalDateTime`

- `PUT /sales/v2/deliveries/hub/accept` - Accept hub delivery
  - Use case: Accept delivery at transfer hub
  - Request body: Array with `Id`

- `PUT /sales/v2/deliveries/hub/depart` - Depart hub delivery
  - Use case: Mark delivery as departed from hub
  - Request body: Array with `Id`

- `PUT /sales/v2/deliveries/hub/verifyID` - Verify ID at hub
  - Use case: Verify customer ID for hub delivery
  - Request body: Array with `Id`, `PaymentType`

- `PUT /sales/v2/deliveries/complete` - Complete delivery
  - Use case: Mark delivery as completed with accepted/returned packages
  - Request body: Array with `Id`, `ActualArrivalDateTime`, `PaymentType`, `AcceptedPackages` (array of labels), `ReturnedPackages` (array with return details)

### Retailer Deliveries

- `PUT /sales/v2/deliveries/retailer` - Update retailer deliveries
  - Use case: Modify retailer delivery details
  - Request body: Same as POST but with `Id` field included

---

## DELETE Endpoints (3 endpoints)

### Receipts

- `DELETE /sales/v2/receipts/{id}` - Archive/void sales receipt
  - Use case: Cancel/void incorrect sales
  - Returns: Confirmation of voided receipt

### Deliveries

- `DELETE /sales/v2/deliveries/{id}` - Void delivery
  - Use case: Cancel incorrect delivery

- `DELETE /sales/v2/deliveries/retailer/{id}` - Void retailer delivery
  - Use case: Cancel incorrect retailer delivery route

---

## Common Use Cases

### 1. Create Retail Sales Receipt

```php
$sales = [
    [
        'SalesDateTime' => '2025-01-15T14:30:00Z',
        'SalesCustomerType' => 'Consumer',
        'PatientLicenseNumber' => null, // Only for medical sales
        'CaregiverLicenseNumber' => null,
        'IdentificationMethod' => "Driver's License",
        'Transactions' => [
            [
                'PackageLabel' => '1A4060300000001000000050',
                'Quantity' => 3.5,
                'UnitOfMeasure' => 'Grams',
                'TotalAmount' => 45.00
            ],
            [
                'PackageLabel' => '1A4060300000001000000051',
                'Quantity' => 1,
                'UnitOfMeasure' => 'Each',
                'TotalAmount' => 15.00
            ]
        ]
    ]
];

$api->post("/sales/v2/receipts?licenseNumber={$license}", $sales);
```

### 2. Get Sales for Date Range

```php
$salesStart = '2025-01-01';
$salesEnd = '2025-01-31';

$receipts = $api->get("/sales/v2/receipts/active", [
    'licenseNumber' => $license,
    'salesDateStart' => $salesStart,
    'salesDateEnd' => $salesEnd
]);
```

### 3. Finalize Receipts

```php
$receiptsToFinalize = [
    ['Id' => 1],
    ['Id' => 2]
];

$api->put("/sales/v2/receipts/finalize?licenseNumber={$license}", $receiptsToFinalize);
```

### 4. Create Retailer Delivery Route

```php
$delivery = [
    [
        'DateTime' => '2025-01-15T10:00:00Z',
        'DriverEmployeeId' => '1',
        'DriverName' => 'John Doe',
        'DriversLicenseNumber' => 'DL123456',
        'PhoneNumberForQuestions' => '+1-555-123-4567',
        'VehicleMake' => 'Ford',
        'VehicleModel' => 'Transit',
        'VehicleLicensePlateNumber' => 'ABC123',
        'EstimatedDepartureDateTime' => '2025-01-15T11:00:00Z',
        'Destinations' => [
            [
                'SalesCustomerType' => 'Consumer',
                'ConsumerId' => '456',
                'RecipientName' => 'Jane Smith',
                'RecipientAddressStreet1' => '123 Main St',
                'RecipientAddressCity' => 'Denver',
                'RecipientAddressState' => 'CO',
                'RecipientAddressPostalCode' => '80202',
                'Transactions' => [
                    [
                        'PackageLabel' => '1A4060300000001000000060',
                        'Quantity' => 3.5,
                        'UnitOfMeasure' => 'Grams',
                        'TotalPrice' => 45.00
                    ]
                ]
            ]
        ]
    ]
];

$api->post("/sales/v2/deliveries/retailer?licenseNumber={$license}", $delivery);
```

### 5. Complete Hub Delivery with Returns

```php
$completion = [
    [
        'Id' => 6,
        'ActualArrivalDateTime' => '2025-01-15T13:00:00Z',
        'PaymentType' => 'Cash',
        'AcceptedPackages' => [
            '1A4060300000001000000001'
        ],
        'ReturnedPackages' => [
            [
                'Label' => '1A4060300000001000000002',
                'ReturnQuantityVerified' => 1.0,
                'ReturnUnitOfMeasure' => 'Ounces',
                'ReturnReason' => 'Spoilage',
                'ReturnReasonNote' => 'Product damaged during transport'
            ]
        ]
    ]
];

$api->put("/sales/v2/deliveries/complete?licenseNumber={$license}", $completion);
```

### 6. End Retailer Delivery Route

```php
$endDelivery = [
    [
        'RetailerDeliveryId' => 6,
        'ActualArrivalDateTime' => '2025-01-15T17:00:00Z',
        'Packages' => [
            [
                'Label' => '1A4060300000001000000002',
                'EndQuantity' => 1.0,
                'EndUnitOfMeasure' => 'Ounces'
            ]
        ]
    ]
];

$api->post("/sales/v2/deliveries/retailer/end?licenseNumber={$license}", $endDelivery);
```

---

## Important Notes

- **License verification**: ALWAYS check license type is retail before calling sales endpoints
- **Customer types**: Medical vs recreational affects required fields
- **Patient tracking**: Medical sales require patient license number
- **Payment types**: Must use valid payment type from reference data
- **Voiding sales**: Use DELETE endpoint, not negative transactions
- **Date filtering**: Use `salesDateStart` and `salesDateEnd` for queries
- **Hub vs Retailer deliveries**: Hub deliveries go through transfer hubs; retailer deliveries are direct-to-customer routes
- **Finalization**: Once finalized, receipts cannot be modified without unfinalizing first

---

## Related Categories

- `categories/packages.md` - Package endpoints (for inventory being sold)
- `categories/patients.md` - Patient management (for medical sales)
- `categories/transporters.md` - Driver and vehicle management
- `patterns/license-types.md` - Complete license compatibility matrix

---

**For complete request/response details**, read `collections/metrc-sales.postman_collection.json`
