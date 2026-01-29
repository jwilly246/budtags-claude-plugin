# LeafLink Customer Workflow

Guide for managing customer relationships, licenses, and CRM activities.

## Overview

This workflow covers:
- Managing customer profiles
- Tracking customer licenses
- Organizing customers by status and tier
- Managing contacts
- Logging customer activities
- CRM integration

---

## Step 1: Fetch Customers

### Get All Customers

```php
use App\Services\Api\LeafLinkApi;

$api = new LeafLinkApi();

$response = $api->get('/customers/', [
    'limit' => 100,
    'offset' => 0
]);

$customers = $response->json('results');
$totalCount = $response->json('count');

foreach ($customers as $customer) {
    echo "{$customer['name']}\n";
    echo "Email: {$customer['email']}\n";
    echo "City: {$customer['city']}, {$customer['state']}\n";
    echo "Licenses: " . count($customer['licenses']) . "\n";
    echo "---\n";
}
```

### Get Customer by ID

```php
$customerId = 123;

$response = $api->get_customer_by_id($customerId);

if ($response->successful()) {
    $customer = $response->json();

    echo "Customer: {$customer['name']}\n";
    echo "Email: {$customer['email']}\n";
    echo "Phone: {$customer['phone']}\n";
    echo "Status: {$customer['customer_status']}\n";
    echo "Tier: {$customer['customer_tier']}\n";
}
```

### Get Multiple Customers

```php
$customerIds = [123, 456, 789];
$fields = ['id', 'name', 'email', 'licenses', 'city', 'state'];

$response = $api->get_customers(
    ids: $customerIds,
    fields: $fields
);

$customers = $response->json('results');
```

---

## Step 2: Filter Customers

### Filter by License Type

```php
// Find all retail dispensaries in Colorado
$response = $api->get('/customers/', [
    'license_types__in' => 'retail',
    'state' => 'CO',
    'status' => 'active',
    'limit' => 100
]);

$retailCustomers = $response->json('results');
```

### Filter by Name and Location

```php
$response = $api->get('/customers/', [
    'name__icontains' => 'green',     // Name contains "green"
    'city' => 'Denver',
    'state' => 'CO',
    'limit' => 50
]);

$customers = $response->json('results');
```

### Filter by Date Range

```php
// Customers created in last 30 days
$response = $api->get('/customers/', [
    'created_date__gte' => now()->subDays(30)->toDateString(),
    'created_date__lte' => now()->toDateString(),
    'limit' => 100
]);

$newCustomers = $response->json('results');
```

### Available Customer Filters (87 Total!)

Common filters include:

| Filter | Example | Description |
|--------|---------|-------------|
| `name__icontains` | `'dispensary'` | Name contains (case-insensitive) |
| `email__icontains` | `'@gmail.com'` | Email contains |
| `city` | `'Denver'` | Exact city match |
| `state` | `'CO'` | State abbreviation |
| `zip_code` | `'80202'` | ZIP code |
| `license_types__in` | `'retail,cultivation'` | Multiple license types |
| `license_number__icontains` | `'C11'` | License number contains |
| `customer_status` | `5` | Customer status ID |
| `customer_tier` | `3` | Customer tier ID |
| `created_date__gte` | `'2024-01-01'` | Created after date |
| `modified__gte` | `'2025-01-01'` | Modified after date |

---

## Step 3: Create and Update Customers

### Create New Customer

```php
$response = $api->post('/customers/', [
    'name' => 'Green Valley Dispensary',
    'email' => 'orders@greenvalley.com',
    'phone' => '555-123-4567',
    'address' => '123 Main St',
    'city' => 'Denver',
    'state' => 'CO',
    'zip_code' => '80202',
    'customer_status' => 1,  // Status ID (optional)
    'customer_tier' => 2      // Tier ID (optional)
]);

if ($response->successful()) {
    $customer = $response->json();

    LogService::store(
        'LeafLink Customer Created',
        "Customer: {$customer['name']}\nEmail: {$customer['email']}"
    );
}
```

### Update Customer Information

```php
$customerId = 123;

$response = $api->patch("/customers/{$customerId}/", [
    'email' => 'newemail@greenvalley.com',
    'phone' => '555-999-8888',
    'customer_tier' => 3  // Promote to higher tier
]);

if ($response->successful()) {
    LogService::store(
        'LeafLink Customer Updated',
        "Customer #{$customerId} information updated"
    );
}
```

---

## Step 4: Manage Customer Statuses

### List Customer Statuses

```php
$response = $api->get('/customer-statuses/', [
    'limit' => 50
]);

$statuses = $response->json('results');

foreach ($statuses as $status) {
    echo "ID: {$status['id']}\n";
    echo "Name: {$status['name']}\n";
    echo "Description: {$status['description']}\n";
    echo "---\n";
}
```

### Create Custom Status

```php
$response = $api->post('/customer-statuses/', [
    'name' => 'VIP',
    'description' => 'VIP customers with priority service'
]);

if ($response->successful()) {
    $status = $response->json();

    LogService::store(
        'Customer Status Created',
        "Status: {$status['name']} (ID: {$status['id']})"
    );
}
```

### Update Customer Status

```php
$statusId = 5;

$response = $api->patch("/customer-statuses/{$statusId}/", [
    'name' => 'Premium VIP',
    'description' => 'Updated VIP tier with additional benefits'
]);
```

### Assign Status to Customer

```php
$customerId = 123;
$statusId = 5;

$response = $api->patch("/customers/{$customerId}/", [
    'customer_status' => $statusId
]);

if ($response->successful()) {
    LogService::store(
        'Customer Status Assigned',
        "Customer #{$customerId} assigned to status #{$statusId}"
    );
}
```

---

## Step 5: Manage Customer Tiers

### List Customer Tiers

```php
$response = $api->get('/customer-tiers/', [
    'limit' => 50
]);

$tiers = $response->json('results');

foreach ($tiers as $tier) {
    echo "{$tier['name']}\n";
    echo "Discount: {$tier['discount_percent']}%\n";
    echo "---\n";
}
```

### Create Tier with Discount

```php
$response = $api->post('/customer-tiers/', [
    'name' => 'Gold',
    'description' => 'Gold tier customers',
    'discount_percent' => 10.0
]);

if ($response->successful()) {
    $tier = $response->json();

    LogService::store(
        'Customer Tier Created',
        "Tier: {$tier['name']} ({$tier['discount_percent']}% discount)"
    );
}
```

### Update Tier Discount

```php
$tierId = 2;

$response = $api->patch("/customer-tiers/{$tierId}/", [
    'discount_percent' => 15.0  // Increase discount
]);
```

### Segment Customers by Tier

```php
// Get all Gold tier customers
$response = $api->get('/customers/', [
    'customer_tier' => 2,  // Gold tier ID
    'status' => 'active',
    'limit' => 100
]);

$goldCustomers = $response->json('results');

echo "Gold tier customers: " . count($goldCustomers) . "\n";
```

---

## Step 6: Manage Contacts

### List Customer Contacts

```php
$customerId = 123;

$response = $api->get('/contacts/', [
    'customer' => $customerId,
    'limit' => 50
]);

$contacts = $response->json('results');

foreach ($contacts as $contact) {
    echo "{$contact['first_name']} {$contact['last_name']}\n";
    echo "Title: {$contact['title']}\n";
    echo "Email: {$contact['email']}\n";
    echo "Phone: {$contact['phone']}\n";
    echo "Primary: " . ($contact['is_primary'] ? 'Yes' : 'No') . "\n";
    echo "---\n";
}
```

### Add New Contact

```php
$response = $api->post('/contacts/', [
    'customer' => 123,
    'first_name' => 'John',
    'last_name' => 'Doe',
    'email' => 'john@greenvalley.com',
    'phone' => '555-123-4567',
    'title' => 'Purchasing Manager',
    'is_primary' => true
]);

if ($response->successful()) {
    $contact = $response->json();

    LogService::store(
        'Contact Added',
        "Customer #{$contact['customer']}: {$contact['first_name']} {$contact['last_name']}"
    );
}
```

### Update Contact Information

```php
$contactId = 456;

$response = $api->patch("/contacts/{$contactId}/", [
    'email' => 'john.doe@newdomain.com',
    'phone' => '555-999-8888'
]);
```

### Delete Contact

```php
$contactId = 456;

$response = $api->delete("/contacts/{$contactId}/");

if ($response->status() === 204) {
    LogService::store('Contact Deleted', "Contact #{$contactId} removed");
}
```

---

## Step 7: Track Customer Activities

### List Customer Activities

```php
$customerId = 123;

$response = $api->get('/activity-entries/', [
    'customer' => $customerId,
    'date__gte' => now()->subDays(30)->toDateString(),  // Last 30 days
    'limit' => 100
]);

$activities = $response->json('results');

foreach ($activities as $activity) {
    echo "[{$activity['date']}] {$activity['entry']}\n";
}
```

### Filter Activities by Date Range

```php
$response = $api->get('/activity-entries/', [
    'customer' => 123,
    'date__gte' => '2025-01-01',
    'date__lte' => '2025-01-31',
    'limit' => 100
]);

$januaryActivities = $response->json('results');
```

### Search Activity Descriptions

```php
$response = $api->get('/activity-entries/', [
    'entry__icontains' => 'order',  // Activities mentioning "order"
    'limit' => 50
]);

$orderActivities = $response->json('results');
```

---

## Step 8: Customer Segmentation

### High-Value Customers

```php
// Find VIP customers in top tier
$response = $api->get('/customers/', [
    'customer_tier' => 3,      // Top tier
    'customer_status' => 5,    // VIP status
    'status' => 'active',
    'limit' => 100
]);

$vipCustomers = $response->json('results');
```

### New Customers (Last 30 Days)

```php
$response = $api->get('/customers/', [
    'created_date__gte' => now()->subDays(30)->toDateString(),
    'limit' => 100
]);

$newCustomers = $response->json('results');
```

### Customers by Region

```php
// Colorado customers
$response = $api->get('/customers/', [
    'state' => 'CO',
    'status' => 'active',
    'limit' => 100
]);

$coloradoCustomers = $response->json('results');
```

### License Type Segmentation

```php
// Retail dispensaries
$response = $api->get('/customers/', [
    'license_types__in' => 'retail',
    'limit' => 100
]);

$retailers = $response->json('results');

// Cultivation facilities
$response = $api->get('/customers/', [
    'license_types__in' => 'cultivation',
    'limit' => 100
]);

$cultivators = $response->json('results');
```

---

## Complete Customer Controller

```php
namespace App\Http\Controllers;

use App\Services\Api\LeafLinkApi;
use App\Services\LogService;
use Illuminate\Http\Request;
use Inertia\Inertia;

class LeafLinkCustomerController extends Controller
{
    public function index(Request $request)
    {
        $api = new LeafLinkApi();

        $filters = [
            'name__icontains' => $request->input('search'),
            'state' => $request->input('state'),
            'customer_tier' => $request->input('tier'),
            'customer_status' => $request->input('status'),
            'limit' => 100,
            'offset' => 0
        ];

        // Remove null filters
        $filters = array_filter($filters, fn($value) => !is_null($value));

        $response = $api->get('/customers/', $filters);

        return Inertia::render('Leaflink/Customers', [
            'customers' => $response->json('results'),
            'totalCount' => $response->json('count'),
            'filters' => $request->only(['search', 'state', 'tier', 'status'])
        ]);
    }

    public function show(int $id)
    {
        $api = new LeafLinkApi();

        $customer = $api->get_customer_by_id($id)->json();

        // Get customer contacts
        $contacts = $api->get('/contacts/', [
            'customer' => $id
        ])->json('results');

        // Get recent activities
        $activities = $api->get('/activity-entries/', [
            'customer' => $id,
            'date__gte' => now()->subDays(90)->toDateString(),
            'limit' => 50
        ])->json('results');

        return Inertia::render('Leaflink/CustomerDetails', [
            'customer' => $customer,
            'contacts' => $contacts,
            'activities' => $activities
        ]);
    }

    public function create(Request $request)
    {
        $values = $request->validate([
            'name' => 'required|string',
            'email' => 'required|email',
            'phone' => 'nullable|string',
            'city' => 'required|string',
            'state' => 'required|string|size:2',
            'customer_tier' => 'nullable|integer'
        ]);

        $api = new LeafLinkApi();
        $response = $api->post('/customers/', $values);

        if ($response->successful()) {
            $customer = $response->json();

            LogService::store(
                'LeafLink Customer Created',
                "Customer: {$customer['name']}\nID: {$customer['id']}"
            );

            return redirect()->route('leaflink.customers.show', $customer['id'])
                ->with('success', 'Customer created successfully');
        }

        return redirect()->back()->with('error', 'Failed to create customer');
    }
}
```

---

## Best Practices

### 1. Maintain Clean Customer Data

```php
// Regularly audit and clean customer data
public function audit_customers()
{
    $api = new LeafLinkApi();

    $response = $api->get('/customers/', ['limit' => 500]);
    $customers = $response->json('results');

    $issues = [];

    foreach ($customers as $customer) {
        // Check for missing email
        if (empty($customer['email'])) {
            $issues[] = ['customer_id' => $customer['id'], 'issue' => 'Missing email'];
        }

        // Check for missing license
        if (empty($customer['licenses'])) {
            $issues[] = ['customer_id' => $customer['id'], 'issue' => 'No license'];
        }
    }

    LogService::store('Customer Data Audit', count($issues) . " issues found");

    return $issues;
}
```

### 2. Track Customer Engagement

```php
// Log all customer interactions
LogService::store(
    'Customer Interaction',
    "Customer #{$customerId}: {$interactionType}\n{$notes}"
);
```

### 3. Segment for Marketing

```php
// Create targeted customer lists
$vipList = $this->get_vip_customers();
$newList = $this->get_new_customers();
$inactiveList = $this->get_inactive_customers();
```

---

**See Also:**
- `OPERATIONS_CATALOG.md` - Customer operations
- `ORDER_WORKFLOW.md` - Order management
- `ERROR_HANDLING.md` - Troubleshooting
