# QuickBooks Code Examples

Real code examples from the BudTags QuickBooksApi service.

---

## Authentication Examples

### Example 1: Initiate OAuth Flow

```php
use App\Services\Api\QuickBooksApi;

// In controller
public function login()
{
    $authUrl = QuickBooksApi::oauth_begin();
    return redirect($authUrl);
}
```

**What happens:**
1. Generates CSRF state token
2. Stores state in session
3. Builds QuickBooks authorization URL
4. Redirects user to QuickBooks

---

### Example 2: Complete OAuth Callback

```php
use App\Services\Api\QuickBooksApi;

public function callback(Request $request)
{
    try {
        QuickBooksApi::oauth_complete($request);

        return redirect('/quickbooks/dashboard')
            ->with('success', 'QuickBooks connected successfully!');
    } catch (\Exception $e) {
        return redirect('/quickbooks/dashboard')
            ->with('error', 'Failed to connect: ' . $e->getMessage());
    }
}
```

---

### Example 3: Set Up API Service for User

```php
use App\Services\Api\QuickBooksApi;

$qbo = new QuickBooksApi();
$qbo->set_user(auth()->user());

// Now ready to make API calls
$customers = $qbo->get_customers();
```

---

## Customer Examples

### Example 4: Get All Customers (Paginated)

```php
$qbo = new QuickBooksApi();
$qbo->set_user($user);

$customers = $qbo->get_customers(1, 50); // Page 1, 50 per page

foreach ($customers as $customer) {
    echo "{$customer->DisplayName} - Balance: \${$customer->Balance}\n";
}
```

---

### Example 5: Get All Customers (Auto-Paginated)

```php
$allCustomers = $qbo->get_all_customers();

echo "Total customers: " . count($allCustomers) . "\n";

// Find specific customer
$customer = collect($allCustomers)->firstWhere('DisplayName', 'Acme Dispensary');
```

---

### Example 6: Update Customer Email

```php
$updated = $qbo->update_customer([
    'id' => '123',
    'primary_email_address' => 'newemail@example.com'
]);

LogService::store(
    'Customer Updated',
    "Updated email for {$updated->DisplayName}"
);
```

---

## Invoice Examples

### Example 7: Create Simple Invoice

```php
$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 10,
            'unit_price' => 25.00,
            'description' => 'Premium Cannabis Flower - 1oz'
        ]
    ]
]);

echo "Invoice #{$invoice->DocNumber} created: \${$invoice->TotalAmt}";
```

---

### Example 8: Create Invoice with Multiple Line Items and Payment Terms

```php
$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'txn_date' => '2025-01-15',
    'sales_term_ref' => '3', // Net 30
    'customer_memo' => 'Thank you for your business!',
    'private_note' => 'Order #12345',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 10,
            'unit_price' => 25.00,
            'description' => 'Premium Cannabis Flower - 1oz'
        ],
        [
            'item_id' => '457',
            'quantity' => 5,
            'unit_price' => 15.00,
            'description' => 'Cannabis Pre-Rolls - 5 pack'
        ],
        [
            'item_id' => '458',
            'quantity' => 2,
            'unit_price' => 50.00,
            'description' => 'Cannabis Edibles - Gummies'
        ]
    ]
]);

LogService::store(
    'QBO Invoice Created',
    "Invoice #{$invoice->DocNumber}\nCustomer: {$invoice->CustomerRef->name}\nTotal: \${$invoice->TotalAmt}"
);
```

---

### Example 9: Send Invoice via Email

```php
$invoice = $qbo->get_invoice('789');

$sent = $qbo->send_invoice($invoice->Id, 'customer@example.com');

if ($sent) {
    LogService::store(
        'Invoice Sent',
        "Invoice #{$invoice->DocNumber} emailed to customer@example.com"
    );

    return redirect()->back()->with('success', 'Invoice sent');
} else {
    return redirect()->back()->with('error', 'Failed to send invoice');
}
```

---

### Example 10: Download Invoice PDF

```php
$pdfContent = $qbo->download_invoice_pdf('789');

// Save to storage
$filename = "invoice-{$invoice->DocNumber}.pdf";
Storage::put("invoices/{$filename}", $pdfContent);

// Or return as download
return response($pdfContent, 200, [
    'Content-Type' => 'application/pdf',
    'Content-Disposition' => "attachment; filename=\"{$filename}\""
]);
```

---

### Example 11: Create Invoice from Order

```php
// From internal order model
$order = Order::with('items')->findOrFail($orderId);

$invoice = $qbo->create_invoice([
    'customer_id' => $order->qbo_customer_id,
    'txn_date' => $order->order_date,
    'customer_memo' => "Order #{$order->id}",
    'private_note' => "Internal order ID: {$order->id}",
    'line_items' => $order->items->map(function($item) {
        return [
            'item_id' => $item->qbo_item_id,
            'quantity' => $item->quantity,
            'unit_price' => $item->unit_price,
            'description' => $item->description
        ];
    })->toArray()
]);

// Save QuickBooks invoice ID back to order
$order->update(['qbo_invoice_id' => $invoice->Id]);

LogService::store(
    'Order Invoiced',
    "Order #{$order->id} → QBO Invoice #{$invoice->DocNumber}"
);
```

---

## Payment Examples

### Example 12: Record Full Payment

```php
$invoice = $qbo->get_invoice('789');

$payment = $qbo->create_payment([
    'customer_id' => $invoice->CustomerRef->value,
    'invoice_id' => $invoice->Id,
    'amount' => $invoice->Balance,  // Pay full balance
    'txn_date' => now()->format('Y-m-d'),
    'payment_method_id' => '1',  // Cash
    'deposit_to_account_id' => '35',  // Checking
    'private_note' => 'Payment received at dispensary'
]);

LogService::store(
    'Payment Recorded',
    "Invoice #{$invoice->DocNumber} paid in full: \${$payment->TotalAmt}"
);
```

---

### Example 13: Record Partial Payment

```php
$payment = $qbo->create_payment([
    'customer_id' => '123',
    'invoice_id' => '789',
    'amount' => 100.00,  // Partial payment
    'payment_method_id' => '1'
]);

$invoice = $qbo->get_invoice('789');
echo "Remaining balance: \${$invoice->Balance}";
```

---

## Credit Memo Examples

### Example 14: Create Credit Memo for Return

```php
$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'txn_date' => '2025-01-20',
    'customer_memo' => 'Return - damaged product',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 2,
            'unit_price' => 25.00,
            'description' => 'Returned units - product defect'
        ]
    ]
]);

LogService::store(
    'Credit Memo Created',
    "Credit memo #{$creditMemo->DocNumber} for \${$creditMemo->TotalAmt}"
);
```

---

### Example 15: Apply Credit to Invoice

```php
$payment = $qbo->apply_credit_to_invoice([
    'customer_id' => '123',
    'credit_memo_id' => '456',
    'invoice_id' => '789',
    'amount' => 50.00
]);

LogService::store(
    'Credit Applied',
    "Applied \${$payment->TotalAmt} credit to Invoice"
);
```

---

### Example 16: Check Available Credits

```php
$availableCredit = $qbo->get_customer_available_credits('123');

if ($availableCredit > 0) {
    echo "Customer has \${$availableCredit} in available credits";

    // Get credit memos
    $creditMemos = $qbo->get_customer_credit_memos('123');

    foreach ($creditMemos as $memo) {
        if ($memo->Balance > 0) {
            echo "  Credit #{$memo->DocNumber}: \${$memo->Balance} available\n";
        }
    }
}
```

---

## Item Examples

### Example 17: Get Items with Caching

```php
// Cache for 10 minutes
$items = $qbo->get_items_cached(600);

foreach ($items as $item) {
    echo "{$item->Name} - Qty: {$item->QtyOnHand} - Price: \${$item->UnitPrice}\n";
}
```

---

### Example 18: Create New Item

```php
$item = $qbo->create_item([
    'name' => 'Premium Cannabis Flower - 1oz',
    'description' => 'Top-shelf indoor grown cannabis flower',
    'sku' => 'FLOWER-001',
    'qty_on_hand' => 100,
    'unit_price' => 250.00,
    'inv_start_date' => '2025-01-01',
    'income_account_ref' => '79',   // Sales income account
    'asset_account_ref' => '81',    // Inventory asset account
    'expense_account_ref' => '80'   // COGS account
]);

LogService::store(
    'QBO Item Created',
    "Item: {$item->Name} (ID: {$item->Id})"
);
```

---

### Example 19: Update Item Quantity

```php
$updatedItem = $qbo->update_item_quantity('456', 150.00);

LogService::store(
    'QBO Quantity Updated',
    "Item {$updatedItem->Name}: Qty updated to {$updatedItem->QtyOnHand}"
);
```

---

## Metrc Sync Examples

### Example 20: Sync Quantities from Metrc

```php
$qbo = new QuickBooksApi();
$qbo->set_user($user);

$result = $qbo->sync_quantities_from_metrc();

LogService::store(
    'Metrc → QBO Sync Complete',
    "Synced: {$result['synced']}, Failed: {$result['failed']}, Skipped: {$result['skipped']}"
);

if ($result['failed'] > 0) {
    foreach ($result['errors'] as $error) {
        LogService::store('QBO Sync Error', $error);
    }
}
```

---

### Example 21: Create Item Mapping

```php
use App\Models\QboItemMapping;

// Create mapping from Metrc item to QuickBooks item
QboItemMapping::create([
    'org_id' => auth()->user()->active_org->id,
    'metrc_item_id' => 'metrc-item-123',
    'metrc_item_name' => 'Premium Flower - 1oz',
    'qbo_item_id' => '456',
    'qbo_item_name' => 'Cannabis Flower 1oz'
]);

// Now sync will update this QBO item with Metrc quantities
$result = $qbo->sync_quantities_from_metrc();
```

---

## Error Handling Examples

### Example 22: Handle API Errors with Logging

```php
try {
    $invoice = $qbo->create_invoice($data);

    LogService::store(
        'QBO Invoice Created',
        "Invoice #{$invoice->DocNumber}"
    );

    return redirect()->back()->with('success', 'Invoice created');
} catch (\Exception $e) {
    LogService::store(
        'QBO Invoice Creation Failed',
        "Error: {$e->getMessage()}\nData: " . json_encode($data, JSON_PRETTY_PRINT)
    );

    return redirect()->back()->with('error', 'Failed to create invoice: ' . $e->getMessage());
}
```

---

### Example 23: Validate Before API Call

```php
// Check if customer exists
$customer = $qbo->get_customer($customerId);
if (!$customer) {
    return back()->withErrors(['customer_id' => 'Customer not found in QuickBooks']);
}

// Check if customer is active
if (!$customer->Active) {
    return back()->withErrors(['customer_id' => 'Customer is inactive in QuickBooks']);
}

// Check invoice balance before payment
$invoice = $qbo->get_invoice($invoiceId);
if ($paymentAmount > $invoice->Balance) {
    return back()->withErrors(['amount' => 'Payment exceeds invoice balance']);
}

// Now safe to proceed
$payment = $qbo->create_payment($data);
```

---

### Example 24: Handle Token Expiration

```php
try {
    $qbo = new QuickBooksApi();
    $qbo->set_user($user);
    $customers = $qbo->get_customers();
} catch (\Exception $e) {
    if (str_contains($e->getMessage(), 'Unauthorized') || str_contains($e->getMessage(), '401')) {
        // Token may be expired, try refreshing
        try {
            $qbo->refresh_token();
            $customers = $qbo->get_customers(); // Retry
        } catch (\Exception $refreshError) {
            // Refresh failed, need to re-authorize
            return redirect('/quickbooks/login')
                ->with('error', 'QuickBooks connection expired. Please reconnect.');
        }
    } else {
        throw $e;
    }
}
```

---

## Controller Examples

### Example 25: Complete Invoice Creation Controller

```php
use App\Services\Api\QuickBooksApi;
use App\Services\LogService;
use Illuminate\Http\Request;

public function createInvoice(Request $request)
{
    $validated = $request->validate([
        'customer_id' => 'required|string',
        'txn_date' => 'nullable|date',
        'due_date' => 'nullable|date',
        'sales_term_ref' => 'nullable|string',
        'customer_memo' => 'nullable|string',
        'line_items' => 'required|array|min:1',
        'line_items.*.item_id' => 'required|string',
        'line_items.*.quantity' => 'required|numeric|min:0.01',
        'line_items.*.unit_price' => 'required|numeric|min:0',
        'line_items.*.description' => 'nullable|string',
    ]);

    try {
        $qbo = new QuickBooksApi();
        $qbo->set_user(auth()->user());

        // Verify customer exists
        $customer = $qbo->get_customer($validated['customer_id']);
        if (!$customer) {
            return back()->withErrors(['customer_id' => 'Customer not found']);
        }

        $invoice = $qbo->create_invoice($validated);

        LogService::store(
            'QBO Invoice Created',
            "Invoice #{$invoice->DocNumber}\nCustomer: {$customer->DisplayName}\nTotal: \${$invoice->TotalAmt}"
        );

        return redirect('/quickbooks/invoices')->with('success', "Invoice #{$invoice->DocNumber} created");
    } catch (\Exception $e) {
        LogService::store(
            'QBO Invoice Creation Failed',
            "Customer ID: {$validated['customer_id']}\nError: {$e->getMessage()}"
        );

        return back()->with('error', 'Failed to create invoice: ' . $e->getMessage());
    }
}
```

---

### Example 26: Batch Create Invoices from Orders

```php
use App\Models\Order;
use App\Services\Api\QuickBooksApi;

public function batchCreateInvoices()
{
    $orders = Order::where('qbo_invoice_id', null)
        ->where('status', 'ready_to_invoice')
        ->get();

    $qbo = new QuickBooksApi();
    $qbo->set_user(auth()->user());

    $created = 0;
    $failed = 0;

    foreach ($orders as $order) {
        try {
            $invoice = $qbo->create_invoice([
                'customer_id' => $order->qbo_customer_id,
                'txn_date' => $order->order_date,
                'customer_memo' => "Order #{$order->id}",
                'line_items' => $order->items->map(fn($item) => [
                    'item_id' => $item->qbo_item_id,
                    'quantity' => $item->quantity,
                    'unit_price' => $item->unit_price,
                    'description' => $item->description
                ])->toArray()
            ]);

            $order->update(['qbo_invoice_id' => $invoice->Id]);

            LogService::store(
                'Invoice Created (Batch)',
                "Order #{$order->id} → Invoice #{$invoice->DocNumber}"
            );

            $created++;
        } catch (\Exception $e) {
            LogService::store(
                'Invoice Creation Failed (Batch)',
                "Order #{$order->id}: {$e->getMessage()}"
            );

            $failed++;
        }
    }

    return redirect()->back()->with('success', "Created {$created} invoices, {$failed} failed");
}
```

---

## Frontend Integration Example

### Example 27: React Component with QuickBooks Data

```typescript
import { useForm } from '@inertiajs/react';
import { Customer, Invoice } from '@/Types/types-qbo';
import { toast } from 'react-toastify';

interface Props {
    customers: Customer[];
}

const CreateInvoiceForm: React.FC<Props> = ({ customers }) => {
    const { data, setData, post, processing } = useForm({
        customer_id: '',
        line_items: [
            { item_id: '', quantity: 1, unit_price: 0, description: '' }
        ]
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        post('/quickbooks/create-invoice', {
            onSuccess: (page) => {
                const flash = (page.props as any).flash?.success;
                if (flash) toast.success(flash);
            },
            onError: (errors) => {
                const errorMessage = Object.values(errors)[0] as string;
                toast.error(errorMessage);
            }
        });
    };

    return (
        <form onSubmit={handleSubmit}>
            <select
                value={data.customer_id}
                onChange={(e) => setData('customer_id', e.target.value)}
            >
                <option value="">Select Customer</option>
                {customers.map(customer => (
                    <option key={customer.Id} value={customer.Id}>
                        {customer.DisplayName}
                    </option>
                ))}
            </select>

            {/* Line items */}

            <button type="submit" disabled={processing}>
                Create Invoice
            </button>
        </form>
    );
};
```

---

## Next Steps

- **[OPERATIONS_CATALOG.md](OPERATIONS_CATALOG.md)** - All available operations
- **[WORKFLOWS/](WORKFLOWS/)** - Step-by-step workflow guides
- **[ERROR_HANDLING.md](ERROR_HANDLING.md)** - Common errors and solutions
