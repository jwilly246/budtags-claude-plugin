# Credit Memo Workflow

Guide to creating credit memos and applying credits to invoices in QuickBooks.

---

## Creating Credit Memos

### Basic Credit Memo

```php
$qbo = new QuickBooksApi();
$qbo->set_user($user);

$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 2,
            'unit_price' => 25.00,
            'description' => 'Return - damaged product'
        ]
    ]
]);

echo "Credit memo #{$creditMemo->DocNumber} created: \${$creditMemo->TotalAmt}";
```

### Complete Credit Memo with Options

```php
$creditMemo = $qbo->create_credit_memo([
    // Required
    'customer_id' => '123',
    'line_items' => [/* ... */],

    // Optional
    'txn_date' => '2025-01-15',
    'customer_memo' => 'Refund for damaged items',
    'private_note' => 'Customer reported product quality issue',
]);
```

---

## Checking Available Credits

### Get Customer's Available Credits

```php
$availableCredit = $qbo->get_customer_available_credits('123');

echo "Customer has \${$availableCredit} in available credits";
```

### Get Customer's Credit Memos

```php
$creditMemos = $qbo->get_customer_credit_memos('123');

foreach ($creditMemos as $memo) {
    echo "Credit #{$memo->DocNumber}\n";
    echo "  Total: \${$memo->TotalAmt}\n";
    echo "  Balance: \${$memo->Balance}\n";
    echo "  Available: \${$memo->Balance}\n\n";
}
```

---

## Applying Credits to Invoices

### Apply Credit to Specific Invoice

```php
$payment = $qbo->apply_credit_to_invoice([
    'customer_id' => '123',
    'credit_memo_id' => '456',
    'invoice_id' => '789',
    'amount' => 50.00
]);

echo "Applied \${$payment->TotalAmt} credit to invoice";
```

**What Happens:**
1. QuickBooks creates a Payment object
2. Links payment to customer, invoice, and credit memo
3. Reduces invoice balance by credit amount
4. Reduces credit memo balance by applied amount

---

## Credit Scenarios

### Scenario 1: Full Refund for Invoice

```php
// Customer returns entire order
$invoice = $qbo->get_invoice('789');

// Create credit memo matching invoice
$creditMemo = $qbo->create_credit_memo([
    'customer_id' => $invoice->CustomerRef->value,
    'customer_memo' => "Full refund for Invoice #{$invoice->DocNumber}",
    'line_items' => [
        // Copy line items from invoice
        [
            'item_id' => '456',
            'quantity' => 10,
            'unit_price' => 25.00
        ]
    ]
]);

// Apply credit to original invoice
$qbo->apply_credit_to_invoice([
    'customer_id' => $invoice->CustomerRef->value,
    'credit_memo_id' => $creditMemo->Id,
    'invoice_id' => '789',
    'amount' => $creditMemo->TotalAmt
]);

// Invoice now has $0 balance
```

### Scenario 2: Partial Product Return

```php
// Customer returns 2 out of 10 units
$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'customer_memo' => 'Partial return - 2 units damaged',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 2,  // Only returned quantity
            'unit_price' => 25.00
        ]
    ]
]);
// Credit: $50.00

// Apply to invoice
$qbo->apply_credit_to_invoice([
    'customer_id' => '123',
    'credit_memo_id' => $creditMemo->Id,
    'invoice_id' => '789',
    'amount' => 50.00
]);
```

### Scenario 3: Store Credit (Not Applied to Invoice)

```php
// Create credit memo without applying it
$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'customer_memo' => 'Store credit for future purchases',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 1,
            'unit_price' => 100.00
        ]
    ]
]);

// Don't apply to any invoice - credit stays on customer account
// Customer can use it on future invoices
```

### Scenario 4: Apply Credit to Multiple Invoices

```php
$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'line_items' => [/* $200 credit */]
]);

// Apply $100 to invoice 1
$qbo->apply_credit_to_invoice([
    'customer_id' => '123',
    'credit_memo_id' => $creditMemo->Id,
    'invoice_id' => '789',
    'amount' => 100.00
]);

// Apply remaining $100 to invoice 2
$qbo->apply_credit_to_invoice([
    'customer_id' => '123',
    'credit_memo_id' => $creditMemo->Id,
    'invoice_id' => '790',
    'amount' => 100.00
]);
```

---

## Common Patterns

### Pattern 1: Automatic Credit Application

```php
// Get customer's unpaid invoices
$invoices = $qbo->get_customer_invoices('123');
$unpaidInvoices = array_filter($invoices, fn($inv) => $inv->Balance > 0);

// Get available credits
$availableCredit = $qbo->get_customer_available_credits('123');

if ($availableCredit > 0 && count($unpaidInvoices) > 0) {
    // Apply credits to oldest invoice first
    $oldestInvoice = $unpaidInvoices[0];

    $applyAmount = min($availableCredit, $oldestInvoice->Balance);

    $creditMemos = $qbo->get_customer_credit_memos('123');
    $unappliedMemo = array_filter($creditMemos, fn($cm) => $cm->Balance > 0)[0];

    $qbo->apply_credit_to_invoice([
        'customer_id' => '123',
        'credit_memo_id' => $unappliedMemo->Id,
        'invoice_id' => $oldestInvoice->Id,
        'amount' => $applyAmount
    ]);
}
```

---

## Frontend Integration

### ApplyCreditModal Component

**Location:** `resources/js/Pages/Quickbooks/Modals/ApplyCreditModal.tsx`

**Features:**
- Shows available credit memos for customer
- Displays credit balances
- Shows invoices with balances due
- Calculates maximum applicable amount
- Real-time balance updates

---

## Troubleshooting

### Error: "Insufficient credit balance"

**Cause:** Trying to apply more credit than available

**Solution:**
```php
$creditMemo = $qbo->get_credit_memo($creditMemoId);
$maxApplicable = $creditMemo->Balance;

if ($amount > $maxApplicable) {
    throw new \Exception("Only \${$maxApplicable} available on this credit memo");
}
```

---

## Next Steps

- **[INVOICE_WORKFLOW.md](INVOICE_WORKFLOW.md)** - Create invoices
- **[PAYMENT_WORKFLOW.md](PAYMENT_WORKFLOW.md)** - Record payments
