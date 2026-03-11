# Sales Orders Category

**Total Endpoints**: 9
**Operations**: Full CRUD + Complete + Line management
**Related Read-Only**: Sales Invoices, Sales Quotes, Sales Order Groups

---

## GET Endpoints

- `GET /SalesOrders` - List sales orders (paginated)
- `GET /SalesOrders/{guid}` - Get single order with all lines

### Filters
| Filter | Type | Description |
|--------|------|-------------|
| `customerCode` | string | Customer code prefix |
| `customerId` | GUID(s) | Comma-separated customer GUIDs |
| `orderNumber` | string (20) | Exact match (overrides other filters) |
| `orderStatus` | string | Comma-separated: Parked, Placed, Completed, Backordered, Deleted |
| `customOrderStatus` | string | Custom status filter |
| `startDate` | date | Orders dated after (YYYY-MM-DD) |
| `endDate` | date | Orders dated before |
| `completedAfter` | date | Completed after date |
| `completedBefore` | date | Completed before date |
| `modifiedSince` | datetime | Created/edited after (UTC) |
| `warehouseCode` | string | Filter by warehouse |
| `sourceId` | string | Filter by source ID |
| `serialBatch` | boolean | Include serial/batch numbers |

Default: Excludes "Deleted" status. Ordered by `LastModifiedOn` descending.

---

## POST Endpoints

- `POST /SalesOrders` - Create new sales order
- `POST /SalesOrders/{guid}` - Create with specific GUID
- `POST /SalesOrders/{guid}/Lines` - Add line to existing order
- `POST /SalesOrders/{guid}/Complete` - Mark order complete

---

## PUT Endpoints

- `PUT /SalesOrders/{guid}` - Update order (FULL OBJECT REQUIRED)
- `PUT /SalesOrders/{guid}/Lines/{lineGuid}` - Update specific line

WARNING: PUT replaces the entire object. See `patterns/full-object-updates.md`.

---

## DELETE Endpoints

- `DELETE /SalesOrders/{guid}` - Delete order
- `DELETE /SalesOrders/{guid}/Lines/{lineGuid}` - Delete line

---

## Key Fields

### Sales Order
| Field | Type | Length | Required (POST) |
|-------|------|--------|-----------------|
| `Guid` | GUID | - | Optional (auto-generated) |
| `OrderNumber` | string | 20 | Read-only |
| `OrderDate` | datetime | - | Required for PUT |
| `RequiredDate` | datetime | - | Optional (>2000-01-01) |
| `OrderStatus` | string | 20 | Required |
| `Customer` | object | - | Required (Guid or CustomerCode) |
| `Warehouse` | object | - | Required (Guid or WarehouseCode) |
| `Tax` | object | - | Required (TaxCode or TaxRate) |
| `Currency` | object | - | Optional (must match customer currency) |
| `Salesperson` | object | - | Optional (Guid required) |
| `ExchangeRate` | decimal | - | Required |
| `SubTotal` | decimal | - | Required |
| `TaxTotal` | decimal | - | Required |
| `Total` | decimal | - | Required |
| `Comments` | string | 2048 | Optional |
| `CustomerRef` | string | 500 | Optional |
| `DiscountRate` | decimal | - | Optional |
| `SalesOrderLines` | array | - | Required (min 1 line) |
| `DeliveryName` | string | 500 | Optional |
| `DeliveryStreetAddress` | string | 500 | Optional |
| `DeliveryCity` | string | 500 | Optional |
| `DeliveryRegion` | string | 500 | Optional |
| `DeliveryCountry` | string | 500 | Optional (ISO 3166) |
| `DeliveryPostCode` | string | 50 | Optional |

### Sales Order Line
| Field | Type | Length | Required |
|-------|------|--------|----------|
| `Guid` | GUID | - | Required for PUT |
| `LineNumber` | integer | - | Optional |
| `Product` | object | - | Required (Guid or ProductCode) |
| `OrderQuantity` | decimal | - | Required |
| `UnitPrice` | decimal | - | Required |
| `DiscountRate` | decimal | - | Optional |
| `LineTotal` | decimal | - | Calculated |
| `LineTax` | decimal | - | Calculated |
| `Comments` | string | 1024 | Optional |
| `LineType` | string | - | Optional ("Charge" or null) |
| `BatchNumbers` | array | - | If serialBatch=true |
| `SerialNumbers` | array | - | If serialBatch=true |

---

## POST/PUT Query Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `saveAddress` | false | Create/update customer address from delivery fields |
| `sendAccountingJournalOnly` | false | Send journal only to accounting system |
| `serialBatch` | false | Auto-assign serial/batch numbers |
| `taxInclusive` | false | Totals include tax (recalculated exclusive on save) |

---

## Common Use Cases

### 1. Fetch Recent Orders
```php
$response = $api->get('/SalesOrders', [
    'modifiedSince' => now()->subDay()->format('Y-m-d'),
    'orderStatus' => 'Completed',
    'pageSize' => 200,
]);
$orders = $response->json()['Items'];
```

### 2. Create Sales Order
```php
$api->post('/SalesOrders', [
    'OrderDate' => now()->format('Y-m-d'),
    'OrderStatus' => 'Placed',
    'Customer' => ['CustomerCode' => 'ACME'],
    'Warehouse' => ['WarehouseCode' => 'MAIN'],
    'Tax' => ['TaxCode' => 'V.A.T.', 'TaxRate' => 0.2],
    'ExchangeRate' => 1.0,
    'SubTotal' => 100.00,
    'TaxTotal' => 20.00,
    'Total' => 120.00,
    'SalesOrderLines' => [
        [
            'LineNumber' => 1,
            'Product' => ['ProductCode' => 'SKU-001'],
            'OrderQuantity' => 5.0,
            'UnitPrice' => 20.0,
        ],
    ],
]);
```

### 3. Update Order (Safe Pattern)
```php
$order = $api->get("/SalesOrders/{$guid}")->json();
$order['Comments'] = 'Updated via API';
$api->put("/SalesOrders/{$guid}", $order);
```

---

## Related Read-Only Resources

- `GET /SalesInvoices` - Invoices generated from completed orders
- `GET /SalesQuotes` - Sales quotes
- `GET /SalesOrderGroups` - Order groupings

---

## Important Notes

- OrderNumber is read-only, auto-generated (max 17 chars for POST, 3 reserved for suffix)
- Charge lines (`LineType="Charge"`) ignore quantity, discount, volume, weight, batch, serial
- Discounted unit price must be >= product minimum sell price
- Default ordering by `LastModifiedOn` descending
