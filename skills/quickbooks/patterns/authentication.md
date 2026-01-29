# QuickBooks OAuth 2.0 Authentication Pattern

**Pattern:** OAuth 2.0 Flow
**Scope:** Organization-scoped authentication
**Security:** CSRF protection, encrypted token storage

---

## Overview

QuickBooks uses OAuth 2.0 for authentication. Each organization has its own QuickBooks connection stored in the `QboAccessKey` model.

**Key Models:**
- `QboAccessKey` - Stores encrypted OAuth tokens per user/organization

**Routes:**
- `/quickbooks/login` - Initiate OAuth flow
- `/quickbooks/callback` - OAuth callback handler
- `/quickbooks/logout` - Disconnect QuickBooks

---

## OAuth 2.0 Flow

### Step 1: Initiate OAuth Flow

**User Action:** User clicks "Connect QuickBooks" button

**Code:**
```php
// Route: /quickbooks/login
$authUrl = QuickBooksApi::oauth_begin();
return redirect($authUrl);
```

**What Happens:**
1. Generates CSRF state token
2. Stores state in session
3. Redirects user to QuickBooks login page
4. User logs into QuickBooks
5. User authorizes app permissions

---

### Step 2: Handle Callback

**After Authorization:** QuickBooks redirects back to `/quickbooks/callback`

**Query Parameters:**
- `code` - Authorization code
- `state` - CSRF token (must match session)
- `realmId` - QuickBooks company ID

**Code:**
```php
// Route: /quickbooks/callback
QuickBooksApi::oauth_complete($request);

// Tokens now stored in database
session()->flash('message', 'QuickBooks connected successfully!');
return redirect('/quickbooks');
```

**What Happens:**
1. Validates CSRF state token
2. Exchanges authorization code for access + refresh tokens
3. Stores encrypted tokens in `QboAccessKey` table
4. Stores QuickBooks company ID (realm_id)
5. Sets token expiration timestamp

**Database Storage:**
```php
QboAccessKey::create([
    'user_id' => $user->id,
    'org_id' => $user->active_org->id,
    'access_key' => encrypt($accessToken),
    'refresh_key' => encrypt($refreshToken),
    'realm_id' => $realmId,
    'expires_at' => now()->addSeconds($expiresIn)
]);
```

---

### Step 3: Using Authenticated API

**Every API Call:**
```php
$qbo = new QuickBooksApi();
$qbo->set_user($user);  // Loads tokens for user's active org
$customers = $qbo->get_all_customers();
```

**What `set_user()` Does:**
1. Loads `QboAccessKey` for user's active organization
2. Decrypts access and refresh tokens
3. Configures DataService with OAuth credentials
4. Checks if token needs refresh (auto-refreshes if needed)

---

## Security Features

### CSRF Protection

**State Token:**
- Generated during oauth_begin()
- Stored in session
- Validated during oauth_complete()
- Prevents cross-site request forgery

**Validation:**
```php
if ($request->state !== session('oauth_state')) {
    throw new Exception('Invalid state token');
}
```

### Encrypted Token Storage

**Encryption:**
- Access tokens encrypted using Laravel's encrypt()
- Refresh tokens encrypted using Laravel's encrypt()
- Decrypted only when needed for API calls

**Model Configuration:**
```php
class QboAccessKey extends Model {
    protected $casts = [
        'access_key' => 'encrypted',
        'refresh_key' => 'encrypted',
    ];
}
```

---

## Organization Scoping

**Multi-Tenant Pattern:**
- Each organization has its own QuickBooks connection
- Tokens stored with both user_id AND org_id
- When user switches active organization, different QuickBooks connection used

**Token Lookup:**
```php
$accessKey = QboAccessKey::where('user_id', $user->id)
    ->where('org_id', $user->active_org->id)
    ->first();
```

**See:** `patterns/multi-tenancy.md` for complete multi-tenancy patterns

---

## Token Lifecycle

### Access Token
- **Lifespan:** 1 hour
- **Refresh:** Automatic (before expiration)
- **Storage:** Encrypted in database

### Refresh Token
- **Lifespan:** 100 days (QuickBooks default)
- **Usage:** Refreshes access token when expired
- **Storage:** Encrypted in database

**See:** `patterns/token-refresh.md` for automatic refresh logic

---

## Error Handling

### Common OAuth Errors

**No Connection Exists:**
```php
// User hasn't connected QuickBooks yet
if (!$accessKey) {
    return redirect('/quickbooks/login')
        ->with('message', 'Please connect QuickBooks first');
}
```

**State Mismatch:**
```php
// CSRF validation failed
if ($request->state !== session('oauth_state')) {
    throw new Exception('Invalid state token - possible CSRF attack');
}
```

**Token Exchange Failed:**
```php
// Authorization code expired or invalid
try {
    $accessToken = $client->getAccessToken('authorization_code', [
        'code' => $request->code
    ]);
} catch (Exception $e) {
    Log::error('QuickBooks OAuth failed: ' . $e->getMessage());
    return redirect('/quickbooks/login')
        ->with('error', 'Failed to connect QuickBooks');
}
```

---

## Testing OAuth Flow

### Local Development

**QuickBooks Sandbox:**
1. Create QuickBooks Developer account
2. Create sandbox app
3. Get sandbox client ID and secret
4. Set in `.env`:
   ```
   QUICKBOOKS_CLIENT_ID=your_sandbox_client_id
   QUICKBOOKS_CLIENT_SECRET=your_sandbox_secret
   QUICKBOOKS_REDIRECT_URI=http://localhost:8000/quickbooks/callback
   QUICKBOOKS_ENV=sandbox
   ```

### Production

**QuickBooks Production:**
1. Submit app for production approval
2. Get production client ID and secret
3. Set in `.env`:
   ```
   QUICKBOOKS_ENV=production
   ```

---

## Best Practices

✅ **ALWAYS validate CSRF state token**
✅ **ALWAYS encrypt tokens in database**
✅ **ALWAYS scope tokens to organization**
✅ **ALWAYS check token expiration before API calls**
✅ **ALWAYS log OAuth events via LogService**

❌ **NEVER store tokens in plain text**
❌ **NEVER share tokens between organizations**
❌ **NEVER skip CSRF validation**
❌ **NEVER hardcode client credentials**

---

## Related Patterns

- `patterns/token-refresh.md` - Automatic token refresh
- `patterns/multi-tenancy.md` - Organization scoping
- `patterns/logging.md` - Logging OAuth events
- `categories/authentication.md` - Authentication operations reference
