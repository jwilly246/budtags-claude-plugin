# AR Aging

> Verbatim transcription of [https://kssdata.com/docs/v1#group-ar-aging](https://kssdata.com/docs/v1#group-ar-aging) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /arAging

Doc anchor: [`#get-arAging`](https://kssdata.com/docs/v1#get-arAging)

**Badges:** Paginated

Returns accounts receivable aging records broken out by AR account and supplier.

> **Callout:** AR Aging is recalculated once per day at the end of the day

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `CustomerIDs` | query | `number[]` | optional | Comma-separated list of customer IDs whose AR accounts should be included. |
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "ARAccountID": 1,
      "SupplierID": 42,
      "OpenCredit": "-31.050000",
      "CurrentDue": "0.000000",
      "Due_1_30": "34635.280000",
      "Due_31_60": "0.000000",
      "Due_61_90": "0.000000",
      "Due_91": "0.000000",
      "CloseDate": "2026-01-25T07:00:00.000Z",
      "TotalBalanceOutstanding": "34635.280000",
      "CurrentInvoices": [],
      "Invoices_1_30": [
        {
          "InvoiceID": 12345,
          "InvoiceNum": "X-12345",
          "OpenBalance": "11545.090000"
        },
        {
          "InvoiceID": 12346,
          "InvoiceNum": "X-12346",
          "OpenBalance": "11545.090000"
        },
        {
          "InvoiceID": 12347,
          "InvoiceNum": "X-12347",
          "OpenBalance": "11545.100000"
        }
      ],
      "Invoices_31_60": [],
      "Invoices_61_90": [],
      "Invoices_91": [],
      "TimeUpdated": "2024-09-23T19:05:39.984Z",
      "CreditInvoices": []
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```
