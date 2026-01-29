# QuickBooks Multi-Tenancy Pattern

**Pattern:** Organization-Scoped Authentication
**Scope:** One QuickBooks connection per organization
**Model:** `QboAccessKey`

---

## Overview

BudTags supports multiple organizations (multi-tenancy). Each organization can have its own QuickBooks connection, allowing different organizations to connect to different QuickBooks companies.

**Key Concept:** Tokens are scoped to `(user_id, org_id)` pair

---

## Database Model

### QboAccessKey Schema

```php
Schema::create('qbo_access_keys', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained()->onDelete('cascade');
    $table->foreignId('org_id')->constrained('organizations')->onDelete('cascade');
    $table->string('access_key');  // Encrypted access token
    $table->string('refresh_key'); // Encrypted refresh token
    $table->string('realm_id');    // QuickBooks company ID
    $table->timestamp('expires_at');
    $table->timestamps();

    // Unique constraint: one QB connection per user per org
    $table->unique(['user_id', 'org_id']);
});
```

**Key Fields:**
- `user_id` + `org_id` - Composite key for org scoping
- `realm_id` - QuickBooks company ID (different for each QB company)
- `expires_at` - Access token expiration timestamp

---

## Token Lookup Pattern

### Loading Tokens for Active Organization

```php
public function set_user(User $user): void {
    // Load tokens for user's ACTIVE organization only
    $this->access_key = QboAccessKey::where('user_id', $user->id)
        ->where('org_id', $user->active_org->id)  // Active org scoping
        ->first();

    if (!$this->access_key) {
        throw new Exception('No QuickBooks connection for this organization');
    }

    // Configure API with org-specific tokens
    $this->setupDataService();
}
```

### When User Switches Organizations

**Scenario:** User switches from Org A to Org B

**Before:**
```php
$user->active_org_id = 1;  // Org A
$qbo->set_user($user);
// Uses Org A's QuickBooks connection
```

**After Switch:**
```php
$user->update(['active_org_id' => 2]);  // Switch to Org B
$qbo = new QuickBooksApi();  // Create new instance
$qbo->set_user($user);
// Uses Org B's QuickBooks connection (different realm_id)
```

**IMPORTANT:** Each organization can connect to a different QuickBooks company!

---

## Multiple Connections Per User

**Example:**
- User belongs to 3 organizations
- Each organization connected to different QuickBooks company
- User sees different data depending on active organization

```
User: John Doe
├─ Organization A → QuickBooks Company X (realm_id: 123)
├─ Organization B → QuickBooks Company Y (realm_id: 456)
└─ Organization C → QuickBooks Company Z (realm_id: 789)
```

**Database:**
```
qbo_access_keys table:
| user_id | org_id | realm_id | access_key | refresh_key |
|---------|--------|----------|------------|-------------|
| 1       | 1      | 123      | abc...     | xyz...      |
| 1       | 2      | 456      | def...     | uvw...      |
| 1       | 3      | 789      | ghi...     | rst...      |
```

---

## Cross-Org Access Prevention

### Security Pattern

**ALWAYS check active_org_id:**

```php
// ✅ CORRECT - Scoped to active org
$accessKey = QboAccessKey::where('user_id', $user->id)
    ->where('org_id', $user->active_org->id)
    ->first();
```

```php
// ❌ WRONG - Could access other org's tokens!
$accessKey = QboAccessKey::where('user_id', $user->id)->first();
```

**Middleware:** `has-org` middleware ensures user has active organization

---

## OAuth Flow Per Organization

### Connecting Organization to QuickBooks

```php
// User clicks "Connect QuickBooks" in Org A
Route::get('/quickbooks/login', function () {
    // State includes current org_id
    session(['oauth_org_id' => auth()->user()->active_org->id]);

    $authUrl = QuickBooksApi::oauth_begin();
    return redirect($authUrl);
});

// After OAuth callback
Route::get('/quickbooks/callback', function (Request $request) {
    $orgId = session('oauth_org_id');

    // Store tokens for THIS organization
    QboAccessKey::create([
        'user_id' => auth()->id(),
        'org_id' => $orgId,  // Scoped to org in session
        'access_key' => $accessToken,
        'refresh_key' => $refreshToken,
        'realm_id' => $request->realmId
    ]);
});
```

---

## Disconnecting QuickBooks

### Disconnect Current Organization

```php
Route::get('/quickbooks/logout', function () {
    $user = auth()->user();

    QboAccessKey::where('user_id', $user->id)
        ->where('org_id', $user->active_org->id)
        ->delete();

    return redirect('/quickbooks')
        ->with('message', 'QuickBooks disconnected');
});
```

**Effect:**
- Deletes tokens for current organization only
- Other organizations' connections remain intact
- User can still access QuickBooks through other orgs

---

## Best Practices

✅ **ALWAYS scope queries to active_org_id**
✅ **ALWAYS use unique constraint on (user_id, org_id)**
✅ **ALWAYS check for null access_key** - Org may not be connected
✅ **ALWAYS store org_id during OAuth callback**

❌ **NEVER query without org_id** - Security risk
❌ **NEVER share tokens between organizations**
❌ **NEVER assume user has QuickBooks connected**
❌ **NEVER use first() without org_id filter**

---

## Testing Multi-Tenancy

### Setup Test Data

```php
// Create 2 organizations
$org1 = Organization::create(['name' => 'Org A']);
$org2 = Organization::create(['name' => 'Org B']);

// Create user in both orgs
$user = User::factory()->create();
$user->organizations()->attach([$org1->id, $org2->id]);

// Connect Org A to QuickBooks Company X
$user->update(['active_org_id' => $org1->id]);
// Go through OAuth flow...

// Connect Org B to QuickBooks Company Y
$user->update(['active_org_id' => $org2->id]);
// Go through OAuth flow again...

// Verify separate connections
assert(QboAccessKey::where('org_id', $org1->id)->first()->realm_id === '123');
assert(QboAccessKey::where('org_id', $org2->id)->first()->realm_id === '456');
```

---

## Related Patterns

- `patterns/authentication.md` - OAuth flow
- `patterns/token-refresh.md` - Token refresh logic
- `patterns/logging.md` - Organization-scoped logging
