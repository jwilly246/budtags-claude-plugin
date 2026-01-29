# QuickBooks OAuth 2.0 Authentication Flow

Complete guide to OAuth authentication, token management, and troubleshooting in the BudTags QuickBooks integration.

---

## Table of Contents

1. [Overview](#overview)
2. [OAuth 2.0 Flow Steps](#oauth-20-flow-steps)
3. [Token Storage](#token-storage)
4. [Automatic Token Refresh](#automatic-token-refresh)
5. [Multi-Tenant Support](#multi-tenant-support)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

---

## Overview

**Authentication Method:** OAuth 2.0 Authorization Code Flow
**Token Lifetime:**
- Access Token: 1 hour
- Refresh Token: 60 days (rolling refresh)

**Flow Type:** Three-legged OAuth
1. User initiates connection
2. User authorizes on QuickBooks
3. Application receives authorization code
4. Application exchanges code for tokens

---

## OAuth 2.0 Flow Steps

### Step 1: User Initiates Connection

**Route:** `GET /quickbooks/login`

**Controller:** `QuickBooksController@login`

```php
public function login() {
    $authUrl = QuickBooksApi::oauth_begin();
    return redirect($authUrl);
}
```

**What Happens:**
1. Generates CSRF state token for security
2. Stores state in session
3. Builds authorization URL with scopes
4. Redirects user to QuickBooks login

**Authorization URL:**
```
https://appcenter.intuit.com/connect/oauth2
?client_id={CLIENT_ID}
&response_type=code
&scope=com.intuit.quickbooks.accounting
&redirect_uri={REDIRECT_URI}
&state={CSRF_TOKEN}
```

**Scopes Requested:**
- `com.intuit.quickbooks.accounting` - Full accounting access

---

### Step 2: User Authorizes on QuickBooks

**User Experience:**
1. Redirected to QuickBooks login page
2. Logs into QuickBooks account
3. Selects company to connect
4. Authorizes app permissions
5. Redirected back to application

**QuickBooks Callback:**
```
{REDIRECT_URI}
?code={AUTHORIZATION_CODE}
&state={CSRF_TOKEN}
&realmId={COMPANY_ID}
```

---

### Step 3: Application Receives Callback

**Route:** `GET /quickbooks/callback`

**Controller:** `QuickBooksController@callback`

```php
public function callback(Request $request) {
    QuickBooksApi::oauth_complete($request);
    return redirect('/quickbooks/dashboard')->with('success', 'QuickBooks connected!');
}
```

**oauth_complete() Process:**

```php
public static function oauth_complete(Request $request): void
{
    // 1. Validate CSRF state
    if ($request->state !== session('oauth_state')) {
        throw new \Exception('Invalid OAuth state');
    }

    // 2. Exchange authorization code for tokens
    $oauth2LoginHelper = new OAuth2LoginHelper($clientId, $clientSecret);
    $accessTokenObj = $oauth2LoginHelper->exchangeAuthorizationCodeForToken(
        $request->code,
        $redirectUri
    );

    // 3. Extract tokens
    $accessToken = $accessTokenObj->getAccessToken();
    $refreshToken = $accessTokenObj->getRefreshToken();
    $expiresIn = $accessTokenObj->getAccessTokenExpiresAt();
    $realmId = $request->realmId;

    // 4. Store tokens in database
    QboAccessKey::updateOrCreate(
        [
            'user_id' => auth()->id(),
            'org_id' => auth()->user()->active_org->id
        ],
        [
            'access_key' => encrypt($accessToken),
            'refresh_key' => encrypt($refreshToken),
            'realm_id' => $realmId,
            'expires_at' => Carbon::createFromTimestamp($expiresIn)
        ]
    );

    // 5. Log success
    LogService::store(
        'QuickBooks Connected',
        "Company ID: {$realmId}"
    );
}
```

---

### Step 4: Tokens Stored in Database

**See:** [Token Storage](#token-storage) section below

---

## Token Storage

### QboAccessKey Model

**Table:** `qbo_access_keys`

**Schema:**
```php
Schema::create('qbo_access_keys', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained()->onDelete('cascade');
    $table->foreignId('org_id')->constrained('organizations')->onDelete('cascade');
    $table->text('access_key');   // Encrypted access token
    $table->text('refresh_key');  // Encrypted refresh token
    $table->string('realm_id');   // QuickBooks company ID
    $table->timestamp('expires_at');
    $table->timestamps();

    $table->unique(['user_id', 'org_id']);
});
```

**Model Attributes:**
- `access_key` - Access token (encrypted)
- `refresh_key` - Refresh token (encrypted)
- `realm_id` - QuickBooks company ID
- `expires_at` - Access token expiration timestamp

**Encryption:**
- Tokens are encrypted using Laravel's `encrypt()` helper
- Decrypted automatically when retrieved
- Stored as TEXT columns for variable length

**Organization Scoping:**
- Each user can have one QuickBooks connection per organization
- Unique constraint on `user_id + org_id`
- Allows multi-tenant support

---

## Automatic Token Refresh

### When Tokens Expire

**Access Token:** Expires after 1 hour
**Refresh Token:** Expires after 60 days (rolling)

**Rolling Refresh:** Each token refresh extends refresh token by 60 days

### Auto-Refresh Logic

**Triggered:** Before every API request

```php
public function set_user(User $user): void
{
    // Load access key from database
    $this->access_key = QboAccessKey::where('user_id', $user->id)
        ->where('org_id', $user->active_org->id)
        ->firstOrFail();

    // Check if token expires soon (within 5 minutes)
    if ($this->access_key->expires_at < now()->addMinutes(5)) {
        $this->refresh_token();
    }

    // Configure DataService with current tokens
    $this->service = DataService::Configure([
        'auth_mode' => 'oauth2',
        'ClientID' => config('budtags.quickbooks_client_id'),
        'ClientSecret' => config('budtags.quickbooks_client_secret'),
        'accessTokenKey' => decrypt($this->access_key->access_key),
        'refreshTokenKey' => decrypt($this->access_key->refresh_key'),
        'QBORealmID' => $this->access_key->realm_id,
        'baseUrl' => config('budtags.quickbooks_base_url')
    ]);
}
```

### refresh_token() Method

```php
public function refresh_token(): void
{
    $oauth2LoginHelper = new OAuth2LoginHelper(
        config('budtags.quickbooks_client_id'),
        config('budtags.quickbooks_client_secret')
    );

    // Use refresh token to get new tokens
    $accessTokenObj = $oauth2LoginHelper->refreshToken(
        decrypt($this->access_key->refresh_key)
    );

    // Update database with new tokens
    $this->access_key->update([
        'access_key' => encrypt($accessTokenObj->getAccessToken()),
        'refresh_key' => encrypt($accessTokenObj->getRefreshToken()),
        'expires_at' => Carbon::createFromTimestamp(
            $accessTokenObj->getAccessTokenExpiresAt()
        )
    ]);

    // Reconfigure DataService with new token
    $this->service->updateOAuth2Token($accessTokenObj);

    // Log refresh event
    LogService::store(
        'QBO Token Refreshed',
        "New expiration: {$this->access_key->expires_at}"
    );
}
```

**Key Points:**
- ✅ Happens automatically, transparently to application
- ✅ No user interaction required
- ✅ Updates both access and refresh tokens
- ✅ Extends refresh token lifetime by 60 days
- ✅ Logged for debugging

---

## Multi-Tenant Support

### Organization-Scoped Tokens

Each organization can connect to a different QuickBooks company:

```php
// Organization A connects to QuickBooks Company "ABC Corp"
QboAccessKey: user_id=1, org_id=5, realm_id="123456789"

// Organization B connects to QuickBooks Company "XYZ LLC"
QboAccessKey: user_id=1, org_id=8, realm_id="987654321"
```

**Same user, different QuickBooks companies based on active organization.**

### Active Organization Context

```php
// User selects active organization
session(['org' => $organization->id]);

// QuickBooksApi uses active org
$qbo = new QuickBooksApi();
$qbo->set_user($user); // Uses $user->active_org->id

// All API calls scoped to this organization's QuickBooks connection
```

### Switching Organizations

```php
// User switches organization
$user->setActiveOrg($newOrg);

// Next QuickBooks API call uses new org's connection
$qbo = new QuickBooksApi();
$qbo->set_user($user); // Now uses different QuickBooks company
```

**Important:** If new organization doesn't have QuickBooks connected, `set_user()` will throw an exception.

---

## Configuration

### Environment Variables

**Required in `.env`:**

```env
# QuickBooks OAuth Credentials
QUICKBOOKS_CLIENT_ID=your_client_id_here
QUICKBOOKS_CLIENT_SECRET=your_client_secret_here

# QuickBooks Environment
QUICKBOOKS_BASE_URL=https://sandbox-quickbooks.api.intuit.com
# Production: https://quickbooks.api.intuit.com

# OAuth Redirect URI
APP_URL=https://your-domain.com
```

### Config File

**Location:** `config/budtags.php`

```php
return [
    'quickbooks_client_id' => env('QUICKBOOKS_CLIENT_ID'),
    'quickbooks_client_secret' => env('QUICKBOOKS_CLIENT_SECRET'),
    'quickbooks_base_url' => env('QUICKBOOKS_BASE_URL'),
    'quickbooks_redirect_uri' => env('APP_URL') . '/quickbooks/callback',
];
```

### Obtaining Credentials

**Steps:**
1. Go to [Intuit Developer Portal](https://developer.intuit.com/)
2. Create app or use existing app
3. Get Client ID and Client Secret from app settings
4. Add redirect URI: `{YOUR_DOMAIN}/quickbooks/callback`
5. Enable "Accounting" scope

**Sandbox vs Production:**
- **Sandbox:** For testing with sandbox QuickBooks companies
- **Production:** For live QuickBooks companies
- **URLs are different** (see QUICKBOOKS_BASE_URL above)

---

## Troubleshooting

### Common Issues

#### Issue: "Invalid OAuth state"

**Cause:** CSRF state mismatch

**Solutions:**
- Browser session expired during OAuth flow
- User navigated away and came back
- Session storage issue

**Fix:**
```php
// Restart OAuth flow
return redirect('/quickbooks/login');
```

---

#### Issue: "No QuickBooks connection found"

**Error:** Exception thrown by `set_user()`

**Cause:** User/organization doesn't have QboAccessKey record

**Solutions:**
```php
// Check if connected before using API
$hasConnection = QboAccessKey::where('user_id', $user->id)
    ->where('org_id', $user->active_org->id)
    ->exists();

if (!$hasConnection) {
    return redirect('/quickbooks/login')->with('error', 'Please connect QuickBooks');
}
```

---

#### Issue: "Token expired" or "Invalid refresh token"

**Cause:** Refresh token expired (after 60 days of no use)

**Solution:**
```php
// Catch refresh token error
try {
    $qbo->refresh_token();
} catch (\Exception $e) {
    // Refresh token expired, need to re-authorize
    $this->access_key->delete();

    return redirect('/quickbooks/login')
        ->with('error', 'QuickBooks connection expired. Please reconnect.');
}
```

**Prevention:**
- Use QuickBooks integration regularly (at least once per 60 days)
- Background job to refresh tokens weekly

---

#### Issue: "Realm ID mismatch"

**Cause:** Trying to use tokens for different QuickBooks company

**Solution:**
- Tokens are company-specific
- Must re-authorize if company changes
- Check realm_id matches

---

#### Issue: "Redirect URI mismatch"

**Error from QuickBooks:** "redirect_uri doesn't match registered URI"

**Cause:** OAuth callback URI doesn't match Intuit app settings

**Solution:**
1. Check `.env` APP_URL matches deployed domain
2. Check Intuit app settings include exact callback URI
3. Ensure HTTPS in production (QuickBooks requires HTTPS for production)

**Registered URI must exactly match:**
```
{APP_URL}/quickbooks/callback
```

---

### Debugging OAuth Flow

**Enable detailed logging:**

```php
// In oauth_begin()
Log::info('OAuth Begin', [
    'user_id' => auth()->id(),
    'org_id' => auth()->user()->active_org->id,
    'state' => $state,
    'auth_url' => $authUrl
]);

// In oauth_complete()
Log::info('OAuth Callback', [
    'code' => $request->code,
    'state' => $request->state,
    'realm_id' => $request->realmId,
    'session_state' => session('oauth_state')
]);

Log::info('Tokens Received', [
    'access_token_length' => strlen($accessToken),
    'refresh_token_length' => strlen($refreshToken),
    'expires_at' => $expiresAt
]);
```

**Check database:**
```sql
SELECT
    user_id,
    org_id,
    realm_id,
    expires_at,
    created_at,
    updated_at
FROM qbo_access_keys
WHERE user_id = ?;
```

---

### Testing OAuth Flow

**Manual Test:**
1. Delete existing QboAccessKey for test user/org
2. Visit `/quickbooks/login`
3. Authorize on QuickBooks sandbox
4. Verify redirect to `/quickbooks/callback`
5. Check database for new QboAccessKey record
6. Try making API call (e.g., `get_company_info()`)

**Automated Test:**
```php
// Feature test
public function test_oauth_flow()
{
    $user = User::factory()->create();
    $org = Organization::factory()->create();
    $user->setActiveOrg($org);

    // Simulate OAuth callback
    $response = $this->actingAs($user)->get('/quickbooks/callback', [
        'code' => 'fake_auth_code',
        'state' => session('oauth_state'),
        'realmId' => '123456789'
    ]);

    // Assert token stored
    $this->assertDatabaseHas('qbo_access_keys', [
        'user_id' => $user->id,
        'org_id' => $org->id,
        'realm_id' => '123456789'
    ]);
}
```

---

## Security Considerations

### Token Encryption

**All tokens are encrypted at rest:**
```php
'access_key' => encrypt($accessToken)
```

**Laravel encryption uses:**
- AES-256-CBC cipher
- APP_KEY as encryption key
- Automatically decrypted when retrieved

**Never log or expose tokens:**
```php
// ❌ WRONG
Log::info('Access Token: ' . $accessToken);

// ✅ CORRECT
Log::info('Access Token Length: ' . strlen($accessToken));
```

---

### CSRF Protection

**State parameter prevents CSRF attacks:**

```php
// Generate random state
$state = Str::random(40);
session(['oauth_state' => $state]);

// Include in auth URL
$authUrl = $oauth2Helper->getAuthorizationCodeURL() . "&state={$state}";

// Validate on callback
if ($request->state !== session('oauth_state')) {
    abort(403, 'Invalid OAuth state');
}
```

---

### HTTPS Requirement

**Production Requirements:**
- QuickBooks REQUIRES HTTPS for production apps
- Redirect URI must use `https://`
- Sandbox allows HTTP for testing

**Enforce HTTPS:**
```php
// In AppServiceProvider
if (app()->environment('production')) {
    URL::forceScheme('https');
}
```

---

## Disconnecting QuickBooks

**Route:** `GET /quickbooks/logout`

**Controller:**
```php
public function logout()
{
    $user = auth()->user();

    QboAccessKey::where('user_id', $user->id)
        ->where('org_id', $user->active_org->id)
        ->delete();

    LogService::store('QuickBooks Disconnected', '');

    return redirect('/quickbooks/dashboard')
        ->with('success', 'QuickBooks disconnected');
}
```

**What Happens:**
- Deletes QboAccessKey record from database
- Tokens removed from application
- QuickBooks still shows app as authorized (user must manually revoke in QuickBooks settings)
- User must re-authorize to reconnect

---

## Next Steps

Now that you understand OAuth authentication, explore the workflows:

- **[WORKFLOWS/INVOICE_WORKFLOW.md](WORKFLOWS/INVOICE_WORKFLOW.md)** - Create and manage invoices
- **[WORKFLOWS/PAYMENT_WORKFLOW.md](WORKFLOWS/PAYMENT_WORKFLOW.md)** - Record payments
- **[WORKFLOWS/METRC_SYNC_WORKFLOW.md](WORKFLOWS/METRC_SYNC_WORKFLOW.md)** - Sync inventory from Metrc
- **[OPERATIONS_CATALOG.md](OPERATIONS_CATALOG.md)** - All available operations
