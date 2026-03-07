# Salespersons Category

**Operations**: Full CRUD

---

## Endpoints

- `GET /Salespersons` - List salespersons (paginated)
- `GET /Salespersons/{guid}` - Get single salesperson
- `POST /Salespersons` - Create salesperson
- `PUT /Salespersons/{guid}` - Update salesperson
- `DELETE /Salespersons/{guid}` - Delete salesperson

### Filters
| Filter | Type | Description |
|--------|------|-------------|
| `modifiedSince` | date | Modified since (YYYY-MM-DD) |
| `pageSize` | integer | Default 200 |

---

## Key Fields

| Field | Type | Length | Required |
|-------|------|--------|----------|
| `Guid` | GUID | - | Auto-generated |
| `FullName` | string | 256 | Required |
| `Email` | string | 256 | Optional |
| `Obsolete` | boolean | - | Optional |

---

## Usage

Salespersons are referenced in Sales Orders and Customers:

```json
{
  "Salesperson": {
    "Guid": "abc-123...",
    "FullName": "Jane Smith",
    "Email": "jane@example.com"
  }
}
```

When assigning a salesperson to a customer or order, the `Guid` is required.
