# Products & Catalog - LeafLink API Category

Complete reference for product catalog management endpoints - 24 total operations.

---

## Collection Reference

**OpenAPI Schemas:**
- `schemas/openapi-products-core.json` - Core product CRUD
- `schemas/openapi-products-metadata.json` - Images, batches, strains, product lines

**Total Endpoints:** 24
**Company Compatibility:** Seller companies only (buyers have read-only access)

---

## Endpoint Overview

### Products (Core)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/` | List all products |
| POST | `/products/` | Create product |
| GET | `/products/{id}/` | Get product details |
| PATCH | `/products/{id}/` | Update product |
| DELETE | `/products/{id}/` | Archive product |

### Product Batches

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product-batches/` | List batches |
| POST | `/product-batches/` | Create batch |
| GET | `/product-batches/{id}/` | Get batch details |

### Product Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product-categories/` | List categories |
| GET | `/product-categories/{id}/` | Get category |
| GET | `/product-subcategories/` | List subcategories |
| GET | `/product-subcategories/{id}/` | Get subcategory |

### Product Lines

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product-lines/` | List product lines |
| POST | `/product-lines/` | Create product line |
| GET | `/product-lines/{id}/` | Get product line |
| PATCH | `/product-lines/{id}/` | Update product line |

### Product Images

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product-images/` | List images |
| POST | `/product-images/` | Upload image |
| GET | `/product-images/{id}/` | Get image |
| DELETE | `/product-images/{id}/` | Delete image |

### Strains

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/strains/` | List strains |
| POST | `/strains/` | Create strain |
| GET | `/strains/{id}/` | Get strain |
| PATCH | `/strains/{id}/` | Update strain |

---

## Common Use Cases

### 1. Create Product

```php
$response = $api->post('/products/', [
    'name' => 'Blue Dream',
    'category' => 5,  // Category ID
    'subcategory' => 23,  // Subcategory ID
    'price' => 25.00,
    'unit' => 'each',
    'company' => $companyId,
    'brand' => $brandId,
    'description' => 'Premium Blue Dream flowers',
    'active' => true
]);

$product = $response->json();
$productId = $product['id'];
```

### 2. Upload Product Image

```php
// Upload image to product
$response = $api->post('/product-images/', [
    'product' => $productId,
    'image_url' => 'https://example.com/product.jpg',
    'is_primary' => true
]);
```

### 3. Fetch Products with Filters

```php
// Get products by category, price range
$response = $api->get('/products/', [
    'category' => 5,
    'price__gte' => 10.00,
    'price__lte' => 50.00,
    'active' => 'true',
    'name__icontains' => 'dream',
    'limit' => 100
]);

$products = $response->json('results');
```

### 4. Update Product Price

```php
$response = $api->patch("/products/{$productId}/", [
    'price' => 30.00
]);
```

### 5. Get Categories and Subcategories

```php
// Get all categories
$categories = $api->get_categories();

// Get all subcategories
$subcategories = $api->get_subcategories();

// Get product lines for company
$productLines = $api->get_product_lines($companyId);
```

---

## Available Filters

### Text Filters
- `name__icontains` - Case-insensitive name search
- `name__startswith` - Name starts with
- `description__icontains` - Description contains

### Category Filters
- `category` - Category ID
- `subcategory` - Subcategory ID
- `product_line` - Product line ID
- `brand` - Brand ID

### Pricing Filters
- `price__gte`, `price__lte` - Price range
- `unit` - Unit type (e.g., 'each', 'gram', 'ounce')

### Status Filters
- `active` - Active products only (true/false)
- `in_stock` - In stock only

### Date Filters
- `created_date__gte`, `created_date__lte` - Creation date range
- `modified__gte`, `modified__lte` - Last modified range

---

## Important Notes

### Company Scoping

- Only **seller companies** can create/update products
- **Buyer companies** can browse products (read-only)
- All products are company-scoped (tied to seller)

### Product Hierarchy

```
Brand
└── Product Line (optional grouping)
    └── Product
        ├── Category (required)
        ├── Subcategory (optional)
        ├── Strain (optional, for cannabis products)
        ├── Images (multiple allowed)
        └── Batches (for inventory tracking)
```

### Trailing Slash Required

```php
// ❌ Wrong
$api->get('/products')

// ✅ Correct
$api->get('/products/')
```

---

## Related Resources

- **Scenarios:** `scenarios/product-sync-workflow.md` - Product catalog synchronization
- **Patterns:** `patterns/company-scoping.md` - Seller vs buyer access
- **Patterns:** `patterns/filtering.md` - Advanced product search
- **Schemas:** `schemas/openapi-products-core.json`, `schemas/openapi-products-metadata.json`

---

## Quick Reference

```php
// Create product
$api->post('/products/', ['name' => 'Blue Dream', 'price' => 25.00, 'category' => 5]);

// Update product
$api->patch("/products/{$id}/", ['price' => 30.00]);

// Upload image
$api->post('/product-images/', ['product' => $id, 'image_url' => 'https://...']);

// Get categories
$api->get_categories();

// Search products
$api->get('/products/', ['name__icontains' => 'dream', 'category' => 5]);
```
