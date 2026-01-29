# Date & Time Formats

Metrc API uses **ISO 8601** format for all date and datetime fields.

---

## Standard Formats

### Date Only (YYYY-MM-DD)

```
2025-01-15
```

**Use for**:
- ActualDate
- HarvestDate
- PackagedDate
- SellByDate
- ExpirationDate

**PHP Example**:
```php
$date = now()->format('Y-m-d'); // "2025-01-15"
```

### DateTime with UTC (YYYY-MM-DDTHH:MM:SSZ)

```
2025-01-15T13:30:00Z
```

**Use for**:
- SalesDateTime
- EstimatedDepartureDateTime
- EstimatedArrivalDateTime

**PHP Example**:
```php
$datetime = now()->utc()->format('Y-m-d\TH:i:s\Z'); // "2025-01-15T13:30:00Z"
```

### DateTime with Timezone (YYYY-MM-DDTHH:MM:SS±HH:MM)

```
2025-01-15T13:30:00-08:00
```

**Use for**: Timestamped events with local timezone

**PHP Example**:
```php
$datetime = now()->format('c'); // "2025-01-15T13:30:00-08:00"
```

---

## Common Date Fields

| Field Name | Format | Example | Purpose |
|------------|--------|---------|---------|
| `ActualDate` | Date | 2025-01-15 | Actual date action occurred |
| `PlannedDate` | Date | 2025-01-20 | Planned/scheduled date |
| `HarvestDate` | Date | 2025-01-10 | Date harvest occurred |
| `PackagedDate` | Date | 2025-01-12 | Date package was created |
| `ExpirationDate` | Date | 2025-07-15 | Product expiration date |
| `SellByDate` | Date | 2025-06-30 | Sell-by date |
| `UseByDate` | Date | 2025-07-01 | Use-by date |
| `SalesDateTime` | DateTime | 2025-01-15T14:30:00Z | When sale occurred |
| `EstimatedDepartureDateTime` | DateTime | 2025-01-16T09:00:00Z | Transfer departure |
| `EstimatedArrivalDateTime` | DateTime | 2025-01-16T15:00:00Z | Transfer arrival |

---

## Laravel Date Helpers

```php
// Current date (for ActualDate fields)
$today = now()->format('Y-m-d');

// Current datetime UTC (for SalesDateTime)
$now = now()->utc()->format('Y-m-d\TH:i:s\Z');

// Specific date
$date = Carbon::parse('2025-01-15')->format('Y-m-d');

// Date from user input
$inputDate = Carbon::createFromFormat('m/d/Y', $request->date)->format('Y-m-d');

// Add days to current date
$futureDate = now()->addDays(30)->format('Y-m-d');
```

---

## Date Validation

```php
use Carbon\Carbon;

function validate_metrc_date(string $date): bool
{
    try {
        Carbon::createFromFormat('Y-m-d', $date);
        return true;
    } catch (\Exception $e) {
        return false;
    }
}

// Usage
if (!validate_metrc_date($request->actual_date)) {
    throw new \Exception("Invalid date format. Use YYYY-MM-DD");
}
```

---

## Common Date Scenarios

### 1. Package Creation Date

```php
$packages = [
    [
        'Tag' => '1A4060300000001000000050',
        'ActualDate' => now()->format('Y-m-d'), // TODAY
        // ...
    ]
];
```

### 2. Sales Receipt DateTime

```php
$sale = [
    [
        'SalesDateTime' => now()->utc()->format('Y-m-d\TH:i:s\Z'), // NOW in UTC
        // ...
    ]
];
```

### 3. Transfer Departure (Future Date)

```php
$transfer = [
    [
        'EstimatedDepartureDateTime' => now()->addDay()->setTime(9, 0)->utc()->format('Y-m-d\TH:i:s\Z'), // Tomorrow 9 AM
        // ...
    ]
];
```

### 4. Package Expiration (30 days from now)

```php
$package = [
    [
        'ExpirationDate' => now()->addDays(30)->format('Y-m-d'),
        // ...
    ]
];
```

---

## Date Query Parameters

When filtering by date ranges:

```php
// Get packages modified in January 2025
$packages = $api->get("/packages/v2/active", [
    'licenseNumber' => $license,
    'lastModifiedStart' => '2025-01-01',
    'lastModifiedEnd' => '2025-01-31'
]);

// Get sales for today
$sales = $api->get("/sales/v2/receipts", [
    'licenseNumber' => $license,
    'salesDateStart' => now()->format('Y-m-d'),
    'salesDateEnd' => now()->format('Y-m-d')
]);
```

---

## Timezone Considerations

1. **Metrc uses UTC internally** for datetime storage
2. **Convert to local timezone** when displaying to users
3. **Always send dates in Metrc's expected format**
4. **Don't rely on automatic timezone conversion**

```php
// ✅ CORRECT - Explicit UTC conversion
$salesDateTime = now()->utc()->format('Y-m-d\TH:i:s\Z');

// ❌ WRONG - May use wrong timezone
$salesDateTime = now()->format('Y-m-d\TH:i:s\Z');
```

---

## Common Date Errors

### Error: "Invalid date format"

**Cause**: Using wrong format (e.g., MM/DD/YYYY instead of YYYY-MM-DD)

**Fix**:
```php
// ❌ WRONG
'ActualDate' => '01/15/2025'

// ✅ CORRECT
'ActualDate' => '2025-01-15'
```

### Error: "Date cannot be in the future"

**Cause**: Using future date for ActualDate (past events)

**Fix**:
```php
// ❌ WRONG
'ActualDate' => now()->addDays(5)->format('Y-m-d')

// ✅ CORRECT
'ActualDate' => now()->format('Y-m-d')
```

---

## Summary

✅ **Date format**: `YYYY-MM-DD` (2025-01-15)
✅ **DateTime format**: `YYYY-MM-DDTHH:MM:SSZ` (2025-01-15T13:30:00Z)
✅ **Use UTC** for datetime fields
✅ **Validate formats** before sending to API
✅ **Use Carbon/date helpers** for formatting
❌ **Don't use** MM/DD/YYYY, DD/MM/YYYY, or other formats
❌ **Don't mix** timezone formats in same request
