# Unleashed Software API - Rules, Patterns & Conventions

This document summarizes the common patterns, conventions, and rules for the Unleashed Software API.

---

## Table of Contents
1. [Authentication & Authorization](#authentication--authorization)
2. [Common Query Parameters](#common-query-parameters)
3. [Request/Response Patterns](#requestresponse-patterns)
4. [Endpoint Naming Conventions](#endpoint-naming-conventions)
5. [Date & Time Formats](#date--time-formats)
6. [Pagination Patterns](#pagination-patterns)
7. [Full Object Updates](#full-object-updates)
8. [GUID Identifiers](#guid-identifiers)
9. [Error Handling](#error-handling)
10. [HTTP Methods Usage](#http-methods-usage)

---

## Authentication & Authorization

### HMAC-SHA256 Signing

All requests must be signed using HMAC-SHA256:

1. Extract the query string from the request URL (everything after `?`, or empty string if none)
2. Generate HMAC-SHA256 hash of the query string using the **API Key** as the secret
3. Base64-encode the hash
4. Send as `api-auth-signature` header

### Required Headers

| Header | Value | Description |
|--------|-------|-------------|
| `api-auth-id` | Your API ID | Identifies the API consumer |
| `api-auth-signature` | Base64(HMAC-SHA256(query_string, api_key)) | Request signature |
| `Content-Type` | `application/json` | Request body format |
| `Accept` | `application/json` | Response format |

### PHP Implementation

```php
$apiId = config('services.unleashed.api_id');
$apiKey = config('services.unleashed.api_key');
$queryString = 'pageSize=200&customerCode=ACME';

$signature = base64_encode(
    hash_hmac('sha256', $queryString, $apiKey, true)
);

$headers = [
    'api-auth-id' => $apiId,
    'api-auth-signature' => $signature,
    'Content-Type' => 'application/json',
    'Accept' => 'application/json',
];
```

### Base URL

```
https://api.unleashedsoftware.com/
```

### API Credentials

- API ID and Key are available only to the **account owner**
- Trial accounts also have API access
- Credentials stored in BudTags `Secret` model per-organization

---

## Common Query Parameters

### Pagination Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pageSize` | integer | 200 | Results per page (1-1000) |
| `pageNumber` | integer | 1 | Page number (1-indexed) |

### Date Filtering Parameters
| Parameter | Type | Format | Description |
|-----------|------|--------|-------------|
| `modifiedSince` | date | YYYY-MM-DD | Records created/modified since date |
| `startDate` | date | YYYY-MM-DD | Records with date after this |
| `endDate` | date | YYYY-MM-DD | Records with date before this |

### Sorting Parameters
| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `orderBy` | string | Varies per resource | Sort column |
| `sort` | string | `asc`, `desc` | Sort direction |

Example:
```
/SalesOrders?customerCode=ACME&startDate=2025-01-01&endDate=2025-03-31&pageSize=200&pageNumber=1
```

---

## Request/Response Patterns

### Response Structure

All paginated GET responses follow this structure:

```json
{
  "Pagination": {
    "NumberOfItems": 523,
    "PageSize": 200,
    "PageNumber": 1,
    "NumberOfPages": 3
  },
  "Items": [
    { "Guid": "...", "...": "..." }
  ]
}
```

### Request Bodies

- POST/PUT requests accept a **single object** (not arrays like Metrc)
- Content-Type must be `application/json`
- PUT requests must contain ALL fields (see Full Object Updates)

### Nested Objects

Many resources contain nested objects (Customer, Warehouse, Currency, Tax, etc.). When creating/updating, you typically only need to provide the identifier:

```json
{
  "Customer": { "CustomerCode": "ACME" },
  "Warehouse": { "WarehouseCode": "MAIN" }
}
```

At minimum, provide either `Guid` OR the code/name field for nested objects.

---

## Endpoint Naming Conventions

### URL Patterns

| Operation | Pattern | Example |
|-----------|---------|---------|
| List all | `GET /{Resource}` | `GET /SalesOrders` |
| Get by GUID | `GET /{Resource}/{guid}` | `GET /SalesOrders/abc-123` |
| Create | `POST /{Resource}` or `POST /{Resource}/{guid}` | `POST /SalesOrders` |
| Update | `POST /{Resource}/{guid}` or `PUT /{Resource}/{guid}` | `PUT /SalesOrders/abc-123` |
| Delete | `DELETE /{Resource}/{guid}` | `DELETE /SalesOrders/abc-123` |
| Sub-resource | `GET /{Resource}/{guid}/{SubResource}` | `GET /Customers/{guid}/Contacts` |

### Resource Names (PascalCase, plural)

Editable: `SalesOrders`, `Customers`, `Products`, `StockAdjustments`, `PurchaseOrders`, `SalesShipments`, `CreditNotes`, `SupplierReturns`, `Assemblies`, `BillOfMaterials`, `Salespersons`, `WarehouseStockTransfers`, `AttributeSets`

Read-Only: `StockOnHand`, `StockCounts`, `SalesInvoices`, `SalesQuotes`, `Warehouses`, `Suppliers`, `Currencies`, `Taxes`, `PaymentTerms`, `DeliveryMethods`, `ProductGroups`, `ProductBrands`, `SellPriceTiers`, `CustomerTypes`, `Accounts`, `UnitOfMeasures`, etc.

---

## Date & Time Formats

### Query Parameter Dates
- Format: `YYYY-MM-DD` (ISO 8601 date only)
- Example: `?startDate=2025-01-01&endDate=2025-03-31`

### Response DateTime Fields
- Format: ISO 8601 with time component
- Timezone: UTC
- Example: `"2025-01-15T10:30:00Z"`

### Common Date Fields
| Field | Description |
|-------|-------------|
| `OrderDate` | Date the order was placed |
| `RequiredDate` | Requested delivery date |
| `CompletedDate` | Date order was completed |
| `CreatedOn` | Record creation timestamp |
| `LastModifiedOn` | Last modification timestamp |

---

## Pagination Patterns

### Default Behavior
- Default page size: 200 items
- Maximum page size: 1000 items
- Pages are 1-indexed (first page is 1)
- Use `pageSize=0` to get count only (no items returned)

### Response Metadata
```json
{
  "Pagination": {
    "NumberOfItems": 523,
    "PageSize": 200,
    "PageNumber": 1,
    "NumberOfPages": 3
  }
}
```

### Endpoints Without Pagination
- `Currencies`
- `Companies`
- `SellPriceTiers`

### PHP Iteration Example

```php
$page = 1;
$allItems = [];

do {
    $response = $api->get('/SalesOrders', [
        'pageSize' => 200,
        'pageNumber' => $page,
        'modifiedSince' => $since,
    ]);

    $data = $response->json();
    $allItems = array_merge($allItems, $data['Items']);
    $totalPages = $data['Pagination']['NumberOfPages'];
    $page++;
} while ($page <= $totalPages);
```

---

## Full Object Updates

CRITICAL: The Unleashed API does NOT support partial updates.

### The Rule

When you PUT/update a resource, you MUST include ALL fields. Any field not included in the request will be **overwritten with a blank value**.

### Safe Pattern: GET -> Modify -> PUT

```php
// 1. Fetch the complete current object
$response = $api->get("/Customers/{$guid}");
$customer = $response->json();

// 2. Modify only the fields you need to change
$customer['CreditLimit'] = 50000;
$customer['Notes'] = 'Updated credit limit';

// 3. Send the complete object back
$api->put("/Customers/{$guid}", $customer);
```

### Dangerous Pattern (DO NOT USE)

```php
// This BLANKS every field except CreditLimit!
$api->put("/Customers/{$guid}", [
    'CreditLimit' => 50000,
]);
```

### Resources Requiring Full Object Updates

All 13 editable resources: Sales Orders, Customers, Products, Stock Adjustments, Purchase Orders, Sales Shipments, Credit Notes, Supplier Returns, Assemblies, Bill of Materials, Salespersons, Warehouse Stock Transfers, Attribute Sets

### Some Exceptions

A few fields on certain resources explicitly state "null or missing property will not override existing information":
- Products: `MinimumOrderQuantity`, `MinimumSaleQuantity`, `MinimumSellPrice`
- Customers: `DeliveryInstruction`

These are exceptions, not the rule. Always assume fields will be blanked unless documented otherwise.

---

## GUID Identifiers

### Format
```
XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```
Example: `c97c6b46-f1cc-4741-b236-f882995e7d9a`

### Behavior
- Auto-generated on POST if not provided
- Read-only after creation (cannot be changed)
- Used for individual resource retrieval: `GET /{Resource}/{guid}`
- Used for updates: `PUT /{Resource}/{guid}`
- Null GUID: `00000000-0000-0000-0000-000000000000`

### In BudTags
Store GUIDs locally for fast lookups:
```php
$customer = UnleashedCustomer::where('unleashed_guid', $guid)->first();
```

---

## Error Handling

### HTTP Status Codes
| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad Request | Check request body/params for validation errors |
| 401 | Unauthorized | Verify API ID and signature |
| 404 | Not Found | Check GUID or resource path |
| 405 | Method Not Allowed | Check HTTP method for resource |
| 500 | Server Error | Retry with backoff |

### Common Error Scenarios

1. **Signature mismatch (401)**: Query string in signature doesn't match URL
2. **Invalid GUID (404)**: Resource with that GUID doesn't exist
3. **Missing required field (400)**: POST/PUT missing required fields
4. **Validation error (400)**: Field value exceeds max length or wrong format
5. **Stale data on PUT**: Object modified between GET and PUT

### Retry Strategy

No documented rate limits, but recommend:
- Maximum 3 retries for 5xx errors
- Exponential backoff (1s, 2s, 4s)
- No retry for 4xx errors (fix the request)
- Reduce pageSize if experiencing timeouts

---

## HTTP Methods Usage

| Method | Idempotent | Use Case |
|--------|------------|----------|
| GET | Yes | Retrieve resources (list or single) |
| POST | No | Create new resources |
| PUT | Yes | Update existing resources (full replacement) |
| DELETE | Yes | Remove resources |

Notes:
- Some resources use POST for both create and update (e.g., Products, Customers)
- PUT always requires the complete object
- DELETE is permanent and cannot be undone
- GET requests never modify data
