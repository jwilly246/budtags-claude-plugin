# Supplier Returns Category

**Operations**: Full CRUD
**Related Read-Only**: Supplier Return Reasons

---

## Endpoints

- `GET /SupplierReturns` - List supplier returns (paginated)
- `GET /SupplierReturns/{guid}` - Get single return
- `POST /SupplierReturns` - Create return
- `PUT /SupplierReturns/{guid}` - Update return (FULL OBJECT REQUIRED)
- `DELETE /SupplierReturns/{guid}` - Delete return

### Common Filters
| Filter | Type | Description |
|--------|------|-------------|
| `modifiedSince` | date | Returns modified since date |
| `pageSize` | integer | Default 200 |

---

## Key Fields

### Supplier Return
| Field | Type | Required |
|-------|------|----------|
| `Supplier` | object | Required (Guid or SupplierCode) |
| `Warehouse` | object | Required (Guid or WarehouseCode) |
| `ReturnReason` | string | Required |
| `ReturnLines` | array | Required (min 1 line) |
| `ReturnDate` | datetime | Optional |
| `Comments` | string | Optional |

### Return Line
| Field | Type | Required |
|-------|------|----------|
| `Product` | object | Required (Guid or ProductCode) |
| `ReturnQuantity` | decimal | Required |
| `UnitCost` | decimal | Required |
| `Comments` | string | Optional |

---

## Related: Supplier Return Reasons (Read-Only)

- `GET /SupplierReturnReasons` - List valid return reasons

---

## Important Notes

- PUT replaces entire object - see `patterns/full-object-updates.md`
- Return reasons must match valid values from SupplierReturnReasons endpoint
