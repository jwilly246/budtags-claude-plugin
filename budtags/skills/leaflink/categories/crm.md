# CRM & Contacts - LeafLink API Category

Reference for contacts and activity entries.

Behaviour lines are tagged "verified 2026-10-16 (sandbox, <file>)"; raw files are in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/`. `patterns/verified-behavior.md` wins on any conflict.

---

## Collection Reference

**OpenAPI Schema:** `schemas/openapi-crm.json`
**Total Endpoints:** 10
**Company Compatibility:** All company types

---

## Endpoint Overview

### Contacts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/contacts/` | List contacts (includes deleted ones by default) |
| POST | `/contacts/` | Create contact (required: `owner`, `first_name`) |
| GET | `/contacts/{id}/` | Get contact details |
| PATCH | `/contacts/{id}/` | Update contact (partial) |
| DELETE | `/contacts/{id}/` | Sets `delete: true`; the row stays |

### Activity Entries

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/activity-entries/` | List activity entries |
| POST | `/activity-entries/` | Create entry (required: `type`, `entry`, `owner`, `author`) |
| GET | `/activity-entries/{id}/` | Get entry |
| PATCH | `/activity-entries/{id}/` | Update entry |
| DELETE | `/activity-entries/{id}/` | Sets `delete: true` (spec: "These can be filtered out in list requests.") |

There is no `/notes/` endpoint in the official spec.

---

## Contact Fields (spec `Contact`)

`id`, `owner`, `first_name` (max 30), `last_name` (max 30), `email`, `secondary_email`, `role`, `description`, `phone`, `phone_extension`, `secondary_phone`, `secondary_phone_extension`, `delete`, `created_on`, `modified`.

There is no `customer`, `company`, `title`, `is_primary` or `active` field. A customer's contacts come from `GET /customers/?include_children=contacts` (verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)).

## Activity Entry Fields (spec `CompanyActivityEntry`)

`id`, `type` (free string in the spec), `date`, `entry` (the message), `owner`, `author`, `company`, `customer`, `staff`, `brand`, `contact`, `delete`, `created_on`, `modified`.

---

## Common Use Cases

### 1. Create Contact

```php
// phone: 10 bare digits only
$response = $api->post('/contacts/', [
    'owner' => $companyId,
    'first_name' => 'John',      // max 30 chars
    'last_name' => 'Smith',      // max 30 chars
    'email' => 'john@example.com',
    'phone' => '3135550100',
    'role' => 'Buyer',
]);
```

### 2. List Live Contacts

```php
// The default list INCLUDES deleted contacts - always filter delete=false.
// verified 2026-10-16 (sandbox, r2_t8_contacts.txt)
$response = $api->get('/contacts/', [
    'delete' => 'false',
    'modified__gte' => '2026-10-16T00:00:00Z',  // honoured (r3_a_param_sweep.txt)
]);

$contacts = $response->json('results');
```

### 3. Log Activity Entry

```php
$response = $api->post('/activity-entries/', [
    'owner' => $companyId,
    'author' => $staffId,
    'customer' => $customerId,
    'contact' => $contactId,  // Optional
    'type' => 'call',
    'entry' => 'Discussed delivery timeline and payment terms.',
    'date' => '2026-10-16T17:00:00Z',
]);
```

### 4. Get Activity History

```php
$response = $api->get('/activity-entries/', [
    'customer' => $customerId,
    'date__gte' => '2025-01-01T00:00:00Z',
    'date__lte' => '2025-01-31T23:59:59Z',
    'delete' => 'false',
    'limit' => 100,
]);
```

### 5. Update Contact

```php
// Partial: only the sent keys change - verified 2026-10-16 (sandbox, r2_t12_contact_patch.txt T12.1)
$response = $api->patch("/contacts/{$contactId}/", [
    'email' => 'new.email@example.com',
    'phone' => '3135559999',
]);
```

---

## Contact Write Rules (verified 2026-10-16, sandbox, r2_t12_contact_patch.txt / r2_t8_contacts.txt)

- **`phone` must be 10 bare digits.** `(313) 555-0100`, `+13135550100`, `313.555.0100` -> 400 `"Phone number must consist of 10 digits."` Strip formatting before every push. (Customer phones accept formatting; contact phones do not.)
- **`first_name` over 30 chars -> 400** `"Ensure this field has no more than 30 characters."` (T12.7). `last_name` has the same limit (spec).
- `description: null` reads back `""`; `role: null` and `last_name: ""` are accepted (T12.5, T12.6).
- **DELETE sets `delete: true`; the row stays.** `GET /contacts/{id}/` still returns 200 with `delete: true` (r2_t8_contacts.txt).
- **The default `/contacts/` list includes deleted contacts**: 1381 = 496 deleted + 885 live. `delete=false` returns only live ones; `delete=true` only deleted ones (r2_t8_contacts.txt).

---

## Available Filters (spec)

### Contact Filters
- `id`, `owner`, `company_slug`
- `first_name`, `first_name__in`, `first_name__startswith`
- `last_name`, `last_name__in`, `last_name__startswith`
- `delete` - deletion flag (verified honoured)
- `created_on__gt/__gte/__lt/__lte`, `modified__gt/__gte/__lt/__lte` (`modified__gte` verified honoured)

### Activity Filters
- `customer`, `contact`, `company`, `brand`, `staff`, `owner`, `author` (and `*_id` forms)
- `type` (comma list), `entry`, `entry__in`, `entry__startswith`, `search`
- `date__gt/__gte/__lt/__lte`, `created_on__*`, `modified__*`
- `delete` / `is_deleted`
- `fields_include`, `fields_exclude`, `fields_add`, `ordering`

There is no `created_date__*`, `email__icontains`, `is_primary`, `active` or `activity_date__*` filter.

---

## Important Notes

### Contact vs Customer

- **Customer** = the seller's CRM record of a buyer company
- **Contact** = an individual person
- A customer can have many contacts; read them via `include_children=contacts` on `/customers/`

---

## Related Resources

- **Scenarios:** `scenarios/customer-workflow.md`
- **Patterns:** `patterns/verified-behavior.md`
- **Schema:** `schemas/openapi-crm.json`

---

## Quick Reference

```php
// Create contact (10-digit phone, names <= 30 chars)
$api->post('/contacts/', ['owner' => $companyId, 'first_name' => 'John', 'phone' => '3135550100']);

// List live contacts
$api->get('/contacts/', ['delete' => 'false']);

// Log activity
$api->post('/activity-entries/', ['owner' => $companyId, 'author' => $staffId, 'customer' => $id, 'type' => 'call', 'entry' => 'Follow-up']);

// Get activities
$api->get('/activity-entries/', ['customer' => $customerId, 'date__gte' => '2025-01-01T00:00:00Z']);
```
