# QuickBooks Token Refresh Pattern

**Pattern:** Refresh-on-expiry during service setup
**Trigger:** `set_service()` / `set_service_from_token()` when `now() >= expires_at`
**On failure:** Token row is DELETED and the exception re-thrown

---

## Overview

QuickBooks access tokens expire after 1 hour. The integration refreshes an expired token once, at service-setup time, using the stored refresh token.

**Key Concepts:**
- Access token lifespan: 1 hour
- Refresh token: 100-day inactivity rule PLUS a 5-year hard cap (since Jan 2026 - see below)
- Refresh happens when the service is configured, NOT before every API call
- Refresh only fires when the token is ALREADY expired (no early-refresh buffer)
- A failed refresh deletes the token row - recovery is a human re-auth

---

## Where Refresh Happens

All entry points funnel through `set_service_from_token()` (`app/Services/Api/QuickBooksApi.php`):

```php
public function set_service(User $user): self {
    $accessToken = $user->qbo_access_key_for_org;

    return $this->set_service_from_token($accessToken);
}

public function set_service_from_token(?QboAccessKey $accessToken): self {
    // Guard: token record with empty credentials is corrupt - delete it
    if ($accessToken && (empty($accessToken->access_key) || empty($accessToken->refresh_key))) {
        LogService::store('QuickBooks Corrupt Token Cleaned', "Token ID {$accessToken->id} had empty credentials — deleting.");
        $accessToken->delete();
        $accessToken = null;
    }

    $this->service = $accessToken ? self::make_service($accessToken) : self::make_service();

    if ($accessToken && now() >= $accessToken->expires_at) {
        try {
            $this->refresh_token($accessToken);
        } catch (\Exception $e) {
            LogService::store('QuickBooks Token Refresh Failed', "Error: {$e->getMessage()}");
            $accessToken->delete();   // dead chain - do not hammer it
            throw $e;                 // caller handles (usually redirect to re-auth)
        }
    }

    return $this;
}
```

**Important details:**

- The check is `now() >= expires_at` - refresh fires only when the token is already
  expired. There is NO pre-expiry buffer. A token that expires mid-request is not
  protected against; in practice requests complete in seconds and this has not been
  an issue.
- Refresh happens once per `QuickBooksApi` setup, not per API call. A long-running
  process that holds one instance past the 1-hour mark will start failing with
  auth errors; construct a fresh instance (or re-call `set_service`) instead.
- A corrupt token row (empty `access_key`/`refresh_key`) is deleted on sight and
  treated as "no connection".

---

## The Refresh Itself

```php
public function refresh_token(QboAccessKey &$accessToken): QboAccessKey {
    $OAuth2LoginHelper = (object) $this->service->getOAuth2LoginHelper();
    $refreshedAccessTokenObj = $OAuth2LoginHelper->refreshToken();
    $this->service->updateOAuth2Token($refreshedAccessTokenObj);

    // save to our database:
    $accessToken->update([
        'expires_at' => Carbon::parse($refreshedAccessTokenObj->getAccessTokenExpiresAt()),
        'access_key' => $refreshedAccessTokenObj->getAccessToken(),
        'refresh_key' => $refreshedAccessTokenObj->getRefreshToken(),
    ]);

    return $accessToken;
}
```

- The SDK's `OAuth2LoginHelper::refreshToken()` uses the refresh token already
  configured on the service (from `make_service($accessToken)`).
- ALL THREE fields are persisted: new access token, new refresh token, new expiry.
  Dropping the refresh token here would kill the chain (see rotation section).
- `getAccessTokenExpiresAt()` returns a datetime string - it is parsed with
  `Carbon::parse()`, not added as seconds.

---

## Token Lifespan

### Access Token

**Lifespan:** 1 hour (3600 seconds)
**Stored:** `expires_at` timestamp in `qbo_access_keys`
**Refresh:** At service setup when expired

### Refresh Token

**Lifespan:** TWO independent limits apply:
1. **100-day inactivity rule** (rolling - each successful refresh restarts this clock)
2. **5-year hard cap** (Intuit policy change, production since 2026-01-27) - the
   5-year clock starts at initial authorization and NEVER resets on refresh

**Stored:** `refresh_key` column
**Usage:** Only during token refresh
**Renewal:** Store whatever refresh token the refresh response returns - it rotates

**Critical:** If the refresh token dies (100 days without a successful refresh, OR
the 5-year cap), the user must re-authorize via the OAuth flow at `/quickbooks/auth`.

**5-year cap timeline:** for apps on the `com.intuit.quickbooks.accounting` scope
(BudTags is one), the earliest hard expirations begin **October 2028**. QBO notifies
customers in-product 30 days before expiry and by email 7 days before. Intuit also
added an optional request header `x-include-refresh-token-hard-expires-in: true` on
the token endpoint that returns `x_refresh_token_hard_expires_in` (seconds left of
the 5-year window); the PHP SDK exposes this from v6.2.4 via
`includeRefreshTokenHardExpiresIn` / `refreshTokenHardExpiresIn`. BudTags does not
consume it yet - a scheduled re-auth will eventually be needed regardless.
See `PLATFORM_CHANGES.md` for the full policy change.

---

## Error Handling

### Refresh Fails (`invalid_grant`, expired chain)

The integration does NOT retry. `set_service_from_token()` logs
`QuickBooks Token Refresh Failed`, **deletes the token row**, and re-throws.
Callers use `QuickBooksApi::is_oauth_error($e)` to distinguish auth failures
from other errors and redirect the user to reconnect:

```php
public static function is_oauth_error(\Exception $e): bool {
    $message = $e->getMessage();

    return str_contains($message, 'invalid_grant')
        || str_contains($message, 'token')
        || str_contains($message, '401')
        || str_contains($message, 'Unauthorized');
}
```

**User action required:** re-auth through the OAuth flow. There is no automatic
recovery from a dead refresh chain, by design.

---

## Monitoring

```sql
SELECT * FROM logs
WHERE title IN ('QuickBooks Token Refresh Failed', 'QuickBooks Corrupt Token Cleaned')
ORDER BY created_at DESC
LIMIT 10;
```

The daily invoice sync logs `QBO Invoice Sync Auth Failed` as a KEYED row (one live
row, repeat-bumped) while its service-user token is dead - see
`patterns/billing-invoice-sync.md`.

---

## Testing Token Refresh

```php
// In tinker: force expiry, then set up the service
$accessKey = QboAccessKey::first();
$accessKey->update(['expires_at' => now()->subMinute()]);

$qbo = new QuickBooksApi();
$qbo->set_service($user);          // refresh fires here
$customers = $qbo->get_all_customers();
```

---

## Best Practices

✅ **ALWAYS store all three fields after refresh** - access token, refresh token, expiry
✅ **ALWAYS use `is_oauth_error()` to classify failures** - then redirect to re-auth
✅ **ALWAYS construct a fresh service for long-running work** - refresh only fires at setup
✅ **ALWAYS log refresh failures via LogService**

❌ **NEVER retry a failed refresh in a loop** - a dead chain stays dead; the row is deleted for a reason
❌ **NEVER copy a token chain to another environment** - see incident notes below
❌ **NEVER store only the access token** - the rotated refresh token must be saved too

---

## Refresh Token Rotation

**QuickBooks Security:** Each refresh returns a NEW refresh token

**Before Refresh:**
```
access_token: abc123 (expires in 30 minutes)
refresh_token: xyz789
```

**After Refresh:**
```
access_token: def456 (expires in 1 hour)
refresh_token: uvw012 (NEW - replaces xyz789)
```

**IMPORTANT:** Always store the NEW refresh token returned during refresh!

```php
// ✅ CORRECT - Store both new tokens
$accessToken->update([
    'access_key' => $new_access_token,
    'refresh_key' => $new_refresh_token,  // NEW token
    'expires_at' => $new_expiration
]);
```

```php
// ❌ WRONG - Only updating access token
$accessToken->update([
    'access_key' => $new_access_token,
    // Missing refresh_key update - old refresh token becomes invalid!
    'expires_at' => $new_expiration
]);
```

---

## Refresh-token chain gotchas (learned in production)

The refresh token ROTATES: every refresh can return a NEW refresh token, and using
a stale copy kills the whole chain with `invalid_grant`. Two real incidents:

1. **Staging clobber (fixed 2026-07-16):** staging ran `qbo:sync-invoices` with a
   copied prod token; each staging refresh rotated the chain and invalidated prod's
   copy. The scheduled command is now `environments('production')` — never let two
   environments share one token chain.
2. **`invalid_grant` on refresh deletes the token** (`QuickBooksApi::set_service_from_token`)
   — by design, so a dead chain doesn't get hammered. Recovery is always a human
   re-auth at `/quickbooks/auth`. The daily sync logs `QBO Invoice Sync Auth Failed`
   as a KEYED row (one live row, repeat-bumped) until reconnected.

The "stays fresh as long as it's used every ~90-100 days" rule holds only up to the
5-year hard cap (see Token Lifespan above) — the daily 06:00 sync keeps the
service-user chain alive until then, with the earliest possible hard expiry in
October 2028. If the chain dies BEFORE that, look for a second consumer of the same
token (another environment, a dashboard session with a stale copy), not for expiry.

**Note:** "Exception appears in converting Response to XML" is NOT a token problem —
see `patterns/error-handling.md` (SDK schema drift).

---

## Related Patterns

- `patterns/authentication.md` - Initial OAuth flow
- `patterns/multi-tenancy.md` - Organization-scoped tokens
- `patterns/billing-invoice-sync.md` - Service-user token for the daily sync
- `patterns/error-handling.md` - Handling token errors
- `categories/authentication.md` - Authentication operations
