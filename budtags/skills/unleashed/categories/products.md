# Products Category

**Total Endpoints**: 3
**Operations**: GET (list/single), POST (create/update), POST Obsolete
**Related Read-Only**: Product Brands, Product Groups, Product Prices, Sell Price Tiers, Attribute Sets

---

## GET Endpoints

- `GET /Products` - List products (paginated)
- `GET /Products/{guid}` - Get single product

### Filters
| Filter | Type | Description |
|--------|------|-------------|
| `productCode` | string | Code prefix match |
| `productDescription` | string | Description prefix match |
| `product` | string | Code OR description contains |
| `productGroup` | string | Exact group match (not subgroups) |
| `productBrand` | string | Exact brand match |
| `ProductBarcode` | string | Exact barcode match |
| `productId` | GUID(s) | Comma-separated product GUIDs |
| `customerCode` | string | Show customer-specific pricing |
| `brief` | boolean | Abbreviated response (fewer fields) |
| `smart` | boolean | In-stock + recently in-stock (6 months) |
| `includeObsolete` | boolean | Include obsolete products |
| `includeAttributes` | boolean | Include product attributes |
| `excludeAssembled` | boolean | Exclude assembled products |
| `excludeComponents` | boolean | Exclude component products |
| `modifiedSince` | date | YYYY-MM-DD |
| `orderBy` | string | `LastModifiedOn`, `CreatedOn`, `ProductCode` (default) |
| `sort` | string | `asc`, `desc` |

---

## POST Endpoints

- `POST /Products` - Create product
- `POST /Products/{guid}` - Create/update product
- `POST /Products/Obsolete/{guid}` - Mark product obsolete

Note: Products use POST for both create and update, not PUT.

---

## Key Fields

### Product
| Field | Type | Length | Required |
|-------|------|--------|----------|
| `ProductCode` | string | 100 | Required (set only on creation) |
| `ProductDescription` | string | 500 | Required |
| `UnitOfMeasure` | object | - | Required for updates (Guid or Name) |
| `DefaultPurchasePrice` | decimal | - | Optional |
| `DefaultSellPrice` | decimal | - | Optional |
| `MinimumSellPrice` | decimal | - | Optional (>= DefaultSellPrice) |
| `Barcode` | string | 200 | Optional |
| `PackSize` | decimal | - | Optional |
| `Width/Height/Depth/Weight` | decimal | - | Optional |
| `Notes` | string | 1024 | Optional |
| `Comments` | string | 1024 | Optional |
| `IsComponent` | boolean | - | Optional |
| `IsAssembledProduct` | boolean | - | Optional |
| `IsSerialized` | boolean | - | Optional (read-only after creation) |
| `IsBatchTracked` | boolean | - | Optional (read-only after creation) |
| `IsSellable` | boolean | - | Optional (default: true) |
| `IsPurchasable` | boolean | - | Optional (default: true) |
| `Obsolete` | boolean | - | Optional |
| `ProductGroup` | object | - | Optional (Guid or GroupName) |
| `ProductSubGroup` | object | - | Optional (must be child of ProductGroup) |
| `ProductBrand` | object | - | Optional (Guid or BrandName) |
| `Supplier` | object | - | Optional (Guid required) |

### Pricing Tiers
- `SellPriceTier1` through `SellPriceTier10` - Each contains `Name` (string) and `Value` (decimal)

### Stock Management
| Field | Type | Description |
|-------|------|-------------|
| `MinStockAlertLevel` | decimal | Low stock alert |
| `MaxStockAlertLevel` | decimal | High stock alert |
| `ReOrderPoint` | decimal | Reorder trigger |
| `MinimumOrderQuantity` | decimal | Min order qty |
| `MinimumSaleQuantity` | decimal | Min sale qty |
| `NeverDiminishing` | boolean | Never reduces stock |

### Response-Only Fields
| Field | Type | Description |
|-------|------|-------------|
| `LastCost` | decimal | Last purchase cost |
| `AverageLandPrice` | decimal | Average cost including freight |
| `NominalCost` | decimal | Standard cost |
| `InventoryDetails` | array | Per-warehouse stock details (requires Per Warehouse Controls) |
| `AlternateUnitsOfMeasure` | array | Alternate UoM with conversion rates |
| `Images` | array | Product images (Url, IsDefault) |

---

## Common Use Cases

### 1. Fetch Products by Group
```php
$response = $api->get('/Products', [
    'productGroup' => 'Cannabis',
    'includeObsolete' => 'false',
    'pageSize' => 200,
]);
$products = $response->json()['Items'];
```

### 2. Create Product
```php
$api->post('/Products', [
    'ProductCode' => 'CBD-OIL-30ML',
    'ProductDescription' => 'CBD Oil 30ml Tincture',
    'UnitOfMeasure' => ['Name' => 'Each'],
    'DefaultSellPrice' => 29.99,
    'DefaultPurchasePrice' => 12.00,
    'ProductGroup' => ['GroupName' => 'Tinctures'],
    'IsSellable' => true,
    'IsPurchasable' => true,
]);
```

### 3. Get Customer-Specific Pricing
```php
$response = $api->get('/Products', [
    'customerCode' => 'ACME',
    'productCode' => 'CBD',
]);
// Response includes CustomerSellPrice field
```

---

## Important Notes

- ProductCode set only on creation, cannot be updated
- Updates overwrite existing info; fields left blank are removed
- Exceptions: `MinimumOrderQuantity`, `MinimumSaleQuantity`, `MinimumSellPrice` - null/missing won't override
- `IsSerialized` and `IsBatchTracked` are read-only after creation
- `InventoryDetails` requires Per Warehouse Controls enabled
- Products use POST for updates (not PUT)
