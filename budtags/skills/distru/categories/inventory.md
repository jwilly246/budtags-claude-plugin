# Inventory Domain — Batches, Packages, Stock Adjustments

The Distru Inventory domain covers physical product stock. **Batches** are the canonical unit (production/receipt lot); **Packages** are sub-units that derive from Batches. **Stock Adjustments** are append-only correction records.

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/batches` | List batches | `include_costs=true` toggles dual-cost data |
| POST | `/public/v1/batches` | Create batch | WRITE |
| GET | `/public/v1/packages` | List packages | **READ-ONLY** via public API |
| GET | `/public/v1/stock_adjustments` | List adjustments | Page-number pagination |
| POST | `/public/v1/stock_adjustments` | Create adjustment | **APPEND-ONLY** — no PUT, no DELETE |

## Batch entity shape (high-level)

```jsonc
{
  "id": "bat_...",
  "product_id": "prd_...",
  "lot_number": "LOT-2026-04-001",
  "quantity_on_hand": 1250.0,
  "unit_of_measure": "g",
  "location_id": "loc_...",
  "received_at": "2026-04-12T00:00:00Z",
  "expiration_date": "2027-04-12",
  "actual_cost": 8.50,         // only present when include_costs=true
  "default_cost": 9.00,        // only present when include_costs=true
  "custom_fields": { /* ... */ },
  "test_result_ids": ["tr_..."],
  "created_at": "...",
  "updated_at": "..."
}
```

## Package entity shape (high-level)

Packages are derivatives of Batches. Through the public API they are **read-only** — the package lifecycle (split, transfer) happens inside Distru.

```jsonc
{
  "id": "pkg_...",
  "batch_id": "bat_...",
  "product_id": "prd_...",
  "metrc_package_tag": "1A40A0300001234000005678",
  "quantity": 28.0,
  "unit_of_measure": "g",
  "location_id": "loc_...",
  "status": "ACTIVE",
  "created_at": "...",
  "updated_at": "..."
}
```

## Stock Adjustment entity shape (high-level)

Adjustments record a delta against a Batch (or Package, depending on tenant config). Append-only by design: corrections to a prior adjustment require **another adjustment**, not a PUT.

```jsonc
{
  "id": "adj_...",
  "batch_id": "bat_...",
  "delta": -12.0,
  "reason": "Damaged in transit",
  "adjusted_by_user_id": "usr_...",
  "adjusted_at": "2026-05-14T09:00:00Z"
}
```

## Cost data (`include_costs` flag)

By default, `GET /batches` omits cost fields. Pass `include_costs=true` to include both `actual_cost` and `default_cost`. Two-cost model:

- `actual_cost` — what was actually paid for the lot
- `default_cost` — the standing cost assumption for the product

Budtags should prefer `actual_cost` for COGS reconciliation; fall back to `default_cost` when missing.

## Filters (query-string)

| Endpoint | Param | Meaning |
|----------|-------|---------|
| `/batches` | `updated_at_from`, `updated_at_to` | Incremental sync |
| `/batches` | `include_costs` | Toggle cost fields |
| `/batches` | `location_id` | Filter to one warehouse |
| `/stock_adjustments` | `batch_id` | Adjustments for one batch |

## Write Safety

- Batches: POST only documented (no PUT shape confirmed in public docs).
- Packages: read-only.
- Stock Adjustments: POST only — to "undo," POST a counter-adjustment.
- **No idempotency keys** — duplicate adjustments are possible on retry. Reconcile by comparing `created_at` and amounts.

## Cross-references

- Product and batch lineage: `categories/products.md`
- Adjustment audit trail design: `patterns/write-safety.md`
