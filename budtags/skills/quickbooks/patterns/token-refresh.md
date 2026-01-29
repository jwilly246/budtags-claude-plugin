# QuickBooks Token Refresh Pattern

**Pattern:** Automatic Token Refresh
**Trigger:** Before every API call
**Threshold:** 5 minutes before expiration

---

## Overview

QuickBooks access tokens expire after 1 hour. The integration automatically refreshes tokens before they expire using the refresh token.

**Key Concepts:**
- Access token lifespan: 1 hour
- Refresh token lifespan: 100 days
- Auto-refresh: Triggered 5 minutes before expiration
- Transparent: No user action required

---

## Auto-Refresh Logic

### When It Triggers

**Before Every API Call:**
```php
public function set_user(User $user): void {
    // Load access key
    $this->access_key = QboAccessKey::where('user_id', $user->id)
        ->where('org_id', $user->active_org->id)
        ->first();

    // Check if token needs refresh (5-minute buffer)
    if ($this->access_key->expires_at < now()->addMinutes(5)) {
        $this->refresh_token();
    }

    // Configure DataService
    $this->setupDataService();
}
```

**5-Minute Buffer:**
- Prevents race conditions
- Ensures token valid for entire API call
- Handles clock skew between servers

---

## Refresh Process

### Step 1: Check Expiration

```php
if ($this->access_key->expires_at < now()->addMinutes(5)) {
    $this->refresh_token();
}
```

### Step 2: Exchange Refresh Token

```php
public function refresh_token(): void {
    $oauth2 = new OAuth2LoginHelper(
        config('quickbooks.client_id'),
        config('quickbooks.client_secret')
    );

    // Exchange refresh token for new access token
    $accessTokenObj = $oauth2->refreshAccessTokenWithRefreshToken(
        $this->access_key->refresh_key
    );

    // Update database
    $this->access_key->update([
        'access_key' => $accessTokenObj->getAccessToken(),
        'refresh_key' => $accessTokenObj->getRefreshToken(),
        'expires_at' => now()->addSeconds($accessTokenObj->getAccessTokenExpiresAt())
    ]);

    // Log refresh event
    LogService::store(
        'QuickBooks Token Refreshed',
        "Access token refreshed for org {$this->user->active_org->id}"
    );
}
```

### Step 3: Update DataService

After refresh, DataService automatically uses new token (configured in set_user()).

---

## Token Lifespan

### Access Token

**Lifespan:** 1 hour (3600 seconds)
**Stored:** `expires_at` timestamp in database
**Refresh:** Automatic when < 5 minutes remaining

### Refresh Token

**Lifespan:** 100 days (default QuickBooks setting)
**Stored:** Encrypted in `refresh_key` column
**Usage:** Only during token refresh
**Renewal:** QuickBooks provides new refresh token with each refresh

**Critical:** If refresh token expires (100 days of inactivity), user must re-authorize via OAuth flow.

---

## Error Handling

### Refresh Token Expired

**Scenario:** User hasn't used QuickBooks for 100+ days

**Error:**
```
Exception: Refresh token expired
```

**Solution:**
```php
try {
    $this->refresh_token();
} catch (Exception $e) {
    if (str_contains($e->getMessage(), 'Refresh token expired')) {
        // Delete expired connection
        $this->access_key->delete();

        // Redirect to re-authorize
        throw new Exception('QuickBooks connection expired. Please reconnect.');
    }

    throw $e;
}
```

**User Action Required:** Must go through OAuth flow again

---

### Network/API Failures

**Scenario:** QuickBooks API temporarily unavailable

**Error:**
```
Exception: Failed to refresh token - network error
```

**Solution:**
```php
try {
    $this->refresh_token();
} catch (Exception $e) {
    // Log error
    LogService::store(
        'QuickBooks Token Refresh Failed',
        $e->getMessage()
    );

    // Retry with exponential backoff
    sleep(2);
    $this->refresh_token();
}
```

---

## Logging

### Successful Refresh

```php
LogService::store(
    'QuickBooks Token Refreshed',
    "Access token refreshed for org {$org_id}"
);
```

### Failed Refresh

```php
LogService::store(
    'QuickBooks Token Refresh Failed',
    "Error: {$error_message}\nOrg: {$org_id}"
);
```

**See:** `patterns/logging.md` for logging patterns

---

## Testing Token Refresh

### Force Expiration (Development)

```php
// In tinker or test
$accessKey = QboAccessKey::first();
$accessKey->update(['expires_at' => now()->subMinute()]);

// Next API call will trigger refresh
$qbo = new QuickBooksApi();
$qbo->set_user($user);
// Token automatically refreshed here
$customers = $qbo->get_all_customers();
```

### Monitor Refresh Events

```sql
SELECT * FROM logs
WHERE title = 'QuickBooks Token Refreshed'
ORDER BY created_at DESC
LIMIT 10;
```

---

## Best Practices

✅ **ALWAYS use 5-minute buffer** - Prevents token expiration mid-request
✅ **ALWAYS log refresh events** - Track token health
✅ **ALWAYS handle refresh token expiration** - Prompt user to reconnect
✅ **ALWAYS store both tokens after refresh** - QuickBooks provides new refresh token

❌ **NEVER skip expiration check** - Could cause API failures
❌ **NEVER store only access token** - Need refresh token for renewal
❌ **NEVER ignore refresh errors** - Could indicate expired connection
❌ **NEVER manually refresh tokens** - Auto-refresh handles it

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
$this->access_key->update([
    'access_key' => $new_access_token,
    'refresh_key' => $new_refresh_token,  // NEW token
    'expires_at' => $new_expiration
]);
```

```php
// ❌ WRONG - Only updating access token
$this->access_key->update([
    'access_key' => $new_access_token,
    // Missing refresh_key update - old refresh token becomes invalid!
    'expires_at' => $new_expiration
]);
```

---

## Related Patterns

- `patterns/authentication.md` - Initial OAuth flow
- `patterns/multi-tenancy.md` - Organization-scoped tokens
- `patterns/error-handling.md` - Handling token errors
- `categories/authentication.md` - Authentication operations
