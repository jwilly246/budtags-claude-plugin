# QuickBooks Account Operations

**Category:** Account Operations
**Operations:** 5 methods
**Purpose:** Query chart of accounts for financial tracking

---

## Overview

Account operations access the QuickBooks chart of accounts. Accounts categorize financial transactions (income, expenses, assets, liabilities).

**Common Account Types:**
- Income
- Expense
- Bank
- Other Current Asset
- Accounts Receivable
- Accounts Payable

**See Also:**
- `ENTITY_TYPES.md` - Account type definition

---

## Operations

### 37. `get_accounts()`
Get all accounts

**Returns:** Array of Account objects

**Usage:**
```php
$accounts = $qbo->get_accounts();
foreach ($accounts as $account) {
    echo "{$account->Name} ({$account->AccountType})\n";
}
```

### 38. `get_income_accounts()`
Get accounts of type 'Income'

**Returns:** Array of Account objects (type 'Income')

**Usage:**
```php
$incomeAccounts = $qbo->get_income_accounts();
```

**Use Case:** Assigning income accounts to invoice line items or items

### 39. `get_expense_accounts()`
Get accounts of type 'Expense' or 'Cost of Goods Sold'

**Returns:** Array of Account objects

**Usage:**
```php
$expenseAccounts = $qbo->get_expense_accounts();
```

**Use Case:** Assigning expense accounts to items or bills

### 40. `get_deposit_accounts()` *(duplicate - see payments category)*
Get bank and asset accounts for deposits

**Returns:** Array of Account objects

### 41. `get_account(string $id)`
Get single account by QuickBooks ID

**Returns:** Account object or `null`

**Usage:**
```php
$account = $qbo->get_account('79');
if ($account) {
    echo "Account: {$account->Name}";
}
```

---

## Common Workflows

### List All Accounts by Type
```php
$accounts = $qbo->get_accounts();

$byType = [];
foreach ($accounts as $account) {
    $byType[$account->AccountType][] = $account;
}

foreach ($byType as $type => $accts) {
    echo "$type:\n";
    foreach ($accts as $acct) {
        echo "  - {$acct->Name}\n";
    }
}
```

### Find Account for Invoice Line Items
```php
$incomeAccounts = $qbo->get_income_accounts();

// Use in invoice line items
$lineItem = [
    'item_id' => '456',
    'quantity' => 10,
    'unit_price' => 25.00,
    'income_account_ref' => $incomeAccounts[0]->Id
];
```
