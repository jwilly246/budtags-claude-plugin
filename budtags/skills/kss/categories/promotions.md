# Promotions

> Verbatim transcription of [https://kssdata.com/docs/v1#group-promotions](https://kssdata.com/docs/v1#group-promotions) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /menuPromotions

Doc anchor: [`#get-menuPromotions`](https://kssdata.com/docs/v1#get-menuPromotions)

**Badges:** Paginated

Returns menu promotions filtered by supplier, state, and active date range.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |
| `StartDate` | query | `date` | optional | ISO 8601 date string. Returns promotions whose end date is on or after this value. |
| `EndDate` | query | `date` | optional | ISO 8601 date string. Returns promotions whose start date is on or before this value. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "MenuPromotionID": 7001,
      "SupplierID": 1,
      "SupplierName": "Kiva",
      "State": "CA",
      "Description": "Featured products for spring menus.",
      "StartDate": "2025-03-01",
      "EndDate": "2025-05-31",
      "TimeUpdated": "2025-02-15T10:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /promotionsProducts

Doc anchor: [`#get-promotionsProducts`](https://kssdata.com/docs/v1#get-promotionsProducts)

**Badges:** Paginated

Returns promotion records with their associated products filtered by supplier and state.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "PromotionID": 42,
      "PromotionTypeID": 4,
      "States": [
        "CA"
      ],
      "PromotionName": "Spring Chocolate Deal",
      "ProductOverrideType": "none",
      "UnitPrice": 15.5,
      "StartDate": "2025-01-01",
      "EndDate": "2025-03-31",
      "AllProducts": false,
      "ProductIDs": [
        160,
        161,
        162
      ],
      "TimeUpdated": "2024-12-20T10:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```
