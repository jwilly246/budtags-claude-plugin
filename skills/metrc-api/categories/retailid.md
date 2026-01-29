# RetailId Category

**Collection File**: `collections/metrc-retailid.postman_collection.json`
**Total Endpoints**: 6
**License Compatibility**: All license types (QR code functionality)

---

## Overview

The RetailId category provides QR code functionality for package tracking. These endpoints allow you to:
- Associate external QR codes with Metrc packages
- Generate QR codes directly from packages
- Merge packages using QR identifiers
- Retrieve package information via QR codes

---

## GET Endpoints (2 endpoints)

### QR Code Retrieval

- `GET /retailid/v2/receive/{label}` - Get QR codes by package label
  - Use case: Retrieve all QR codes associated with a specific package tag
  - Path param: `{label}` - The package label (e.g., "1A4060300000001000000041")
  - Query params: `licenseNumber` (required)

- `GET /retailid/v2/receive/qr/{shortCode}` - Get package by QR short code
  - Use case: Look up package information using the short code from a QR URL
  - Path param: `{shortCode}` - The short code from QR URL (e.g., "3W5E11264SGPN")
  - Query params: `licenseNumber` (required)
  - Note: Short code is the identifier after the domain (e.g., from `https://id.14a.com/3W5E11264SGPN`)

---

## POST Endpoints (4 endpoints)

### QR Code Association

- `POST /retailid/v2/associate` - Associate QR codes with packages
  - Use case: Link external QR code URLs to Metrc packages
  - Request body: Array of objects with `PackageLabel` and `QrUrls` (array of QR URLs)
  - Batch operations: Supports multiple packages per request

```php
$associations = [
    [
        'PackageLabel' => '1A4060300000001000000041',
        'QrUrls' => [
            'https://id.14a.com/3W5E11264SGPN',
            'https://id.14a.com/3W5E11264SGPO',
            'https://id.14a.com/3W5E11264SGPP'
        ]
    ],
    [
        'PackageLabel' => '1A4060300000001000000042',
        'QrUrls' => [
            'https://id.14a.com/3W5E11264SGPR'
        ]
    ]
];

$api->post("/retailid/v2/associate?licenseNumber={$license}", $associations);
```

### QR Code Generation

- `POST /retailid/v2/generate` - Generate QR codes from package
  - Use case: Create new QR codes for a package (e.g., for individual units)
  - Request body: Object with `PackageLabel` and `Quantity`
  - Returns: Array of generated QR code URLs

```php
$generate = [
    'PackageLabel' => '1A4060300000001000000041',
    'Quantity' => 10
];

$api->post("/retailid/v2/generate?licenseNumber={$license}", $generate);
```

### Package Merging

- `POST /retailid/v2/merge` - Merge packages via QR
  - Use case: Combine multiple packages into one using their QR identifiers
  - Request body: Object with `packageLabels` (array of package labels to merge)
  - Note: All packages must be compatible (same item, same facility)

```php
$merge = [
    'packageLabels' => [
        '1A4060300000001000000051',
        '1A4060300000001000000052'
    ]
];

$api->post("/retailid/v2/merge?licenseNumber={$license}", $merge);
```

### Package Information

- `POST /retailid/v2/packages/info` - Get package info via QR
  - Use case: Retrieve detailed package information for multiple packages
  - Request body: Object with `packageLabels` (array of package labels)
  - Returns: Package details including item, quantity, lab results

```php
$infoRequest = [
    'packageLabels' => [
        '1A4060300000001000000041',
        '1A4060300000001000000042',
        '1A4060300000001000000043'
    ]
];

$info = $api->post("/retailid/v2/packages/info?licenseNumber={$license}", $infoRequest);
```

---

## Common Use Cases

### 1. Full QR Workflow: Generate and Associate

```php
// Step 1: Generate QR codes for a package
$generateResponse = $api->post("/retailid/v2/generate?licenseNumber={$license}", [
    'PackageLabel' => '1A4060300000001000000041',
    'Quantity' => 5  // Generate 5 QR codes for individual units
]);

// Step 2: If using external QR system, associate those URLs
$api->post("/retailid/v2/associate?licenseNumber={$license}", [
    [
        'PackageLabel' => '1A4060300000001000000041',
        'QrUrls' => $externalQrUrls // From your QR generation system
    ]
]);
```

### 2. Consumer Lookup by QR Code

```php
// Customer scans QR code, extract short code from URL
$shortCode = '3W5E11264SGPN'; // Extracted from https://id.14a.com/3W5E11264SGPN

// Look up package info
$packageInfo = $api->get("/retailid/v2/receive/qr/{$shortCode}?licenseNumber={$license}");

// Returns: Package details, item info, lab results, chain of custody
```

### 3. Merge Partial Packages

```php
// Combine two partially-used packages of the same item
$api->post("/retailid/v2/merge?licenseNumber={$license}", [
    'packageLabels' => [
        '1A4060300000001000000051', // 2.5g remaining
        '1A4060300000001000000052'  // 1.0g remaining
    ]
]);
// Result: New package with 3.5g, old packages marked as merged
```

---

## Important Notes

- **QR URL Format**: QR URLs typically follow the pattern `https://id.14a.com/{shortCode}`
- **License requirement**: All endpoints require `licenseNumber` query parameter
- **Batch operations**: Associate endpoint supports multiple packages per request
- **Merge restrictions**: Only compatible packages can be merged (same item, same state)
- **Quantity for generate**: Typically matches number of individual retail units in package

---

## Related Categories

- `categories/packages.md` - Package management endpoints
- `categories/labtests.md` - Lab test results (visible in QR lookups)
- `patterns/batch-operations.md` - Batch operation patterns

---

**For complete request/response details**, read `collections/metrc-retailid.postman_collection.json`
