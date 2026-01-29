# Webhooks Category

**Collection File**: `collections/metrc-webhooks.postman_collection.json`
**Total Endpoints**: 5
**License Compatibility**: All license types

---

## GET Endpoints

- `GET /webhooks/v2/subscriptions` - Get webhook subscriptions
  - Use case: List active webhook configurations

---

## POST Endpoints

- `POST /webhooks/v2/subscriptions` - Create webhook subscription
  - Use case: Subscribe to Metrc events (package updates, transfers, etc.)
  - Request body: Webhook URL, event types

---

## PUT Endpoints

- `PUT /webhooks/v2/subscriptions` - Update webhook subscription
  - Use case: Modify webhook URL or event filters

---

## DELETE Endpoints

- `DELETE /webhooks/v2/subscriptions/{id}` - Delete webhook subscription
  - Use case: Remove webhook when no longer needed

---

## Example

```php
$subscription = [
    [
        'Url' => 'https://myapp.com/api/metrc-webhook',
        'Events' => ['PackageCreated', 'PackageModified', 'TransferCreated']
    ]
];

$api->post("/webhooks/v2/subscriptions?licenseNumber={$license}", $subscription);
```

---

## Common Events

- PackageCreated, PackageModified, PackageFinished
- PlantCreated, PlantModified, PlantHarvested (cultivation only)
- TransferCreated, TransferModified, TransferAccepted
- SaleCreated (retail only)

---

## Important Notes

- Webhook URL must be HTTPS
- Metrc will POST event data to your endpoint
- Implement signature verification for security
- Handle retries and acknowledgments properly
