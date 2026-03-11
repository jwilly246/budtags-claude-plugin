# Customer Sync Workflow

Sync customers between BudTags organizations and Unleashed.

---

## Goal
Bidirectional customer sync: import Unleashed customers into BudTags and push BudTags customer changes back to Unleashed.

## Prerequisites
- Unleashed API credentials configured
- Customer code mapping strategy (match by code or name)

## Complexity
Medium - full-object-update requirement makes updates delicate

---

## Workflow Overview

```
1. Fetch customers from Unleashed (incremental)
2. Match to local BudTags customers
3. Create/update local records
4. Push changes back (GET -> Modify -> PUT pattern)
```

---

## Step 1: Import Customers

```php
public function import_customers(): void
{
    $org = request()->user()->active_org->model()->get();
    $last_sync = $org->unleashed_customer_sync ?? now()->subDays(90);

    $page = 1;
    $all_customers = [];

    do {
        $response = $this->api->get('/Customers', [
            'modifiedSince' => $last_sync->format('Y-m-d'),
            'includeObsolete' => 'false',
            'pageSize' => 200,
            'pageNumber' => $page,
        ]);

        $data = $response->json();
        $all_customers = array_merge($all_customers, $data['Items']);
        $total_pages = $data['Pagination']['NumberOfPages'];
        $page++;
    } while ($page <= $total_pages);

    foreach ($all_customers as $customer) {
        UnleashedCustomer::updateOrCreate(
            [
                'organization_id' => $org->id,
                'unleashed_guid' => $customer['Guid'],
            ],
            [
                'customer_code' => $customer['CustomerCode'],
                'customer_name' => $customer['CustomerName'],
                'email' => $customer['Email'] ?? null,
                'phone' => $customer['PhoneNumber'] ?? null,
                'credit_limit' => $customer['CreditLimit'] ?? null,
                'payment_term' => $customer['PaymentTerm'] ?? null,
                'raw_data' => $customer,
            ]
        );
    }

    $org->update(['unleashed_customer_sync' => now()]);

    LogService::store(
        type: 'unleashed_customer_import',
        message: "Imported " . count($all_customers) . " customers from Unleashed",
    );
}
```

---

## Step 2: Push Customer Update (Safe Pattern)

CRITICAL: Always GET before updating. See `patterns/full-object-updates.md`.

```php
public function update_unleashed_customer(string $guid, array $changes): array
{
    // 1. GET the complete current customer
    $response = $this->api->get("/Customers/{$guid}");
    $customer = $response->json();

    // 2. Merge changes into the complete object
    $customer = array_merge($customer, $changes);

    // 3. POST the complete object back (Customers use POST, not PUT)
    $response = $this->api->post("/Customers/{$guid}", $customer);

    return $response->json();
}
```

---

## Step 3: Create New Customer in Unleashed

```php
public function push_customer(Customer $local_customer): array
{
    $response = $this->api->post('/Customers', [
        'CustomerCode' => $local_customer->code,
        'CustomerName' => $local_customer->name,
        'ContactFirstName' => $local_customer->contact_first_name,
        'ContactLastName' => $local_customer->contact_last_name,
        'Email' => $local_customer->email,
        'PhoneNumber' => $local_customer->phone,
        'Currency' => ['CurrencyCode' => 'USD'],
    ]);

    $result = $response->json();

    // Store the GUID mapping
    UnleashedCustomer::create([
        'organization_id' => $local_customer->organization_id,
        'unleashed_guid' => $result['Guid'],
        'customer_code' => $result['CustomerCode'],
        'customer_name' => $result['CustomerName'],
        'local_customer_id' => $local_customer->id,
    ]);

    return $result;
}
```

---

## Common Issues

### 1. CustomerCode Already Exists
**Problem**: Trying to create a customer with an existing code
**Solution**: Check existence first with `GET /Customers?customerCode=CODE`

### 2. Data Loss on Update
**Problem**: Sending partial update blanks other fields
**Solution**: ALWAYS use the GET -> Modify -> POST pattern

### 3. Primary Contact Updates
**Problem**: Contact details not updating
**Solution**: Must include `ContactFirstName`, `ContactLastName`, and/or `Email` in the request

---

## Related Resources

- `categories/customers.md` - Customer endpoint details
- `patterns/full-object-updates.md` - CRITICAL for updates
- `patterns/pagination.md` - Iteration patterns
