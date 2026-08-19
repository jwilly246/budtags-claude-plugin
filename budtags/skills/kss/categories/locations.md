# Locations

> Verbatim transcription of [https://kssdata.com/docs/v1#group-locations](https://kssdata.com/docs/v1#group-locations) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /locations

Doc anchor: [`#get-locations`](https://kssdata.com/docs/v1#get-locations)

**Badges:** Paginated

Returns warehouse and distribution locations filtered by state and location ID.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `LocationIDs` | query | `number[]` | optional | Comma-separated list of location IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "LocationID": 1,
      "Location": "Alameda",
      "DBA": "Kiva Sales & Service",
      "Address": "2300 N Loop Rd",
      "Address2": null,
      "Address3": "N/A",
      "City": "Alameda",
      "State": "CA",
      "PostalCode": "94502",
      "TimeUpdated": "2024-09-23T19:05:39.984Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /locations/:locationID

Doc anchor: [`#get-locations--locationID`](https://kssdata.com/docs/v1#get-locations--locationID)

Returns a single location by ID.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `locationID` | path | `number` | required | The ID of the location to retrieve. |

### Example Response

**json**

```json
{
  "Data": [
    {
      "LocationID": 1,
      "Location": "Alameda",
      "DBA": "Kiva Sales & Service",
      "Address": "2300 N Loop Rd",
      "Address2": null,
      "Address3": "N/A",
      "City": "Alameda",
      "State": "CA",
      "PostalCode": "94502",
      "TimeUpdated": "2024-09-23T19:05:39.984Z"
    }
  ]
}
```
