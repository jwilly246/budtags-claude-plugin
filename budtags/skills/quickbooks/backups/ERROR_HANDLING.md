# QuickBooks Error Handling Guide

Common errors, causes, and solutions for QuickBooks API integration.

---

## Common Errors

### 1. SyncToken Mismatch / Stale Object Error

**Error Message:**
```
Stale Object Error: You and QuickBooks_Name are working on this at the same time. QuickBooks_Name has already updated it. Save this as something else, or close the transaction and open it again.
```

**Cause:**
- Trying to update an entity with an outdated SyncToken
- Entity was modified elsewhere after you fetched it

**Solution:**
```php
// ✅ CORRECT - Always fetch latest before updating
$invoice = $qbo->get_invoice($invoiceId);
// Now invoice has current SyncToken

$updated = $qbo->update_invoice([
    'id' => $invoiceId,
    'customer_memo' => 'Updated memo',
    'line_items' => /* ... */
]);
```

**Note:** The `update_invoice()` and `update_customer()` methods in `QuickBooksApi` already handle this automatically by fetching the latest entity first.

---

### 2. Authentication / Token Errors

#### Error: "Invalid access token"

**Cause:** Access token expired

**Solution:**
- Auto-refresh handles this automatically
- If manual refresh needed:
```php
$qbo->refresh_token();
```

#### Error: "Invalid refresh token"

**Cause:** Refresh token expired (60 days of no use)

**Solution:**
```php
// Refresh token expired, must re-authorize
$this->access_key->delete();

return redirect('/quickbooks/login')
    ->with('error', 'QuickBooks connection expired. Please reconnect.');
```

#### Error: "Unauthorized / 401"

**Causes:**
1. No QuickBooks connection exists
2. Token expired
3. Wrong company (realm_id mismatch)

**Solution:**
```php
// Check if connected
$hasConnection = QboAccessKey::where('user_id', $user->id)
    ->where('org_id', $user->active_org->id)
    ->exists();

if (!$hasConnection) {
    return redirect('/quickbooks/login');
}
```

---

### 3. Validation Errors

#### Error: "Required parameter is missing"

**Common Missing Fields:**
- Invoice: `CustomerRef`, `Line` (at least one line item required)
- Payment: `CustomerRef`, linked transaction reference
- Customer: `DisplayName`

**Solution:**
```php
// Validate before API call
$validator = Validator::make($request->all(), [
    'customer_id' => 'required',
    'line_items' => 'required|array|min:1',
    'line_items.*.item_id' => 'required',
    'line_items.*.quantity' => 'required|numeric|min:0.01',
    'line_items.*.unit_price' => 'required|numeric|min:0',
]);

if ($validator->fails()) {
    return redirect()->back()->withErrors($validator);
}
```

#### Error: "Invalid Reference"

**Causes:**
- Customer ID doesn't exist
- Item ID doesn't exist or is inactive
- Account ID doesn't exist

**Solution:**
```php
// Verify customer exists
$customer = $qbo->get_customer($customerId);
if (!$customer) {
    throw new \Exception("Customer not found in QuickBooks");
}

// Verify all items exist
$items = $qbo->get_items_cached();
$itemIds = collect($items)->pluck('Id')->toArray();

foreach ($lineItems as $line) {
    if (!in_array($line['item_id'], $itemIds)) {
        throw new \Exception("Item {$line['item_id']} not found");
    }
}
```

---

### 4. Business Logic Errors

#### Error: "Cannot modify paid invoice"

**Cause:** Trying to update invoice that has payments applied

**Solution:**
```php
$invoice = $qbo->get_invoice($invoiceId);

if ($invoice->Balance < $invoice->TotalAmt) {
    throw new \Exception("Cannot modify invoice with payments applied. Create a credit memo instead.");
}
```

#### Error: "Payment exceeds balance"

**Cause:** Trying to record payment larger than invoice balance

**Solution:**
```php
$invoice = $qbo->get_invoice($invoiceId);

if ($paymentAmount > $invoice->Balance) {
    throw new \Exception("Payment amount (\${$paymentAmount}) exceeds invoice balance (\${$invoice->Balance})");
}
```

#### Error: "Insufficient credit balance"

**Cause:** Trying to apply more credit than available

**Solution:**
```php
$creditMemo = $qbo->get_credit_memo($creditMemoId);

if ($amount > $creditMemo->Balance) {
    throw new \Exception("Only \${$creditMemo->Balance} available on this credit memo");
}
```

---

### 5. Connection / Network Errors

#### Error: "Timeout / Connection refused"

**Causes:**
1. QuickBooks API is down
2. Network connectivity issues
3. Firewall blocking requests

**Solution:**
```php
try {
    $invoice = $qbo->create_invoice($data);
} catch (\Exception $e) {
    if (str_contains($e->getMessage(), 'timeout') || str_contains($e->getMessage(), 'connection')) {
        LogService::store('QBO Connection Error', $e->getMessage());
        return redirect()->back()->with('error', 'QuickBooks is temporarily unavailable. Please try again.');
    }

    throw $e;
}
```

---

### 6. Rate Limiting

#### Error: "Rate limit exceeded"

**Cause:** Too many API requests in short time

**QuickBooks Limits:**
- 500 requests per minute per company
- 5000 requests per day per app

**Solution:**
```php
// Implement exponential backoff
$maxRetries = 3;
$attempt = 0;

while ($attempt < $maxRetries) {
    try {
        $result = $qbo->create_invoice($data);
        break; // Success
    } catch (\Exception $e) {
        if (str_contains($e->getMessage(), 'rate limit')) {
            $attempt++;
            $waitSeconds = pow(2, $attempt); // 2, 4, 8 seconds
            sleep($waitSeconds);
        } else {
            throw $e;
        }
    }
}
```

**Best Practices:**
- Cache GET requests when possible
- Batch operations when possible
- Use `get_items_cached()` instead of repeated `get_items()`

---

## Error Handling Patterns

### Pattern 1: Try-Catch with Logging

```php
try {
    $invoice = $qbo->create_invoice($data);

    LogService::store(
        'QBO Invoice Created',
        "Invoice #{$invoice->DocNumber} created for customer {$invoice->CustomerRef->name}"
    );

    return redirect()->back()->with('success', 'Invoice created');
} catch (\Exception $e) {
    LogService::store(
        'QBO Invoice Creation Failed',
        "Error: {$e->getMessage()}\nData: " . json_encode($data, JSON_PRETTY_PRINT)
    );

    return redirect()->back()->with('error', 'Failed to create invoice: ' . $e->getMessage());
}
```

---

### Pattern 2: Validation Before API Call

```php
// Validate locally before expensive API call
$customer = $qbo->get_customer($customerId);
if (!$customer) {
    return redirect()->back()->withErrors(['customer_id' => 'Customer not found in QuickBooks']);
}

if (!$customer->Active) {
    return redirect()->back()->withErrors(['customer_id' => 'Customer is inactive']);
}

// Now safe to create invoice
$invoice = $qbo->create_invoice($data);
```

---

### Pattern 3: Graceful Degradation

```php
try {
    $items = $qbo->get_items_cached();
} catch (\Exception $e) {
    // Log error but don't block page
    LogService::store('QBO Items Fetch Failed', $e->getMessage());

    // Use stale cache or empty array
    $items = Cache::get("qbo_items_{$org->id}_stale") ?? [];
}
```

---

## Debugging Errors

### Enable Detailed Logging

```php
// In QuickBooksApi methods
public function create_invoice(array $data): object
{
    Log::info('QBO Create Invoice Request', [
        'user_id' => auth()->id(),
        'org_id' => auth()->user()->active_org->id,
        'data' => $data
    ]);

    try {
        $invoice = /* ... API call ... */;

        Log::info('QBO Create Invoice Success', [
            'invoice_id' => $invoice->Id,
            'doc_number' => $invoice->DocNumber
        ]);

        return $invoice;
    } catch (\Exception $e) {
        Log::error('QBO Create Invoice Failed', [
            'error' => $e->getMessage(),
            'trace' => $e->getTraceAsString(),
            'data' => $data
        ]);

        throw $e;
    }
}
```

---

### Check QuickBooks API Logs

**In QuickBooks Online:**
1. Go to Settings → Audit Log
2. Filter by "API" activity
3. Check for failed API calls

---

### Check Laravel Logs

```bash
# View recent logs
tail -f storage/logs/laravel.log

# Search for QuickBooks errors
grep "QBO" storage/logs/laravel.log | grep "error"
```

---

### Check Database

```sql
-- Check access key expiration
SELECT
    user_id,
    org_id,
    realm_id,
    expires_at,
    CASE
        WHEN expires_at < NOW() THEN 'EXPIRED'
        WHEN expires_at < DATE_ADD(NOW(), INTERVAL 5 MINUTE) THEN 'EXPIRING SOON'
        ELSE 'VALID'
    END as status
FROM qbo_access_keys
WHERE user_id = ?;

-- Check sync logs
SELECT *
FROM qbo_sync_logs
WHERE org_id = ?
ORDER BY created_at DESC
LIMIT 10;
```

---

## Error Codes Reference

### QuickBooks API Error Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 400 | Bad Request | Invalid data, validation error |
| 401 | Unauthorized | Invalid or expired token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Entity doesn't exist |
| 500 | Internal Server Error | QuickBooks server error |
| 503 | Service Unavailable | QuickBooks maintenance |

---

## Preventing Errors

### Best Practices

1. **Always use try-catch** around QuickBooks API calls
2. **Validate data locally** before API calls
3. **Use LogService** for all QuickBooks operations
4. **Cache GET requests** to reduce API calls
5. **Fetch latest entity** before updates
6. **Check balances** before payments/credits
7. **Verify references** (customer, item, account exist)
8. **Handle token expiration** gracefully
9. **Use typed data** (TypeScript types)
10. **Monitor sync logs** for recurring errors

---

## Next Steps

- **[OPERATIONS_CATALOG.md](OPERATIONS_CATALOG.md)** - All available operations
- **[CODE_EXAMPLES.md](CODE_EXAMPLES.md)** - Working code examples
- **[WORKFLOWS/](WORKFLOWS/)** - Step-by-step workflow guides
