# States

> Verbatim transcription of [https://kssdata.com/docs/v1#group-states](https://kssdata.com/docs/v1#group-states) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /states

Doc anchor: [`#get-states`](https://kssdata.com/docs/v1#get-states)

**Badges:** Paginated

Returns the active states available to your API key.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "StateAbbreviation": "CA",
      "StateName": "California",
      "OrderCutOffTime": "2:30 PM",
      "TimeZone": "America/Los_Angeles",
      "OrderCutOffDaysInAdvance": "1",
      "TimeUpdated": "2025-12-30T18:28:17.710Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```
