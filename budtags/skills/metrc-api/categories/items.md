# Items Category

**Collection File**: `collections/metrc-items.postman_collection.json`
**Total Endpoints**: 16
**License Compatibility**: All license types

---

## GET Endpoints (7 endpoints)

- `GET /items/v2/{id}` - Get item by ID
- `GET /items/v2/active` - Get all active items
- `GET /items/v2/inactive` - Get inactive items
- `GET /items/v2/categories` - Get item categories
- `GET /items/v2/brands` - Get item brands
- `GET /items/v2/{id}/image` - Get item image by ID
  - Use case: Retrieve product image
- `GET /items/v2/{id}/file` - Get item file by ID
  - Use case: Retrieve attached documents (COAs, specs, etc.)

---

## POST Endpoints (5 endpoints)

- `POST /items/v2/create` - Create new items
  - Use case: Add new products to catalog
  - Request body: Array of item objects with name, category, unit

- `POST /items/v2/image` - Upload item image
  - Use case: Add product images

- `POST /items/v2/file` - Upload item file
  - Use case: Attach documents (COAs, specifications) to items

### Item Brands

- `POST /items/v2/brands` - Create item brand
  - Use case: Create new brand for product categorization

---

## PUT Endpoints (2 endpoints)

- `PUT /items/v2/update` - Update existing items
  - Use case: Modify item details, pricing, categories

- `PUT /items/v2/brands` - Update item brand
  - Use case: Modify brand information

---

## DELETE Endpoints (2 endpoints)

- `DELETE /items/v2/{id}` - Archive item
  - Use case: Remove discontinued products

- `DELETE /items/v2/brands/{id}` - Archive item brand
  - Use case: Remove brand from active use

---

## Common Example

```php
$newItems = [
    [
        'ItemCategory' => 'Buds',
        'Name' => 'Blue Dream 3.5g',
        'UnitOfMeasure' => 'Grams',
        'Strain' => 'Blue Dream',
        'UnitThcContent' => 0.22,
        'UnitThcContentUnitOfMeasure' => 'Percent',
        'UnitCbdContent' => 0.01,
        'UnitCbdContentUnitOfMeasure' => 'Percent'
    ]
];

$api->post("/items/v2/create?licenseNumber={$license}", $newItems);
```
