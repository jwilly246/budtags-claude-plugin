# Scenario: New Controller Method

**Use this checklist when verifying new controller methods.**

---

## Required Pattern Files

Load these patterns before verification:
- `patterns/backend-critical.md` - Organization scoping, logging
- `patterns/backend-style.md` - Method naming, request handling
- IF forms: `patterns/backend-flash-messages.md`
- IF API calls: `patterns/integrations.md`

---

## Verification Checklist

### Static Analysis (REQUIRED)
- [ ] PHPStan passes at level 10: `./vendor/bin/phpstan analyse [file]`
- [ ] Pint passes: `./vendor/bin/pint [file] --test`
- [ ] Code written with intention to pass (not fixed after)
- [ ] No `@phpstan-ignore` without justification

### Method Naming & Structure
- [ ] Method name is `snake_case` with verb-first naming
- [ ] Uses `create()` not `store()`, `delete()` not `destroy()`
- [ ] No camelCase methods (e.g., `bulkAdjust` → `adjust_bulk`)
- [ ] Clear, descriptive method name (e.g., `fetch_active_packages`)

### Request Handling
- [ ] Uses `request()` helper (not `Request $request` injection)
- [ ] Uses `request()->user()` (not `auth()->user()`)
- [ ] Validation rules inline at point of use
- [ ] Uses `$values` variable for validated data
- [ ] No mutating validated data

### Organization Scoping (CRITICAL)
- [ ] All queries scoped to `active_org` or `active_org_id`
- [ ] Uses `request()->user()->active_org->model()->get()`
- [ ] Models created with `organization_id` field
- [ ] Comment explains security boundary

### Authorization & Security
- [ ] Cross-org access prevented with `abort_if` check
- [ ] Comment explains what's being protected
- [ ] Permission check via middleware or `can_in_active_org()`
- [ ] Model belongs to active org verified before operations

### Logging
- [ ] Uses `LogService::store()` for actions
- [ ] NEVER uses `Log::` facade or `\Log::`
- [ ] Log message descriptive (action + details)
- [ ] Related model passed to LogService

### Dependency Injection
- [ ] Method-level injection for single-use services
- [ ] Constructor injection only when service used by ALL methods
- [ ] No over-injection

### Array Composition
- [ ] Uses spread operator (`...$values`)
- [ ] Clear separation between validated and additional fields
- [ ] No `array_merge()` for simple composition

### Return & Redirect
- [ ] Consistent `redirect()->back()` usage
- [ ] Includes `->with('message')` for success (NOT `->with('success')`)
- [ ] Error handling with `->with('error')`
- [ ] No hard-coded URLs in redirects

### Routes (if adding/modifying)
- [ ] Route names use single words or dashes (NOT dots)
- [ ] Examples: `'users-edit'`, `'labels-create'`, `'pick-license'`
- [ ] NO dot notation: `'profile.edit'` should be `'profile-edit'`
- [ ] Verified existing routes follow dash pattern

---

## Common Issues to Check

### Issue 1: Unscoped Query
```php
// ❌ WRONG
$items = Item::all();

// ✅ FIX
$items = request()->user()->active_org->items()->get();
```

### Issue 2: Wrong Flash Key
```php
// ❌ WRONG
return redirect()->back()->with('success', 'Item created');

// ✅ FIX
return redirect()->back()->with('message', 'Item created');
```

### Issue 3: No Org Check Before Update
```php
// ❌ WRONG
public function update(Item $item) {
    $item->update(request()->all());
}

// ✅ FIX
public function update(Item $item) {
    abort_if($item->organization_id !== request()->user()->active_org_id, 403);
    $values = request()->validate([...]);
    $item->update($values);
}
```

### Issue 4: No Logging
```php
// ❌ WRONG - No audit trail
$item->delete();

// ✅ FIX
$item->delete();
LogService::store('Item Deleted', "Deleted item {$item->name}", $item);
```

### Issue 5: Wrong Route Naming
```php
// ❌ WRONG - Uses dot notation
Route::get('/updates/{announcement}', ...)->name('updates.show');

// ✅ FIX - Use dashes or single word
Route::get('/updates/{announcement}', ...)->name('updates');
// OR
Route::get('/updates/{announcement}', ...)->name('updates-show');
```

---

## Priority Levels

**CRITICAL** (Must fix immediately):
- Organization scoping violations
- Cross-org access vulnerabilities
- Missing authorization checks
- Using Log facade instead of LogService

**HIGH** (Fix before merging):
- Wrong method naming (store/destroy)
- Missing flash messages
- No error handling

**MEDIUM** (Fix when convenient):
- camelCase methods
- Request injection
- Inconsistent patterns
- Route naming (dots instead of dashes)

---

## Example: Compliant Controller Method

```php
public function create() {
    $values = request()->validate([
        'name' => 'string|required|max:255',
        'quantity' => 'integer|required|min:0',
    ]);

    $item = Item::create([
        ...$values,
        'organization_id' => request()->user()->active_org_id,
    ]);

    LogService::store('Item Created', "Created item {$item->name}", $item);

    return redirect()->back()->with('message', 'Item created successfully');
}

public function delete(Item $item) {
    // don't let users delete items from other organizations
    abort_if($item->organization_id !== request()->user()->active_org_id, 403);

    $item->delete();
    LogService::store('Item Deleted', "Deleted item {$item->name}", $item);

    return redirect()->back()->with('message', 'Item deleted');
}
```

---

## Related Scenarios

- `migration.md` - For database changes
- `react-component.md` - For frontend components
- `inertia-form.md` - For form submissions
- `react-query-hook.md` - For React Query data fetching
