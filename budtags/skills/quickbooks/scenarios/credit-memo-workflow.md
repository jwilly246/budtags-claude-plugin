# Credit Memo Workflow

Guide to creating credit memos and applying credits to invoices in QuickBooks.

---

## Creating Credit Memos

### Basic Credit Memo

```php
$qbo = new QuickBooksApi();
$qbo->set_service($user);

$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 2,
            'unit_price' => 25.00,
            'amount' => 50.00,
            'description' => 'Return - damaged product'
        ]
    ]
]);

echo "Credit memo #{$creditMemo->DocNumber} created: \${$creditMemo->TotalAmt}";
```

`create_credit_memo` returns a plain `object` (no typed SDK class). Each line
requires `item_id`, `quantity`, `unit_price`, and `amount`; `description` is
optional.

### Complete Credit Memo with Options

```php
$creditMemo = $qbo->create_credit_memo([
    // Required
    'customer_id' => '123',
    'line_items' => [/* ... */],

    // Optional
    'txn_date' => '2025-01-15',
    'doc_number' => 'CM-1001',
    'customer_email' => 'billing@example.com',  // mapped to BillEmail
    'private_note' => 'Customer reported product quality issue',
]);
```

**Supported optional keys:** `txn_date`, `doc_number`, `customer_email` (mapped to
`BillEmail`), `private_note`. There is no `customer_memo` key.

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

**Method:** `apply_credit_to_invoice(string $credit_memo_id, string $invoice_id, float $amount, string $customer_id): object`

All four arguments are positional and required.

```php
$payment = $qbo->apply_credit_to_invoice('456', '789', 50.00, '123');

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
    'private_note' => "Full refund for Invoice #{$invoice->DocNumber}",
    'line_items' => [
        // Copy line items from invoice
        [
            'item_id' => '456',
            'quantity' => 10,
            'unit_price' => 25.00,
            'amount' => 250.00
        ]
    ]
]);

// Apply credit to original invoice
// apply_credit_to_invoice(credit_memo_id, invoice_id, amount, customer_id)
$qbo->apply_credit_to_invoice(
    $creditMemo->Id,
    '789',
    $creditMemo->TotalAmt,
    $invoice->CustomerRef->value
);

// Invoice now has $0 balance
```

### Scenario 2: Partial Product Return

```php
// Customer returns 2 out of 10 units
$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'private_note' => 'Partial return - 2 units damaged',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 2,  // Only returned quantity
            'unit_price' => 25.00,
            'amount' => 50.00
        ]
    ]
]);
// Credit: $50.00

// Apply to invoice
$qbo->apply_credit_to_invoice($creditMemo->Id, '789', 50.00, '123');
```

### Scenario 3: Store Credit (Not Applied to Invoice)

```php
// Create credit memo without applying it
$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'private_note' => 'Store credit for future purchases',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 1,
            'unit_price' => 100.00,
            'amount' => 100.00
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
$qbo->apply_credit_to_invoice($creditMemo->Id, '789', 100.00, '123');

// Apply remaining $100 to invoice 2
$qbo->apply_credit_to_invoice($creditMemo->Id, '790', 100.00, '123');
```

---

## Common Patterns

### Pattern 1: Automatic Credit Application

```php
// Get customer's unpaid invoices (get_customer_invoices returns a Collection)
$unpaidInvoices = $qbo->get_customer_invoices('123')
    ->filter(fn ($inv) => $inv->Balance > 0)
    ->values();

// Get available credits
$availableCredit = $qbo->get_customer_available_credits('123');

if ($availableCredit > 0 && $unpaidInvoices->isNotEmpty()) {
    // Apply credits to oldest invoice first
    $oldestInvoice = $unpaidInvoices->first();

    $applyAmount = min($availableCredit, $oldestInvoice->Balance);

    $creditMemos = $qbo->get_customer_credit_memos('123');  // Collection
    $unappliedMemo = $creditMemos->first(fn ($cm) => $cm->Balance > 0);

    $qbo->apply_credit_to_invoice(
        $unappliedMemo->Id,
        $oldestInvoice->Id,
        $applyAmount,
        '123'
    );
}
```

---

## Frontend Integration

### ApplyCreditModal Component

**Location:** `resources/js/Components/ApplyCreditModal.tsx`

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

**Solution:** There is no single-credit-memo getter. Fetch the customer's credit
memos (or the cached org list) and locate the one you need.

```php
// Filter the customer's credit memos to the target memo
$creditMemo = $qbo->get_customer_credit_memos($customerId)
    ->firstWhere('Id', $creditMemoId);

// Or, from the cached org-wide list:
// $creditMemo = $qbo->get_credit_memos_cached($orgId)->firstWhere('Id', $creditMemoId);

$maxApplicable = (float) $creditMemo->Balance;

if ($amount > $maxApplicable) {
    throw new \Exception("Only \${$maxApplicable} available on this credit memo");
}
```

---

## Next Steps

- **[INVOICE_WORKFLOW.md](INVOICE_WORKFLOW.md)** - Create invoices
- **[PAYMENT_WORKFLOW.md](PAYMENT_WORKFLOW.md)** - Record payments
