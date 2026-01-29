# API Integration Patterns

**Source:** `.claude/docs/integrations/metrc.md`, `.claude/docs/integrations/quickbooks.md`
**Last Updated:** 2026-01-08
**Pattern Count:** 14 patterns (API service + Lab/Transporter + Pass Data optimization)

> **Note (Dec 2025):** Added LabCompany/TransporterCompany patterns, MetrcFacility architecture, TransferCartService patterns.

---

## Overview

All API integrations use dedicated service classes (`MetrcApi`, `QuickBooksApi`, `LeafLinkApi`). NEVER make direct API calls without using these services.

---

## Pattern 1: Service Usage with `set_user()`

**Rule:** ALWAYS call `set_user(User $user)` before using API services.

### ✅ CORRECT

```php
use App\Services\Api\MetrcApi;

public function fetch_packages(MetrcApi $api) {
    $api->set_user(request()->user());

    $license = session('license');
    $packages = $api->packages($license, 'Active');

    return response()->json($packages);
}
```

### ❌ WRONG

```php
// ❌ No set_user() call - API keys not configured!
public function fetch_packages(MetrcApi $api) {
    $packages = $api->packages($license, 'Active');  // Fails!
}

// ❌ Direct API call without service
$packages = Http::get('https://api-ca.metrc.com/packages/v1/active');
```

---

## Pattern 2: Metrc License Type Restrictions

**Rule:** Different license types have access to different endpoints.

### License Types

| License Type | Prefix | Has Access To |
|--------------|--------|---------------|
| Cultivation | `au-c-xxxxx` | Plants, plant batches, plant waste reasons, packages |
| Processing/Manufacturing | `au-p-xxxxx` | Packages, harvest waste (NO plants) |
| Retail | `au-r-xxxxx` | Packages, sales (NO plants) |

### ✅ CORRECT - Conditional Endpoint Access

```php
// Check data source before fetching plant-specific data
$data_source = session('data_source');  // 'plants' or 'packages'

$waste_reasons = ($data_source === 'plants')
    ? $api->waste_reasons($facility)  // Only for cultivation licenses
    : null;

$waste_types = $api->waste_types($facility);  // Available to all
$waste_methods = $api->waste_methods($facility);  // Available to all
```

### ❌ WRONG - Calling Plant Endpoints with Non-Cultivation License

```php
// ❌ Will cause 401 errors for processing/retail licenses!
$waste_reasons = $api->waste_reasons($facility);

// ❌ Assume all licenses have plant access
$plants = $api->plants($facility);  // Fails for au-p-xxxxx licenses!
```

---

## Pattern 3: Metrc API Caching

**Rule:** Cache Metrc data when possible to avoid rate limits.

### ✅ CORRECT

```php
public function fetch_facilities(MetrcApi $api) {
    $api->set_user(request()->user());

    // Cache facilities for 1 hour
    $facilities = Cache::remember(
        "metrc_facilities_{$api->user->active_org_id}",
        3600,
        fn() => $api->facilities()
    );

    return response()->json($facilities);
}
```

---

## Pattern 3.5: Pass Fetched Data Instead of Re-Fetching

**Rule:** When data has already been fetched (e.g., in middleware), pass it to services instead of letting them fetch it again.

> **Source:** Nick's refactoring of FacilityPermissionsService (Jan 2026) - eliminated redundant API calls.

### ❌ WRONG - Double API Call

```php
// Middleware
public function handle(Request $request, Closure $next) {
    $facilities = $this->api->facilities();  // ← API call #1
    $first_license = $facilities[0]['License']['Number'] ?? null;

    // Service makes ANOTHER API call internally!
    $perms = app('FacilityPermissionsService')
        ->get_frontend_facility_permissions($first_license);  // ← API call #2!

    session(['license' => $first_license, 'facility_permissions' => $perms]);
    return $next($request);
}

// Service (OLD - bad pattern)
class FacilityPermissionsService {
    public function get_frontend_facility_permissions(string $license): array {
        $facilities = $this->metrc_api->facilities();  // ❌ Fetches AGAIN!
        foreach ($facilities as $facility) {
            if ($facility['License']['Number'] === $license) {
                return $this->extract_permissions($facility['FacilityType']);
            }
        }
        return [];
    }
}
```

### ✅ CORRECT - Pass Already-Fetched Data

```php
// Middleware
public function handle(Request $request, Closure $next) {
    $facilities = $this->api->facilities();  // ← Only API call
    $first_license = $facilities[0]['License']['Number'] ?? null;

    // Pass the already-fetched facilities to the service
    $perms = $this->permission_service()
        ->extract_facility_permissions($facilities, $first_license);  // ← No API call!

    session(['license' => $first_license, 'facility_permissions' => $perms]);
    return $next($request);
}

// Service (NEW - good pattern)
class FacilityPermissionsService {
    // Accept pre-fetched data as parameter
    public function extract_facility_permissions(array $facilities, string $license): array {
        foreach ($facilities as $facility) {
            if ($facility['License']['Number'] === $license) {
                return [
                    'can_grow_plants' => $facility['FacilityType']['CanGrowPlants'] ?? false,
                    'is_retail' => $facility['FacilityType']['IsRetail'] ?? false,
                    // ... extract other permissions
                ];
            }
        }
        return [];
    }
}
```

### Key Insight

**Design services with two entry points:**
1. `get_*()` - Fetches and processes (for direct use)
2. `extract_*()` - Processes pre-fetched data (for use when caller already has data)

```php
class FacilityPermissionsService {
    // Entry point 1: Fetch and process (standalone use)
    public function get_frontend_facility_permissions(string $license): array {
        $facilities = $this->metrc_api->facilities();
        return $this->extract_facility_permissions($facilities, $license);
    }

    // Entry point 2: Process only (when data already fetched)
    public function extract_facility_permissions(array $facilities, string $license): array {
        // ... just processing, no API call
    }
}
```

---

## Pattern 4: QuickBooks OAuth Integration

**Rule:** QuickBooks uses OAuth tokens that expire. Handle token refresh.

### ✅ CORRECT

```php
use App\Services\Api\QuickBooksApi;

public function fetch_invoices(QuickBooksApi $qb) {
    $qb->set_user(request()->user());

    try {
        $invoices = $qb->getInvoices();
        return response()->json($invoices);
    } catch (TokenExpiredException $e) {
        // Automatic token refresh handled by QuickBooksApi
        return redirect()->route('quickbooks.reconnect');
    }
}
```

---

## Pattern 5: Error Handling

**Rule:** Handle API errors gracefully with user-friendly messages.

### ✅ CORRECT

```php
public function sync_packages(MetrcApi $api) {
    $api->set_user(request()->user());

    try {
        $packages = $api->packages(session('license'), 'Active');

        LogService::store(
            'Metrc Sync',
            "Synced {count($packages)} packages from Metrc",
            null
        );

        return redirect()->back()->with('message', "Synced {count($packages)} packages");

    } catch (\Exception $e) {
        LogService::store(
            'Metrc Sync Failed',
            "Failed to sync packages: {$e->getMessage()}",
            null
        );

        return redirect()->back()->with('error', 'Failed to sync packages: ' . $e->getMessage());
    }
}
```

---

## Pattern 6: License/Facility Selection

**Rule:** Metrc operations require license selection. Validate before API calls.

### ✅ CORRECT

```php
// Middleware ensures license selected
Route::middleware(['auth', 'has-org', 'facility-license'])->group(function () {
    Route::post('/metrc/sync', [MetrcController::class, 'sync_packages']);
});

// In controller - license guaranteed to exist
public function sync_packages(MetrcApi $api) {
    $license = session('license');  // Guaranteed by middleware

    $api->set_user(request()->user());
    $packages = $api->packages($license, 'Active');
    // ...
}
```

### ❌ WRONG

```php
// ❌ No license validation
public function sync_packages(MetrcApi $api) {
    $license = session('license');  // Might be null!

    $packages = $api->packages($license, 'Active');  // Fails!
}
```

---

## Pattern 7: API Service Methods

**Common Metrc Methods:**

```php
$api->set_user($user);  // ALWAYS call first

// Packages
$api->packages($license, 'Active');  // Active packages
$api->packages($license, 'Inactive');  // Inactive packages
$api->packages($license, 'Onhold');  // On-hold packages

// Plants (ONLY for cultivation licenses!)
$api->plants($license, 'Flowering');
$api->plants($license, 'Vegetative');

// Waste (check license type!)
$api->waste_reasons($facility);  // Only cultivation
$api->waste_types($facility);  // All licenses
$api->waste_methods($facility);  // All licenses

// Facilities
$api->facilities();  // All facilities for user's org

// Lab Results
$api->lab_results($package_id);
```

**Common QuickBooks Methods:**

```php
$qb->set_user($user);  // ALWAYS call first

$qb->getInvoices();
$qb->getCreditMemos();
$qb->getItems();
$qb->getCustomers();
$qb->createInvoice($data);
$qb->createCreditMemo($data);
```

---

## Pattern 8: Organization-Scoped API Credentials

**Rule:** API keys stored per organization. Service configures keys via `set_user()`.

### How it Works

```php
// API service loads keys from user's active org
class MetrcApi {
    public function set_user(User $user): void {
        $secret = $user->active_org->secrets()
            ->where('type', 'metrc')
            ->where('active', true)
            ->first();

        if (!$secret) {
            throw new \Exception('No active Metrc API key configured');
        }

        $this->user_api_key = $secret->user_api_key;
        $this->vendor_api_key = $secret->vendor_api_key;
    }
}
```

---

## Pattern 9: Lab Company Integration

**Rule:** Lab companies are global entities (no organization_id). Use `LabCompany` model with `MetrcFacility` relationship.

### Model Structure

```php
class LabCompany extends Model {
    protected $fillable = [
        'name',
        'phone',
        'enabled',              // Show in transfer dropdowns
        'contact_emails',       // JSON array for COC distribution
        'request_pickup_enabled',
        'generate_coc_enabled',
    ];

    protected $casts = [
        'enabled' => 'boolean',
        'contact_emails' => 'array',
        'request_pickup_enabled' => 'boolean',
        'generate_coc_enabled' => 'boolean',
    ];

    public function facilities(): HasMany {
        return $this->hasMany(MetrcFacility::class, 'lab_company_id');
    }
}
```

### Controller Pattern

```php
public function create_facility() {
    $validated = request()->validate([
        'lab_company_id' => 'required|exists:lab_companies,id',
        'name' => 'required|string|max:255',
        'license_recreational' => 'nullable|string',
        'license_medical' => 'nullable|string',
        'street' => 'nullable|string',
        'city' => 'nullable|string',
        'state' => 'nullable|string|size:2',
        'zip' => 'nullable|string|max:10',
    ]);

    // Get Lab facility type ID
    $labTypeId = MetrcFacilityType::where('name', 'Lab')->first()->id;

    MetrcFacility::create([
        ...$validated,
        'metrc_facility_type_id' => $labTypeId,
    ]);

    return redirect()->back()->with('message', 'Lab facility created');
}
```

### Query Pattern - Exclude Sandbox

```php
// Production orgs exclude SF-SBX-* licenses
LabCompany::with(['facilities' => function ($query) use ($user) {
    $query->when($user->active_org?->name !== 'Budtags', function ($q) {
        $q->where('license_recreational', 'not like', 'SF-SBX-%');
    });
}])
->where('enabled', true)
->get();
```

---

## Pattern 10: Transporter Company Integration

**Rule:** Similar to Lab Company, transporters are global entities with feature flags.

### Model Structure (Updated Dec 2025)

```php
class TransporterCompany extends Model {
    protected $fillable = [
        'name',
        'phone',
        'enabled',              // NEW - master visibility switch
        'contact_emails',       // NEW - JSON array
        'request_pickup_enabled', // NEW - feature flag
    ];

    protected $casts = [
        'enabled' => 'boolean',
        'contact_emails' => 'array',
        'request_pickup_enabled' => 'boolean',
    ];

    public function facilities(): HasMany {
        return $this->hasMany(MetrcFacility::class, 'transporter_company_id');
    }
}
```

### Seeder Pattern

```php
$jkLogix = TransporterCompany::updateOrCreate(
    ['name' => 'JK Logix Inc'],
    [
        'phone' => '(517) 574-5930',
        'enabled' => true,
        'request_pickup_enabled' => true,  // Feature enabled
        'contact_emails' => ['ahervey@jklogix.com', 'orders@jklogix.com'],
    ]
);
```

---

## Pattern 11: MetrcFacility Architecture

**Rule:** MetrcFacility is the central hub linking organizations, labs, and transporters.

### Facility Ownership Matrix

| Type | organization_id | company_id FK | Owner |
|------|----------------|---------------|-------|
| Lab | NULL | `lab_company_id` | Budtags (global) |
| Transport | NULL | `transporter_company_id` | Budtags (global) |
| Processor | UUID | NULL | Client org |
| Retailer | UUID | NULL | Client org |
| Grower | UUID | NULL | Client org |

### Relationships

```php
class MetrcFacility extends Model {
    public function org(): BelongsTo {
        return $this->belongsTo(Organization::class, 'organization_id');
    }

    public function lab_company(): BelongsTo {
        return $this->belongsTo(LabCompany::class);
    }

    public function transporter_company(): BelongsTo {
        return $this->belongsTo(TransporterCompany::class);
    }

    public function metrc_facility_type(): BelongsTo {
        return $this->belongsTo(MetrcFacilityType::class);
    }
}
```

### Query - Destination Facilities (Exclude Labs/Transporters)

```php
// Get non-lab, non-transporter facilities for transfers
MetrcFacility::whereNull('lab_company_id')
    ->whereNull('transporter_company_id')
    ->where('enabled', true)
    ->get();
```

---

## Pattern 12: Email Distribution Pattern

**Rule:** Store emails as JSON array, iterate for distribution.

### Storage Pattern

```php
protected $casts = ['contact_emails' => 'array'];

// Example data: ["email1@lab.com", "email2@lab.com"]
```

### Distribution Pattern

```php
foreach ($company->contact_emails ?? [] as $email) {
    Mail::to($email)->send(new COCGenerated($pdf, ...));
}
```

---

## Pattern 13: Feature Flags Pattern

**Rule:** Use boolean columns for feature toggles on company models.

### Common Feature Flags

```php
// On Company models
'enabled' => boolean           // Master switch for visibility
'request_pickup_enabled' => boolean  // Feature: pickup requests
'generate_coc_enabled' => boolean    // Feature: COC generation (labs only)
```

### Usage in Queries

```php
// Only labs with COC generation enabled
LabCompany::where('enabled', true)
    ->where('generate_coc_enabled', true)
    ->get();
```

---

## Verification Checklist

### Metrc Integration
- [ ] Uses `MetrcApi` service with `set_user()`
- [ ] Caches data appropriately
- [ ] Handles rate limits and API errors
- [ ] Validates license selection before operations
- [ ] Checks license type before calling plant endpoints
- [ ] No direct HTTP calls to Metrc API
- [ ] Passes pre-fetched data when available (avoid double API calls)

### QuickBooks Integration
- [ ] Uses `QuickBooksApi` service with `set_user()`
- [ ] Handles OAuth token expiration
- [ ] Organization-scoped credentials
- [ ] No direct HTTP calls to QuickBooks API

### Error Handling
- [ ] Try/catch around all API calls
- [ ] Logs API failures with `LogService`
- [ ] User-friendly error messages
- [ ] Redirects with error flash message

### Lab/Transporter Integration
- [ ] Lab facilities use `lab_company_id` FK
- [ ] Transporter facilities use `transporter_company_id` FK
- [ ] Global entities have `organization_id` = NULL
- [ ] Feature flags checked before enabling features
- [ ] Sandbox licenses filtered for production orgs
- [ ] Email distribution uses JSON array iteration
- [ ] `contact_emails` cast as `array`

### MetrcFacility Architecture
- [ ] Correct ownership (org-owned vs global)
- [ ] Correct company FK based on type
- [ ] Destination queries exclude labs/transporters
- [ ] `metrc_facility_type_id` set correctly

---

## Common Violations

### Violation 1: No `set_user()` Call

```php
// ❌ WRONG
public function sync(MetrcApi $api) {
    $packages = $api->packages($license, 'Active');  // Fails - no API keys!
}

// ✅ FIX
public function sync(MetrcApi $api) {
    $api->set_user(request()->user());
    $packages = $api->packages($license, 'Active');
}
```

### Violation 2: Direct API Calls

```php
// ❌ WRONG - Bypasses service layer
$packages = Http::withHeaders([
    'Authorization' => 'Bearer ...'
])->get('https://api-ca.metrc.com/packages/v1/active');

// ✅ FIX - Use service
$api->set_user(request()->user());
$packages = $api->packages($license, 'Active');
```

### Violation 3: Calling Plant Endpoints Without License Check

```php
// ❌ WRONG - Fails for non-cultivation licenses
$waste_reasons = $api->waste_reasons($facility);

// ✅ FIX - Check data source/license type
$waste_reasons = ($data_source === 'plants')
    ? $api->waste_reasons($facility)
    : null;
```

### Violation 4: Wrong Facility FK

```php
// ❌ WRONG - Using organization_id for lab facility
MetrcFacility::create([
    'organization_id' => $org->id,  // Labs should be global!
    'name' => 'Lab Name',
]);

// ✅ FIX - Use lab_company_id, no organization_id
MetrcFacility::create([
    'lab_company_id' => $labCompany->id,
    'metrc_facility_type_id' => $labTypeId,
    'name' => 'Lab Name',
    // organization_id stays NULL
]);
```

### Violation 5: Missing Sandbox Filter

```php
// ❌ WRONG - Shows sandbox labs in production
LabCompany::with('facilities')->where('enabled', true)->get();

// ✅ FIX - Filter SF-SBX-* for production orgs
LabCompany::with(['facilities' => function ($query) use ($user) {
    $query->when($user->active_org?->name !== 'Budtags', function ($q) {
        $q->where('license_recreational', 'not like', 'SF-SBX-%');
    });
}])
->where('enabled', true)
->get();
```

---

## Impact of Violations

| Violation | Impact | Severity |
|-----------|--------|----------|
| No `set_user()` call | API requests fail (no credentials) | **CRITICAL** |
| Direct API calls | Bypasses caching, error handling | **HIGH** |
| Wrong license type endpoint | 401 errors for non-cultivation licenses | **HIGH** |
| Wrong facility FK | Data corruption, broken relationships | **CRITICAL** |
| Missing sandbox filter | Sandbox data visible in production | **MEDIUM** |
| No error handling | Unhandled exceptions, poor UX | **MEDIUM** |

---

## Related Patterns

- **backend-critical.md** - Organization scoping
- **backend-style.md** - Service usage patterns
- **database.md** - MetrcFacility table structure
- `.claude/docs/integrations/metrc.md` - Complete Metrc API reference
- `.claude/docs/integrations/quickbooks.md` - Complete QuickBooks API reference

### Reference Files

| Component | Location |
|-----------|----------|
| LabCompany Model | `app/Models/LabCompany.php` |
| TransporterCompany Model | `app/Models/TransporterCompany.php` |
| MetrcFacility Model | `app/Models/MetrcFacility.php` |
| LabController | `app/Http/Controllers/LabController.php` |
| TransporterController | `app/Http/Controllers/TransporterController.php` |
| TransferCartService | `app/Services/TransferCartService.php` |
| Lab Seeder | `database/seeders/LabSeeder.php` |
| Transporter Seeder | `database/seeders/TransporterSeeder.php` |
