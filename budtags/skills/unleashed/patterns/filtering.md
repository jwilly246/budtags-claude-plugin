# Unleashed API Filtering

Query string filters available per resource type.

---

## Common Filters (Most Resources)

| Filter | Type | Description |
|--------|------|-------------|
| `modifiedSince` | date (YYYY-MM-DD) | Records created/modified since date |
| `pageSize` | integer | Results per page (default 200) |
| `pageNumber` | integer | Page number (1-indexed) |
| `orderBy` | string | Sort column (varies per resource) |
| `sort` | string | `asc` or `desc` |

---

## Sales Orders Filters

| Filter | Type | Description |
|--------|------|-------------|
| `customerCode` | string | Customer code prefix match |
| `customerId` | GUID(s) | Comma-separated customer GUIDs |
| `orderNumber` | string | Exact order number (overrides other filters) |
| `orderStatus` | string | Comma-separated statuses (e.g., "Completed,Backordered") |
| `customOrderStatus` | string | Custom status filter |
| `startDate` | date | Orders dated after this |
| `endDate` | date | Orders dated before this |
| `completedAfter` | date | Orders completed after date |
| `completedBefore` | date | Orders completed before date |
| `warehouseCode` | string | Filter by warehouse |
| `sourceId` | string | Filter by source ID |
| `serialBatch` | boolean | Include serial/batch numbers in response |

---

## Products Filters

| Filter | Type | Description |
|--------|------|-------------|
| `productCode` | string | Code prefix match |
| `productDescription` | string | Description prefix match |
| `product` | string | Code OR description contains |
| `productGroup` | string | Exact group match |
| `productBrand` | string | Exact brand match |
| `ProductBarcode` | string | Exact barcode match |
| `productId` | GUID(s) | Comma-separated product GUIDs |
| `brief` | boolean | Abbreviated response (fewer fields) |
| `smart` | boolean | In-stock + recently in-stock |
| `includeObsolete` | boolean | Include obsolete products |
| `includeAttributes` | boolean | Include product attributes |
| `excludeAssembled` | boolean | Exclude assembled products |
| `excludeComponents` | boolean | Exclude component products |
| `customerCode` | string | Show customer-specific pricing |

---

## Customers Filters

| Filter | Type | Description |
|--------|------|-------------|
| `customerCode` | string | Code prefix match |
| `customerName` | string | Name prefix match |
| `customer` | string | Code OR name contains (case-sensitive) |
| `customerType` | string | Exact type match |
| `currency` | string | Exact currency code match |
| `sellPriceTier` | string | Exact tier match |
| `salesOrderGroup` | string | Exact group match |
| `contactEmail` | string | Contact email prefix match |
| `stopCredit` | boolean | Credit-stopped customers only |
| `includeObsolete` | boolean | Include obsolete customers |
| `includeAllContacts` | boolean | Return first 100 contacts |
| `xeroContactId` | string | Xero Contact ID prefix match |

---

## Stock On Hand Filters

| Filter | Type | Description |
|--------|------|-------------|
| `productId` | GUID(s) | Comma-separated product GUIDs |
| `warehouseCode` | string | Filter by warehouse code |
| `warehouseName` | string | Filter by warehouse name |
| `asAtDate` | date | Stock levels at specific date |
| `isAssembled` | boolean | Include auto-assembly quantities |

---

## Stock Adjustments Filters

| Filter | Type | Description |
|--------|------|-------------|
| `adjustmentDate` | date | Adjustments since date |
| `productCode` | string | Filter by product code |
| `warehouseCode` | string | Filter by warehouse code |

---

## Date Format

All date filters use ISO 8601: `YYYY-MM-DD`

```
/SalesOrders?startDate=2025-01-01&endDate=2025-03-31&modifiedSince=2025-03-01
```

---

## Combining Filters

Filters are combined with `&`:

```php
$response = $api->get('/SalesOrders', [
    'customerCode' => 'ACME',
    'orderStatus' => 'Completed',
    'startDate' => '2025-01-01',
    'pageSize' => 200,
]);
```
