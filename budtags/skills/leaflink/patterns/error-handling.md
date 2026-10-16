# LeafLink Error Handling

HTTP status codes, real error bodies, and safe retry rules for LeafLink Marketplace V2 API.

Lines marked "verified 2026-10-16 (sandbox, file)" cite raw files in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/`. Full evidence list: `verified-behavior.md`.

---

## HTTP Status Codes

| Code | Meaning | Common Causes | Action |
|------|---------|---------------|--------|
| **200** | OK | Successful GET/PATCH. **Also returned when a filter or field was silently ignored** | Read back what you wrote |
| **201** | Created | Successful POST | Save the returned id/number before anything else |
| **204** | No Content | Successful DELETE | - |
| **400** | Bad Request | Validation errors, forbidden fields, wrong state, `limit` > 500 | Do not retry; fix the body |
| **401** | Unauthorized | Missing/invalid API key | Verify key and `App ` header |
| **403** | Forbidden | No permission for the resource | Check company context and key permissions |
| **404** | Not Found | Id doesn't exist, isn't yours, or was deleted | `{"detail": "No OrderedProduct matches the given query."}` after a line DELETE (sandbox, r3_c_line_delete.txt) |
| **429** | Too Many Requests | Over 300/min (burst 1000/min) per key owner (docs) | Back off; no rate-limit headers are sent to warn you (sandbox, r2_t8_t9_console.txt) |
| **500 / 503 / 504** | Server / gateway error | LeafLink or CloudFront. The sandbox returned 504 (CloudFront, 180 s) on a list call and 503 "upstream connect error" (sandbox, logs/requests.jsonl, r3_a_param_sweep.txt) | Retry GETs only |

**A 200 is not proof a write landed.** `sales_reps` on an order PATCH returned 200 and stayed `[]`; `ein` on a customer PATCH returned 200 and stayed `null` (sandbox, r2_t11_order_create_shape.txt, g_customers.txt). Read the field back.

---

## Common Errors

### 1. Missing Trailing Slash

```
400 Bad Request: "Request path must end in a slash"
```

```php
// ❌ Wrong
$api->get('/orders-received');

// ✅ Correct
$api->get('/orders-received/');
```

### 2. A filter that does nothing (no error at all)

An unknown or unsupported filter returns **200 with the whole list**, not a 400. Example: `/orders-received/?customer_id=2209363` and `/customers/?license_number__in=...` returned every row (sandbox, r3_a_param_sweep.txt). Check `filtering.md` before trusting a filter.

### 3. Wrong value types

Real 400s, verified 2026-10-16 (sandbox):

| Request | Error | File |
|---------|-------|------|
| `unit_denomination: "Gram"` or `"28"` | `{"unit_denomination": ["Value must be id of an existing UnitDenomination."]}` | w_c_units.txt |
| `tax_type: "$"` | `{"tax_amount": ["Fixed ($) tax amounts are not supported. Send tax_type \"%\" with a rate between 0 and 1."]}` | w_d_discount_tax.txt |
| `tax_amount: 24` | `{"tax_amount": ["Tax rate must be between 0 and 1"]}` | w_d_discount_tax.txt |
| `sale_price: null` | `{"sale_price": ["This field may not be null."]}` | w_a_sale_price.txt |
| `on_sale: false` | `{"non_field_errors": "Forbidden fields in update operation: on_sale"}` | w_a_sale_price.txt |
| `paid: true` | `{"non_field_errors": "Forbidden fields in update operation: {'paid'}"}` | w_e_payments.txt |
| `paid_date` as datetime | `{"paid_date": ["Date has wrong format. Use one of these formats instead: MM/DD/YYYY, YYYY-MM-DD."]}` | w_e_payments.txt |
| payment over balance | `{"non_field_errors": "You cannot overpay for an invoice."}` | w_e_payments.txt |
| `line_items: []` | `{"line_items": {"non_field_errors": ["This list may not be empty."]}}` | r2_t1_line_semantics.txt |
| nested order PATCH on Cancelled/Rejected | `{"non_field_errors": "Order cannot be edited."}` | r2_t7_sale_clear.txt |
| reject a Complete order | `["Cannot perform reject action on an order in complete state."]` | r2_t15_transitions.txt |
| `shipping_details: ""` | `{"shipping_details": ["This field may not be blank."]}` | r3_b_shipping_details.txt |
| product create without `maximum_order` | `{"maximum_order": ["This field is required."]}` | r2_t5_max_order.txt |
| sub-category from another category | `{"sub_category": "Subcategory does not belong to category"}` | r2_t6_category_pair.txt |
| contact `phone: "(313) 555-0100"` | `{"phone": ["Phone number must consist of 10 digits."]}` | r2_t12_contact_patch.txt |
| contact `first_name` > 30 chars | `{"first_name": ["Ensure this field has no more than 30 characters."]}` | r2_t12_contact_patch.txt |
| `/orders-received/?fields_include=id` | `{"non_field_errors": "Fields `id` do not exist on this endpoint."}` | logs/requests.jsonl |
| `limit=1000` | 400 | r2_t9_pagination.txt |

### 4. Authentication Errors

```php
$headers = [
    'Authorization' => 'App ' . $apiKey,  // 'App ' prefix, not 'Bearer '
    'Accept' => 'application/json',
];
```

### 5. Permission / Company Context

```php
// /companies/ lists the key's company; seller and buyer are booleans (there is no company_type)
$company = $api->get('/companies/')->json('results.0');

if ($company['seller']) {
    $orders = $api->get('/orders-received/');
}
```

`GET /companies/` returned `"buyer": false, "seller": true` for Evo (sandbox, logs/requests.jsonl).

---

## Error Response Format

Error bodies are NOT one shape. Parse all of these (sandbox, files in the table above):

```json
{"detail": "No OrderedProduct matches the given query."}
{"unit_denomination": ["Value must be id of an existing UnitDenomination."]}
{"sub_category": "Subcategory does not belong to category"}
{"non_field_errors": "Forbidden fields in update operation: on_sale"}
{"line_items": {"non_field_errors": ["This list may not be empty."]}}
["Cannot perform reject action on an order in complete state."]
```

A field value can be a list or a plain string, can be nested, and the whole body can be a top-level array. Gateway errors (504) are HTML, not JSON.

---

## Retry Strategies

### The rule: retry GETs, never blind-retry writes

- **GET**: retry on 429, 5xx and transport errors with backoff and a max attempt count.
- **POST / PATCH that create things: NEVER auto-retry on a timeout or 5xx.** LeafLink has no idempotency keys (spec), and the sandbox proved:
  - the same payment body POSTed twice = two payments (sandbox, w_e_payments.txt E2)
  - an order PATCH line without `id` adds a new line every time (sandbox, r2_t1_line_semantics.txt T1.b)
- Before re-sending a create, **read back by a natural key**: order by `external_id_seller`, payments via `GET /orders-received/{number}/payments/`, lines by product + quantity on the order.
- 429: back off and retry (the request was rejected, nothing was written). Honour `Retry-After` if present; LeafLink sends no rate-limit headers before you hit the limit.

```php
public function get(string $url, array $params = [], int $retries = 3)
{
    for ($attempt = 0; ; $attempt++) {
        try {
            $response = Http::withHeaders($this->headers())->get($this->url($url), $params);
        } catch (ConnectionException $e) {
            if ($attempt >= $retries) {
                throw $e;
            }
            sleep(2 ** ($attempt + 1));
            continue;
        }

        if (($response->status() === 429 || $response->serverError()) && $attempt < $retries) {
            sleep((int) ($response->header('Retry-After') ?: 2 ** ($attempt + 1)));
            continue;
        }

        return $response;
    }
}

// Writes: one attempt; on timeout, read back before deciding to send again
public function post(string $url, array $body)
{
    return Http::withHeaders($this->headers())->post($this->url($url), $body);
}
```

---

## Best Practices

### ✅ Do:

1. Read back every write that matters (status, money, `listing_state`, `sales_reps`)
2. Save a created id (order `number`, line `id`, payment `id`) before the next call
3. Log status, URL and body (never the key)
4. Parse string, list, nested and top-level-array error bodies
5. Retry GETs with backoff and a cap

### ❌ Don't:

1. Auto-retry POST/PATCH that create orders, lines, payments, strains or product lines
2. Treat 200 as "applied"
3. Expose API keys in errors or logs
4. Retry 400s

---

## Debugging Checklist

1. ✅ **Trailing slash** on every path
2. ✅ **API key** valid, `App ` prefix
3. ✅ **Company context** (`seller` / `buyer` booleans)
4. ✅ **Filter honoured?** (`filtering.md`)
5. ✅ **Field types**: `unit_denomination` id, `tax_amount`/`discount` 0-1 fractions, money objects, `paid_date` plain date
6. ✅ **Order status** allows the edit (nested PATCH refused on Cancelled/Rejected)
7. ✅ **Read back** after a 200

---

## Quick Reference

```php
$status = $response->status();
$body = $response->json();          // may be an array at top level
$detail = $response->json('detail') ?? $response->json('non_field_errors');

'/orders-received/'                 // trailing /
'created_on__gte'                   // real date filter (not created_date)
'2026-10-16T17:00:00Z'              // day-only datetime fields
'App ' . $apiKey                    // auth header
```
