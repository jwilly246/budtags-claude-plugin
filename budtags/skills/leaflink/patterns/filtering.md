# LeafLink API Filtering

Comprehensive filtering patterns using Django-style query parameters for LeafLink Marketplace V2 API.

---

## Filter Operators

LeafLink follows Django REST framework filtering conventions:

| Operator | Example | Description |
|----------|---------|-------------|
| (none) | `status=draft` | Exact match |
| `__in` | `status__in=draft,confirmed` | Multiple values (comma-separated) |
| `__lt` | `created_date__lt=2025-01-31` | Less than |
| `__lte` | `created_date__lte=2025-01-31` | Less than or equal |
| `__gt` | `created_date__gt=2025-01-01` | Greater than |
| `__gte` | `created_date__gte=2025-01-01` | Greater than or equal |
| `__icontains` | `name__icontains=blue` | Case-insensitive contains |
| `__startswith` | `name__startswith=Blue` | Starts with (case-sensitive) |
| `__istartswith` | `name__istartswith=blue` | Starts with (case-insensitive) |
| `__endswith` | `name__endswith=OG` | Ends with (case-sensitive) |
| `__iendswith` | `name__iendswith=og` | Ends with (case-insensitive) |
| `__isnull` | `deleted_at__isnull=true` | Check for null/non-null |

---

## Common Filter Patterns

### 1. Date Range Filtering (Most Common)

```php
$response = $api->get('/orders-received/', [
    'created_date__gte' => '2025-01-01',        // After or on Jan 1
    'created_date__lte' => '2025-01-31',        // Before or on Jan 31
]);
```

**Use Cases:**
- Orders in specific month
- Recent activity (last 7 days, 30 days)
- Between two dates
- After/before specific date

**Examples:**
```php
// Today's orders
'created_date__gte' => now()->startOfDay()->toIso8601String(),
'created_date__lte' => now()->endOfDay()->toIso8601String()

// Last 30 days
'created_date__gte' => now()->subDays(30)->toDateString()

// Specific month
'created_date__gte' => '2025-01-01',
'created_date__lt' => '2025-02-01'  // Note: __lt to exclude Feb 1
```

### 2. Status Filtering

```php
// Single status
$response = $api->get('/orders-received/', [
    'status' => 'confirmed'
]);

// Multiple statuses (comma-separated)
$response = $api->get('/orders-received/', [
    'status__in' => 'draft,confirmed,shipped'
]);
```

**Common Statuses:**
- Orders: `draft`, `confirmed`, `shipped`, `delivered`, `canceled`
- Customers: `active`, `inactive`, `pending`

### 3. Text Search

```php
// Case-insensitive contains (most flexible)
$response = $api->get('/customers/', [
    'name__icontains' => 'dispensary'
]);

// Starts with (find all "Blue *" products)
$response = $api->get('/products/', [
    'name__startswith' => 'Blue'
]);

// Exact match
$response = $api->get('/products/', [
    'name' => 'Blue Dream'
]);
```

### 4. Relationship Filtering

```php
// Filter by related company
$response = $api->get('/orders-received/', [
    'customer' => 123  // Customer ID
]);

// Filter by related product
$response = $api->get('/line-items/', [
    'product' => 456  // Product ID
]);

// Multiple related IDs
$response = $api->get('/orders-received/', [
    'customer__in' => '123,456,789'
]);
```

### 5. Null/Non-Null Filtering

```php
// Only show non-deleted items
$response = $api->get('/products/', [
    'deleted_at__isnull' => 'true'
]);

// Only show items with specific field set
$response = $api->get('/customers/', [
    'email__isnull' => 'false'  // Has email
]);
```

---

## Complex Filtering Examples

### Example 1: Orders with Multiple Criteria

```php
$response = $api->get('/orders-received/', [
    'created_date__gte' => '2025-01-01',
    'created_date__lte' => '2025-01-31',
    'status__in' => 'confirmed,shipped',
    'customer' => 123,
    'limit' => 100,
    'offset' => 0
]);
```

**Filters:**
- Created in January 2025
- Status is confirmed OR shipped
- From customer ID 123
- Paginated (100 per page)

### Example 2: Customers with 87 Filter Parameters

```php
// The /customers/ endpoint supports 87 filter parameters!
$response = $api->get('/customers/', [
    'license_types__in' => 'retail,cultivation',  // Multiple license types
    'status' => 'active',                         // Only active
    'created_date__gte' => '2024-01-01',         // Created this year
    'name__icontains' => 'green',                 // Name contains "green"
    'city' => 'Denver',                           // Located in Denver
    'state' => 'CO',                              // Colorado only
    'limit' => 100
]);
```

### Example 3: Products with Price Range

```php
$response = $api->get('/products/', [
    'category' => 5,                              // Specific category ID
    'price__gte' => 10.00,                        // Minimum price $10
    'price__lte' => 50.00,                        // Maximum price $50
    'in_stock' => true,                           // Only in-stock items
    'active' => true,                             // Only active products
    'name__icontains' => 'og'                     // Contains "og"
]);
```

---

## Implementation in BudTags

### Basic Filtering

```php
// In controller
public function index(Request $request) {
    $filters = [];

    // Add filters conditionally
    if ($request->has('status')) {
        $filters['status'] = $request->get('status');
    }

    if ($request->has('date_from')) {
        $filters['created_date__gte'] = $request->get('date_from');
    }

    if ($request->has('date_to')) {
        $filters['created_date__lte'] = $request->get('date_to');
    }

    $orders = $this->api->get('/orders-received/', $filters);

    return response()->json($orders->json());
}
```

### Dynamic Filter Building

```php
// Build filters from request
$filters = collect($request->only([
    'status',
    'customer',
    'date_from',
    'date_to'
]))
->filter() // Remove null values
->mapWithKeys(function ($value, $key) {
    // Map friendly names to API parameters
    return match($key) {
        'date_from' => ['created_date__gte' => $value],
        'date_to' => ['created_date__lte' => $value],
        default => [$key => $value]
    };
})
->toArray();

$response = $api->get('/orders-received/', $filters);
```

---

## Filter Validation

### Common Errors

**Invalid Filter Syntax:**
```
400 Bad Request: "Unknown filter: date__greater_than. Did you mean date__gte?"
```

**Solution:** Use correct operator names (__gte, __lte, __in, etc.)

**Invalid Value Format:**
```
400 Bad Request: "Enter a valid date/time."
```

**Solution:** Use ISO 8601 format for dates

---

## Best Practices

✅ **Do:**
- Use `__icontains` for flexible text search
- Combine date range filters for time periods
- Use `__in` for multiple status/ID filters
- Filter on indexed fields when possible
- Validate filter values before sending

❌ **Don't:**
- Use `__contains` (case-sensitive, less flexible than `__icontains`)
- Forget double underscores in operators
- Send empty string values (use null checks instead)
- Over-filter (too many filters slow down queries)

---

## Quick Reference

```php
// Date ranges
'created_date__gte' => '2025-01-01'  // On or after
'created_date__lte' => '2025-01-31'  // On or before
'created_date__gt' => '2025-01-01'   // After (exclusive)
'created_date__lt' => '2025-02-01'   // Before (exclusive)

// Multiple values
'status__in' => 'draft,confirmed,shipped'
'customer__in' => '123,456,789'

// Text search
'name__icontains' => 'blue'      // Case-insensitive contains
'name__startswith' => 'Blue'     // Starts with
'name' => 'Blue Dream'           // Exact match

// Relationships
'customer' => 123                // Related by ID
'product' => 456

// Null checks
'email__isnull' => 'false'       // Has email
'deleted_at__isnull' => 'true'   // Not deleted
```

---

## Most Complex Endpoint: /customers/

The `/customers/` endpoint has **87 filter parameters** - the most in the LeafLink API!

**Categories of filters:**
- Basic info: name, email, phone, status
- Location: city, state, zip_code, country
- Licensing: license_types, license_numbers
- Relationships: company, tier, sales_rep
- Dates: created_date, modified, last_order_date
- Business: payment_terms, credit_limit, tax_exempt
- And 60+ more!

Always reference the OpenAPI schema for complete filter documentation.
