# LeafLink Company Scoping (CRITICAL!)

Understanding seller vs buyer context in LeafLink API - the most important concept for successful integration.

"Spec" = the official OpenAPI (`~/budtags-audits/2026-10-15/leaflink_docs_gap_audit/official_openapi.json`); "docs" = its text copies in `.../leaflink_docs_gap_audit/text/`.

---

## Critical Concept

**Every LeafLink API request is scoped by the API key.**

- **App token**: "access via API to the single company in which the App token was created" (docs, api_authorization.txt). Budtags uses App keys: one key = one company.
- **User token**: "access to all companies via API that the user is permissioned within" (docs). With a User token, always filter by `company`, and remember several endpoints ignore `company` (see below).

---

## Two Company Types

A company is a seller, a buyer, or both: `/companies/` returns `seller` and `buyer` **booleans**. There is no `company_type` field (spec CompanyResponse; Evo reads `"seller": true, "buyer": false` in sandbox logs/requests.jsonl 2026-10-16).

### 1. Seller (Brand/Manufacturer)

**Endpoints Used** (spec paths):
- `/orders-received/`, `/orders-received/{number}/`, `/orders-received/{number}/transition/{action}/`, `/orders-received/{number}/line-items/`, `/orders-received/{number}/payments/`
- `/line-items/`, `/order-payments/`, `/order-event-logs/`, `/order-sales-reps/`
- `/products/`, `/product-lines/`, `/strains/`, `/product-images/`, `/product-batches/`
- `/customers/`, `/customer-statuses/`, `/customer-tiers/`, `/contacts/`, `/activity-entries/`
- `/brands/`, `/licenses/`, `/companies/`, `/company-staff/`
- `/inventory/items/` and `/inventory/facilities/` (BETA). Brand inventory itself lives on the product: `quantity`, `reserved_qty`, `available_inventory` (docs, brands_api_inventory.txt). There is no `/inventory-items/` path.

**Order lifecycle** (spec statuses): Draft -> Submitted -> Accepted -> Fulfilled -> Shipped -> Complete, plus Backorder, Rejected, Cancelled, Combined. Transitions and their inventory effects: `verified-behavior.md`.

### 2. Buyer (Retailer/Dispensary)

**Endpoints Used** (spec paths):
- `/buyer/orders/` - orders placed with sellers
- `/retailer-inventory/` - retail inventory
- Product browsing of seller catalogs

---

## API Key Company Association

```php
// The App key decides which company's data you see
$headers = ['Authorization' => 'App ' . $sellerKey];
```

You cannot switch company with the same App key.

### `company` filters that are ignored

Verified 2026-10-16 (sandbox, r3_a_param_sweep.txt): `/brands/?company=`, `/product-lines/?company=` and `/licenses/?company=` return the same rows with or without the filter. With an App key that is harmless (one company). With a User token, filter client-side.

---

## Data Visibility Rules

| Resource | Seller Sees | Buyer Sees |
|----------|-------------|------------|
| **Orders** | Incoming orders (`/orders-received/`) | Outgoing orders (`/buyer/orders/`) |
| **Products** | Own listings (create/update; archive instead of delete) | Seller catalogs (read) |
| **Customers** | Own customer records | N/A |
| **Inventory** | Product `quantity` / `reserved_qty` / `available_inventory`; `/inventory/items/` (BETA) | `/retailer-inventory/` |
| **Line Items** | Lines on orders received | Lines on orders placed |

---

## Checking Company Context

`/companies/me/` is not in the spec (it works in practice per the docs audit). The spec path is `/companies/`:

```php
$company = $api->get('/companies/')->json('results.0');
// { "id": 11992, "name": "EVO Pharms", "seller": true, "buyer": false, ... }

if ($company['seller']) {
    // seller endpoints
}
```

---

## Common Scoping Issues

### Issue 1: Empty Results

**Cause**: wrong company context, or a filter that IS honoured narrowed it to nothing.

```php
// ❌ Buyer key on seller orders
$api->get('/orders-received/');

// ✅ Buyer orders
$api->get('/buyer/orders/');
```

### Issue 2: Too MANY results

**Cause**: an ignored filter returns the whole list with a 200 (sandbox, r3_a_param_sweep.txt). See `filtering.md`.

### Issue 3: 404 Not Found

**Cause**: the id doesn't exist, isn't your company's, or (line items) was deleted.

---

## Best Practices

✅ **Do:**
- Use App keys (one company each)
- Read `seller` / `buyer` from `/companies/`
- Log the company id in debug messages

❌ **Don't:**
- Look for `company_type` (it doesn't exist)
- Call `/inventory-items/` (it doesn't exist)
- Trust `company=` on brands, product-lines or licenses

---

## Key Takeaways

1. **One App key = one company**
2. **Seller orders** = `/orders-received/` (keyed by `number`)
3. **Buyer orders** = `/buyer/orders/`
4. **Company type** = `seller` / `buyer` booleans on `/companies/`
5. **Empty or too-full results** = check company context and whether the filter is honoured
