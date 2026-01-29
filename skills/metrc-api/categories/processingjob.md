# Processing Job Category

**Collection File**: `collections/metrc-processingjob.postman_collection.json`
**Total Endpoints**: 17
**License Compatibility**: Processing/Manufacturing licenses (AU-P-######)

---

## GET Endpoints (8 endpoints)

- `GET /processingjobs/v2/{id}` - Get processing job by ID
- `GET /processingjobs/v2/active` - Get active processing jobs
- `GET /processingjobs/v2/inactive` - Get inactive processing jobs
- `GET /processingjobs/v2/categories` - Get processing job categories
- `GET /processingjobs/v2/attributes` - Get processing job attributes

### Job Types

- `GET /processingjobs/v2/jobtypes/active` - Get active job types
- `GET /processingjobs/v2/jobtypes/inactive` - Get inactive job types

---

## POST Endpoints (4 endpoints)

- `POST /processingjobs/v2/start` - Start/create processing job
  - Use case: Track manufacturing/extraction processes
  - Request body: Source packages, processing type, expected output

- `POST /processingjobs/v2/packages` - Create packages from processing job
  - Use case: Create finished products from processing

### Job Type Management

- `POST /processingjobs/v2/jobtypes` - Create new job type
  - Use case: Define custom processing workflows

---

## PUT Endpoints (4 endpoints)

- `PUT /processingjobs/v2/adjust` - Adjust processing job details
- `PUT /processingjobs/v2/finish` - Finish processing job
- `PUT /processingjobs/v2/unfinish` - Unfinish processing job (reopen)
- `PUT /processingjobs/v2/jobtypes` - Update job type

---

## DELETE Endpoints (2 endpoints)

- `DELETE /processingjobs/v2/{id}` - Archive processing job
- `DELETE /processingjobs/v2/jobtypes/{id}` - Archive job type

---

## Example

```php
// Create extraction processing job
$job = [
    [
        'ProcessingJobName' => 'CO2 Extraction Batch 001',
        'ProcessingJobType' => 'CO2 Extraction',
        'SourcePackages' => [
            ['PackageLabel' => '1A4060300000001000000010', 'Weight' => 1000, 'UnitOfMeasure' => 'Grams']
        ],
        'ActualDate' => '2025-01-15'
    ]
];

$api->post("/processingjobs/v2/create?licenseNumber={$license}", $job);
```
