# Lab Tests Category

**Collection File**: `collections/metrc-labtests.postman_collection.json`
**Total Endpoints**: 8
**License Compatibility**: All licenses (Testing Labs have full access)

---

## GET Endpoints

- `GET /labtests/v2/states` - Get lab test states (TestPassed, TestFailed, etc.)
- `GET /labtests/v2/types` - Get lab test types (cannabinoid, pesticide, etc.)
- `GET /labtests/v2/results` - Get lab test results

---

## POST Endpoints

- `POST /labtests/v2/record` - Record lab test results
  - Use case: Submit COA data to Metrc
  - Request body: Test results, cannabinoid percentages, pass/fail status

- `POST /labtests/v2/labtestdocument` - Upload lab test document (COA PDF)
  - Use case: Attach Certificate of Analysis

---

## PUT Endpoints

- `PUT /labtests/v2/labtestdocument` - Update lab test document

---

## DELETE Endpoints

- `DELETE /labtests/v2/results/{id}` - Delete lab test result

---

## Example

```php
$testResults = [
    [
        'Label' => '1A4060300000001000000050',
        'ResultDate' => '2025-01-15',
        'LabTestDocument' => [
            'DocumentFileName' => 'COA-12345.pdf',
            'DocumentFileBase64' => base64_encode($pdfContent)
        ],
        'Results' => [
            ['LabTestTypeName' => 'THC', 'Quantity' => 22.5, 'Passed' => true],
            ['LabTestTypeName' => 'CBD', 'Quantity' => 1.2, 'Passed' => true]
        ]
    ]
];

$api->post("/labtests/v2/record?licenseNumber={$license}", $testResults);
```

---

## Related

- `scenarios/record-lab-test-results.md` - Complete COA submission workflow
