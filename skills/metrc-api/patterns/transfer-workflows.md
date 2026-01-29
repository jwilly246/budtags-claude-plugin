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

```javascript
POST /transfers/v1/external/outgoing

{
  "LicenseNumber": "123-ABC",
  "DestinationFacilityLicenseNumber": "456-DEF",
  "DestinationFacilityName": "Recipient Facility Name",
  "TransferTypeName": "Transfer",
  "ShipmentTypeName": "Wholesale Product",
  "PlannedRoute": "Take Highway 1 to Main St",
  "EstimatedDepartureDateTime": "2025-01-15T10:00:00",
  "EstimatedArrivalDateTime": "2025-01-15T14:00:00",
  "Transporters": [
    {
      "TransporterFacilityLicenseNumber": null,
      "DriverName": "John Smith",
      "DriverLicenseNumber": "D1234567",
      "PhoneNumber": "555-1234",
      "VehicleMake": "Toyota",
      "VehicleModel": "Tacoma",
      "VehicleLicensePlateNumber": "ABC123"
    }
  ],
  "Packages": [
    {
      "PackageLabel": "1A4000000000001000012345",
      "WholesalePrice": 100.00
    },
    {
      "PackageLabel": "1A4000000000001000067890",
      "WholesalePrice": 150.00
    }
  ]
}
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

```javascript
PUT /transfers/v1/external/outgoing

{
  "Id": 12345,  // TransferId from Step 1
  "LicenseNumber": "123-ABC",
  "DestinationFacilityLicenseNumber": "456-DEF",
  "DestinationFacilityName": "Recipient Facility Name",
  "TransferTypeName": "Transfer",
  "ShipmentTypeName": "Wholesale Product",
  "PlannedRoute": "UPDATED: Take Highway 2 instead",
  "EstimatedDepartureDateTime": "2025-01-15T11:00:00",  // Changed time
  "EstimatedArrivalDateTime": "2025-01-15T15:00:00"
}
```

**Note:** You can only update certain fields. Cannot modify packages or transporters after creation - must delete and recreate.

### Step 3: Depart the Transfer

Once the transfer is ready to depart:

```javascript
PUT /transfers/v1/external/outgoing/depart

{
  "Id": 12345,  // TransferId
  "ActualDepartureDateTime": "2025-01-15T10:30:00"
}
```

### Step 4: Complete the Transfer (At Destination)

The receiving facility must accept the transfer:

```javascript
PUT /transfers/v1/external/incoming/{id}/deliveries/{deliveryId}/packages/wholesale

[
  {
    "PackageLabel": "1A4000000000001000012345",
    "ShipperWholesalePrice": 100.00,
    "ReceivedDateTime": "2025-01-15T14:30:00"
  },
  {
    "PackageLabel": "1A4000000000001000067890",
    "ShipperWholesalePrice": 150.00,
    "ReceivedDateTime": "2025-01-15T14:30:00"
  }
]
```

---

## Tracking Outgoing Transfers (Cascading API Calls)

To track packages leaving your inventory via outgoing transfers, you must make **cascading API calls**. This is necessary because IDs are part of the URL path.

### The Cascading Call Pattern

**⚠️ Rate Limiting Warning:** This pattern requires multiple API calls and can quickly hit rate limits for facilities with many transfers.

```javascript
async function trackOutgoingTransfers(facility) {
  const transferredPackages = [];

  // Step 1: Get all outgoing transfers
  const transfers = await axios.get('/transfers/v1/outgoing', {
    params: { licenseNumber: facility }
  });

  console.log(`Found ${transfers.data.length} outgoing transfers`);

  // Step 2: For each transfer, get its deliveries
  for (const transfer of transfers.data) {
    try {
      const deliveries = await axios.get(`/transfers/v1/${transfer.Id}/deliveries`);

      console.log(`Transfer ${transfer.Id} has ${deliveries.data.length} deliveries`);

      // Step 3: For each delivery, get its packages
      for (const delivery of deliveries.data) {
        const packages = await axios.get(`/transfers/v1/deliveries/${delivery.Id}/packages`);

        console.log(`Delivery ${delivery.Id} has ${packages.data.length} packages`);

        // Store package data with transfer/delivery context
        transferredPackages.push(...packages.data.map(pkg => ({
          ...pkg,
          transferId: transfer.Id,
          deliveryId: delivery.Id,
          destinationFacility: transfer.DestinationFacilityName,
          status: transfer.ShipmentTransactionType
        })));

        // IMPORTANT: Add delay to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      // Add delay between transfers
      await new Promise(resolve => setTimeout(resolve, 500));

    } catch (error) {
      console.error(`Error processing transfer ${transfer.Id}:`, error.message);

      // Handle rate limiting
      if (error.response?.status === 429) {
        const retryAfter = parseInt(error.response.headers['retry-after'] || 60);
        console.log(`Rate limited. Waiting ${retryAfter} seconds...`);
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
        // Retry logic here...
      }
    }
  }

  return transferredPackages;
}
```

### Performance Analysis

**API Call Calculation:**
- If you have **10 outgoing transfers**
- Each transfer has **2 deliveries**
- Each delivery has **5 packages**

**Total API calls:**
1. `GET /outgoing` = **1 call**
2. `GET /transfers/{id}/deliveries` × 10 = **10 calls**
3. `GET /deliveries/{id}/packages` × 20 = **20 calls**
4. **Total: 31 API calls**

**Time estimate** (with 500ms delays):
- 31 calls × 500ms = **15.5 seconds minimum**

### Optimization Strategies

#### 1. Cache Transfer Data

```javascript
// Cache transfers for 1 hour to avoid redundant calls
const cacheKey = `transfers:outgoing:${facility}`;
const cachedTransfers = await redis.get(cacheKey);

if (cachedTransfers) {
  return JSON.parse(cachedTransfers);
}

const transfers = await trackOutgoingTransfers(facility);

await redis.setex(cacheKey, 3600, JSON.stringify(transfers));

return transfers;
```

#### 2. Use lastModifiedStart Filter

```javascript
// Only fetch transfers modified in last hour
const oneHourAgo = new Date();
oneHourAgo.setHours(oneHourAgo.getHours() - 1);

const transfers = await axios.get('/transfers/v1/outgoing', {
  params: {
    licenseNumber: facility,
    lastModifiedStart: oneHourAgo.toISOString(),
    lastModifiedEnd: new Date().toISOString()
  }
});
```

#### 3. Parallel Requests (Use with Caution)

```javascript
// Process transfers in parallel (respects rate limits via connection pooling)
const transferPromises = transfers.data.map(async (transfer) => {
  const deliveries = await axios.get(`/transfers/v1/${transfer.Id}/deliveries`);

  const packagePromises = deliveries.data.map(async (delivery) => {
    return await axios.get(`/transfers/v1/deliveries/${delivery.Id}/packages`);
  });

  return await Promise.all(packagePromises);
});

const allPackages = await Promise.all(transferPromises);
```

**Trade-off:** Faster but higher risk of hitting rate limits. Monitor 429 responses carefully.

---

## Tracking Incoming Transfers

Incoming transfers are simpler because the receiving facility typically doesn't need cascading calls.

```javascript
async function trackIncomingTransfers(facility) {
  const incoming = await axios.get('/transfers/v1/incoming', {
    params: { licenseNumber: facility }
  });

  // Filter for pending transfers
  const pending = incoming.data.filter(t =>
    t.ShipmentTransactionType === 'Pending'
  );

  return {
    total: incoming.data.length,
    pending: pending.length,
    transfers: incoming.data
  };
}
```

### Accepting Incoming Packages

```javascript
async function acceptIncomingDelivery(transferId, deliveryId, packages) {
  // packages = [{ PackageLabel, ShipperWholesalePrice, ReceivedDateTime }]

  // Must chunk to 10 packages max (object limiting)
  const chunks = [];
  for (let i = 0; i < packages.length; i += 10) {
    chunks.push(packages.slice(i, i + 10));
  }

  for (const chunk of chunks) {
    await axios.put(
      `/transfers/v1/external/incoming/${transferId}/deliveries/${deliveryId}/packages/wholesale`,
      chunk
    );

    // Add delay between chunks
    await new Promise(resolve => setTimeout(resolve, 500));
  }
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
```javascript
{
  "TransporterFacilityLicenseNumber": null,  // OK if non-licensed driver
  "DriverName": "REQUIRED",
  "DriverLicenseNumber": "REQUIRED",
  "PhoneNumber": "REQUIRED",
  "VehicleMake": "REQUIRED",
  "VehicleModel": "REQUIRED",
  "VehicleLicensePlateNumber": "REQUIRED"
}
```

### 3. Package Not in Active Inventory

**Error:** `"Package 1A4000000000001000012345 is not in active inventory"`

**Cause:** Package has been finished, discontinued, or already transferred.

**Solution:** Verify package is in active inventory before creating transfer:
```javascript
const pkg = await axios.get('/packages/v1/active', {
  params: {
    licenseNumber: facility,
    label: packageLabel
  }
});

if (!pkg.data || pkg.data.length === 0) {
  throw new Error('Package not found in active inventory');
}
```

### 4. Rate Limiting on Cascading Calls

**Error:** HTTP 429 "Too Many Requests"

**Cause:** Making too many cascading calls too quickly.

**Solution:** See optimization strategies above + implement exponential backoff:
```javascript
async function fetchWithRetry(url, params, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await axios.get(url, { params });
    } catch (error) {
      if (error.response?.status === 429 && i < maxRetries - 1) {
        const retryAfter = parseInt(error.response.headers['retry-after'] || 60);
        const delay = Math.min(retryAfter * 1000, Math.pow(2, i) * 1000);

        console.log(`Rate limited. Retry ${i + 1}/${maxRetries} in ${delay}ms`);
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw error;
      }
    }
  }
}
```

---

## Related Patterns

- **[Object Limiting](./object-limiting.md)** - Handle 10 object limit when accepting packages
- **[Rate Limiting](./rate-limiting.md)** - Essential for cascading API call patterns
- **[Inventory Management](./inventory-management.md)** - Track packages leaving via transfers
- **[Error Handling](./error-handling.md)** - Comprehensive error handling strategies

---

## Quick Reference

```
✅ DO:
- Add delays between cascading API calls (500ms minimum)
- Cache transfer data to avoid redundant calls
- Use lastModifiedStart filter to reduce API calls
- Chunk packages into batches of 10 when accepting
- Handle 429 rate limit errors with Retry-After header
- Verify packages are in active inventory before transferring

❌ DON'T:
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
- [ ] Add 500ms delays between cascading calls
- [ ] Implement rate limit retry logic
- [ ] Cache results for 1 hour
- [ ] Monitor for HTTP 429 errors
