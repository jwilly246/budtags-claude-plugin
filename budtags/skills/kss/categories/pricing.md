# Pricing

> Verbatim transcription of [https://kssdata.com/docs/v1#group-pricing](https://kssdata.com/docs/v1#group-pricing) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /customerPricing

Doc anchor: [`#get-customerPricing`](https://kssdata.com/docs/v1#get-customerPricing)

**Badges:** Paginated

Returns per-customer product pricing including any applicable promotions and discounts for a given effective date.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `CustomerIDs` | query | `number[]` | required | Comma-separated list of customer IDs to fetch pricing for. Returns 403 if none are accessible. |
| `EffectiveDate` | query | `date` | optional | ISO 8601 date string to evaluate promotion validity against. Defaults to the current date. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "ProductID": 160,
      "CustomerID": 1,
      "FullPrice": "18.00",
      "UnitPrice": "15.50",
      "Discount": "2.50",
      "PromotionID": 42,
      "StartDate": "2025-01-01",
      "EndDate": "2025-03-31",
      "TimeUpdated": "2025-01-10T08:00:00.000Z"
    },
    {
      "ProductID": 161,
      "CustomerID": 1,
      "FullPrice": "18.00",
      "UnitPrice": "18.00",
      "Discount": "0.00",
      "PromotionID": null,
      "StartDate": null,
      "EndDate": null,
      "TimeUpdated": "2025-01-10T08:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```
