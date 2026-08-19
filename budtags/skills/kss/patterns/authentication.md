# Authentication

> Verbatim transcription of [https://kssdata.com/docs/v1#authentication](https://kssdata.com/docs/v1#authentication) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.

Every request must include your API key in the **`x-api-key`** request header. Requests without a valid key return `401 Unauthorized`.

**http header**

```bash
x-api-key: your-api-key
```

### Key Types

**Employee** — Full access to all endpoints and all data across any state or customer.

**Customer** — Access is scoped to the customer accounts associated with the key. Requests for data outside that scope are silently filtered or return `403`.

**Supplier** — Access is scoped to the supplier accounts associated with the key. Some endpoints are unavailable to Supplier keys entirely, noted per endpoint below.
