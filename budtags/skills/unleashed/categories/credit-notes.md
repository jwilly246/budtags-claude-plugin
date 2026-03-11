# Credit Notes Category

**Total Endpoints**: 9
**Operations**: GET, POST (FreeCredit only), PUT, DELETE, Complete + Line management
**Limitation**: Only "FreeCredit" notes can be created/updated via API

---

## GET Endpoints

- `GET /CreditNotes` - List credit notes (paginated)
- `GET /CreditNotes/{guid}` - Get single credit note

### Filters
| Filter | Type | Description |
|--------|------|-------------|
| `creditNumber` | string | Exact match (overrides other filters) |
| `creditStatus` | string | Filter by status (e.g., "Parked") |
| `startDate` | date | Credits dated after |
| `endDate` | date | Credits dated before |
| `modifiedSince` | date | Modified since |

---

## POST Endpoints

- `POST /CreditNotes/FreeCredit` - Create free-entry credit note
- `POST /CreditNotes/{guid}/Complete` - Complete credit note
- `POST /CreditNotes/{guid}/Lines` - Add line to credit note

---

## PUT Endpoints

- `PUT /CreditNotes/{guid}` - Update credit note
- `PUT /CreditNotes/{guid}/Lines/{lineGuid}` - Update line

---

## DELETE Endpoints

- `DELETE /CreditNotes/{guid}` - Delete credit note
- `DELETE /CreditNotes/{guid}/Lines/{lineGuid}` - Delete line

---

## Key Fields

### Credit Note
| Field | Type | Required (POST) |
|-------|------|-----------------|
| `CreditDate` | datetime | Required |
| `Customer` | object | Required (Guid or CustomerCode) |
| `Warehouse` | object | Required (Guid or WarehouseCode) |
| `ExchangeRate` | decimal | Required |
| `Comments` | string (1024) | Optional |
| `Reference` | string (500) | Optional |

### Credit Note Line
| Field | Type | Required |
|-------|------|----------|
| `Product` | object | Required (Guid or ProductCode) |
| `CreditQuantity` | decimal | Required |
| `CreditPrice` | decimal | Required |
| `Reason` | string | Required |
| `Return` | boolean | Required |

---

## Common Use Cases

### Create Free Credit Note
```php
$api->post('/CreditNotes/FreeCredit', [
    'CreditDate' => now()->format('Y-m-d'),
    'Customer' => ['CustomerCode' => 'ACME'],
    'Warehouse' => ['WarehouseCode' => 'MAIN'],
    'ExchangeRate' => 1.0,
    'CreditLines' => [
        [
            'Product' => ['ProductCode' => 'SKU-001'],
            'CreditQuantity' => 2,
            'CreditPrice' => 25.00,
            'Reason' => 'Damaged goods',
            'Return' => true,
        ],
    ],
]);
```

---

## Important Notes

- Only FreeCredit credit notes can be created or updated via API
- Batch/serial numbers cannot be hard-allocated to free-entry notes in Parked status
- GUIDs follow standard format
