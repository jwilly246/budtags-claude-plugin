# Backend Style Patterns

**Source:** `.claude/docs/backend/coding-style.md`, `.claude/docs/backend/architecture.md`
**Last Updated:** 2026-01-09
**Pattern Count:** 12 style rules (includes Pattern 0: Static Analysis)

---

## Overview

These patterns ensure **consistency and maintainability** across the BudTags codebase. While not security-critical like organization scoping, they significantly impact code quality and developer experience.

---

## Pattern 0: Static Analysis (PHPStan + Pint) - REQUIRED

**Rule:** ALL PHP code must pass PHPStan level 10 and Pint formatting. Write code with the intention of passing - don't fix after the fact.

> **Enforcement:** Pre-commit hook (`.husky/pre-commit`) runs on ALL branches.

### Required Tools

| Tool | Level/Preset | Config File | Purpose |
|------|--------------|-------------|---------|
| PHPStan + Larastan | Level 10 | `phpstan.neon` | Static type analysis (Laravel-aware) |
| Pint | Laravel preset | `pint.json` | Code formatting |

> **Note:** Larastan (`vendor/larastan/larastan/extension.neon`) is required for accurate Laravel analysis - it understands Eloquent relationships, facades, request helpers, etc.

### ✅ Run Before Committing

```bash
# Run both in parallel on your changed files
./vendor/bin/phpstan analyse app/Http/Controllers/MyController.php --memory-limit=512M &
./vendor/bin/pint app/Http/Controllers/MyController.php --test &
wait

# Or let the pre-commit hook handle it (runs automatically)
git commit -m "Your message"
# → Pint auto-fixes and re-stages
# → PHPStan blocks if issues found
```

### Writing PHPStan-Clean Code

```php
// ✅ CORRECT - Explicit types, null handling
public function fetch_packages(): array {
    $user = request()->user();
    if (!$user) {
        return [];
    }

    /** @var \App\Models\User $user */
    $packages = $user->active_org->packages()->get();

    return $packages->toArray();
}

// ❌ WRONG - Missing null checks, unclear types
public function fetch_packages() {
    $packages = request()->user()->active_org->packages()->get();
    return $packages;  // Return type unclear
}
```

### Common PHPStan Issues & Fixes

```php
// Issue: "Cannot call method on mixed"
// Fix: Add type annotation or null check
/** @var User $user */
$user = request()->user();

// Issue: "Parameter expects string, mixed given"
// Fix: Cast or validate
$name = (string) request()->input('name');

// Issue: "Return type includes null but never returns null"
// Fix: Remove null from return type if truly never null
public function get_name(): string {  // Not ?string
    return $this->name ?? 'Default';
}
```

### PHPDoc Import Style

**Rule:** Use imported class names in `@var` and `@param` annotations. Import classes even if only used in docblocks.

```php
// ✅ CORRECT - Import and use short name
use Illuminate\Support\Collection;
use App\Models\Product;

/** @var Collection<int, Product> $products */
$products = $org->products()->get();

// ❌ WRONG - Fully qualified paths in annotations
/** @var \Illuminate\Support\Collection<int, \App\Models\Product> $products */
$products = $org->products()->get();
```

**Why import over fully qualified?**
- **Readability** - Short names are easier to scan
- **Consistency** - Same style as actual code usage
- **Refactoring** - If namespace changes, only imports update
- **IDE support** - Better autocomplete and "find usages"

### Pint Formatting

Pint auto-fixes most issues. Key rules from `pint.json`:
- Laravel preset (PSR-12 based)
- Opening braces on same line
- No space after `!` operator
- Minimal class attribute separation

### Verification Checklist

- [ ] `./vendor/bin/phpstan analyse [files]` passes
- [ ] `./vendor/bin/pint [files] --test` shows no changes needed
- [ ] No `@phpstan-ignore` without justification comment
- [ ] No `// @ts-ignore` equivalent workarounds
- [ ] PHPDoc annotations use imported class names (not fully qualified paths)

---

## Pattern 1: Method Naming (snake_case, verb-first)

**Rule:** Use `snake_case` with verb-first naming. NO `store()` or `destroy()` (use `create()` and `delete()`).

### ✅ CORRECT

```php
// CRUD operations
public function create()         // Not store()
public function update(Item $item)
public function delete(Item $item)  // Not destroy()

// Fetching data
public function fetch_logs()
public function fetch_active_packages()
public function fetch_items_by_category()

// Processing/exporting
public function export_inventory()
public function process_transfer()
public function adjust_bulk()      // Not bulkAdjust()
public function sync_quantities()

// Boolean checks
public function is_expired()
public function has_permission()
public function can_approve()
```

### ❌ WRONG

```php
// RESTful naming - NOT allowed
public function store()        // Use create()
public function destroy()      // Use delete()

// camelCase - NOT allowed
public function bulkAdjust()   // Use adjust_bulk()
public function syncQuantities()  // Use sync_quantities()
public function exportInventory()  // Use export_inventory()

// Unclear verbs
public function handle()       // Handle what?
public function process()      // Process what?
public function do_stuff()     // Too vague
```

---

## Pattern 2: Request Handling (use `request()` helper)

**Rule:** Use `request()` helper directly. DON'T inject `Request $request` unless absolutely necessary.

### ✅ CORRECT

```php
public function create() {
    $values = request()->validate([
        'name' => 'string|required',
        'quantity' => 'integer|required|min:0',
    ]);

    $user = request()->user();
    $ip = request()->ip();

    $item = Item::create([
        ...$values,
        'organization_id' => $user->active_org_id,
    ]);

    return redirect()->back()->with('message', 'Item created');
}
```

### ❌ WRONG

```php
// Request injection - unnecessary for simple cases
public function create(Request $request) {
    $validated = $request->validate([...]);
    $user = $request->user();

    // ...
}

// Using auth() instead of request()->user()
$user = auth()->user();  // Use request()->user()
```

### When Request Injection IS Acceptable

Only inject `Request` when:
- Using specialized request classes (e.g., `CreatePackageRequest`)
- Passing request to service methods
- Need request in multiple methods (constructor injection)

```php
// ✅ Acceptable - FormRequest
public function create(CreatePackageRequest $request) {
    $validated = $request->validated();
    // ...
}
```

---

## Pattern 3: Validation Patterns (inline at point of use)

**Rule:** Validation rules inline where used. Use `$values` for validated data.

### ✅ CORRECT

```php
public function update(Label $label) {
    $values = request()->validate([
        'name' => 'string|required|max:255',
        'width' => 'integer|required|min:1',
        'height' => 'integer|required|min:1',
    ]);

    $label->update($values);  // Clean, validated data

    return redirect()->back()->with('message', 'Label updated');
}
```

### ❌ WRONG

```php
public function update(Label $label) {
    // Mutating validated data - anti-pattern!
    $validated = request()->validate([...]);
    $validated['organization_id'] = request()->user()->active_org_id;
    $validated['updated_by'] = request()->user()->id;

    $label->update($validated);
}

// Validation rules in separate method - over-engineered
protected function getValidationRules(): array {
    return ['name' => 'required'];
}
```

---

## Pattern 4: Array Composition (spread operator)

**Rule:** Use spread operator (`...`) for array composition. Makes intent clear.

### ✅ CORRECT

```php
$values = request()->validate([
    'name' => 'string|required',
    'quantity' => 'integer|required',
]);

$package = Package::create([
    ...$values,
    'organization_id' => request()->user()->active_org_id,
    'created_by' => request()->user()->id,
]);
```

### ❌ WRONG

```php
// Mutating validated data
$validated = request()->validate([...]);
$validated['organization_id'] = request()->user()->active_org_id;
$package = Package::create($validated);

// array_merge - verbose
$package = Package::create(array_merge($validated, [
    'organization_id' => request()->user()->active_org_id,
]));
```

---

## Pattern 5: Dependency Injection (method-level preferred)

**Rule:** Method-level injection unless service used by ALL methods.

### ✅ CORRECT - Method-Level Injection

```php
class PackageController extends Controller
{
    // Only create() uses InventoryService - inject at method level
    public function create(InventoryService $inventoryService) {
        $values = request()->validate([...]);

        $package = Package::create([
            ...$values,
            'organization_id' => request()->user()->active_org_id,
        ]);

        $inventoryService->updateStock($package);

        return redirect()->back()->with('message', 'Package created');
    }

    // Other methods don't need InventoryService
    public function update(Package $package) {
        // ...
    }
}
```

### ✅ CORRECT - Constructor Injection (when used by ALL methods)

```php
class MetrcSyncController extends Controller
{
    public function __construct(
        private MetrcApi $metrcApi  // Used by ALL methods
    ) {}

    public function sync_packages() {
        $this->metrcApi->fetchPackages();
    }

    public function sync_plants() {
        $this->metrcApi->fetchPlants();
    }

    public function sync_transfers() {
        $this->metrcApi->fetchTransfers();
    }
}
```

### ❌ WRONG - Constructor Injection for Single-Use

```php
class PackageController extends Controller
{
    // ❌ Constructor injection for service used by only ONE method
    public function __construct(
        private InventoryService $inventoryService
    ) {}

    public function create() {
        // Only method using InventoryService
        $this->inventoryService->updateStock($package);
    }

    public function update(Package $package) {
        // Doesn't use InventoryService
    }

    public function delete(Package $package) {
        // Doesn't use InventoryService
    }
}
```

---

## Pattern 6: Redirect Patterns (consistent usage)

**Rule:** Use `redirect()->back()` consistently. Include `with('message')` for success feedback.

### ✅ CORRECT

```php
public function create() {
    $values = request()->validate([...]);

    $item = Item::create([
        ...$values,
        'organization_id' => request()->user()->active_org_id,
    ]);

    LogService::store('Item Created', "Created item {$item->name}", $item);

    return redirect()->back()->with('message', 'Item created successfully');
}

public function delete(Item $item) {
    abort_if($item->organization_id !== request()->user()->active_org_id, 403);

    $item->delete();
    LogService::store('Item Deleted', "Deleted item {$item->name}", $item);

    return redirect()->back()->with('message', 'Item deleted');
}
```

### ❌ WRONG

```php
// Inconsistent redirect usage
return back();  // Use redirect()->back()
return redirect('/items');  // Hard-coded URL
return response()->json(['success' => true]);  // Use Inertia
```

---

## Pattern 6.5: Graceful Authorization Degradation

**Rule:** For feature-gated pages (e.g., plant access requires cultivation license), use redirects instead of exceptions. Better UX for users who navigate to pages their license type doesn't support.

> **Source:** Nick's refactoring of FacilityPermissionsService (Jan 2026) - changed from throwing exceptions to redirects.

### ✅ CORRECT - Graceful Redirect

```php
use Inertia\Response;
use Illuminate\Http\RedirectResponse;

public function navigator_plants(MetrcApi $api, FacilityPermissionsService $perms): Response|RedirectResponse {
    // Check license capability, redirect if not supported
    if (!$perms->can_access_plants()) {
        return redirect()->to('/metrc/nav');  // User stays in app, no error page
    }

    // ... continue with plant-specific logic
    return Inertia::render('Plants', [...]);
}
```

### ❌ WRONG - Throwing Exceptions

```php
public function navigator_plants(MetrcApi $api, FacilityPermissionsService $perms): Response {
    // ❌ Throws 401 error page - harsh UX for legitimate users with wrong license type
    $perms->require_plant_access(session('license'));

    // User never sees this if they have a retail license
    return Inertia::render('Plants', [...]);
}
```

### When to Use Each Pattern

| Scenario | Pattern | Example |
|----------|---------|---------|
| **Feature not available for license type** | Redirect | Retail license accessing plants page |
| **User lacks permission** | `abort_if` | User without 'edit-labels' accessing edit |
| **Cross-org access attempt** | `abort_if` | User trying to access another org's data |
| **Invalid input** | Validation | Missing required fields |

### Key Insight

Exceptions are for **security violations** (someone trying to access what they shouldn't).
Redirects are for **capability mismatches** (someone navigating to a feature their license doesn't support).

---

## Pattern 7: Thin Controllers (Pass IDs, Not Models)

**Rule:** Controllers should ONLY validate, coordinate, and return responses. Model resolution and business logic belong in services.

### ✅ CORRECT - Controller Passes IDs to Service

```php
public function create(MessageService $message_service): JsonResponse {
    $values = request()->validate([
        'seller_organization_id' => 'required|uuid|exists:organizations,id',
        'brand_id' => 'nullable|uuid|exists:brands,id',
        'subject' => 'required|string|max:255',
        'message' => 'required|string|max:5000',
    ]);

    // Controller passes validated IDs - service resolves them
    $conversation = $message_service->find_or_create_conversation(
        request()->user()->active_org,
        $values['seller_organization_id'],  // Pass ID, not model
        $values['brand_id'] ?? null,        // Pass ID, not model
        $values['subject'],
        $values['message'],
        request()->user()
    );

    return response()->json([
        'conversation_id' => $conversation->id,
    ]);
}
```

```php
// Service resolves IDs and contains business logic
class MessageService {
    public function find_or_create_conversation(
        Organization $buyer_org,
        string $seller_org_id,
        ?string $brand_id,
        string $subject,
        string $message,
        User $sender
    ): Conversation {
        // Service resolves IDs to models
        $seller_org = Organization::findOrFail($seller_org_id);
        $brand = $brand_id ? Brand::find($brand_id) : null;

        // Business rules belong in service
        abort_if($buyer_org->id === $seller_org->id, 400, 'Cannot message your own organization');

        // Complex logic in service
        return DB::transaction(function () use (...) {
            // ...
        });
    }
}
```

### ❌ WRONG - Controller Resolves Models

```php
public function create(MessageService $message_service): JsonResponse {
    $values = request()->validate([...]);

    // ❌ Controller is resolving models - this belongs in service
    $seller_org = Organization::where('id', $values['seller_organization_id'])->firstOrFail();
    $brand = isset($values['brand_id']) ? Brand::find($values['brand_id']) : null;

    // ❌ Business rule in controller - belongs in service
    abort_if($buyer_org->id === $seller_org->id, 400, 'Cannot message your own organization');

    $conversation = $message_service->find_or_create_conversation(
        $buyer_org,
        $seller_org,  // ❌ Passing model instead of ID
        $brand,       // ❌ Passing model instead of ID
        // ...
    );
}
```

### What Belongs Where

| Concern | Controller | Service |
|---------|------------|---------|
| Validation (`request()->validate()`) | ✅ | ❌ |
| Authorization (`abort_if` for org access) | ✅ | ❌ |
| Model resolution from IDs | ❌ | ✅ |
| Business rules ("can't message self") | ❌ | ✅ |
| Database transactions | ❌ | ✅ |
| Logging (`LogService::store()`) | ❌ | ✅ |
| Event broadcasting | ❌ | ✅ |
| Response formatting | ✅ | ❌ |

### Why This Matters

1. **Testability** - Services can be unit tested with just IDs
2. **Single Responsibility** - "What models exist" is a service concern
3. **Reusability** - Same service method works from multiple controllers
4. **Clarity** - Controller signature shows it only needs validation

---

## Pattern 8: Service Layer (keep it simple)

**Rule:** Services only for multi-controller logic, APIs, or complex workflows. Simple logic stays in protected methods.

### ✅ CORRECT - Simple Validation in Controller

```php
class StrainController extends Controller
{
    public function create() {
        $this->validate_no_duplicates();

        $values = request()->validate([...]);
        $strain = Strain::create([
            ...$values,
            'organization_id' => request()->user()->active_org_id,
        ]);

        return redirect()->back()->with('message', 'Strain created');
    }

    protected function validate_no_duplicates(): void {
        $name = request()->input('name');
        $exists = request()->user()->active_org->strains()
            ->where('name', $name)
            ->exists();

        if ($exists) {
            throw ValidationException::withMessages([
                'name' => 'A strain with this name already exists',
            ]);
        }
    }
}
```

### ✅ CORRECT - Service for Multi-Controller Logic

```php
// LabelMakerService - used by multiple controllers, complex logic
class LabelController extends Controller
{
    public function create(LabelMakerService $labelMaker) {
        $label = $labelMaker->build_label($package, $template);
        // ...
    }
}

class PrintGroupController extends Controller
{
    public function create(LabelMakerService $labelMaker) {
        $labels = $labelMaker->build_labels_bulk($packages);
        // ...
    }
}
```

### ❌ WRONG - Over-Engineering

```php
// ❌ Single-method service for simple validation
class StrainValidationService
{
    public function validateNoDuplicates(string $name): void {
        // Simple logic that belongs in controller
    }
}

// Usage - over-engineered
public function create(StrainValidationService $validator) {
    $validator->validateNoDuplicates(request()->input('name'));
}
```

---

## Verification Checklist

When reviewing backend style, verify:

### Method Naming
- [ ] All methods use `snake_case`
- [ ] Verb-first naming (create, update, delete, fetch, export, process)
- [ ] No `store()` or `destroy()` (use `create()` and `delete()`)
- [ ] No camelCase method names

### Request Handling
- [ ] Uses `request()` helper (not `Request $request` injection)
- [ ] Uses `request()->user()` (not `auth()->user()`)
- [ ] Validation rules inline at point of use
- [ ] Uses `$values` variable name for validated data
- [ ] No mutating validated data

### Array Composition
- [ ] Uses spread operator (`...$values`)
- [ ] Clear separation between validated and additional fields
- [ ] No `array_merge()` for simple composition

### Dependency Injection
- [ ] Method-level injection for single-method usage
- [ ] Constructor injection only when service used by ALL methods
- [ ] No over-injection

### Thin Controllers
- [ ] Controller only validates, coordinates, and returns responses
- [ ] Model resolution from IDs happens in service, not controller
- [ ] Business rules (e.g., "can't message self") are in service
- [ ] Database transactions wrapped in service
- [ ] Logging and event broadcasting in service

### Redirects
- [ ] Consistent `redirect()->back()` usage
- [ ] Includes `->with('message')` for success feedback
- [ ] No hard-coded URLs

### Service Layer
- [ ] Services only for multi-controller logic or complex workflows
- [ ] Simple logic stays in protected controller methods
- [ ] No single-method services for trivial validation

### Constants & Values
- [ ] Values inline at point of use (default)
- [ ] No constants files for single-use values
- [ ] Only extracted if 3+ usages across different files

---

## Common Violations

### Violation 1: RESTful Method Names

```php
// ❌ WRONG
public function store()
public function destroy()

// ✅ FIX
public function create()
public function delete()
```

### Violation 2: camelCase Methods

```php
// ❌ WRONG
public function bulkAdjust()
public function syncQuantities()

// ✅ FIX
public function adjust_bulk()
public function sync_quantities()
```

### Violation 3: Request Injection

```php
// ❌ WRONG - Unnecessary injection
public function create(Request $request) {
    $validated = $request->validate([...]);
}

// ✅ FIX
public function create() {
    $values = request()->validate([...]);
}
```

### Violation 4: Mutating Validated Data

```php
// ❌ WRONG
$validated = request()->validate([...]);
$validated['organization_id'] = request()->user()->active_org_id;

// ✅ FIX
$values = request()->validate([...]);
$item = Item::create([
    ...$values,
    'organization_id' => request()->user()->active_org_id,
]);
```

### Violation 5: Constructor Injection for Single-Method Service

```php
// ❌ WRONG
public function __construct(
    private SomeService $service  // Only used by one method
) {}

// ✅ FIX
public function create(SomeService $service) {
    // Method-level injection
}
```

### Violation 6: Model Resolution in Controller

```php
// ❌ WRONG - Controller resolves models from IDs
public function create(SomeService $service): JsonResponse {
    $values = request()->validate([...]);

    $seller = Organization::findOrFail($values['seller_id']);
    $brand = Brand::find($values['brand_id']);

    // Business rule in controller
    abort_if($buyer->id === $seller->id, 400, 'Cannot do that');

    $service->do_something($buyer, $seller, $brand);
}

// ✅ FIX - Controller passes IDs, service resolves
public function create(SomeService $service): JsonResponse {
    $values = request()->validate([...]);

    $result = $service->do_something(
        request()->user()->active_org,
        $values['seller_id'],      // Pass ID
        $values['brand_id'] ?? null // Pass ID
    );
}

// Service handles resolution and business logic
class SomeService {
    public function do_something(Organization $buyer, string $seller_id, ?string $brand_id) {
        $seller = Organization::findOrFail($seller_id);
        $brand = $brand_id ? Brand::find($brand_id) : null;

        abort_if($buyer->id === $seller->id, 400, 'Cannot do that');
        // ...
    }
}
```

### Violation 7: Return Type Changes Without Updating Callers

> **Source:** Bug discovered in Nick's refactoring (Jan 2026) - changing `HasMany` to `Collection` broke `->limit()` calls.

```php
// ⚠️ DANGER: When changing return types, check ALL callers for method compatibility!

// OLD - returned HasMany (query builder)
protected function active_secrets(int $secret_type_id): ?HasMany {
    return $this->active_org->secrets()->where('is_active', 1)->where('secret_type_id', $secret_type_id);
}
// Callers could use query builder methods: ->limit(), ->orderBy(), ->get()

// NEW - returns Collection (already executed)
protected function active_secrets(int $secret_type_id): Collection {
    return $this->active_org->secrets()->where('is_active', 1)->where('secret_type_id', $secret_type_id)->get();
}
// ❌ BREAKING: Callers using ->limit() will fail!
// Collection doesn't have limit() - use take() instead

// Common method compatibility issues:
// Query Builder → Collection
// - limit()     → take()
// - orderBy()   → sortBy() / sortByDesc()
// - where()     → filter()
// - first()     → first() (works on both)
// - get()       → (already executed, remove call)
```

**When refactoring return types:**
1. Search for ALL usages of the method
2. Verify each caller uses compatible methods
3. Update callers before merging

---

## Pattern 8: Routes Do NOT Use Named Routes

**Rule:** BudTags does **NOT use named routes**. Do not add `->name()` to routes.

### ✅ CORRECT - BudTags Convention

```php
// No ->name() calls - just define the route
Route::get('/dashboard', [DashboardController::class, 'index']);
Route::get('/contacts', [ContactController::class, 'index']);
Route::get('/users', [UserController::class, 'index']);
Route::get('/users/{user}', [UserController::class, 'edit']);
Route::post('/labels', [LabelController::class, 'create']);
Route::post('/labels/print', [LabelController::class, 'print_many']);
```

### ❌ WRONG - Adding Named Routes

```php
// ❌ Do NOT add ->name() to routes
Route::get('/dashboard', ...)->name('dashboard');        // Wrong - remove ->name()
Route::get('/users/{user}', ...)->name('users-edit');    // Wrong - remove ->name()
Route::get('/profile', ...)->name('profile.edit');       // Wrong - remove ->name()
```

### Pattern Rules

1. **No named routes**: Do not use `->name()` on any routes
2. **URL-based navigation**: Use explicit URLs in redirects and links
3. **Existing legacy routes**: Some old routes may have names - do not add more

### Why No Named Routes?

- BudTags uses explicit URL paths for clarity
- Avoids indirection between route names and actual URLs
- Frontend uses direct URL strings with Inertia's `router.visit()` and `Link href=""`

# These profile routes need to be fixed eventually:
# profile.edit → profile-edit
# profile.update → profile-update
# profile.destroy → profile-delete
```

**Decision Rule:** Use single words or dashes. No dots ever.

---

## Pattern 9: Constants & Values (Inline by Default)

**Rule:** Keep values inline at point of use. Only extract to a shared constant when the SAME value is used 3+ times across DIFFERENT files.

### ✅ CORRECT - Inline Values

```php
// Status values - inline in model or controller
$package->update(['status' => 'active']);
$query->where('status', 'pending');

// Validation rules - inline where used
$values = request()->validate([
    'quantity' => 'integer|required|min:0|max:100000',
]);

// Config values - inline unless shared
$timeout = 30;
$retries = 3;
```

### ❌ WRONG - Premature Abstraction

```php
// ❌ Constants file for values used in 1-2 places
// constants/package-constants.php
const STATUS_ACTIVE = 'active';
const STATUS_PENDING = 'pending';
const MAX_QUANTITY = 100000;

// Usage - unnecessary indirection
$package->update(['status' => PackageConstants::STATUS_ACTIVE]);
```

### When to Extract (3+ Cross-File Rule)

Extract ONLY when:
1. The SAME exact value appears 3+ times
2. Those usages span DIFFERENT files
3. Changing the value would require updating multiple files

```php
// ✅ ACCEPTABLE - Truly shared value (used in 4+ files)
// config/app.php or constants file
const METRC_DATE_FORMAT = 'Y-m-d';

// Usage across many files
Carbon::parse($date)->format(METRC_DATE_FORMAT);
```

### Never Extract

- Status strings used only in one model/controller
- Validation rules (keep inline)
- Magic numbers used once
- Configuration values that should be in .env
- Domain-specific enums (keep in model or inline)

---

## Pattern 10: YAGNI for Model Scopes

**Rule:** Don't add query scopes unless they're used in 3+ places. Prefer inline queries.

> **Source:** Nick's refactoring of Secret model (Jan 2026) - removed unused `scopeOwnedBy()` and `scopeActiveMetrc()` scopes.

### ✅ CORRECT - Inline Query (Used Once or Twice)

```php
// In controller or single location - keep inline
$keys = Secret::where('organization_id', $this->active_org_id)
    ->where('user_id', $this->id)
    ->where('is_active', true)
    ->get();
```

### ❌ WRONG - Premature Scope Abstraction

```php
// In model - but only called once!
public function scopeOwnedBy(Builder $query, string $user_id): void {
    $query->where('user_id', $user_id);
}

public function scopeActiveMetrc(Builder $query): void {
    $query->where('is_active', true)
        ->where('secret_type_id', SecretType::lookup('Metrc'));
}

// Single usage - doesn't justify the abstraction
$keys = Secret::ownedBy($user->id)->activeMetrc()->get();
```

### When to Extract Scopes

Extract to a scope ONLY when:
- Query pattern used **3+ times** across **different files**
- Query is complex and benefits from a semantic name
- Query needs to be composable with other scopes

---

## Pattern 11: Semantic Naming for Domain Concepts

**Rule:** Column and method names should communicate business meaning, not just technical function.

> **Source:** Nick's refactoring (Jan 2026) - renamed `selected_metrc_key_id` to `borrowed_metrc_key_id`.

### ✅ CORRECT - Business-Meaningful Names

```php
// "borrowed" communicates the temporary nature of using someone else's key
$table->foreignUuid('borrowed_metrc_key_id');

// Method name explains the business concept
public function borrowed_metrc_key(): BelongsTo {
    return $this->belongsTo(Secret::class, 'borrowed_metrc_key_id');
}
```

### ❌ WRONG - Generic Technical Names

```php
// "selected" is too generic - selected for what? By whom?
$table->foreignUuid('selected_metrc_key_id');

// Doesn't communicate that this is for devs borrowing customer keys
public function selected_metrc_key(): BelongsTo {
    return $this->belongsTo(Secret::class, 'selected_metrc_key_id');
}
```

### Naming Guidelines

| Context | ❌ Generic | ✅ Semantic |
|---------|-----------|------------|
| Temp key usage | `selected_key_id` | `borrowed_key_id` |
| Feature toggle | `enabled` | `seller_features_enabled` |
| User reference | `user_id` | `owner_id` (when ownership matters) |
| Status field | `status` | `approval_status`, `sync_status` |

---

## Style Impact

| Violation | Impact | Severity |
|-----------|--------|----------|
| Wrong method naming | Inconsistency, harder to find methods | **MEDIUM** |
| Request injection | Unnecessary verbosity | **LOW** |
| Mutating validated data | Harder to track data flow | **MEDIUM** |
| Over-engineering | Increased complexity, harder to maintain | **MEDIUM** |
| Inconsistent redirects | Confusing patterns | **LOW** |
| Premature constant abstraction | Unnecessary indirection, harder navigation | **MEDIUM** |
| Model resolution in controller | Harder to test, mixed concerns, harder to reuse | **MEDIUM** |
| Business rules in controller | Duplicated logic across controllers | **MEDIUM** |

---

## Related Patterns

- **backend-critical.md** - Security, org scoping, logging
- **php8-brevity.md** - PHP 8 shorthand (`??`, `fn()`, `?->`, `match()`) - Nick's concise style
- **backend-flash-messages.md** - User feedback patterns
- **database.md** - Model patterns, relationships
- `.claude/docs/backend/coding-style.md` - Complete style guide
- `.claude/docs/backend/architecture.md` - Service layer patterns
