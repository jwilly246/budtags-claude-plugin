# Canix API Write Safety

## Overview

All Canix write endpoints (POST, PUT, DELETE) are explicitly marked with this warning:

> **CALLING THIS ENDPOINT WILL MODIFY YOUR DATA IRREVERSIBLY. ONLY CALL THIS ON SANDBOX DATA DURING DEVELOPMENT/CODING/TESTING.**

This means: always test on sandbox first, and implement safeguards in production code.

## Writable Entities

| Entity | POST (Create) | PUT (Update) | DELETE | Notes |
|--------|:---:|:---:|:---:|-------|
| Sales Orders | Yes | Yes | — | + Status transition via PUT |
| Purchase Orders | Yes | — | — | Create only, no update/delete |
| Items | Yes | Yes | Yes | Full CRUD |
| Strains | Yes | Yes | — | Create + update (update has fewer fields) |
| Vendors | Yes | Yes | Yes | Full CRUD |
| Standard Costs | — | Yes | Yes | Update + delete only (create via items endpoint) |
| Item Photos | Yes | — | — | Async via Submissions (Metrc-bound) |
| Item Files | Yes | — | — | Async via Submissions (Metrc-bound) |

## Read-Only Entities

These entities can only be fetched, not modified through the API:

- **Packages** — Read only (created internally via Metrc)
- **Plants** — Read only
- **Plant Batches** — Read only
- **Harvests** — Read only
- **Transfers** — Read only
- **Transfer Destinations** — Read only
- **Locations** — Read only
- **Customers** — Read only (no CRUD endpoints)
- **Brands** — Read only
- **Item Types / Sub-Types** — Read only
- **Non-Cannabis Products** — Read only
- **Manufacturing Batches / Runs** — Read only
- **Bills of Materials** — Read only
- **Company** — Read only
- **Facilities** — Read only
- **Weight Units** — Read only
- **Audited Actions** — Read only

## Sales Order Status Transitions

The status transition endpoint has specific rules:

```
PUT /sales_orders/{id}/status/{status_name}
```

**Valid statuses**: `created`, `approved`, `filled`, `shipped`, `accepted`, `archived`, `requested`, `canceled`

**Cancellation restrictions**: Cannot cancel orders that are `shipped`, `accepted`, `returned`, or `archived`.

## BudTags Bidirectional Sync Safety

When Canix is the source of truth (user has Canix API key configured):

1. **Disable local editing** of synced fields (same pattern as LeafLink disabling invoice editing)
2. **Write-back on save**: When a BudTags record with a `canix_id` is modified, push changes to Canix
3. **Conflict detection**: Compare `updated_at` timestamps — last-write-wins
4. **Dry run mode**: ImportOptions supports `dryRun: true` for testing without mutations
5. **Logging**: Log all write operations via LogService for audit trail

## Best Practices

- Always test against the Canix sandbox environment first
- Implement dry-run mode before enabling production writes
- Log every write operation (request + response) for debugging
- Use optimistic locking with `updated_at` comparison for conflict detection
- Validate all required fields locally before sending to Canix
- Never auto-delete records in Canix without explicit user confirmation

---

**See:** `patterns/async-submissions.md` for handling async write operations that go through Metrc
