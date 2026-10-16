# LeafLink API Filtering

Query-parameter filters for LeafLink Marketplace V2 API list endpoints.

Lines marked "verified 2026-10-16 (sandbox, file)" cite raw files in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/`. "Spec" = the official OpenAPI (`~/budtags-audits/2026-10-15/leaflink_docs_gap_audit/official_openapi.json`).

---

## The one rule: an ignored filter returns EVERYTHING

LeafLink does not reject a filter it does not apply. It returns 200 with the **whole unfiltered list**, so `count` equals the unfiltered total. Several filters the spec lists are ignored in practice. Verified 2026-10-16 (sandbox, r3_a_param_sweep.txt).

Before relying on a filter, check it below. When a lookup must find one row (a licence, an id), check that every returned row really matches.

---

## Filter Operators

There is no generic operator set. Each endpoint lists its own per-field variants in the spec (e.g. `/customers/` has `name`, `name__in`, `name__startswith`; `/orders-received/` has `created_on__gte/__lte/__gt/__lt`). Use only names the spec lists for that endpoint, then check them against the table below.

| Form | Example | Meaning |
|------|---------|---------|
| (none) | `status=Submitted` | Exact match (some fields are case-insensitive, see table) |
| `__gte` / `__lte` / `__gt` / `__lt` | `modified__gte=2026-10-16T15:00:00Z` | Range on dates and numbers |
| `__in` | `id__in=2209363,2209361` | Comma-separated list (where honoured) |
| `__startswith` | `name__startswith=Blue` | Prefix (listed on many customer fields) |
| `__not` | `status__not=Draft` | Exclude (orders `status__not`) |
| `__isnull` | `parent__isnull=true` | Null check (where listed) |

Date filters are `created_on__*` and `modified__*` (plus `last_edit__*` on products). There is no `created_date` field anywhere. Send datetimes in Zulu: `2026-10-16T15:00:00Z`.

---

## Honoured vs ignored (sandbox, 2026-10-16)

Verified 2026-10-16 (sandbox, r3_a_param_sweep.txt; contacts also r2_t8_contacts.txt; ordering also r2_t9_pagination.txt). "Spec" = listed in the official spec for that endpoint.

### `/products/`

| Param | Result | Spec |
|-------|--------|------|
| `sku` | HONOURED | yes |
| `created_on__gte`, `created_on__lt` | HONOURED | yes |
| `modified__gte` | HONOURED | yes |
| `listing_state` | HONOURED | yes |
| `include_children=strains` | HONOURED | yes |
| `fields_include` | HONOURED (also always returns `display_name`, `quantity`, `reserved_qty`) | yes |
| `id__gt`, `id__gte`, `id__in` | **IGNORED** | no |
| `ordering` (`id` / `-id`) | **IGNORED** | no |

### `/customers/`

| Param | Result | Spec |
|-------|--------|------|
| `id__in` | HONOURED | yes |
| `name` | HONOURED, **exact match only** (`ZZ BUDTAGS` -> 0 rows) | yes |
| `license_number` | HONOURED, **exact and case-sensitive** (lowercase -> 0 rows) | yes |
| `license_number__in` | **IGNORED** (one or two values) | **yes, but ignored** |
| `license_number__iexact`, `license_number__icontains` | **IGNORED** | no |
| `modified__gte` | HONOURED | yes |
| `ordering` (`id` / `-id`) | HONOURED | no |
| `include_children=contacts,managers` | HONOURED | yes |
| `fields_include` | HONOURED | yes |

Find customers by licence with one `license_number=<exact>` call per licence. `license_number__in` silently returns the whole customer list.

### `/contacts/`

| Param | Result | Spec |
|-------|--------|------|
| `delete=false` | HONOURED (default list INCLUDES deleted contacts) | yes |
| `modified__gte` | HONOURED | yes |
| `ordering` | HONOURED | no |

### `/orders-received/`

| Param | Result | Spec |
|-------|--------|------|
| `status` | HONOURED, case-insensitive (`Rejected` = `rejected`) | yes |
| `external_id_seller` | HONOURED | yes |
| `created_on__gte`, `created_on__lt` | HONOURED | yes |
| `modified__gte` | HONOURED | yes |
| `customer` | HONOURED | yes |
| `customer_id`, `customer__id` | **IGNORED** | no |
| `include_children=line_items,sales_reps` | HONOURED (line_items come back even without it) | yes |
| `ordering` (`id`, `-id`, `created_on`, `-created_on`, `-modified`) | HONOURED | no |
| `fields_include=id` | **400** `"Fields `id` do not exist on this endpoint."`; use `number` (r2_t9_pagination.txt) | - |

### `/line-items/`

| Param | Result | Spec |
|-------|--------|------|
| `order` | HONOURED (paging by `limit=1` + `next` works) | yes |
| `ordering` | **IGNORED** | no |

### `/order-payments/`

| Param | Result | Spec |
|-------|--------|------|
| `ordering` (`-id` / `id`) | HONOURED | no |
| `modified__gte` | **IGNORED** | no |
| `order` | **IGNORED** | no |

The spec lists only `limit`/`offset` here. For one order's payments use `GET /orders-received/{number}/payments/` (paged, honours `limit`).

### `/order-event-logs/`

| Param | Result | Spec |
|-------|--------|------|
| `order` | HONOURED | yes |
| `ordering` | HONOURED | no |
| `modified__gte` | **IGNORED** | no |

### Other endpoints

| Endpoint | Param | Result | Spec |
|----------|-------|--------|------|
| `/product-images/` | `product`, `ordering` | HONOURED | `product` yes, `ordering` no |
| `/product-batches/` | `ordering` | **IGNORED** | no |
| `/strains/` | `name` | HONOURED | yes |
| `/brands/` | `company` | **IGNORED** | **yes, but ignored** |
| `/product-lines/` | `company` | **IGNORED** | **yes, but ignored** |
| `/licenses/` | `company` | **IGNORED** | no |

An App key sees one company, so the ignored `company` filters return that company's rows anyway; never rely on them with a User token.

---

## Common Filter Patterns

### Incremental sync window

```php
$response = $api->get('/orders-received/', [
    'modified__gte' => $since->utc()->format('Y-m-d\TH:i:s\Z'),
    'ordering' => 'id',
    'limit' => 100,
    'offset' => 0,
]);
```

### Status

```php
// One status (case-insensitive)
$api->get('/orders-received/', ['status' => 'Submitted']);

// Exclude one
$api->get('/orders-received/', ['status__not' => 'Draft']);
```

Real order statuses: Draft, Submitted, Accepted, Backorder, Fulfilled, Shipped, Complete, Rejected, Combined, Cancelled (spec).

### Customer by licence

```php
// One call per licence; exact, case-sensitive
$response = $api->get('/customers/', ['license_number' => 'AU-R-000171']);
```

### Live contacts only

```php
$response = $api->get('/contacts/', ['delete' => 'false', 'ordering' => 'id']);
```

---

## Implementation in BudTags

Build filters from the request, mapped to real LeafLink names:

```php
$filters = collect($request->only(['status', 'customer', 'date_from', 'date_to']))
    ->filter()
    ->mapWithKeys(fn ($value, $key) => match ($key) {
        'date_from' => ['created_on__gte' => $value],
        'date_to' => ['created_on__lte' => $value],
        default => [$key => $value],
    })
    ->toArray();

$response = $api->get('/orders-received/', $filters);
```

---

## Best Practices

✅ **Do:**
- Use only filter names the spec lists for that endpoint
- Check the honoured/ignored table before trusting a filter
- Verify returned rows match when looking up one record
- Use `modified__gte` (Zulu) for incremental reads

❌ **Don't:**
- Use `created_date__*`, `status__in`, `total__gte`, `price__gte`, `name__icontains` on customers/products, `active`: they are not LeafLink filters
- Use `license_number__in` or products `id__gt`/`id__in` (ignored, whole list comes back)
- Expect a 400 for an unknown filter; you get the whole list
