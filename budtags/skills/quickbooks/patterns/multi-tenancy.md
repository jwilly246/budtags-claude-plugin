# QuickBooks Multi-Tenancy Pattern

**Pattern:** Organization-Scoped Authentication
**Scope:** One QuickBooks connection per organization
**Model:** `QboAccessKey`

---

## Overview

BudTags is multi-tenant. Most QuickBooks features run against the org the current user is looking at, so each organization can hold its own QuickBooks connection. The billing/overdue subsystem is the one exception: it runs unattended against a single **service user's** token (see the [Service-User Model](#service-user-model-billing-sync) below).

**Key Concept:** Interactive tokens are scoped to the `(user_id, organization_id)` pair, unique on that pair.

> The column is `organization_id` (a UUID FK to `organizations`), NOT `org_id`.

---

## Database Model

### QboAccessKey Schema

Built across two migrations - the base table, then `organization_id` + the unique key:

```php
// 2025_09_11 create_qbo_access_keys_table
Schema::create('qbo_access_keys', function (Blueprint $table) {
    $table->id();
    $table->timestamps();
    $table->text('access_key');    // OAuth access token (encrypted at rest via cast since 2026-07-24)
    $table->text('realm_id');      // QuickBooks company ID
    $table->string('refresh_key'); // OAuth refresh token (widened to text + encrypted by 2026_07_24 migration)
    $table->dateTime('expires_at');
    $table->foreignUuid('user_id')->constrained('users')->cascadeOnDelete()->cascadeOnUpdate();
});

// 2026_03_08 add_organization_id_to_qbo_access_keys (backfilled from users.active_org_id)
Schema::table('qbo_access_keys', function (Blueprint $table) {
    $table->foreignUuid('organization_id')->after('user_id')
        ->constrained('organizations')->cascadeOnDelete()->cascadeOnUpdate();
    $table->unique(['user_id', 'organization_id']); // one QB connection per user per org
});
```

**Key Fields:**
- `user_id` + `organization_id` - Unique pair; the scoping key
- `realm_id` - QuickBooks company ID (differs per QB company)
- `expires_at` - Access token expiration (`datetime` cast on the model)

**Model** (`App\Models\QboAccessKey`):
```php
protected $fillable = ['user_id', 'organization_id', 'access_key', 'refresh_key', 'expires_at', 'realm_id'];
protected $hidden = ['access_key', 'refresh_key']; // keep tokens out of JSON/Inertia props
protected $casts = [
    'expires_at' => 'datetime',
    'access_key' => 'encrypted',
    'refresh_key' => 'encrypted',
];
```

Tokens are hidden from serialization AND encrypted at rest (since 2026-07-24) - see `patterns/authentication.md`.

---

## Token Lookup Pattern

Interactive requests never query `QboAccessKey` by hand. The `User` model exposes a `HasOne` scoped to the current active org, and `set_service()` reads it:

```php
// User model
public function qbo_access_key(): HasMany {                 // all of a user's tokens
    return $this->hasMany(QboAccessKey::class);
}

public function qbo_access_key_for_org(): HasOne {          // token for the ACTIVE org only
    return $this->hasOne(QboAccessKey::class)
        ->where('organization_id', $this->active_org_id);
}
```

```php
// QuickBooksApi::set_service() - the standard entry point
public function set_service(User $user): self {
    $accessToken = $user->qbo_access_key_for_org;
    return $this->set_service_from_token($accessToken);
}
```

Because `qbo_access_key_for_org` is a dynamic relationship pinned to `active_org_id`, switching orgs (or pinning `active_org_id` mid-request, as the OAuth callback does) automatically changes which QuickBooks company you talk to. There is no `set_user()` method.

---

## Cross-Org Access Prevention

**ALWAYS resolve tokens through the scoped relationship, never a bare `user_id` filter:**

```php
// ✅ CORRECT - scoped to the active org
$qbo = (new QuickBooksApi)->set_service($user);

// ✅ CORRECT - guard when a connection may not exist
abort_if(!$user->qbo_access_key_for_org, 403, 'QuickBooks not connected');
```

```php
// ❌ WRONG - could grab another org's token
$token = QboAccessKey::where('user_id', $user->id)->first();
```

**Middleware:** the `/quickbooks` route group runs behind `auth` + `has-org` + `quickbooks`, so `active_org_id` is guaranteed set on every interactive endpoint. Cache keys and the Redis invoice snapshot are org-scoped for the same reason - see `patterns/caching.md`.

> The one legitimate `where('user_id', ...)` lookup is the billing sync (below), which deliberately ignores the active-org relationship because the service user's `active_org_id` may not match the org the token was minted for.

---

## Disconnecting QuickBooks

`logout` deletes only the active org's token via the scoped relationship:

```php
public function logout(): RedirectResponse {
    $this->user()->qbo_access_key_for_org()->delete();

    return redirect()->back()->with('message', 'Disconnected from QuickBooks successfully!');
}
```

Other organizations' connections stay intact.

---

## Service-User Model (Billing Sync)

The overdue-invoice pipeline (`qbo:sync-invoices`) is org-scoped in its *outputs* but runs from a single BudTags-owned QuickBooks connection: one **service user** whose token can read invoices for every org that has a `qbo_customer_id`.

- **Which user:** `config('quickbooks.service_user_id')` (env `QBO_SERVICE_USER_ID`).
- **Token lookup - deliberately by `user_id` only:**
  ```php
  // SyncQboInvoices::initialize_api()
  $token = QboAccessKey::where('user_id', $user->id)->latest()->first();
  $api = app(QuickBooksApi::class);
  $api->set_service_from_token($token);
  ```
  This bypasses `qbo_access_key_for_org` on purpose: the service user's `active_org_id` may differ from the org the token was created against, and the token works company-wide regardless.
- **Per-org fan-out:** the command iterates `Organization::whereNotNull('qbo_customer_id')` and fetches each org's invoices with `get_customer_invoices($org->qbo_customer_id)`, then writes org-scoped billing state and an org-scoped Redis snapshot.

Full flow, billing columns, thresholds, schedule, and re-auth recovery live in `patterns/billing-invoice-sync.md`.

---

## Best Practices

✅ **ALWAYS scope interactive access through `set_service($user)` / `qbo_access_key_for_org`**
✅ **ALWAYS rely on the `(user_id, organization_id)` unique key - one connection per pair**
✅ **ALWAYS guard for a missing connection** (`abort_if(!$user->qbo_access_key_for_org, ...)`)
✅ **ALWAYS use `organization_id` (UUID), not `org_id`**

❌ **NEVER filter `QboAccessKey` by bare `user_id`** except the intentional service-user lookup
❌ **NEVER share tokens between organizations in interactive flows**
❌ **NEVER assume a user has QuickBooks connected**
❌ **NEVER reference `org_id` - that column name does not exist here**

---

## Related Patterns

- `patterns/authentication.md` - OAuth flow and token storage
- `patterns/token-refresh.md` - Token refresh logic
- `patterns/billing-invoice-sync.md` - Service-user token + overdue pipeline
- `patterns/caching.md` - Org-scoped cache keys and the Redis invoice snapshot
- `patterns/logging.md` - Organization-scoped logging
