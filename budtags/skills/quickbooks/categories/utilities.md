# QuickBooks Utility Operations

**Category:** Utility Methods
**Operations:** 6 methods
**Purpose:** Company info, payment terms, cache management, and pagination

---

## Overview

Utility operations cover company info, payment terms (used on invoices), cache
invalidation after writes, and the internal pagination helper.

**Logging note:** there is no `log()` method on the service. Logging is done by
calling `LogService::store(...)` directly. NEVER use the Laravel `Log::` facade.

**See Also:**
- `patterns/caching.md` - Cache strategy
- `patterns/logging.md` - LogService usage

---

## Company Info

### 1. `get_company_info(): ?IPPCompanyInfo`

Fetch the connected company's info; returns `null` on error. Used as a quick
connection-status/health check after `set_service`.

```php
$qbo->set_service($user);
$company = $qbo->get_company_info();
if ($company === null) {
    // not connected / token problem
}
```

---

## Payment Terms

### 2. `get_terms(int $start_at = 1, int $max_count = 100): Collection`

Payment terms (`SELECT * FROM Term`), e.g. Net 15 / Net 30. Logs and returns
empty on error.

```php
$net30 = $qbo->get_terms()->firstWhere('Name', 'Net 30');

$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'sales_term_ref' => $net30->Id,
    'due_date' => date('Y-m-d', strtotime('+30 days')),
    'line_items' => [...],
]);
```

### 3. `get_terms_cached(string $org_id): Collection`

Cached `get_terms` (`qbo:terms:{org_id}`). Backs `GET /quickbooks/terms`.

---

## Cache Management

### 4. `clear_cache(string $orgId): void`

Forget the per-org read caches: items, accounts, all-invoices, credit memos,
payment methods, deposit accounts, and terms. Call after any write so the next
fetch is fresh.

```php
$qbo->update_item($id, $data);
$qbo->clear_cache($orgId);
```

Note: `clear_cache` does NOT clear the paginated invoice pages - use
`clear_invoices_cache` for those.

### 5. `clear_invoices_cache(string $orgId): void`

Forget the paginated invoice caches (`qbo:invoices:{orgId}:page:1..100`).

```php
$qbo->clear_invoices_cache($orgId);
```

---

## Pagination Helper

### 6. `call_query_paginated(string $query): Collection` *(protected)*

Internal helper that pages through a QuickBooks query 1000 rows at a time until a
short page is returned. Backs all `get_all_*` methods. Not part of the public API
- pass a full query string, e.g. `SELECT * FROM Item`.

```php
// internal usage
return $this->call_query_paginated('SELECT * FROM Customer');
```

---

## Common Workflows

### Clear Cache After a Bulk Write
```php
foreach ($rows as $row) {
    $qbo->create_item($row);
}
$qbo->clear_cache($orgId);
```

### Use Payment Terms on an Invoice
```php
$net30 = $qbo->get_terms()->firstWhere('Name', 'Net 30');
$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'sales_term_ref' => $net30->Id,
    'due_date' => date('Y-m-d', strtotime('+30 days')),
    'line_items' => [...],
]);
```

### Log an Operation
```php
LogService::store('QuickBooks Sync', "Synced {$count} items from Metrc");
```

**See:** `patterns/logging.md`
