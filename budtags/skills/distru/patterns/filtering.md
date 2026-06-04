# Pattern — Filtering

Distru's filter parameter conventions are **inconsistent across endpoints** — the API was clearly built incrementally by different teams and the differences are wire-stable. This document catalogs every variation observed in Phase 0.5.

**Phase 0.5 audited 2026-05-21.** Mapping doc: `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md` (Section 10, API Quirks).

## URL convention — kebab-case for compound paths

Compound endpoint paths use **kebab-case**, not snake_case:

| Wrong (snake_case — returns 404) | Right (kebab-case — works) |
|---|---|
| ~~/stock_adjustments~~ | `/adjustments` |
| ~~/test_results~~ | `/test-results` |
| ~~/payment_methods~~ | `/payment-methods` |
| ~~/product_pos_mappings~~ | `/product-pos-mappings` |
| ~~/custom_fields~~ | `/custom-fields` |
| ~~/file_attachments~~ | `/file-attachments` |

**Field names within request/response bodies still use snake_case** — only URL path segments are kebab. This is a deliberate convention split.

## Silent ignore on unknown parameters

Distru returns **HTTP 200** for queries containing unknown filter params, with results matching whatever filters *did* apply. There is no error to indicate "you typo'd this param name."

```bash
# This returns 200 with ALL orders (param silently ignored — not a 400)
GET /public/v1/orders?relationship_type=Customer

# So does this
GET /public/v1/orders?totally_made_up_param=foo
```

**Defensive coding strategy:** when building a filter builder, log a warning when the result-count looks unexpectedly large compared to the expected filter narrowing. Don't rely on Distru telling you the filter is wrong.

## Datetime filters — comma-range strings (NOT `_from`/`_to` pairs)

All datetime filters are **single comma-separated range strings**:

```
?updated_datetime=2026-01-01T00:00:00Z,2026-02-01T00:00:00Z       # both bounds
?updated_datetime=2026-01-01T00:00:00Z,                            # open-ended upper (from this date forward)
?updated_datetime=,2026-02-01T00:00:00Z                            # open-ended lower (everything up to this date)
```

There is **no** `updated_datetime_from` + `updated_datetime_to` pair. The single comma-range parameter is the only form.

### Datetime field names

Endpoints use `inserted_datetime`, `updated_datetime`, `delivery_datetime`, `due_datetime`, `order_datetime`, `invoice_datetime`, `completion_datetime` — all with `_datetime` suffix. NOTE: `purchase_datetime` was claimed by earlier docs but verified 2026-05-26 as NOT a real wire field on /purchases — the actual filter param there is `order_datetime` despite the resource being /purchases.

**Exceptions** (use `_at` suffix instead):
- `/product-pos-mappings` → `inserted_at`, `updated_at`
- `/users` → `deleted_at`

Don't standardize the suffix in the importer — preserve each endpoint's actual field names.

## Multi-value filter syntax — INCONSISTENT across endpoints

There are **two competing forms** used by different endpoints:

### Form 1 — Bracket array (most common)
```
?status[]=COMPLETED&status[]=CANCELED
?product_ids[]=uuid1&product_ids[]=uuid2
?tags[]=tag1&tags[]=tag2
```

### Form 2 — Comma-separated string (used by /products menu_id)
```
?menu_id=uuid1,uuid2,uuid3
```

You **cannot interchange** the two. `?status=COMPLETED,CANCELED` on /orders silently ignores the filter (returns all). `?menu_id[]=uuid1` on /products silently ignores the filter.

### Catalog of multi-value filter syntax (Phase 0.5 audit)

| Endpoint | Multi-value filter | Syntax |
|---|---|---|
| /orders | `status[]` | bracket array |
| /purchases | `status[]` | bracket array (Title Case values) |
| /invoices | `status[]`, `order_id[]` | bracket array |
| /products | `brand_id[]`, `category_id[]`, `vendor_id[]`, `tags[]` | bracket array |
| /products | `menu_id` | **comma-string** (the odd one out) |
| /packages | `product_ids[]`, `statuses[]`, `location_id[]`, `batch_id[]` | bracket array (PLURAL names) |
| /batches | `location_id[]`, `strain_id[]` | bracket array |
| /batches | `product_id` | **SINGULAR string** (NOT product_ids[]) |
| /companies | `tags[]` | bracket array |
| /contacts | `tags[]` | bracket array |
| /test-results | `package_id[]`, `product_id[]` | bracket array |
| /inventory | `grouping[]`, `location_id[]`, `product_id[]`, `batch_id[]`, `strain_id[]` | bracket array |
| /assemblies | `location_id[]` | bracket array |

### Singular vs plural — cross-endpoint naming inconsistency

- `/batches?product_id=<uuid>` (SINGULAR — only one product allowed)
- `/packages?product_ids[]=<uuid>&product_ids[]=<uuid>` (PLURAL — multiple)
- `/orders?status[]=PENDING` (SINGULAR status, bracket array)
- `/packages?statuses[]=ACTIVE` (PLURAL statuses, bracket array)

Same conceptual filter, different param name per endpoint. Don't refactor — preserve.

## Boolean filters

Some endpoints accept boolean filters as `true`/`false` strings:

```
?include_costs=true         # /batches, /packages
?is_active=true             # /payment-methods, /menus
?is_published=true          # /menus
```

`/products` uses a **tri-state** `deleted` filter:
```
?deleted=true               # only deleted
?deleted=false              # only non-deleted (default)
?deleted=only               # only deleted (alias for true on some)
```

## String filters — substring vs exact

Most string filters are **substring matches**:
- `/orders?invoice_number=001` matches `INV-001`, `INV-0012`, `2001-INV`
- `/products?name=Blue` matches "Blue Dream", "Bluefin", etc.

There is no documented exact-match modifier.

## Status casing — Title Case INPUT, UPPERCASE RESPONSE (on /purchases, /invoices)

```
GET /public/v1/purchases?status[]=Pending           # filter requires Title Case
# Response field will be:
"status": "PENDING"                                  # but response is UPPERCASE
```

Same status field, different casing in vs out. The filter-string Title Case is non-negotiable — UPPERCASE in the filter returns 400.

Exception: `/orders` accepts UPPERCASE in filter AND returns UPPERCASE — no flip. Title Case fails on /orders.

## Tenant-customizable enum filters

The following filter values are NOT a fixed enum — tenants can rename, delete, or add values:

- `relationship_type` on /companies (defaults: Customer, Supplier, Distributor, Cultivator, Manufacturer)
- `reason` and `category` on /adjustments
- `role` on /users
- Custom field `type` values

For these, hardcoding a filter value risks 0-result responses if the tenant's deployment doesn't use that default. Discover the actual tenant values via a first-pass scan + dedupe.

## Recommended filter builder

```php
class DistruFilterBuilder
{
    private array $filters = [];

    public function dateRange(string $field, ?string $from, ?string $to): self
    {
        $this->filters[$field] = ($from ?? '') . ',' . ($to ?? '');
        return $this;
    }

    public function bracketArray(string $field, array $values): self
    {
        // Note: param name MUST include the trailing [] per Distru convention
        $key = str_ends_with($field, '[]') ? $field : "{$field}[]";
        foreach ($values as $v) {
            $this->filters[$key][] = $v;
        }
        return $this;
    }

    public function commaString(string $field, array $values): self
    {
        $this->filters[$field] = implode(',', $values);
        return $this;
    }

    public function single(string $field, $value): self
    {
        $this->filters[$field] = $value;
        return $this;
    }

    public function toQuery(): string
    {
        return http_build_query($this->filters);
    }
}
```

PHP's `http_build_query` correctly produces `param%5B%5D=v1&param%5B%5D=v2` for bracket arrays — Distru accepts both URL-encoded `%5B%5D` and bare `[]`.

## Cross-references

- Per-endpoint filter tables: each `categories/*.md` has its own filter parameters table
- Pagination interaction: `patterns/pagination.md`
- Tenant-customizable enum handling: mapping doc Decision #15
