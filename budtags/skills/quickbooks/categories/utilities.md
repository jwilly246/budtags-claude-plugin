# QuickBooks Utility Operations

**Category:** Utility Methods
**Operations:** 5 methods (includes Terms Operations)
**Purpose:** Helper methods for caching, pagination, logging, and payment terms

---

## Overview

Utility operations provide helper functionality for caching, pagination, logging, and payment term management.

**See Also:**
- `patterns/caching.md` - Cache strategy details
- `patterns/logging.md` - LogService usage

---

## Caching & Performance

### `get_items_cached(int $ttl = 300)`
Get items with caching (5-minute default TTL)

**See:** `categories/items.md` for details

### `clearCache()`
Clear all QuickBooks data caches

**Usage:**
```php
$qbo->clearCache();
// Clears Laravel cache for this service
```

**When to Use:**
- After bulk operations
- After importing/updating many records
- When stale data detected

**See:** `patterns/caching.md`

---

## Pagination Helpers

### `fetch_all(string $entity_type)`
Internal helper for fetching all entities with auto-pagination

**Parameters:**
- `entity_type` - QuickBooks entity type ('Customer', 'Invoice', etc.)

**Usage (internal):**
```php
// Used internally by get_all_customers(), get_all_invoices(), etc.
return $this->fetch_all('Customer');
```

**Notes:**
- Handles 1000-item-per-page limit automatically
- Iterates until no more results
- Used by all `get_all_*()` methods

---

## Logging

### `log(string $title, string $message)`
Log QuickBooks operations via LogService

**Usage:**
```php
$this->log(
    'QBO Invoice Created',
    "Invoice #{$invoice->DocNumber} for \${$invoice->TotalAmt}"
);
```

**IMPORTANT:**
- ALWAYS use LogService::store() directly
- NEVER use Laravel Log:: facade
- Logs are organization-scoped

**See:** `patterns/logging.md` for complete logging patterns

---

## Payment Terms Operations

### `get_terms()`
Get all payment terms

**Returns:** Array of Term objects

**Usage:**
```php
$terms = $qbo->get_terms();
foreach ($terms as $term) {
    echo "{$term->Id}: {$term->Name}\n";
}
// Output: 1: Net 15, 2: Net 30, 3: Net 60, etc.
```

**Use Case:** Setting payment terms on invoices

**Example:**
```php
$terms = $qbo->get_terms();
$net30 = array_filter($terms, fn($t) => $t->Name === 'Net 30')[0];

$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'sales_term_ref' => $net30->Id,  // Apply Net 30 terms
    'line_items' => [...]
]);
```

---

## Common Workflows

### Clear Cache After Bulk Import
```php
// Import 500 items from Metrc
foreach ($metrcItems as $item) {
    $qbo->create_item([...]);
}

// Clear cache so next fetch gets fresh data
$qbo->clearCache();
```

### Use Payment Terms in Invoice
```php
// Get available terms
$terms = $qbo->get_terms();

// Find "Net 30"
$net30 = collect($terms)->firstWhere('Name', 'Net 30');

// Create invoice with terms
$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'sales_term_ref' => $net30->Id,
    'due_date' => date('Y-m-d', strtotime('+30 days')),
    'line_items' => [...]
]);
```

### Log QuickBooks Operations
```php
LogService::store(
    'QuickBooks Sync',
    "Synced {$count} items from Metrc to QuickBooks"
);
```

**See:** `patterns/logging.md`
