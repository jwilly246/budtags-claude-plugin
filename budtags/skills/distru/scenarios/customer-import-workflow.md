# Scenario — Customer Import Workflow

Import Distru Companies and Contacts. A single Company can be a customer, a vendor, or both — route to the appropriate Budtags table based on `relationship_type`.

## Prerequisites

- Distru API key configured.
- Decision on how Budtags handles companies that are both customers and vendors (commonly: a row in each table linked by a shared `distru_company_id`).

## Step 1 — Paginate `/companies`

```php
$page = 1;
do {
    $response = $api->get('/companies', [
        'page[number]' => $page,
        'page[size]'   => 200,
        'updated_at_from' => $importJob->last_synced_at?->toIso8601String() ?? '1970-01-01T00:00:00Z',
    ]);

    foreach ($response['data'] as $distruCompany) {
        $this->upsertCompany($distruCompany);
    }

    $page++;
} while ($response['next_page'] !== null);
```

## Step 2 — Route by relationship_type

```php
protected function upsertCompany(array $c): DistruCompany
{
    $relationshipType = strtoupper($c['relationship_type'] ?? '');

    $mapping = DistruCompany::updateOrCreate(
        [
            'organization_id' => $this->org->id,
            'distru_company_id' => $c['id'],
        ],
        [
            'name' => $c['name'],
            'dba' => $c['dba'] ?? null,
            'license_number' => $c['license_number'] ?? null,
            'license_type' => $c['license_type'] ?? null,
            'relationship_type' => $relationshipType,
            'category' => $c['category'] ?? null,
            'email' => $c['email'] ?? null,
            'phone' => $c['phone'] ?? null,
            'last_synced_at' => now(),
        ],
    );

    if (str_contains($relationshipType, 'CUSTOMER')) {
        $mapping->update(['customer_id' => $this->upsertCustomer($c)->id]);
    }

    if (str_contains($relationshipType, 'VENDOR')) {
        $mapping->update(['vendor_id' => $this->upsertVendor($c)->id]);
    }

    return $mapping;
}
```

## Step 3 — Customer side

```php
protected function upsertCustomer(array $c): Customer
{
    return Customer::updateOrCreate(
        [
            'organization_id' => $this->org->id,
            'external_distru_id' => $c['id'],
        ],
        [
            'name' => $c['name'],
            'dba' => $c['dba'] ?? null,
            'license_number' => $c['license_number'] ?? null,
            'email' => $c['email'] ?? null,
            'phone' => $c['phone'] ?? null,
            'billing_address' => $c['billing_address'] ?? null,
            'shipping_address' => $c['shipping_address'] ?? null,
        ],
    );
}
```

## Step 4 — Vendor side

Mirror the customer pattern against the `vendors` table.

## Step 5 — Paginate `/contacts`

```php
$page = 1;
do {
    $response = $api->get('/contacts', [
        'page[number]' => $page,
        'page[size]'   => 200,
    ]);

    foreach ($response['data'] as $contact) {
        $this->upsertContact($contact);
    }

    $page++;
} while ($response['next_page'] !== null);
```

## Step 6 — Map Contacts to the right side

A Contact's parent Company may be a customer, a vendor, or both. Attach the contact to whichever side the parent maps to:

```php
protected function upsertContact(array $contact): void
{
    $parent = DistruCompany::firstWhere([
        'organization_id' => $this->org->id,
        'distru_company_id' => $contact['company_id'],
    ]);
    if (!$parent) return; // skip orphans

    if ($parent->customer_id) {
        CustomerContact::updateOrCreate(
            ['customer_id' => $parent->customer_id, 'external_distru_id' => $contact['id']],
            ['name' => $contact['name'], 'email' => $contact['email'] ?? null, 'phone' => $contact['phone'] ?? null],
        );
    }
    if ($parent->vendor_id) {
        VendorContact::updateOrCreate(
            ['vendor_id' => $parent->vendor_id, 'external_distru_id' => $contact['id']],
            ['name' => $contact['name'], 'email' => $contact['email'] ?? null, 'phone' => $contact['phone'] ?? null],
        );
    }
}
```

## Cross-references

- Endpoint details: `categories/crm.md`
- Pagination: `patterns/pagination.md`
