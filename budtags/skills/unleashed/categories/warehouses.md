# Warehouses & Stock Transfers Category

**Stock Transfer Endpoints**: 10
**Operations**: Full CRUD + Complete + Line management
**Related Read-Only**: Warehouses

---

## Warehouse Stock Transfers

### GET Endpoints

- `GET /WarehouseStockTransfers` - List transfers (paginated)
- `GET /WarehouseStockTransfers/{guid}` - Get by GUID
- `GET /WarehouseStockTransfers/{transferNumber}` - Get by number

### Filters
| Filter | Type | Description |
|--------|------|-------------|
| `transferStatus` | string | Comma-separated (e.g., "Parked,Completed") |
| `modifiedSince` | date | Modified since (YYYY-MM-DD) |

### POST Endpoints

- `POST /WarehouseStockTransfers` - Create transfer
- `POST /WarehouseStockTransfers/{guid}/Lines` - Add line
- `POST /WarehouseStockTransfers/{guid}/Complete` - Complete transfer

### PUT Endpoints

- `PUT /WarehouseStockTransfers/{guid}` - Update transfer
- `PUT /WarehouseStockTransfers/{guid}/Lines/{lineGuid}` - Update line

### DELETE Endpoints

- `DELETE /WarehouseStockTransfers/{guid}` - Delete transfer
- `DELETE /WarehouseStockTransfers/{guid}/Lines/{lineGuid}` - Delete line

### Key Fields

#### Transfer
| Field | Type | Length | Required |
|-------|------|--------|----------|
| `SourceWarehouse` | object | - | Required (Guid or WarehouseCode) |
| `DestinationWarehouse` | object | - | Required (Guid or WarehouseCode) |
| `TransferStatus` | string | 20 | Required |
| `TransferDetails` | array | - | Required (min 1 line) |
| `OrderDate` | datetime | - | Optional (UTC) |
| `DeliveryDate` | datetime | - | Optional (UTC) |
| `Comments` | string | 1024 | Optional |

#### Transfer Detail Line
| Field | Type | Required |
|-------|------|----------|
| `Product` | object | Required (Guid or ProductCode) |
| `TransferQuantity` | decimal | Required (>0) |
| `Comments` | string (1024) | Optional |

---

## Warehouses (Read-Only)

- `GET /Warehouses` - List all warehouses

### Warehouse Fields
| Field | Type | Length |
|-------|------|--------|
| `Guid` | GUID | - |
| `WarehouseCode` | string | 15 |
| `WarehouseName` | string | 100 |
| `IsDefault` | boolean | - |
| `Obsolete` | boolean | - |
| `StreetNo` | string | 500 |
| `AddressLine1/2` | string | 500 |
| `City` | string | 500 |
| `Region` | string | 500 |
| `Country` | string | 500 |
| `PostCode` | string | 500 |
| `PhoneNumber` | string | 25 |
| `ContactName` | string | 50 |

---

## Common Use Cases

### Create Inter-Warehouse Transfer
```php
$api->post('/WarehouseStockTransfers', [
    'SourceWarehouse' => ['WarehouseCode' => 'MAIN'],
    'DestinationWarehouse' => ['WarehouseCode' => 'RETAIL'],
    'TransferStatus' => 'Parked',
    'OrderDate' => now()->format('Y-m-d'),
    'TransferDetails' => [
        [
            'Product' => ['ProductCode' => 'SKU-001'],
            'TransferQuantity' => 50,
        ],
    ],
]);
```

---

## Important Notes

- POST/PUT disallow user-generated GUIDs for transfers
- Blank fields on PUT overwrite previous values
- TransferQuantity must be greater than zero
