# Purchase Orders Category

**Total Endpoints**: 11
**Operations**: Full CRUD + Receipt + Complete + Line management
**Related Read-Only**: Suppliers

---

## GET Endpoints

- `GET /PurchaseOrders` - List purchase orders (paginated)
- `GET /PurchaseOrders/{guid}` - Get single PO
- `GET /PurchaseOrders/{guid}/Costs` - Get PO costs breakdown

### Filters
| Filter | Type | Description |
|--------|------|-------------|
| `supplierCode` | string | Supplier code prefix |
| `orderNumber` | string (15) | Exact PO number (overrides others) |
| `orderStatus` | string | Parked, Placed, Unapproved, Costed, Receipted, Complete, Deleted |
| `customOrderStatus` | string | Custom status (overrides orderStatus) |
| `startDate` | date | Orders dated after |
| `endDate` | date | Orders dated before |
| `completedAfter` | date | Completed after date |
| `completedBefore` | date | Completed before date |
| `modifiedSince` | datetime | Modified since (UTC) |
| `warehouseCode` | string (15) | Filter by warehouse |
| `serialBatch` | boolean | Include serial/batch numbers |
| `brief` | boolean | Abbreviated product data (default: true) |

---

## POST Endpoints

- `POST /PurchaseOrders` - Create purchase order
- `POST /PurchaseOrders/{guid}/Lines` - Add line
- `POST /PurchaseOrders/{guid}/Receipt` - Receipt PO
- `POST /PurchaseOrders/{guid}/Complete` - Complete PO

---

## PUT Endpoints

- `PUT /PurchaseOrders/{guid}` - Update PO (FULL OBJECT REQUIRED)
- `PUT /PurchaseOrders/{guid}/Lines/{lineGuid}` - Update line

---

## DELETE Endpoints

- `DELETE /PurchaseOrders/{guid}` - Delete PO
- `DELETE /PurchaseOrders/{guid}/Lines/{lineGuid}` - Delete line

---

## Key Fields

### Purchase Order
| Field | Type | Length | Required (POST) |
|-------|------|--------|-----------------|
| `Supplier` | object | - | Required (Guid or SupplierCode) |
| `OrderStatus` | string | 50 | Required (Parked/Placed/Complete) |
| `SubTotal` | decimal | - | Required |
| `TaxTotal` | decimal | - | Required |
| `Total` | decimal | - | Required |
| `PurchaseOrderLines` | array | - | Required (min 1 line) |
| `OrderDate` | datetime | - | Optional (UTC) |
| `Currency` | object | - | Optional (must match supplier default) |
| `Tax` | object | - | Optional (TaxCode or TaxRate) |
| `Warehouse` | object | - | Optional (Guid or WarehouseCode) |
| `ExchangeRate` | decimal | - | Optional |
| `SupplierRef` | string | 500 | Optional |
| `Comments` | string | 1024 | Optional |
| `DiscountRate` | decimal | - | Optional (0-1) |
| `DeliveryDate` | datetime | - | Optional |

### Purchase Order Line
| Field | Type | Length | Required |
|-------|------|--------|----------|
| `LineNumber` | integer | - | Required |
| `Product` | object | - | Required (Guid or ProductCode) |
| `OrderQuantity` | decimal (4dp) | - | Required |
| `UnitPrice` | decimal (4dp) | - | Required |
| `LineTotal` | decimal (2dp) | - | Required |
| `LineTax` | decimal (2dp) | - | Required |
| `UnitOfMeasure` | object | - | Optional (Guid or Name) |
| `DiscountRate` | decimal | - | Optional (0-1) |
| `Comments` | string | 1024 | Optional |
| `DeliveryDate` | datetime | - | Optional |

---

## Common Use Cases

### 1. Fetch Recent POs
```php
$response = $api->get('/PurchaseOrders', [
    'modifiedSince' => now()->subWeek()->format('Y-m-d'),
    'orderStatus' => 'Placed',
    'pageSize' => 200,
]);
```

### 2. Create Purchase Order
```php
$api->post('/PurchaseOrders', [
    'OrderDate' => now()->format('Y-m-d'),
    'OrderStatus' => 'Placed',
    'Supplier' => ['SupplierCode' => 'SUPP01'],
    'Warehouse' => ['WarehouseCode' => 'MAIN'],
    'Tax' => ['TaxCode' => 'V.A.T.'],
    'SubTotal' => 500.00,
    'TaxTotal' => 100.00,
    'Total' => 600.00,
    'PurchaseOrderLines' => [
        [
            'LineNumber' => 1,
            'Product' => ['ProductCode' => 'RAW-001'],
            'OrderQuantity' => 100,
            'UnitPrice' => 5.00,
            'LineTotal' => 500.00,
            'LineTax' => 100.00,
        ],
    ],
]);
```

---

## Important Notes

- OrderNumber is read-only (system-generated, 15 chars)
- Currency cannot be changed after creation
- DiscountRate must be between 0 and 1
- At least one line with Placed/Costed/Complete status required
- Tax priority: Product tax > PO tax > Supplier tax > Default
- Pending serial/batch numbers convert to confirmed upon Receipt
