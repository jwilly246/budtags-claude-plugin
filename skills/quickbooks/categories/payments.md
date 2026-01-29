# QuickBooks Payment Operations

**Category:** Payment Operations
**Operations:** 3 methods
**Purpose:** Record customer payments against invoices

---

## Overview

Payment operations record customer payments and link them to invoices, reducing outstanding balances.

**Key Concepts:**
- Payments linked to invoices
- Payment methods (Cash, Check, Credit Card, etc.)
- Deposit accounts for payment tracking

**See Also:**
- `scenarios/payment-workflow.md` - Complete payment guide
- `ENTITY_TYPES.md` - Payment and PaymentMethod types

---

## Operations

### 34. `get_payment_methods()`
Get all payment methods

**Returns:** Array of PaymentMethod objects

**Usage:**
```php
$methods = $qbo->get_payment_methods();
foreach ($methods as $method) {
    echo "{$method->Id}: {$method->Name}\n";
}
// Output: 1: Cash, 2: Check, 3: Credit Card, etc.
```

### 35. `get_deposit_accounts()`
Get all accounts that can receive deposits

**Returns:** Array of Account objects (type 'Bank' or 'Other Current Asset')

**Usage:**
```php
$accounts = $qbo->get_deposit_accounts();
foreach ($accounts as $account) {
    echo "{$account->Id}: {$account->Name}\n";
}
```

### 36. `create_payment(array $data)`
Record customer payment against invoice

**Required:**
- `customer_id` - QuickBooks customer ID
- `invoice_id` - QuickBooks invoice ID to apply payment to
- `amount` - Payment amount
- `txn_date` - Payment date
- `payment_method_id` - Payment method ID (from get_payment_methods())
- `deposit_account_id` - Deposit account ID (from get_deposit_accounts())

**Usage:**
```php
$payment = $qbo->create_payment([
    'customer_id' => '123',
    'invoice_id' => '789',
    'amount' => 250.00,
    'txn_date' => '2025-01-15',
    'payment_method_id' => '1',  // Cash
    'deposit_account_id' => '35' // Checking Account
]);

echo "Payment recorded: \${$payment->TotalAmt}";
```

**Returns:** Created Payment object

**Notes:**
- Payment reduces invoice balance
- Links payment to invoice automatically
- Can make partial payments
- Logs payment via LogService

---

## Common Workflows

### Record Full Payment on Invoice
```php
$invoice = $qbo->get_invoice('789');

$payment = $qbo->create_payment([
    'customer_id' => $invoice->CustomerRef,
    'invoice_id' => $invoice->Id,
    'amount' => $invoice->Balance,  // Pay full balance
    'txn_date' => date('Y-m-d'),
    'payment_method_id' => '1',     // Cash
    'deposit_account_id' => '35'    // Checking
]);
```

### Record Partial Payment
```php
$payment = $qbo->create_payment([
    'customer_id' => '123',
    'invoice_id' => '789',
    'amount' => 100.00,  // Partial payment
    'txn_date' => date('Y-m-d'),
    'payment_method_id' => '3',  // Credit Card
    'deposit_account_id' => '35'
]);
```

**See:** `scenarios/payment-workflow.md`
