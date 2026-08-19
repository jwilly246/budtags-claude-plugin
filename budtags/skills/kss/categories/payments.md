# Payments

> Verbatim transcription of [https://kssdata.com/docs/v1#group-payments](https://kssdata.com/docs/v1#group-payments) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /payments/types

Doc anchor: [`#get-payments-types`](https://kssdata.com/docs/v1#get-payments-types)

**Badges:** Paginated

Returns the list of payment types. Optionally filter by PaymentTypeIDs or SupplierIDs.

> **Callout:** Each payment type is returned once per supplier in its product groups. Results default to active suppliers only; Employee keys may include inactive suppliers with the Active filter. Supplier keys only see rows for their authorized suppliers, plus the shared generic payment type (PaymentTypeID = -1).

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `PaymentTypeIDs` | query | `number[]` | optional | Comma-separated list of payment type IDs to filter by. |
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `Active` | query | `boolean[]` | optional | True or False flag for supplier status. Defaults to Active only; only Employee keys may override. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "PaymentTypeID": 3,
      "Name": "ACH",
      "SupplierID": null,
      "TimeCreated": "2025-01-01T00:00:00.000Z",
      "TimeUpdated": "2025-01-01T00:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /payments

Doc anchor: [`#get-payments`](https://kssdata.com/docs/v1#get-payments)

**Badges:** Paginated

Returns payments for an AR account, including payment type and available balance. AvailableBalance is the payment's remaining credit after confirmed applications and pending requests, and is never negative. A reversed payment can appear with a negative Amount and an AvailableBalance of 0.

> **Callout:** Customer keys only see payments for their authorized AR accounts. Supplier keys only see payments belonging to their authorized suppliers.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `ARAccountIDs` | query | `number[]` | optional | Comma-separated list of AR account IDs to filter by. |
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `PaymentTypeIDs` | query | `number[]` | optional | Comma-separated list of payment type IDs to filter by. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "PaymentID": 1,
      "PaymentInvoiceID": 90001,
      "PaymentInvoiceNum": "INV-PAY-0001",
      "ARAccountID": 123,
      "PaymentTypeID": 3,
      "PaymentTypeName": "ACH",
      "Amount": "5000.000000",
      "SupplierID": null,
      "LoadSheetStatusID": 7,
      "PostDate": "2025-03-01T00:00:00.000Z",
      "TimeCreated": "2025-03-01T08:00:00.000Z",
      "TimeUpdated": "2025-03-01T08:00:00.000Z",
      "ARNote": null,
      "Memo": "Check #12345",
      "AvailableBalance": "3500.000000"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /payments/openInvoices

Doc anchor: [`#get-payments-openInvoices`](https://kssdata.com/docs/v1#get-payments-openInvoices)

**Badges:** Paginated

Returns invoices with a non-zero open balance. Used to identify invoices eligible for payment allocation.

> **Callout:** Customer keys only see invoices for their authorized AR accounts; InvoiceTotal and OpenBalance reflect the entire invoice. Supplier keys only see invoices that contain their products; InvoiceTotal and OpenBalance reflect only the portion of the invoice attributable to the supplier, and OpenDebit / OpenCredit are not returned.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `ARAccountIDs` | query | `number[]` | optional | Comma-separated list of AR account IDs to filter by. |
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. Only meaningful for supplier keys; ignored for customer and employee keys. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "InvoiceID": 8001,
      "InvoiceNum": "INV-2025-0042",
      "CustomerID": 1,
      "ARAccountID": 123,
      "InvoiceTotal": "1200.00",
      "OpenDebit": "1200.00",
      "OpenCredit": "0.00",
      "OpenBalance": "1200.00",
      "CreditTermID": 5,
      "TermID": 5,
      "DueDate": "2025-04-01T00:00:00.000Z",
      "Date": "2025-03-01T00:00:00.000Z",
      "PONum": "PO-2025-001"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /payments/applications

Doc anchor: [`#get-payments-applications`](https://kssdata.com/docs/v1#get-payments-applications)

**Badges:** Paginated

Returns payment allocations and allocation requests, each with its current Status (Pending, Exported, Confirmed, or Rejected). Includes both API-initiated requests and allocations applied directly in Encompass.

> **Callout:** Customer keys only see allocations for their authorized AR accounts. Supplier keys only see allocations whose payment belongs to one of their authorized suppliers. RequestID is null for allocations applied directly in Encompass; PaymentApplicationID and TimeApplied are populated once a request has been confirmed.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `ARAccountIDs` | query | `number[]` | optional | Comma-separated list of AR account IDs to filter by. |
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by (matched against the supplier on the underlying payment). |
| `PaymentInvoiceNums` | query | `string[]` | optional | Comma-separated list of payment invoice numbers to filter by. |
| `TargetInvoiceNums` | query | `string[]` | optional | Comma-separated list of target invoice numbers to filter by. |
| `Statuses` | query | `string[]` | optional | Comma-separated list of statuses to filter by.<br>Values: `Pending` = Pending — queued for export to Encompass, `Exported` = Exported — sent to Encompass, awaiting confirmation, `Confirmed` = Confirmed — applied in Encompass, `Rejected` = Rejected — not confirmed within the timeout window |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "PaymentApplicationID": 5001,
      "RequestID": 1,
      "PaymentInvoiceNum": "INV-PAY-0001",
      "TargetInvoiceNum": "INV-2025-0042",
      "ARAccountID": 123,
      "Amount": "1200.00",
      "Status": "Confirmed",
      "RequestedByUserID": 501,
      "AppliedBy": "jsmith",
      "TimeRequested": "2025-03-08T09:00:00.000Z",
      "TimeExported": "2025-03-08T09:05:00.000Z",
      "TimeApplied": "2025-03-10T14:00:00.000Z",
      "TimeUpdated": "2025-03-10T14:00:00.000Z"
    },
    {
      "PaymentApplicationID": null,
      "RequestID": 2,
      "PaymentInvoiceNum": "INV-PAY-0002",
      "TargetInvoiceNum": "INV-2025-0099",
      "ARAccountID": 123,
      "Amount": "500.00",
      "Status": "Pending",
      "RequestedByUserID": 501,
      "AppliedBy": null,
      "TimeRequested": "2025-03-19T10:00:00.000Z",
      "TimeExported": null,
      "TimeApplied": null,
      "TimeUpdated": "2025-03-19T10:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## POST /payments/applications

Doc anchor: [`#post-payments-applications`](https://kssdata.com/docs/v1#post-payments-applications)

**Badges:** Not available to Supplier keys

Creates a payment allocation request. Validates the payment has sufficient available balance and the target invoice belongs to the same AR account. The request is queued as Pending and exported to Encompass on the next export run.

> **Callout:** Not available to supplier keys (returns 403). Customer keys may only request allocations against their authorized AR accounts.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `PaymentInvoiceNum` | query | `string` | required | The invoice number of the payment to allocate from. |
| `TargetInvoiceNum` | query | `string` | required | The invoice number to allocate the payment toward. |
| `ARAccountID` | query | `number` | required | The AR account ID both invoices belong to. |
| `Amount` | query | `number` | required | The dollar amount to allocate. Must be positive and not exceed the available balance. |

### Example Response

**json**

```json
{
  "Data": {
    "RequestID": 2,
    "PaymentInvoiceNum": "INV-PAY-0001",
    "TargetInvoiceNum": "INV-2025-0042",
    "ARAccountID": 123,
    "Amount": "500.00",
    "Status": "Pending",
    "RequestedByUserID": 501,
    "TimeRequested": "2025-03-19T10:00:00.000Z",
    "TimeExported": null,
    "TimeConfirmed": null,
    "MatchedPaymentApplicationID": null,
    "TimeUpdated": "2025-03-19T10:00:00.000Z"
  }
}
```
