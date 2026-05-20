# CRM Domain — Companies and Contacts

The Distru CRM domain covers all external counterparties — customers and vendors are both represented as **Companies**, distinguished by their `relationship_type` and `category` fields. **Contacts** are people associated with Companies.

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/companies` | List companies | Filter by category and relationship_type |
| POST | `/public/v1/companies` | Create company | UPSERT |
| PUT | `/public/v1/companies/{id}` | Update company | UPSERT |
| GET | `/public/v1/contacts` | List contacts | Page-number pagination |
| POST | `/public/v1/contacts` | Create contact | UPSERT |
| PUT | `/public/v1/contacts/{id}` | Update contact | UPSERT |

## Company entity shape (high-level)

```jsonc
{
  "id": "co_...",
  "name": "Acme Cannabis Co",
  "dba": "Acme Co",
  "license_number": "C11-0000123-LIC",
  "license_type": "Retailer",
  "relationship_type": "CUSTOMER",   // or VENDOR, both, neither
  "category": "Retail",
  "email": "ap@acme.example",
  "phone": "+1-555-555-1212",
  "billing_address": { /* ... */ },
  "shipping_address": { /* ... */ },
  "custom_fields": { /* ... */ },
  "created_at": "...",
  "updated_at": "..."
}
```

## Contact entity shape (high-level)

```jsonc
{
  "id": "con_...",
  "company_id": "co_...",
  "name": "Jane Buyer",
  "role": "Purchasing Manager",
  "email": "jane@acme.example",
  "phone": "+1-555-555-1213",
  "custom_fields": { /* ... */ }
}
```

## Filters (query-string)

| Param | Meaning |
|-------|---------|
| `relationship_type` | CUSTOMER / VENDOR / both |
| `category` | Tenant-defined category label |
| `updated_at_from`, `updated_at_to` | Incremental sync |
| `name` | Partial match (verify) |

## Customer vs Vendor distinction

A single Company can be **both** a customer and a vendor simultaneously. Look at `relationship_type` (and/or `category`) to decide which Budtags-side table the row should populate. The customer-import workflow consults both signals — see `scenarios/customer-import-workflow.md`.

## Write Safety

- UPSERT on POST and PUT.
- Contacts must reference an existing `company_id`. Create the Company first.
- **No idempotency keys** — capture response `id`.

## Cross-references

- Workflow: `scenarios/customer-import-workflow.md`
- Write semantics: `patterns/write-safety.md`
