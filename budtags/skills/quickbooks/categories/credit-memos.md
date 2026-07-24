# QuickBooks Credit Memo Operations

**Category:** Credit Memo Operations
**Operations:** 6 methods
**Purpose:** Read, create, and apply credit memos (customer credits/refunds)

---

## Overview

Credit memo operations read credit memos, create them, and apply them to
invoices. Applying a credit is done by creating a zero-total Payment that links
the credit memo and the invoice. There is no single-credit-memo getter.

**See Also:**
- `scenarios/credit-memo-workflow.md` - Complete credit memo guide
- `ENTITY_TYPES.md` - CreditMemo type definition

---

## Operations

### 1. `get_credit_memos(int $start_at = 1, int $max_count = 100): Collection`

Paginated credit memos (`SELECT * FROM CreditMemo`). Logs and returns empty on
error.

### 2. `get_credit_memos_cached(string $org_id): Collection`

Cached `get_credit_memos` for an org (`qbo:credit_memos:{org_id}`). Backs
`GET /quickbooks/credit-memos`.

### 3. `get_customer_credit_memos(string $customer_id, int $start_at = 1, int $max_count = 100): Collection`

Credit memos for one customer (`WHERE CustomerRef = '...'`).

### 4. `create_credit_memo(array $credit_memo_data): object`

Create a credit memo. Same shape as `create_invoice`. Returns the created QB
CreditMemo (no typed SDK class - plain `object`).

**Required:** `customer_id`, `line_items` (each `item_id`, `quantity`,
`unit_price`, `amount`; `description` optional). Lines with a falsy `item_id`
are skipped.
**Optional:** `txn_date`, `doc_number`, `customer_email` (-> `BillEmail`),
`private_note`.

```php
$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'txn_date' => '2026-01-15',
    'line_items' => [
        ['item_id' => '456', 'quantity' => 2, 'unit_price' => 25.00, 'amount' => 50.00],
    ],
    'private_note' => 'Credit for damaged goods',
]);
```

### 5. `apply_credit_to_invoice(string $credit_memo_id, string $invoice_id, float $amount, string $customer_id): object`

Apply a credit memo to an invoice by creating a linking Payment (TotalAmt 0). All
four arguments are required. Returns the created Payment `object`.

```php
$qbo->apply_credit_to_invoice('CM-123', 'INV-789', 50.00, '123');
```

### 6. `get_customer_available_credits(string $customer_id): float`

Total available credit for a customer: sums `RemainingCredit` (falling back to
`Balance`) across their credit memos. Returns `0` on error.

```php
$available = $qbo->get_customer_available_credits('123');
```

---

## Common Workflows

### Issue Credit and Apply to an Invoice
```php
$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'line_items' => [
        ['item_id' => '456', 'quantity' => 5, 'unit_price' => 20.00, 'amount' => 100.00],
    ],
    'private_note' => 'Return credit',
]);

$qbo->apply_credit_to_invoice($creditMemo->Id, '789', 100.00, '123');
```

### Check a Customer's Credit Balance
```php
$memos = $qbo->get_customer_credit_memos('123');
$available = $qbo->get_customer_available_credits('123');
```

**See:** `scenarios/credit-memo-workflow.md`
