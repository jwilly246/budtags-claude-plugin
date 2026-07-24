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

The wrapper handles fetch-before-update two ways. For **invoices and items** the `*_id` + array signature fetches internally, so the SyncToken never leaves the method. For **customers** the caller fetches the `IPPCustomer` first (getting its SyncToken), mutates it, and passes the whole object in.

### Customer: caller fetches, wrapper submits

Real signature - `update_customer(IPPCustomer $customer): IPPCustomer`. The controller fetches, mutates, then hands the object over:

```php
// ✅ CORRECT - caller fetches so the SyncToken rides along on the object
$customer = $api->get_customer($input['id']);          // IPPCustomer with current SyncToken
$customer->DisplayName = (string) $input['displayName'];
$customer->Active = (bool) $input['active'];
$updated = $api->update_customer($customer);           // wrapper calls $this->service->Update($customer)
```

```php
// Inside QuickBooksApi::update_customer()
public function update_customer(IPPCustomer $customer): IPPCustomer {
    $customer = $this->service->Update($customer);     // SyncToken came from get_customer()
    $error = $this->service->getLastError();
    if ($error) {
        throw new ConflictException($error->getResponseBody());
    }
    return $customer;
}
```

```php
// ❌ WRONG - hand-built object, no fetch, no SyncToken
$customer = new IPPCustomer();
$customer->Id = $input['id'];
$customer->DisplayName = $input['displayName'];
$api->update_customer($customer);                      // FAILS - stale/missing SyncToken
```

---

## Common Update Operations

### Update Invoice

Real signature - `update_invoice(string $invoice_id, array $invoice_data): IPPInvoice`. It fetches the existing invoice for its SyncToken before applying changes:

```php
public function update_invoice(string $invoice_id, array $invoice_data): IPPInvoice {
    // Fetch existing invoice (need SyncToken for QB API updates)
    $existing_invoice = $this->get_invoice($invoice_id);
    if (!$existing_invoice) {
        throw new \Exception("Invoice {$invoice_id} not found");
    }

    if (isset($invoice_data['doc_number'])) {
        $existing_invoice->DocNumber = (string) $invoice_data['doc_number'];
    }
    if (isset($invoice_data['private_note'])) {
        $existing_invoice->PrivateNote = (string) $invoice_data['private_note'];
    }
    // ... txn_date, due_date, line_items ...

    $updated_invoice = $this->service->Update($existing_invoice);   // SyncToken preserved

    $error = $this->service->getLastError();
    if ($error) {
        throw new ConflictException($error->getResponseBody());
    }
    return $updated_invoice;
}
```

Caller side:
```php
$api->update_invoice($invoice_id, ['private_note' => 'Reviewed by ops']);
```

### Update Item

Real signature - `update_item(string $item_id, array $data): IPPItem`. It fetches the item (via `FindById('Item', $item_id)`) for its SyncToken, then applies any of `UnitPrice`, `PurchaseCost`, `QtyOnHand`:

```php
public function update_item(string $item_id, array $data): IPPItem {
    $item = $this->service->FindById('Item', $item_id);   // fetch for SyncToken

    if (isset($data['UnitPrice']))    { $item->UnitPrice = (float) $data['UnitPrice']; }
    if (isset($data['PurchaseCost'])) { $item->PurchaseCost = (float) $data['PurchaseCost']; }
    if (isset($data['QtyOnHand']))    { $item->QtyOnHand = (float) $data['QtyOnHand']; }

    $updated_item = $this->service->Update($item);        // full update, SyncToken preserved

    $error = $this->service->getLastError();
    if ($error) {
        throw new \Exception($error->getResponseBody());
    }
    return $updated_item;
}
```

> There is no public `get_item()` method. Items are fetched internally with `$this->service->FindById('Item', $id)`. `update_item_quantity(string $item_id, float $new_quantity)` is a narrower variant that only sets `QtyOnHand`, used by `sync_quantities_from_metrc()`.

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
