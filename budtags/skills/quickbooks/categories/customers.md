# QuickBooks Customer Operations

**Category:** Customer Operations
**Operations:** 8 methods
**Purpose:** CRUD operations for QuickBooks customers

---

## Overview

Customer operations manage QuickBooks customer records including creation, retrieval, updates, and related entity queries (invoices, credit memos).

**Key Concepts:**
- Pagination for large customer lists
- SyncToken required for updates
- Bulk operations for efficiency

**See Also:**
- `ENTITY_TYPES.md` - Customer TypeScript type definition
- `patterns/syncing.md` - SyncToken update patterns

---

## Operations

### 5. `get_customers(int $start_at = 1, int $max_count = 100)`

**Purpose:** Get paginated list of customers

**Signature:**
```php
public function get_customers(int $start_at = 1, int $max_count = 100): array
```

**Parameters:**
- `$start_at` - Starting position (1-indexed)
- `$max_count` - Max customers per page (default: 100, max: 1000)

**Returns:** Array of Customer objects

**Usage:**
```php
$customers = $qbo->get_customers(1, 50); // Get first 50 customers
```

**Notes:**
- QuickBooks limits to 1000 results per query
- Use `get_all_customers()` for full list with auto-pagination

---

### 6. `get_all_customers()`

**Purpose:** Get ALL customers with automatic pagination

**Signature:**
```php
public function get_all_customers(): array
```

**Returns:** Array of all Customer objects

**Usage:**
```php
$allCustomers = $qbo->get_all_customers();
// Automatically handles pagination
```

**Notes:**
- Uses `fetch_all()` utility for auto-pagination
- Handles 1000-item-per-page limit
- May take longer for large customer lists

---

### 7. `get_customer(string $id)`

**Purpose:** Get single customer by QuickBooks ID

**Signature:**
```php
public function get_customer(string $id): ?object
```

**Parameters:**
- `$id` - QuickBooks customer ID

**Returns:** Customer object or `null` if not found

**Usage:**
```php
$customer = $qbo->get_customer('123');
if ($customer) {
    echo $customer->DisplayName;
}
```

---

### 8. `get_customers_by_id(array $ids)`

**Purpose:** Bulk fetch multiple customers by IDs

**Signature:**
```php
public function get_customers_by_id(array $ids): array
```

**Parameters:**
- `$ids` - Array of QuickBooks customer IDs

**Returns:** Array of Customer objects

**Usage:**
```php
$customers = $qbo->get_customers_by_id(['123', '456', '789']);
```

**Notes:**
- More efficient than multiple single requests
- Returns only found customers (no error for missing IDs)

---

### 9. `update_customer(array $data)`

**Purpose:** Update existing customer

**Signature:**
```php
public function update_customer(array $data): object
```

**Parameters:**
- `$data` - Array with customer data (must include `id`)

**Required Fields:**
- `id` - QuickBooks customer ID

**Optional Fields:**
- `display_name`, `company_name`, `given_name`, `family_name`
- `primary_phone`, `primary_email_address`
- `billing_address`, `shipping_address`

**Usage:**
```php
$updated = $qbo->update_customer([
    'id' => '123',
    'display_name' => 'New Name',
    'primary_email_address' => 'newemail@example.com'
]);
```

**Important:**
- Fetches current customer first to get SyncToken
- Updates only provided fields
- Preserves other fields

**See:** `patterns/syncing.md` for SyncToken requirements

---

### 10. `make_customer()`

**Purpose:** Example/template method for creating customers

**Signature:**
```php
public function make_customer(): object
```

**Notes:**
- This appears to be example/template code
- Creates a hard-coded customer for testing
- Not recommended for production use
- Better to create custom method accepting parameters

---

### 11. `get_customer_invoices(string $customer_id)`

**Purpose:** Get all invoices for a specific customer

**Signature:**
```php
public function get_customer_invoices(string $customer_id): array
```

**Parameters:**
- `$customer_id` - QuickBooks customer ID

**Returns:** Array of Invoice objects

**Usage:**
```php
$invoices = $qbo->get_customer_invoices('123');
foreach ($invoices as $invoice) {
    echo "Invoice #{$invoice->DocNumber}: \${$invoice->TotalAmt}\n";
}
```

**See Also:** `categories/invoices.md` for invoice operations

---

### 12. `get_customer_credit_memos(string $customer_id)`

**Purpose:** Get all credit memos for a specific customer

**Signature:**
```php
public function get_customer_credit_memos(string $customer_id): array
```

**Parameters:**
- `$customer_id` - QuickBooks customer ID

**Returns:** Array of CreditMemo objects

**Usage:**
```php
$credits = $qbo->get_customer_credit_memos('123');
```

**See Also:** `categories/credit-memos.md` for credit memo operations

---

## Common Workflows

### Fetch and Display Customers
```php
$qbo = new QuickBooksApi();
$qbo->set_user($user);

$customers = $qbo->get_all_customers();
foreach ($customers as $customer) {
    echo "{$customer->DisplayName} - {$customer->PrimaryEmailAddr->Address}\n";
}
```

### Update Customer Contact Info
```php
$updated = $qbo->update_customer([
    'id' => '123',
    'primary_email_address' => 'newemail@example.com',
    'primary_phone' => '(555) 123-4567'
]);
```

### Get Customer Financial Summary
```php
$customer = $qbo->get_customer('123');
$invoices = $qbo->get_customer_invoices('123');
$credits = $qbo->get_customer_credit_memos('123');

$totalInvoiced = array_sum(array_column($invoices, 'TotalAmt'));
$totalCredits = array_sum(array_column($credits, 'TotalAmt'));
```
