# Payment Workflow

Guide to recording payments against QuickBooks invoices in BudTags.

---

## Creating Payments

### Basic Payment

**Method:** `create_payment(array $payment_data): IPPPayment`

**Required keys:** `invoice_id`, `customer_id`, `amount`, `txn_date`.

```php
$qbo = new QuickBooksApi();
$qbo->set_service($user);

$payment = $qbo->create_payment([
    'customer_id' => '123',
    'invoice_id' => '789',
    'amount' => 250.00,
    'txn_date' => '2025-01-15'
]);

echo "Payment recorded: \${$payment->TotalAmt}";
```

### Complete Payment with All Options

```php
$payment = $qbo->create_payment([
    // Required
    'customer_id' => '123',
    'invoice_id' => '789',
    'amount' => 250.00,
    'txn_date' => '2025-01-15',         // Payment date (required)

    // Optional
    'payment_method_id' => '1',         // Payment method (Cash, Check, Card, etc.)
    'payment_ref_num' => 'CHK-1042',    // Check / transaction reference number
    'deposit_to_account_id' => '35',    // Bank account to deposit to
]);
```

**Note:** `create_payment` does not accept a `private_note` key. The supported
optional keys are `payment_method_id`, `payment_ref_num`, and
`deposit_to_account_id`.

---

## Payment Methods

### Get Available Payment Methods

```php
$methods = $qbo->get_payment_methods();

foreach ($methods as $method) {
    echo "ID: {$method->Id}, Name: {$method->Name}\n";
}
// Output:
// ID: 1, Name: Cash
// ID: 2, Name: Check
// ID: 3, Name: Credit Card
// ID: 4, Name: Debit Card
```

### Common Payment Methods

- **Cash** - Cash payments
- **Check** - Check payments
- **Credit Card** - Credit card payments
- **Debit Card** - Debit card payments
- **ACH** - Bank transfers
- **Other** - Other payment types

---

## Deposit Accounts

### Get Bank Accounts for Deposits

```php
$accounts = $qbo->get_deposit_accounts();

foreach ($accounts as $account) {
    echo "ID: {$account->Id}, Name: {$account->Name}\n";
}
// Output:
// ID: 35, Name: Checking Account
// ID: 36, Name: Savings Account
// ID: 37, Name: Merchant Account
```

---

## Payment Scenarios

### Scenario 1: Full Payment

```php
$invoice = $qbo->get_invoice('789');
$totalDue = $invoice->Balance;

$payment = $qbo->create_payment([
    'customer_id' => $invoice->CustomerRef->value,
    'invoice_id' => '789',
    'amount' => $totalDue,  // Pay full balance
    'txn_date' => date('Y-m-d'),
    'payment_method_id' => '1',  // Cash
    'deposit_to_account_id' => '35'  // Checking
]);

// Invoice balance now = $0.00
```

### Scenario 2: Partial Payment

```php
$invoice = $qbo->get_invoice('789');
// Balance: $500.00

$payment = $qbo->create_payment([
    'customer_id' => $invoice->CustomerRef->value,
    'invoice_id' => '789',
    'amount' => 250.00,  // Partial payment
    'txn_date' => date('Y-m-d'),
    'payment_method_id' => '1'
]);

// Invoice balance now = $250.00
// Can make additional payments later
```

### Scenario 3: Multiple Payments on One Invoice

```php
// First payment
$payment1 = $qbo->create_payment([
    'customer_id' => '123',
    'invoice_id' => '789',
    'amount' => 100.00,
    'txn_date' => '2025-01-15',
    'payment_method_id' => '1'  // Cash
]);

// Second payment (later date)
$payment2 = $qbo->create_payment([
    'customer_id' => '123',
    'invoice_id' => '789',
    'amount' => 150.00,
    'txn_date' => '2025-01-20',
    'payment_method_id' => '3'  // Credit Card
]);

// Invoice balance reduced by $250 total
```

---

## Common Patterns

### Pattern 1: Record Payment from Order

```php
$order = Order::find($orderId);

$payment = $qbo->create_payment([
    'customer_id' => $order->qbo_customer_id,
    'invoice_id' => $order->qbo_invoice_id,
    'amount' => $order->payment_amount,
    'txn_date' => $order->payment_date,
    'payment_method_id' => $order->qbo_payment_method_id,
    'payment_ref_num' => "ORDER-{$order->id}",
    'deposit_to_account_id' => $order->qbo_deposit_account_id
]);

$order->update(['qbo_payment_id' => $payment->Id]);

LogService::store(
    'Payment Recorded',
    "Order #{$order->id} → QBO Payment #{$payment->Id}"
);
```

### Pattern 2: Auto-Receive Payment on Invoice Creation

```php
// Create invoice
$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'line_items' => [/* ... */]
]);

// Immediately record payment (COD scenario)
$payment = $qbo->create_payment([
    'customer_id' => '123',
    'invoice_id' => $invoice->Id,
    'amount' => $invoice->TotalAmt,  // Pay in full
    'txn_date' => date('Y-m-d'),
    'payment_method_id' => '1',  // Cash
    'payment_ref_num' => 'COD'
]);

LogService::store('COD Payment', "Invoice #{$invoice->DocNumber} paid in full");
```

---

## Validation

### Check Invoice Balance Before Payment

```php
$invoice = $qbo->get_invoice($invoiceId);

if ($invoice->Balance <= 0) {
    throw new \Exception("Invoice is already paid in full");
}

if ($paymentAmount > $invoice->Balance) {
    throw new \Exception("Payment amount exceeds invoice balance");
}
```

### Controller Validation Example

```php
// The real endpoint is QuickBooksController::record_payment($api, $invoice_id):
// the invoice id is a route parameter and input is validated in camelCase.
public function record_payment(QuickBooksApi $api, string $invoice_id): RedirectResponse
{
    $api->set_service($this->user());

    $input = request()->validate([
        'customerId' => 'required|string',
        'amount' => 'required|numeric|min:0.01',
        'txnDate' => 'required|date',
        'paymentMethodId' => 'nullable|string',
        'paymentRefNum' => 'nullable|string|max:21',
        'depositToAccountId' => 'nullable|string',
    ]);

    // Verify invoice balance
    $invoice = $api->get_invoice($invoice_id);
    if ($input['amount'] > (float) $invoice->Balance) {
        return redirect()->back()->with('error', 'Payment exceeds invoice balance');
    }

    $api->create_payment([
        'invoice_id' => $invoice_id,
        'customer_id' => $input['customerId'],
        'amount' => (float) $input['amount'],
        'txn_date' => $input['txnDate'],
        'payment_method_id' => $input['paymentMethodId'] ?? null,
        'payment_ref_num' => $input['paymentRefNum'] ?? null,
        'deposit_to_account_id' => $input['depositToAccountId'] ?? null,
    ]);

    return redirect()->back()->with('message', 'Payment recorded');
}
```

---

## Troubleshooting

### Error: "Invalid Invoice Reference"

**Solution:** Verify invoice exists and is not deleted

```php
$invoice = $qbo->get_invoice($invoiceId);
if (!$invoice) {
    throw new \Exception("Invoice not found");
}
```

### Error: "Payment exceeds balance"

**Solution:** Check current invoice balance

```php
$invoice = $qbo->get_invoice($invoiceId);
$maxPayment = $invoice->Balance;
```

---

## Next Steps

- **[CREDIT_MEMO_WORKFLOW.md](CREDIT_MEMO_WORKFLOW.md)** - Issue credits and apply to invoices
- **[INVOICE_WORKFLOW.md](INVOICE_WORKFLOW.md)** - Create invoices
