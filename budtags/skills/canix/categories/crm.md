# CRM — Customers & Vendors

Canix separates **customers** (entities you sell to) from **vendors** (entities you buy from). Customers are read-only via API; vendors have full CRUD.

## Customer Endpoints (2 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/customers` | List active customers | Returns CustomerExtended with outstanding_balance |
| GET | `/customers/{id}` | Get single customer | Returns Customer |

**Note**: Customers are **read-only** — no create, update, or delete endpoints.

## Vendor Endpoints (6 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/vendors` | List active vendors | Paginated, filterable |
| POST | `/vendors` | Create vendor | ⚠️ WRITE |
| GET | `/vendors/{id}` | Get single vendor | Full details |
| PUT | `/vendors/{id}` | Update vendor | ⚠️ WRITE |
| DELETE | `/vendors/{id}` | Delete vendor | ⚠️ WRITE, returns 204 |

## Customer Schema

```json
{
  "id": 345,
  "contact_name": "John Smith",
  "company_name": "Zen Ltd",
  "facility_license_number": "2020124",
  "license_type": "3",
  "customer_number": "247123",
  "license_expiration_date": "2020-04-24",
  "phone": "1222312",
  "email": "john.doe@example.com",
  "territory": "abc",
  "address": {
    "street": "123 Cumberland St",
    "street2": "West",
    "city": "DL",
    "county": "LN",
    "state": "OK",
    "postal_code": "111001"
  },
  "notes": "great customer!",
  "outstanding_balance": 0,
  "dba": "Doing Business As",
  "is_active": true,
  "updated_at": "2020-04-24T02:18:42.703Z"
}
```

### Key Customer Fields

- **`facility_license_number`** — Customer's license number (string)
- **`license_type`** — License type identifier
- **`customer_number`** — Customer's internal reference number
- **`territory`** — Sales territory assignment
- **`outstanding_balance`** — Only in list endpoint (CustomerExtended)
- **`dba`** — "Doing Business As" name
- **`is_active`** — Whether customer is active
- **`address`** — Nested Address object

## Vendor Schema

```json
{
  "id": 123,
  "name": "Canna Cones",
  "is_active": true,
  "contact_name": "John Smith",
  "email": "john@cannacones.com",
  "phone": "+16501109234",
  "license_number": "X-000012",
  "license_expiration_date": "2022-03-16T07:00:00Z",
  "address": "63 Bluxome St.",
  "address2": "Suite A",
  "city": "San Francisco",
  "postal_code": "94107",
  "state": "CA",
  "country": "US",
  "website_url": "cannacones.com",
  "notes": "Best vendor",
  "min_lead_time": { "value": 2, "unit": "week" },
  "updated_at": "2018-11-06T08:00:00.000Z"
}
```

### Key Vendor Fields

- **`license_number`** / **`license_expiration_date`** — Vendor's license info
- **`min_lead_time`** — Object with `value` (integer) and `unit` (string: day, week, month)
- **Address fields** — Flat fields (not nested object like Customer)
- **`is_active`** — Whether vendor is active

## VendorRequestBody (Create/Update)

```json
{
  "name": "Canna Cones",
  "contact_name": "John Smith",
  "email": "john@cannacones.com",
  "phone": "+16501109234",
  "license_number": "X-000012",
  "license_expiration_date": "2022-03-16",
  "address": "63 Bluxome St.",
  "address2": "Suite A",
  "city": "San Francisco",
  "postal_code": "94107",
  "state": "CA",
  "country": "US",
  "website_url": "cannacones.com",
  "notes": "Best vendor",
  "min_lead_time": { "value": 2, "unit": "week" }
}
```

**Required fields**: `name` only. All other fields are optional.

## Customer vs Vendor Address Differences

| Aspect | Customer | Vendor |
|--------|----------|--------|
| Format | Nested `address` object | Flat fields (`address`, `city`, `state`, etc.) |
| County | Yes (`county` field) | No |
| Country | In address object | Top-level field |
| Street2 | In address object | Top-level field |

## Common Queries

```php
// Fetch all customers
$customers = $api->get('/customers', [
    'limit' => 2000,
    'where' => "is_active=true",
    'order_by' => 'company_name asc',
]);

// Fetch vendors for import
$vendors = $api->get('/vendors', [
    'limit' => 2000,
    'order_by' => 'id asc',
]);

// Create vendor from BudTags
$vendor = $api->post('/vendors', [
    'name' => 'New Vendor',
    'email' => 'vendor@example.com',
    'license_number' => 'LIC-001',
]);
```

## BudTags Mapping

### Customers
| Canix Field | BudTags Field | Model |
|-------------|---------------|-------|
| `id` | `canix_id` | Customer |
| `company_name` | `name` | Customer |
| `contact_name` | `contact_name` | Customer |
| `email` | `email` | Customer |
| `phone` | `phone` | Customer |
| `facility_license_number` | `license_number` | Customer |
| `address.*` | Address fields | Customer |

### Vendors (NEW model in BudTags)
| Canix Field | BudTags Field | Model |
|-------------|---------------|-------|
| `id` | `canix_id` | Vendor |
| `name` | `name` | Vendor |
| `email` | `email` | Vendor |
| `phone` | `phone` | Vendor |
| `license_number` | `license_number` | Vendor |
| Address fields | `address`, `city`, `state`, `zipcode` | Vendor |

---

**See:** `categories/sales-orders.md` for orders that reference customers
**See:** `categories/purchase-orders.md` for orders that reference vendors
**See:** `scenarios/customer-import-workflow.md` for import workflow
