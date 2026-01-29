# Packages Category

**Collection File**: `collections/metrc-packages.postman_collection.json`
**Total Endpoints**: 32
**License Compatibility**: All license types

---

## GET Endpoints (11 endpoints)

### Retrieve Packages

- `GET /packages/v2/{id}` - Get package by ID
- `GET /packages/v2/{label}` - Get package by label (tag)
- `GET /packages/v2/active` - Get all active packages
- `GET /packages/v2/inactive` - Get inactive packages
- `GET /packages/v2/onhold` - Get packages on hold
- `GET /packages/v2/intransit` - Get packages in transit

### Reference Data

- `GET /packages/v2/types` - Get package types (Immature Plant, Product, etc.)
- `GET /packages/v2/{id}/labtestresults` - Get lab test results for specific package

### Adjustment History

- `GET /packages/v2/adjustments` - Get adjustment history for facility
  - Returns all package quantity adjustments with reasons and timestamps
  - Use case: Display adjustment history, audit trail, inventory reconciliation
  - Query params: `licenseNumber` (required), `pageNumber`, `pageSize`, `lastModifiedStart`, `lastModifiedEnd`
  - Response fields:
    - `PackageId` - Internal Metrc package ID
    - `PackageLabel` - Package tag (e.g., "1A4060300000001000000001")
    - `ItemName` - Name of the item adjusted
    - `ItemCategoryName` - Category (e.g., "Buds", "Edible")
    - `AdjustmentQuantity` - Delta change (negative for decreases)
    - `AdjustmentUnitOfMeasureName` - Full unit name (e.g., "Grams")
    - `AdjustmentUnitOfMeasureAbbreviation` - Short unit (e.g., "g")
    - `AdjustmentReasonName` - Reason for adjustment
    - `AdjustmentNote` - Optional note/explanation
    - `AdjustmentDate` - When adjustment was made (ISO 8601)
    - `PackagedDate` - Original package creation date
    - `AdjustedByUserName` - User who made the adjustment
    - `PackageLabTestResultExpirationDateTime` - Lab test expiration (nullable)

- `GET /packages/v2/adjust/reasons` - Get valid adjustment reasons for dropdown
  - Response: Array of `{ Name: string, RequiresNote: boolean }`

### Transferred Packages

- `GET /packages/v2/transferred` - Get packages transferred to/from facility
  - Use case: Track packages that have been transferred between facilities
  - Query params: `licenseNumber` (required), `pageNumber`, `pageSize`, `lastModifiedStart`, `lastModifiedEnd`

**Common Query Parameters**: `licenseNumber` (required), `pageNumber`, `pageSize`, `lastModifiedStart`, `lastModifiedEnd`

---

## POST Endpoints (6 endpoints)

### Package Adjustments

- `POST /packages/v2/adjust` - Adjust package quantities/weights
  - Use case: Fix inventory discrepancies, record waste
  - Request body: Array of adjustment objects with `Label`, `Quantity`, `UnitOfMeasure`, `AdjustmentReason`, `AdjustmentDate`

- `POST /packages/v2/finish` - Finish (deactivate) packages
  - Use case: Mark packages as sold, destroyed, or completed
  - Request body: Array with `Label`, `ActualDate`

- `POST /packages/v2/unfinish` - Unfinish previously finished packages
  - Use case: Reverse a finish action
  - Request body: Array with `Label`

- `POST /packages/v2/remediate` - Remediate failed packages
  - Use case: Re-process failed lab tests
  - Request body: Array with remediation details

### Package Creation

- `POST /packages/v2/create` - Create new packages
  - Use case: Create packages from items/ingredients
  - Request body: Array of package objects with `Tag`, `Item`, `Quantity`, `UnitOfMeasure`, `ActualDate`

- `POST /packages/v2/create/testing` - Create packages for lab testing
  - Use case: Create sample packages for COA testing
  - Request body: Similar to create, with testing-specific fields

- `POST /packages/v2/create/plantings` - Create plantings from packages
  - Use case: Plant immature plants from package
  - Request body: Package tag, plant batch name, count, location

---

## PUT Endpoints (14 endpoints)

### Package Updates

- `PUT /packages/v2/location` - Move packages to new location
  - Use case: Relocate inventory within facility
  - Request body: Array with `Label`, `Location`, `MoveDate`

- `PUT /packages/v2/item` - Change package item
  - Use case: Correct item assignment errors
  - Request body: Array with `Label`, `Item`

- `PUT /packages/v2/note` - Update package notes
  - Use case: Add descriptive notes to packages
  - Request body: Array with `PackageLabel`, `Note`

### Shelf Life Management

- `PUT /packages/v2/usebydate` - Change shelf life dates
  - Use case: Update expiration, sell-by, and use-by dates
  - Request body: Array with `Label`, `ExpirationDate`, `SellByDate`, `UseByDate`
  - Date format: YYYY-MM-DD

### Donation & Trade Sample Flags

- `PUT /packages/v2/donation/flag` - Flag package as donation
  - Use case: Mark packages intended for donation
  - Request body: Array with `Label`

- `PUT /packages/v2/donation/unflag` - Remove donation flag
  - Use case: Unmark packages previously flagged for donation
  - Request body: Array with `Label`

- `PUT /packages/v2/tradesample/flag` - Flag as trade sample
  - Use case: Mark packages as trade samples for vendors/partners
  - Request body: Array with `Label`

- `PUT /packages/v2/tradesample/unflag` - Remove trade sample flag
  - Use case: Unmark trade sample packages
  - Request body: Array with `Label`

### Lab Test & External ID Management

- `PUT /packages/v2/labtests/required` - Change required lab test batches
  - Use case: Modify which lab test batches a package requires
  - Request body: Array with `Label`, `RequiredLabTestBatches` (string array)

- `PUT /packages/v2/externalid` - Change external tracking ID
  - Use case: Link package to external system ID (ERP, POS, etc.)
  - Request body: Array with `PackageLabel`, `ExternalId`

### Quantity Adjustments

- `PUT /packages/v2/adjust` - Adjust package quantity (alternative method)
  - Use case: Same as POST /adjust but using PUT method
  - Request body: Array with `Label`, `Quantity`, `UnitOfMeasure`, `AdjustmentReason`, `AdjustmentDate`, `ReasonNote`

### Decontamination

- `PUT /packages/v2/decontaminate` - Record product decontamination
  - Use case: Document decontamination procedures for failed lab tests
  - Request body: Array with `PackageLabel`, `DecontaminationMethodName`, `DecontaminationDate`, `DecontaminationSteps`

---

## DELETE Endpoints (1 endpoint)

- `DELETE /packages/v2/{id}` - Discontinue/void a package
  - Use case: Permanently discontinue a package (cannot be undone)
  - Note: Package must be inactive before discontinuing

---

## Common Use Cases

### 1. Get Active Packages with Pagination

```php
$api = new MetrcApi();
$api->set_user($user);

$packages = [];
$pageNumber = 1;
$pageSize = 50;

do {
    $response = $api->get("/packages/v2/active", [
        'licenseNumber' => $license,
        'pageNumber' => $pageNumber,
        'pageSize' => $pageSize
    ]);

    $packages = array_merge($packages, $response);
    $pageNumber++;
} while (count($response) === $pageSize);
```

### 2. Adjust Package Quantity

```php
$adjustments = [
    [
        'Label' => '1A4060300000001000000001',
        'Quantity' => -1.5,
        'UnitOfMeasure' => 'Grams',
        'AdjustmentReason' => 'Drying',
        'AdjustmentDate' => '2025-01-15',
        'ReasonNote' => 'Weight loss during drying process'
    ]
];

$api->post("/packages/v2/adjust?licenseNumber={$license}", $adjustments);
```

### 3. Create New Packages

```php
$newPackages = [
    [
        'Tag' => '1A4060300000001000000010',
        'Item' => 'Blue Dream 1/8oz',
        'Quantity' => 3.5,
        'UnitOfMeasure' => 'Grams',
        'ActualDate' => '2025-01-15',
        'Ingredients' => [
            [
                'Package' => '1A4060300000001000000001',
                'Quantity' => 3.5,
                'UnitOfMeasure' => 'Grams'
            ]
        ]
    ]
];

$api->post("/packages/v2/create?licenseNumber={$license}", $newPackages);
```

### 4. Flag Package as Donation

```php
$donationPackages = [
    ['Label' => '1A4060300000001000000041'],
    ['Label' => '1A4060300000001000000042']
];

$api->put("/packages/v2/donation/flag?licenseNumber={$license}", $donationPackages);
```

### 5. Update Shelf Life Dates

```php
$shelfLifeUpdates = [
    [
        'Label' => '1A4060300000001000000041',
        'ExpirationDate' => '2025-06-15',
        'SellByDate' => '2025-05-15',
        'UseByDate' => '2025-06-01'
    ]
];

$api->put("/packages/v2/usebydate?licenseNumber={$license}", $shelfLifeUpdates);
```

### 6. Record Decontamination

```php
$decontamination = [
    [
        'PackageLabel' => '1A4060300000001000000050',
        'DecontaminationMethodName' => 'Further Drying',
        'DecontaminationDate' => '2025-01-17',
        'DecontaminationSteps' => 'Extended drying period in controlled environment'
    ]
];

$api->put("/packages/v2/decontaminate?licenseNumber={$license}", $decontamination);
```

---

## Important Notes

- **Always require licenseNumber**: Every endpoint needs it as a query parameter
- **Pagination**: Active/inactive endpoints can return large datasets - always paginate
- **Batch operations**: All POST/PUT endpoints accept arrays for batch operations
- **Date format**: Use ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)
- **Package tags**: Must be assigned from available tag pool (see `/tags/v2/package/available`)

---

**For complete request/response details**, read `collections/metrc-packages.postman_collection.json`
