# Products Domain — Products and Test Results

The Distru Products domain covers the catalog (Products with brand, category, strain, POS mappings) and the lab/COA layer (Test Results with 200+ field types covering cannabinoids, terpenes, pesticides, solvents, microbials).

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/products` | List products | Page-number pagination |
| GET | `/public/v1/products/{id}` | Get one product | Includes brand, category, strain, POS mappings |
| POST | `/public/v1/products` | Create product | UPSERT |
| PUT | `/public/v1/products/{id}` | Update product | UPSERT |
| GET | `/public/v1/test_results` | List test results | 200+ field types |
| POST | `/public/v1/test_results` | Upload test result | UPSERT |
| PUT | `/public/v1/test_results/{id}` | Update test result | UPSERT |

## Product entity shape (high-level)

```jsonc
{
  "id": "prd_...",
  "name": "Blue Dream 3.5g",
  "sku": "BD-35-2026",
  "brand_id": "br_...",
  "brand_name": "Acme Brands",
  "category": "Flower",
  "subcategory": "Indica",
  "strain_id": "str_...",
  "strain_name": "Blue Dream",
  "unit_of_measure": "g",
  "package_size": 3.5,
  "price": 30.00,
  "wholesale_price": 18.00,
  "image_url": "...",
  "pos_mappings": {
    "blaze": { "product_id": "..." },
    "dutchie": { "product_id": "..." },
    "treez": { "product_id": "..." }
  },
  "custom_fields": { /* ... */ },
  "created_at": "...",
  "updated_at": "..."
}
```

## Test Result entity shape (high-level)

Test results carry an array of measured values, each with a field type (`THC_PCT`, `CBD_PCT`, `PESTICIDE_MYCLOBUTANIL_PPB`, etc.) and a value or pass/fail. Linked to a Batch (and through it, a Product).

```jsonc
{
  "id": "tr_...",
  "batch_id": "bat_...",
  "lab_name": "...",
  "sample_id": "...",
  "tested_at": "2026-04-12T00:00:00Z",
  "values": [
    { "field": "THC_PCT", "value": 21.4 },
    { "field": "CBD_PCT", "value": 0.1 },
    { "field": "PESTICIDE_MYCLOBUTANIL_PPB", "value": 0, "passed": true }
  ],
  "coa_url": "..."
}
```

## POS Mappings

Distru maintains parallel product identifiers for the major retail POS systems (Blaze, Dutchie, Treez). When importing into Budtags, surface these as `external_pos_id` records or marketplace-mapping rows so re-syncs can match on multiple keys.

## Strain eventual consistency

The Strains lookup table is **eventually consistent** with ~1s lag after a write. See `patterns/eventual-consistency.md`. Practical impact: when a new product is created with a brand-new strain, the Strain may not appear in `/strains` lookups for a brief moment.

## Filters (query-string)

| Param | Meaning |
|-------|---------|
| `updated_at_from`, `updated_at_to` | Incremental sync |
| `category`, `subcategory` | Catalog filters |
| `brand_id` | Filter to one brand |

## Write Safety

- POST and PUT are UPSERT.
- Image uploads (if supported) may follow a separate URL-pattern — verify before importing images.
- **No idempotency keys** — capture response `id`.

## Cross-references

- Brand and Strain reference data (read via Products endpoint payloads, no dedicated CRUD documented)
- Workflow: `scenarios/product-import-workflow.md`
- Eventual consistency: `patterns/eventual-consistency.md`
