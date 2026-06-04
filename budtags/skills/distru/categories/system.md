# System Domain — Strains, Users, Menus, Payment Methods, Custom Fields, File Attachments

The Distru System domain covers reference data (Strains, Users, Menus, PaymentMethods) and config primitives (CustomFields, FileAttachments). **Five endpoints in this domain had slug errors — the kebab-case rule is in full force here.**

**Phase 0.5 audited 2026-05-21.** Mapping doc: `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md`.

## Endpoints

| Method | Path | Operation | Page size | Notes |
|--------|------|-----------|-----------|-------|
| GET | `/public/v1/strains` | List strains | **50,000** (highest cap in API) | Eventually consistent ~1s. POST also supported (UPSERT). |
| GET | `/public/v1/strains/{id}` | Get one strain | | |
| POST | `/public/v1/strains` | Create or update strain | | UPSERT |
| GET | `/public/v1/users` | List users | 1,000 | |
| GET | `/public/v1/users/{id}` | Get one user | | |
| GET | `/public/v1/menus` | List menus | 500 | |
| GET | `/public/v1/menus/{id}` | Get one menu | | |
| GET | `/public/v1/payment-methods` | List payment methods | 5,000 | **HYPHEN** (`/payment_methods` returns 404) |
| GET | `/public/v1/payment-methods/{id}` | Get one payment method | | |
| POST | `/public/v1/custom-fields` | Create custom field definition | | **HYPHEN, POST-ONLY** (no GET) |
| POST | `/public/v1/file-attachments` | Upload file | | **HYPHEN, POST-ONLY** (no GET). HTTP 422 on quota exceeded. |

### Five slug corrections in this domain

| ~~Wrong slug~~ | Correct slug |
|---|---|
| ~~/payment_methods~~ | `/payment-methods` |
| ~~/custom_fields~~ | `/custom-fields` |
| ~~/file_attachments~~ | `/file-attachments` |
| ~~/stock_adjustments~~ (also lives in inventory) | `/adjustments` |
| ~~/test_results~~ (in products) | `/test-results` |

The six total kebab-case corrections in the API are: `/adjustments`, `/test-results`, `/payment-methods`, `/product-pos-mappings`, `/custom-fields`, `/file-attachments`.

## Strain entity shape

```jsonc
{
  "id": "<uuid>",
  "name": "...",
  "type": "Indica|Sativa|Hybrid|CBD|...",
  "metrc_strain_id": "<string|null>",
  "thc_lower": "<decimal|null>",
  "thc_upper": "<decimal|null>",
  "cbd_lower": "<decimal|null>",
  "cbd_upper": "<decimal|null>",
  "inserted_datetime": "<iso>",
  "updated_datetime": "<iso>"
}
```

### Strain filter parameters

| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | |
| `updated_datetime` | comma-range | |
| `name` | string | |
| `type` | string | |
| `page[number]` | integer | |

Page size cap 50,000 — strains are tiny and orgs can have many. RBAC permission `settings_permissions_strains` is REQUIRED.

## User entity shape

```jsonc
{
  "id": "<uuid>",
  "full_name": "...",
  "email": "...",
  "role": "Admin|Manager|Sales|...",                  // free-text role label (tenant-customizable)
  "banned": <boolean>,
  "deleted_at": "<iso|null>"                          // NOTE: _at suffix, not _datetime
}
```

Users are referenced as `creator` / `owner` embeds on Orders, Invoices, Batches, Adjustments. The `role` field is tenant-customizable text — don't hardcode role parsing.

`deleted_at` uses `_at` suffix (also seen on `/product-pos-mappings`). Most other entities use `_datetime`.

### User filter parameters

| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | |
| `updated_datetime` | comma-range | |
| `email` | string | substring match |
| `page[number]` | integer | |

RBAC permission `settings_permissions_manage_team` is REQUIRED.

## Menu entity shape

```jsonc
{
  "id": "<uuid>",
  "name": "...",
  "is_published": <boolean>,
  "is_active": <boolean>,
  "inserted_datetime": "<iso>",
  "updated_datetime": "<iso>"
  // Menu line-items are NOT exposed via this endpoint
}
```

Menus correlate with the `menu_id` filter on `/products` (comma-string syntax). A product may belong to multiple menus.

### Menu filter parameters

| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | |
| `updated_datetime` | comma-range | |
| `is_published` | boolean | |
| `is_active` | boolean | |
| `page[number]` | integer | |

## Payment Method entity shape

```jsonc
{
  "id": "<uuid>",
  "name": "...",
  "is_active": <boolean>,
  "inserted_datetime": "<iso>",
  "updated_datetime": "<iso>"
}
```

Referenced by ID on `POST /invoices/{id}/payments` and `POST /purchases/{id}/payments`.

### Payment Method filter parameters

| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | |
| `updated_datetime` | comma-range | |
| `is_active` | boolean | |
| `page[number]` | integer | |

RBAC permission `settings_permissions_payment_methods` is REQUIRED.

## Custom Field definitions (POST-only)

```php
$response = $api->post('/custom-fields', [
    'name' => 'Internal Lot Code',
    'type' => 'TEXT',                                   // TEXT | NUMBER | DATE | DROPDOWN | CHECKBOX | TEXTAREA
    'entity_type' => 'PRODUCT',                          // PRODUCT | COMPANY | ORDER | INVOICE | PURCHASE | BATCH | PACKAGE | CONTACT
    // ... + options[] if type=DROPDOWN
]);
// Response includes integer id
```

**No GET endpoint** — read custom field definitions only via `custom_data[]` on entities. Mapping doc Decision #20 covers the 3-tier strategy for preserving custom-field data through import:

1. Tier 1 — store `custom_data[]` JSON verbatim in `distru_*.raw_payload`
2. Tier 2 — reconstruct field definitions table from observed `{id, name, type}` triples
3. Tier 3 — defer native columns until customer has migrated and admin has reviewed

The `id` field on a CustomFieldDefinition is **INTEGER** (not UUID) — matches the `id` in `custom_data[]` entries on entities.

RBAC permission `settings_permissions_custom_fields` is REQUIRED.

## File Attachment uploads (POST-only)

```php
$response = $api->attach('file', $fileContents, $filename)
    ->post('/file-attachments', [
        // ONE of the following ref fields is REQUIRED (entity to attach to):
        'order_id' => '<uuid>',
        // OR
        'invoice_id' => '<uuid>',
        // OR
        'purchase_id' => '<uuid>',
        'company_id' => '<uuid>',
        'contact_id' => '<uuid>',
        'location_id' => '<uuid>',
        'product_id' => '<uuid>',
        'batch_id' => '<uuid>',
        'package_id' => '<uuid>',
        'assembly_id' => '<uuid>',
        'test_result_id' => '<uuid>',
        'request_id' => '<uuid>',                       // HIDDEN entity type
        'task_id' => '<uuid>',                          // HIDDEN entity type
        'stock_transfer_id' => '<uuid>',                // HIDDEN entity type
        'return_id' => '<uuid>',                        // HIDDEN entity type
        'order_shipment_id' => '<uuid>',                // HIDDEN entity type
        'agent_chat_thread_id' => '<uuid>',             // HIDDEN entity type
        'ai_order_intake_id' => '<uuid>',               // HIDDEN entity type
        'ai_purchase_intake_id' => '<uuid>',            // HIDDEN entity type
    ]);
```

Returns HTTP 422 on quota exceeded (storage limit). Otherwise HTTP 200 with attachment id.

### Hidden entity types

The file-attachments endpoint accepts ref fields for 8 entity types that have NO list/GET endpoints in the public API:

- Request
- Task
- StockTransfer
- Return
- OrderShipment
- AgentChatThread
- AIOrderIntake
- AIPurchaseIntake

These exist server-side and have IDs that can be attached to, but the public API does not expose their list/detail endpoints. Migration can preserve attachments for these entity types if the IDs are known from another source (e.g., Distru web UI export), but the entities themselves cannot be enumerated via API.

## RBAC permissions reference (8 distinct permissions for full import)

| Permission | Endpoints gated |
|---|---|
| `orders_permissions_view` | `/orders` |
| `invoices_permissions_view` | `/invoices`, `POST /invoices/{id}/payments` |
| `purchases_permissions_view` | `/purchases`, `POST /purchases/{id}/payments` |
| `products_permissions_view` | `/products`, `/batches`, `/packages`, `/adjustments`, `/inventory`, `/test-results`, `/product-pos-mappings` |
| `companies_permissions_view` | `/companies`, `/locations` |
| `contacts_permissions_view` | `/contacts` |
| `assemblies_permissions_view` | `/assemblies` |
| `settings_permissions_strains` | `/strains` |
| `settings_permissions_manage_team` | `/users` |
| `settings_permissions_payment_methods` | `/payment-methods` |
| `settings_permissions_custom_fields` | `POST /custom-fields` |

Total: 7-8 distinct permissions required for a complete read import. Customers must verify these are enabled on the API key's user before Phase B import begins.

## Cross-references

- Strains referenced by Products and Batches: `categories/products.md`, `categories/inventory.md`
- Users referenced as creator/owner on Orders/Invoices/Purchases/Batches: all
- Payment methods used in payment POSTs: `categories/sales-orders.md`, `categories/purchase-orders.md`
- Custom field handling: mapping doc Decision #20
- Filter conventions: `patterns/filtering.md`
