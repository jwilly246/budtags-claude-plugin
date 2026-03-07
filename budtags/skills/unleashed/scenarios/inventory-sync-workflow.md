# Inventory Sync Workflow

Sync stock on hand and product data between Unleashed and BudTags, keeping inventory levels aligned with Metrc values.

---

## Goal
Fetch product inventory from Unleashed Stock On Hand endpoint and sync with BudTags product records.

## Prerequisites
- Unleashed API credentials configured
- Product mappings between Unleashed and BudTags/Metrc
- Warehouse mapping established

## Complexity
Medium - pagination, multi-warehouse, reconciliation

---

## Workflow Overview

```
1. Fetch products from Unleashed (incremental)
2. Fetch stock on hand levels
3. Compare with local inventory records
4. Update discrepancies
5. Log changes for audit trail
```

---

## Step 1: Fetch Products

```php
public function sync_products(): void
{
    $org = request()->user()->active_org->model()->get();
    $last_sync = $org->unleashed_product_sync ?? now()->subDays(30);

    $page = 1;
    $all_products = [];

    do {
        $response = $this->api->get('/Products', [
            'modifiedSince' => $last_sync->format('Y-m-d'),
            'includeObsolete' => 'false',
            'pageSize' => 200,
            'pageNumber' => $page,
        ]);

        $data = $response->json();
        $all_products = array_merge($all_products, $data['Items']);
        $total_pages = $data['Pagination']['NumberOfPages'];
        $page++;
    } while ($page <= $total_pages);

    foreach ($all_products as $product) {
        $this->upsert_product($product, $org);
    }

    $org->update(['unleashed_product_sync' => now()]);
}
```

---

## Step 2: Fetch Stock On Hand

```php
public function sync_stock_levels(): void
{
    $org = request()->user()->active_org->model()->get();
    $page = 1;
    $all_stock = [];

    do {
        $response = $this->api->get('/StockOnHand', [
            'warehouseCode' => $org->default_warehouse_code,
            'pageSize' => 500,
            'pageNumber' => $page,
        ]);

        $data = $response->json();
        $all_stock = array_merge($all_stock, $data['Items']);
        $total_pages = $data['Pagination']['NumberOfPages'];
        $page++;
    } while ($page <= $total_pages);

    foreach ($all_stock as $stock) {
        $this->update_stock_level($stock, $org);
    }
}
```

---

## Step 3: Update Local Records

```php
private function update_stock_level(array $stock, Organization $org): void
{
    $product = UnleashedProduct::where([
        'organization_id' => $org->id,
        'unleashed_guid' => $stock['ProductGuid'],
    ])->first();

    if (! $product) {
        return;
    }

    $changed = $product->qty_on_hand !== (float) $stock['QtyOnHand'];

    $product->update([
        'qty_on_hand' => $stock['QtyOnHand'],
        'allocated_qty' => $stock['AllocatedQty'],
        'available_qty' => $stock['AvailableQty'],
        'on_purchase' => $stock['OnPurchase'],
        'avg_cost' => $stock['AvgCost'],
        'total_cost' => $stock['TotalCost'],
    ]);

    if ($changed) {
        LogService::store(
            type: 'unleashed_stock_change',
            message: "Stock updated for {$product->product_code}: {$stock['QtyOnHand']}",
        );
    }
}
```

---

## Step 4: Multi-Warehouse Stock Check

```php
public function check_all_warehouses(string $product_guid): array
{
    $response = $this->api->get("/StockOnHand/{$product_guid}/AllWarehouses");
    return $response->json();
}
```

---

## Common Issues

### 1. Zero-Transaction Products Missing
**Problem**: Products without any transactions don't appear in Stock On Hand
**Solution**: Cross-reference with Products endpoint; treat missing as zero stock

### 2. Stale Data
**Problem**: Stock levels don't reflect recent changes
**Solution**: Use `modifiedSince` filter and sync frequently

### 3. Multi-Warehouse Complexity
**Problem**: Same product has different stock in different warehouses
**Solution**: Use `warehouseCode` filter or `AllWarehouses` endpoint per product

---

## Related Resources

- `categories/stock.md` - Stock On Hand and Adjustments endpoints
- `categories/products.md` - Product endpoint details
- `patterns/pagination.md` - Iteration patterns
