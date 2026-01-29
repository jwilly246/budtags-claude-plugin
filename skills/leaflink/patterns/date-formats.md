# LeafLink Date & Time Formats

ISO 8601 date formatting requirements and common date fields for LeafLink Marketplace V2 API.

---

## Standard Format: ISO 8601

LeafLink uses **ISO 8601** format for all dates and timestamps.

---

## Accepted Formats

### Date Only

```
YYYY-MM-DD
```

**Examples:**
```
2025-01-15
2024-12-31
2025-06-01
```

**Use for:**
- Order dates
- Delivery dates
- Date range filters

### Date with Time (UTC)

```
YYYY-MM-DDTHH:MM:SSZ
```

**Examples:**
```
2025-01-15T10:30:00Z
2024-12-31T23:59:59Z
2025-06-01T00:00:00Z
```

**Use for:**
- Created/modified timestamps
- Precise time tracking
- Event logging

### Date with Timezone

```
YYYY-MM-DDTHH:MM:SS+HH:MM
```

**Examples:**
```
2025-01-15T10:30:00-07:00  // Mountain Time
2025-01-15T10:30:00-08:00  // Pacific Time
2025-01-15T10:30:00+00:00  // UTC
```

**Use for:**
- Timezone-specific operations
- Regional time conversions

---

## Common Date Fields

### Orders

| Field | Type | Description | Format |
|-------|------|-------------|--------|
| `created_date` | datetime | When order was created | ISO 8601 with time |
| `modified` | datetime | Last update timestamp | ISO 8601 with time |
| `order_date` | date | Order placed date | YYYY-MM-DD |
| `delivery_date` | date | Requested delivery | YYYY-MM-DD |
| `shipped_date` | date | When order shipped | YYYY-MM-DD |

### Products

| Field | Type | Description | Format |
|-------|------|-------------|--------|
| `created_date` | datetime | Product created | ISO 8601 with time |
| `modified` | datetime | Last product update | ISO 8601 with time |

### Customers

| Field | Type | Description | Format |
|-------|------|-------------|--------|
| `created_date` | datetime | Customer created | ISO 8601 with time |
| `modified` | datetime | Last update | ISO 8601 with time |
| `last_order_date` | date | Most recent order | YYYY-MM-DD |

---

## Laravel/PHP Date Formatting

### Converting Laravel Dates to ISO 8601

```php
use Carbon\Carbon;

// Date only
$dateOnly = now()->toDateString();
// Output: "2025-01-15"

// Date with time (UTC)
$dateTime = now()->toIso8601String();
// Output: "2025-01-15T10:30:00Z"

// Specific date
$specificDate = Carbon::parse('2025-01-15')->toDateString();
// Output: "2025-01-15"

// Start of day
$startOfDay = now()->startOfDay()->toIso8601String();
// Output: "2025-01-15T00:00:00Z"

// End of day
$endOfDay = now()->endOfDay()->toIso8601String();
// Output: "2025-01-15T23:59:59Z"
```

### Date Range Filters

```php
// Today's orders
$response = $api->get('/orders-received/', [
    'created_date__gte' => now()->startOfDay()->toIso8601String(),
    'created_date__lte' => now()->endOfDay()->toIso8601String()
]);

// Last 30 days
$response = $api->get('/orders-received/', [
    'created_date__gte' => now()->subDays(30)->toDateString()
]);

// Specific month (January 2025)
$response = $api->get('/orders-received/', [
    'created_date__gte' => '2025-01-01',
    'created_date__lt' => '2025-02-01'  // Exclusive upper bound
]);

// Last 7 days
$response = $api->get('/orders-received/', [
    'created_date__gte' => now()->subDays(7)->toDateString(),
    'created_date__lte' => now()->toDateString()
]);

// This year
$response = $api->get('/orders-received/', [
    'created_date__gte' => now()->startOfYear()->toDateString()
]);

// Custom date range from request
$response = $api->get('/orders-received/', [
    'created_date__gte' => Carbon::parse($request->date_from)->toDateString(),
    'created_date__lte' => Carbon::parse($request->date_to)->toDateString()
]);
```

---

## Frontend Date Handling (React/TypeScript)

### Display Formatting

```typescript
// Format for display
const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
};

// Example: "2025-01-15T10:30:00Z" → "Jan 15, 2025"
```

### Form Input Formatting

```typescript
// Convert to ISO 8601 for API
const dateInput = document.querySelector('input[type="date"]').value;
// dateInput: "2025-01-15"

// Send as-is to API (already in YYYY-MM-DD format)
const response = await fetch('/api/orders/', {
    method: 'POST',
    body: JSON.stringify({
        order_date: dateInput
    })
});
```

---

## Common Patterns

### 1. Date Range Picker

```php
// Controller
public function index(Request $request) {
    $filters = [];

    if ($request->has('date_from')) {
        $filters['created_date__gte'] = Carbon::parse($request->date_from)
            ->startOfDay()
            ->toIso8601String();
    }

    if ($request->has('date_to')) {
        $filters['created_date__lte'] = Carbon::parse($request->date_to)
            ->endOfDay()
            ->toIso8601String();
    }

    $orders = $api->get('/orders-received/', $filters);

    return response()->json($orders->json());
}
```

### 2. Relative Date Filters

```php
// Helper function
public function getDateRange(string $range): array {
    return match($range) {
        'today' => [
            'created_date__gte' => now()->startOfDay()->toIso8601String(),
            'created_date__lte' => now()->endOfDay()->toIso8601String()
        ],
        'yesterday' => [
            'created_date__gte' => now()->subDay()->startOfDay()->toIso8601String(),
            'created_date__lte' => now()->subDay()->endOfDay()->toIso8601String()
        ],
        'last_7_days' => [
            'created_date__gte' => now()->subDays(7)->startOfDay()->toIso8601String()
        ],
        'last_30_days' => [
            'created_date__gte' => now()->subDays(30)->startOfDay()->toIso8601String()
        ],
        'this_month' => [
            'created_date__gte' => now()->startOfMonth()->toIso8601String()
        ],
        'last_month' => [
            'created_date__gte' => now()->subMonth()->startOfMonth()->toIso8601String(),
            'created_date__lt' => now()->startOfMonth()->toIso8601String()
        ],
        default => []
    };
}

// Usage
$filters = $this->getDateRange($request->range);
$orders = $api->get('/orders-received/', $filters);
```

---

## Validation

### Request Validation

```php
$validated = $request->validate([
    'order_date' => 'required|date|date_format:Y-m-d',
    'delivery_date' => 'nullable|date|date_format:Y-m-d|after:order_date',
    'date_from' => 'nullable|date',
    'date_to' => 'nullable|date|after_or_equal:date_from'
]);
```

---

## Common Errors

### Invalid Date Format

**Error:**
```
400 Bad Request: "Enter a valid date/time."
```

**Cause:**
- Using format like `01/15/2025` instead of `2025-01-15`
- Missing leading zeros: `2025-1-5` instead of `2025-01-05`
- Using non-ISO format

**Solution:**
```php
// ❌ Wrong
'order_date' => '01/15/2025'
'order_date' => '2025-1-5'

// ✅ Correct
'order_date' => '2025-01-15'
'order_date' => now()->toDateString()
```

### Timezone Issues

**Problem:** Dates off by one day due to timezone conversion

**Solution:** Use `startOfDay()` and `endOfDay()` for UTC:
```php
// ❌ May have timezone issues
'created_date__gte' => '2025-01-15'

// ✅ Explicit UTC boundaries
'created_date__gte' => '2025-01-15T00:00:00Z',
'created_date__lte' => '2025-01-15T23:59:59Z'
```

---

## Best Practices

✅ **Do:**
- Always use ISO 8601 format
- Include leading zeros (2025-01-05, not 2025-1-5)
- Use Laravel Carbon for date manipulation
- Validate date formats before API calls
- Use `startOfDay()`/`endOfDay()` for precise ranges

❌ **Don't:**
- Use US format (01/15/2025)
- Use European format (15/01/2025)
- Forget timezone considerations
- Hardcode date strings (use Carbon)
- Mix date formats within same application

---

## Quick Reference

```php
// Date only
now()->toDateString()                    // "2025-01-15"

// Date with time (UTC)
now()->toIso8601String()                 // "2025-01-15T10:30:00Z"

// Date ranges
now()->startOfDay()->toIso8601String()   // "2025-01-15T00:00:00Z"
now()->endOfDay()->toIso8601String()     // "2025-01-15T23:59:59Z"

// Relative dates
now()->subDays(7)->toDateString()        // 7 days ago
now()->subMonths(1)->toDateString()      // 1 month ago
now()->startOfMonth()->toDateString()    // First day of month

// Parsing
Carbon::parse('2025-01-15')->toDateString()
Carbon::parse($request->date)->toIso8601String()
```
