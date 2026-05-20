# Pattern — Authentication

Distru's Public API v1 uses **Bearer JWT** authentication. A single token per API user, set in the `Authorization` request header.

## Header Format

```http
Authorization: Bearer eyJhbGciOiJI...
```

This is **different** from the other integrations in Budtags:

| Platform | Header |
|----------|--------|
| Canix | `X-API-KEY: {key}` |
| LeafLink | `Authorization: App {token}` |
| **Distru** | **`Authorization: Bearer {jwt}`** |

Hard-coding the wrong header is the #1 cause of 401 responses during initial integration.

## Generating an API Key

1. The Distru account must have **API access enabled** by a Distru account rep (not self-service).
2. Once enabled, an admin user navigates to **Settings → Integrations → Distru API → Create API Key**.
3. The generated token is a JWT — **show once, store immediately**.

## Storage in Budtags

Mirror the Canix and LeafLink storage pattern:

1. Add a `Distru` case to `app/Enums/SecretType.php`.
2. Add a `distru_key` accessor on the `User` model that returns the org's Secret of type `Distru`.
3. The `DistruApi` client resolves the key via `get_org_level_key($user)` — same shape as `CanixApi`.

```php
// User model accessor (mirrors canix_key)
public function getDistruKeyAttribute(): ?Secret
{
    return $this->active_org
        ?->secrets()
        ->where('type', SecretType::Distru->value)
        ->first();
}
```

## Scoping

- Tokens are **per-user**, not per-organization. Multiple Distru users → multiple tokens.
- Distru filters API results by the token-holder's **team permissions** — a key may silently see fewer records than another key in the same Distru org. This is not a Budtags bug; it is a Distru permission filter.
- Token **expiration**: JWTs typically have a built-in `exp`. Distru docs do not specify rotation cadence; assume tokens can be revoked at any time and handle 401 as a re-auth signal.

## Code reference — `DistruApi` skeleton

```php
namespace App\Services\Api;

class DistruApi extends BaseMarketplaceApi
{
    protected string $base_url = 'https://app.distru.com/public/v1';

    protected function auth_headers(): array
    {
        return ['Authorization' => 'Bearer ' . $this->get_org_level_key($this->user)?->part1];
    }
}
```

## Common Auth Errors

- **401 Unauthorized** — wrong header (`X-API-KEY` or `App {token}` instead of `Bearer {jwt}`), expired token, or revoked token.
- **403 Forbidden** — valid token but the team permissions exclude that resource.
- **Empty `data` array on a known-populated endpoint** — possibly the team permission filter; verify with a different key.

## Cross-references

- Write patterns: `patterns/write-safety.md`
- Error handling: `patterns/error-handling.md`
