# Manufacturing Domain — Assemblies

The Distru Manufacturing domain is, as of v1 public API, a **single endpoint**: Assemblies. An Assembly represents any manufacturing/processing event — a recipe execution, a split, a sales conversion, or a lab-testing destination operation.

> **Distru does not expose write endpoints for Assemblies via the public API.** Assemblies are created inside Distru and read out via this endpoint.

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/assemblies` | List assemblies | Fixed page size 500; eventually consistent ~1s |

## Assembly entity shape (high-level)

```jsonc
{
  "id": "asm_...",
  "completion_datetime": "2026-05-13T18:42:00Z",
  "creation_source": "MANUALLY_CREATED",  // or SPLIT_PACKAGE, SALES_ORDER, LAB_TESTING
  "license_number": "C11-0000123-LIC",
  "input_batches": [
    { "batch_id": "bat_in_1", "quantity": 1000, "unit_of_measure": "g" }
  ],
  "output_batches": [
    { "batch_id": "bat_out_1", "quantity": 850, "unit_of_measure": "g" }
  ],
  "waste": [
    { "amount": 50, "unit_of_measure": "g", "reason": "Trim loss" }
  ],
  "labor": [ /* ... */ ],
  "machine_info": { /* ... */ },
  "custom_fields": { /* ... */ },
  "created_at": "...",
  "updated_at": "..."
}
```

## Creation sources

| Source | Meaning |
|--------|---------|
| `MANUALLY_CREATED` | Operator-initiated assembly (most common for processing runs) |
| `SPLIT_PACKAGE` | Generated when a package is split into smaller units |
| `SALES_ORDER` | Auto-created at order fulfillment to record conversion |
| `LAB_TESTING` | Auto-created when a sample is consumed for lab testing |

When importing, filter on `creation_source` to scope work — e.g., a manufacturing-focused import may want only `MANUALLY_CREATED`, while a compliance audit may include all four.

## Pagination quirk — fixed 500 page size

Assemblies enforces a **hard 500/page cap** that cannot be overridden via `page[size]`. Do not assume your page-size parameter takes effect on this endpoint. Use `next_page` for terminal detection as usual.

## Eventual consistency

Assemblies are **eventually consistent** — a record created inside Distru may take up to ~1s to appear on `GET /assemblies`. Practical guidance:

- The response from the operation that created the Assembly is authoritative; trust it.
- If polling for an Assembly, back off — 1.5s minimum between retries.
- Never use a missing list-query record to conclude a write failed.

See `patterns/eventual-consistency.md`.

## Filters (query-string)

| Param | Meaning |
|-------|---------|
| `completion_datetime_from`, `completion_datetime_to` | Time window on completion |
| `creation_source` | One of the four values above |
| `license_number` | Scope to one license |
| `page[number]` | Pagination |

## Cross-references

- Eventual consistency: `patterns/eventual-consistency.md`
- Workflow: `scenarios/assembly-import-workflow.md`
- Batch references: `categories/inventory.md`
