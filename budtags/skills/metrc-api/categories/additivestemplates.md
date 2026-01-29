# Additives Templates Category

**Collection File**: `collections/metrc-additivestemplates.postman_collection.json`
**Total Endpoints**: 5
**License Compatibility**: Cultivation licenses

---

## GET Endpoints

- `GET /additivestemplates/v2/active` - Get active additive templates

---

## POST Endpoints

- `POST /additivestemplates/v2/create` - Create additive templates
  - Use case: Create reusable fertilizer/pesticide application templates
  - Request body: Template name, ingredients, application rates

---

## PUT Endpoints

- `PUT /additivestemplates/v2/update` - Update template details

---

## Example

```php
$templates = [
    [
        'Name' => 'Vegetative Nutrients - Week 3',
        'Ingredients' => [
            ['Name' => 'Nitrogen', 'Amount' => 10, 'UnitOfMeasure' => 'Milliliters']
        ]
    ]
];

$api->post("/additivestemplates/v2/create?licenseNumber={$license}", $templates);
```
