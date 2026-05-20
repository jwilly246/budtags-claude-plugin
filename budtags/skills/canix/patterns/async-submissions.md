# Canix Async Submissions

## Overview

Certain write operations in Canix that interact with Metrc are processed **asynchronously**. These operations return a Submission UUID that must be polled to determine the outcome.

## Which Operations Use Submissions?

Based on the API documentation, async submissions are used for operations that go through the compliance tracking system (Metrc):

- `POST /items/photos` — Upload METRC item photos
- `POST /items/files` — Upload METRC item files
- Package creation (not exposed in API)
- Inventory adjustments (not exposed in API)
- Transfer submissions (not exposed in API)

**Direct synchronous operations** (do NOT use submissions):
- Sales order CRUD (`POST/PUT /sales_orders`)
- Purchase order CRUD (`POST /purchase_orders`)
- Item CRUD (`POST/PUT/DELETE /items`)
- Strain CRUD (`POST/PUT /strains`)
- Vendor CRUD (`POST/PUT/DELETE /vendors`)
- Standard cost CRUD (`POST/PUT/DELETE /standard_costs`)

## Polling Endpoint

```
GET /submissions/{submission_id}
```

The `submission_id` is a base64-encoded UUID string, e.g., `"U3VibWlzc2lvbjo0NTY3ODk="`.

## Submission Statuses

| Status | Terminal? | Description |
|--------|-----------|-------------|
| `CREATED` | No | Transaction queued for processing |
| `PENDING_APPROVAL` | No | Awaiting admin approval |
| `PENDING` | No | Pending response from compliance system |
| `RETRYING` | No | Failed but will be automatically retried |
| `SUCCESS` | **Yes** | Transaction completed successfully |
| `FAILED` | **Yes** | Transaction failed permanently |
| `DENIED` | **Yes** | Admin reviewed and denied |
| `ABORTED` | **Yes** | Transaction has been aborted |
| `PARTIAL_FAILURE` | **Yes** | Some steps succeeded, others failed |

### Terminal vs Non-Terminal

```php
$terminal_statuses = ['SUCCESS', 'FAILED', 'DENIED', 'ABORTED', 'PARTIAL_FAILURE'];
$is_done = in_array($submission->status, $terminal_statuses);
```

## Submission Response Schema

```json
{
  "uuid": "U3VibWlzc2lvbjo0NTY3ODk=",
  "status": "SUCCESS",
  "readable_name": "Create Package",
  "description": "Package created from harvest\nTag: 1A40000000000000001",
  "error_message": "",
  "result": {
    "package_id": 12345,
    "tag": "1A40000000000000001"
  },
  "created_at": "2024-01-15T10:30:00.000Z",
  "last_run_at": "2024-01-15T10:30:05.000Z"
}
```

### Key Fields

- `status` — Current status (see table above)
- `error_message` — Non-empty when FAILED (describes the error)
- `result` — Non-null when SUCCESS (contains created record IDs/data)
- `last_run_at` — Null if not yet executed

## Polling Implementation

```php
public function poll_submission(string $uuid, int $max_attempts = 30, int $interval_ms = 2000): array
{
    $terminal = ['SUCCESS', 'FAILED', 'DENIED', 'ABORTED', 'PARTIAL_FAILURE'];

    for ($i = 0; $i < $max_attempts; $i++) {
        $submission = $this->api->get("/submissions/{$uuid}");

        if (in_array($submission['status'], $terminal)) {
            return $submission;
        }

        // Exponential backoff: 2s, 4s, 8s... capped at 30s
        $wait = min($interval_ms * pow(2, intdiv($i, 5)), 30000);
        usleep($wait * 1000);
    }

    throw new \RuntimeException("Submission {$uuid} did not complete after {$max_attempts} attempts");
}
```

## Error Handling

```php
$submission = $this->poll_submission($uuid);

match ($submission['status']) {
    'SUCCESS'         => $this->handle_success($submission['result']),
    'FAILED'          => throw new CanixApiException($submission['error_message']),
    'DENIED'          => throw new CanixApiException('Submission denied by admin'),
    'ABORTED'         => throw new CanixApiException('Submission was aborted'),
    'PARTIAL_FAILURE' => $this->handle_partial_failure($submission),
};
```

## Usage in BudTags Import

For the Canix integration, submissions are primarily relevant when:

1. Uploading item photos/files (these go through Metrc)
2. Future write-back features that create packages or transfers

Most BudTags import operations (read) and direct write operations (sales orders, items, strains, vendors) are **synchronous** and do not involve submissions.

---

**See:** `patterns/write-safety.md` for which operations are writable and their safety considerations
