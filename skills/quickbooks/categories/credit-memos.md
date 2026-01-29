# QuickBooks Credit Memo Operations

**Category:** Credit Memo Operations
**Operations:** 5 methods
**Purpose:** Create and apply credit memos (customer credits/refunds)

---

## Overview

Credit memo operations handle customer credits and refunds. Credit memos can be applied to specific invoices to reduce amounts owed.

**Key Concepts:**
- Line items similar to invoices
- Can apply to specific invoices
- Reduces customer balance

**See Also:**
- `scenarios/credit-memo-workflow.md` - Complete credit memo guide
- `ENTITY_TYPES.md` - CreditMemo type definition

---

## Operations

### 29. `get_all_credit_memos()`
Get ALL credit memos with automatic pagination

**Returns:** Array of CreditMemo objects

### 30. `get_credit_memo(string $id)`
Get single credit memo by QuickBooks ID

**Returns:** CreditMemo object or `null`

### 31. `create_credit_memo(array $data)`
Create new credit memo

**Required:**
- `customer_id` - QuickBooks customer ID
- `line_items` - Array of line item objects

**Line Item Structure:**
```php
[
    'item_id' => '456',
    'quantity' => 2,
    'unit_price' => 25.00,
    'description' => 'Refund for damaged product'
]
```

**Usage:**
```php
$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'txn_date' => '2025-01-15',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 2,
            'unit_price' => 25.00
        ]
    ],
    'customer_memo' => 'Credit for damaged goods'
]);
```

**Returns:** Created CreditMemo object

### 32. `apply_credit_to_invoice(string $credit_memo_id, string $invoice_id, float $amount)`
Apply credit memo to specific invoice

**Parameters:**
- `credit_memo_id` - QuickBooks credit memo ID
- `invoice_id` - QuickBooks invoice ID to apply credit to
- `amount` - Amount to apply

**Usage:**
```php
$qbo->apply_credit_to_invoice('CM-123', 'INV-789', 50.00);
// Applies $50 credit to invoice, reducing balance
```

**Notes:**
- Credit reduces invoice balance
- Can apply partial credit amounts
- Logs application via LogService

### 33. `get_customer_available_credits(string $customer_id)`
Calculate total available credit balance for customer

**Returns:** Float (total available credit amount)

**Usage:**
```php
$availableCredit = $qbo->get_customer_available_credits('123');
echo "Customer has \${$availableCredit} in credits";
```

---

## Common Workflows

### Issue Credit for Returned Goods
```php
// Create credit memo
$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'line_items' => [
        ['item_id' => '456', 'quantity' => 5, 'unit_price' => 20.00]
    ],
    'customer_memo' => 'Return credit'
]);

// Apply to open invoice
$qbo->apply_credit_to_invoice($creditMemo->Id, $invoiceId, 100.00);
```

### Check Customer Credit Balance
```php
$credits = $qbo->get_customer_credit_memos('123');
$availableCredit = $qbo->get_customer_available_credits('123');

echo "Total credit memos: " . count($credits) . "\n";
echo "Available credit: \${$availableCredit}";
```

**See:** `scenarios/credit-memo-workflow.md`
