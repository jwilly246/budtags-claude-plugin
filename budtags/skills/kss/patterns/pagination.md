# Pagination

> Verbatim transcription of [https://kssdata.com/docs/v1#pagination](https://kssdata.com/docs/v1#pagination) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.

All list endpoints support pagination via **`Page`** and **`PageSize`** query parameters. The default page size is **50**. The maximum page size is **500**.

Paginated responses wrap results in a `Data` array alongside `Page` and `PageSize` fields. A **`HasNextPage`** boolean indicates whether more results exist beyond the current page.

**example request**

```bash
GET /api/{{version}}/products?States=CA&Page=2&PageSize=100
```

**json**

```json
{
  "Data": [ ... ],
  "Page": 2,
  "PageSize": 100,
  "HasNextPage": true
}
```
