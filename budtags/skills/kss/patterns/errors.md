# Errors

> Verbatim transcription of [https://kssdata.com/docs/v1#errors](https://kssdata.com/docs/v1#errors) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.

The API uses standard HTTP status codes. Error responses include a JSON body with an `error` field describing the issue.

| Name | Description |
|---|---|
| **`400 Bad Request`** | Missing or invalid parameter. |
| **`401 Unauthorized`** | Missing or invalid API key. |
| **`403 Forbidden`** | Your key does not have access to this resource. |
| **`404 Not Found`** | The endpoint does not exist. |
| **`429 Too Many Requests`** | Rate limit exceeded. |
| **`500 Server Error`** | Unexpected server error. Contact KSS support. |

**error response**

```json
{
  "Error": "InvoiceIDs parameter is required"
}
```
