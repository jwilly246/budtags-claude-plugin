# Suppliers

> Verbatim transcription of [https://kssdata.com/docs/v1#group-suppliers](https://kssdata.com/docs/v1#group-suppliers) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /suppliers

Doc anchor: [`#get-suppliers`](https://kssdata.com/docs/v1#get-suppliers)

**Badges:** Paginated

Returns suppliers filtered by state, supplier ID, and status.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |
| `Active` | query | `boolean[]` | optional | True or False flag for supplier status. Defaults to Active only for Customer and Supplier keys |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "SupplierID": 1,
      "Supplier": "Kiva",
      "State": "CA",
      "Active": true,
      "Description": "Premium cannabis edibles and infused products.",
      "BrandAssetsURL": "https://cdn.example.com/kiva/brand-assets.zip",
      "SupplierWebsiteURL": "https://www.kivaconfections.com",
      "TimeUpdated": "2025-01-01T00:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /suppliers/creditTerms

Doc anchor: [`#get-suppliers-creditTerms`](https://kssdata.com/docs/v1#get-suppliers-creditTerms)

**Badges:** Not available to Customer keys · Paginated

Returns the credit terms offered by each supplier.

> **Callout:** Not available to customer keys (returns 403). Supplier keys only see rows for their authorized suppliers.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "SupplierID": 5,
      "TermID": 3,
      "Term": "Net 30",
      "TimeUpdated": "2025-01-15T10:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /suppliers/:supplierID

Doc anchor: [`#get-suppliers--supplierID`](https://kssdata.com/docs/v1#get-suppliers--supplierID)

Returns a single supplier by ID.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `supplierID` | path | `number` | required | The ID of the supplier to retrieve. |

### Example Response

**json**

```json
{
  "Data": [
    {
      "SupplierID": 1,
      "Supplier": "Kiva",
      "State": "CA",
      "Active": true,
      "Description": "Premium cannabis edibles and infused products.",
      "BrandAssetsURL": "https://cdn.example.com/kiva/brand-assets.zip",
      "SupplierWebsiteURL": "https://www.kivaconfections.com",
      "TimeUpdated": "2025-01-01T00:00:00.000Z"
    }
  ]
}
```
