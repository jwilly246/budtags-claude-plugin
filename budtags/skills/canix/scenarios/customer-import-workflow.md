# Scenario: Import Customers & Vendors from Canix

This workflow imports Canix customers into BudTags `Customer` records and Canix vendors into the new `Vendor` model.

## Prerequisites

- Canix API key configured
- Organization context established

## Import Order

Customers and vendors have no dependencies on other entities — they can be imported in any order, but should come before sales orders (which reference customers) and purchase orders (which reference vendors).

## Step 1: Import Customers

```php
$offset = 0;
$limit = 2000;

do {
    $customers = $api->get('/customers', array_filter([
        'limit' => $limit,
        'offset' => $offset,
        'where' => $modified_since ? "updated_at >= '{$modified_since}'" : null,
        'order_by' => 'id asc',
    ]));

    collect($customers)->each(function (array $customer) use ($ctx) {
        $this->process_customer($customer, $ctx);
        $ctx->increment_progress();
    });

    $offset += $limit;
} while (count($customers) === $limit);
```

### Process Individual Customer

```php
private function process_customer(array $data, ImportContext $ctx): void
{
    $existing = $ctx->customer_cache[$data['id']] ?? null;

    $address = $data['address'] ?? [];

    $customer_data = [
        'organization_id'         => $ctx->org_id,
        'canix_id'                => $data['id'],
        'name'                    => $data['company_name'] ?? $data['contact_name'],
        'contact_name'            => $data['contact_name'] ?? null,
        'email'                   => $data['email'] ?? null,
        'phone'                   => $data['phone'] ?? null,
        'license_number'          => $data['facility_license_number'] ?? null,
        'license_expiration_date' => $data['license_expiration_date'] ?? null,
        'address'                 => $address['street'] ?? null,
        'address2'                => $address['street2'] ?? null,
        'city'                    => $address['city'] ?? null,
        'state'                   => $address['state'] ?? null,
        'zipcode'                 => $address['postal_code'] ?? null,
        'notes'                   => $data['notes'] ?? null,
        'source'                  => 'canix',
    ];

    if ($existing) {
        $existing->update($customer_data);
        $ctx->stats['updated']++;
    } else {
        Customer::create($customer_data);
        $ctx->stats['created']++;
    }
}
```

### Customer Field Mapping

| Canix Customer | BudTags Customer | Notes |
|----------------|------------------|-------|
| `id` | `canix_id` | Integer FK |
| `company_name` | `name` | Primary name |
| `contact_name` | `contact_name` | Contact person |
| `email` | `email` | Direct |
| `phone` | `phone` | Direct |
| `facility_license_number` | `license_number` | String |
| `license_expiration_date` | `license_expiration_date` | Date |
| `address.street` | `address` | Nested → flat |
| `address.street2` | `address2` | Nested → flat |
| `address.city` | `city` | Nested → flat |
| `address.state` | `state` | Nested → flat |
| `address.postal_code` | `zipcode` | Nested → flat |
| `notes` | `notes` | Direct |
| `customer_number` | — | Not mapped (Canix internal) |
| `territory` | — | Not mapped |
| `license_type` | — | Not mapped |
| `outstanding_balance` | — | Dynamic, not persisted |
| `dba` | — | Not mapped |

## Step 2: Import Vendors (NEW Model)

```php
$offset = 0;
$limit = 2000;

do {
    $vendors = $api->get('/vendors', array_filter([
        'limit' => $limit,
        'offset' => $offset,
        'order_by' => 'id asc',
    ]));

    collect($vendors)->each(function (array $vendor) use ($ctx) {
        $this->process_vendor($vendor, $ctx);
        $ctx->increment_progress();
    });

    $offset += $limit;
} while (count($vendors) === $limit);
```

### Process Individual Vendor

```php
private function process_vendor(array $data, ImportContext $ctx): void
{
    Vendor::updateOrCreate(
        ['organization_id' => $ctx->org_id, 'canix_id' => $data['id']],
        [
            'name'            => $data['name'],
            'email'           => $data['email'] ?? null,
            'phone'           => $data['phone'] ?? null,
            'address'         => $data['address'] ?? null,
            'city'            => $data['city'] ?? null,
            'state'           => $data['state'] ?? null,
            'zipcode'         => $data['postal_code'] ?? null,
            'license_number'  => $data['license_number'] ?? null,
            'notes'           => $data['notes'] ?? null,
        ],
    );
}
```

### Vendor Field Mapping

| Canix Vendor | BudTags Vendor | Notes |
|--------------|----------------|-------|
| `id` | `canix_id` | Integer FK |
| `name` | `name` | Required |
| `email` | `email` | Direct |
| `phone` | `phone` | Direct |
| `address` | `address` | Flat (not nested like Customer) |
| `city` | `city` | Direct |
| `state` | `state` | Direct |
| `postal_code` | `zipcode` | Direct |
| `license_number` | `license_number` | Direct |
| `notes` | `notes` | Direct |
| `contact_name` | — | Not mapped (future consideration) |
| `license_expiration_date` | — | Not mapped |
| `website_url` | — | Not mapped |
| `min_lead_time` | — | Not mapped |
| `country` | — | Not mapped |
| `address2` | — | Not mapped |

## Deduplication Strategy

### Customers
- Primary key: `(organization_id, canix_id)` unique index
- On re-import: updateOrCreate by `canix_id` — updates existing record
- Cross-source dedup (same customer in both LeafLink and Canix): not handled automatically; customer may exist twice with different `leaflink_id` and `canix_id`

### Vendors
- Primary key: `(organization_id, canix_id)` unique index
- On re-import: updateOrCreate by `canix_id`
- Vendors are Canix-only (no LeafLink equivalent)

## Cache Building

After import, build caches for order processing:

```php
// Build customer cache: canix_id → uuid
$ctx->customer_cache = Customer::where('organization_id', $org_id)
    ->whereNotNull('canix_id')
    ->pluck('id', 'canix_id')
    ->toArray();

// Build vendor cache: canix_id → uuid
$ctx->vendor_cache = Vendor::where('organization_id', $org_id)
    ->whereNotNull('canix_id')
    ->pluck('id', 'canix_id')
    ->toArray();
```

## Error Handling

- Missing `company_name`: fall back to `contact_name`
- Missing address fields: set null (all address fields are nullable)
- Inactive customers (`is_active=false`): still import, but mark if applicable

---

**See:** `categories/crm.md` for complete endpoint details
**See:** `scenarios/sales-order-import-workflow.md` for orders that reference customers
**See:** `categories/purchase-orders.md` for POs that reference vendors
