# Key Naming Conventions

Consistent key naming is **CRITICAL** for cache management, debugging, and preventing cross-tenant data leaks in BudTags.

---

## Key Structure

All BudTags cache keys follow this pattern:

```
{namespace}:{entity}:{scope}:{identifier}
```

| Component | Description | Example |
|-----------|-------------|---------|
| `namespace` | System prefix | `metrc`, `org`, `label_group` |
| `entity` | What's being cached | `package`, `day-of-packages`, `transfer_selections` |
| `scope` | Context/isolation | `{license}`, `{org_id}`, `{facility}` |
| `identifier` | Specific item | `{label}`, `{id}`, `{date}` |

---

## Metrc Entity Keys

### Single Entity Caching

```php
// Pattern: metrc:{entity}:{unique_id}
"metrc:package:{$label}"           // metrc:package:1A4060300001234
"metrc:plant:{$tag}"               // metrc:plant:1A4060300005678
"metrc:strain:{$id}"               // metrc:strain:42
"metrc:item:{$id}"                 // metrc:item:123
"metrc:transfer-delivery:{$id}"    // metrc:transfer-delivery:98765
```

### License-Scoped Lists

```php
// Pattern: metrc:{entity-list}:{license}
"metrc:strains:{$facility}"        // metrc:strains:AU-P-000001
"metrc:locations:{$facility}"      // metrc:locations:AU-P-000001
"metrc:active-items:{$facility}"   // metrc:active-items:AU-P-000001
"metrc:employees:{$facility}"      // metrc:employees:AU-P-000001
"metrc:plants-flowering:{$facility}" // metrc:plants-flowering:AU-C-000001
```

### Day-Partitioned Lists (Most Common)

```php
// Pattern: metrc:day-of-{entity}:{license}:{date}
// Date format: M/D/Y (isoFormat)

"metrc:day-of-packages:{$facility}:{$date}"          // metrc:day-of-packages:AU-P-000001:1/15/2025
"metrc:day-of-inactive-packages:{$facility}:{$date}" // metrc:day-of-inactive-packages:AU-P-000001:1/15/2025
"metrc:day-of-plants:{$facility}:{$date}"            // metrc:day-of-plants:AU-C-000001:1/15/2025
"metrc:day-of-vegetative-plants:{$facility}:{$date}" // metrc:day-of-vegetative-plants:AU-C-000001:1/15/2025
"metrc:day-of-harvests:{$facility}:{$date}"          // metrc:day-of-harvests:AU-C-000001:1/15/2025
"metrc:day-of-inactive-harvests:{$facility}:{$date}" // metrc:day-of-inactive-harvests:AU-C-000001:1/15/2025
"metrc:transfers-{$type}:{$facility}:{$date}"        // metrc:transfers-incoming:AU-P-000001:1/15/2025
```

**Date Generation:**
```php
$timestamp = $start_day->isoFormat('M/D/Y');  // "1/15/2025"
$cache_key = "metrc:day-of-packages:{$facility}:{$timestamp}";
```

### Fast-Changing Data (Short TTL)

```php
// Pattern: metrc:{entity}-available-tags:{license}
"metrc:package-available-tags:{$facility}"  // 2 min TTL
"metrc:plant-available-tags:{$facility}"    // 2 min TTL
```

### Reference Data (Long TTL)

```php
// Pattern: metrc:{reference-type}:{license}
"metrc:item-categories:{$facility}"     // 30 day TTL
"metrc:locations-types:{$facility}"     // DEFAULT_CACHE_TIME
"metrc:waste-reasons:{$facility}"       // DEFAULT_CACHE_TIME
"metrc:adjustment-reasons:{$facility}"  // 1 hour TTL
```

### Lab Results

```php
// By package ID
"metrc:lab-results:{$package_id}"                    // metrc:lab-results:123456

// By source label (shared across siblings)
"metrc:lab-results-by-source:{$facility}:{$label}"   // metrc:lab-results-by-source:AU-P-000001:1A406...
```

---

## Organization-Scoped Keys

For user/organization-specific data that must be isolated:

```php
// Pattern: org:{org_id}:{feature}
"org:{$org_id}:transfer_selections"    // org:abc-123-def:transfer_selections

// From TransferSelectionMemoryService.php
private function cache_key(string $org_id): string {
    return "org:{$org_id}:transfer_selections";
}
```

**CRITICAL**: Always include `org_id` to prevent cross-tenant data access!

---

## Temporary/Counter Keys

For short-lived data like job progress:

```php
// Pattern: {feature}:{id}
"label_group_success:{$group_id}"    // label_group_success:42
"batch_progress:{$batch_id}"         // batch_progress:xyz789
```

---

## Global/Shared Keys

For data that's the same across all contexts:

```php
// Pattern: metrc:{entity}
"metrc:waste-methods"        // Same for all licenses
"metrc:waste-types"          // Same for all licenses
"metrc:tests-types-by-test-batch"  // Same for all licenses
```

---

## Key Construction Helpers

### Date Formatting

```php
// Always use isoFormat for dates in keys
$date = $start_day->isoFormat('M/D/Y');  // "1/15/2025" (no leading zeros)

// NOT these:
// $start_day->format('Y-m-d')  // Different format
// $start_day->toDateString()   // Different format
```

### License Extraction from Keys

```php
// Extract license from day-of-packages key (DevController pattern)
$licenses = collect(Redis::command('keys', ['*day-of-packages*']))
    ->map(fn($key) => preg_replace("/^.+day-of-packages:([a-zA-Z0-9\-]+):.+$/", '$1', $key))
    ->unique()
    ->values();
```

---

## Anti-Patterns

```php
// ❌ WRONG: Missing scope (security vulnerability!)
Cache::forever("packages", $packages);

// ✅ CORRECT: Include facility/license
Cache::forever("metrc:packages:{$facility}", $packages);

// ❌ WRONG: Wrong date format
$key = "metrc:day-of-packages:{$facility}:{$start_day->format('Y-m-d')}";

// ✅ CORRECT: Use isoFormat('M/D/Y')
$key = "metrc:day-of-packages:{$facility}:{$start_day->isoFormat('M/D/Y')}";

// ❌ WRONG: Inconsistent prefix
"pkg:{$label}"
"package-cache:{$label}"

// ✅ CORRECT: Always use metrc: prefix
"metrc:package:{$label}"

// ❌ WRONG: Mixing scopes
"metrc:user-data:{$user_id}"  // User-specific should use org:

// ✅ CORRECT: Use appropriate namespace
"org:{$org_id}:user_preferences"
```

---

## Key Reference Table

| Key Pattern | TTL | Use Case |
|-------------|-----|----------|
| `metrc:package:{label}` | forever | Single package data |
| `metrc:day-of-packages:{license}:{date}` | forever | Day's active packages |
| `metrc:day-of-inactive-packages:{license}:{date}` | 30 days | Day's finished packages |
| `metrc:package-available-tags:{license}` | 2 min | Available tags |
| `metrc:active-items:{license}` | 12 hours | All items |
| `metrc:locations:{license}` | forever | Location list |
| `metrc:item-categories:{license}` | forever | Categories |
| `metrc:lab-results:{package_id}` | forever | Lab test results |
| `metrc:facilities:{key_id}` | forever | User's facilities |
| `org:{org_id}:transfer_selections` | 30 days | Driver/vehicle memory |
| `label_group_success:{id}` | 1 hour | Job progress counter |
