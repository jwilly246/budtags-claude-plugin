# QuickBooks Operations Catalog

Complete reference of all QuickBooks operations implemented in `app/Services/Api/QuickBooksApi.php`.

**Total Operations:** 40+
**Categories:** 8

---

## Table of Contents

1. [Authentication & Token Management](#authentication--token-management)
2. [Customer Operations](#customer-operations)
3. [Invoice Operations](#invoice-operations)
4. [Item/Product Operations](#itemproduct-operations)
5. [Credit Memo Operations](#credit-memo-operations)
6. [Payment Operations](#payment-operations)
7. [Account Operations](#account-operations)
8. [Terms Operations](#terms-operations)
9. [Utility Methods](#utility-methods)

---

## Authentication & Token Management

### 1. `oauth_begin()`

**Purpose:** Initiate OAuth 2.0 flow with QuickBooks

**Signature:**
```php
public static function oauth_begin(): string
```

**Returns:** Authorization URL (string)

**Usage:**
```php
$authUrl = QuickBooksApi::oauth_begin();
return redirect($authUrl);
```

**Notes:**
- Generates CSRF token for security
- Stores state in session
- Redirects user to QuickBooks login
- Route: `/quickbooks/login`

---

### 2. `oauth_complete(Request $request)`

**Purpose:** Complete OAuth flow and store access tokens

**Signature:**
```php
public static function oauth_complete(Request $request): void
```

**Parameters:**
- `$request` - Contains `code`, `state`, `realmId` from QuickBooks callback

**Returns:** `void` (stores tokens in database)

**Usage:**
```php
QuickBooksApi::oauth_complete($request);
// Tokens now stored in QboAccessKey model
```

**Database Storage:**
```php
QboAccessKey::create([
    'user_id' => $user->id,
    'org_id' => $user->active_org->id,
    'access_key' => $accessToken,
    'refresh_key' => $refreshToken,
    'realm_id' => $realmId,
    'expires_at' => now()->addSeconds($expiresIn)
]);
```

**Notes:**
- Validates CSRF state
- Exchanges auth code for tokens
- Stores encrypted tokens
- Organization-scoped
- Route: `/quickbooks/callback`

---

### 3. `refresh_token()`

**Purpose:** Refresh expired access token using refresh token

**Signature:**
```php
public function refresh_token(): void
```

**Returns:** `void` (updates tokens in database)

**Usage:**
```php
$qbo = new QuickBooksApi();
$qbo->set_user($user);
$qbo->refresh_token(); // Usually called automatically
```

**Auto-Refresh Logic:**
```php
// Called automatically before every API request
if ($this->access_key->expires_at < now()->addMinutes(5)) {
    $this->refresh_token();
}
```

**Notes:**
- Automatically called when token near expiration
- Updates both access and refresh tokens
- Logs refresh events via LogService
- Throws exception if refresh token expired

---

### 4. `set_user(User $user)`

**Purpose:** Configure API service for specific user/organization

**Signature:**
```php
public function set_user(User $user): void
```

**Parameters:**
- `$user` - User model with active_org relationship loaded

**Usage:**
```php
$qbo = new QuickBooksApi();
$qbo->set_user($user);
// Now ready to make API calls
```

**Sets Up:**
- Access key retrieval from database
- DataService configuration
- OAuth credentials
- Realm ID (QuickBooks company ID)
- Automatic token refresh

**Throws:**
- Exception if no QuickBooks connection exists for user

---

## Customer Operations

### 5. `get_customers(int $start_at = 1, int $max_count = 100)`

**Purpose:** Get paginated list of customers

**Signature:**
```php
public function get_customers(int $start_at = 1, int $max_count = 100): array
```

**Parameters:**
- `$start_at` - Starting position (1-indexed)
- `$max_count` - Max customers per page (default: 100, max: 1000)

**Returns:** Array of Customer objects

**Usage:**
```php
$customers = $qbo->get_customers(1, 50); // Get first 50 customers
```

**Query:**
```sql
SELECT * FROM Customer STARTPOSITION 1 MAXRESULTS 50
```

**Notes:**
- QuickBooks limits to 1000 results per query
- Use `get_all_customers()` for full list with auto-pagination

---

### 6. `get_all_customers()`

**Purpose:** Get ALL customers with automatic pagination

**Signature:**
```php
public function get_all_customers(): array
```

**Returns:** Array of all Customer objects

**Usage:**
```php
$allCustomers = $qbo->get_all_customers();
// Automatically handles pagination
```

**Implementation:**
```php
public function get_all_customers(): array {
    return $this->fetch_all('Customer');
}
```

**Notes:**
- Uses `fetch_all()` utility for auto-pagination
- Handles 1000-item-per-page limit
- May take longer for large customer lists

---

### 7. `get_customer(string $id)`

**Purpose:** Get single customer by QuickBooks ID

**Signature:**
```php
public function get_customer(string $id): ?object
```

**Parameters:**
- `$id` - QuickBooks customer ID

**Returns:** Customer object or `null` if not found

**Usage:**
```php
$customer = $qbo->get_customer('123');
if ($customer) {
    echo $customer->DisplayName;
}
```

**Query:**
```sql
SELECT * FROM Customer WHERE Id = '123'
```

---

### 8. `get_customers_by_id(array $ids)`

**Purpose:** Bulk fetch multiple customers by IDs

**Signature:**
```php
public function get_customers_by_id(array $ids): array
```

**Parameters:**
- `$ids` - Array of QuickBooks customer IDs

**Returns:** Array of Customer objects

**Usage:**
```php
$customers = $qbo->get_customers_by_id(['123', '456', '789']);
```

**Query:**
```sql
SELECT * FROM Customer WHERE Id IN ('123', '456', '789')
```

**Notes:**
- More efficient than multiple single requests
- Returns only found customers (no error for missing IDs)

---

### 9. `update_customer(array $data)`

**Purpose:** Update existing customer

**Signature:**
```php
public function update_customer(array $data): object
```

**Parameters:**
- `$data` - Array with customer data (must include `id`)

**Required Fields:**
- `id` - QuickBooks customer ID

**Optional Fields:**
- `display_name`, `company_name`, `given_name`, `family_name`
- `primary_phone`, `primary_email_address`
- `billing_address`, `shipping_address`

**Usage:**
```php
$updated = $qbo->update_customer([
    'id' => '123',
    'display_name' => 'New Name',
    'primary_email_address' => 'newemail@example.com'
]);
```

**Returns:** Updated Customer object

**Important:**
- Fetches current customer first to get SyncToken
- Updates only provided fields
- Preserves other fields

---

### 10. `make_customer()`

**Purpose:** Example/template method for creating customers

**Signature:**
```php
public function make_customer(): object
```

**Usage:**
```php
$customer = $qbo->make_customer();
```

**Notes:**
- This appears to be example/template code
- Creates a hard-coded customer for testing
- Not recommended for production use
- Better to create custom method accepting parameters

---

### 11. `get_customer_invoices(string $customer_id)`

**Purpose:** Get all invoices for a specific customer

**Signature:**
```php
public function get_customer_invoices(string $customer_id): array
```

**Parameters:**
- `$customer_id` - QuickBooks customer ID

**Returns:** Array of Invoice objects

**Usage:**
```php
$invoices = $qbo->get_customer_invoices('123');
foreach ($invoices as $invoice) {
    echo "Invoice #{$invoice->DocNumber}: \${$invoice->TotalAmt}\n";
}
```

**Query:**
```sql
SELECT * FROM Invoice WHERE CustomerRef = '123'
```

---

### 12. `get_customer_credit_memos(string $customer_id)`

**Purpose:** Get all credit memos for a specific customer

**Signature:**
```php
public function get_customer_credit_memos(string $customer_id): array
```

**Parameters:**
- `$customer_id` - QuickBooks customer ID

**Returns:** Array of CreditMemo objects

**Usage:**
```php
$credits = $qbo->get_customer_credit_memos('123');
```

**Query:**
```sql
SELECT * FROM CreditMemo WHERE CustomerRef = '123'
```

---

## Invoice Operations

### 13. `get_invoices(int $start_at = 1, int $max_count = 100)`

**Purpose:** Get paginated list of invoices

**Signature:**
```php
public function get_invoices(int $start_at = 1, int $max_count = 100): array
```

**Parameters:**
- `$start_at` - Starting position (1-indexed)
- `$max_count` - Max invoices per page (default: 100, max: 1000)

**Returns:** Array of Invoice objects

**Usage:**
```php
$invoices = $qbo->get_invoices(1, 50);
```

**Query:**
```sql
SELECT *, Line.* FROM Invoice STARTPOSITION 1 MAXRESULTS 50
```

**Notes:**
- Includes `Line.*` to get full line item details

---

### 14. `get_all_invoices()`

**Purpose:** Get ALL invoices with automatic pagination

**Signature:**
```php
public function get_all_invoices(): array
```

**Returns:** Array of all Invoice objects

**Usage:**
```php
$allInvoices = $qbo->get_all_invoices();
```

**Notes:**
- Auto-paginates through all invoices
- Includes full line item details
- May be slow for large invoice counts

---

### 15. `get_invoice(string $id)`

**Purpose:** Get single invoice by QuickBooks ID

**Signature:**
```php
public function get_invoice(string $id): ?object
```

**Parameters:**
- `$id` - QuickBooks invoice ID

**Returns:** Invoice object or `null` if not found

**Usage:**
```php
$invoice = $qbo->get_invoice('789');
if ($invoice) {
    echo "Invoice #{$invoice->DocNumber}\n";
    echo "Total: \${$invoice->TotalAmt}\n";
    echo "Balance: \${$invoice->Balance}\n";
}
```

**Query:**
```sql
SELECT *, Line.* FROM Invoice WHERE Id = '789'
```

---

### 16. `get_invoice_count()`

**Purpose:** Get total count of invoices in QuickBooks

**Signature:**
```php
public function get_invoice_count(): int
```

**Returns:** Total invoice count (integer)

**Usage:**
```php
$count = $qbo->get_invoice_count();
echo "Total invoices: {$count}";
```

**Query:**
```sql
SELECT COUNT(*) FROM Invoice
```

---

### 17. `create_invoice(array $data)`

**Purpose:** Create new invoice with line items

**Signature:**
```php
public function create_invoice(array $data): object
```

**Required Parameters:**
- `customer_id` - QuickBooks customer ID
- `line_items` - Array of line item objects

**Optional Parameters:**
- `txn_date` - Transaction date (default: today)
- `due_date` - Due date
- `sales_term_ref` - Payment terms ID
- `customer_memo` - Memo to customer
- `private_note` - Internal note
- `deposit_to_account_ref` - Deposit account ID

**Line Item Structure:**
```php
[
    'item_id' => '456',           // Required: QuickBooks item ID
    'quantity' => 10,             // Required: Quantity
    'unit_price' => 25.00,        // Required: Unit price
    'description' => 'Product',   // Optional: Description
    'tax_code_ref' => 'NON'      // Optional: Tax code
]
```

**Usage:**
```php
$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'txn_date' => '2025-01-15',
    'due_date' => '2025-02-15',
    'sales_term_ref' => '3',  // Net 30
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 10,
            'unit_price' => 25.00,
            'description' => 'Premium Cannabis Flower'
        ],
        [
            'item_id' => '457',
            'quantity' => 5,
            'unit_price' => 15.00,
            'description' => 'Cannabis Pre-Rolls'
        ]
    ],
    'customer_memo' => 'Thank you for your business!'
]);

echo "Invoice #{$invoice->DocNumber} created\n";
echo "Total: \${$invoice->TotalAmt}";
```

**Returns:** Created Invoice object

**Notes:**
- QuickBooks auto-calculates totals, taxes, etc.
- Line items auto-number (LineNum: 1, 2, 3...)
- See `WORKFLOWS/INVOICE_WORKFLOW.md` for complete guide

---

### 18. `update_invoice(array $data)`

**Purpose:** Update existing invoice

**Signature:**
```php
public function update_invoice(array $data): object
```

**Required Parameters:**
- `id` - QuickBooks invoice ID

**Optional Parameters:**
- All fields from `create_invoice()`
- Can update line items, customer, dates, etc.

**Usage:**
```php
$updated = $qbo->update_invoice([
    'id' => '789',
    'customer_memo' => 'Updated memo',
    'line_items' => [/* updated line items */]
]);
```

**Important:**
- Fetches current invoice first to get SyncToken
- **Must provide ALL line items**, not just changed ones
- QuickBooks replaces line items entirely

**Returns:** Updated Invoice object

---

### 19. `send_invoice(string $id, string $email)`

**Purpose:** Email invoice to customer via QuickBooks

**Signature:**
```php
public function send_invoice(string $id, string $email): bool
```

**Parameters:**
- `$id` - QuickBooks invoice ID
- `$email` - Recipient email address

**Returns:** `true` on success, `false` on failure

**Usage:**
```php
$sent = $qbo->send_invoice('789', 'customer@example.com');
if ($sent) {
    echo "Invoice sent successfully";
}
```

**Notes:**
- Uses QuickBooks email templates
- Email comes from QuickBooks, not your server
- QuickBooks tracks delivery status

---

### 20. `download_invoice_pdf(string $id)`

**Purpose:** Download invoice as PDF

**Signature:**
```php
public function download_invoice_pdf(string $id): string
```

**Parameters:**
- `$id` - QuickBooks invoice ID

**Returns:** PDF content (binary string)

**Usage:**
```php
$pdf = $qbo->download_invoice_pdf('789');

// Save to file
file_put_contents('invoice.pdf', $pdf);

// Or return as download
return response($pdf, 200, [
    'Content-Type' => 'application/pdf',
    'Content-Disposition' => 'attachment; filename="invoice.pdf"'
]);
```

**Endpoint:**
```
GET https://sandbox-quickbooks.api.intuit.com/v3/company/{realmId}/invoice/{id}/pdf
```

---

### 21. `get_customer_available_credits(string $customer_id)`

**Purpose:** Calculate total available credit balance for customer

**Signature:**
```php
public function get_customer_available_credits(string $customer_id): float
```

**Parameters:**
- `$customer_id` - QuickBooks customer ID

**Returns:** Total available credit amount (float)

**Usage:**
```php
$availableCredit = $qbo->get_customer_available_credits('123');
echo "Available credit: \${$availableCredit}";
```

**Calculation:**
```php
// Gets all credit memos for customer
// Sums: TotalAmt - Balance (applied amount)
$total = 0;
foreach ($creditMemos as $memo) {
    $total += ($memo->TotalAmt - $memo->Balance);
}
```

**Notes:**
- Only counts unapplied credit (Balance > 0)
- Returns 0.00 if no credits available

---

## Item/Product Operations

### 22. `get_items(int $start_at = 1, int $max_count = 100)`

**Purpose:** Get paginated list of items/products

**Signature:**
```php
public function get_items(int $start_at = 1, int $max_count = 100): array
```

**Parameters:**
- `$start_at` - Starting position (1-indexed)
- `$max_count` - Max items per page (default: 100, max: 1000)

**Returns:** Array of Item objects

**Usage:**
```php
$items = $qbo->get_items(1, 100);
foreach ($items as $item) {
    echo "{$item->Name} - Qty: {$item->QtyOnHand}\n";
}
```

**Query:**
```sql
SELECT * FROM Item WHERE Type = 'Inventory' STARTPOSITION 1 MAXRESULTS 100
```

**Notes:**
- Filters to inventory items only
- Non-inventory, service items excluded

---

### 23. `get_all_items()`

**Purpose:** Get ALL items with automatic pagination

**Signature:**
```php
public function get_all_items(): array
```

**Returns:** Array of all Item objects

**Usage:**
```php
$allItems = $qbo->get_all_items();
```

**Notes:**
- Auto-paginates through all items
- Inventory items only
- May be slow for large catalogs

---

### 24. `get_items_cached(int $ttl = 300)`

**Purpose:** Get items from cache or API

**Signature:**
```php
public function get_items_cached(int $ttl = 300): array
```

**Parameters:**
- `$ttl` - Cache time-to-live in seconds (default: 5 minutes)

**Returns:** Array of Item objects (cached)

**Usage:**
```php
// Cache for 10 minutes
$items = $qbo->get_items_cached(600);
```

**Cache Key:**
```php
"qbo_items_{$this->access_key->org_id}"
```

**Notes:**
- Use for read-heavy operations
- Clear cache after bulk updates
- Organization-scoped cache

---

### 25. `create_item(array $data)`

**Purpose:** Create new inventory item

**Signature:**
```php
public function create_item(array $data): object
```

**Required Parameters:**
- `name` - Item name
- `qty_on_hand` - Initial quantity
- `inv_start_date` - Inventory start date
- `unit_price` - Unit price
- `income_account_ref` - Income account ID
- `asset_account_ref` - Asset account ID
- `expense_account_ref` - COGS account ID

**Optional Parameters:**
- `description` - Item description
- `sku` - SKU/product code
- `track_qty_on_hand` - Track quantity (default: true)

**Usage:**
```php
$item = $qbo->create_item([
    'name' => 'Premium Cannabis Flower - 1oz',
    'description' => 'Top-shelf indoor grown',
    'sku' => 'FLOWER-001',
    'qty_on_hand' => 100,
    'unit_price' => 250.00,
    'inv_start_date' => '2025-01-01',
    'income_account_ref' => '79',  // Sales account
    'asset_account_ref' => '81',   // Inventory asset
    'expense_account_ref' => '80'  // COGS
]);

echo "Item created: {$item->Name} (ID: {$item->Id})";
```

**Returns:** Created Item object

**Notes:**
- Type automatically set to 'Inventory'
- TrackQtyOnHand automatically true

---

### 26. `delete_item(string $id)`

**Purpose:** Soft delete item (mark as inactive)

**Signature:**
```php
public function delete_item(string $id): object
```

**Parameters:**
- `$id` - QuickBooks item ID

**Returns:** Updated Item object (with `Active = false`)

**Usage:**
```php
$deleted = $qbo->delete_item('456');
echo "Item deactivated";
```

**Implementation:**
```php
// Fetches item, sets Active = false, updates
$item = $this->service->FindById('Item', $id);
$item->Active = false;
return $this->service->Update($item);
```

**Notes:**
- Does NOT permanently delete
- Item becomes inactive (hidden from lists)
- Can be reactivated in QuickBooks

---

### 27. `update_item_quantity(string $id, float $new_qty)`

**Purpose:** Update item quantity on hand

**Signature:**
```php
public function update_item_quantity(string $id, float $new_qty): object
```

**Parameters:**
- `$id` - QuickBooks item ID
- `$new_qty` - New quantity on hand

**Returns:** Updated Item object

**Usage:**
```php
$updated = $qbo->update_item_quantity('456', 150.00);
echo "New quantity: {$updated->QtyOnHand}";
```

**Notes:**
- Sets absolute quantity (not increment/decrement)
- QuickBooks auto-adjusts inventory value
- Used by Metrc sync workflow

---

### 28. `sync_quantities_from_metrc()`

**Purpose:** Sync inventory quantities from Metrc to QuickBooks

**Signature:**
```php
public function sync_quantities_from_metrc(): array
```

**Returns:** Sync result array
```php
[
    'synced' => 15,   // Successfully synced
    'failed' => 0,    // Failed to sync
    'skipped' => 3    // No mapping found
]
```

**Usage:**
```php
$result = $qbo->sync_quantities_from_metrc();
echo "Synced: {$result['synced']}, Failed: {$result['failed']}, Skipped: {$result['skipped']}";
```

**Process:**
1. Get all Metrc packages for organization
2. Group by ItemName, sum Quantity
3. Look up QboItemMapping for each Metrc item
4. Update QuickBooks item quantity
5. Log results to QboSyncLog

**See:** `WORKFLOWS/METRC_SYNC_WORKFLOW.md` for complete details

---

## Credit Memo Operations

### 29. `get_credit_memos(int $start_at = 1, int $max_count = 100)`

**Purpose:** Get paginated list of credit memos

**Signature:**
```php
public function get_credit_memos(int $start_at = 1, int $max_count = 100): array
```

**Parameters:**
- `$start_at` - Starting position
- `$max_count` - Max results per page

**Returns:** Array of CreditMemo objects

**Usage:**
```php
$credits = $qbo->get_credit_memos(1, 50);
```

**Query:**
```sql
SELECT *, Line.* FROM CreditMemo STARTPOSITION 1 MAXRESULTS 50
```

---

### 30. `create_credit_memo(array $data)`

**Purpose:** Create new credit memo

**Signature:**
```php
public function create_credit_memo(array $data): object
```

**Required Parameters:**
- `customer_id` - QuickBooks customer ID
- `line_items` - Array of line items

**Optional Parameters:**
- `txn_date` - Transaction date (default: today)
- `private_note` - Internal note
- `customer_memo` - Memo to customer

**Line Item Structure:** (same as invoices)
```php
[
    'item_id' => '456',
    'quantity' => 2,
    'unit_price' => 25.00,
    'description' => 'Return - damaged product'
]
```

**Usage:**
```php
$creditMemo = $qbo->create_credit_memo([
    'customer_id' => '123',
    'txn_date' => '2025-01-15',
    'customer_memo' => 'Refund for damaged items',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 2,
            'unit_price' => 25.00,
            'description' => 'Damaged product return'
        ]
    ]
]);

echo "Credit memo #{$creditMemo->DocNumber} created: \${$creditMemo->TotalAmt}";
```

**Returns:** Created CreditMemo object

**See:** `WORKFLOWS/CREDIT_MEMO_WORKFLOW.md` for applying credits

---

### 31. `apply_credit_to_invoice(array $data)`

**Purpose:** Apply credit memo to specific invoice

**Signature:**
```php
public function apply_credit_to_invoice(array $data): object
```

**Required Parameters:**
- `customer_id` - QuickBooks customer ID
- `credit_memo_id` - QuickBooks credit memo ID
- `invoice_id` - QuickBooks invoice ID
- `amount` - Amount to apply

**Usage:**
```php
$payment = $qbo->apply_credit_to_invoice([
    'customer_id' => '123',
    'credit_memo_id' => '456',
    'invoice_id' => '789',
    'amount' => 50.00
]);

echo "Applied \${$payment->TotalAmt} credit to invoice";
```

**Returns:** Payment object (QuickBooks creates a payment to link the credit)

**Process:**
1. Creates a Payment object
2. Links to customer
3. Links to invoice
4. Links to credit memo
5. Sets amount

**Notes:**
- Can apply partial credits
- Can apply multiple credits to one invoice
- Updates both invoice and credit memo balances

---

## Payment Operations

### 32. `create_payment(array $data)`

**Purpose:** Record payment against invoice

**Signature:**
```php
public function create_payment(array $data): object
```

**Required Parameters:**
- `customer_id` - QuickBooks customer ID
- `invoice_id` - QuickBooks invoice ID
- `amount` - Payment amount

**Optional Parameters:**
- `txn_date` - Transaction date (default: today)
- `payment_method_id` - Payment method ID
- `deposit_to_account_id` - Deposit account ID
- `private_note` - Internal note

**Usage:**
```php
$payment = $qbo->create_payment([
    'customer_id' => '123',
    'invoice_id' => '789',
    'amount' => 250.00,
    'txn_date' => '2025-01-15',
    'payment_method_id' => '1',        // Cash
    'deposit_to_account_id' => '35',   // Checking account
    'private_note' => 'Cash payment received'
]);

echo "Payment recorded: \${$payment->TotalAmt}";
```

**Returns:** Created Payment object

**Notes:**
- Updates invoice balance automatically
- Can make partial payments
- Multiple payments allowed per invoice

**See:** `WORKFLOWS/PAYMENT_WORKFLOW.md` for complete details

---

### 33. `get_payment_methods()`

**Purpose:** Get all active payment methods

**Signature:**
```php
public function get_payment_methods(): array
```

**Returns:** Array of PaymentMethod objects

**Usage:**
```php
$methods = $qbo->get_payment_methods();
foreach ($methods as $method) {
    echo "{$method->Name} (ID: {$method->Id})\n";
}
// Output: Cash (ID: 1), Check (ID: 2), Credit Card (ID: 3), etc.
```

**Query:**
```sql
SELECT * FROM PaymentMethod WHERE Active = true
```

---

### 34. `get_payment_method(string $id)`

**Purpose:** Get single payment method by ID

**Signature:**
```php
public function get_payment_method(string $id): ?object
```

**Parameters:**
- `$id` - QuickBooks payment method ID

**Returns:** PaymentMethod object or `null`

**Usage:**
```php
$method = $qbo->get_payment_method('1');
echo $method->Name; // "Cash"
```

---

## Account Operations

### 35. `get_accounts(int $start_at = 1, int $max_count = 100)`

**Purpose:** Get paginated list of accounts (Chart of Accounts)

**Signature:**
```php
public function get_accounts(int $start_at = 1, int $max_count = 100): array
```

**Parameters:**
- `$start_at` - Starting position
- `$max_count` - Max results per page

**Returns:** Array of Account objects

**Usage:**
```php
$accounts = $qbo->get_accounts(1, 100);
foreach ($accounts as $account) {
    echo "{$account->Name} ({$account->AccountType})\n";
}
```

**Query:**
```sql
SELECT * FROM Account STARTPOSITION 1 MAXRESULTS 100
```

---

### 36. `get_all_accounts()`

**Purpose:** Get ALL accounts with automatic pagination

**Signature:**
```php
public function get_all_accounts(): array
```

**Returns:** Array of all Account objects

**Usage:**
```php
$allAccounts = $qbo->get_all_accounts();
```

---

### 37. `get_account(string $id)`

**Purpose:** Get single account by ID

**Signature:**
```php
public function get_account(string $id): ?object
```

**Parameters:**
- `$id` - QuickBooks account ID

**Returns:** Account object or `null`

**Usage:**
```php
$account = $qbo->get_account('35');
echo "{$account->Name} - {$account->AccountType}";
```

---

### 38. `get_deposit_accounts()`

**Purpose:** Get accounts suitable for deposits (bank accounts)

**Signature:**
```php
public function get_deposit_accounts(): array
```

**Returns:** Array of Account objects (type: Bank)

**Usage:**
```php
$depositAccounts = $qbo->get_deposit_accounts();
foreach ($depositAccounts as $account) {
    echo "{$account->Name} (ID: {$account->Id})\n";
}
```

**Query:**
```sql
SELECT * FROM Account WHERE AccountType = 'Bank' AND Active = true
```

**Notes:**
- Used for payment deposit destinations
- Only returns active bank accounts

---

### 39. `get_company_info()`

**Purpose:** Get QuickBooks company information

**Signature:**
```php
public function get_company_info(): object
```

**Returns:** CompanyInfo object

**Usage:**
```php
$company = $qbo->get_company_info();
echo "Company: {$company->CompanyName}\n";
echo "Industry: {$company->IndustryType}\n";
echo "Email: {$company->Email}\n";
```

**Query:**
```sql
SELECT * FROM CompanyInfo
```

**Company Object Includes:**
- CompanyName
- LegalName
- CompanyAddr (address)
- Email, WebAddr
- FiscalYearStartMonth
- Country, etc.

---

## Terms Operations

### 40. `get_terms()`

**Purpose:** Get all payment terms

**Signature:**
```php
public function get_terms(): array
```

**Returns:** Array of Term objects

**Usage:**
```php
$terms = $qbo->get_terms();
foreach ($terms as $term) {
    echo "{$term->Name} - {$term->DueDays} days\n";
}
// Output: Net 15 - 15 days, Net 30 - 30 days, Due on Receipt - 0 days
```

**Query:**
```sql
SELECT * FROM Term WHERE Active = true
```

**Notes:**
- Used when creating invoices
- Determines due date calculation

---

## Utility Methods

### 41. `clearCache()`

**Purpose:** Clear cached QuickBooks data

**Signature:**
```php
public function clearCache(): void
```

**Usage:**
```php
$qbo->clearCache();
// Now next get_items_cached() will fetch fresh data
```

**Clears:**
- Items cache
- Any other cached QuickBooks data for organization

**Cache Key Pattern:**
```php
"qbo_*_{$this->access_key->org_id}"
```

---

### 42. `fetch_from_cache_or_api()`

**Purpose:** Generic caching helper for API calls

**Signature:**
```php
protected function fetch_from_cache_or_api(
    string $cache_key,
    callable $fetch_callback,
    int $ttl = 300
): mixed
```

**Parameters:**
- `$cache_key` - Cache key
- `$fetch_callback` - Function to fetch data from API
- `$ttl` - Cache time-to-live in seconds (default: 5 minutes)

**Usage:**
```php
$data = $this->fetch_from_cache_or_api(
    "qbo_custom_data_{$this->access_key->org_id}",
    fn() => $this->service->Query('SELECT * FROM CustomEntity'),
    600 // 10 minutes
);
```

**Notes:**
- Internal utility method
- Used by `get_items_cached()`
- Can be used for custom caching needs

---

### 43. `fetch_all(string $entity)`

**Purpose:** Auto-paginate through all records of an entity

**Signature:**
```php
protected function fetch_all(string $entity): array
```

**Parameters:**
- `$entity` - QuickBooks entity name (e.g., 'Customer', 'Invoice', 'Item')

**Returns:** Array of all entity objects

**Usage:**
```php
// Used internally by get_all_customers(), get_all_invoices(), etc.
$all = $this->fetch_all('Customer');
```

**Process:**
1. Query first 1000 records
2. If 1000 returned, fetch next 1000
3. Repeat until < 1000 returned
4. Merge all results

**Query Pattern:**
```sql
SELECT * FROM {$entity} STARTPOSITION {$position} MAXRESULTS 1000
```

**Notes:**
- Handles QuickBooks 1000-item-per-query limit
- May be slow for large datasets
- Internal utility method

---

## Summary

**Total Operations:** 43 methods

**By Category:**
- Authentication & Token Management: 4 methods
- Customer Operations: 8 methods
- Invoice Operations: 9 methods
- Item/Product Operations: 7 methods
- Credit Memo Operations: 5 methods (includes `get_customer_available_credits`)
- Payment Operations: 3 methods
- Account Operations: 5 methods (includes `get_company_info`)
- Terms Operations: 1 method
- Utility Methods: 3 methods (internal helpers)

---

## Next Steps

For workflow-specific guides, see:
- **[OAUTH_FLOW.md](OAUTH_FLOW.md)** - Authentication setup
- **[WORKFLOWS/INVOICE_WORKFLOW.md](WORKFLOWS/INVOICE_WORKFLOW.md)** - Invoice management
- **[WORKFLOWS/PAYMENT_WORKFLOW.md](WORKFLOWS/PAYMENT_WORKFLOW.md)** - Payment recording
- **[WORKFLOWS/CREDIT_MEMO_WORKFLOW.md](WORKFLOWS/CREDIT_MEMO_WORKFLOW.md)** - Credit operations
- **[WORKFLOWS/METRC_SYNC_WORKFLOW.md](WORKFLOWS/METRC_SYNC_WORKFLOW.md)** - Metrc integration
