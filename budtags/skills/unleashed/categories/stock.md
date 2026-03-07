# Stock Category

**Stock Adjustments Endpoints**: 3
**Stock On Hand Endpoints**: 3
**Related Read-Only**: Stock Counts, Recost Adjustments

---

## Stock On Hand (Read-Only)

### GET Endpoints

- `GET /StockOnHand` - List stock levels (paginated)
- `GET /StockOnHand/{productGuid}` - Stock for single product
- `GET /StockOnHand/{productGuid}/AllWarehouses` - Stock across all warehouses

### Filters
| Filter | Type | Description |
|--------|------|-------------|
| `productId` | GUID(s) | Comma-separated product GUIDs |
| `warehouseCode` | string | Filter by warehouse code |
| `warehouseName` | string | Filter by warehouse name |
| `asAtDate` | date | Stock levels at specific date (YYYY-MM-DD) |
| `isAssembled` | boolean | Include auto-assembly BOM quantities |
| `modifiedSince` | date | Records modified since date |

### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `ProductCode` | string (100) | SKU |
| `ProductDescription` | string (500) | Product name |
| `ProductGuid` | GUID | Product identifier |
| `WarehouseCode` | string (15) | Warehouse code |
| `Warehouse` | string (100) | Warehouse name |
| `QtyOnHand` | decimal | Physical quantity |
| `AllocatedQty` | decimal | Reserved/allocated |
| `AvailableQty` | decimal | On hand - allocated + assemblable |
| `OnPurchase` | decimal | Pending purchase orders |
| `AvgCost` | decimal | Average unit cost |
| `TotalCost` | decimal | Extended inventory value |
| `DaysSinceLastSale` | integer (nullable) | Days since last transaction |

Note: Products without any transactions are not returned.

---

## Stock Adjustments (CRUD)

### GET Endpoints

- `GET /StockAdjustments` - List adjustments (paginated)
- `GET /StockAdjustments/{guid}` - Get single adjustment

### Filters
| Filter | Type | Description |
|--------|------|-------------|
| `adjustmentDate` | date | Adjustments since date |
| `modifiedSince` | date | Modified since date |
| `productCode` | string | Filter by product |
| `warehouseCode` | string | Filter by warehouse |

### POST Endpoint

- `POST /StockAdjustments` - Create stock adjustment

Note: No PUT or DELETE for Stock Adjustments.

### Stock Adjustment Fields
| Field | Type | Length | Required |
|-------|------|--------|----------|
| `AdjustmentReason` | string | 20 | Required |
| `Warehouse` | object | - | Required (Guid or WarehouseCode) |
| `StockAdjustmentLines` | array | - | Required (min 1 line) |
| `AdjustmentDate` | datetime | - | Optional (UTC) |
| `AdjustmentNumber` | string | 20 | Optional |
| `Status` | string | 20 | Optional |
| `AccountCode` | string | 50 | Optional |

### Stock Adjustment Line Fields
| Field | Type | Length | Required |
|-------|------|--------|----------|
| `Product` | object | - | Required (Guid or ProductCode) |
| `NewQuantity` | decimal | - | Required |
| `NewActualValue` | decimal | - | Required |
| `Comments` | string | 200 | Optional |
| `SerialNumbers` | array | - | Optional (completed adjustments only) |
| `BatchNumbers` | array | - | Optional (completed adjustments only) |

---

## Common Use Cases

### 1. Check Stock Levels
```php
$response = $api->get('/StockOnHand', [
    'warehouseCode' => 'MAIN',
    'pageSize' => 500,
]);
$stock = $response->json()['Items'];
```

### 2. Stock at Specific Date
```php
$response = $api->get('/StockOnHand', [
    'asAtDate' => '2025-01-31',
    'warehouseCode' => 'MAIN',
]);
```

### 3. Create Stock Adjustment
```php
$api->post('/StockAdjustments', [
    'AdjustmentReason' => 'Count',
    'AdjustmentDate' => now()->format('Y-m-d'),
    'Status' => 'Completed',
    'Warehouse' => ['WarehouseCode' => 'MAIN'],
    'StockAdjustmentLines' => [
        [
            'Product' => ['ProductCode' => 'SKU-001'],
            'NewQuantity' => 100,
            'NewActualValue' => 500.00,
            'Comments' => 'Inventory count adjustment',
        ],
    ],
]);
```

### 4. Stock for Specific Product Across Warehouses
```php
$response = $api->get("/StockOnHand/{$productGuid}/AllWarehouses");
$warehouse_stock = $response->json();
```

---

## Important Notes

- Serial/batch numbers can only be assigned to "Completed" stock adjustments
- JSON uses `Identifier` for serial numbers, XML uses `SerialNumber`
- JSON uses `Number` for batch numbers, XML uses `BatchNumber`
- Stock On Hand excludes products with zero transactions
- All datetime fields in UTC only
