# Reporting - LeafLink API Category

Complete reference for report generation and download endpoints - 3 total operations.

---

## Collection Reference

**OpenAPI Schema:** `schemas/openapi-promotions-reports.json`
**Total Endpoints:** 3
**Company Compatibility:** All company types

---

## Endpoint Overview

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports/` | List available reports |
| POST | `/reports/` | Generate new report |
| GET | `/reports/{id}/download/` | Download generated report |

---

## Common Use Cases

### 1. List Available Reports

```php
$response = $api->get('/reports/');
$reports = $response->json('results');

// Response includes:
// - id, report_type, status
// - created_date, parameters
// - download_url (when ready)
```

### 2. Generate Report

```php
$response = $api->post('/reports/', [
    'report_type' => 'sales',  // sales, inventory, orders
    'start_date' => '2025-01-01',
    'end_date' => '2025-01-31',
    'format' => 'csv',  // csv, xlsx, pdf
    'filters' => [
        'customer' => $customerId,  // Optional filters
        'product_category' => 5
    ]
]);

$report = $response->json();
$reportId = $report['id'];
```

### 3. Check Report Status

```php
$response = $api->get("/reports/{$reportId}/");
$report = $response->json();

if ($report['status'] === 'completed') {
    $downloadUrl = $report['download_url'];
    // Report ready to download
} else {
    // Status: 'pending', 'processing', 'failed'
}
```

### 4. Download Report

```php
// Once status is 'completed'
$response = $api->get("/reports/{$reportId}/download/");

// Save file
file_put_contents("report_{$reportId}.csv", $response->body());

// Or redirect user to download URL
return redirect($report['download_url']);
```

### 5. Poll for Report Completion

```php
// Reports are generated asynchronously
$maxAttempts = 30;
$attempt = 0;

do {
    sleep(2);  // Wait 2 seconds between checks
    $response = $api->get("/reports/{$reportId}/");
    $report = $response->json();
    $attempt++;
} while ($report['status'] !== 'completed' && $attempt < $maxAttempts);

if ($report['status'] === 'completed') {
    // Download report
    $file = $api->get("/reports/{$reportId}/download/")->body();
}
```

---

## Report Types

### Sales Reports
- Order totals and trends
- Revenue by product/category
- Customer purchasing patterns
- Sales rep performance

### Inventory Reports
- Stock levels across facilities
- Low stock alerts
- Inventory turnover
- Batch tracking

### Order Reports
- Order history and details
- Fulfillment metrics
- Delivery performance
- Pending orders

---

## Report Formats

### CSV (Comma-Separated Values)
- Best for: Data analysis, Excel import
- File extension: `.csv`
- Easy to parse programmatically

### XLSX (Excel)
- Best for: Spreadsheet viewing, formatting
- File extension: `.xlsx`
- Maintains formatting, formulas

### PDF
- Best for: Printing, archiving
- File extension: `.pdf`
- Fixed format, not editable

---

## Report Status

| Status | Description | Action |
|--------|-------------|--------|
| `pending` | Report queued | Wait |
| `processing` | Report generating | Poll for completion |
| `completed` | Report ready | Download |
| `failed` | Generation error | Check error message, retry |

---

## Available Filters

### Date Filters
- `start_date`, `end_date` - Report date range
- `created_date__gte`, `created_date__lte` - Report creation range

### Report Filters
- `report_type` - Type of report
- `status` - Current status
- `format` - Output format

### Custom Filters (per report type)
Varies by report type:
- Customer, product, category filters
- Facility, location filters
- Sales rep, order status filters

---

## Important Notes

### Asynchronous Generation

Reports are NOT generated immediately:
1. POST request creates report job
2. Status starts as `pending` or `processing`
3. Poll GET endpoint until status is `completed`
4. Download via `/download/` endpoint

Typical generation time: 5-30 seconds depending on data size.

### Download URLs

- Download URLs are temporary
- URLs expire after 24-48 hours
- Save file locally if needed long-term
- Can re-generate report if URL expires

### Rate Limits

- Limited concurrent report generations
- Recommended: Generate reports during off-peak hours
- Large reports may take longer to process

---

## Best Practices

✅ **Do:**
- Poll with reasonable intervals (2-5 seconds)
- Set maximum retry attempts
- Handle failed reports gracefully
- Save downloaded reports to local storage
- Use appropriate format for use case

❌ **Don't:**
- Poll too frequently (< 1 second intervals)
- Generate massive date ranges unnecessarily
- Assume immediate completion
- Leave reports without cleanup

---

## Related Resources

- **Schema:** `schemas/openapi-promotions-reports.json`

---

## Quick Reference

```php
// Generate report
$report = $api->post('/reports/', ['report_type' => 'sales', 'start_date' => '2025-01-01', 'end_date' => '2025-01-31']);

// Check status
$status = $api->get("/reports/{$reportId}/")->json('status');

// Download (when completed)
$file = $api->get("/reports/{$reportId}/download/")->body();
file_put_contents("report.csv", $file);
```
