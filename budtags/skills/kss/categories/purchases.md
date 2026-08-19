# Purchases

> Verbatim transcription of [https://kssdata.com/docs/v1#group-purchases](https://kssdata.com/docs/v1#group-purchases) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /purchases

Doc anchor: [`#get-purchases`](https://kssdata.com/docs/v1#get-purchases)

**Badges:** Not available to Customer keys · Paginated

Returns purchase orders filtered by purchase ID, vendor, location, status, and date range. Not accessible to Customer API keys.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `PurchaseIDs` | query | `number[]` | optional | Comma-separated list of purchase IDs to filter by. |
| `VendorIDs` | query | `number[]` | optional | Comma-separated list of vendor IDs to filter by. |
| `LocationIDs` | query | `number[]` | optional | Comma-separated list of destination location IDs to filter by. |
| `Statuses` | query | `string[]` | optional | Comma-separated list of purchase statuses to filter by. Defaults to all statuses.<br>Values: `New` = New, `Accepted` = Accepted, `Received` = Received, `Confirmed` = Confirmed, `Verified` = Verified |
| `StartDate` | query | `date` | optional | ISO 8601 date string. Returns purchases with a PostDate on or after this date. |
| `EndDate` | query | `date` | optional | ISO 8601 date string. Returns purchases with a PostDate on or before this date. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "PurchaseID": 10001,
      "ReceiveDate": "2025-03-01T00:00:00.000Z",
      "ShipmentNum": "SHP-2025-001",
      "ShipmentID": 5001,
      "ToLocationID": 3,
      "ToLocationName": "Main Warehouse",
      "VendorName": "Acme Distributing",
      "VendorID": 42,
      "PostDate": "2025-03-01T00:00:00.000Z",
      "Status": "Received",
      "PONum": "PO-2025-0123",
      "Freight": "150.00",
      "Tax": "0.00",
      "OtherCost": "0.00",
      "Total": "4500.00",
      "TotalCases": "30",
      "PublicPDFLink": null,
      "Memo": null,
      "InvoiceDate": "2025-03-01T00:00:00.000Z",
      "DueDate": "2025-04-01T00:00:00.000Z",
      "Terms": "Net 30",
      "TermID": 5,
      "LastEditTime": "2025-03-02T10:00:00.000Z",
      "LastCalcTime": "2025-03-02T10:00:00.000Z",
      "TimeUpdated": "2025-03-02T10:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /purchases/:purchaseID

Doc anchor: [`#get-purchases--purchaseID`](https://kssdata.com/docs/v1#get-purchases--purchaseID)

**Badges:** Not available to Customer keys

Returns a single purchase order by ID.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `purchaseID` | path | `number` | required | The ID of the purchase to retrieve. |

### Example Response

**json**

```json
{
  "Data": [
    {
      "PurchaseID": 10001,
      "ReceiveDate": "2025-03-01T00:00:00.000Z",
      "ShipmentNum": "SHP-2025-001",
      "ShipmentID": 5001,
      "ToLocationID": 3,
      "ToLocationName": "Main Warehouse",
      "VendorName": "Acme Distributing",
      "VendorID": 42,
      "PostDate": "2025-03-01T00:00:00.000Z",
      "Status": "Received",
      "PONum": "PO-2025-0123",
      "Freight": "150.00",
      "Tax": "0.00",
      "OtherCost": "0.00",
      "Total": "4500.00",
      "TotalCases": "30",
      "PublicPDFLink": null,
      "Memo": null,
      "InvoiceDate": "2025-03-01T00:00:00.000Z",
      "DueDate": "2025-04-01T00:00:00.000Z",
      "Terms": "Net 30",
      "TermID": 5,
      "LastEditTime": "2025-03-02T10:00:00.000Z",
      "LastCalcTime": "2025-03-02T10:00:00.000Z",
      "TimeUpdated": "2025-03-02T10:00:00.000Z"
    }
  ]
}
```
