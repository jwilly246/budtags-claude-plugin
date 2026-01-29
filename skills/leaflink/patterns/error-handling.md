# LeafLink Error Handling

HTTP status codes, common errors, and retry strategies for LeafLink Marketplace V2 API.

---

## HTTP Status Codes

| Code | Meaning | Common Causes | Action |
|------|---------|---------------|--------|
| **200** | OK | Successful GET/PATCH/PUT | Process response data |
| **201** | Created | Successful POST | Resource created successfully |
| **204** | No Content | Successful DELETE | Resource deleted successfully |
| **400** | Bad Request | Invalid parameters, missing trailing slash, validation errors | Check request format and parameters |
| **401** | Unauthorized | Missing/invalid API key | Verify API key and authorization header |
| **403** | Forbidden | No permission to access resource | Check company context and permissions |
| **404** | Not Found | Resource doesn't exist or doesn't belong to your company | Verify resource ID and company ownership |
| **429** | Too Many Requests | Rate limit exceeded | Implement exponential backoff |
| **500** | Server Error | LeafLink internal error | Retry with exponential backoff, contact support if persists |

---

## Common Errors

### 1. Missing Trailing Slash (MOST COMMON!)

**Error:**
```
400 Bad Request: "Request path must end in a slash"
```

**Cause:** Endpoint path missing trailing `/`

**Solution:**
```php
// ❌ Wrong
$api->get('/orders-received')
$api->get('/products')

// ✅ Correct
$api->get('/orders-received/')
$api->get('/products/')
```

**Prevention:** Always include `/` at end of all endpoint paths.

---

### 2. Invalid Filter Syntax

**Error:**
```
400 Bad Request: "Unknown filter: date__greater_than. Did you mean date__gte?"
```

**Cause:** Using incorrect filter operator

**Solution:**
```php
// ❌ Wrong
'date__greater_than' => '2025-01-01'
'date>' => '2025-01-01'

// ✅ Correct
'created_date__gte' => '2025-01-01'
'created_date__lte' => '2025-01-31'
```

**Reference:** Use `__gte`, `__lte`, `__in`, `__icontains`, etc.

---

### 3. Invalid Date Format

**Error:**
```
400 Bad Request: "Enter a valid date/time."
```

**Cause:** Using non-ISO 8601 date format

**Solution:**
```php
// ❌ Wrong
'order_date' => '01/15/2025'
'order_date' => '15-01-2025'

// ✅ Correct
'order_date' => '2025-01-15'
'order_date' => now()->toDateString()
```

---

### 4. Authentication Errors

**Error:**
```
401 Unauthorized: "Invalid token"
```

**Cause:** Missing or invalid API key

**Solution:**
```php
// Verify API key exists and is active
if (!$apiKey) {
    throw new Exception('LeafLink API key not configured');
}

// Ensure correct header format
$headers = [
    'Authorization' => 'App ' . $apiKey,  // Note: 'App ' prefix, not 'Bearer '
    'Accept' => 'application/json'
];
```

---

### 5. Permission/Company Context Errors

**Error:**
```
403 Forbidden: "You do not have permission to perform this action"
```

**Cause:** Resource doesn't belong to authenticated company OR company type doesn't have access

**Solution:**
```php
// Check company context
$company = $api->get('/companies/me/')->json();

if ($company['company_type'] === 'buyer') {
    // Use buyer endpoints
    $orders = $api->get('/buyer/orders/');
} else {
    // Use seller endpoints
    $orders = $api->get('/orders-received/');
}
```

---

### 6. Resource Not Found

**Error:**
```
404 Not Found
```

**Cause:** Resource ID doesn't exist OR doesn't belong to your company

**Solution:**
```php
// Always handle 404s gracefully
$response = $api->get("/orders-received/{$orderId}/");

if ($response->status() === 404) {
    LogService::store(
        'LeafLink Order Not Found',
        "Order ID {$orderId} not found or doesn't belong to this company"
    );
    return null;
}
```

---

### 7. Rate Limiting

**Error:**
```
429 Too Many Requests
```

**Cause:** Exceeded API rate limits

**Solution:** Implement exponential backoff (see retry strategy below)

---

## Error Response Format

LeafLink returns errors in JSON format:

```json
{
    "detail": "Error message describing what went wrong",
    "field_name": ["Specific field error message"],
    "another_field": ["Another error"]
}
```

**Examples:**

```json
// General error
{
    "detail": "Request path must end in a slash"
}

// Field validation errors
{
    "name": ["This field is required."],
    "price": ["Ensure this value is greater than or equal to 0."]
}

// Multiple errors
{
    "order_date": ["Enter a valid date."],
    "delivery_date": ["This field may not be null."]
}
```

---

## Retry Strategies

### Exponential Backoff for Rate Limits

```php
public function get(string $url, array $params = [], int $retries = 3) {
    $attempt = 0;

    retry:
    $response = Http::withHeaders($this->headers())
        ->get($this->url($url), $params);

    // Retry on 429 (rate limit) or 500 (server error)
    if (in_array($response->status(), [429, 500]) && $attempt < $retries) {
        $attempt++;
        $delay = pow(2, $attempt); // Exponential: 2s, 4s, 8s
        sleep($delay);

        LogService::store(
            'LeafLink API Retry',
            "Attempt {$attempt}/{$retries} after {$delay}s delay\nStatus: {$response->status()}"
        );

        goto retry;
    }

    return $response;
}
```

### Laravel HTTP Client Retry

```php
use Illuminate\Support\Facades\Http;

// Built-in retry mechanism
$response = Http::retry(3, 100, function ($exception, $request) {
    // Retry on 429 and 500 errors
    return in_array($exception->response->status(), [429, 500]);
})
->withHeaders($this->headers())
->get($this->url($url), $params);
```

---

## Error Handling Implementation

### Basic Error Handling

```php
public function fetchOrders() {
    $response = $this->api->get('/orders-received/');

    if ($response->successful()) {
        return $response->json('results');
    }

    // Log error
    LogService::store(
        'LeafLink API Error',
        "Status: {$response->status()}\n" .
        "URL: /orders-received/\n" .
        "Body: {$response->body()}"
    );

    // Handle specific status codes
    return match($response->status()) {
        401 => throw new AuthenticationException('Invalid LeafLink API key'),
        403 => throw new AuthorizationException('No access to this resource'),
        404 => [],  // Return empty array for not found
        429 => throw new TooManyRequestsException('Rate limit exceeded'),
        default => throw new ApiException('LeafLink API error: ' . $response->status())
    };
}
```

### Comprehensive Error Handling

```php
public function safeApiCall(string $method, string $url, array $data = []) {
    try {
        $response = match($method) {
            'GET' => $this->api->get($url, $data),
            'POST' => $this->api->post($url, $data),
            'PATCH' => $this->api->patch($url, $data),
            'DELETE' => $this->api->delete($url)
        };

        if (!$response->successful()) {
            $this->handleError($response, $url, $method);
            return null;
        }

        return $response->json();

    } catch (\Exception $e) {
        LogService::store(
            'LeafLink API Exception',
            "Method: {$method}\n" .
            "URL: {$url}\n" .
            "Error: {$e->getMessage()}"
        );
        return null;
    }
}

private function handleError($response, $url, $method) {
    $status = $response->status();
    $body = $response->json();

    LogService::store(
        'LeafLink API Error',
        "Method: {$method}\n" .
        "URL: {$url}\n" .
        "Status: {$status}\n" .
        "Error: " . ($body['detail'] ?? json_encode($body))
    );

    // User-friendly error messages
    $message = match($status) {
        400 => 'Invalid request. ' . ($body['detail'] ?? 'Please check your input.'),
        401 => 'Authentication failed. Please check your API key.',
        403 => 'You do not have permission to access this resource.',
        404 => 'The requested resource was not found.',
        429 => 'Too many requests. Please try again in a few moments.',
        500 => 'LeafLink server error. Please try again later.',
        default => 'An unexpected error occurred.'
    };

    session()->flash('error', $message);
}
```

---

## Best Practices

### ✅ Do:

1. **Always handle errors gracefully**
   ```php
   if ($response->successful()) {
       // Process data
   } else {
       // Handle error
   }
   ```

2. **Log all errors with context**
   ```php
   LogService::store(
       'LeafLink Error',
       "Status: {$status}\nURL: {$url}\nBody: {$body}"
   );
   ```

3. **Implement retry logic for transient errors**
   - Retry 429 (rate limit)
   - Retry 500 (server error)
   - Use exponential backoff

4. **Provide user-friendly error messages**
   ```php
   session()->flash('error', 'Unable to fetch orders. Please try again.');
   ```

5. **Validate inputs before API calls**
   ```php
   $validated = $request->validate([
       'order_date' => 'required|date|date_format:Y-m-d'
   ]);
   ```

### ❌ Don't:

1. **Expose API keys in error messages**
   ```php
   // ❌ Wrong
   throw new Exception("API error with key: {$apiKey}");

   // ✅ Correct
   throw new Exception("API authentication failed");
   ```

2. **Ignore error responses**
   ```php
   // ❌ Wrong
   $data = $api->get('/orders-received/')->json();

   // ✅ Correct
   $response = $api->get('/orders-received/');
   if ($response->successful()) {
       $data = $response->json();
   }
   ```

3. **Retry indefinitely**
   - Always set max retry attempts
   - Use exponential backoff

4. **Show technical errors to end users**
   - Log detailed errors for debugging
   - Show friendly messages to users

---

## Debugging Checklist

When encountering errors, check:

1. ✅ **Trailing slash** - All paths end with `/`
2. ✅ **API key** - Valid and active
3. ✅ **Company context** - Using correct endpoints for company type
4. ✅ **Date format** - ISO 8601 (YYYY-MM-DD)
5. ✅ **Filter syntax** - Correct operators (`__gte`, `__lte`, etc.)
6. ✅ **Resource ownership** - Resource belongs to your company
7. ✅ **Required fields** - All required fields included
8. ✅ **Network connectivity** - Can reach LeafLink API
9. ✅ **Rate limits** - Not exceeding request limits

---

## Quick Reference

```php
// Check response success
if ($response->successful()) { }
if ($response->failed()) { }
if ($response->status() === 200) { }

// Get error details
$status = $response->status();
$body = $response->json();
$detail = $response->json('detail');

// Common fixes
'/orders-received/'  // Always include trailing /
'created_date__gte'  // Use correct filter operators
'2025-01-15'         // Use ISO 8601 dates
'App ' . $apiKey     // Correct auth header format
```
