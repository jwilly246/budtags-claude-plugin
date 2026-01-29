# Invoice Workflow

Complete guide to creating, updating, sending, and managing QuickBooks invoices in BudTags.

---

## Table of Contents

1. [Creating Invoices](#creating-invoices)
2. [Updating Invoices](#updating-invoices)
3. [Sending Invoices](#sending-invoices)
4. [Downloading Invoice PDFs](#downloading-invoice-pdfs)
5. [Querying Invoices](#querying-invoices)
6. [Invoice Validation](#invoice-validation)
7. [Common Patterns](#common-patterns)
8. [Troubleshooting](#troubleshooting)

---

## Creating Invoices

### Basic Invoice Creation

**Method:** `create_invoice(array $data)`

**Minimum Required Fields:**
- `customer_id` - QuickBooks customer ID
- `line_items` - Array of line items (at least one)

**Basic Example:**
```php
$qbo = new QuickBooksApi();
$qbo->set_user($user);

$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 10,
            'unit_price' => 25.00
        ]
    ]
]);

echo "Invoice #{$invoice->DocNumber} created\n";
echo "Total: \${$invoice->TotalAmt}";
```

---

### Complete Invoice with All Options

```php
$invoice = $qbo->create_invoice([
    // Required
    'customer_id' => '123',

    // Dates
    'txn_date' => '2025-01-15',        // Invoice date (default: today)
    'due_date' => '2025-02-15',        // Due date (optional, can use sales_term_ref instead)

    // Payment Terms
    'sales_term_ref' => '3',           // Payment terms ID (e.g., Net 30)

    // Memos/Notes
    'customer_memo' => 'Thank you for your business!',  // Visible to customer
    'private_note' => 'Internal note about this invoice',  // Internal only

    // Deposit Account
    'deposit_to_account_ref' => '35',  // Bank account ID for deposits

    // Line Items (at least one required)
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 10,
            'unit_price' => 25.00,
            'description' => 'Premium Cannabis Flower - 1oz',
            'tax_code_ref' => 'NON'  // Tax code (optional)
        ],
        [
            'item_id' => '457',
            'quantity' => 5,
            'unit_price' => 15.00,
            'description' => 'Cannabis Pre-Rolls'
        ]
    ]
]);
```

**Result:**
```php
Invoice {
    Id: "789"
    DocNumber: "1001"
    TotalAmt: 325.00
    Balance: 325.00
    CustomerRef: { value: "123", name: "Customer Name" }
    Line: [
        { Amount: 250.00, Description: "Premium Cannabis Flower - 1oz" },
        { Amount: 75.00, Description: "Cannabis Pre-Rolls" }
    ]
    TxnDate: "2025-01-15"
    DueDate: "2025-02-15"
}
```

---

### Line Item Details

**Line Item Structure:**
```php
[
    'item_id' => '456',           // QuickBooks item ID (required)
    'quantity' => 10,             // Quantity (required)
    'unit_price' => 25.00,        // Unit price (required)
    'description' => 'Text',      // Description (optional, uses item description if omitted)
    'tax_code_ref' => 'NON'      // Tax code (optional)
]
```

**How QuickBooks Processes Line Items:**
1. Looks up Item by `item_id`
2. Uses `quantity` × `unit_price` to calculate Amount
3. Uses provided `description` or falls back to item's default description
4. Auto-assigns LineNum (1, 2, 3, ...)
5. Links to Item's income account
6. Applies tax code if provided

**Multiple Line Items:**
```php
'line_items' => [
    ['item_id' => '456', 'quantity' => 10, 'unit_price' => 25.00],
    ['item_id' => '457', 'quantity' => 5, 'unit_price' => 15.00],
    ['item_id' => '458', 'quantity' => 2, 'unit_price' => 50.00],
]
// Total: (10×25) + (5×15) + (2×50) = $425.00
```

---

### Payment Terms

**Common Payment Terms:**
- Net 15: Due in 15 days
- Net 30: Due in 30 days
- Net 60: Due in 60 days
- Due on Receipt: Due immediately

**Get Available Terms:**
```php
$terms = $qbo->get_terms();
foreach ($terms as $term) {
    echo "ID: {$term->Id}, Name: {$term->Name}, Days: {$term->DueDays}\n";
}
```

**Use in Invoice:**
```php
$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'sales_term_ref' => '3',  // Net 30
    'line_items' => [/* ... */]
]);
// QuickBooks automatically calculates due_date = txn_date + 30 days
```

---

## Updating Invoices

### Update Invoice

**Method:** `update_invoice(array $data)`

**Important:** Must include invoice `id` and **all** line items

```php
// First, get the current invoice
$invoice = $qbo->get_invoice('789');

// Update with new data
$updated = $qbo->update_invoice([
    'id' => '789',
    'customer_memo' => 'Updated memo',

    // MUST include ALL line items (QuickBooks replaces them entirely)
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 15,  // Changed from 10
            'unit_price' => 25.00,
            'description' => 'Premium Cannabis Flower - 1oz'
        ],
        [
            'item_id' => '457',
            'quantity' => 5,
            'unit_price' => 15.00,
            'description' => 'Cannabis Pre-Rolls'
        ],
        // Adding new line item
        [
            'item_id' => '460',
            'quantity' => 3,
            'unit_price' => 10.00,
            'description' => 'Cannabis Edibles'
        ]
    ]
]);

echo "Invoice updated. New total: \${$updated->TotalAmt}";
```

**What Gets Updated:**
- ✅ Customer memo
- ✅ Private note
- ✅ Line items (replaced entirely)
- ✅ Dates (txn_date, due_date)
- ✅ Payment terms

**Important Notes:**
- **SyncToken** is automatically fetched and included
- **Must provide ALL line items**, not just changed ones
- QuickBooks replaces line items entirely (no partial updates)
- Cannot update if invoice has been paid

---

### Common Update Scenarios

**1. Change Invoice Date:**
```php
$qbo->update_invoice([
    'id' => '789',
    'txn_date' => '2025-01-20',
    'line_items' => $existingLineItems  // Must include
]);
```

**2. Add Line Item:**
```php
// Get existing line items
$invoice = $qbo->get_invoice('789');
$existingLines = /* convert $invoice->Line to array format */;

// Add new line
$existingLines[] = [
    'item_id' => '999',
    'quantity' => 1,
    'unit_price' => 100.00
];

// Update with all lines
$qbo->update_invoice([
    'id' => '789',
    'line_items' => $existingLines
]);
```

**3. Remove Line Item:**
```php
// Get existing, filter out one
$invoice = $qbo->get_invoice('789');
$lines = /* convert and filter */;

// Update with remaining lines
$qbo->update_invoice([
    'id' => '789',
    'line_items' => $lines
]);
```

---

## Sending Invoices

### Email Invoice to Customer

**Method:** `send_invoice(string $id, string $email)`

```php
$sent = $qbo->send_invoice('789', 'customer@example.com');

if ($sent) {
    echo "Invoice sent successfully";
} else {
    echo "Failed to send invoice";
}
```

**What Happens:**
1. QuickBooks generates PDF
2. QuickBooks sends email using their templates
3. Email comes from QuickBooks, not your server
4. QuickBooks tracks delivery status

**Email Contents:**
- Subject: Invoice from [Your Company]
- Body: QuickBooks default template
- Attachment: Invoice PDF
- Payment link (if QuickBooks Payments enabled)

**Customer Email Source:**
- Uses email passed to `send_invoice()`
- Can differ from customer's primary email in QuickBooks

**Checking if Sent:**
```php
$invoice = $qbo->get_invoice('789');
if ($invoice->EmailStatus === 'EmailSent') {
    echo "Invoice has been emailed";
}
```

---

## Downloading Invoice PDFs

### Get Invoice as PDF

**Method:** `download_invoice_pdf(string $id)`

```php
$pdfContent = $qbo->download_invoice_pdf('789');

// Save to file
file_put_contents(storage_path('invoices/invoice-789.pdf'), $pdfContent);

// Or return as download response
return response($pdfContent, 200, [
    'Content-Type' => 'application/pdf',
    'Content-Disposition' => 'attachment; filename="invoice-' . $invoice->DocNumber . '.pdf"'
]);
```

**Use Cases:**
- Download for record keeping
- Email from your own server
- Attach to other documents
- Print locally

**PDF Contains:**
- Company logo and info
- Customer billing address
- Line items with descriptions and amounts
- Totals, taxes, balance due
- Payment terms and due date

---

## Querying Invoices

### Get All Invoices (Paginated)

```php
$invoices = $qbo->get_invoices(1, 50);  // Page 1, 50 per page

foreach ($invoices as $invoice) {
    echo "#{$invoice->DocNumber} - {$invoice->CustomerRef->name} - \${$invoice->TotalAmt}\n";
}
```

### Get All Invoices (Auto-Paginated)

```php
$allInvoices = $qbo->get_all_invoices();
echo "Total invoices: " . count($allInvoices);
```

### Get Single Invoice

```php
$invoice = $qbo->get_invoice('789');

if ($invoice) {
    echo "Invoice #{$invoice->DocNumber}\n";
    echo "Customer: {$invoice->CustomerRef->name}\n";
    echo "Date: {$invoice->TxnDate}\n";
    echo "Due: {$invoice->DueDate}\n";
    echo "Total: \${$invoice->TotalAmt}\n";
    echo "Balance: \${$invoice->Balance}\n";

    // Line items
    foreach ($invoice->Line as $line) {
        if ($line->DetailType === 'SalesItemLineDetail') {
            echo "  - {$line->Description}: \${$line->Amount}\n";
        }
    }
}
```

### Get Customer's Invoices

```php
$customerInvoices = $qbo->get_customer_invoices('123');

echo "Invoices for customer:\n";
foreach ($customerInvoices as $invoice) {
    echo "  #{$invoice->DocNumber} - \${$invoice->Balance} due\n";
}
```

### Get Invoice Count

```php
$count = $qbo->get_invoice_count();
echo "Total invoices in QuickBooks: {$count}";
```

---

## Invoice Validation

### Required Field Validation

QuickBooks validates:
- ✅ Customer must exist
- ✅ At least one line item required
- ✅ Item IDs must be valid
- ✅ Amounts must be positive
- ✅ Dates must be valid format

**Example Validation in Controller:**
```php
public function createInvoice(Request $request)
{
    $validated = $request->validate([
        'customer_id' => 'required|string',
        'txn_date' => 'nullable|date',
        'line_items' => 'required|array|min:1',
        'line_items.*.item_id' => 'required|string',
        'line_items.*.quantity' => 'required|numeric|min:0.01',
        'line_items.*.unit_price' => 'required|numeric|min:0',
    ]);

    $qbo = new QuickBooksApi();
    $qbo->set_user(auth()->user());

    try {
        $invoice = $qbo->create_invoice($validated);
        return response()->json($invoice);
    } catch (\Exception $e) {
        return response()->json(['error' => $e->getMessage()], 400);
    }
}
```

---

## Common Patterns

### Pattern 1: Create Invoice from Order

```php
// From LeafLink order or internal order
$order = Order::find($orderId);

$invoice = $qbo->create_invoice([
    'customer_id' => $order->qbo_customer_id,
    'txn_date' => $order->order_date,
    'due_date' => $order->due_date,
    'customer_memo' => "Order #{$order->id}",
    'private_note' => "Internal order ID: {$order->id}",
    'line_items' => $order->items->map(fn($item) => [
        'item_id' => $item->qbo_item_id,
        'quantity' => $item->quantity,
        'unit_price' => $item->unit_price,
        'description' => $item->description
    ])->toArray()
]);

// Save QuickBooks invoice ID to order
$order->update(['qbo_invoice_id' => $invoice->Id]);
```

---

### Pattern 2: Batch Create Invoices

```php
$orders = Order::where('qbo_invoice_id', null)
    ->where('status', 'ready_to_invoice')
    ->get();

foreach ($orders as $order) {
    try {
        $invoice = $qbo->create_invoice([
            'customer_id' => $order->qbo_customer_id,
            'line_items' => /* ... */
        ]);

        $order->update(['qbo_invoice_id' => $invoice->Id]);

        LogService::store(
            'Invoice Created',
            "Order #{$order->id} → QBO Invoice #{$invoice->DocNumber}"
        );
    } catch (\Exception $e) {
        LogService::store(
            'Invoice Creation Failed',
            "Order #{$order->id}: {$e->getMessage()}"
        );
    }
}
```

---

### Pattern 3: Invoice with Auto-Send

```php
// Create invoice
$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'line_items' => [/* ... */]
]);

// Immediately send to customer
$sent = $qbo->send_invoice($invoice->Id, $customer->email);

if ($sent) {
    LogService::store('Invoice Sent', "Invoice #{$invoice->DocNumber} emailed to {$customer->email}");
}
```

---

## Troubleshooting

### Error: "Invalid Customer Reference"

**Cause:** Customer ID doesn't exist in QuickBooks

**Solution:**
```php
// Verify customer exists first
$customer = $qbo->get_customer($customerId);
if (!$customer) {
    throw new \Exception("Customer not found in QuickBooks");
}
```

---

### Error: "Invalid Item Reference"

**Cause:** Item ID doesn't exist or is inactive

**Solution:**
```php
// Verify all items exist and are active
$items = $qbo->get_items_cached();
$itemIds = collect($items)->pluck('Id')->toArray();

foreach ($lineItems as $line) {
    if (!in_array($line['item_id'], $itemIds)) {
        throw new \Exception("Item {$line['item_id']} not found");
    }
}
```

---

### Error: "Stale object error / SyncToken mismatch"

**Cause:** Invoice was modified elsewhere, SyncToken is outdated

**Solution:**
```php
// Always fetch latest before updating
$invoice = $qbo->get_invoice($invoiceId);
// Now invoice has current SyncToken

$updated = $qbo->update_invoice([
    'id' => $invoiceId,
    'line_items' => /* ... */
]);
```

**Note:** `update_invoice()` method already does this internally

---

### Error: "Cannot modify paid invoice"

**Cause:** Trying to update invoice that has been paid

**Solution:**
```php
// Check balance before updating
$invoice = $qbo->get_invoice($invoiceId);

if ($invoice->Balance < $invoice->TotalAmt) {
    throw new \Exception("Cannot modify invoice with payments applied");
}
```

---

### Invoice Not Showing in QuickBooks

**Possible Causes:**
1. Created in wrong company (check realm_id)
2. Filtered out in QuickBooks UI
3. Marked as deleted

**Check:**
```php
// Verify invoice exists
$invoice = $qbo->get_invoice($invoiceId);
if ($invoice) {
    echo "Invoice exists in QBO\n";
    echo "Status: " . ($invoice->Balance > 0 ? 'Unpaid' : 'Paid') . "\n";
}
```

---

## Frontend Integration

### CreateInvoiceModal Component

**Location:** `resources/js/Pages/Quickbooks/Modals/CreateInvoiceModal.tsx`

**Features:**
- Customer selection dropdown
- Dynamic line item rows (add/remove)
- Item selection per line
- Quantity and price inputs
- Date pickers for invoice date and due date
- Payment terms dropdown
- Memo fields
- Real-time total calculation

**Usage:**
```tsx
<CreateInvoiceModal
    isOpen={showModal}
    onClose={() => setShowModal(false)}
    customers={customers}
    items={items}
    paymentTerms={terms}
/>
```

---

## Next Steps

- **[PAYMENT_WORKFLOW.md](PAYMENT_WORKFLOW.md)** - Record payments against invoices
- **[CREDIT_MEMO_WORKFLOW.md](CREDIT_MEMO_WORKFLOW.md)** - Issue refunds and credits
- **[OPERATIONS_CATALOG.md](../OPERATIONS_CATALOG.md)** - All available operations
