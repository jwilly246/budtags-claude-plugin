# QuickBooks Account Operations

**Category:** Account Operations
**Operations:** 4 methods
**Purpose:** Query the chart of accounts

---

## Overview

Account operations read the QuickBooks chart of accounts. There are no
type-filtered helpers such as `get_income_accounts` / `get_expense_accounts` -
filter the full list yourself by `AccountType`.

**Common Account Types:** Income, Expense, Cost of Goods Sold, Bank,
Other Current Asset, Accounts Receivable, Accounts Payable.

**See Also:**
- `ENTITY_TYPES.md` - Account type definition
- `categories/payments.md` - `get_deposit_accounts` / `get_deposit_accounts_cached`
  (Bank-type accounts for payment deposits)

---

## Operations

### 1. `get_accounts(int $start_at = 1, int $max_count = 100): Collection`

Paginated accounts (`SELECT * FROM Account`). Returns empty on error.

### 2. `get_all_accounts(): Collection`

All accounts, auto-paginated.

### 3. `get_all_accounts_cached(string $org_id): Collection`

Cached `get_all_accounts` (`qbo:accounts:{org_id}`), stale-while-revalidate.
Backs `GET /quickbooks/accounts`.

### 4. `get_account(string $id): ?object`

Single account by ID (`FindById`), or `null`. Used to validate a deposit account
before recording a payment.

```php
$account = $qbo->get_account('35');
if ($account && $account->AccountType === 'Bank') {
    // valid deposit account
}
```

---

## Common Workflows

### Group Accounts by Type
```php
$byType = $qbo->get_all_accounts()->groupBy('AccountType');
foreach ($byType as $type => $accts) {
    echo "{$type}: {$accts->count()}\n";
}
```

### Find Income Accounts (filter yourself)
```php
$income = $qbo->get_all_accounts()
    ->filter(fn ($a) => $a->AccountType === 'Income')
    ->values();
```
