# Unleashed API Authentication

HMAC-SHA256 signing, API credentials, and header requirements.

---

## Authentication Method

Unleashed uses HMAC-SHA256 signature-based authentication. Every request must include:

1. **API ID** - Identifies the consumer
2. **Signature** - HMAC-SHA256 hash of the query string, signed with the API Key

---

## Signing Process

### Step 1: Extract Query String

Take everything after the `?` in the URL. If no query parameters, use an empty string.

```
URL: /SalesOrders?customerCode=ACME&pageSize=200
Query String: customerCode=ACME&pageSize=200

URL: /Products/abc-123-guid
Query String: (empty string)
```

### Step 2: Generate HMAC-SHA256 Hash

```php
$signature = hash_hmac('sha256', $queryString, $apiKey, true);
```

### Step 3: Base64 Encode

```php
$encoded = base64_encode($signature);
```

---

## Required Headers

| Header | Value |
|--------|-------|
| `api-auth-id` | Your API ID |
| `api-auth-signature` | `base64_encode(hash_hmac('sha256', $queryString, $apiKey, true))` |
| `Content-Type` | `application/json` |
| `Accept` | `application/json` |

---

## PHP Implementation

```php
public function build_headers(string $query_string = ''): array
{
    $api_id = config('services.unleashed.api_id');
    $api_key = config('services.unleashed.api_key');

    $signature = base64_encode(
        hash_hmac('sha256', $query_string, $api_key, true)
    );

    return [
        'api-auth-id' => $api_id,
        'api-auth-signature' => $signature,
        'Content-Type' => 'application/json',
        'Accept' => 'application/json',
    ];
}
```

---

## Storage in BudTags

API credentials stored per-organization in the `Secret` model:

```php
Schema:
- user_id (foreign key)
- org_id (foreign key)
- type ('unleashed')
- part1 (encrypted API ID)
- part2 (encrypted API Key)
- active (boolean)
- description (nullable string)
```

---

## Common Auth Errors

### 401 Unauthorized
**Cause**: Invalid API ID or signature mismatch
**Fix**: Verify the query string used for signing matches the actual URL query string exactly. Check that the API Key is correct.

### Signature Mismatch
**Cause**: Query string in signature calculation differs from URL
**Fix**: Ensure you're signing the raw query string without the leading `?`. URL-encoded characters must match.

---

## Security Best Practices

- Store API credentials encrypted (BudTags Secret model)
- Never log API keys or signatures
- Use config() to access credentials, never env() directly
- Rotate keys if compromised
- Use HTTPS only (enforced by API)
