# Scenario: Check-In Incoming Transfer

**Goal**: Receive and check-in packages from incoming transfer

**License Compatibility**: All license types

**Complexity**: Moderate

**Prerequisites**:
- Incoming transfer exists in Metrc
- Transfer packages documented

---

## Workflow

1. Get incoming transfers
2. View transfer packages
3. Verify package details
4. Accept transfer (automatic package creation)

---

## Implementation

### Step 1: Get Incoming Transfers

```php
$api = new MetrcApi();
$api->set_user($user);
$license = session('license');

// Get pending incoming transfers
$incoming = $api->get("/transfers/v2/incoming", [
    'licenseNumber' => $license
]);

// Filter to pending only
$pending = array_filter($incoming, function($transfer) {
    return $transfer['ShipmentTransactionType'] === 'Standard' &&
           !$transfer['ReceivedDateTime'];
});
```

### Step 2: View Transfer Packages

```php
// Get first pending transfer
$transfer = $pending[0];
$deliveryId = $transfer['DeliveryId'];

// Get packages in delivery
$packages = $api->get("/transfers/v2/deliveries/{$deliveryId}/packages", [
    'licenseNumber' => $license
]);

foreach ($packages as $package) {
    echo "{$package['PackageLabel']} - {$package['ProductName']} - {$package['ShippedQuantity']} {$package['ShippedUnitOfMeasure']}\n";
}
```

### Step 3: Accept Transfer

**Note**: Acceptance happens automatically when you view the transfer in Metrc web interface, or you can create an external incoming transfer record.

```php
// For external incoming transfers, create record
$incomingTransfer = [
    [
        'ShipperLicenseNumber' => $transfer['ShipperLicenseNumber'],
        'ShipperName' => $transfer['ShipperName'],
        'ShipperMainPhoneNumber' => $transfer['ShipperMainPhoneNumber'],
        'DriverName' => $transfer['DriverName'],
        'DriverLicenseNumber' => $transfer['DriverLicenseNumber'],
        'VehicleMake' => $transfer['VehicleMake'],
        'VehicleModel' => $transfer['VehicleModel'],
        'VehicleLicensePlateNumber' => $transfer['VehicleLicensePlateNumber'],
        'ReceivedDateTime' => now()->utc()->format('Y-m-d\TH:i:s\Z'),
        'Packages' => array_map(function($pkg) {
            return [
                'PackageLabel' => $pkg['PackageLabel'],
                'ReceivedQuantity' => $pkg['ShippedQuantity'],
                'ReceivedUnitOfMeasure' => $pkg['ShippedUnitOfMeasure']
            ];
        }, $packages)
    ]
];

$api->post("/transfers/v2/external/incoming?licenseNumber={$license}", $incomingTransfer);
```

---

## Common Issues

### Issue: "Transfer already accepted"
**Solution**: Check if `ReceivedDateTime` is set

```php
if ($transfer['ReceivedDateTime']) {
    throw new Exception("Transfer already accepted on " . $transfer['ReceivedDateTime']);
}
```

---

## Related

- `categories/transfers.md` - Transfer endpoints
- `categories/packages.md` - Package endpoints
