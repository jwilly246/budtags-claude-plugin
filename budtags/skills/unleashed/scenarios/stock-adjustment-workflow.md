# Stock Adjustment Workflow

Record stock adjustments in Unleashed, comparable to Metrc package adjustments.

---

## Goal
Create stock adjustments in Unleashed to reconcile inventory discrepancies found during Metrc/BudTags sync.

## Prerequisites
- Unleashed API credentials configured
- Product GUID mappings
- Warehouse GUID or code known
- Valid adjustment reason

## Complexity
Low-Medium - straightforward POST, but requires correct field values

---

## Workflow Overview

```
1. Identify discrepancy (BudTags/Metrc vs Unleashed)
2. Look up product and warehouse identifiers
3. Build adjustment payload
4. POST stock adjustment
5. Log the adjustment
```

---

## Step 1: Build and Submit Adjustment

```php
public function create_adjustment(
    string $product_code,
    float $new_quantity,
    float $new_value,
    string $reason,
    string $warehouse_code = 'MAIN'
): array {
    $org = request()->user()->active_org->model()->get();

    $response = $this->api->post('/StockAdjustments', [
        'AdjustmentReason' => $reason,
        'AdjustmentDate' => now()->format('Y-m-d'),
        'Status' => 'Completed',
        'Warehouse' => ['WarehouseCode' => $warehouse_code],
        'StockAdjustmentLines' => [
            [
                'Product' => ['ProductCode' => $product_code],
                'NewQuantity' => $new_quantity,
                'NewActualValue' => $new_value,
                'Comments' => "Adjusted via BudTags sync - {$reason}",
            ],
        ],
    ]);

    $result = $response->json();

    LogService::store(
        type: 'unleashed_stock_adjustment',
        message: "Stock adjusted for {$product_code}: qty={$new_quantity}, reason={$reason}",
        data: ['response' => $result],
    );

    return $result;
}
```

---

## Step 2: Batch Adjustments

For multiple products in one adjustment:

```php
public function batch_adjustment(array $adjustments, string $reason): array
{
    $lines = [];
    foreach ($adjustments as $i => $adj) {
        $lines[] = [
            'LineNumber' => $i + 1,
            'Product' => ['ProductCode' => $adj['product_code']],
            'NewQuantity' => $adj['new_quantity'],
            'NewActualValue' => $adj['new_value'],
            'Comments' => $adj['comment'] ?? '',
        ];
    }

    return $this->api->post('/StockAdjustments', [
        'AdjustmentReason' => $reason,
        'AdjustmentDate' => now()->format('Y-m-d'),
        'Status' => 'Completed',
        'Warehouse' => ['WarehouseCode' => 'MAIN'],
        'StockAdjustmentLines' => $lines,
    ])->json();
}
```

---

## Step 3: With Serial/Batch Numbers

Serial and batch numbers can only be assigned to completed adjustments:

```php
$this->api->post('/StockAdjustments', [
    'AdjustmentReason' => 'Count',
    'Status' => 'Completed',
    'Warehouse' => ['WarehouseCode' => 'MAIN'],
    'StockAdjustmentLines' => [
        [
            'Product' => ['ProductCode' => 'SERIALIZED-ITEM'],
            'NewQuantity' => 5,
            'NewActualValue' => 250.00,
            'SerialNumbers' => [
                ['Identifier' => 'SN-001'],
                ['Identifier' => 'SN-002'],
            ],
        ],
    ],
]);
```

---

## Common Issues

### 1. Invalid Adjustment Reason
**Problem**: Reason doesn't match valid values
**Solution**: Check valid reasons in Unleashed settings

### 2. Product Not Found
**Problem**: ProductCode doesn't exist in Unleashed
**Solution**: Sync products first, verify code mapping

### 3. Completed vs Parked
**Problem**: Serial/batch numbers rejected
**Solution**: Must set Status to "Completed" for serial/batch assignment

---

## Related Resources

- `categories/stock.md` - Stock Adjustment endpoint details
- `patterns/authentication.md` - API setup
