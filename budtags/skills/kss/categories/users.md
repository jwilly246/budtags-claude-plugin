# Users

> Verbatim transcription of [https://kssdata.com/docs/v1#group-users](https://kssdata.com/docs/v1#group-users) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /users

Doc anchor: [`#get-users`](https://kssdata.com/docs/v1#get-users)

**Badges:** Paginated

Returns users filtered by state, role, customer ID, and supplier ID. Supplier API keys return their own Supplier users and active Customer users. Customer API keys only return their own Customer users.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `UserIDs` | query | `number[]` | optional | Comma-separated list of user IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |
| `CustomerIDs` | query | `number[]` | optional | Comma-separated list of customer IDs to filter by. |
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `Roles` | query | `string[]` | optional | Comma-separated list of roles to filter by.<br>Values: `Customer` = Customer, `Supplier` = Supplier, `Admin` = Admin, `DistributorRep` = Distributor Rep |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |
| `Active` | query | `boolean[]` | optional | True or False flag for user status. Defaults to Active = true only for Customer and Supplier keys |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "UserID": 501,
      "SiteUserID": 1001,
      "UserActive": true,
      "KSSLiveAccess": true,
      "Email": "buyer@example.com",
      "States": [
        "CA"
      ],
      "Role": "Customer",
      "CustomerIDs": [
        1
      ],
      "SupplierIDs": null,
      "LocationIDs": [
        3
      ],
      "PowerUser": false,
      "JobTitle": null,
      "Department": null,
      "FullName": "Jane Buyer"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /users/:userID

Doc anchor: [`#get-users--userID`](https://kssdata.com/docs/v1#get-users--userID)

Returns a single user by ID.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `userID` | path | `number` | required | The ID of the user to retrieve. |

### Example Response

**json**

```json
{
  "Data": [
    {
      "UserID": 501,
      "SiteUserID": 1001,
      "UserActive": true,
      "KSSLiveAccess": true,
      "Email": "buyer@example.com",
      "States": [
        "CA"
      ],
      "Role": "Customer",
      "CustomerIDs": [
        1
      ],
      "SupplierIDs": null,
      "LocationIDs": [
        3
      ],
      "PowerUser": false,
      "JobTitle": null,
      "Department": null,
      "FullName": "Jane Buyer"
    }
  ]
}
```
