# Backend Critical Patterns

**Source:** `.claude/docs/backend/coding-style.md`, `.claude/docs/backend/multi-tenancy.md`
**Last Updated:** 2026-01-08
**Pattern Count:** 9 critical rules

---

## Overview

These are **SECURITY-CRITICAL** patterns that must NEVER be violated. Violations can lead to:
- Cross-organization data leaks
- Unauthorized access to sensitive data
- Audit trail gaps
- Permission bypass

---

## Pattern 1: Organization Scoping (HIGHEST PRIORITY)

**Rule:** ALL database queries MUST be scoped to `request()->user()->active_org_id`.

### ✅ CORRECT

```php
// Scope queries to active organization
$strains = request()->user()->active_org->strains()->get();

// Use active_org_id directly (preferred - no extra query)
$item = NonMetrcItem::create([
    ...$values,
    'organization_id' => request()->user()->active_org_id,
]);

// With comment explaining security boundary
// don't let users view strains from other orgs
$strains = request()->user()->active_org->strains()->get();
```

### ❌ WRONG

```php
// NOT scoped to organization - SECURITY VIOLATION!
$strains = Strain::all();

// Loading relationship just to access ID - inefficient
$org = request()->user()->active_org;
$org_id = $org->id;  // Should use: request()->user()->active_org_id
```

---

## Pattern 2: Active Org ID Access

**Rule:** Use `active_org_id` property directly, DON'T load `active_org` relationship just for ID.

### ✅ CORRECT

```php
// Direct property access - no extra query
$org_id = request()->user()->active_org_id;

$label = Label::create([
    'name' => $name,
    'organization_id' => request()->user()->active_org_id,
]);
```

### ❌ WRONG

```php
// Loading full relationship just to get ID - waste of query
$org = request()->user()->active_org;
$org_id = $org->id;

// Using auth()->user() instead of request()->user()
$org_id = auth()->user()->active_org_id;  // Use request()->user()
```

---

## Pattern 3: Authorization Checks with Comments

**Rule:** ALWAYS add comments explaining what's being protected and WHY.

### ✅ CORRECT

```php
// don't let users of other orgs view logs
abort_if($item->organization_id !== request()->user()->active_org_id, 403);

// ensure user has permission to edit labels in their active org
abort_unless(request()->user()->can_in_active_org('edit-labels'), 403);

// verify package belongs to user's organization before allowing edit
if ($package->organization_id !== request()->user()->active_org_id) {
    abort(403, 'Cannot modify packages from another organization');
}
```

### ❌ WRONG

```php
// No comment - unclear what's being protected
abort_if($item->organization_id !== request()->user()->active_org_id, 403);

// No authorization check at all - SECURITY VIOLATION!
public function delete(Label $label) {
    $label->delete();  // Missing check!
}
```

---

## Pattern 4: Permission Checks

**Rule:** Use `org:permission-name` middleware OR `can_in_active_org('permission')` method.

### ✅ CORRECT - Middleware

```php
// In routes/web.php
Route::middleware(['auth', 'has-org', 'org:edit-labels'])->group(function () {
    Route::post('/labels/create', [LabelController::class, 'create']);
    Route::patch('/labels/{label}', [LabelController::class, 'update']);
});
```

### ✅ CORRECT - Programmatic Check

```php
// In controller method
public function approve(Label $label) {
    // ensure user has approve-labels permission in active org
    abort_unless(request()->user()->can_in_active_org('approve-labels'), 403);

    $label->update(['approved' => true]);
    return redirect()->back()->with('message', 'Label approved');
}
```

### ❌ WRONG

```php
// No permission check - anyone can edit!
Route::post('/labels/create', [LabelController::class, 'create']);

// Using wrong permission check method
if (request()->user()->hasPermission('edit-labels')) {  // Wrong method!
    // ...
}
```

---

## Pattern 5: Logging (CRITICAL)

**Rule:** ALWAYS use `LogService::store()`. NEVER use `Log::` facade or `\Log::`.

### ✅ CORRECT

```php
use App\Services\LogService;

LogService::store(
    'Package Created',
    "Created package {$package->Tag} with {$package->Quantity} units",
    $package
);

LogService::store(
    'Strain Updated',
    "Updated strain name from '{$oldName}' to '{$newName}'",
    $strain
);
```

### ❌ WRONG

```php
// NEVER use Laravel's Log facade!
\Log::info('Package created');
Log::info('Action performed');

// No logging at all - missing audit trail
public function delete(Strain $strain) {
    $strain->delete();
    // Missing: LogService::store('Strain Deleted', ...)
}
```

---

## Pattern 6: Cross-Org Access Prevention

**Rule:** ALWAYS verify model belongs to active org before operations.

### ✅ CORRECT

```php
public function update(Label $label) {
    // don't let users edit labels from other orgs
    abort_if($label->organization_id !== request()->user()->active_org_id, 403);

    $values = request()->validate([
        'name' => 'string|required',
    ]);

    $label->update($values);
    LogService::store('Label Updated', "Updated label {$label->name}", $label);

    return redirect()->back()->with('message', 'Label updated');
}
```

### ❌ WRONG

```php
public function update(Label $label) {
    // No org check - SECURITY VIOLATION!
    // Users can edit labels from other orgs by changing URL!

    $label->update(request()->all());
    return redirect()->back();
}
```

---

## Pattern 7: Creating Org-Scoped Models

**Rule:** ALWAYS set `organization_id` when creating models.

### ✅ CORRECT

```php
public function create() {
    $values = request()->validate([
        'name' => 'string|required',
        'description' => 'string|nullable',
    ]);

    $strain = Strain::create([
        ...$values,
        'organization_id' => request()->user()->active_org_id,
    ]);

    LogService::store('Strain Created', "Created strain {$strain->name}", $strain);

    return redirect()->back()->with('message', 'Strain created successfully');
}
```

### ❌ WRONG

```php
public function create() {
    $validated = request()->validate([...]);

    // Mutating validated data - anti-pattern!
    $validated['organization_id'] = request()->user()->active_org_id;

    // Not using spread operator - harder to track what's being set
    $strain = Strain::create($validated);

    return redirect()->back();
}
```

---

## Pattern 8: Multi-Tenancy Comments

**Rule:** Add comments explaining multi-tenancy boundaries.

### ✅ CORRECT

```php
public function fetch_strains() {
    // don't let users view strains from other orgs
    $strains = request()->user()->active_org->strains()->get();

    return response()->json($strains);
}

public function delete(Strain $strain) {
    // verify strain belongs to user's organization
    abort_if($strain->organization_id !== request()->user()->active_org_id, 403);

    $strain->delete();
    LogService::store('Strain Deleted', "Deleted strain {$strain->name}", $strain);

    return redirect()->back()->with('message', 'Strain deleted');
}
```

### ❌ WRONG

```php
public function fetch_strains() {
    // No comment - unclear why we're scoping
    $strains = request()->user()->active_org->strains()->get();
    return response()->json($strains);
}
```

---

## Pattern 9: Session-Cached Permission Checks

**Rule:** For permission checks that require external API calls, use session-cached data (populated by middleware) instead of making API calls on every check.

> **Source:** Nick's refactoring of FacilityPermissionsService (Jan 2026) - changed from API calls to session reads.

### ❌ WRONG - API Call Per Permission Check

```php
class FacilityPermissionsService {
    // Every call to can_access_plants() makes an API request!
    public function can_access_plants(string $license): bool {
        $perms = $this->get_facility_permissions($license);  // ← API CALL!
        return $perms['CanGrowPlants'] ?? false;
    }

    protected function get_facility_permissions(string $license): array {
        $facilities = $this->metrc_api->facilities();  // ← EXPENSIVE!
        foreach ($facilities as $facility) {
            if ($facility['License']['Number'] === $license) {
                return $facility['FacilityType'] ?? [];
            }
        }
        return [];
    }
}

// Usage in controller - triggers API call every time!
if ($perms->can_access_plants(session('license'))) {
    // ...
}
```

### ✅ CORRECT - Session-Cached Check

```php
class FacilityPermissionsService {
    // Read from session - no API call!
    // Middleware already populated session('facility_permissions')
    public function can_access_plants(): bool {
        return session('facility_permissions')['can_grow_plants'] ?? false;
    }

    public function can_sell_to_consumers(): bool {
        return session('facility_permissions')['can_sell_to_consumers'] ?? false;
    }

    public function is_retail(): bool {
        return session('facility_permissions')['is_retail'] ?? false;
    }
}

// Usage in controller - instant, no API call
if ($perms->can_access_plants()) {
    // ...
}
```

### How It Works

1. **Middleware** fetches facility data once per session:
```php
// EnsureUserHasFacilities middleware
$facilities = $this->api->facilities();  // One API call
$perms = $this->permission_service()->extract_facility_permissions($facilities, $license);
session(['facility_permissions' => $perms]);  // Cache in session
```

2. **Services** read from session (no API call):
```php
public function can_access_plants(): bool {
    return session('facility_permissions')['can_grow_plants'] ?? false;
}
```

3. **License changes** trigger session refresh (middleware runs again)

### When to Use This Pattern

| Scenario | Pattern |
|----------|---------|
| Permission checks in controllers | Session-cached |
| Initial login / license selection | Middleware populates session |
| Admin dashboard (needs fresh data) | Direct API call |
| Webhook processing | Direct API call (no session) |

### Key Insight

Session-cached permissions turn **O(n) API calls** into **O(1) session reads**.

If a page checks 5 different permissions, that's potentially 5 API calls saved per page load.

---

## Verification Checklist

When reviewing backend code, verify:

### Organization Scoping
- [ ] All queries scoped to `active_org` or `active_org_id`
- [ ] No `Model::all()` without org scope
- [ ] No `Model::find()` without subsequent org check
- [ ] Models created with `organization_id` field

### Authorization
- [ ] Cross-org access prevented with `abort_if` checks
- [ ] Comments explain what's being protected
- [ ] Permission checks via middleware or `can_in_active_org()`
- [ ] Route middleware includes `org:permission-name` where needed

### Logging
- [ ] Uses `LogService::store()` for all actions
- [ ] NEVER uses `Log::` facade or `\Log::`
- [ ] Log messages descriptive (action + details)
- [ ] Related model passed to `LogService::store()`

### Access Patterns
- [ ] Uses `active_org_id` property (not loading relationship for ID)
- [ ] Uses `request()->user()` (not `auth()->user()`)
- [ ] Comments explain security boundaries

### Session-Cached Permissions
- [ ] Permission checks read from session, not API
- [ ] Middleware populates `session('facility_permissions')`
- [ ] No redundant API calls for permission checks

---

## Common Violations

### Violation 1: Unscoped Queries

```php
// ❌ Returns ALL strains from ALL organizations!
$strains = Strain::all();

// ✅ Fix
$strains = request()->user()->active_org->strains()->get();
```

### Violation 2: Missing Org Check Before Update/Delete

```php
// ❌ Users can edit any label by changing URL!
public function update(Label $label) {
    $label->update(request()->all());
}

// ✅ Fix
public function update(Label $label) {
    abort_if($label->organization_id !== request()->user()->active_org_id, 403);
    $label->update(request()->validate([...]));
}
```

### Violation 3: Using Log Facade

```php
// ❌ Bypasses BudTags logging system!
Log::info('Package created');

// ✅ Fix
LogService::store('Package Created', 'Created package #123', $package);
```

### Violation 4: No Comments on Security Checks

```php
// ❌ Unclear what's being protected
abort_if($item->organization_id !== request()->user()->active_org_id, 403);

// ✅ Fix with comment
// don't let users delete items from other organizations
abort_if($item->organization_id !== request()->user()->active_org_id, 403);
```

---

## Security Impact

| Violation | Impact | Severity |
|-----------|--------|----------|
| Unscoped queries | Data leak across organizations | **CRITICAL** |
| Missing org check | Users can access/modify other orgs' data | **CRITICAL** |
| No logging | Missing audit trail, compliance issues | **HIGH** |
| Missing permission check | Unauthorized access to features | **HIGH** |
| No security comments | Maintainability issue, unclear intent | **MEDIUM** |

---

## Related Patterns

- **backend-style.md** - Method naming, request handling
- **backend-flash-messages.md** - User feedback patterns
- **database.md** - Schema compliance, relationships
- `.claude/docs/backend/multi-tenancy.md` - Complete multi-tenancy guide
- `.claude/docs/backend/coding-style.md` - Full coding standards
