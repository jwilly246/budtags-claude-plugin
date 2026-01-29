# QuickBooks Logging Pattern

**Pattern:** Organization-Scoped Logging via LogService
**Service:** `LogService::store()`
**CRITICAL:** NEVER use Laravel's `Log::` facade

---

## Overview

All QuickBooks operations must be logged using `LogService::store()` for organization-scoped activity tracking. This ensures logs are associated with the correct organization and user.

**CRITICAL RULE:** NEVER use `Log::info()`, `Log::error()`, or any Laravel Log facade methods. ALWAYS use `LogService::store()`.

---

## LogService Pattern

### Basic Usage

```php
LogService::store(
    'Title of the log entry',
    'Detailed message or description'
);
```

### QuickBooks Examples

**OAuth Connection:**
```php
LogService::store(
    'QuickBooks Connected',
    "Organization '{$org->name}' connected to QuickBooks Company {$realmId}"
);
```

**Invoice Creation:**
```php
LogService::store(
    'QBO Invoice Created',
    "Invoice #{$invoice->DocNumber} for {$customer->DisplayName}\nAmount: \${$invoice->TotalAmt}"
);
```

**Token Refresh:**
```php
LogService::store(
    'QuickBooks Token Refreshed',
    "Access token refreshed for org {$orgId}"
);
```

**Cache Clear:**
```php
LogService::store(
    'QuickBooks Cache Cleared',
    "Cache cleared for org {$orgId}"
);
```

**Metrc Sync:**
```php
LogService::store(
    'QuickBooks Inventory Sync',
    "Synced {$synced} items from Metrc to QuickBooks\nFailed: {$failed}\nSkipped: {$skipped}"
);
```

---

## Organization Scoping

### Automatic Scoping

`LogService::store()` automatically associates logs with:
- Current authenticated user (`user_id`)
- User's active organization (`org_id`)
- Timestamp (`created_at`)

**Database Schema:**
```php
logs table:
- id
- user_id (foreign key)
- org_id (foreign key)
- title (string)
- message (text)
- created_at
- updated_at
```

### Viewing Logs

**Per Organization:**
```php
$logs = Log::where('org_id', $user->active_org->id)
    ->orderBy('created_at', 'desc')
    ->get();
```

**Per User:**
```php
$logs = Log::where('user_id', $user->id)
    ->where('org_id', $user->active_org->id)
    ->get();
```

---

## Logging Levels

### Success Operations

**Pattern:** Use positive titles

```php
LogService::store(
    'QBO Invoice Created',
    "Invoice #{$invoice->DocNumber} created successfully"
);

LogService::store(
    'QuickBooks Connected',
    "Successfully connected to QuickBooks"
);
```

### Errors & Failures

**Pattern:** Include error details

```php
LogService::store(
    'QBO Invoice Creation Failed',
    "Failed to create invoice: {$exception->getMessage()}\n" .
    "Customer ID: {$customerId}\n" .
    "Error Code: {$errorCode}"
);

LogService::store(
    'QuickBooks Token Refresh Failed',
    "Token refresh failed: {$error}\nOrg: {$orgId}"
);
```

### Warnings

**Pattern:** Indicate potential issues

```php
LogService::store(
    'QuickBooks Cache Miss',
    "Cache miss for items - fetching from API\nOrg: {$orgId}"
);
```

---

## What to Log

### ALWAYS Log

✅ OAuth events (connect, disconnect, token refresh)
✅ Entity creation (invoices, customers, credit memos)
✅ Payment recording
✅ Sync operations (Metrc → QuickBooks)
✅ Bulk operations (importing many items)
✅ Errors and exceptions
✅ Cache clear events

### DON'T Log

❌ Individual read operations (get_customer, get_invoice)
❌ Cache hits
❌ Internal method calls
❌ Validation checks

**Reason:** Avoid log spam. Only log significant events.

---

## Error Logging Pattern

### Try-Catch with Logging

```php
try {
    $invoice = $qbo->create_invoice($data);

    LogService::store(
        'QBO Invoice Created',
        "Invoice #{$invoice->DocNumber} created"
    );

    return $invoice;
} catch (Exception $e) {
    LogService::store(
        'QBO Invoice Creation Failed',
        "Error: {$e->getMessage()}\nData: " . json_encode($data)
    );

    throw $e;  // Re-throw after logging
}
```

---

## Log Message Format

### Structured Format

**Title:** Short, descriptive, searchable
**Message:** Detailed, multi-line if needed

```php
// ✅ GOOD
LogService::store(
    'QBO Payment Recorded',
    "Payment ID: {$payment->Id}\n" .
    "Invoice: #{$invoice->DocNumber}\n" .
    "Amount: \${$payment->TotalAmt}\n" .
    "Method: {$paymentMethod->Name}"
);
```

```php
// ❌ BAD - Not enough detail
LogService::store(
    'Payment',
    'Payment made'
);
```

---

## Viewing Logs in UI

**Route:** `/logs` (typically)

**Display:**
```php
// In controller
public function index() {
    $logs = Log::where('org_id', auth()->user()->active_org->id)
        ->where('title', 'LIKE', 'QBO%')  // Filter QuickBooks logs
        ->orderBy('created_at', 'desc')
        ->paginate(50);

    return inertia('Logs/Index', ['logs' => $logs]);
}
```

---

## Best Practices

✅ **ALWAYS use LogService::store()**
✅ **ALWAYS include entity IDs in messages**
✅ **ALWAYS log errors with full exception details**
✅ **ALWAYS use descriptive titles**
✅ **ALWAYS include org_id in error logs**

❌ **NEVER use Log::info() or Log::error()**
❌ **NEVER log sensitive data (access tokens, passwords)**
❌ **NEVER log every read operation**
❌ **NEVER use generic titles** ("Error", "Success")

---

## Testing Logs

### Verify Logging in Tests

```php
// Create invoice
$qbo->create_invoice($data);

// Assert log was created
$log = Log::where('title', 'QBO Invoice Created')
    ->where('org_id', $user->active_org->id)
    ->latest()
    ->first();

$this->assertNotNull($log);
$this->assertStringContainsString('Invoice #', $log->message);
```

---

## Related Patterns

- `patterns/multi-tenancy.md` - Organization scoping
- `categories/utilities.md` - log() utility method
- `.claude/docs/backend/logging.md` - Complete logging guide
