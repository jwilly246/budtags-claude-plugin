# QuickBooks OAuth 2.0 Authentication Pattern

**Pattern:** OAuth 2.0 Flow
**Scope:** Organization-scoped authentication
**Security:** Session-identified callback, tokens hidden from serialization

---

## Overview

QuickBooks uses OAuth 2.0 for authentication. Each organization has its own QuickBooks connection stored in the `QboAccessKey` model, keyed to a `(user_id, organization_id)` pair.

**Key Models:**
- `QboAccessKey` - Stores OAuth tokens per user/organization

**Routes:**
- `GET /quickbooks/login` -> `QuickBooksController::initiate_login` - Initiate OAuth flow (inside the `auth` + `has-org` + `quickbooks` group)
- `GET /quickbooks/auth` -> `QuickBooksController::set_login_tokens` - OAuth callback handler (registered OUTSIDE the auth group, `web` middleware only, because the session may not survive the cross-domain redirect)
- `POST /quickbooks/logout` -> `QuickBooksController::logout` - Disconnect QuickBooks
- Dev variants: `GET /dev/qbo/login` -> `DevController::initiate_qbo_login`, `GET /dev/qbo/auth` -> `DevController::set_qbo_token`

> There is NO `/quickbooks/callback` route. The callback is `/quickbooks/auth`.

---

## API Wrapper Signatures

Real method signatures on `App\Services\Api\QuickBooksApi` (verify against `app/Services/Api/QuickBooksApi.php`):

```php
public function oauth_begin(): RedirectResponse;                                 // redirects the user to Intuit
public function oauth_complete(User $user, string $code, string $realm): QboAccessKey;
public function set_service(User $user): self;                                   // loads $user->qbo_access_key_for_org
public function set_service_from_token(?QboAccessKey $accessToken): self;
public function refresh_token(QboAccessKey &$accessToken): QboAccessKey;
public static function is_oauth_error(\Exception $e): bool;                      // matches invalid_grant/token/401/Unauthorized
```

Service construction is handled by two privates: `service_config(array $config_overrides = []): array` builds the SDK config array, and `make_service(QboAccessKey|string $key_or_redirect = '/quickbooks/auth'): DataService` builds the `DataService`. The constructor calls `make_service()` with no token, so a fresh `QuickBooksApi` is unauthenticated until you call `set_service()` or `set_service_from_token()`.

> `set_user()` does not exist. The current method is `set_service(User $user)`.

---

## OAuth 2.0 Flow

### Step 1: Initiate OAuth Flow

**User Action:** User clicks "Connect QuickBooks" button, hitting `GET /quickbooks/login`.

`initiate_login` stashes the identifying context in the session (the callback runs unauthenticated, so this is how it recovers who is connecting), then returns the redirect from `oauth_begin()`:

```php
public function initiate_login(QuickBooksApi $api): RedirectResponse {
    session([
        'qb_return_url' => request()->headers->get('referer') ?? '/quickbooks',
        'qb_oauth_user_id' => request()->user()->id,
        'qb_oauth_org_id' => request()->user()->active_org_id,
    ]);

    return $api->oauth_begin();
}
```

`oauth_begin()` builds the Intuit authorization URL via the SDK's `OAuth2LoginHelper`, turns on OAuth call logging under `storage/logs/qbo`, and returns a `RedirectResponse` to that URL.

---

### Step 2: Handle Callback

**After Authorization:** QuickBooks redirects back to `GET /quickbooks/auth` with `code` and `realmId` query params (and `error`/`error_description` if the user denied access).

`set_login_tokens` re-identifies the user from the session, temporarily points them at the org that started the flow, and exchanges the code:

```php
public function set_login_tokens(QuickBooksApi $api): RedirectResponse {
    $user_id = session('qb_oauth_user_id');
    $return_url = session('qb_return_url', '/quickbooks');

    if (!$user_id) {
        return redirect()->to('/quickbooks')->with('message', 'OAuth session expired. Please try connecting again.');
    }

    if (request()->error) {
        // user denied or Intuit returned an error - log and bail
        session()->forget(['qb_return_url', 'qb_oauth_user_id', 'qb_oauth_org_id']);
        return redirect()->to($return_url)->with('message', 'QuickBooks authorization was not completed. Please try again.');
    }

    $user = User::findOrFail($user_id);

    // Pin the active org to the one that started the flow so the token saves against it
    $org_id = session('qb_oauth_org_id');
    if ($org_id && $user->active_org_id !== $org_id) {
        $user->active_org_id = $org_id;
    }

    $api->oauth_complete($user, request()->code ?? '', request()->realmId ?? '');

    session()->forget(['qb_return_url', 'qb_oauth_user_id', 'qb_oauth_org_id']);

    return redirect()->to($return_url);
}
```

`oauth_complete()` exchanges the authorization code, and on failure logs `QuickBooks OAuth Failed` and throws a `ConflictException`. On success it upserts one row per `(user_id, organization_id)`:

```php
public function oauth_complete(User $user, string $code, string $realm): QboAccessKey {
    $helper = (object) $this->service->getOAuth2LoginHelper();
    $accessToken = $helper->exchangeAuthorizationCodeForToken($code, $realm);
    $this->service->updateOAuth2Token($accessToken);

    return QboAccessKey::updateOrCreate(
        ['user_id' => $user->id, 'organization_id' => $user->active_org_id],
        [
            'realm_id' => $realm,
            'expires_at' => Carbon::parse($accessToken->getAccessTokenExpiresAt()),
            'access_key' => $accessToken->getAccessToken(),
            'refresh_key' => $accessToken->getRefreshToken(),
        ],
    );
}
```

> The code does NOT hand-roll a CSRF `state` token or validate one. The user is identified through the `qb_oauth_user_id` / `qb_oauth_org_id` session keys, and `oauth_complete` uses `updateOrCreate` on the `(user_id, organization_id)` unique key rather than blind `create`.

---

### Step 3: Using Authenticated API

**Every API Call:**
```php
$qbo = (new QuickBooksApi)->set_service($user);  // loads tokens for user's active org
$customers = $qbo->get_all_customers();
```

**What `set_service()` Does:**
1. Reads `$user->qbo_access_key_for_org` (the `HasOne` scoped to `active_org_id`)
2. Delegates to `set_service_from_token($accessToken)`, which:
   - deletes and nulls the token if it exists but has empty `access_key`/`refresh_key` (logs `QuickBooks Corrupt Token Cleaned`)
   - rebuilds the `DataService` from the token (or an anonymous service if none)
   - if `now() >= expires_at`, calls `refresh_token()`; a failed refresh deletes the token, logs `QuickBooks Token Refresh Failed`, and re-throws

For a token you already hold (for example the billing sync's service-user token), skip `set_service()` and pass it directly:
```php
$api->set_service_from_token($token);  // token is a QboAccessKey, not user-scoped
```

---

## Security Features

### Callback Identity

The callback route is unauthenticated (`web` middleware only), so it cannot rely on `auth()`. Identity is carried across the redirect in three session keys written by `initiate_login`: `qb_oauth_user_id`, `qb_oauth_org_id`, and `qb_return_url`. `set_login_tokens` resolves the user with `findOrFail`, then clears all three keys once the exchange completes.

### Token Storage (encrypted at rest since 2026-07-24)

Both token columns use Laravel `encrypted` casts (added on branch `qbo-token-encryption`, matching the SpotifyAccessKey idiom). Both columns are `text` (encrypted payloads exceed varchar(255); migration `2026_07_24_000000_encrypt_qbo_access_key_tokens` widened `refresh_key` and encrypted existing rows idempotently, with a reversible `down()`):

```php
class QboAccessKey extends Model {
    protected $hidden = ['access_key', 'refresh_key'];  // keep tokens out of JSON/Inertia props
    protected $casts = [
        'expires_at' => 'datetime',
        'access_key' => 'encrypted',
        'refresh_key' => 'encrypted',
    ];
}
```

Reading `$token->access_key` transparently decrypts; all writes encrypt. Never read the columns with `DB::table()` (bypasses casts). The corrupt-token guard in `set_service_from_token()` catches `DecryptException` (pre-encryption plaintext rows, APP_KEY rotation) and treats the row as corrupt: delete + re-auth, same as empty credentials. `$hidden` additionally keeps tokens out of serialized output (JSON responses, Inertia props).

Before 2026-07-24 tokens were stored in PLAINTEXT - any DB dump from before then contains live token material.

---

## Organization Scoping

**Multi-Tenant Pattern:**
- Each organization has its own QuickBooks connection
- Tokens stored with both `user_id` AND `organization_id`, unique on the pair
- When the user switches active organization, a different QuickBooks connection is used

**Token Lookup (via the scoped relationship):**
```php
// User::qbo_access_key_for_org() - HasOne scoped to active_org_id
public function qbo_access_key_for_org(): HasOne {
    return $this->hasOne(QboAccessKey::class)
        ->where('organization_id', $this->active_org_id);
}
```

**See:** `patterns/multi-tenancy.md` for complete multi-tenancy patterns

---

## Configuration

`service_config()` reads its credentials from `config/budtags.php`, and `make_service()` adds the redirect/scope for the auth flow. The real keys:

```php
private static function service_config(array $config_overrides = []): array {
    return [
        ...$config_overrides,
        'auth_mode' => 'oauth2',
        'ClientID' => config('budtags.qbo_client_id'),       // env QBO_CLIENT_ID
        'ClientSecret' => config('budtags.qbo_client_secret'), // env QBO_CLIENT_SECRET
        'baseUrl' => config('budtags.qbo_env'),              // env QBO_ENV - SDK environment string
    ];
}

// In make_service(), the auth-flow branch adds:
//   'RedirectURI' => config('app.url') . '/quickbooks/auth',
//   'scope'       => 'com.intuit.quickbooks.accounting',
```

**Relevant `.env` keys** (see `.env.example`):
```
QBO_APP_ID=
QBO_ENV=Production          # SDK environment string (e.g. Production / Development), NOT a URL
QBO_CLIENT_ID=
QBO_CLIENT_SECRET=
```

> The old fictional `QUICKBOOKS_CLIENT_ID` / `QUICKBOOKS_REDIRECT_URI` / `QUICKBOOKS_ENV=sandbox` variables do not exist. `QBO_ENV` is passed to the SDK as `baseUrl` and carries the SDK environment string, not a callback URL. The RedirectURI is derived from `config('app.url')`.

---

## Token Lifecycle

### Access Token
- **Lifespan:** 1 hour
- **Refresh:** Automatic - `set_service_from_token()` calls `refresh_token()` once `now() >= expires_at`
- **Storage:** `access_key` column, encrypted at rest via cast (hidden from serialization, see above)

### Refresh Token
- **Lifespan:** 100-day inactivity rule PLUS a 5-year hard cap since 2026-01-27 (never resets on refresh; earliest expirations for accounting-scope apps begin October 2028 - see `PLATFORM_CHANGES.md`)
- **Usage:** Refreshes the access token when expired; `refresh_token()` persists the rotated pair back to the row
- **Storage:** `refresh_key` column, encrypted at rest via cast (hidden from serialization, see above)

**See:** `patterns/token-refresh.md` for automatic refresh logic

---

## Error Handling

### Detecting OAuth Errors

Use the static helper rather than string-matching by hand - it collapses the common failure signatures:

```php
public static function is_oauth_error(\Exception $e): bool {
    $message = $e->getMessage();

    return str_contains($message, 'invalid_grant')
        || str_contains($message, 'token')
        || str_contains($message, '401')
        || str_contains($message, 'Unauthorized');
}
```

### No Connection Exists

Guard before authenticating - the scoped relationship is null when the org has never connected:
```php
abort_if(!$user->qbo_access_key_for_org, 403, 'QuickBooks not connected');
$qbo = (new QuickBooksApi)->set_service($user);
```

### Token Exchange Failed

`oauth_complete()` catches the SDK `ServiceException`, logs it via `LogService`, and rethrows as a `ConflictException` - do not add a second `try/catch` around it or log with `Log::`:
```php
// inside oauth_complete()
} catch (ServiceException $e) {
    LogService::store('QuickBooks OAuth Failed', "Token exchange failed for {$user->email} (realm: {$realm}). Error: {$e->getMessage()}");
    throw new ConflictException('Failed to connect to QuickBooks. Please try again.');
}
```

### Expired / Invalid Refresh Token

When `refresh_token()` throws, `set_service_from_token()` deletes the dead token and rethrows, so the user is forced back through the connect flow at `/quickbooks/login`. For the unattended billing sync, the same failure is captured with keyed logging instead (see `patterns/billing-invoice-sync.md`).

---

## Best Practices

✅ **ALWAYS call `set_service($user)` (or `set_service_from_token($token)`) before any API call**
✅ **ALWAYS scope tokens to `(user_id, organization_id)`**
✅ **ALWAYS keep `access_key` / `refresh_key` in the model's `$hidden` array**
✅ **ALWAYS log OAuth events via `LogService::store()`**
✅ **ALWAYS let `set_service_from_token()` own refresh - it persists the rotated pair**

❌ **NEVER surface `access_key` / `refresh_key` to the client**
❌ **NEVER call the removed `set_user()` - it is `set_service()`**
❌ **NEVER share tokens between organizations**
❌ **NEVER hardcode client credentials - read them from `config('budtags.qbo_*')`**

---

## Related Patterns

- `patterns/token-refresh.md` - Automatic token refresh
- `patterns/multi-tenancy.md` - Organization scoping
- `patterns/billing-invoice-sync.md` - Service-user token + unattended re-auth recovery
- `patterns/logging.md` - Logging OAuth events
- `categories/authentication.md` - Authentication operations reference
