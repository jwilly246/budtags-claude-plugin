# Rate Limiting

> Verbatim transcription of [https://kssdata.com/docs/v1#rate-limiting](https://kssdata.com/docs/v1#rate-limiting) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.

Rate limits are enforced per API key. Each key has a configurable maximum requests per hour. When the limit is reached, the API returns `429 Too Many Requests`.

Every response reports your current standing so you can pace requests before you are throttled:

| Name | Description |
|---|---|
| **`RateLimit-Limit`** | The maximum number of requests allowed in the current window. |
| **`RateLimit-Remaining`** | Requests you have left before hitting the limit. `0` means the next request may be rejected. |
| **`RateLimit-Reset`** | Seconds until your remaining count recovers. |
| **`Retry-After`** | On a `429` only: seconds to wait before retrying. |

When you receive a `429`, wait the number of seconds given in `Retry-After` before sending another request rather than retrying immediately.

If you are building a sync process that requires high request volume, contact KSS to discuss your needs.

**response headers**

```bash
RateLimit-Limit: 1000
RateLimit-Remaining: 847
RateLimit-Reset: 2934
```

> ↻ **Use pagination and filtering.** Fetching only the data you need — by state, supplier, or customer — is the most effective way to reduce request volume.
