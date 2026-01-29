# LeafLink Company Scoping (CRITICAL!)

Understanding seller vs buyer context in LeafLink API - the most important concept for successful integration.

---

## Critical Concept

**Every LeafLink API request is scoped to a company context.**

API keys are associated with ONE company, and all operations return data for that company only.

---

## Two Company Types

### 1. Seller (Brand/Manufacturer)

**Primary Role**: Product provider

**Capabilities:**
- Manages product catalog
- Receives orders from buyers (retailers)
- Ships orders to buyers
- Tracks customer relationships
- Manages seller inventory

**Endpoints Used:**
- `/orders-received/*` - Incoming orders from buyers
- `/products/*` - Product catalog management
- `/customers/*` - Customer relationships
- `/inventory-items/*` - Seller inventory
- `/brands/*` - Brand management

**Example Workflow:**
1. Buyer browses seller's product catalog
2. Buyer places order → appears in `/orders-received/`
3. Seller accepts/confirms order
4. Seller ships products to buyer
5. Order marked as delivered

### 2. Buyer (Retailer/Dispensary)

**Primary Role**: Product purchaser/retailer

**Capabilities:**
- Places orders from sellers
- Receives deliveries
- Tracks retailer inventory for POS
- Manages own facilities

**Endpoints Used:**
- `/buyer/orders/*` - Outgoing orders to sellers
- `/retailer-inventory/*` - Retail inventory tracking
- `/facilities/*` - Retailer locations
- (Limited product browsing - seller catalogs)

**Example Workflow:**
1. Buyer browses seller catalogs
2. Buyer creates order → appears in `/buyer/orders/`
3. Seller confirms and ships
4. Buyer receives delivery
5. Updates retailer inventory

---

## API Key Company Association

Each API key is tied to ONE company:

```php
// API key determines which company's data you see
$headers = ['Authorization' => 'App SELLER_KEY'];  // See seller data only
$headers = ['Authorization' => 'App BUYER_KEY'];   // See buyer data only
```

You CANNOT switch company context with the same API key.

---

## Data Visibility Rules

| Resource | Seller Sees | Buyer Sees |
|----------|-------------|------------|
| **Orders** | Incoming orders (`/orders-received/`) | Outgoing orders (`/buyer/orders/`) |
| **Products** | Own products only (can create/update) | All seller products (read-only browsing) |
| **Customers** | Own customer relationships | N/A (not applicable to buyers) |
| **Inventory** | Own seller inventory (`/inventory-items/`) | Own retailer inventory (`/retailer-inventory/`) |
| **Line Items** | Line items for orders received | Line items for orders placed |

---

## Checking Company Context

```php
// Get authenticated company
$response = $api->get('/companies/me/');

$company = $response->json();
// {
//     "id": 123,
//     "name": "Acme Cannabis Co",
//     "company_type": "seller",  // or "buyer"
//     ...
// }
```

**Use this to:**
- Determine which endpoints are available
- Route to correct order endpoints
- Display appropriate UI/features

---

## Common Scoping Issues

### Issue 1: Empty Results

**Symptom**: API call returns empty array when data should exist

**Cause**: Using wrong company context

**Solution**:
```php
// ❌ Wrong: Buyer trying to access seller orders
$api->get('/orders-received/');  // Returns []

// ✅ Correct: Buyer using buyer orders endpoint
$api->get('/buyer/orders/');
```

### Issue 2: 404 Not Found

**Symptom**: GET /resource/{id}/ returns 404

**Cause**: Resource doesn't belong to authenticated company

**Solution**:
- Verify resource ID belongs to your company
- Check company context before accessing resources
- Only access resources you created or received

### Issue 3: Mismatched Order Endpoints

**Symptom**: Can't find orders in expected endpoint

**Cause**: Confusion between seller/buyer order endpoints

**Solution**:
```php
// Seller company - received orders
$orders = $api->get('/orders-received/');

// Buyer company - placed orders
$orders = $api->get('/buyer/orders/');
```

---

## Best Practices

✅ **Do:**
- Always check company type at integration start
- Use correct endpoint for company context
- Filter by company-scoped relationships
- Log company context in debug messages

❌ **Don't:**
- Assume data visibility across companies
- Try to access other companies' data
- Mix seller/buyer endpoints
- Forget company context when troubleshooting

---

## Key Takeaways

1. **One API key = One company** - No switching contexts
2. **Seller orders** = `/orders-received/` (incoming)
3. **Buyer orders** = `/buyer/orders/` (outgoing)
4. **Empty results** = Usually wrong company context
5. **Check company type FIRST** when building integrations
