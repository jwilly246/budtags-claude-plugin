# Vendors

> Verbatim transcription of [https://kssdata.com/docs/v1#group-vendors](https://kssdata.com/docs/v1#group-vendors) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /vendors

Doc anchor: [`#get-vendors`](https://kssdata.com/docs/v1#get-vendors)

**Badges:** Not available to Customer keys · Paginated

Returns the vendors a supplier ships from for each warehouse location, including address, lead time, and DOI targets.

> **Callout:** Not available to customer keys (returns 403). Supplier keys only see vendors for their authorized suppliers. Inactive vendors are hidden unless an Employee key explicitly requests them via Active=false.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `LocationIDs` | query | `number[]` | optional | Comma-separated list of destination location IDs to filter by. |
| `VendorIDs` | query | `number[]` | optional | Comma-separated list of vendor IDs to filter by. |
| `Active` | query | `boolean[]` | optional | True or False flag for vendor status. Defaults to Active = true; only Employee keys may request inactive vendors. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "SupplierID": 5,
      "LocationID": 3,
      "VendorID": 42,
      "VendorName": "Acme Distributing",
      "VendorLicenseNumber": "C11-0000042-LIC",
      "VendorAddress": "500 Industrial Way",
      "VendorAddress2": null,
      "VendorCity": "Oakland",
      "VendorState": "CA",
      "VendorPostalCode": "94607",
      "LeadTimeDays": 5,
      "TargetDOI": 14,
      "MaxDOI": 30,
      "PickupDates": [
        "Mon",
        "Wed",
        "Fri"
      ],
      "RequirePOBatchCodes": false,
      "Active": true,
      "TimeUpdated": "2025-01-15T10:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```
