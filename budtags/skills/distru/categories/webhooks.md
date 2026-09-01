# Distru Webhooks (wire contract)

Source: apidocs.distru.dev Webhooks section, captured 2026-09-01. Webhooks are
NOT in the OpenAPI spec — this doc is the contract. Not yet used by Budtags
(no receiver exists as of 2026-09-01); see DISTRU-API-EXPANSION-RESEARCH.md in
the app repo for the adoption assessment.

## Entity types and what triggers them

Webhook types: **Sales Orders, Purchase Orders, Assemblies, Invoices,
Companies, Returns, Products.** A webhook fires on create, edit, or hard
delete of the record.

Nested-record edits fire the PARENT's webhook (never their own), with `object`
being the full parent:

| Parent | Nested records that trigger it |
|---|---|
| Sales Orders | items, charges |
| Purchase Orders | items, charges |
| Invoices | items, charges, payments |
| Assemblies | inputs, outputs, costs |
| Returns | items |
| Companies | the related company, its locations, its licenses, its contacts (each with profile) |
| Products | bills of materials (and each BOM's inputs and costs) |

**Explicit limitation: inventory quantity changes do NOT trigger Product
webhooks.** There are no package/batch/inventory webhook types at all — stock
freshness still requires polling.

## Payload

JSON POST with six top-level fields:

- `type` — entity type: `ORDER`, `PURCHASE`, `INVOICE`, `PRODUCT`, …
- `event` — `CREATE`, `UPDATE`, or `DELETE` (added 2026-09-01)
- `id` — public id of the entity (same as `object.id`)
- `object` — the FULL entity, in exactly the shape the matching
  `GET /public/v1/<type>/<id>` returns, **fetched fresh at send time** (not a
  snapshot at commit time). `null` on DELETE.
- `changes` — object of changed TOP-LEVEL fields with `before`/`after` values
  (added 2026-09-01). Empty `{}` on CREATE, DELETE, and nested-record-only
  edits. Referenced-record fields carry the full record shape (or `{"id": …}`
  if it no longer exists), never a bare id. Custom-field edits appear as
  `changes.custom_data`: a LIST of `{id, name, value: {before, after}}` (note:
  a list here, unlike the POST-body map).
- `occurred_datetime` — when the change was recorded (UTC); retries keep the
  original value.

`object` matching the GET shape means an existing importer row-pipeline can
parse webhook bodies unchanged. Because `object` is fetched at send time it
can be NEWER than `changes`; the intermediate edit still gets its own webhook.

## Ordering and retries

- Every change gets its own webhook; edits are never collapsed.
- **Per-record ordering guaranteed** (since 2026-09-01): a later webhook for a
  record waits for the earlier one to deliver or be given up on. Different
  records are independent and arrive in any order.
- Non-2xx / unreachable ⇒ retries with increasing delay, ~10 attempts over
  roughly 4 hours, then dropped.

## Signing

Header: `x-distru-signature: sha256=<hex digest>` — HMAC-SHA256 of the RAW
request body with the signing secret provisioned at setup. Verify against raw
bytes (never re-serialize; key order matters) with a constant-time compare.

## Setup

API docs (2026-09-01) say webhook setup goes through Distru Customer Support,
who provide the signing secret. The 2026-08-28 marketing changelog says in-app
webhook management no longer requires superadmin, so customer-tier orgs can
manage their own. One setup per Distru org (Evo, Indulge, Gelato CA, Endo).
