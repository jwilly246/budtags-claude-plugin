# QuickBooks Payment Operations

**Category:** Payment Operations
**Operations:** 6 methods
**Purpose:** Record customer payments and read payment methods / deposit accounts

---

## Overview

Payment operations record customer payments against invoices and provide the
supporting reference reads (payment methods, deposit accounts). A payment links
to exactly one invoice via a `LinkedTxn`.

**See Also:**
- `scenarios/payment-workflow.md` - Complete payment guide
- `ENTITY_TYPES.md` - Payment and PaymentMethod types

---

## Operations

### 1. `get_payment_methods(): Collection`

Active payment methods (`WHERE Active = true`). Takes no pagination args.

```php
foreach ($qbo->get_payment_methods() as $m) {
    echo "{$m->Id}: {$m->Name}\n";
}
```

### 2. `get_payment_methods_cached(string $org_id): Collection`

Cached `get_payment_methods` (`qbo:payment_methods:{org_id}`). Backs
`GET /quickbooks/payment-methods`.

### 3. `get_payment_method(string $id): ?object`

Single payment method by ID (`FindById`), or `null`. Used to validate a chosen
method before recording a payment.

### 4. `get_deposit_accounts(): Collection`

Accounts that can receive deposits: filters all accounts to
`AccountType === 'Bank'` and active.

### 5. `get_deposit_accounts_cached(string $org_id): Collection`

Cached `get_deposit_accounts` (`qbo:deposit_accounts:{org_id}`). Backs
`GET /quickbooks/deposit-accounts`.

### 6. `create_payment(array $payment_data): IPPPayment`

Record a payment linked to an invoice. Logs on success/failure via `LogService`.

**Required keys:** `invoice_id`, `customer_id`, `amount`, `txn_date`.
**Optional keys:** `payment_method_id` (-> `PaymentMethodRef`), `payment_ref_num`
(check/transaction #), `deposit_to_account_id` (-> `DepositToAccountRef`).

```php
$payment = $qbo->create_payment([
    'invoice_id' => '789',
    'customer_id' => '123',
    'amount' => 250.00,
    'txn_date' => '2026-01-15',
    'payment_method_id' => '1',
    'deposit_to_account_id' => '35',
]);
```

**Note:** the deposit key is `deposit_to_account_id` (not `deposit_account_id`).

---

## Common Workflows

### Record a Full Payment
```php
$invoice = $qbo->get_invoice('789');
$customerId = is_object($invoice->CustomerRef)
    ? $invoice->CustomerRef->value
    : $invoice->CustomerRef;

$qbo->create_payment([
    'invoice_id' => $invoice->Id,
    'customer_id' => $customerId,
    'amount' => (float) $invoice->Balance,
    'txn_date' => date('Y-m-d'),
]);
```

### Record a Partial Payment with Method + Deposit
```php
$qbo->create_payment([
    'invoice_id' => '789',
    'customer_id' => '123',
    'amount' => 100.00,
    'txn_date' => date('Y-m-d'),
    'payment_method_id' => '3',
    'deposit_to_account_id' => '35',
]);
```

**See:** `scenarios/payment-workflow.md`
