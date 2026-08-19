# Purchase Transactions

> Verbatim transcription of [https://kssdata.com/docs/v1#group-purchase-transactions](https://kssdata.com/docs/v1#group-purchase-transactions) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /purchaseTrans

Doc anchor: [`#get-purchaseTrans`](https://kssdata.com/docs/v1#get-purchaseTrans)

**Badges:** Not available to Customer keys · Paginated

Returns purchase order line items for one or more purchases. PurchaseIDs is required. Not accessible to Customer API keys.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `PurchaseIDs` | query | `number[]` | required | Comma-separated list of purchase IDs to retrieve line items for. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "PurchaseTransID": 99001,
      "PurchaseID": 10001,
      "ProductID": 5001,
      "Ordered": "10",
      "NumUnits": "120",
      "FOB": "12.50",
      "DepositCost": "0.00",
      "ExtPrice": "1500.00",
      "ExpirationDate": "2026-01-01T00:00:00.000Z",
      "CodeDate": "2025-01-15T00:00:00.000Z",
      "BatchCode": "BCH-001",
      "LaidInCost": "13.00",
      "PalletTag": null,
      "Cases": "10",
      "Weight": "120.00",
      "TimeUpdated": "2025-03-02T10:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```
