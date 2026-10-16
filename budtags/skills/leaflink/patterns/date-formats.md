# LeafLink Date & Time Formats

ISO 8601 dates, the real LeafLink date fields, and the time-zone rules that move a date by a day.

Lines marked "verified 2026-10-16 (sandbox, file)" cite raw files in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/`. "Spec" = the official OpenAPI (`~/budtags-audits/2026-10-15/leaflink_docs_gap_audit/official_openapi.json`).

---

## The three rules

1. **LeafLink returns datetimes in Mountain time** (`-06:00` / `-07:00`), e.g. `2026-10-20T11:00:00-06:00`. Verified 2026-10-16 (sandbox, w_f_dates.txt).
2. **Send a day-only value (`ship_date`, `payment_due_date`) as `YYYY-MM-DDT17:00:00Z`.** The spec says: "It is best practice to include a time (e.g. 2024-01-15T17:00:00Z)."
3. **Never take the calendar day from a Mountain timestamp without choosing the zone.** Midnight in Detroit is 22:00 the previous day in Mountain.

### What a write reads back as

Verified 2026-10-16 (sandbox, w_f_dates.txt):

| Sent | Read back | Day |
|------|-----------|-----|
| `2026-10-20T17:00:00Z` | `2026-10-20T11:00:00-06:00` | right (F1, F4) |
| `2026-10-21` (date only) | `2026-10-21T00:00:00-06:00` | right (F2, F5) |
| `2026-10-22T00:00:00-04:00` (midnight Detroit) | `2026-10-21T22:00:00-06:00` | **previous day** (F3) |

The spec says a date without a time "will default to the server's time zone which is UTC"; the sandbox stored it as midnight Mountain. Sending `T17:00:00Z` avoids both.

---

## Accepted Formats

| Format | Example | Use for |
|--------|---------|---------|
| Date only | `2026-10-16` | `paid_date`, `next_contact_date` (date fields) |
| UTC datetime | `2026-10-16T17:00:00Z` | `ship_date`, `payment_due_date`, `payment_date`, filters |
| Offset datetime | `2026-10-16T11:00:00-06:00` | What LeafLink returns |

`paid_date` is a plain date. A datetime gives 400 `"Date has wrong format. Use one of these formats instead: MM/DD/YYYY, YYYY-MM-DD."` Verified 2026-10-16 (sandbox, w_e_payments.txt E3). (`paid` itself cannot be PATCHed; a full payment sets both.)

---

## Common Date Fields (spec)

There is no `created_date` field on any LeafLink object. It is `created_on`.

### Orders

| Field | Type | Notes |
|-------|------|-------|
| `created_on` | datetime | When the order was created |
| `modified` | datetime | Last modified |
| `ship_date` | datetime | Send `T17:00:00Z`; cleared by Shipped -> Rejected (sandbox, r3_i_reject_shipped_paid.txt) |
| `payment_due_date` | datetime | Send `T17:00:00Z`; cleared by Shipped -> Rejected (sandbox, r3_i_reject_shipped_paid.txt) |
| `paid_date` | date | Set by LeafLink when a payment settles the balance (sandbox, w_e_payments.txt E5) |

There is no `order_date`, `delivery_date` or `shipped_date` field.

### Payments

| Field | Type | Notes |
|-------|------|-------|
| `payment_date` | datetime | Send `T17:00:00Z`; reads back `T11:00:00-06:00` (sandbox, w_e_payments.txt E6) |
| `created_on`, `modified` | datetime | |

### Products

| Field | Type | Notes |
|-------|------|-------|
| `created_on` | datetime | |
| `modified` | datetime | "last modified"; moves on API price and quantity edits, NOT on order-driven quantity/reservation changes (sandbox, w_c_units.txt, w_b_inventory.txt) |
| `last_edit` | datetime | "last edited by a user"; moves on API price and quantity edits (sandbox, w_c_units.txt, r2_t4_inventory_mgmt.txt) |
| `drop_date`, `dropped` | datetime | Scheduled / actual move to Available |

### Customers and contacts

| Field | Type |
|-------|------|
| `created_on`, `modified` | datetime |
| `next_contact_date` (customer) | date |

---

## Laravel/PHP Date Formatting

```php
use Carbon\Carbon;

// Day-only field going TO LeafLink (ship_date, payment_due_date, payment_date)
$due = $order->payment_due_date->format('Y-m-d') . 'T17:00:00Z';

// Date field (paid_date)
$paid = $date->toDateString(); // "2026-10-16"

// Filter boundary in Zulu
$since = now()->subDay()->utc()->format('Y-m-d\TH:i:s\Z');

// Day FROM a LeafLink datetime: convert to the org's zone first
$day = Carbon::parse('2026-10-21T22:00:00-06:00')->setTimezone('America/Detroit')->toDateString();
// "2026-10-22"
```

Never send `$date->toIso8601String()` for a `date`-cast column: that is local midnight (e.g. Detroit `-04:00`), which LeafLink stores as the previous day.

### Date Range Filters

```php
// Orders created in October 2026 (UTC bounds)
$response = $api->get('/orders-received/', [
    'created_on__gte' => '2026-10-01T00:00:00Z',
    'created_on__lt' => '2026-11-01T00:00:00Z',
]);

// Changed since the last sync
$response = $api->get('/orders-received/', [
    'modified__gte' => $last_sync->utc()->format('Y-m-d\TH:i:s\Z'),
    'ordering' => 'id',
]);
```

Honoured date filters per endpoint: `filtering.md`. (`/order-payments/` and `/order-event-logs/` ignore `modified__gte`.)

---

## Frontend Date Handling (React/TypeScript)

```typescript
// Display in the org's zone, not the browser's or Mountain
const formatDate = (iso: string, timeZone: string): string =>
    new Date(iso).toLocaleDateString('en-US', { timeZone, year: 'numeric', month: 'short', day: 'numeric' });
```

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Date one day early | Sent local midnight, or took the day from a Mountain offset | Send `T17:00:00Z`; convert before taking the day |
| `paid_date` 400 "Date has wrong format" | Sent a datetime | Plain `YYYY-MM-DD` (and `paid` cannot be PATCHed anyway) |
| Filter returns everything | Filter is ignored on that endpoint | Check `filtering.md` |

---

## Quick Reference

```php
// To LeafLink, day-only datetime fields
$day->format('Y-m-d') . 'T17:00:00Z'      // "2026-10-16T17:00:00Z"

// To LeafLink, date fields
$day->toDateString()                       // "2026-10-16"

// Filters
'created_on__gte' => '2026-10-01T00:00:00Z'
'modified__gte'   => '2026-10-16T15:00:00Z'
```
