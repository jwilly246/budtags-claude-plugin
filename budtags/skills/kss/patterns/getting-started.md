# Getting Started

> Verbatim transcription of [https://kssdata.com/docs/v1#overview](https://kssdata.com/docs/v1#overview) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.

The KSS API provides programmatic access to product catalog, inventory, customer, invoice, and pricing data. All requests are made over HTTPS and return JSON responses.

There are two environments, each backed by its own isolated database and requiring a separate API key.

| Name | Value | Notes |
|---|---|---|
| **Production** | `api.kssdata.com` | Live data. Use production API keys only. Data is updated continuously |
| **Test** | `api.test.kssdata.com` | Safe for development and integration testing. Data is updated every Sunday morning |

> ⚠️ **API keys are environment-scoped.** A production key will be rejected by the test environment and vice versa. Never use production keys in development or CI pipelines.

All endpoints are versioned under `/api/v1`. A full request to the products endpoint looks like:

**https**

```bash
GET https://api.kssdata.com/api/{{version}}/products?States=CA&Statuses=1
x-api-key: your-api-key
```
