# Pattern — Write Safety

Distru's write surface is small but has sharp edges. POST is **UPSERT** with **non-sparse update semantics** — meaning a nested array (items[], charges[], tags[]) must be sent **complete** on every write, or omitted records get DELETED. No idempotency keys. One DELETE endpoint exists in the entire API.

**Phase 0.5 audited 2026-05-21.** Mapping doc: `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md`.

## The write surface — full inventory

| Endpoint | Method | Operation |
|---|---|---|
| `/public/v1/orders` | POST | UPSERT order (with items[], charges[]) |
| `/public/v1/invoices` | POST | UPSERT invoice (with items[], charges[]) |
| `/public/v1/invoices/{id}/payments` | POST | Insert payment (WRITE-ONLY) |
| `/public/v1/purchases` | POST | UPSERT purchase (Pending status only) |
| `/public/v1/purchases/{id}/payments` | POST | Insert payment (WRITE-ONLY) |
| `/public/v1/companies` | POST | UPSERT company |
| `/public/v1/contacts` | POST | UPSERT contact (no full_name) |
| `/public/v1/locations` | POST | UPSERT location |
| `/public/v1/products` | POST | UPSERT product (with read/write field-name inversions) |
| `/public/v1/strains` | POST | UPSERT strain |
| `/public/v1/product-pos-mappings` | POST | UPSERT POS mapping |
| `/public/v1/product-pos-mappings/{id}` | **DELETE** | **The ONLY DELETE in the API** |
| `/public/v1/custom-fields` | POST | CREATE custom field definition (no GET) |
| `/public/v1/file-attachments` | POST | Upload file (HTTP 422 on quota exceeded; no GET) |

> No write endpoints for: `/batches`, `/packages`, `/adjustments`, `/inventory`, `/assemblies`, `/users`, `/menus`, `/payment-methods`, `/test-results`. These are read-only via the public API. (Inventory primitives are side-effects of order/purchase/assembly completion.)

## UPSERT semantics

POST with no `id` field → creates a new resource and returns it with assigned `id`.

POST with `id` field → updates the existing resource. Distru does NOT support PATCH (partial update) on most resources — every POST is a full-resource replace.

```php
// Create
$new = $api->post('/orders', ['order_number' => 'SO-001', 'company_id' => '...', 'items' => [...]]);
$newId = $new['id'];

// Update — same payload shape, just include the id
$updated = $api->post('/orders', ['id' => $newId, 'order_number' => 'SO-001', 'items' => [...]]);
```

## Non-sparse updates — items[] and charges[] arrays

**This is the easiest way to lose data.** Updating an order without including its existing items[] DELETES them.

```php
// WRONG — this deletes all line items!
$api->post('/orders', [
    'id' => $orderId,
    'internal_notes' => 'Updated note',
    // items array OMITTED — Distru will delete all items
]);

// RIGHT — re-fetch and include the full items array
$existing = $api->get("/orders/{$orderId}");
$api->post('/orders', [
    'id' => $orderId,
    'internal_notes' => 'Updated note',
    'items' => $existing['items'],          // preserve unchanged items
    'charges' => $existing['charges'],
]);
```

Affected arrays (per-endpoint):
- `/orders` → `items[]`, `charges[]`
- `/invoices` → `items[]`, `charges[]`
- `/purchases` → `items[]`, `charges[]`
- `/companies` → `licenses[]`, `tags[]`, `locations[]` (sending empty `tags: []` removes ALL tags)
- `/products` → `tags[]`, `image_urls[]`

**Defensive pattern:** the importer's writeback layer should ALWAYS perform read-modify-write — never blind-POST partial payloads.

## Read/write field name inversions

Several fields use different names on read vs write — the read shape is rich (full embed), the write shape is flat (just the id). Sending the read shape to a POST will fail or silently ignore.

Catalogued in detail in `categories/products.md`. Key examples:

| Read field (response) | Write field (request) |
|---|---|
| `vendor: { id, name, ... }` | `vendor_id: <uuid>` |
| `product_group: { id, name, ... }` | `group_id: <uuid>` (note: NOT `product_group_id`) |
| `brand: { id, name, ... }` | `brand_id: <uuid>` |
| `product_category: { id, name, ... }` | `product_category_id: <uuid>` |
| `is_active: true` | `is_inactive: false` (INVERTED BOOLEAN) |
| `custom_data: [{id, name, type, value}]` | `custom_data: [{id, value}]` (omit name+type) |

The writeback mapper must translate both directions of the shape.

## Server-side immutability rules

Some entities become **read-only** after they pass certain states:

| Entity | Rule |
|---|---|
| `/purchases` | Cannot edit once status is past `Pending`. Distru returns HTTP 400. |
| `/orders` | Some fields locked after status `COMPLETED` (varies by field — Distru returns 400 with field-level errors). |
| `/invoices` | Cannot edit once payments have been recorded. |
| `/contacts` | `full_name` field never accepted — server-derived. |

For these, plan writeback to be staged at the editable state only. Once an entity advances, treat it as snapshot data.

## No idempotency keys

Distru does NOT support `Idempotency-Key` headers (or any equivalent). Two consecutive identical POSTs with no `id` field will create TWO resources.

**Reconciliation strategy:**

1. Track local "intent IDs" (e.g., your Budtags-internal order id).
2. On POST, store the returned Distru `id` alongside the local id.
3. On retry of an ambiguous POST (network timeout, 500 with no body), query for the entity by a natural key (order_number, sku, license_number) BEFORE retrying.
4. If found, store the id and stop. If not found, retry.

## Bulk write — NOT supported

There is no batch/bulk write endpoint. Every POST is one-resource-at-a-time. For migration import, sequential POSTs with conservative pacing (~10/sec) avoid 429s while making forward progress.

## Payment writes — write-only ledger

`POST /invoices/{id}/payments` and `POST /purchases/{id}/payments` insert payment records but **there is no GET for the payment ledger**. The Invoice response includes only `paid_amount` and `remaining_amount` aggregates.

Migration implication: payment history cannot be round-tripped through the API. Customers lose payment line-item detail unless exported via Distru's CSV export.

## The lone DELETE — /product-pos-mappings/{id}

This is the **only DELETE endpoint** in the entire Distru public API. It removes a single POS mapping by id.

```bash
DELETE /public/v1/product-pos-mappings/123
→ 200 OK
```

For all other entities, deletion is not possible via the API. To "delete" a product, use the `is_inactive: true` field on POST (soft-delete via flag). To delete a company/contact/order, you cannot — only the Distru web UI can.

## Write-safety checklist for writeback code

Before any POST is dispatched:

- [ ] Has the entity been GET'd to capture its current state? (mandatory for updates)
- [ ] Are all non-sparse arrays (items, charges, tags) sent complete?
- [ ] Have read-shape embeds been flattened to write-shape ids (vendor → vendor_id, etc.)?
- [ ] Is the entity in an editable state (e.g., purchase still `Pending`)?
- [ ] Is the `full_name` field stripped from contact writes?
- [ ] Has `custom_data[]` been reshaped from `{id, name, type, value}` → `{id, value}`?
- [ ] Is `outstanding_balance_threshold` on Company in INTEGER CENTS, not decimal dollars?
- [ ] Is local intent-id stored so a retry can reconcile?

## Cross-references

- Per-endpoint write specifics: each `categories/*.md`
- Error handling on writes: `patterns/error-handling.md`
- Custom field handling: mapping doc Decision #20
- Cost field preservation on writeback: mapping doc Section 7
