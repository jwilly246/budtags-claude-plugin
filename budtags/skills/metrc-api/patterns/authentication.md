# Authentication

Metrc API uses API key authentication with license numbers for authorization.

---

## API Key Setup

### 1. Obtain API Key

- Log into Metrc web interface
- Navigate to Admin > Integrations
- Generate API key for your facility
- **Keep key secure** - treat like a password!

### 2. Base URL by State

Metrc uses different base URLs per state:

| State | Base URL |
|-------|----------|
| California | `https://api-ca.metrc.com` |
| Colorado | `https://api-co.metrc.com` |
| Michigan | `https://api-mi.metrc.com` |
| Massachusetts | `https://api-ma.metrc.com` |
| Oregon | `https://api-or.metrc.com` |
| (Other states) | `https://api-{state}.metrc.com` |

**Sandbox/Testing**: `https://sandbox-api-ca.metrc.com` (replace CA with your state)

---

## Required Headers

All API requests require:

```php
$headers = [
    'Content-Type' => 'application/json',
    'Authorization' => 'Basic ' . base64_encode("{$apiKey}:"),
];
```

**Important**: API key goes in username, password is empty!

---

## BudTags MetrcApi Usage

BudTags wraps all Metrc API calls in `App\Services\Api\MetrcApi`. The `get()`/`post()` methods are **protected** — they enforce caching, rate limiting, and metrics internally. Always use the 147+ public methods instead.

### Standard Controller Setup

```php
// Resolve from container (never use `new MetrcApi()`)
$api = app(\App\Services\Api\MetrcApi::class);

// CRITICAL: Always set user context before any API call
$api->set_user(request()->user());

// License and facility from session
$license = session('license');
$facility = session('facility');
```

### Using Public Methods (Preferred)

```php
// ✅ Use dedicated public methods — handles caching, rate limits, pagination
$packages = $api->one_day_of_packages($facility, now()->format('Y-m-d'));
$strains = $api->strains($facility);
$plants = $api->one_day_of_plants($facility, now()->format('Y-m-d'));
$transfers = $api->fetch_transfers_bulk($facility, 'incoming');

// For write operations
$api->packages_adjust($license, $adjustments);
$api->change_plant_growth_phase($license, $phaseChanges);
```

### Raw Endpoint Calls (When No Public Method Exists)

```php
// Some endpoints don't have dedicated public methods
// Use the raw get/post through available wrapper methods
$labResults = $api->get("/packages/v2/{$packageId}/labtestresults", [
    'licenseNumber' => $license,
]);
```

---

## License Number Requirement

**Almost ALL endpoints require `licenseNumber` as a query parameter:**

```php
// ✅ CORRECT
$api->get("/packages/v2/active", [
    'licenseNumber' => 'AU-R-000001'
]);

// ❌ WRONG - will fail!
$api->get("/packages/v2/active");
```

**Exception**: `/facilities/v2/` endpoint doesn't require licenseNumber.

---

## Environment Configuration

```php
// config/metrc.php
return [
    'state' => env('METRC_STATE', 'ca'),
    'environment' => env('METRC_ENVIRONMENT', 'production'), // or 'sandbox'
];

// .env
METRC_STATE=ca
METRC_ENVIRONMENT=sandbox
```

---

## Security Best Practices

1. **Never commit API keys** to version control
2. **Store in database encrypted** or use Laravel secrets
3. **Use environment variables** for base URLs
4. **Implement rate limiting** on your end
5. **Log API calls** for debugging (but not keys!)
6. **Rotate keys periodically**
7. **Use HTTPS only** - never plain HTTP

---

## Testing Authentication

```php
// Test if API key is valid
try {
    $facilities = $api->get("/facilities/v2/");
    echo "Authentication successful! Found " . count($facilities) . " facilities.";
} catch (\Exception $e) {
    echo "Authentication failed: " . $e->getMessage();
}
```

---

## Common Authentication Errors

### 401 Unauthorized

**Causes**:
- Invalid API key
- API key not base64 encoded correctly
- Missing Authorization header

**Fix**:
```php
// Ensure proper encoding
$auth = base64_encode("{$apiKey}:"); // Note the colon!
```

### 403 Forbidden

**Causes**:
- API key valid, but license doesn't have access to endpoint
- License type mismatch (e.g., retail accessing plant endpoints)

**Fix**: Check `patterns/license-types.md` for compatibility

---

## Summary

✅ **Use Basic Auth** with API key as username
✅ **Include licenseNumber** in query params (except `/facilities/v2/`)
✅ **Base URL varies by state** (`api-{state}.metrc.com`)
✅ **Secure API keys** - never expose publicly
✅ **Test in sandbox** before production
