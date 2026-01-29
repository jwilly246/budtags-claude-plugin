# Scenario: Record Sales Receipt

**Goal**: Record retail sales transaction to customer

**License Compatibility**: ⚠️ **RETAIL LICENSES ONLY** (AU-R-######)

**Complexity**: Moderate

**Prerequisites**:
- Active packages with available inventory
- Customer type (Consumer, Patient, Caregiver)
- Payment method

---

## Workflow

1. Verify packages available
2. Calculate totals
3. Submit sales receipt
4. (Optional) Print receipt

---

## Implementation

### Step 1: Prepare Sales Data

```php
$sale = [
    [
        'SalesDateTime' => now()->utc()->format('Y-m-d\TH:i:s\Z'),
        'SalesCustomerType' => 'Consumer', // or 'Patient', 'Caregiver'
        'PatientLicenseNumber' => null, // Required for medical sales
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
```

### Step 2: Submit to Metrc

**Endpoint**: `POST /sales/v2/receipts`

```php
try {
    $api->post("/sales/v2/receipts?licenseNumber={$license}", $sale);
    return redirect()->back()->with('message', 'Sale recorded successfully');
} catch (\Exception $e) {
    Log::error("Sales receipt failed: " . $e->getMessage());
    return redirect()->back()->with('error', $e->getMessage());
}
```

---

## Medical Sales Example

```php
// For medical sales, patient license required
$medicalSale = [
    [
        'SalesDateTime' => now()->utc()->format('Y-m-d\TH:i:s\Z'),
        'SalesCustomerType' => 'Patient',
        'PatientLicenseNumber' => 'MMJ-12345', // Required!
        'CaregiverLicenseNumber' => null,
        'IdentificationMethod' => 'Medical Card',
        'Transactions' => [/* ... */]
    ]
];
```

---

## Related

- `categories/sales.md` - Sales endpoints
- `categories/patients.md` - Patient management
- `patterns/license-types.md` - Retail license requirements
