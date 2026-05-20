# System Domain — Locations, Custom Fields, Users, Roles, Payment Methods, POS Mappings

System endpoints expose tenant configuration and reference data referenced by other domains.

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/locations` | List locations | Warehouses and facilities |
| POST | `/public/v1/locations` | Create location | UPSERT |
| PUT | `/public/v1/locations/{id}` | Update location | UPSERT |
| GET | `/public/v1/custom_fields` | List custom fields | Reference (read-only via public API) |
| GET | `/public/v1/users` | List users | Reference |
| GET | `/public/v1/roles` | List roles | Reference |
| GET | `/public/v1/payment_methods` | List payment methods | Reference |
| GET | `/public/v1/pos_mappings` | List POS mappings | Blaze/Dutchie/Treez identifiers |

> Reference endpoints not all confirmed in the public docs as separate URLs — some are returned inline on the entities that reference them (e.g., `pos_mappings` inside a Product payload). Verify per endpoint before assuming a standalone GET exists.

## Location entity shape (high-level)

```jsonc
{
  "id": "loc_...",
  "name": "Main Warehouse",
  "address": {
    "line_1": "123 Cannabis Ave",
    "city": "Oakland",
    "state": "CA",
    "postal_code": "94601"
  },
  "license_number": "C11-0000123-LIC",
  "location_type": "WAREHOUSE",
  "created_at": "...",
  "updated_at": "..."
}
```

## Custom fields

Each business resource (Orders, Products, Companies, etc.) supports tenant-defined custom fields, returned as a `custom_fields` object on the resource and described by `GET /custom_fields`. Treat custom fields as opaque key-value pairs when importing — Budtags stores them as JSON, not as typed columns.

## POS Mappings

Where present, POS mappings link a Distru entity to its identifier in an external retail POS (Blaze, Dutchie, Treez). Use these identifiers as alternate keys when syncing — Budtags' marketplace integration layer already understands the concept of external IDs.

## Filters

| Endpoint | Param | Meaning |
|----------|-------|---------|
| `/locations` | `location_type` | WAREHOUSE / FACILITY / etc. |
| `/locations` | `license_number` | Scope by license |
| `/users`, `/roles` | (none documented) | Often returns small reference lists |

## Cross-references

- Custom fields are referenced from every business category — see their respective files
- POS mappings detail: `categories/products.md`
