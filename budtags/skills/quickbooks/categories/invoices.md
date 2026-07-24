# QuickBooks Invoice Operations

**Category:** Invoice Operations
**Operations:** 11 methods
**Purpose:** Read, create, update, send, and download invoices

---

## Overview

Invoice operations cover the full lifecycle. Reads come in paginated, all,
cached, and overdue variants. Creation and updates take an array payload that the
service maps into QuickBooks line items. Updates fetch the existing invoice first
to carry its SyncToken.

**See Also:**
- `scenarios/invoice-workflow.md` - Complete invoice workflow
- `ENTITY_TYPES.md` - Invoice and line item types
- `patterns/syncing.md` - SyncToken requirements

---

## Operations

### 1. `get_invoices(int $start_at = 1, int $max_count = 100): LengthAwarePaginator`

Paginated invoices (`SELECT *, Line.* FROM Invoice`) wrapped in a
`LengthAwarePaginator` (path `/orders/quickbooks`). Returns an empty paginator on
error.

### 2. `get_invoices_cached(string $orgId, int $page = 1, int $perPage = 50): LengthAwarePaginator`

Cached wrapper over `get_invoices`, keyed per org and page
(`qbo:invoices:{orgId}:page:{page}`), stale-while-revalidate.

### 3. `get_all_invoices(): Collection`

All invoices, auto-paginated with line detail.

### 4. `get_all_invoices_cached(string $org_id): Collection`

Cached `get_all_invoices` (`qbo:all_invoices:{org_id}`). Backs the JSON
`GET /quickbooks/invoices` endpoint.

### 5. `get_overdue_invoices(): Collection`

Open, past-due invoices (`Balance > '0' AND DueDate < today`), auto-paginated.
Used by the billing/overdue sync.

### 6. `get_invoice(string $id): ?IPPInvoice`

Single invoice by ID (`FindById`), or `null`.

### 7. `get_invoice_count(): int`

Total invoice count (`SELECT COUNT(*) FROM Invoice`).

### 8. `create_invoice(array $invoice_data): IPPInvoice`

Create an invoice with line items.

**Required keys:** `customer_id`, `line_items` (each needs `item_id`, `quantity`,
`unit_price`, `amount`; `description` optional). Line items with a falsy
`item_id` are skipped.

**Optional keys:** `txn_date`, `sales_term_ref`, `due_date`, `doc_number`,
`customer_email` (-> `BillEmail`), `private_note`.

```php
$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'txn_date' => '2026-01-15',
    'due_date' => '2026-02-14',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 10,
            'unit_price' => 25.00,
            'amount' => 250.00,
            'description' => 'Premium Flower',
        ],
    ],
    'private_note' => 'Thank you for your business!',
]);
```

### 9. `update_invoice(string $invoice_id, array $invoice_data): IPPInvoice`

Update header and/or line items. Fetches the existing invoice first (SyncToken),
then applies any provided `doc_number`, `txn_date`, `due_date`, `private_note`,
and `line_items`. Throws `ConflictException` on API error.

```php
$qbo->update_invoice('789', [
    'private_note' => 'Updated terms',
    'line_items' => [
        ['id' => '1', 'item_id' => '456', 'quantity' => 8, 'unit_price' => 25.00, 'amount' => 200.00],
    ],
]);
```

### 10. `send_invoice(string $invoice_id, ?string $send_to_email = null): bool`

Email the invoice via QuickBooks. When `$send_to_email` is null the SDK sends to
the invoice's stored `BillEmail`. Fetches the invoice first; throws on failure;
logs via `LogService`.

```php
$qbo->send_invoice('789', 'customer@example.com');
$qbo->send_invoice('789'); // uses invoice BillEmail
```

### 11. `download_invoice_pdf(string $invoice_id): string`

Download the invoice PDF. Returns a **filesystem path** to the generated temp PDF
(not the binary contents). Throws on error.

```php
$path = $qbo->download_invoice_pdf('789');
return response()->download($path, "invoice-789.pdf");
```

---

## Common Workflows

### Create Then Send
```php
$invoice = $qbo->create_invoice($data);
$qbo->send_invoice($invoice->Id); // to customer BillEmail
```

### Serve the PDF
```php
$path = $qbo->download_invoice_pdf($invoice->Id);
return response()->download($path, "invoice-{$invoice->DocNumber}.pdf");
```

**See:** `scenarios/invoice-workflow.md`.
