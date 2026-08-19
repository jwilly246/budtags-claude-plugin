# Invoices

> Verbatim transcription of [https://kssdata.com/docs/v1#group-invoices](https://kssdata.com/docs/v1#group-invoices) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /invoices

Doc anchor: [`#get-invoices`](https://kssdata.com/docs/v1#get-invoices)

**Badges:** Paginated

Returns invoices filtered by customer, status, date range, and state.

> **Callout:** Defaults to returning only New (1) status invoices if the 'Statuses' parameter is not included

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `CustomerIDs` | query | `number[]` | optional | Comma-separated list of customer IDs to filter by. |
| `InvoiceIDs` | query | `number[]` | optional | Comma-separated list of invoice IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |
| `Statuses` | query | `number[]` | optional | Comma-separated list of invoice status IDs. Defaults to New (1).<br>Values: `1` = New, `2` = Locked for Routing, `3` = Loaded, `4` = Returned, `5` = Balanced, `7` = Verified |
| `StartDate` | query | `date` | optional | ISO 8601 date string. Returns invoices on or after this date. |
| `EndDate` | query | `date` | optional | ISO 8601 date string. Returns invoices on or before this date. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "InvoiceID": 9001,
      "CustomerID": 1,
      "CustomerName": "Acme Beverages",
      "InvoiceNum": "INV-2025-0001",
      "OpenDebit": "0.320000",
      "OpenCredit": "0.000000",
      "PONum": null,
      "PODate": null,
      "TermID": 3,
      "PDFURL": "https://example.com/api?APIKeyID=123456",
      "Memo": "This is a memo",
      "Date": "2026-02-10T07:00:00.000Z",
      "DueDate": "2026-03-11T06:00:00.000Z",
      "Status": 1,
      "InvoiceTotal": "1536.000000",
      "SubmittedByUserID": 856,
      "SubmittedByUserName": "John Doe",
      "SubmittedByUserEmail": "john.doe@example.com",
      "BuiltByUserID": 856,
      "BuiltByUserName": "Jane Smith",
      "BuiltByUserEmail": "jane.smith@example.com",
      "InvoiceTimeCreated": "2026-01-27T13:40:00.000Z",
      "InvoiceLastUpdated": "2026-01-27T13:40:00.000Z",
      "ARNote": null,
      "TotalNumUnits": "72",
      "TotalCases": "6.00",
      "TotalFullPrice": "1680.000000",
      "TotalExtPrice": "1536.000000",
      "TotalDiscount": "144.000000",
      "OpenBalance": "1536.000000"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /invoices/:invoiceID

Doc anchor: [`#get-invoices--invoiceID`](https://kssdata.com/docs/v1#get-invoices--invoiceID)

Returns a single invoice by ID.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `invoiceID` | path | `number` | required | The ID of the invoice to retrieve. |

### Example Response

**json**

```json
{
  "Data": [
    {
      "InvoiceID": 9001,
      "CustomerID": 1,
      "CustomerName": "Acme Beverages",
      "InvoiceNum": "INV-2025-0001",
      "OpenDebit": "0.320000",
      "OpenCredit": "0.000000",
      "PONum": null,
      "PODate": null,
      "TermID": 3,
      "PDFURL": "https://example.com/api?APIKeyID=123456",
      "Memo": "This is a memo",
      "Date": "2026-02-10T07:00:00.000Z",
      "DueDate": "2026-03-11T06:00:00.000Z",
      "Status": 1,
      "InvoiceTotal": "1536.000000",
      "SubmittedByUserID": 856,
      "SubmittedByUserName": "John Doe",
      "SubmittedByUserEmail": "john.doe@example.com",
      "BuiltByUserID": 856,
      "BuiltByUserName": "Jane Smith",
      "BuiltByUserEmail": "jane.smith@example.com",
      "InvoiceTimeCreated": "2026-01-27T13:40:00.000Z",
      "InvoiceLastUpdated": "2026-01-27T13:40:00.000Z",
      "TotalNumUnits": "72",
      "TotalCases": "6.00",
      "TotalFullPrice": "1680.000000",
      "TotalExtPrice": "1536.000000",
      "TotalDiscount": "144.000000",
      "OpenBalance": "1536.000000"
    }
  ]
}
```

---

## GET /invoiceTransactions

Doc anchor: [`#get-invoiceTransactions`](https://kssdata.com/docs/v1#get-invoiceTransactions)

**Badges:** Paginated

Returns line item transactions for the specified invoices. InvoiceIDs is required.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `InvoiceIDs` | query | `number[]` | required | Comma-separated list of invoice IDs to fetch transactions for. Returns 400 if not provided. |
| `Statuses` | query | `number[]` | optional | Comma-separated list of invoice status IDs. If provided and does not include Verified (7), verified invoices are excluded from results.<br>Values: `1` = New, `2` = Locked for Routing, `3` = Loaded, `4` = Returned, `5` = Balanced, `7` = Verified |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "InvoiceTransID": 20001,
      "InvoiceID": 9001,
      "CustomerID": 1,
      "ProductID": 171,
      "ProductName": "Terra Bites Milk Chocolate Blueberries",
      "Cases": "1.00",
      "NumUnits": 20,
      "Ordered": 20,
      "BackOrder": 0,
      "FullPrice": "11.000000",
      "Discount": "2.250000",
      "UnitPrice": "8.750000",
      "ExtPrice": "175.000000",
      "TimeUpdated": "2024-09-23T19:05:39.984Z",
      "SupplierID": 5,
      "PromotionID": 5571,
      "BatchCode": "BATCH-2025-01",
      "COA_URL": "https://cdn.example.com/coa/batch-2025-001.pdf"
    },
    {
      "InvoiceTransID": 20002,
      "InvoiceID": 9001,
      "ProductID": 736,
      "ProductName": "Camino Gummies Wild Cherry",
      "Cases": "1.00",
      "NumUnits": 20,
      "Ordered": 20,
      "BackOrder": 0,
      "FullPrice": "11.000000",
      "Discount": "0.000000",
      "UnitPrice": "11.000000",
      "ExtPrice": "220.000000",
      "TimeUpdated": "2024-09-23T19:05:39.984Z",
      "SupplierID": 5,
      "PromotionID": null,
      "BatchCode": "BATCH-2025-002",
      "COA_URL": null
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /invoiceTransactions/:invoiceID

Doc anchor: [`#get-invoiceTransactions--invoiceID`](https://kssdata.com/docs/v1#get-invoiceTransactions--invoiceID)

**Badges:** Paginated

Returns line item transactions for a single invoice by ID.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `invoiceID` | path | `number` | required | The ID of the invoice to fetch transactions for. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "InvoiceTransID": 20001,
      "InvoiceID": 9001,
      "CustomerID": 1,
      "ProductID": 171,
      "ProductName": "Terra Bites Milk Chocolate Blueberries",
      "Cases": "1.00",
      "NumUnits": 20,
      "Ordered": 20,
      "BackOrder": 0,
      "FullPrice": "11.000000",
      "Discount": "2.250000",
      "UnitPrice": "8.750000",
      "ExtPrice": "175.000000",
      "TimeUpdated": "2024-09-23T19:05:39.984Z",
      "SupplierID": 5,
      "PromotionID": 5571,
      "BatchCode": "BATCH-2025-01",
      "COA_URL": "https://cdn.example.com/coa/batch-2025-001.pdf"
    },
    {
      "InvoiceTransID": 20002,
      "InvoiceID": 9001,
      "ProductID": 736,
      "ProductName": "Camino Gummies Wild Cherry",
      "Cases": "1.00",
      "NumUnits": 20,
      "Ordered": 20,
      "BackOrder": 0,
      "FullPrice": "11.000000",
      "Discount": "0.000000",
      "UnitPrice": "11.000000",
      "ExtPrice": "220.000000",
      "TimeUpdated": "2024-09-23T19:05:39.984Z",
      "SupplierID": 5,
      "PromotionID": null,
      "BatchCode": "BATCH-2025-002",
      "COA_URL": null
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /invoiceCOAs

Doc anchor: [`#get-invoiceCOAs`](https://kssdata.com/docs/v1#get-invoiceCOAs)

**Badges:** Paginated

Returns certificate of analysis records for the specified invoices. InvoiceIDs is required.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `InvoiceIDs` | query | `number[]` | required | Comma-separated list of invoice IDs to fetch COAs for. Returns 400 if not provided. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "InvoiceID": 9001,
      "ProductID": 160,
      "InvoiceTransID": 20001,
      "BatchCode": "BATCH-2025-001",
      "COA_URL": "https://cdn.example.com/coa/batch-2025-001.pdf",
      "TimeUpdated": "2025-01-10T14:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /invoiceCOAs/:invoiceID

Doc anchor: [`#get-invoiceCOAs--invoiceID`](https://kssdata.com/docs/v1#get-invoiceCOAs--invoiceID)

**Badges:** Paginated

Returns certificate of analysis records for a single invoice by ID.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `invoiceID` | path | `number` | required | The ID of the invoice to fetch COAs for. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "InvoiceID": 9001,
      "ProductID": 160,
      "InvoiceTransID": 20001,
      "BatchCode": "BATCH-2025-001",
      "COA_URL": "https://cdn.example.com/coa/batch-2025-001.pdf",
      "TimeUpdated": "2025-01-10T14:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /invoices/creditTerms

Doc anchor: [`#get-invoices-creditTerms`](https://kssdata.com/docs/v1#get-invoices-creditTerms)

**Badges:** Paginated

Returns the catalog of credit terms (Net 30, Net 60, etc.) used on invoices.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `TermIDs` | query | `number[]` | optional | Comma-separated list of term IDs to filter by. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "TermID": 3,
      "Term": "Net 30",
      "DaysOfCredit": 30,
      "AccountOnHold": false,
      "TimeUpdated": "2025-01-01T00:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```
