# Unleashed GUID Identifiers

GUID format, behavior, and usage patterns.

---

## Format

```
XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

Example: `c97c6b46-f1cc-4741-b236-f882995e7d9a`

Null GUID: `00000000-0000-0000-0000-000000000000`

---

## Behavior

- **Auto-generated**: If not provided on POST, the API generates one
- **Read-only after creation**: Cannot be changed once set
- **Case-insensitive**: `ABC-123` and `abc-123` treated the same
- **Unique per resource type**: GUIDs are unique within each resource

---

## Usage in API Calls

### Retrieve Single Resource
```
GET /SalesOrders/{guid}
GET /Customers/{guid}
GET /Products/{guid}
```

### Update Resource
```
PUT /SalesOrders/{guid}
POST /Products/{guid}
```

### Delete Resource
```
DELETE /SalesOrders/{guid}
```

### Sub-Resources
```
GET /Customers/{guid}/Contacts
POST /SalesOrders/{guid}/Lines
DELETE /SalesOrders/{guid}/Lines/{lineGuid}
```

---

## Nested Object References

When creating/updating, reference related objects by GUID or code:

```json
{
  "Customer": { "Guid": "abc-123-..." },
  "Warehouse": { "WarehouseCode": "MAIN" },
  "Product": { "ProductCode": "SKU-001" }
}
```

At minimum, provide either `Guid` OR the code/name field. Both are accepted.

---

## BudTags Storage

Store GUIDs locally for mapping between systems:

```php
// Store mapping
$mapping = UnleashedMapping::create([
    'organization_id' => $org_id,
    'unleashed_guid' => $response['Guid'],
    'local_model_type' => 'Product',
    'local_model_id' => $product->id,
]);

// Lookup
$guid = UnleashedMapping::where('local_model_id', $product->id)
    ->where('local_model_type', 'Product')
    ->value('unleashed_guid');
```
