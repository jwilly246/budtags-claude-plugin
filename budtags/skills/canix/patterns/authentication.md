# Canix API Authentication

## API Key Setup

Canix uses API key authentication via a custom HTTP header.

### Header Format

```
X-API-KEY: {your_api_key}
```

**This is NOT a Bearer token or Authorization header.** The key goes in the `X-API-KEY` header directly.

### Key Generation

Generate API keys at: `https://app.canix.com/company/api`

Keys are company-scoped — all API operations return data for the company associated with the key.

### Base URL

```
https://api.canix.com/api/v1
```

All endpoint paths are relative to this base URL.

---

## BudTags Storage Pattern

Canix API keys are stored in the `secrets` table using the same pattern as LeafLink and Metrc:

```php
// Lookup the secret type
$canix_type_id = SecretType::lookup('Canix');

// Store key (org-wide)
Secret::create([
    'organization_id' => $org->id,
    'secret_type_id'  => $canix_type_id,
    'part1'           => $api_key,
]);

// Store key (facility-scoped)
Secret::create([
    'organization_id'   => $org->id,
    'secret_type_id'    => $canix_type_id,
    'metrc_facility_id' => $facility_id,
    'part1'             => $api_key,
]);
```

### Key Resolution Priority (in CanixApi)

1. Explicitly set key via `set_key(string)` (CLI/testing)
2. Facility-scoped key via `for_facility(int)` → secrets table lookup
3. Org-level key from user's active organization
4. Throws `Exception` if none found

---

## Laravel HTTP Client Example

```php
$response = Http::withHeaders([
    'X-API-KEY' => $this->resolve_key(),
    'Accept'    => 'application/json',
])->get('https://api.canix.com/api/v1/sales_orders', [
    'limit'  => 100,
    'offset' => 0,
]);
```

---

## Common Auth Errors

| Code | Meaning | Resolution |
|------|---------|------------|
| 401 | Not authenticated | API key missing or invalid |
| 403 | Access denied | Key doesn't have permission for this resource |

---

**See:** `patterns/facility-scoping.md` for how facility_id interacts with API key scope
