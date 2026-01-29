# QuickBooks Authentication Operations

**Category:** Authentication & Token Management
**Operations:** 4 methods
**Purpose:** OAuth 2.0 flow and token lifecycle management

---

## Overview

QuickBooks uses OAuth 2.0 for authentication. All operations in this category handle the OAuth flow, token storage, automatic refresh, and user/organization setup.

**Key Models:**
- `QboAccessKey` - Stores encrypted OAuth tokens per user/organization

**Key Patterns:**
- Organization-scoped authentication (one QuickBooks connection per org)
- Automatic token refresh (transparent to users)
- Secure token storage (encrypted in database)

**See Also:**
- `patterns/authentication.md` - Detailed OAuth 2.0 flow
- `patterns/token-refresh.md` - Token refresh logic
- `patterns/multi-tenancy.md` - Organization scoping details

---

## Operations

### 1. `oauth_begin()`

**Purpose:** Initiate OAuth 2.0 flow with QuickBooks

**Signature:**
```php
public static function oauth_begin(): string
```

**Returns:** Authorization URL (string)

**Usage:**
```php
$authUrl = QuickBooksApi::oauth_begin();
return redirect($authUrl);
```

**Notes:**
- Generates CSRF token for security
- Stores state in session
- Redirects user to QuickBooks login
- Route: `/quickbooks/login`

---

### 2. `oauth_complete(Request $request)`

**Purpose:** Complete OAuth flow and store access tokens

**Signature:**
```php
public static function oauth_complete(Request $request): void
```

**Parameters:**
- `$request` - Contains `code`, `state`, `realmId` from QuickBooks callback

**Returns:** `void` (stores tokens in database)

**Usage:**
```php
QuickBooksApi::oauth_complete($request);
// Tokens now stored in QboAccessKey model
```

**Database Storage:**
```php
QboAccessKey::create([
    'user_id' => $user->id,
    'org_id' => $user->active_org->id,
    'access_key' => $accessToken,
    'refresh_key' => $refreshToken,
    'realm_id' => $realmId,
    'expires_at' => now()->addSeconds($expiresIn)
]);
```

**Notes:**
- Validates CSRF state
- Exchanges auth code for tokens
- Stores encrypted tokens
- Organization-scoped
- Route: `/quickbooks/callback`

---

### 3. `refresh_token()`

**Purpose:** Refresh expired access token using refresh token

**Signature:**
```php
public function refresh_token(): void
```

**Returns:** `void` (updates tokens in database)

**Usage:**
```php
$qbo = new QuickBooksApi();
$qbo->set_user($user);
$qbo->refresh_token(); // Usually called automatically
```

**Auto-Refresh Logic:**
```php
// Called automatically before every API request
if ($this->access_key->expires_at < now()->addMinutes(5)) {
    $this->refresh_token();
}
```

**Notes:**
- Automatically called when token near expiration
- Updates both access and refresh tokens
- Logs refresh events via LogService
- Throws exception if refresh token expired

**See:** `patterns/token-refresh.md` for complete refresh logic

---

### 4. `set_user(User $user)`

**Purpose:** Configure API service for specific user/organization

**Signature:**
```php
public function set_user(User $user): void
```

**Parameters:**
- `$user` - User model with active_org relationship loaded

**Usage:**
```php
$qbo = new QuickBooksApi();
$qbo->set_user($user);
// Now ready to make API calls
```

**Sets Up:**
- Access key retrieval from database
- DataService configuration
- OAuth credentials
- Realm ID (QuickBooks company ID)
- Automatic token refresh

**Throws:**
- Exception if no QuickBooks connection exists for user

**See:** `patterns/multi-tenancy.md` for organization scoping details

---

## Common Workflows

### Initial Authentication
1. User clicks "Connect QuickBooks"
2. Call `oauth_begin()` to get auth URL
3. Redirect to QuickBooks login
4. User authorizes app
5. QuickBooks redirects back to callback
6. Call `oauth_complete($request)` to store tokens

### Making API Calls
1. Create QuickBooksApi instance
2. Call `set_user($user)` to load credentials
3. Token automatically refreshed if needed
4. Make API calls (create invoice, fetch customers, etc.)

**See:** `scenarios/invoice-workflow.md` for complete invoice workflow example
