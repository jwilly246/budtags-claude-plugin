# QuickBooks Error Handling Pattern

**Pattern:** Try-Catch with Logging
**Service:** QuickBooks Online API v3
**Common Errors:** SyncToken, Validation, Authentication

---

## Overview

QuickBooks API operations can fail for various reasons. All errors should be caught, logged via LogService, and handled gracefully.

**See:** `ERROR_HANDLING.md` (in backups/) for complete error catalog

---

## Common Error Types

### 1. SyncToken Errors (Most Common)

**Error:**
```
Stale object error: You and another user were working on the same thing.
```

**Cause:** SyncToken doesn't match current value in QuickBooks

**Solution:**
```php
try {
    $updated = $qbo->update_customer($data);
} catch (Exception $e) {
    if (str_contains($e->getMessage(), 'Stale object')) {
        // Re-fetch to get latest SyncToken
        $customer = $qbo->get_customer($data['id']);

        // Re-apply updates
        $customer->DisplayName = $data['display_name'];

        // Retry
        $updated = $qbo->dataService->Update($customer);
    } else {
        throw $e;
    }
}
```

**See:** `patterns/syncing.md` for complete SyncToken pattern

---

### 2. Validation Errors

**Error:**
```
ValidationFault: Invalid Reference Id
ValidationFault: Required parameter missing
```

**Cause:** Invalid or missing required fields

**Common Causes:**
- Invalid customer ID
- Invalid item ID
- Missing required line items
- Invalid date format

**Solution:**
```php
try {
    $invoice = $qbo->create_invoice($data);
} catch (Exception $e) {
    if (str_contains($e->getMessage(), 'ValidationFault')) {
        LogService::store(
            'QBO Validation Error',
            "Validation failed: {$e->getMessage()}\nData: " . json_encode($data)
        );

        return response()->json([
            'error' => 'Invalid invoice data: ' . $e->getMessage()
        ], 400);
    }

    throw $e;
}
```

---

### 3. Authentication Errors

**Error:**
```
AuthenticationFailed: Invalid OAuth credentials
Token expired
```

**Cause:**
- Refresh token expired (100 days of inactivity)
- Invalid access token
- QuickBooks connection deleted

**Solution:**
```php
try {
    $qbo->set_user($user);
    $customers = $qbo->get_all_customers();
} catch (Exception $e) {
    if (str_contains($e->getMessage(), 'AuthenticationFailed')) {
        // Delete expired connection
        QboAccessKey::where('user_id', $user->id)
            ->where('org_id', $user->active_org->id)
            ->delete();

        return redirect('/quickbooks/login')
            ->with('error', 'QuickBooks connection expired. Please reconnect.');
    }

    throw $e;
}
```

**See:** `patterns/token-refresh.md` for token management

---

### 4. Rate Limit Errors

**Error:**
```
Rate limit exceeded
ThrottleException
```

**Cause:** Too many API requests in short period

**QuickBooks Limits:**
- 500 requests per minute per app
- 1000 requests per minute per company

**Solution:**
```php
try {
    $result = $qbo->create_invoice($data);
} catch (Exception $e) {
    if (str_contains($e->getMessage(), 'Rate limit')) {
        // Wait and retry with exponential backoff
        sleep(2);

        try {
            $result = $qbo->create_invoice($data);
        } catch (Exception $e2) {
            LogService::store(
                'QBO Rate Limit Exceeded',
                "Rate limit hit even after retry: {$e2->getMessage()}"
            );

            return response()->json([
                'error' => 'QuickBooks is temporarily unavailable. Please try again in a moment.'
            ], 429);
        }
    } else {
        throw $e;
    }
}
```

---

### 5. Not Found Errors

**Error:**
```
Entity not found: Customer with Id='123' not found
```

**Cause:** Entity doesn't exist in QuickBooks

**Solution:**
```php
$customer = $qbo->get_customer($customerId);

if (!$customer) {
    return response()->json([
        'error' => 'Customer not found in QuickBooks'
    ], 404);
}
```

---

## Error Handling Pattern

### Try-Catch with Logging

```php
try {
    // QuickBooks operation
    $invoice = $qbo->create_invoice($data);

    // Log success
    LogService::store(
        'QBO Invoice Created',
        "Invoice #{$invoice->DocNumber} created"
    );

    return $invoice;

} catch (Exception $e) {
    // Log error
    LogService::store(
        'QBO Invoice Creation Failed',
        "Error: {$e->getMessage()}\n" .
        "Data: " . json_encode($data)
    );

    // Handle specific errors
    if (str_contains($e->getMessage(), 'ValidationFault')) {
        return response()->json(['error' => 'Invalid data'], 400);
    }

    if (str_contains($e->getMessage(), 'Stale object')) {
        // Retry logic
    }

    if (str_contains($e->getMessage(), 'AuthenticationFailed')) {
        return redirect('/quickbooks/login');
    }

    // Re-throw unknown errors
    throw $e;
}
```

---

## Validation Before API Calls

### Prevent Errors Early

```php
// ✅ CORRECT - Validate before API call
if (!isset($data['customer_id'])) {
    return response()->json(['error' => 'Customer ID required'], 400);
}

if (!isset($data['line_items']) || empty($data['line_items'])) {
    return response()->json(['error' => 'Line items required'], 400);
}

// Now safe to call API
$invoice = $qbo->create_invoice($data);
```

```php
// ❌ WRONG - Let API fail with validation error
$invoice = $qbo->create_invoice($data);  // Will fail if data invalid
```

---

## Error Response Format

### API Response

```php
// Success
return response()->json([
    'success' => true,
    'data' => $invoice
]);

// Error
return response()->json([
    'success' => false,
    'error' => 'Invoice creation failed',
    'details' => $e->getMessage()
], 400);
```

### Redirect with Flash

```php
// Success
return redirect('/quickbooks/invoices')
    ->with('message', 'Invoice created successfully');

// Error
return redirect()->back()
    ->with('error', 'Failed to create invoice: ' . $e->getMessage())
    ->withInput();
```

---

## Logging Errors

### Complete Error Information

```php
LogService::store(
    'QBO Operation Failed',
    "Operation: create_invoice\n" .
    "Error: {$e->getMessage()}\n" .
    "Error Code: {$e->getCode()}\n" .
    "Data: " . json_encode($data) . "\n" .
    "Stack Trace: {$e->getTraceAsString()}"
);
```

**See:** `patterns/logging.md` for logging patterns

---

## Testing Error Handling

### Simulate Errors

```php
// Test SyncToken error
$invoice = $qbo->get_invoice('123');
$invoice->SyncToken = '999';  // Wrong SyncToken
$qbo->dataService->Update($invoice);  // Should fail

// Test validation error
$data = ['customer_id' => 'invalid'];  // Invalid customer
$qbo->create_invoice($data);  // Should fail

// Test not found error
$customer = $qbo->get_customer('999999');  // Should return null
```

---

## Best Practices

✅ **ALWAYS wrap QuickBooks operations in try-catch**
✅ **ALWAYS log errors with full context**
✅ **ALWAYS validate data before API calls**
✅ **ALWAYS handle specific error types**
✅ **ALWAYS provide user-friendly error messages**

❌ **NEVER ignore exceptions**
❌ **NEVER expose raw API errors to users**
❌ **NEVER skip logging errors**
❌ **NEVER assume API calls will succeed**

---

## Related Patterns

- `patterns/syncing.md` - SyncToken error handling
- `patterns/token-refresh.md` - Authentication error handling
- `patterns/logging.md` - Error logging patterns
