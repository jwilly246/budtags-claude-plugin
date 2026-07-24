# QuickBooks Customer Operations

**Category:** Customer Operations
**Operations:** 8 methods
**Purpose:** Read and update QuickBooks customers

---

## Overview

Customer operations read customer records and update them. Note there is no
`create_customer` on `QuickBooksApi` - new customers are created by the sync
flow in the controller (`sync_customer`), and `make_customer()` is a hardcoded
example only. Updates take the fetched `IPPCustomer` object (for its SyncToken),
never a bare array.

**See Also:**
- `ENTITY_TYPES.md` - Customer type definition
- `patterns/syncing.md` - SyncToken update patterns
- `categories/invoices.md`, `categories/credit-memos.md` - customer-scoped reads

---

## Operations

### 1. `get_customers(int $start_at = 1, int $max_count = 100): Collection`

Paginated list of customers (`SELECT * FROM Customer`). Returns an empty
Collection on error.

```php
$customers = $qbo->get_customers(1, 50);
```

---

### 2. `get_all_customers(): Collection`

All customers, auto-paginated (1000/page via `call_query_paginated`).

```php
foreach ($qbo->get_all_customers() as $c) {
    echo "{$c->DisplayName}\n";
}
```

---

### 3. `get_customer(string $id): IPPCustomer`

Single customer by QuickBooks ID (`FindById`).

```php
$customer = $qbo->get_customer('123');
echo $customer->DisplayName;
```

---

### 4. `get_customers_by_id(Collection $ids): Collection`

Bulk fetch by IDs via a single `WHERE Id IN (...)` query. Takes a `Collection`
of string IDs (not an array). Returns an empty Collection on error.

```php
$customers = $qbo->get_customers_by_id(collect(['123', '456', '789']));
```

---

### 5. `get_customers_by_id_cached(string $orgId, Collection $ids): Collection`

Cached bulk fetch. Reads each customer from the per-org cache
(`qbo:customer:{orgId}:{id}`), fetches only the misses, and returns customers in
the same order as `$ids` (so they stay aligned with a matching invoice list).

```php
$customers = $qbo->get_customers_by_id_cached($orgId, $invoiceCustomerIds);
```

---

### 6. `update_customer(IPPCustomer $customer): IPPCustomer`

Update a customer. Pass the fetched `IPPCustomer` object (it already carries the
SyncToken); mutate its fields first. Throws `ConflictException` on API error.

```php
$customer = $qbo->get_customer('123');
$customer->DisplayName = 'New Name';
if ($customer->PrimaryEmailAddr == null) {
    $customer->PrimaryEmailAddr = new IPPEmailAddress;
}
$customer->PrimaryEmailAddr->Address = 'newemail@example.com';

$updated = $qbo->update_customer($customer);
```

**Important:** fetch first (SyncToken), mutate, then update. See
`patterns/syncing.md`.

---

### 7. `get_customer_invoices(string $customer_id, int $start_at = 1, int $max_count = 100): Collection`

All invoices for one customer (`WHERE CustomerRef = '...'`), with line detail.

```php
$invoices = $qbo->get_customer_invoices('123');
```

**See Also:** `categories/invoices.md`.

---

### 8. `make_customer(): void`

Hardcoded example that creates a fixed sample customer via the SDK Facade.
Returns `void`. For reference/testing only - not for production.

---

## Common Workflows

### Fetch and Display Customers
```php
$qbo = new QuickBooksApi();
$qbo->set_service($user);

foreach ($qbo->get_all_customers() as $customer) {
    echo "{$customer->DisplayName}\n";
}
```

### Update Customer Contact Info
```php
$customer = $qbo->get_customer('123');
$customer->CompanyName = 'Acme Cannabis Co.';
if ($customer->PrimaryPhone == null) {
    $customer->PrimaryPhone = new IPPTelephoneNumber;
}
$customer->PrimaryPhone->FreeFormNumber = '(555) 123-4567';

$qbo->update_customer($customer);
```

### Customer Financial Summary
```php
$customer = $qbo->get_customer('123');
$invoices = $qbo->get_customer_invoices('123');
$available = $qbo->get_customer_available_credits('123'); // see credit-memos.md
```
