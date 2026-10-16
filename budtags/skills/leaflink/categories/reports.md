# Reporting - LeafLink API Category

Reference for report export endpoints - 3 operations. Checked against the official spec (`~/budtags-audits/2026-10-15/leaflink_docs_gap_audit/official_openapi.json`); not exercised in the 2026-10-16 sandbox tests.

---

## Collection Reference

**OpenAPI Schema:** `schemas/openapi-promotions-reports.json`
**Total Endpoints:** 3
**Company Compatibility:** All company types (legacy User tokens see only report types the user has permission for)

---

## Endpoint Overview

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports/` | List reports generated under the company scope |
| POST | `/reports/` | Request a new report export (201) |
| GET | `/reports/{number}/` | Retrieve one report |

There is no `/reports/{id}/download/` endpoint. The finished file is in the report's `export` field.

---

## ReportDownload Fields (spec)

| Field | Type | Notes |
|-------|------|-------|
| `number` | string | Report id used in `/reports/{number}/` |
| `report_type` | string | **Required**; enum below |
| `company` | integer | **Required** |
| `query` | object | Report query (shape not documented) |
| `status` | string | `running`, `failed`, `completed` |
| `user` | integer | Staff user who requested it |
| `request_time` | string | When it was requested |
| `complete_time` | string | When the export email was sent |
| `export` | string | The exported document |
| `to_email` | string | Where the export was emailed |

**`report_type` values:** `orders-assigned`, `orders-received`, `orders-sent`, `orders-report`, `ordered-products`, `accounts-receivable`, `customer-value`, `sales-rep-activity-feed`, `brand-performance`, `brand-owner-brand-performance`, `brand-owner-inventory-overview`.

The spec lists no `format`, `start_date`, `end_date` or `filters` fields; any date range goes in `query`, whose shape is undocumented.

---

## Common Use Cases

### 1. List Reports

```php
$response = $api->get('/reports/', ['limit' => 50]);
$reports = $response->json('results');
// each: number, report_type, status, request_time, complete_time, export, to_email
```

### 2. Request a Report

```php
$response = $api->post('/reports/', [
    'company' => $companyId,
    'report_type' => 'accounts-receivable',
    'query' => [],   // undocumented shape
]);

$reportNumber = $response->json('number');
```

### 3. Check Report Status

```php
$report = $api->get("/reports/{$reportNumber}/")->json();

if ($report['status'] === 'completed') {
    $export = $report['export'];
} elseif ($report['status'] === 'failed') {
    // handle failure
}
// otherwise 'running'
```

### 4. Poll for Completion

```php
// Reports run asynchronously
$maxAttempts = 30;
$attempt = 0;

do {
    sleep(2);
    $report = $api->get("/reports/{$reportNumber}/")->json();
    $attempt++;
} while ($report['status'] === 'running' && $attempt < $maxAttempts);
```

---

## Report Status

| Status | Description | Action |
|--------|-------------|--------|
| `running` | Report generating | Poll |
| `completed` | Report ready | Read `export` |
| `failed` | Generation error | Retry or check `query` |

---

## Available Filters (spec)

- `company_slug` - Company slug
- `limit`, `offset` - Paging

No `report_type`, `status` or date filters exist on the list.

---

## Important Notes

- Reports are asynchronous: POST creates the job; poll `GET /reports/{number}/` until `status` leaves `running`.
- `complete_time` is described as the time the export email was sent; the export also goes to `to_email`.
- Download URL lifetime, generation time and concurrency limits are not documented.

---

## Related Resources

- **Schema:** `schemas/openapi-promotions-reports.json`

---

## Quick Reference

```php
// Request report
$report = $api->post('/reports/', ['company' => $companyId, 'report_type' => 'orders-received']);

// Check status
$status = $api->get("/reports/{$report->json('number')}/")->json('status');   // running | completed | failed

// Result
$export = $api->get("/reports/{$report->json('number')}/")->json('export');
```
