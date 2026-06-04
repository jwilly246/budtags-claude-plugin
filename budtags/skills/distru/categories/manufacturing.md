# Manufacturing Domain — Assemblies

The Distru Manufacturing domain covers production runs ("Assemblies") that consume ingredient packages and produce output packages, with optional labor/machine cost layering. Read-only via API (no POST).

**Phase 0.5 audited 2026-05-21.** Mapping doc: `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md`.

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/assemblies` | List assemblies | Page size 5,000. **SLOW (~26s)**. Eventually consistent ~1s. |
| GET | `/public/v1/assemblies/{id}` | Get one assembly | Same nested shape as list. |

> No POST. Assemblies must be created via the Distru web UI; the API exposes them read-only.

## Assembly entity shape

```jsonc
{
  "id": "<uuid>",
  "assembly_number": "AS-123",
  "status": "Active|Completed|Canceled|...",
  "creator": { /* User ref */ },
  "location": { /* Location ref | null */ },
  "started_datetime": "<iso|null>",
  "completed_datetime": "<iso|null>",
  "inserted_datetime": "<iso>",
  "creation_source": "MANUAL|ORDER|...",                              // SCALAR — not array (Phase 0.5 correction)
  // NO updated_datetime field at all (Phase 0.5 finding — not in response)

  "outputs": [                                                          // Output packages produced
    {
      "id": "<uuid>",
      "product": { /* Product ref */ },
      "batch": { /* Batch ref */ },
      "package": { /* Package ref */ },
      "quantity": "<decimal>",
      "compliance_type": "METRC|BIOTRACK|NONE",                          // 3-value enum
      "cost_per_unit_actual": "<decimal>",
      "cost_per_unit_default": "<decimal>",
      "total_cost_actual": "<decimal>",
      "total_cost_default": "<decimal>"
    }
  ],
  "ingredients": [                                                      // Input packages consumed
    {
      "id": "<uuid>",
      "product": { /* Product ref */ },
      "batch": { /* Batch ref */ },
      "package": { /* Package ref */ },
      "quantity_used": "<decimal>",
      "cost_per_unit_actual": "<decimal>",
      "total_cost_actual": "<decimal>"
    }
  ],
  "additional_costs": [                                                 // Labor / overhead / machine
    {
      "id": "<uuid>",
      "name": "<string>",
      "type": "LABOR|MACHINE|OVERHEAD|OTHER",
      "amount": "<decimal>",
      "notes": "<string|null>"
    }
  ]
}
```

### Important Phase 0.5 corrections

- **`creation_source` is a SCALAR** (string), NOT an array. Earlier docs implied an array shape; the live API returns a single value.
- **No `updated_datetime` field** — assemblies don't expose an updated timestamp on the response. Use `inserted_datetime` for ingestion ordering; for change detection, refetch by id.
- **No `labor[]` array, no `machine_info` object** — earlier doc drafts marked these `unknown`. They don't exist as separate fields. Labor and machine costs both live in `additional_costs[]` discriminated by `type`.

## Filter parameters

| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | Only datetime filter — there is no `updated_datetime` filter because the field doesn't exist on the entity |
| `status` | string | Single value, not bracket array |
| `creation_source` | string | Single value, scalar match |
| `location_id[]` | bracket array | |
| `license_number` | string | |
| `page[number]` | integer | |

**No `updated_datetime` filter exists.** For incremental sync, use `inserted_datetime` as the watermark, or refetch periodically by id.

## Performance — slowest endpoint

`/assemblies` regularly takes 20-30s to respond, even with small `page[size]`. The nested aggregation across outputs / ingredients / additional_costs is server-expensive. Strategy:

- Use background queues for assembly imports.
- Set HTTP client timeout to **60s minimum** for this endpoint.
- Don't block user-facing requests on `/assemblies` calls.
- Eventually consistent ~1s after write — but writes happen only via the web UI, not the API.

## Compliance type values (3-value enum)

`compliance_type` on each output:
- `METRC` — output package is Metrc-tagged
- `BIOTRACK` — output package is Biotrack-tracked
- `NONE` — non-compliance-tracked output

## Cost layering

Each output's `cost_per_unit_actual` is derived from `ingredients[]` actual costs + `additional_costs[]` distributed across outputs by a Distru-internal allocation algorithm. The breakdown is not exposed via API — only the final per-output `*_actual` and `*_default` values.

Mapping doc Section 7 ("Cost Fidelity") describes how Budtags's mirror tables preserve enough to reconstruct allocation later. For Phase A, store the per-output values verbatim and re-derive allocation only if/when needed.

## Cross-references

- Output products and ingredient products: `categories/products.md`
- Output batches and packages: `categories/inventory.md`
- Assembly import workflow: `scenarios/assembly-import-workflow.md`
- Cost fidelity strategy: mapping doc Section 7
- Eventual consistency: `patterns/eventual-consistency.md`
