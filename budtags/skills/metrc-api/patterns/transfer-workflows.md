# Metrc API Transfer Workflows

## Overview

Transfers are a core compliance workflow in Metrc, representing the movement of cannabis products between facilities. Creating and tracking transfers requires understanding the **cascading API call pattern** and the relationships between transfers, deliveries, packages, and transporters.

This guide covers best practices for:
- Creating outgoing transfers (complex multi-step workflow)
- Tracking incoming transfers
- Handling the cascading API call pattern
- Rate limiting considerations

---

## Transfer Data Model

### Entity Relationships

```
Transfer (top-level)
├── Delivery (1 or more per transfer)
│   ├── Package (1 or more per delivery)
│   └── Transporter (1 or more per delivery)
└── Destination Facility
```

**Key Points:**
- A **Transfer** can have multiple **Deliveries**
- Each **Delivery** can have multiple **Packages**
- Each **Delivery** requires at least one **Transporter**
- IDs are returned in order from POST requests

---

## Creating Outgoing Transfers (Multi-Step Workflow)

Creating an outgoing transfer is a **multi-step process** involving several API calls in sequence.

### Step 1: Create the Transfer

```php
$api = app(\App\Services\Api\MetrcApi::class);
$api->set_user(request()->user());
$license = session('license');

$transferData = [
    [
        'LicenseNumber' => $license,
        'DestinationFacilityLicenseNumber' => '456-DEF',
        'DestinationFacilityName' => 'Recipient Facility Name',
        'TransferTypeName' => 'Transfer',
        'ShipmentTypeName' => 'Wholesale Product',
        'PlannedRoute' => 'Take Highway 1 to Main St',
        'EstimatedDepartureDateTime' => now()->addHour()->utc()->format('Y-m-d\TH:i:s\Z'),
        'EstimatedArrivalDateTime' => now()->addHours(5)->utc()->format('Y-m-d\TH:i:s\Z'),
        'Transporters' => [
            [
                'TransporterFacilityLicenseNumber' => null,
                'DriverName' => 'John Smith',
                'DriverLicenseNumber' => 'D1234567',
                'PhoneNumber' => '555-1234',
                'VehicleMake' => 'Toyota',
                'VehicleModel' => 'Tacoma',
                'VehicleLicensePlateNumber' => 'ABC123',
            ],
        ],
        'Packages' => [
            ['PackageLabel' => '1A4000000000001000012345', 'WholesalePrice' => 100.00],
            ['PackageLabel' => '1A4000000000001000067890', 'WholesalePrice' => 150.00],
        ],
    ],
];

$response = $api->post("/transfers/v2/external/outgoing?licenseNumber={$license}", $transferData);
```

**Response:**
```json
{
  "TransferId": 12345,
  "DeliveryIds": [67890],
  "PackageIds": [111, 222],
  "TransporterIds": [333]
}
```

**Key Points:**
- `TransferId` - The newly created transfer's ID
- `DeliveryIds` - Array of created delivery IDs (one per delivery in request)
- `PackageIds` - Array of package IDs (order matches request)
- `TransporterIds` - Array of transporter IDs (order matches request)

### Step 2: Update Transfer (If Needed)

If you need to modify the transfer after creation:

```php
$updateData = [
    [
        'Id' => 12345,  // TransferId from Step 1
        'LicenseNumber' => $license,
        'PlannedRoute' => 'UPDATED: Take Highway 2 instead',
        'EstimatedDepartureDateTime' => now()->addHours(2)->utc()->format('Y-m-d\TH:i:s\Z'),
        'EstimatedArrivalDateTime' => now()->addHours(6)->utc()->format('Y-m-d\TH:i:s\Z'),
    ],
];

$api->put("/transfers/v2/external/outgoing?licenseNumber={$license}", $updateData);
```

**Note:** You can only update certain fields. Cannot modify packages or transporters after creation - must delete and recreate.

### Step 3: Depart the Transfer

Once the transfer is ready to depart:

```php
$departData = [
    [
        'Id' => 12345,
        'ActualDepartureDateTime' => now()->utc()->format('Y-m-d\TH:i:s\Z'),
    ],
];

$api->put("/transfers/v2/external/outgoing/depart?licenseNumber={$license}", $departData);
```

### Step 4: Complete the Transfer (At Destination)

The receiving facility must accept the transfer:

```php
$receiveData = [
    [
        'PackageLabel' => '1A4000000000001000012345',
        'ShipperWholesalePrice' => 100.00,
        'ReceivedDateTime' => now()->utc()->format('Y-m-d\TH:i:s\Z'),
    ],
    [
        'PackageLabel' => '1A4000000000001000067890',
        'ShipperWholesalePrice' => 150.00,
        'ReceivedDateTime' => now()->utc()->format('Y-m-d\TH:i:s\Z'),
    ],
];

$api->put("/transfers/v2/external/incoming/{$transferId}/deliveries/{$deliveryId}/packages/wholesale?licenseNumber={$license}", $receiveData);
```

---

## Tracking Outgoing Transfers (Cascading API Calls)

To track packages leaving your inventory via outgoing transfers, you must make **cascading API calls**. This is necessary because IDs are part of the URL path.

### The Cascading Call Pattern

**Rate Limiting Warning:** This pattern requires multiple API calls and can quickly hit rate limits for facilities with many transfers.

```php
public function track_outgoing_transfers(string $facility): array
{
    $api = app(\App\Services\Api\MetrcApi::class);
    $api->set_user(request()->user());
    $license = session('license');
    $transferredPackages = [];

    // Step 1: Get all outgoing transfers
    $transfers = $api->fetch_transfers_bulk($facility, 'outgoing');

    LogService::store('Transfer Tracking', "Found " . count($transfers) . " outgoing transfers");

    // Step 2: For each transfer, get its deliveries
    foreach ($transfers as $transfer) {
        try {
            $deliveries = $api->get("/transfers/v2/{$transfer['Id']}/deliveries", [
                'licenseNumber' => $license,
            ]);

            // Step 3: For each delivery, get its packages
            foreach ($deliveries as $delivery) {
                $packages = $api->get("/transfers/v2/deliveries/{$delivery['Id']}/packages", [
                    'licenseNumber' => $license,
                ]);

                // Store package data with transfer/delivery context
                foreach ($packages as $package) {
                    $transferredPackages[] = [
                        ...$package,
                        'transfer_id' => $transfer['Id'],
                        'delivery_id' => $delivery['Id'],
                        'destination_facility' => $transfer['DestinationFacilityName'],
                        'status' => $transfer['ShipmentTransactionType'],
                    ];
                }
            }
        } catch (\Exception $e) {
            LogService::store('transfer_tracking_error', "Error processing transfer {$transfer['Id']}: " . $e->getMessage());

            // Handle rate limiting
            if (str_contains($e->getMessage(), '429')) {
                LogService::store('metrc_rate_limited', 'Rate limited during transfer tracking');
                sleep(60); // Use Retry-After header value in practice
            }
        }
    }

    return $transferredPackages;
}
```

### Performance Analysis

**API Call Calculation:**
- If you have **10 outgoing transfers**
- Each transfer has **2 deliveries**
- Each delivery has **5 packages**

**Total API calls:**
1. `GET /outgoing` = **1 call**
2. `GET /transfers/{id}/deliveries` x 10 = **10 calls**
3. `GET /deliveries/{id}/packages` x 20 = **20 calls**
4. **Total: 31 API calls**

### Optimization Strategies

#### 1. Cache Transfer Data

```php
$cacheKey = "transfers:outgoing:{$facility}";

$transfers = Cache::remember($cacheKey, now()->addHour(), function () use ($facility) {
    return $this->track_outgoing_transfers($facility);
});
```

#### 2. Use lastModifiedStart Filter

```php
// Only fetch transfers modified in last hour
$transfers = $api->get("/transfers/v2/outgoing", [
    'licenseNumber' => $license,
    'lastModifiedStart' => now()->subHour()->format('Y-m-d'),
    'lastModifiedEnd' => now()->format('Y-m-d'),
]);
```

---

## Tracking Incoming Transfers

Incoming transfers are simpler because the receiving facility typically doesn't need cascading calls.

```php
public function track_incoming_transfers(string $facility): array
{
    $api = app(\App\Services\Api\MetrcApi::class);
    $api->set_user(request()->user());

    $incoming = $api->fetch_transfers_bulk($facility, 'incoming');

    // Filter for pending transfers
    $pending = collect($incoming)->filter(fn($t) => !$t['ReceivedDateTime'])->values()->all();

    return [
        'total' => count($incoming),
        'pending' => count($pending),
        'transfers' => $incoming,
    ];
}
```

### Accepting Incoming Packages

```php
public function accept_incoming_delivery(int $transferId, int $deliveryId, array $packages): void
{
    $api = app(\App\Services\Api\MetrcApi::class);
    $api->set_user(request()->user());
    $license = session('license');

    // Must chunk to 10 packages max (object limiting)
    $chunks = array_chunk($packages, 10);

    foreach ($chunks as $chunk) {
        $api->put(
            "/transfers/v2/external/incoming/{$transferId}/deliveries/{$deliveryId}/packages/wholesale?licenseNumber={$license}",
            $chunk
        );
    }

    LogService::store('transfer_accepted', "Accepted delivery {$deliveryId} with " . count($packages) . " packages");
}
```

---

## Common Transfer Errors

### 1. Invalid Transfer State

**Error:** `"Cannot modify transfer in current state"`

**Cause:** Trying to update a transfer that has already been departed or received.

**Solution:** Check transfer's `ShipmentTransactionType` before attempting modifications:
- `"Pending"` - Can be modified
- `"Departed"` - Cannot modify, can only update arrival
- `"Received"` - Complete, no further modifications

### 2. Missing Required Transporter Info

**Error:** `"DriverName is required"`

**Cause:** Not providing all required transporter fields.

**Solution:** Ensure all fields are present:
```php
[
    'TransporterFacilityLicenseNumber' => null,  // OK if non-licensed driver
    'DriverName' => 'REQUIRED',
    'DriverLicenseNumber' => 'REQUIRED',
    'PhoneNumber' => 'REQUIRED',
    'VehicleMake' => 'REQUIRED',
    'VehicleModel' => 'REQUIRED',
    'VehicleLicensePlateNumber' => 'REQUIRED',
]
```

### 3. Package Not in Active Inventory

**Error:** `"Package 1A4000000000001000012345 is not in active inventory"`

**Cause:** Package has been finished, discontinued, or already transferred.

**Solution:** Verify package is in active inventory before creating transfer:
```php
$activePackages = $api->one_day_of_packages($facility, now()->format('Y-m-d'));
$activeLabels = collect($activePackages)->pluck('Label')->all();

if (!in_array($packageLabel, $activeLabels)) {
    throw new \Exception('Package not found in active inventory');
}
```

### 4. Rate Limiting on Cascading Calls

**Error:** HTTP 429 "Too Many Requests"

**Cause:** Making too many cascading calls too quickly.

**Solution:** See optimization strategies above + implement retry with Retry-After header:
```php
private function fetch_with_retry(string $endpoint, array $params, int $maxRetries = 3): array
{
    for ($i = 0; $i < $maxRetries; $i++) {
        try {
            return $api->get($endpoint, $params);
        } catch (\Exception $e) {
            if (str_contains($e->getMessage(), '429') && $i < $maxRetries - 1) {
                LogService::store('metrc_rate_limited', "Rate limited on {$endpoint}. Retry " . ($i + 1) . "/{$maxRetries}");
                sleep(60); // Use Retry-After header value in practice
            } else {
                throw $e;
            }
        }
    }

    throw new \Exception("Max retries exceeded for {$endpoint}");
}
```

---

## Related Patterns

- **[Object Limiting](./object-limiting.md)** - Handle 10 object limit when accepting packages
- **[Inventory Management](./inventory-management.md)** - Track packages leaving via transfers
- **[Error Handling](./error-handling.md)** - Comprehensive error handling strategies

---

## Quick Reference

```
DO:
- Add delays between cascading API calls
- Cache transfer data to avoid redundant calls
- Use lastModifiedStart filter to reduce API calls
- Chunk packages into batches of 10 when accepting
- Handle 429 rate limit errors with Retry-After header
- Verify packages are in active inventory before transferring

DON'T:
- Make cascading calls without rate limit protection
- Modify transfers in "Departed" or "Received" state
- Send more than 10 packages per request when accepting
- Ignore HTTP 429 errors
- Poll outgoing transfers more than once per hour
```

## Transfer Workflow Checklist

**Creating Outgoing Transfer:**
- [ ] Verify all packages are in active inventory
- [ ] Include all required transporter fields
- [ ] Set realistic departure/arrival times
- [ ] Store returned TransferId, DeliveryIds, PackageIds
- [ ] Update local inventory status to "in_transit"

**Accepting Incoming Transfer:**
- [ ] Verify transfer is in "Departed" state
- [ ] Chunk packages into batches of 10 or fewer
- [ ] Include ShipperWholesalePrice for each package
- [ ] Set ReceivedDateTime accurately
- [ ] Update local inventory with received packages

**Tracking Transfers:**
- [ ] Use lastModifiedStart filter to reduce API calls
- [ ] Implement rate limit retry logic
- [ ] Cache results for 1 hour
- [ ] Monitor for HTTP 429 errors
