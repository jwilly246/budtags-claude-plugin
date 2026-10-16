# LeafLink Customer Workflow

Guide for managing customer records, licences, statuses, contacts and CRM activity.

Field and filter names come from the official spec. Write behaviour is tagged "verified 2026-10-16 (sandbox, <file>)"; raw files are in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/`. `patterns/verified-behavior.md` wins on any conflict.

## Overview

This workflow covers:
- Managing customer profiles
- Looking customers up by licence
- Organizing customers by status and tier
- Managing contacts
- Logging customer activities

---

## Step 1: Fetch Customers

### Get All Customers

```php
use App\Services\Api\LeafLinkApi;

$api = new LeafLinkApi();

// ordering=id gives a stable offset walk (honoured on /customers/ - r3_a_param_sweep.txt)
$response = $api->get('/customers/', [
    'limit' => 100,
    'offset' => 0,
    'ordering' => 'id',
]);

$customers = $response->json('results');
$totalCount = $response->json('count');

foreach ($customers as $customer) {
    echo "{$customer['name']}\n";
    echo "Licence: {$customer['license_number']}\n";
    echo "City: {$customer['city']}, {$customer['state']}\n";
    echo "---\n";
}
```

### Get Customer by ID

```php
$response = $api->get_customer_by_id($customerId);

if ($response->successful()) {
    $customer = $response->json();

    echo "Customer: {$customer['name']}\n";
    echo "Status id: {$customer['status']}\n";
    echo "Tier id: {$customer['tier']}\n";
    echo "Archived: " . ($customer['archived'] ? 'yes' : 'no') . "\n";
}
```

### Get Multiple Customers

```php
// id__in honoured - verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)
$response = $api->get('/customers/', [
    'id__in' => '123,456,789',
    'fields_include' => 'id,name,license_number,city,state',
]);
```

---

## Step 2: Filter Customers

### Find by Licence

```php
// license_number is exact AND case-sensitive; one licence per call.
// license_number__in / __iexact / __icontains are IGNORED and return the whole list.
// verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)
foreach ($licences as $licence) {
    $match = $api->get('/customers/', ['license_number' => $licence])->json('results');
}
```

### Filter by Status, Tier, State

```php
// status, tier, state take ids (comma lists allowed per the spec)
$response = $api->get('/customers/', [
    'status' => $statusId,
    'tier' => $tierId,
    'archived' => 'false',
    'limit' => 100,
]);
```

### Filter by Name

```php
// name is EXACT match only (a partial name returned 0 rows) - r3_a_param_sweep.txt
// For a prefix use name__startswith (spec; not sandbox-tested).
$response = $api->get('/customers/', ['name' => 'Green Valley Dispensary']);
```

### Filter by Date Range

```php
// Created in the last 30 days (created_on, not created_date)
$response = $api->get('/customers/', [
    'created_on__gte' => now()->subDays(30)->utc()->format('Y-m-d\TH:i:s\Z'),
    'limit' => 100,
]);

// Changed since a checkpoint (honoured - r3_a_param_sweep.txt)
$response = $api->get('/customers/', ['modified__gte' => '2026-10-16T15:00:00Z']);
```

### Common Customer Filters (spec)

| Filter | Example | Description |
|--------|---------|-------------|
| `id__in` | `'123,456'` | Several ids (verified honoured) |
| `name` | `'Green Valley'` | Exact name (verified exact only) |
| `name__startswith` | `'Green'` | Name prefix |
| `license_number` | `'AU-R-000171'` | Exact, case-sensitive (verified) |
| `status` | `5` | Customer status id(s) |
| `tier` | `3` | Customer tier id(s) |
| `state` | `'MI'` | State |
| `archived` | `'false'` | Archived flag |
| `created_on__gte` | `'2026-01-01T00:00:00Z'` | Created after |
| `modified__gte` | `'2026-10-16T00:00:00Z'` | Modified after (verified honoured) |
| `include_children` | `'contacts,managers'` | Nested children (verified honoured) |

There is no `created_date__*`, `name__icontains`, `email__icontains`, `city`, `zip_code`, `license_types__in`, `license_number__icontains`, `customer_status` or `customer_tier` filter.

---

## Step 3: Create and Update Customers

### Create New Customer

```php
// Required: owner, name (spec CustomerCreate)
$response = $api->post('/customers/', [
    'owner' => $companyId,
    'name' => 'Green Valley Dispensary',
    'email' => 'orders@greenvalley.com',
    'phone' => '(313) 555-0101',          // customer phone accepts formatting (r2_t14_customer_create.txt)
    'license_number' => 'AU-R-000171',
    'corporate_address' => ['address' => '100 Corporate Ave', 'city' => 'Detroit', 'state' => 'MI', 'zipcode' => '48201'],
    'delivery_address' => ['address' => '200 Delivery St', 'city' => 'Ann Arbor', 'state' => 'MI', 'zipcode' => '48104'],
    'status' => $statusId,   // optional
    'tier' => $tierId,       // optional
]);

if ($response->successful()) {
    $customer = $response->json();

    LogService::store(
        'LeafLink Customer Created',
        "Customer: {$customer['name']}\nID: {$customer['id']}"
    );
}
```

Do not send `ein`: it is "DEPRECATED for writes" (spec, release 2.36.0) and a PATCH of it is ignored (g_customers.txt step 6).

### Update Customer Information

```php
// Partial PATCH: only sent keys change - verified 2026-10-16 (sandbox, g_customers.txt step 1)
$response = $api->patch("/customers/{$customerId}/", [
    'email' => 'newemail@greenvalley.com',
    'tier' => $tierId,
]);
```

**Address rules** (verified 2026-10-16 (sandbox, g_customers.txt)):
- Top-level `address` / `city` / `zipcode` overwrite BOTH `corporate_address` and `delivery_address` (step 2).
- A nested `delivery_address` or `corporate_address` changes only that address (steps 8, 9).
- A partial nested object replaces the whole address: `{"corporate_address": {"city": "Warren"}}` blanked address, state and zipcode (step 10). Always send the full nested object.

**Archive rules** (g_customers.txt steps 3-5): `archived: true` archives, `archived: false` un-archives, other edits still work while archived. Only send `archived` when the user changed it. `DELETE /customers/{id}/` also archives (spec).

---

## Step 4: Manage Customer Statuses

### List Customer Statuses

```php
$statuses = $api->get('/customer-statuses/', ['limit' => 50])->json('results');

foreach ($statuses as $status) {
    echo "ID: {$status['id']}\n";
    echo "Label: {$status['state']}\n";        // the status name is `state`
    echo "Description: {$status['description']}\n";
    echo "---\n";
}
```

### Create Custom Status

```php
// Required: state, owner (spec CompanyCustomerStatus)
$response = $api->post('/customer-statuses/', [
    'state' => 'VIP',
    'owner' => $companyId,
    'description' => 'VIP customers with priority service',
    'hex_color' => '#FFD700',
]);
```

### Update Customer Status

```php
$response = $api->patch("/customer-statuses/{$statusId}/", [
    'state' => 'Premium VIP',
]);
```

### Assign Status to Customer

```php
$response = $api->patch("/customers/{$customerId}/", [
    'status' => $statusId,
]);
```

---

## Step 5: Customer Tiers (read-only)

The spec only has `GET /customer-tiers/` and `GET /customer-tiers/{id}/`. Tiers cannot be created or edited through the API. Tier fields: `id`, `rank`, `sort`.

```php
$tiers = $api->get('/customer-tiers/', ['limit' => 50])->json('results');

foreach ($tiers as $tier) {
    echo "{$tier['id']}: {$tier['rank']}\n";
}

// Customers in a tier
$goldCustomers = $api->get('/customers/', ['tier' => $goldTierId, 'archived' => 'false'])->json('results');
```

---

## Step 6: Manage Contacts

Contact fields (spec): `owner`, `first_name`, `last_name`, `email`, `secondary_email`, `role`, `description`, `phone`, `phone_extension`, `secondary_phone`, `secondary_phone_extension`, `delete`. There is no `customer`, `title` or `is_primary`.

### List a Customer's Contacts

```php
// Contacts come nested on the customer - include_children=contacts (honoured, r3_a_param_sweep.txt)
$customer = $api->get('/customers/', [
    'id' => $customerId,
    'include_children' => 'contacts',
])->json('results.0');

foreach ($customer['contacts'] ?? [] as $contact) {
    echo "{$contact['first_name']} {$contact['last_name']} - {$contact['email']}\n";
}
```

### List All Live Contacts

```php
// The default list INCLUDES deleted contacts - always send delete=false.
// verified 2026-10-16 (sandbox, r2_t8_contacts.txt)
$contacts = $api->get('/contacts/', ['delete' => 'false', 'limit' => 100])->json('results');
```

### Add New Contact

```php
// Required: owner, first_name. Names max 30 chars. Phone = 10 bare digits.
// verified 2026-10-16 (sandbox, r2_t12_contact_patch.txt)
$response = $api->post('/contacts/', [
    'owner' => $companyId,
    'first_name' => 'John',
    'last_name' => 'Doe',
    'email' => 'john@greenvalley.com',
    'phone' => preg_replace('/\D/', '', '(313) 555-0100'),   // "3135550100"
    'role' => 'Purchasing Manager',
]);
```

`(313) 555-0100`, `+13135550100` and `313.555.0100` all give 400 `"Phone number must consist of 10 digits."`; a 31-char `first_name` gives 400 (r2_t12_contact_patch.txt).

### Update Contact Information

```php
// Partial PATCH (r2_t12_contact_patch.txt T12.1)
$response = $api->patch("/contacts/{$contactId}/", [
    'email' => 'john.doe@newdomain.com',
    'phone' => '3135559999',
]);
```

### Delete Contact

```php
$response = $api->delete("/contacts/{$contactId}/");

// 204, but the contact is only flagged: GET still returns it with delete: true,
// and it stays in the default /contacts/ list (r2_t8_contacts.txt).
if ($response->status() === 204) {
    LogService::store('Contact Deleted', "Contact #{$contactId} flagged deleted");
}
```

---

## Step 7: Track Customer Activities

Activity entry fields (spec): `type`, `date`, `entry` (message), `owner`, `author`, `customer`, `contact`, `company`, `staff`, `brand`, `delete`.

### List Customer Activities

```php
$response = $api->get('/activity-entries/', [
    'customer' => $customerId,
    'date__gte' => now()->subDays(30)->utc()->format('Y-m-d\TH:i:s\Z'),
    'delete' => 'false',
    'limit' => 100,
]);

foreach ($response->json('results') as $activity) {
    echo "[{$activity['date']}] {$activity['entry']}\n";
}
```

### Search Activity Text

```php
// spec: `search` ("Search by entry field") or entry__startswith; there is no entry__icontains
$orderActivities = $api->get('/activity-entries/', [
    'search' => 'order',
    'limit' => 50,
])->json('results');
```

---

## Step 8: Customer Segmentation

```php
// Top tier + VIP status
$vipCustomers = $api->get('/customers/', [
    'tier' => $topTierId,
    'status' => $vipStatusId,
    'archived' => 'false',
    'limit' => 100,
])->json('results');

// New in the last 30 days
$newCustomers = $api->get('/customers/', [
    'created_on__gte' => now()->subDays(30)->utc()->format('Y-m-d\TH:i:s\Z'),
    'limit' => 100,
])->json('results');

// By state
$michigan = $api->get('/customers/', ['state' => 'MI', 'limit' => 100])->json('results');

// By licence type (license_type takes ONE license-type id)
$retailers = $api->get('/customers/', ['license_type' => $retailLicenseTypeId, 'limit' => 100])->json('results');
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
            'name__startswith' => $request->input('search'),
            'state' => $request->input('state'),
            'tier' => $request->input('tier'),
            'status' => $request->input('status'),
            'ordering' => 'id',
            'limit' => 100,
            'offset' => 0,
        ];

        // Remove null filters
        $filters = array_filter($filters, fn($value) => !is_null($value));

        $response = $api->get('/customers/', $filters);

        return Inertia::render('Leaflink/Customers', [
            'customers' => $response->json('results'),
            'totalCount' => $response->json('count'),
            'filters' => $request->only(['search', 'state', 'tier', 'status']),
        ]);
    }

    public function show(int $id)
    {
        $api = new LeafLinkApi();

        $customer = $api->get('/customers/', [
            'id' => $id,
            'include_children' => 'contacts,managers',
        ])->json('results.0');

        $activities = $api->get('/activity-entries/', [
            'customer' => $id,
            'delete' => 'false',
            'limit' => 50,
        ])->json('results');

        return Inertia::render('Leaflink/CustomerDetails', [
            'customer' => $customer,
            'contacts' => $customer['contacts'] ?? [],
            'activities' => $activities,
        ]);
    }

    public function create(Request $request)
    {
        $values = $request->validate([
            'name' => 'required|string',
            'email' => 'nullable|email',
            'phone' => 'nullable|string',
            'license_number' => 'nullable|string',
            'tier' => 'nullable|integer',
        ]);

        $api = new LeafLinkApi();
        $response = $api->post('/customers/', [
            'owner' => $request->user()->active_org->leaflink_company_id,
            ...$values,
        ]);

        if ($response->successful()) {
            $customer = $response->json();

            LogService::store(
                'LeafLink Customer Created',
                "Customer: {$customer['name']}\nID: {$customer['id']}"
            );

            return redirect("/leaflink/customers/{$customer['id']}")
                ->with('message', 'Customer created successfully');
        }

        return redirect()->back()->with('error', 'Failed to create customer');
    }
}
```

(`leaflink_company_id` is illustrative; use wherever the org stores its LeafLink company id.)

---

## Best Practices

### 1. Never Push Normal Forms Back

- Contact phones: strip to 10 digits before every push (r2_t12_contact_patch.txt).
- Addresses: send complete nested objects, never top-level `address` when the two addresses differ (g_customers.txt).
- `archived`: send only on a real archive/un-archive (g_customers.txt).
- `ein`: never send (ignored; deprecated for writes).

### 2. Audit Customer Data

```php
public function audit_customers()
{
    $api = new LeafLinkApi();

    // Max page size is 500 (r2_t9_pagination.txt)
    $customers = $api->get('/customers/', ['limit' => 500, 'ordering' => 'id'])->json('results');

    $issues = [];

    foreach ($customers as $customer) {
        if (empty($customer['email'])) {
            $issues[] = ['customer_id' => $customer['id'], 'issue' => 'Missing email'];
        }
        if (empty($customer['license_number'])) {
            $issues[] = ['customer_id' => $customer['id'], 'issue' => 'No licence number'];
        }
    }

    LogService::store('Customer Data Audit', count($issues) . " issues found");

    return $issues;
}
```

### 3. Track Customer Engagement

```php
LogService::store(
    'Customer Interaction',
    "Customer #{$customerId}: {$interactionType}\n{$notes}"
);
```

---

**See Also:**
- `categories/customers.md` - Customer endpoints, fields, filters
- `categories/crm.md` - Contacts and activity entries
- `patterns/verified-behavior.md` - Sandbox-verified write behaviour
- `scenarios/order-workflow.md` - Order management
- `patterns/error-handling.md` - Troubleshooting
