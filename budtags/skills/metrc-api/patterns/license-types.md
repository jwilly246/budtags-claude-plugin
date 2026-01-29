# License Type Restrictions

**CRITICAL: Different Metrc license types have access to different endpoints.**

This is the **#1 cause** of 401/403 errors in Metrc integrations. Always verify license type before calling endpoints.

---

## License Type Format

Metrc license numbers follow the pattern: `{STATE}-{TYPE}-{NUMBER}`

- **STATE**: 2-letter state code (CA, CO, MI, etc.)
- **TYPE**: License type identifier
- **NUMBER**: Sequential number

Examples:
- `AU-C-000001` - Cultivation license
- `AU-P-000002` - Processing/Manufacturing license
- `AU-R-000003` - Retail license
- `AU-L-000004` - Testing Lab license

---

## License Type Compatibility Matrix

| Endpoint Category | Cultivation (C) | Processing (P) | Retail (R) | Testing Lab (L) |
|------------------|-----------------|----------------|------------|-----------------|
| **Packages** | ✅ Full Access | ✅ Full Access | ✅ Full Access | ❌ Limited |
| **Plants** | ✅ Full Access | ❌ NO ACCESS | ❌ NO ACCESS | ❌ NO ACCESS |
| **Plant Batches** | ✅ Full Access | ❌ NO ACCESS | ❌ NO ACCESS | ❌ NO ACCESS |
| **Harvests** | ✅ Full Access | ✅ Limited | ❌ NO ACCESS | ❌ NO ACCESS |
| **Sales** | ❌ NO ACCESS | ❌ NO ACCESS | ✅ Full Access | ❌ NO ACCESS |
| **Transfers** | ✅ Outgoing | ✅ Both | ✅ Both | ✅ Both |
| **Items** | ✅ Full Access | ✅ Full Access | ✅ Full Access | ✅ Limited |
| **Lab Tests** | ✅ Submit | ✅ Submit | ✅ View | ✅ Full Access |
| **Processing Jobs** | ❌ Limited | ✅ Full Access | ❌ NO ACCESS | ❌ NO ACCESS |
| **Locations** | ✅ Full Access | ✅ Full Access | ✅ Full Access | ✅ Full Access |
| **Strains** | ✅ Full Access | ✅ Full Access | ✅ Full Access | ❌ View Only |
| **Tags** | ✅ Plant + Package | ✅ Package Only | ✅ Package Only | ✅ Package Only |
| **Patients** | ❌ NO ACCESS | ❌ NO ACCESS | ✅ Full Access (medical states) | ❌ NO ACCESS |

---

## Detailed License Capabilities

### Cultivation Licenses (AU-C-######)

**Primary Purpose**: Growing cannabis plants

**Full Access To**:
- ✅ ALL plant endpoints (`/plants/v2/*`)
- ✅ ALL plant batch endpoints (`/plantbatches/v2/*`)
- ✅ Harvest creation and management
- ✅ Package creation from harvests
- ✅ Waste tracking (plant waste reasons + methods)
- ✅ Strain management
- ✅ Plant tag assignment
- ✅ Outgoing transfers

**LIMITED or NO Access**:
- ❌ Sales endpoints (can't sell directly to consumers)
- ❌ Retail-specific features

**Typical Workflow**:
1. Create plant batches from seeds/clones
2. Grow plants through vegetative → flowering phases
3. Harvest plants
4. Create packages from harvests
5. Transfer packages to processing/retail licensees

---

### Processing/Manufacturing Licenses (AU-P-######)

**Primary Purpose**: Processing cannabis into products

**Full Access To**:
- ✅ Package management
- ✅ Processing job creation
- ✅ Item/product creation
- ✅ Lab test submission
- ✅ Incoming/outgoing transfers
- ✅ Package tag assignment

**CRITICAL RESTRICTIONS**:
- ❌ **NO** plant endpoints (`/plants/v2/*`)
- ❌ **NO** plant batch endpoints (`/plantbatches/v2/*`)
- ❌ **NO** plant waste reasons (only harvest/package waste)
- ❌ Sales endpoints (wholesale only, via transfers)

**Typical Workflow**:
1. Receive packages via incoming transfers
2. Create processing jobs
3. Create product packages from source packages
4. Submit for lab testing
5. Transfer finished products to retailers

---

### Retail Licenses (AU-R-######)

**Primary Purpose**: Selling cannabis to consumers

**Full Access To**:
- ✅ ALL sales endpoints (`/sales/v2/*`)
- ✅ Package management
- ✅ Incoming/outgoing transfers
- ✅ Patient management (medical states)
- ✅ Customer type tracking
- ✅ Sales receipts and transactions

**CRITICAL RESTRICTIONS**:
- ❌ **NO** plant endpoints
- ❌ **NO** plant batch endpoints
- ❌ **NO** processing job endpoints

**Typical Workflow**:
1. Receive packages via incoming transfers
2. Manage inventory
3. Record sales to customers
4. Track patient information (if medical)

---

### Testing Lab Licenses (AU-L-######)

**Primary Purpose**: Lab testing and COA generation

**Full Access To**:
- ✅ Lab test result endpoints
- ✅ COA document upload/management
- ✅ Package viewing (for testing)

**LIMITED Access**:
- ✅ View packages (read-only)
- ✅ View items (read-only)

**RESTRICTIONS**:
- ❌ Cannot create/modify packages
- ❌ Cannot create items
- ❌ No plant access
- ❌ No sales

---

## Code Examples

### 1. Check License Type Before API Call

```php
class MetrcApi {

    private function check_license_compatibility(string $endpoint, string $license): void
    {
        $licenseType = explode('-', $license)[1]; // Extract 'C', 'P', 'R', or 'L'

        // Plant endpoints - cultivation only
        if (str_contains($endpoint, '/plants/v2') && $licenseType !== 'C') {
            throw new Exception(
                "Plant endpoints require Cultivation license. Current: {$license} (Type: {$licenseType})"
            );
        }

        // Plant batch endpoints - cultivation only
        if (str_contains($endpoint, '/plantbatches/v2') && $licenseType !== 'C') {
            throw new Exception(
                "Plant batch endpoints require Cultivation license. Current: {$license}"
            );
        }

        // Sales endpoints - retail only
        if (str_contains($endpoint, '/sales/v2') && $licenseType !== 'R') {
            throw new Exception(
                "Sales endpoints require Retail license. Current: {$license}"
            );
        }
    }

    public function get(string $endpoint, array $params = []): array
    {
        $license = $params['licenseNumber'] ?? null;

        if ($license) {
            $this->check_license_compatibility($endpoint, $license);
        }

        // Proceed with API call...
    }
}
```

### 2. Get License-Appropriate Waste Reasons

```php
// ✅ CORRECT - Only fetch plant waste_reasons for cultivation licenses
$licenseType = explode('-', $license)[1];

if ($licenseType === 'C') {
    // Cultivation - can access plant waste reasons
    $plant_waste_reasons = $api->get("/plants/v2/waste/reasons?licenseNumber={$license}");
} else {
    // Processing/Retail - plant waste reasons will error
    $plant_waste_reasons = null;
}

// All license types can access general waste methods
$waste_methods = $api->get("/wastemethods/v2/all?licenseNumber={$license}");
```

### 3. Conditional Endpoint Loading

```php
public function get_available_endpoints(string $license): array
{
    $licenseType = explode('-', $license)[1];

    $endpoints = [
        'packages' => true,
        'items' => true,
        'locations' => true,
        'transfers' => true,
    ];

    // Add license-specific endpoints
    switch ($licenseType) {
        case 'C': // Cultivation
            $endpoints['plants'] = true;
            $endpoints['plantbatches'] = true;
            $endpoints['harvests'] = true;
            break;

        case 'P': // Processing
            $endpoints['processingjobs'] = true;
            $endpoints['harvests'] = true; // Limited
            break;

        case 'R': // Retail
            $endpoints['sales'] = true;
            $endpoints['patients'] = true;
            break;

        case 'L': // Testing Lab
            $endpoints['labtests'] = true;
            break;
    }

    return $endpoints;
}
```

---

## Common Errors and Fixes

### Error: 401 Unauthorized on `/plants/v2/vegetative`

**Cause**: Processing or Retail license attempting to access plant endpoint

**Fix**:
```php
// Check license type first
$licenseType = explode('-', $license)[1];

if ($licenseType !== 'C') {
    // Don't call plant endpoints
    return [];
}

// Safe to call for cultivation licenses
$plants = $api->get("/plants/v2/vegetative?licenseNumber={$license}");
```

### Error: 403 Forbidden on `/sales/v2/receipts`

**Cause**: Non-retail license attempting to access sales endpoint

**Fix**:
```php
// Only retail licenses can record sales
if ($licenseType !== 'R') {
    throw new Exception("Sales features require retail license");
}

$sales = $api->post("/sales/v2/receipts?licenseNumber={$license}", $data);
```

---

## Best Practices

1. **Always check license type** before building UI features or API calls
2. **Validate on backend** - don't rely on frontend checks alone
3. **Cache license type** - extract once and store in session
4. **Show relevant features only** - hide plant management for non-cultivation users
5. **Provide clear error messages** - explain license type requirements
6. **Test with all license types** - ensure your integration handles each type correctly

---

## Summary

| License Type | Primary Use | Key Access | Key Restrictions |
|--------------|-------------|------------|------------------|
| **Cultivation (C)** | Growing | Plants, Harvests | No Sales |
| **Processing (P)** | Manufacturing | Processing Jobs, Packages | No Plants, No Sales |
| **Retail (R)** | Consumer Sales | Sales, Patients | No Plants, No Processing |
| **Testing Lab (L)** | Lab Testing | Lab Tests, COAs | Read-only for most |

**Golden Rule**: When in doubt, check the license type first!
