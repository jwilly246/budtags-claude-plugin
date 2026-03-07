# Webhooks Category

**Base URL**: `https://services-connect.metrc.com/` (NOT the regular Metrc API URL)
**Auth**: `X-Metrc-Auth` header with integrator API key (NOT HTTP Basic)
**Total Endpoints**: 5
**License Compatibility**: All license types

---

## Authentication

Different from the regular Metrc API. Use a header labeled `X-Metrc-Auth` set to an integrator API key. The header key does not need to match the `tpiApiKey` in the subscription body, but both must be associated with the same deployment.

```php
$headers = [
    'Content-Type' => 'application/json',
    'X-Metrc-Auth' => config('budtags.metrc_vendor_key'),
];
```

---

## GET Endpoints

- `GET /webhooks/v2` - List all webhook subscriptions
  - Returns all subscriptions for the API key used in the `X-Metrc-Auth` header
  - The `errorMessage` key will be populated if there was an error sending a notification

---

## PUT Endpoints

- `PUT /webhooks/v2` - Create or modify webhook subscriptions
  - Use case: Subscribe to Metrc object type changes, or modify existing subscriptions
  - To modify: include `subscriptionId` in the request body
  - Accepts an array of subscription objects (batch create/modify)
  - **Do NOT rely on HTTP status code** — inspect `errorMessage` and `facilities[].invalidPermission`

- `PUT /webhooks/v2/enable/{subscriptionId}` - Enable a subscription
  - Use case: Re-activate a previously disabled subscription

---

## DELETE Endpoints

- `DELETE /webhooks/v2/{subscriptionId}` - Delete a webhook subscription
  - **Irreversible** — consider disabling instead if subscription may be needed later

---

## Subscription Request Body

```json
[
    {
        "objectType": "Package",
        "url": "https://yourapp.com/api/webhooks/metrc/callback",
        "verb": "POST",
        "status": "Active",
        "userApiKey": "customer-api-key",
        "tpiApiKey": "vendor-api-key",
        "facilityLicenseNumbers": ["LICENSE-001", "LICENSE-002"],
        "template": "{\"data\":#DATA#, \"datacount\":#DATACOUNT#}",
        "errorResponseJsonTemplate": "{\"error\":#ERRORMESSAGE#, \"errorcode\":#ERRORCODE#}"
    }
]
```

### Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `objectType` | Yes | Object type string (see Available Object Types below) |
| `url` | Yes | HTTPS endpoint to receive webhook notifications |
| `verb` | Yes | `"PUT"` or `"POST"` |
| `status` | Yes | `"Active"` or `"inactive"` |
| `userApiKey` | Yes | Customer's Metrc API key |
| `tpiApiKey` | Yes | Integrator (vendor) API key |
| `facilityLicenseNumbers` | Yes | **Array** of facility license number strings |
| `serverPublicKeyFingerprint` | No | **Not currently used** — can be excluded |
| `template` | No | JSON template for payload format. Default: `{"data":#DATA#, "datacount":#DATACOUNT#}` |
| `errorResponseJsonTemplate` | No | JSON template for errors. Default: `{"error":#ERRORMESSAGE#, "errorcode":#ERRORCODE#}` |
| `subscriptionId` | No | Include to modify an existing subscription |

---

## Subscription Response Body

```json
[
    {
        "subscriptionId": 123,
        "username": "string",
        "apiKeyName": "string",
        "objectType": "Package",
        "url": "https://yourapp.com/api/webhooks/metrc/callback",
        "verb": "POST",
        "status": "Active",
        "errorMessage": "",
        "serverPublicKeyFingerprint": "",
        "template": "{\"data\":#DATA#, \"datacount\":#DATACOUNT#}",
        "errorResponseJsonTemplate": "{\"error\":#ERRORMESSAGE#, \"errorcode\":#ERRORCODE#}",
        "facilities": [
            {
                "facilityLicenseNumber": "LICENSE-001",
                "invalidPermission": false
            }
        ],
        "deployment": "string"
    }
]
```

**Critical**: Check `errorMessage` (non-empty = error) and `facilities[].invalidPermission` (true = bad permission) to verify success. Do NOT rely on HTTP status code alone.

---

## Available Object Types (19)

Employee, Facility, Harvest, Item, ItemCategory, LabTestBatch, LabTestType, Location, LocationType, Package, Plant, PlantBatch, ProcessingJob, SalesDelivery, SalesReceipt, Strain, Transfer, TransferTemplate, UnitOfMeasure

---

## Webhook Delivery Behavior

- **Sends the full object** (not a delta/diff) — same shape as the regular API response for that entity
- **Default payload format**: `{"data": <entity>, "datacount": <count>}`
- **Timing**: Within 15 minutes of the triggering action (not instant)
- **Subscriptions tied to API keys**: If the key is locked/deleted/expired, subscriptions auto-disable

---

## Example: Create a Package Subscription

```php
$vendor_key = config('budtags.metrc_vendor_key');
$user_api_key = $secret->part1; // Customer's Metrc API key

$payload = [
    [
        'objectType' => 'Package',
        'url' => config('app.url') . "/api/webhooks/metrc/{$org->webhook_token}/packages",
        'verb' => 'POST',
        'status' => 'Active',
        'userApiKey' => $user_api_key,
        'tpiApiKey' => $vendor_key,
        'facilityLicenseNumbers' => [$license],
    ]
];

$response = Http::withHeaders([
    'Content-Type' => 'application/json',
    'X-Metrc-Auth' => $vendor_key,
])->put('https://services-connect.metrc.com/webhooks/v2', $payload);

$subscriptions = $response->json();

// Verify success by inspecting response — NOT HTTP status
foreach ($subscriptions as $sub) {
    if (!empty($sub['errorMessage'])) {
        // Handle error
    }
    foreach ($sub['facilities'] ?? [] as $facility) {
        if ($facility['invalidPermission'] ?? false) {
            // Handle invalid permission for this facility
        }
    }
}
```

---

## Important Notes

- Webhook URL must be HTTPS
- `facilityLicenseNumbers` is an **array**, not a comma-separated string
- `serverPublicKeyFingerprint` is NOT USED — safely exclude it
- `template` and `errorResponseJsonTemplate` are optional with sensible defaults
- Metrc does NOT currently support request signing/HMAC verification
- To disable (not delete): set `status` to `"inactive"` via PUT, or use enable/disable endpoints
- Subscriptions are per API key — listing returns only subscriptions for the auth header's key
