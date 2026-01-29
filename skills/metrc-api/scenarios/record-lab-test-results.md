# Scenario: Record Lab Test Results

**Goal**: Submit COA (Certificate of Analysis) data to Metrc

**License Compatibility**: All licenses (Testing labs have full access)

**Complexity**: Moderate

**Prerequisites**:
- Package to test
- Lab test results/COA document
- Test result data (THC%, CBD%, pesticides, etc.)

---

## Workflow

1. Get package to test
2. Prepare lab test data
3. Upload COA document
4. Submit test results

---

## Implementation

### Step 1: Prepare Lab Test Data

```php
$api = new MetrcApi();
$api->set_user($user);
$license = session('license');

$packageLabel = '1A4060300000001000000050';

// Prepare test results
$testResults = [
    [
        'Label' => $packageLabel,
        'ResultDate' => now()->format('Y-m-d'),
        'LabTestDocument' => [
            'DocumentFileName' => 'COA-12345.pdf',
            'DocumentFileBase64' => base64_encode(file_get_contents($pdfPath))
        ],
        'Results' => [
            [
                'LabTestTypeName' => 'THC',
                'Quantity' => 22.5,
                'Passed' => true,
                'Notes' => null
            ],
            [
                'LabTestTypeName' => 'CBD',
                'Quantity' => 1.2,
                'Passed' => true,
                'Notes' => null
            ],
            [
                'LabTestTypeName' => 'Pesticides',
                'Quantity' => 0,
                'Passed' => true,
                'Notes' => 'All pesticides below detection limit'
            ]
        ]
    ]
];
```

### Step 2: Submit to Metrc

**Endpoint**: `POST /labtests/v2/record`

```php
try {
    $api->post("/labtests/v2/record?licenseNumber={$license}", $testResults);

    Log::info("Lab test results submitted for package {$packageLabel}");

    return redirect()->back()->with('message', 'Lab test results submitted successfully');

} catch (\Exception $e) {
    Log::error("Lab test submission failed: " . $e->getMessage());
    return redirect()->back()->with('error', $e->getMessage());
}
```

---

## Get Available Test Types

```php
// Get valid test type names
$testTypes = $api->get("/labtests/v2/types?licenseNumber={$license}");

// Common types: THC, CBD, Pesticides, Heavy Metals, Microbial, Mycotoxins
$typeNames = array_column($testTypes, 'Name');
```

---

## Failed Test Example

```php
$failedTest = [
    [
        'Label' => $packageLabel,
        'ResultDate' => now()->format('Y-m-d'),
        'Results' => [
            [
                'LabTestTypeName' => 'Pesticides',
                'Quantity' => 5.2,
                'Passed' => false, // FAILED
                'Notes' => 'Pesticide level exceeds state limits'
            ]
        ]
    ]
];

// Package will be flagged in Metrc, may require remediation
```

---

## Related

- `categories/labtests.md` - Lab test endpoints
- `categories/packages.md` - Package endpoints
