# Allocations

> Verbatim transcription of [https://kssdata.com/docs/v1#group-allocations](https://kssdata.com/docs/v1#group-allocations) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /allocations

Doc anchor: [`#get-allocations`](https://kssdata.com/docs/v1#get-allocations)

**Badges:** Paginated

Returns product allocations filtered by customer, supplier, and state.

> **Callout:** A single Allocation ID can effect multiple customers. The Unique key is [Allocation, ProductID, CustomerID]

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `CustomerIDs` | query | `number[]` | optional | Comma-separated list of customer IDs to filter by. |
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "AllocationID": 1001,
      "ProductID": 160,
      "CustomerID": 1,
      "Units": 24,
      "AllocationTypeID": 0,
      "StartDate": "2025-01-01",
      "EndDate": "2025-03-31",
      "TimeUpdated": "2025-01-15T10:00:00.000Z"
    },
    {
      "AllocationID": 1002,
      "ProductID": 161,
      "CustomerID": 1,
      "Units": 48,
      "AllocationTypeID": 0,
      "StartDate": "2025-01-01",
      "EndDate": "2025-03-31",
      "TimeUpdated": "2025-01-15T10:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```
