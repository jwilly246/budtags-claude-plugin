# Sales Shipments Category

**Total Endpoints**: 6
**Operations**: Full CRUD + Line deletion
**Related Read-Only**: Delivery Methods, Shipping Companies

---

## GET Endpoints

- `GET /SalesShipments` - List shipments (paginated)
- `GET /SalesShipments/{guid}` - Get single shipment

### Filters
| Filter | Type | Description |
|--------|------|-------------|
| `orderNumber` | string | Filter by SO number (overrides other filters) |
| `shipmentStatus` | string | Filter by status |
| `startDate` | date | Shipments created after |
| `endDate` | date | Shipments created before |
| `modifiedSince` | datetime | Modified since (UTC) |
| `warehouseCode` | string | Filter by warehouse |
| `serialBatch` | boolean | Include serial/batch numbers |
| `orderBy` | string | `ShipmentNumber` (default: `LastModifiedOn`) |
| `sort` | string | `asc`, `desc` |

---

## POST Endpoints

- `POST /SalesShipments` - Create shipment

---

## PUT Endpoints

- `PUT /SalesShipments/{guid}` - Update shipment (FULL OBJECT REQUIRED)

---

## DELETE Endpoints

- `DELETE /SalesShipments/{guid}` - Delete shipment
- `DELETE /SalesShipments/Lines/{guid}` - Delete shipment line

---

## Key Fields

### Sales Shipment
| Field | Type | Length | Required (POST) |
|-------|------|--------|-----------------|
| `OrderNumber` | string | 20 | Required (identifies sales order) |
| `ShipmentStatus` | string | 20 | Required (when order management enabled) |
| `SalesShipmentLines` | array | - | Required (min 1 line) |
| `DispatchDate` | datetime | - | Optional (YYYY-MM-DD) |
| `Comments` | string | 500 | Optional (editable after dispatch) |
| `TrackingNumber` | string | 100 | Optional (editable after dispatch) |
| `ShippingCompany` | object | - | Optional (Guid or Name) |
| `ShipmentWeight` | string | 50 | Optional |
| `NumberOfPackages` | integer | - | Optional |
| `ReceiverEORI` | string | 20 | Optional |
| `ShipperEORI` | string | 20 | Optional |
| `Incoterm` | string | 3 | Optional |

### Shipment Line
| Field | Type | Required |
|-------|------|----------|
| `Product` | object | Required (Guid or ProductCode) |
| `ShipmentQty` | decimal | Required |
| `SalesOrderLineNumber` | integer | Optional (validates product match) |
| `SerialNumbers` | array | Optional |
| `BatchNumbers` | array | Optional |

### Response-Only Fields
| Field | Type | Description |
|-------|------|-------------|
| `ShipmentNumber` | string (25) | Auto-generated |
| `OrderGuid` | GUID | Related sales order |
| `Customer` | object | Customer details |
| `Warehouse` | object | Warehouse details |
| `DeliveryContact` | object | Contact details |
| `TotalCommercialValue` | decimal | Total commercial value |

---

## Common Use Cases

### 1. Fetch Shipments for Order
```php
$response = $api->get('/SalesShipments', [
    'orderNumber' => 'SO-100',
    'serialBatch' => 'true',
]);
$shipments = $response->json()['Items'];
```

### 2. Create Shipment
```php
$api->post('/SalesShipments', [
    'OrderNumber' => 'SO-100',
    'ShipmentStatus' => 'Dispatched',
    'DispatchDate' => now()->format('Y-m-d'),
    'ShippingCompany' => ['Name' => 'FedEx'],
    'TrackingNumber' => '1234567890',
    'SalesShipmentLines' => [
        [
            'Product' => ['ProductCode' => 'SKU-001'],
            'ShipmentQty' => 5.0,
        ],
    ],
]);
```

---

## Important Notes

- Blank fields on PUT overwrite existing values
- Comments and TrackingNumber remain editable after dispatch
- `serialBatch=true` on POST auto-assigns from Sales Order
- `serialBatch=true` on PUT assigns regardless of SO assignment
- Delivery address fields inherited from Sales Order
