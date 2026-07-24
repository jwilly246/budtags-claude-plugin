# QuickBooks Authentication Operations

**Category:** Authentication & Token Management
**Operations:** 7 methods
**Purpose:** OAuth 2.0 flow, service setup, and token lifecycle management

---

## Overview

QuickBooks uses OAuth 2.0. Before any API call you must construct a
`QuickBooksApi` and attach an authenticated DataService for the current
user/organization with `set_service($user)`. Tokens are stored per
(user_id, organization_id) pair and refreshed automatically when expired.

**Key Models:**
- `QboAccessKey` - Stores OAuth tokens per user/organization

**Token storage (`qbo_access_keys` table):**
- `access_key` - OAuth access token (text)
- `refresh_key` - OAuth refresh token
- `realm_id` - QuickBooks company (realm) ID
- `expires_at` - access token expiry (datetime)
- `user_id`, `organization_id` - owner; UNIQUE together (one token per user+org)

`access_key` and `refresh_key` are `$hidden` on the model so they never leak into
Inertia props or JSON.

**Setup idiom (used everywhere):**
```php
$qbo = new QuickBooksApi();
$qbo->set_service($user);
// or fluent: $qbo = (new QuickBooksApi)->set_service($user);
```

**See Also:**
- `patterns/authentication.md` - OAuth 2.0 flow
- `patterns/token-refresh.md` - Token refresh logic
- `patterns/multi-tenancy.md` - Organization scoping

---

## Operations

### 1. `set_service(User $user): self`

Attach an authenticated DataService using the user's stored token for their
active organization. Reads `$user->qbo_access_key_for_org`. Returns `$this`.

```php
$qbo = (new QuickBooksApi)->set_service($user);
```

- If the token is expired it is refreshed automatically (see `refresh_token`).
- If refresh fails the token record is deleted and the exception re-thrown.
- If no token exists the service is built unauthenticated (calls fail until the
  user connects).

---

### 2. `set_service_from_token(?QboAccessKey $accessToken): self`

Lower-level variant of `set_service`. Attaches the DataService from a specific
token record (or unauthenticated when `null`). Cleans up and deletes token rows
that have empty `access_key`/`refresh_key`. `set_service` delegates to this.

```php
$qbo->set_service_from_token($user->qbo_access_key_for_org);
```

---

### 3. `oauth_begin(): RedirectResponse`

Instance method. Builds the QuickBooks authorization URL and returns a redirect
to it. This is where the "Connect QuickBooks" flow starts.

```php
// QuickBooksController::initiate_login
public function initiate_login(QuickBooksApi $api): RedirectResponse {
    session([
        'qb_return_url' => request()->headers->get('referer') ?? '/quickbooks',
        'qb_oauth_user_id' => request()->user()->id,
        'qb_oauth_org_id' => request()->user()->active_org_id,
    ]);

    return $api->oauth_begin();
}
```

- Route: `GET /quickbooks/login` -> `initiate_login`
- The user id / org id are stashed in the session so the callback can identify
  the user after the cross-domain redirect back from Intuit.

---

### 4. `oauth_complete(User $user, string $code, string $realm): QboAccessKey`

Exchanges the authorization `code` for tokens and upserts the `QboAccessKey`
row for `(user_id => $user->id, organization_id => $user->active_org_id)`.
Returns the persisted token.

```php
// QuickBooksController::set_login_tokens (callback)
$api->oauth_complete(
    $user,
    request()->code ?? '',
    request()->realmId ?? '',
);
```

- Route: `GET /quickbooks/auth` -> `set_login_tokens` (outside auth middleware;
  identifies the user from the session keys set in `initiate_login`).
- There is NO `/quickbooks/callback` route.
- On token-exchange failure it logs via `LogService` and throws `ConflictException`.

---

### 5. `refresh_token(QboAccessKey &$accessToken): QboAccessKey`

Refreshes an expired access token using the refresh token, persists the new
`access_key`, `refresh_key`, and `expires_at`, and returns the updated record.
Called automatically by `set_service` when `now() >= $accessToken->expires_at`;
rarely called directly.

```php
$qbo->refresh_token($accessToken);
```

**See:** `patterns/token-refresh.md`.

---

### 6. `is_oauth_error(\Exception $e): bool` *(static)*

Classifies whether an exception is an auth/token failure (matches
`invalid_grant`, `token`, `401`, or `Unauthorized` in the message). Use it to
decide between "reconnect QuickBooks" and a generic API error.

```php
try {
    $qbo->set_service($user);
    $company = $qbo->get_company_info();
} catch (\Exception $e) {
    $reconnect = QuickBooksApi::is_oauth_error($e);
    // show "session expired, reconnect" vs a generic error
}
```

---

### 7. `set_service_redirect_to_dev(): self`

Configures the service with the `/dev/qbo/auth` redirect URI for the local dev
OAuth flow. Not used in the normal app path.

---

## Common Workflows

### Initial Authentication
1. User clicks "Connect QuickBooks" -> `GET /quickbooks/login` (`initiate_login`).
2. `oauth_begin()` redirects the browser to Intuit.
3. User authorizes; Intuit redirects to `GET /quickbooks/auth` (`set_login_tokens`).
4. `oauth_complete($user, $code, $realm)` upserts the `QboAccessKey`.

### Making API Calls
1. `$qbo = (new QuickBooksApi)->set_service($user);`
2. Token auto-refreshes if expired.
3. Call operations (invoices, customers, items, ...).

**See:** `scenarios/invoice-workflow.md` for a full example.
