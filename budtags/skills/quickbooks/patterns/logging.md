# QuickBooks Logging Pattern

**Pattern:** Activity logging via `LogService`
**Service:** `LogService::store()` and `LogService::store_keyed()`
**CRITICAL:** NEVER use Laravel's `Log::` facade

---

## Overview

All QuickBooks operations are logged through `LogService`, which writes to the app's `logs` table. Do not use the Laravel `Log::` facade.

**CRITICAL RULE:** NEVER use `Log::info()`, `Log::error()`, or any Laravel Log facade methods. ALWAYS use `LogService::store()` (or `store_keyed()` for fixed-cadence jobs).

---

## LogService Signatures

```php
LogService::store(string $title, string|false $desc, ?Model $loggable = null): Log;
LogService::store_keyed(string $dedupe_key, string $title, string|false $desc, ?Model $loggable = null): Log;
```

- `$desc` accepts `false` (e.g. a failed `json_encode`) and is stored as `'JSON encoding failed'`.
- `$loggable` is an optional Eloquent model recorded as a polymorphic `loggable_id`/`loggable_type` (for example the `Organization` in the billing sync).
- `store()` captures `request()->user()?->id` as `user_id`. In a queue or console context there is no request user, so `user_id` is null - that is expected for the scheduled sync.

> There is NO `org_id` column and NO automatic active-org association. Logs are attributed to the acting user (`user_id`) and, when passed, a `loggable` model. Do not claim org scoping that the code does not do.

### QuickBooks Examples (real titles from the code)

```php
// oauth_complete() failure
LogService::store('QuickBooks OAuth Failed', "Token exchange failed for {$user->email} (realm: {$realm}). Error: {$e->getMessage()}");

// send_invoice() success
LogService::store('QB Invoice Sent', "Invoice ID: {$invoice_id}\nDoc Number: {$invoice->DocNumber}\nSent to: ".($send_to_email ?? 'customer default email'));

// create_payment() success
LogService::store('QB Payment Recorded', "Payment ID: {$result->Id}\nInvoice: {$payment_data['invoice_id']}\nAmount: \${$payment_data['amount']}");

// billing sync per-org failure - Organization passed as $loggable
LogService::store('QBO Invoice Sync Failed', "Org: {$org->name} (ID: {$org->id}). Error: {$e->getMessage()}", $org);
```

Other real titles you will see: `QuickBooks Corrupt Token Cleaned`, `QuickBooks Token Refresh Failed`, `QuickBooks API Error`, `QuickBooks Fetch All Error`, `QB Payment Methods Fetch Failed`, `QB Deposit Accounts Fetch Failed`, `QuickBooks Get Terms Failed`, `QuickBooks Get Credit Memos Failed`, `QB Invoice Send Failed`, `QB Payment Creation Failed`, `QB Payment Exception`, `QBO Invoice Sync`.

---

## Storage Model

`store()` writes a `Log` row with these columns:

```php
Log::create([
    'loggable_id'   => $loggable?->id,        // optional morph target
    'loggable_type' => $loggable ? $loggable::class : null,
    'user_id'       => request()->user()?->id, // null in queue/console context
    'title'         => $title,                 // truncated to 255
    'notes'         => $desc,                   // the message column is `notes`, not `message`
    'timestamp'     => now(),
]);
```

> The message field is `notes`. There is no `message` column and no `org_id` column.

### Coalescing (burst dedupe)

`store()` does not blindly insert. Before inserting it scans the newest ~30 rows and, if it finds an identical event (same `title`, `loggable`, `user_id`, and base `notes`) within a 10-minute window, it bumps that row's repeat counter and moves its timestamp forward instead of adding a duplicate. The repeat suffix looks like:

```
\n[Repeated 4x, first 2026-07-24 06:00:01, last 2026-07-24 06:40:02]
```

So a tight retry loop that logs the same failure does not flood the table.

---

## Keyed Logging for Scheduled Jobs

`store()`'s coalescer only merges duplicates within a 10-minute window and a shallow tail scan, which is useless for a job that runs once a day. For fixed-cadence work use `store_keyed($dedupe_key, ...)`: it keeps a cache pointer to the last row written under `$dedupe_key`, so identical notes bump that one row's repeat counter no matter how far apart the runs are, while a changed message starts a fresh row.

The billing invoice sync uses this for auth failure so a dead service-user token does not append an identical row every morning:

```php
// SyncQboInvoices::initialize_api() - token missing or refresh failed
LogService::store_keyed(
    'qbo-invoice-sync-auth',
    'QBO Invoice Sync Auth Failed',
    "Service user ID {$user->id} has no QBO token. Re-authenticate at /quickbooks.",
);
```

The result is a single live "sync is down since X" entry with a repeat counter, rather than 30 identical rows after a month of silence. Once someone re-authenticates and the message changes (or the failure stops), the keyed row stops bumping. See `patterns/billing-invoice-sync.md`.

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

## Viewing Logs

Filter by `title` (searchable) and, when relevant, by the `loggable` morph - not by a nonexistent `org_id` column:

```php
// QuickBooks logs attached to a specific org (via $loggable = Organization)
$logs = Log::where('loggable_type', Organization::class)
    ->where('loggable_id', $org->id)
    ->where('title', 'LIKE', 'QBO%')
    ->latest('timestamp')
    ->paginate(50);
```

---

## Best Practices

✅ **ALWAYS use `LogService::store()` (or `store_keyed()` for cron/scheduled jobs)**
✅ **ALWAYS include entity IDs in the `$desc` message**
✅ **ALWAYS log errors with the full exception message**
✅ **ALWAYS use descriptive titles**
✅ **ALWAYS pass a `$loggable` model when the event belongs to one** (e.g. the `Organization` in the sync)

❌ **NEVER use `Log::info()` or `Log::error()`**
❌ **NEVER log tokens or secrets** (`access_key` / `refresh_key`)
❌ **NEVER claim `org_id` scoping - there is no such column**
❌ **NEVER use generic titles** ("Error", "Success")
❌ **NEVER use `store()` for a once-daily job's repeat suppression - use `store_keyed()`**

---

## Testing Logs

Assert on `title`, the `loggable` morph, and the `notes` column (not `message`):

```php
$qbo->create_payment($data);

$log = Log::where('title', 'QB Payment Recorded')->latest('timestamp')->first();

$this->assertNotNull($log);
$this->assertStringContainsString('Payment ID:', $log->notes);
```

---

## Related Patterns

- `patterns/multi-tenancy.md` - Organization scoping
- `patterns/billing-invoice-sync.md` - Keyed auth-failure logging for the sync
- `.claude/docs/backend/logging.md` - Complete logging guide
