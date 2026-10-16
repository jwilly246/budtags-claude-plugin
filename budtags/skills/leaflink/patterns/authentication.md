# LeafLink API Authentication

API key setup, headers, token types and rate limits for LeafLink Marketplace V2 API.

"Docs" = official doc text copies in `~/budtags-audits/2026-10-15/leaflink_docs_gap_audit/text/` (api_authorization.txt, gs.txt).

---

## API Key Types

### 1. App Token (what Budtags uses)

```
Authorization: App {API_KEY}
```

"An App token will allow access via API to the single company in which the App token was created" (docs). "Note the single space between App and api_key." For an integration offered to more than one LeafLink user, the docs recommend an App token.

```php
$headers = [
    'Authorization' => 'App ' . $apiKey,
    'Accept' => 'application/json',
];
```

### 2. User Token

"A User-level token will allow the user to have access to all companies via API that the user is permissioned within the LeafLink Platform" (docs). Every list call made with a User token must filter by `company`, and some `company` filters are ignored (`company-scoping.md`).

---

## Rate Limits

- "API access is limited to 300 requests/minute, with a burst rate of 1000 requests/minute. Rate limits are tied to the owner of the API key used. The owner is whomever generated the API key originally." Over the limit: 429 (docs).
- So two orgs whose keys one LeafLink user generated share ONE 300/min budget.
- No rate-limit headers are sent on responses, so there is no warning before a 429. Verified 2026-10-16 (sandbox, `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/r2_t8_t9_console.txt` "response headers").

---

## Environments

| Host | Use |
|------|-----|
| `www.leaflink.com/api/v2/` | Production |
| `sandbox.leaflink.com/api/v2/` | Sandbox: "a clone of live LeafLink data and code, updated and reset nightly at 12:00am EST"; a key made in prod reaches the sandbox the following day (docs, gs.txt) |

Sandbox facts proven 2026-10-16 (no webhooks to prod, no reset that night): `verified-behavior.md`.

---

## Storage in BudTags

API keys are stored per organization in the `Secret` model:

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
// app/Services/Api/LeafLinkApi.php (base URL: config('budtags.leaf_link_base_url'))
protected function build_auth_headers(string $token): array
{
    return [
        'Authorization' => 'App '.$token,
        'Accept' => 'application/json',
        'Content-Type' => 'application/json',
    ];
}

// Callers set the key explicitly, e.g.
$api->set_key($user->leaf_link_key->part1);
```

---

## Common Authentication Errors

### 401 Unauthorized

**Cause**: Missing or invalid API key

**Solution**:
- Verify the key is correct and active in LeafLink
- Header format: `Authorization: App {KEY}` (one space)
- A key made in prod today reaches the sandbox only the next day (docs)

### 403 Forbidden

**Cause**: The key lacks permission for the resource

**Solution**:
- Verify company context matches the resource
- Check the key's permissions in LeafLink

---

## Best Practices

✅ **Do:**
- Store API keys encrypted
- Use App tokens for integrations
- Budget rate limits per key OWNER, not per org

❌ **Don't:**
- Hard-code API keys
- Share one key across organizations
- Expose API keys in logs or error messages
