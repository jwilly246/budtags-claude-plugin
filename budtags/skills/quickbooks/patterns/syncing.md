# QuickBooks SyncToken Pattern

**Pattern:** Fetch-Before-Update
**Requirement:** SyncToken required for all UPDATE operations
**Purpose:** Optimistic concurrency control

---

## Overview

QuickBooks uses SyncToken for optimistic concurrency control. Every entity (Invoice, Customer, Item, etc.) has a SyncToken that increments with each update.

**Rule:** To update an entity, you MUST provide the current SyncToken. If the SyncToken doesn't match, the update fails.

---

## What is SyncToken?

### Version Number

SyncToken is like a version number for each entity:

```json
{
    "Id": "123",
    "DisplayName": "John Doe",
    "SyncToken": "5"
}
```

**After update:**
```json
{
    "Id": "123",
    "DisplayName": "Jane Doe",
    "SyncToken": "6"  // Incremented
}
```

### Why SyncToken Exists

**Problem:** Two users update same entity simultaneously
- User A fetches customer (SyncToken: 5)
- User B fetches customer (SyncToken: 5)
- User A updates customer (SyncToken becomes 6)
- User B tries to update customer with SyncToken 5 → **FAILS**

**Solution:** User B must fetch fresh entity (SyncToken: 6) before updating

---

## Fetch-Before-Update Pattern

### ALWAYS Fetch Current Entity First

```php
// ✅ CORRECT - Fetch first to get current SyncToken
public function update_customer(array $data): object {
    // 1. Fetch current customer
    $customer = $this->get_customer($data['id']);

    if (!$customer) {
        throw new Exception('Customer not found');
    }

    // 2. Update fields
    $customer->DisplayName = $data['display_name'] ?? $customer->DisplayName;
    $customer->PrimaryEmailAddr = $data['primary_email_address'] ?? $customer->PrimaryEmailAddr;

    // 3. SyncToken is preserved from fetched entity
    // 4. Send update with current SyncToken
    $updated = $this->dataService->Update($customer);

    return $updated;
}
```

```php
// ❌ WRONG - No fetch, no SyncToken
public function update_customer_wrong(array $data): object {
    $customer = new Customer();
    $customer->Id = $data['id'];
    $customer->DisplayName = $data['display_name'];
    // Missing SyncToken! Update will FAIL
    $updated = $this->dataService->Update($customer);
}
```

---

## Common Update Operations

### Update Invoice

```php
public function update_invoice(array $data): object {
    // Fetch current invoice (includes SyncToken)
    $invoice = $this->get_invoice($data['id']);

    // Update fields
    if (isset($data['customer_memo'])) {
        $invoice->CustomerMemo = $data['customer_memo'];
    }

    if (isset($data['line_items'])) {
        $invoice->Line = $this->build_line_items($data['line_items']);
    }

    // Update (SyncToken preserved)
    $updated = $this->dataService->Update($invoice);

    LogService::store(
        'QBO Invoice Updated',
        "Invoice #{$invoice->DocNumber} updated"
    );

    return $updated;
}
```

### Update Item

```php
public function update_item(array $data): object {
    // Fetch current item
    $item = $this->get_item($data['id']);

    // Update quantity
    if (isset($data['quantity_on_hand'])) {
        $item->QtyOnHand = $data['quantity_on_hand'];
    }

    // Update (SyncToken preserved)
    $updated = $this->dataService->Update($item);

    return $updated;
}
```

---

## SyncToken Error Handling

### Stale SyncToken Error

**Error Message:**
```
Stale object error: You and another user were working on the same thing.
Please start over.
```

**Cause:** SyncToken provided doesn't match current SyncToken in QuickBooks

**Solution:**
```php
try {
    $updated = $this->dataService->Update($entity);
} catch (Exception $e) {
    if (str_contains($e->getMessage(), 'Stale object')) {
        // Re-fetch entity to get latest SyncToken
        $entity = $this->get_entity($entity->Id);

        // Re-apply updates
        $entity->Field = $newValue;

        // Retry update
        $updated = $this->dataService->Update($entity);
    } else {
        throw $e;
    }
}
```

---

## Best Practices

### ALWAYS Fetch Before Update

```php
// ✅ CORRECT
$invoice = $qbo->get_invoice($id);  // Fetch current
$invoice->CustomerMemo = 'Updated memo';
$updated = $qbo->dataService->Update($invoice);  // Update with SyncToken
```

```php
// ❌ WRONG
$invoice = new Invoice();
$invoice->Id = $id;
$invoice->CustomerMemo = 'Updated memo';
$updated = $qbo->dataService->Update($invoice);  // FAILS - no SyncToken
```

### Preserve Unchanged Fields

```php
// ✅ CORRECT - Only update fields that changed
$customer = $qbo->get_customer($id);
$customer->DisplayName = $newName;  // Update only this field
$updated = $qbo->dataService->Update($customer);  // Other fields preserved
```

```php
// ❌ WRONG - Might clear fields
$customer = new Customer();
$customer->Id = $id;
$customer->DisplayName = $newName;
$updated = $qbo->dataService->Update($customer);  // Other fields lost
```

---

## When SyncToken is NOT Required

### Create Operations

**No SyncToken needed:**
```php
// Creating new entities doesn't require SyncToken
$invoice = $qbo->create_invoice($data);
$customer = $qbo->create_customer($data);
$item = $qbo->create_item($data);
```

### Read Operations

**No SyncToken needed:**
```php
$invoice = $qbo->get_invoice($id);
$customers = $qbo->get_all_customers();
```

### Delete Operations

**SyncToken IS required:**
```php
// Fetch first to get SyncToken
$invoice = $qbo->get_invoice($id);

// Delete with SyncToken
$qbo->dataService->Delete($invoice);
```

---

## Testing SyncToken Handling

### Simulate Concurrent Updates

```php
// User A fetches customer
$customerA = $qbo->get_customer('123');  // SyncToken: 5

// User B fetches customer
$customerB = $qbo->get_customer('123');  // SyncToken: 5

// User A updates first
$customerA->DisplayName = 'Alice';
$qbo->dataService->Update($customerA);  // Success, SyncToken now 6

// User B tries to update (has stale SyncToken: 5)
$customerB->DisplayName = 'Bob';
$qbo->dataService->Update($customerB);  // FAILS - Stale SyncToken!
```

---

## Summary

✅ **ALWAYS fetch entity before updating**
✅ **ALWAYS preserve SyncToken from fetched entity**
✅ **ALWAYS handle SyncToken errors gracefully**
✅ **ALWAYS log update operations**

❌ **NEVER create entity object manually for updates**
❌ **NEVER assume SyncToken value**
❌ **NEVER skip fetching before update**
❌ **NEVER ignore SyncToken errors**

---

## Related Patterns

- `patterns/error-handling.md` - Handling SyncToken errors
- `categories/customers.md` - update_customer() example
- `categories/invoices.md` - update_invoice() example
- `categories/items.md` - update_item() example
