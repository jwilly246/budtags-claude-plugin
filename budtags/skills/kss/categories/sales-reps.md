# Sales Reps

> Verbatim transcription of [https://kssdata.com/docs/v1#group-sales-reps](https://kssdata.com/docs/v1#group-sales-reps) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /salesReps

Doc anchor: [`#get-salesReps`](https://kssdata.com/docs/v1#get-salesReps)

**Badges:** Paginated

Returns sales reps grouped by user, including both Territory Managers and Supplier Reps. Each result includes the rep's name, email, type, the product groups they cover, and arrays of associated customers and suppliers. Type is derived from ProductGroup: 'Supplier' indicates a Supplier Rep; any other value (e.g. a product-line group such as 'Cookies' or 'Tinctures') indicates a Territory Manager. Only returns active users, active customers, and active suppliers. Supplier API keys see reps scoped to their authorized suppliers. Customer API keys only see reps assigned to their own customers.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. Supplier keys are automatically scoped to their authorized suppliers. |
| `CustomerIDs` | query | `number[]` | optional | Comma-separated list of customer IDs to filter by. Customer keys are automatically scoped to their authorized customers. |
| `ProductGroups` | query | `string[]` | optional | Comma-separated list of product group names to filter by. Use 'Supplier' to limit results to Supplier Reps, or product-line names (e.g. 'Cookies') to limit to Territory Managers covering those groups. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "UserID": 42,
      "Name": "Jane Smith",
      "Email": "jane.smith@example.com",
      "Type": "Territory Manager",
      "ProductGroups": [
        "Cookies",
        "Tinctures"
      ],
      "Suppliers": [
        {
          "SupplierID": 10,
          "Supplier": "Kiva Confections"
        }
      ],
      "Customers": [
        {
          "CustomerID": 100,
          "CustomerName": "Acme Dispensary"
        },
        {
          "CustomerID": 101,
          "CustomerName": "Green Leaf Co"
        }
      ]
    },
    {
      "UserID": 501,
      "Name": "Bob Jones",
      "Email": "bob.jones@supplier.com",
      "Type": "Supplier Rep",
      "ProductGroups": [
        "Supplier"
      ],
      "Suppliers": [
        {
          "SupplierID": 10,
          "Supplier": "Kiva Confections"
        },
        {
          "SupplierID": 11,
          "Supplier": "Kiva Brand 2"
        }
      ],
      "Customers": [
        {
          "CustomerID": 100,
          "CustomerName": "Acme Dispensary"
        }
      ]
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```
