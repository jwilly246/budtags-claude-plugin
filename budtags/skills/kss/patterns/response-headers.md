# Response Headers

> Verbatim transcription of [https://kssdata.com/docs/v1#response-headers](https://kssdata.com/docs/v1#response-headers) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.

Alongside the rate limit headers, every response includes the following.

### Request tracing

Each response carries an **`X-Request-Id`** header uniquely identifying that request. Include this value when contacting KSS support so we can locate the exact request in our logs.

If you send your own `X-Request-Id` on a request, we echo it back unchanged (when it is a short alphanumeric token), letting you correlate a request across your systems and ours.

### Conditional requests

Responses include an **`ETag`** validator. To avoid re-downloading data that has not changed, send the ETag from a previous response back on your next request using the **`If-None-Match`** header. If the data is unchanged, the API returns `304 Not Modified` with an empty body; otherwise it returns the full response with a new ETag.

Responses are marked `private` and must not be shared between different API keys in a downstream cache.

**conditional request**

```bash
GET /api/{{version}}/products?States=CA
x-api-key: your-api-key
If-None-Match: W/"a1b2c3d4e5f6..."
```
