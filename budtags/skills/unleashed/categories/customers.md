# Customers Category

**Total Endpoints**: 8
**Operations**: Full CRUD + Contact management
**Related Read-Only**: Customer Types, Customer Delivery Addresses, Payment Terms

---

## GET Endpoints

- `GET /Customers` - List customers (paginated)
- `GET /Customers/{guid}` - Get single customer
- `GET /Customers/{guid}/Contacts` - List customer contacts (paginated)

### Filters
| Filter | Type | Description |
|--------|------|-------------|
| `customerCode` | string | Code prefix match |
| `customerName` | string | Name prefix match |
| `customer` | string | Code OR name contains (case-sensitive) |
| `customerType` | string | Exact type match |
| `currency` | string | Exact currency code |
| `sellPriceTier` | string | Exact tier match |
| `salesOrderGroup` | string | Exact group match |
| `contactEmail` | string | Contact email prefix |
| `stopCredit` | boolean | Credit-stopped only |
| `includeObsolete` | boolean | Include obsolete (default: excluded) |
| `includeAllContacts` | boolean | Return first 100 contacts |
| `modifiedSince` | date | YYYY-MM-DD |

---

## POST Endpoints

- `POST /Customers` - Create customer
- `POST /Customers/{guid}` - Create/update customer
- `POST /Customers/{guid}/Contacts` - Create contact

---

## PUT Endpoints

- `PUT /Customers/{guid}/Contacts/{contactGuid}` - Update contact

Note: Customer updates use POST to `/{guid}`, not PUT.

---

## DELETE Endpoints

- `DELETE /Customers/{guid}/Contacts/{contactGuid}` - Delete contact

---

## Key Fields

### Customer
| Field | Type | Length | Required (POST) |
|-------|------|--------|-----------------|
| `CustomerCode` | string | 500 | Required (set only on creation) |
| `CustomerName` | string | 500 | Required |
| `Currency` | object | - | Optional (Guid or CurrencyCode) |
| `DefaultWarehouse` | object | - | Optional (Guid or WarehouseCode) |
| `CustomerType` | string | 50 | Optional |
| `Taxable` | boolean | - | Optional |
| `TaxCode` | string | 50 | Optional |
| `TaxRate` | decimal | - | Optional |
| `DiscountRate` | decimal | - | Optional |
| `CreditLimit` | decimal | - | Optional |
| `PaymentTerm` | string | 100 | Optional |
| `SellPriceTier` | string | 25 | Optional |
| `DeliveryMethod` | string | 50 | Optional |
| `Salesperson` | object | - | Optional (Guid required) |
| `Addresses` | array | - | Optional (types: Postal, Physical, Shipping) |
| `Notes` | string | 1024 | Optional |
| `GSTVATNumber` | string | 500 | Optional |
| `EORINumber` | string | 20 | Optional |

### Primary Contact (on Customer object)
| Field | Type | Length |
|-------|------|--------|
| `ContactFirstName` | string | 500 |
| `ContactLastName` | string | 500 |
| `Email` | string | 500 |
| `PhoneNumber` | string | 500 |
| `MobileNumber` | string | 500 |
| `FaxNumber` | string | 500 |
| `Website` | string | 500 |

### Address Object
| Field | Type | Length |
|-------|------|--------|
| `AddressType` | string | 20 (Postal/Physical/Shipping) |
| `AddressName` | string | 500 |
| `StreetAddress` | string | 500 |
| `StreetAddress2` | string | 500 |
| `City` | string | 500 |
| `Region` | string | 500 |
| `Country` | string | 500 (ISO 3166 or name) |
| `PostalCode` | string | 500 |

### Contact Object
| Field | Type | Length | Required |
|-------|------|--------|----------|
| `FirstName` | string | 500 | * |
| `LastName` | string | 500 | * |
| `EmailAddress` | string | 500 | * |
| `PhoneNumber` | string | 500 | Optional |
| `MobilePhone` | string | 500 | Optional |
| `IsDefault` | boolean | - | Optional |
| `ForInvoicing` | boolean | - | Optional |
| `ForOrdering` | boolean | - | Optional |
| `ForShipping` | boolean | - | Optional |
| `DeliveryAddress` | string | 500 | Optional (must match existing) |

*At minimum, FirstName, LastName, and/or EmailAddress required. Combination must be unique.

---

## Common Use Cases

### 1. Fetch Customers Modified Since Date
```php
$response = $api->get('/Customers', [
    'modifiedSince' => '2025-01-01',
    'pageSize' => 200,
]);
$customers = $response->json()['Items'];
```

### 2. Create Customer
```php
$api->post('/Customers', [
    'CustomerCode' => 'NEWCUST',
    'CustomerName' => 'New Customer Inc',
    'ContactFirstName' => 'John',
    'ContactLastName' => 'Doe',
    'Email' => 'john@example.com',
    'Currency' => ['CurrencyCode' => 'USD'],
]);
```

### 3. Update Customer (Safe Pattern)
```php
$customer = $api->get("/Customers/{$guid}")->json();
$customer['CreditLimit'] = 50000;
$api->post("/Customers/{$guid}", $customer);
```

---

## Important Notes

- CustomerCode is set only on creation, cannot be updated
- Primary contact editable via the customer object; other contacts use separate endpoints
- Contact POST does not accept user-generated GUIDs
- DeliveryInstruction: null/missing on update won't override existing value (exception to full-object-update rule)
- EmailCC supports multiple comma-separated addresses
- Obsolete customers excluded by default
