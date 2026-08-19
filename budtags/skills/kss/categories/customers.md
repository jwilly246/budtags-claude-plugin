# Customers

> Verbatim transcription of [https://kssdata.com/docs/v1#group-customers](https://kssdata.com/docs/v1#group-customers) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /customers

Doc anchor: [`#get-customers`](https://kssdata.com/docs/v1#get-customers)

**Badges:** Paginated

Returns a list of customers filtered by state, customer ID, and account status.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `CustomerIDs` | query | `number[]` | optional | Comma-separated list of customer IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |
| `AccountStatuses` | query | `string[]` | optional | Comma-separated list of account statuses to filter by. Defaults to Active.<br>Values: `Active` = Active, `Inactive` = Inactive, `OutOfBus` = Out of Business |
| `OnHold` | query | `string` | optional | Filter by on hold status. Pass "true" to return only customers on hold, "false" to exclude them. When omitted, on hold status is not filtered.<br>Values: `true` = On Hold, `false` = Not On Hold |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "CustomerID": 1,
      "CustomerName": "Kettles Secret Stash",
      "CustomerNameAlt": "Kettles",
      "ChainName": "Kettles Chain",
      "LicenseNum": "C10-0000001-LIC",
      "Address": "123 Main St, Los Angeles, CA 90001",
      "LocationID": 3,
      "OnHold": false,
      "SalesRepEmail": "jane.smith@example.com",
      "SalesRepName": "Jane Smith",
      "SalesRepPhone": "555-555-0100",
      "SalesRepUserID": 9240,
      "ProfilePictureURL": "https://cdn.e8.co/Kiva/S3UserAvatar/example.jpg",
      "CollectionAgentFullName": null,
      "CollectionAgentEmail": null,
      "State": "CA",
      "DeliveryDays": "1",
      "NextDeliveryDates": "2026-01-05;2026-01-12;2026-01-19;2026-01-26",
      "AccountStatus": "Active",
      "DeliveryDates": [
        "2026-01-05",
        "2026-01-12",
        "2026-01-19",
        "2026-01-26"
      ],
      "DeliveryMinimum": 500,
      "TimeUpdated": "2025-01-15T10:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /customers/creditTerms

Doc anchor: [`#get-customers-creditTerms`](https://kssdata.com/docs/v1#get-customers-creditTerms)

**Badges:** Paginated

Returns the credit terms negotiated between each customer and supplier pair.

> **Callout:** Customer keys only see rows for their authorized customers. Supplier keys only see rows for their authorized suppliers.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `CustomerIDs` | query | `number[]` | optional | Comma-separated list of customer IDs to filter by. |
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "CustomerID": 1,
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

## GET /customers/:customerID

Doc anchor: [`#get-customers--customerID`](https://kssdata.com/docs/v1#get-customers--customerID)

Returns a single customer by ID.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `customerID` | path | `number` | required | The ID of the customer to retrieve. |

### Example Response

**json**

```json
{
  "Data": [
    {
      "CustomerID": 1,
      "CustomerName": "Kettles Secret Stash",
      "CustomerNameAlt": "Kettles",
      "ChainName": "Kettles Chain",
      "LicenseNum": "C10-0000001-LIC",
      "Address": "123 Main St, Los Angeles, CA 90001",
      "LocationID": 3,
      "OnHold": false,
      "SalesRepEmail": "jane.smith@example.com",
      "SalesRepName": "Jane Smith",
      "SalesRepPhone": "555-555-0100",
      "SalesRepUserID": 9240,
      "ProfilePictureURL": "https://cdn.e8.co/Kiva/S3UserAvatar/example.jpg",
      "CollectionAgentFullName": null,
      "CollectionAgentEmail": null,
      "State": "CA",
      "DeliveryDays": "1",
      "NextDeliveryDates": "2026-01-05;2026-01-12;2026-01-19;2026-01-26",
      "AccountStatus": "Active",
      "DeliveryDates": [
        "2026-01-05",
        "2026-01-12",
        "2026-01-19",
        "2026-01-26"
      ],
      "DeliveryMinimum": 500,
      "TimeUpdated": "2025-01-15T10:00:00.000Z"
    }
  ]
}
```

---

## GET /deliveryDays

Doc anchor: [`#get-deliveryDays`](https://kssdata.com/docs/v1#get-deliveryDays)

**Badges:** Paginated

Returns delivery day schedules for active customers.

> **Callout:** 'DeliveryDays' is the day of the week the customer is delivered on. 1 = Monday, 7 = Sunday

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `CustomerIDs` | query | `number[]` | optional | Comma-separated list of customer IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "CustomerID": 1,
      "DeliveryDays": "3",
      "DeliveryDates": [
        "2026-02-04",
        "2026-02-11",
        "2026-02-18",
        "2026-02-25"
      ]
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```
