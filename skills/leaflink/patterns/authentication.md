# LeafLink API Authentication

API key setup, headers, and token types for LeafLink Marketplace V2 API.

---

## API Key Types

LeafLink supports two authentication methods:

### 1. Application API Key (Recommended)

```
Authorization: App {API_KEY}
```

**Characteristics:**
- Scoped to a specific company
- More secure and controlled
- Better for integrations
- Explicitly granted permissions

**Example:**
```php
$headers = [
    'Authorization' => 'App MY_API_KEY_HERE',
    'Accept' => 'application/json'
];
```

### 2. User Token (Legacy)

```
Authorization: Token {USER_TOKEN}
```

**Characteristics:**
- Scoped to user's companies
- Broader access
- Supports multi-company scenarios
- Legacy method (still works but not recommended for new integrations)

---

## Storage in BudTags

API keys are stored per-organization in the `Secret` model:

```php
Schema:
- user_id (foreign key)
- org_id (foreign key)
- type ('leaflink')
- part1 (encrypted API key)
- active (boolean)
- description (nullable string)
```

---

## Retrieving API Key

```php
// In LeafLinkApi service
public function headers() {
    $secret = $this->api_key ?? request()->user()->leaf_link_key?->part1 ?? null;

    if (!$secret) {
        throw new Exception('no active leaf-link key found for current user');
    }

    return [
        'Authorization' => 'App ' . $secret,
        'Accept' => 'application/json',
    ];
}
```

---

## Common Authentication Errors

### 401 Unauthorized

**Cause**: Missing or invalid API key

**Solution**:
- Verify API key is correct
- Check that API key is active in LeafLink
- Ensure proper header format: `Authorization: App {KEY}`

### 403 Forbidden

**Cause**: API key doesn't have permission for requested resource

**Solution**:
- Verify company context matches resource
- Check API key permissions in LeafLink admin
- Ensure company type (seller vs buyer) has access to endpoint

---

## Best Practices

✅ **Do:**
- Store API keys encrypted in database
- Use Application API Keys for integrations
- Verify API key on service initialization
- Handle missing key errors gracefully

❌ **Don't:**
- Hard-code API keys in source code
- Share API keys across organizations
- Use User Tokens for new integrations
- Expose API keys in logs or error messages
