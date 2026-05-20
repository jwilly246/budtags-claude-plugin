# Logistics & System — Transfers, Facilities, Submissions, Audits, Standard Costs

This category covers logistics (transfers), organizational entities (company, facilities), the async submission system, audit trails, and standard cost management.

**Note for BudTags integration**: Transfers overlap with Metrc and are skipped during import. Facilities are imported as reference data for facility scoping. Submissions are used for async write operations. Standard costs are managed through the items endpoint.

## Transfer Endpoints (4 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/transfers` | List active transfers | Paginated, filterable |
| GET | `/transfers/{id}` | Get single transfer | Includes destinations, sales_order link |
| GET | `/transfer_destinations` | List destinations | Paginated, filterable |
| GET | `/transfer_destinations/{id}` | Get single destination | Contents with shipped/received weights |

## Organization Endpoints (3 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/companies/{id}` | Get company by ID | Simple: id, name, timestamps |
| GET | `/facilities` | List facilities | Optional `facility_id` filter |
| GET | `/facilities/{id}` | Get single facility | License number, address |

## Submission Endpoints (1 operation)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/submissions/{id}` | Poll submission status | UUID-based, 9 statuses |

## Audit Endpoints (1 operation)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/audited_actions` | List audit entries | Paginated, filterable |

## Standard Cost Endpoints (3 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/standard_costs/{id}` | Get standard cost | By ID |
| PUT | `/standard_costs/{id}` | Update standard cost | ⚠️ WRITE |
| DELETE | `/standard_costs/{id}` | Delete standard cost | ⚠️ WRITE |

**Note**: Standard costs are created via `POST /items/{id}/standard_cost` (see `categories/products-items.md`).

## Transfer Schema

```json
{
  "id": 123,
  "name": "Transfer",
  "manifest_number": "0000000028",
  "is_active": true,
  "destinations": [
    {
      "id": 456,
      "destination_facility": "401-N0909",
      "transfer_type": "Affiliated",
      "route": "55",
      "departure_time": "2018-11-06T08:00:00.000Z",
      "contents": [
        {
          "package": { ... },
          "status": "shipped",
          "sale_price": 12.34,
          "shipped_weight": 10.00,
          "shipped_weight_unit": "Grams",
          "received_weight": 10.00,
          "received_weight_unit": "Grams"
        }
      ]
    }
  ],
  "sales_order": { ... },
  "updated_at": "2018-11-06T08:00:00.000Z"
}
```

### Key Transfer Fields

- **`manifest_number`** — Official manifest number for compliance
- **`destinations`** — Array of TransferDestination with package contents
- **`sales_order`** — Links transfer to the sales order it fulfills
- **`contents[].shipped_weight` / `received_weight`** — Track weight discrepancies

## Facility Schema

```json
{
  "id": 123,
  "name": "Test Facility",
  "license_number": "4a-x123",
  "is_active": true,
  "address": {
    "street": "123 Cumberland St",
    "street2": "West",
    "city": "Somerset",
    "county": "KY",
    "state": "CO",
    "country": "USA",
    "postal_code": "42504"
  }
}
```

### Key Facility Fields

- **`license_number`** — Facility's compliance license number
- **`is_active`** — Whether facility is currently active
- **`address`** — Full address object

## Company Schema

```json
{
  "id": 123,
  "name": "Test Company",
  "created_at": "2018-11-04T08:00:00.000Z",
  "updated_at": "2018-11-06T08:00:00.000Z"
}
```

Simple entity — just `id`, `name`, and timestamps.

## Submission Schema

See `patterns/async-submissions.md` for full details.

```json
{
  "uuid": "U3VibWlzc2lvbjo0NTY3ODk=",
  "status": "SUCCESS",
  "readable_name": "Create Package",
  "description": "Package created from harvest\nTag: 1A40000000000000001",
  "error_message": "",
  "result": { "package_id": 12345, "tag": "1A40000000000000001" },
  "created_at": "2024-01-15T10:30:00.000Z",
  "last_run_at": "2024-01-15T10:30:05.000Z"
}
```

**9 Statuses**: `CREATED`, `PENDING_APPROVAL`, `PENDING`, `RETRYING`, `FAILED`, `SUCCESS`, `DENIED`, `ABORTED`, `PARTIAL_FAILURE`

## Audited Action Schema

```json
{
  "facility_id": 14,
  "object_id": 1001,
  "object_type": "Package",
  "object_tag": "1A4FF...",
  "context": ["Package Adjustment"],
  "description": "Weight adjusted from 500g to 495g",
  "submitted_date": "2018-11-06T08:00:00.000Z",
  "approval_date": "2018-11-06T08:00:00.000Z",
  "created_at": "2018-11-06T08:00:00.000Z",
  "updated_at": "2018-11-06T08:00:00.000Z"
}
```

Tracks: package adjustments, splits, combines, location changes for plant batches/plants/packages, immatures destroyed, with submitter and approver info.

## Standard Cost Schema

```json
{
  "id": 123,
  "standard_cost_amount": 12.11,
  "standard_cost_currency": "USD",
  "start_date": "2023-04-19",
  "end_date": "2023-05-19"
}
```

### Update Standard Cost Request Body

```json
{
  "cost": 10.50,
  "start_date": "2024-02-03",
  "end_date": "2024-03-03"
}
```

**Required fields**: `cost`, `start_date`. `end_date` is optional.

---

**See:** `patterns/async-submissions.md` for submission polling details
**See:** `patterns/facility-scoping.md` for facility_id usage
**See:** `categories/sales-orders.md` for orders referenced by transfers
