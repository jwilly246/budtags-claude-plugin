# QuickBooks Invoice Operations

**Category:** Invoice Operations
**Operations:** 9 methods
**Purpose:** Create, read, update, send, and download invoices

---

## Overview

Invoice operations handle the complete invoice lifecycle from creation to delivery. Invoices support multiple line items, customer memos, payment terms, and PDF generation.

**Key Concepts:**
- Line items with quantity, price, and tax codes
- SyncToken required for updates
- PDF download and email sending
- Payment term integration

**See Also:**
- `scenarios/invoice-workflow.md` - Complete invoice workflow
- `ENTITY_TYPES.md` - Invoice and OrderLineItem types
- `patterns/syncing.md` - SyncToken requirements

---

## Operations

### 13. `get_invoices(int $start_at = 1, int $max_count = 100)`
Get paginated list of invoices

**Returns:** Array of Invoice objects

### 14. `get_all_invoices()`
Get ALL invoices with automatic pagination

**Returns:** Array of all Invoice objects

### 15. `get_invoice(string $id)`
Get single invoice by QuickBooks ID

**Returns:** Invoice object or `null`

### 16. `get_invoice_count()`
Get total count of invoices

**Returns:** Integer count

### 17. `create_invoice(array $data)`
Create new invoice with line items

**Required:**
- `customer_id` - QuickBooks customer ID
- `line_items` - Array of line item objects

**Line Item Structure:**
```php
[
    'item_id' => '456',           // Required
    'quantity' => 10,             // Required
    'unit_price' => 25.00,        // Required
    'description' => 'Product',   // Optional
    'tax_code_ref' => 'NON'       // Optional
]
```

**Usage:**
```php
$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'txn_date' => '2025-01-15',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 10,
            'unit_price' => 25.00,
            'description' => 'Premium Cannabis Flower'
        ]
    ],
    'customer_memo' => 'Thank you for your business!'
]);
```

**Returns:** Created Invoice object

### 18. `update_invoice(array $data)`
Update existing invoice

**Required:** `id` - QuickBooks invoice ID

**Important:** Fetches current invoice first for SyncToken

**Returns:** Updated Invoice object

### 19. `send_invoice(string $invoice_id, string $email)`
Email invoice to customer

**Parameters:**
- `invoice_id` - QuickBooks invoice ID
- `email` - Recipient email address

**Usage:**
```php
$qbo->send_invoice('789', 'customer@example.com');
```

**Notes:**
- Uses QuickBooks email service
- Sends formatted PDF
- Logs email event via LogService

### 20. `get_invoice_pdf(string $invoice_id)`
Download invoice as PDF

**Returns:** PDF content (binary string)

**Usage:**
```php
$pdf = $qbo->get_invoice_pdf('789');
file_put_contents('invoice.pdf', $pdf);
```

### 21. `delete_invoice(string $id)`
Delete (void) an invoice

**Important:** Invoices cannot be fully deleted, only voided

**Returns:** Void status confirmation

---

## Common Workflows

### Create Invoice with Multiple Line Items
```php
$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'txn_date' => date('Y-m-d'),
    'due_date' => date('Y-m-d', strtotime('+30 days')),
    'line_items' => [
        ['item_id' => '456', 'quantity' => 10, 'unit_price' => 25.00],
        ['item_id' => '457', 'quantity' => 5, 'unit_price' => 15.00]
    ]
]);
```

### Send Invoice via Email
```php
// Create invoice
$invoice = $qbo->create_invoice($data);

// Send to customer
$qbo->send_invoice($invoice->Id, $customer->PrimaryEmailAddr->Address);
```

### Download and Store PDF
```php
$pdf = $qbo->get_invoice_pdf($invoice->Id);
Storage::put("invoices/{$invoice->DocNumber}.pdf", $pdf);
```

**See:** `scenarios/invoice-workflow.md` for complete end-to-end workflow
