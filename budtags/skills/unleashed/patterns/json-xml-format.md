# Unleashed API Request/Response Formats

Content-Type and Accept header requirements for JSON and XML.

---

## Supported Formats

| Format | Content-Type | Accept |
|--------|-------------|--------|
| JSON (recommended) | `application/json` | `application/json` |
| XML (alternative) | `application/xml` | `application/xml` |

---

## Header Requirements

ALWAYS set both headers explicitly:

```php
$headers = [
    'Content-Type' => 'application/json',
    'Accept' => 'application/json',
    'api-auth-id' => $apiId,
    'api-auth-signature' => $signature,
];
```

---

## JSON Response Structure

Paginated endpoints return:

```json
{
  "Pagination": {
    "NumberOfItems": 50,
    "PageSize": 200,
    "PageNumber": 1,
    "NumberOfPages": 1
  },
  "Items": [
    {
      "Guid": "abc-123...",
      "Field": "value"
    }
  ]
}
```

Single resource endpoints return the object directly (no wrapper).

---

## JSON vs XML Field Name Differences

Some fields use different names in JSON vs XML:

| JSON | XML | Resource |
|------|-----|----------|
| `Identifier` | `SerialNumber` | Serial Numbers |
| `Number` | `BatchNumber` | Batch Numbers |

When using JSON (recommended), use the JSON field names.

---

## Best Practices

- Always use JSON for BudTags integration
- Always set both Content-Type AND Accept to `application/json`
- Parse responses with `$response->json()` in Laravel
- Handle both paginated (with `Items` wrapper) and single-resource responses
