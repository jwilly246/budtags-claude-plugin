# LeafLink Verified Behavior (sandbox, 2026-10-16)

What LeafLink actually does on writes and list reads, proven by live calls against `sandbox.leaflink.com` on 2026-10-16 (three rounds, Evo seller 11992, own test customers/listings only).

**This file wins.** If another file in this skill disagrees with a line here, this file is right and the other line is stale.

**Evidence.** Every behavioural line cites its raw file in brackets.
- `[name.txt]` = `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/name.txt`
- `[probe/name]` = `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/webhook_probe/name`
- `[log]` = `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/logs/requests.jsonl`
- `[spec]` = official OpenAPI `~/budtags-audits/2026-10-15/leaflink_docs_gap_audit/official_openapi.json`; `[doc:file]` = official doc text in `.../leaflink_docs_gap_audit/text/file`

---

## The sandbox itself

- **A clone of prod.** "This environment uses a clone of live LeafLink data and code, updated and reset nightly at 12:00am EST." [doc:gs.txt] Real buyers are in it, so test against your own test customer.
- **It did NOT reset on the night of 10-15/16.** Customer 2209361 (created 04:51Z on 10-16, before the documented 05:00Z reset) was still listed at 15:02Z [r2_setup.txt, r3_a_param_sweep.txt `customers id__in` row]. Never count on the nightly wipe: archive your test listings and customers, delete test contacts.
- **It sends NO webhooks to the prod receiver.** Positive control: a prod `PATCH products/843545/` at 00:20:29 EDT reached the prod receiver 16 s later (row 43973) [probe/prod_control_ledger.jsonl, probe/c1_control.txt]. 42 sandbox order writes 04:27-04:28Z produced no rows [w_order_write_times.txt, probe/w_watch_log.txt].
- **No webhook-registration API.** The spec has no webhook path [spec]. Subscriptions are made in the LeafLink UI (Settings > Developer Options) [doc:brands_webhooks_setup.txt].

---

## Products (listings)

### Unit fields

`unit_of_measure` and `unit_denomination` are **two separate fields**. Store both. Never send one without the other and the price/multiplier.

- **`unit_denomination` is written as a numeric id ONLY.** `"Gram"` and `"28"` both give 400 `"Value must be id of an existing UnitDenomination."`; `11` works [w_c_units.txt C1, C1b, C1c]. Reads return an object: `{"id": 11, "value": "28.00000", "name": "Twenty-Eight", "label": "28"}` [w_c_units.txt].
- **Id table** [spec ProductCreate/ProductUpdate]. Send `1` when nothing fits.

| id | label | id | label | id | label | id | label | id | label |
|----|-------|----|-------|----|-------|----|-------|----|-------|
| 1 | 1 | 6 | 2 | 11 | 28 | 16 | 3 3/4 | 21 | 1/5 |
| 2 | 1/2 | 7 | 3 1/2 | 12 | 5 1/4 | 17 | 1/10 | 22 | 1/3 |
| 3 | 1/4 | 8 | 7 | 13 | 4 | 18 | 6/5 | 23 | 1/6 |
| 4 | 1/8 | 9 | 14 | 14 | 2 1/2 | 19 | 3/2 | 24 | 3/10 |
| 5 | 3/4 | 10 | 6 | 15 | 8 | 20 | 2/10 | 25 | 4/10 |

- **`unit_of_measure`** enum: Milligram, Gram, Kilogram, Ounce, Pound, Unit, Liter, Milliliter [spec]. Release 2.27.0 says `Case` is no longer accepted, but the sandbox still accepted `unit_of_measure: "Case"` on create (201, stored "Case") [r2_t4_inventory_mgmt.txt T4z]. Never send it; sell cases with `sell_in_unit_of_measure: "Case"` + `unit_multiplier`.
- **PATCH is partial.** A price-only or quantity-only PATCH kept every unit field [w_c_units.txt C2, C3].
- **`unit_multiplier` is not reset when omitted** (stayed 28 through C2/C3) [w_c_units.txt].
- **Multiplier 1 alone keeps `sell_in_unit_of_measure: "Case"`** [w_c_units.txt C4]. Only `null` or `""` clears it (both read back `null`) [w_c_sellin_clear.txt].
- A failed (400) PATCH does not move `modified` [w_c_units.txt C1].

### Quantity counts listing units

`quantity`, `reserved_qty`, `available_inventory` and an order line's `quantity` all count **listing units**. One unit = denomination x `unit_of_measure` (Gram / id 11 reads `base_units_per_unit` "28", so 1 unit = 28 g). One case = `unit_multiplier` units; a line's `bulk_units` = quantity / multiplier [w_c_units.txt C0 readback, w_b_inventory.txt: Gram/28, multiplier 28, line quantity 28 = bulk_units 1, reserves 28]. Push the count of listing units, never raw Metrc grams.

### Lists replace

- **`strains` = whole-list replace.** `[a, b]` sets both, `[b]` leaves only b, omitted keeps the list, `[]` clears it [w_h_strains.txt H1-H5]. Send the full list every time or leave the key out.
- `product_data_items`: "The list in the request will replace any existing product data items." [spec ProductUpdate]

### Inventory and orders

| Order event | `quantity` | `reserved_qty` | Evidence |
|-------------|-----------|----------------|----------|
| Created as Submitted | no change | + line qty | [w_b_inventory.txt B1] |
| Accepted | no change | no change | [w_b_inventory.txt B2] |
| Fulfilled | - line qty | - line qty (released) | [w_b_inventory.txt B4, B8] |
| Shipped | no change | no change | [w_b_inventory.txt B5] |
| Rejected after Fulfilled | + line qty (given back) | no change | [w_b_inventory.txt B9] |

- `reserved_qty` equalled the sum of open Submitted/Accepted/Backorder line quantities on all 3,217 listings checked [r2_reserve.txt]. Matches the docs' event table [doc:brands_api_inventory.txt].
- A listing's `modified` did **not** move when orders changed its quantity or reservation [w_b_inventory.txt B0-B9]. It does move on API price and quantity edits, and so does `last_edit` [w_c_units.txt C2, C3; r2_t4_inventory_mgmt.txt T4y].
- `available_inventory` is writable: PATCH `{"available_inventory": 30}` with nothing reserved set `quantity` 30 [r2_t4_inventory_mgmt.txt T4x]. Spec: available = quantity - reserved_qty.
- **Unlimited (2) and Inherited (3) listings accept `quantity` and `available_inventory` PATCHes**; `inventory_management` stays as it was [r2_t4_inventory_mgmt.txt im2, im3].

### Thresholds flip `listing_state`

Fields: `threshold_value`, `threshold_action` (`internal` / `unavailable` / `backorder` / `default`), `reverse_threshold_value`, `reverse_threshold_action` (`available`), `low_inventory_alert_threshold`, `should_alert_on_low_inventory` [r2_t3_thresholds.txt, r3_g_threshold_response.txt].

- Quantity at or below `threshold_value` sets `listing_state` to the action (10 -> Internal; with `unavailable` -> Unavailable; with `backorder` -> Backorder). Above `reverse_threshold_value` sets Available (21 with reverse 20). In between, the state does not change. `default` = no flip [r2_t3_thresholds.txt].
- Thresholds beat a hand-set state in the same PATCH: `{"listing_state": "Internal", "quantity": "60"}` read back **Available** [r2_t3_thresholds.txt "hand-hide Internal + qty 60"].
- The PATCH response already shows the flipped state, and a later GET agrees [r3_g_threshold_response.txt]. Read `listing_state` from the response after every quantity push.

### Create rules

- **`maximum_order` key is required on create**: absent -> 400 `"This field is required."`; `null` is accepted [r2_t5_max_order.txt]. `"0"` is stored as 0.0000 and did **not** block a seller-created order [r2_t5_max_order.txt]; whether 0 blocks buyer checkout is untested. Send `null` when there is no maximum (docs suggest "100000" [spec]).
- **Category/sub-category mismatch -> 400** `"Subcategory does not belong to category"`, whether `sub_category` is sent alone or with a non-matching `category` [r2_t6_category_pair.txt].
- A listing under an inactive brand cannot be created non-archived: 400 `"This product must remain archived because the brand ... is not active."` [w_c_units.txt C0].
- Archive = PATCH `{"listing_state": "Archived"}` [w_cleanup.txt].

---

## Orders

### Money

- **Tax = rate x (line subtotal + SHIPPING), before discount.** One $300 line + $50 shipping at 0.24 -> tax 84; a 10% discount leaves tax at 84 [r2_t2_shipping_tax.txt T2.0, T2.1]. Shipping 100 -> tax 96 [T2.3].
- **Discount applies to the lines only, not shipping.** 300 x 0.9 + 50 + 84 = total 404 [r2_t2_shipping_tax.txt T2.1].
- **`tax_type` is `%` only, rate is a 0-1 fraction.** `"$"` -> 400 `"Fixed ($) tax amounts are not supported. Send tax_type "%" with a rate between 0 and 1."`; `24` -> 400 `"Tax rate must be between 0 and 1"` [w_d_discount_tax.txt D7, D9].
- **`discount_type: "%"` takes a 0-1 fraction.** 0.3 = 30% [D5]. `10` = 1000% (total -5256) [D1].
- **`discount_type` alone flips the meaning of the stored value.** `discount` 10 as `$` became 1000% after a PATCH of `{"discount_type": "%"}` only [w_d_discount_tax.txt D3, D4]. `discount` alone keeps the old type [D3]. Always send both together.
- `shipping_charge` accepts a money object or a bare number [r2_t2_shipping_tax.txt T2.3, T2.4].
- **Prices are per sold-in unit (per case when multiplier > 1).** Line quantity 28, multiplier 28, `ordered_unit_price` 300 -> line total 300; two lines -> 600 + 144 tax = 744 [w_b_inventory.txt B1].

### sale_price

- **Clear with `{"amount": "0.00", "currency": "USD"}`.** `null` -> 400 `"This field may not be null."`; `on_sale` -> 400 `"Forbidden fields in update operation: on_sale"` (read-only, derived from sale_price > 0) [w_a_sale_price.txt A1, A3, A4, A5].
- A line sent with `sale_price` = ordered price reads `on_sale: true` [w_b_inventory.txt B1 line 78323776]. Send 0 when the line is not on sale.
- **An on-sale line is billed at `sale_price` and ignores later `ordered_unit_price` edits**: ordered 330 / sale 300 still totals as 300 [w_a_sale_price.txt A6, A7].
- Clearing via `/line-items/{id}/` works on Accepted, Fulfilled, Shipped [w_a_sale_price.txt A1, A10, A12], Cancelled and Rejected [r2_t7_sale_clear.txt T7c, T7d], and does not change the total when sale = ordered.

### Line items

- **Order PATCH `line_items` is an UPSERT keyed by line `id`** [r2_t1_line_semantics.txt]:
  - key omitted -> lines untouched (T1.d)
  - entry with `id` -> that line updated (T1.e)
  - a subset of lines -> the other lines are KEPT (T1.a)
  - entry **without** `id` -> a NEW line is added, even for the same product (T1.b: duplicate, total up)
  - `[]` -> 400 `{"line_items": {"non_field_errors": ["This list may not be empty."]}}` (T1.c)
  - Save a new line's id before the next push; a retried create-line PATCH duplicates it.
- **Remove a line with `DELETE /line-items/{id}/`**: 204 on every status (Submitted, Accepted, Fulfilled, Shipped, Complete, Cancelled, Rejected); GET after -> 404 [r3_c_line_delete.txt]. The order total changes, even on Complete.
- **`/line-items/{id}/` PATCH works on every status** (above). **Nested order PATCH is refused on Cancelled and Rejected**: 400 `"Order cannot be edited."` [r2_t7_sale_clear.txt T7c, T7d]; it works on Submitted [T7a, T7b] and Shipped [w_a_nested_order_patch.txt].
- Order-level PATCHes (notes) work on Shipped [w_a_sale_price.txt A13].
- `is_sample: true` on a create line is kept [r2_t11_order_create_shape.txt].

### Other order fields

- `shipping_details`: `""` -> 400 `"This field may not be blank."`; `null` clears; omitted keeps it. `notes` / `internal_notes` accept `""` and `null` [r3_b_shipping_details.txt].
- `sales_reps` sent on create and on PATCH (`[{"id": n}]` or `[n]`) came back `[]` with a 200 [r2_t11_order_create_shape.txt T11.0, T11.2, T11.3]. Never trust the 200; read back.
- `selected_payment_option` `{"payment_term_id": 2, "payment_method_id": 4}` can be PATCHed after create [r2_t11_order_create_shape.txt T11.1].
- `external_id_seller` on create becomes the `short_id` [w_b_inventory.txt B1].
- `customer` on create accepts an id or `{"id": n}` [r2_t1_line_semantics.txt, r2_t11_order_create_shape.txt].

### Dates

LeafLink returns datetimes in Mountain time (`-06:00` / `-07:00`).

| Sent | Read back | Day |
|------|-----------|-----|
| `2026-10-20T17:00:00Z` | `2026-10-20T11:00:00-06:00` | right [w_f_dates.txt F1, F4] |
| `2026-10-21` (date only) | `2026-10-21T00:00:00-06:00` | right [F2, F5] |
| `2026-10-22T00:00:00-04:00` (midnight Detroit) | `2026-10-21T22:00:00-06:00` | **previous day** [F3] |

Send date-only fields (`ship_date`, `payment_due_date`) as `YYYY-MM-DDT17:00:00Z`. `paid_date` is a plain date: a datetime gives 400 `"Date has wrong format. Use one of these formats instead: MM/DD/YYYY, YYYY-MM-DD."` [w_e_payments.txt E3].

### Transitions

`POST /orders-received/{number}/transition/{accept|fulfill|ship|complete|reject|cancel}/`, no body.

| Status | `available_transitions` read back | Evidence |
|--------|------------------------------------|----------|
| Submitted | accepted, cancelled, rejected | [w_b_inventory.txt B1] |
| Accepted | fulfilled, rejected | [B2] |
| Fulfilled | shipped, accepted, rejected | [B8] |
| Shipped | complete, rejected, fulfilled | [w_b_inventory.txt B5, r3_i_reject_shipped_paid.txt] |
| Complete | shipped | [r3_c_line_delete.txt] |
| Cancelled, Rejected | (none) | [w_b_inventory.txt B9, r3_c_line_delete.txt] |

- **Shipped -> Rejected works** (200) [r2_t15_transitions.txt], also when partly or fully paid [r3_i_reject_shipped_paid.txt]. It **clears `ship_date` and `payment_due_date`**; `paid` and `payment_balance` stay as they were [r3_i_reject_shipped_paid.txt].
- **Complete -> Rejected = 400** `["Cannot perform reject action on an order in complete state."]` [r2_t15_transitions.txt].

### Payments

`POST /order-payments/` with `order`, `recorded_by`, `total` (money), `payment_date` (`T17:00:00Z`), `payment_type`, `reason` [w_e_payments.txt].

- **`paid` cannot be PATCHed**: 400 `"Forbidden fields in update operation: {'paid'}"` [w_e_payments.txt E3b].
- **A payment for the exact balance settles the order**: `paid` true, `paid_date` set, balance 0 [w_e_payments.txt E5].
- **Overpay -> 400** `"You cannot overpay for an invoice."` [w_e_payments.txt E4].
- **POST is NOT idempotent**: the same body twice = two payments (4537234, 4537235) [w_e_payments.txt E2]. Never auto-retry; read `/orders-received/{number}/payments/` first.
- **Payments are accepted on Cancelled and Rejected orders** (201) [r2_t15_transitions.txt]. Guard on our side.

---

## Customers

- **PATCH is partial**: a nickname-only PATCH kept every other field [g_customers.txt step 1].
- **Top-level `address` / `city` / `zipcode` overwrite BOTH `corporate_address` and `delivery_address`** [g_customers.txt step 2]. A nested `delivery_address` or `corporate_address` PATCH changes only that one; top-level `address` mirrors delivery [steps 8, 9].
- **A partial nested object replaces the whole address**: `{"corporate_address": {"city": "Warren"}}` blanked address, state and zipcode [g_customers.txt step 10]. Always send the full nested object.
- **`archived: false` un-archives**; edits work while archived [g_customers.txt steps 3-5]. Never send `archived` unless you mean it.
- **`ein` is ignored**: 200, still reads `null` [g_customers.txt step 6]. Spec 2.36.0: read-only, inherited from the buyer company.
- Customer `phone` accepts `(313) 555-0101` [r2_t14_customer_create.txt].
- Lookup filters: `name` is exact match only; `license_number` is exact AND case-sensitive (lowercase -> 0 rows); `license_number__in`, `__iexact`, `__icontains` are IGNORED and return the whole list [r3_a_param_sweep.txt]. One `license_number=` call per licence.

## Contacts

- **`phone` must be 10 bare digits**: `(313) 555-0100`, `+13135550100`, `313.555.0100` -> 400 `"Phone number must consist of 10 digits."` [r2_t12_contact_patch.txt].
- `first_name` over 30 chars -> 400 [r2_t12_contact_patch.txt T12.7]. PATCH is partial [T12.1].
- **DELETE sets `delete: true`; the row stays.** GET still returns it [r2_t8_contacts.txt].
- **The default `/contacts/` list INCLUDES deleted contacts** (1381 = 496 deleted + 885 live). Filter with `delete=false` [r2_t8_contacts.txt].

---

## Lists and limits

- **Page size: default 50, max 500; `limit=1000` -> 400** (products, customers, contacts, line-items) [r2_t9_pagination.txt]. Details in `pagination.md`.
- **Honoured vs ignored query parameters**: full table in `filtering.md`. An ignored parameter returns the WHOLE list with a 200, so a filter that "works" can silently return everything [r3_a_param_sweep.txt].
- **`/orders-received/` `fields_include` takes order field names**: `fields_include=id` -> 400 `"Fields `id` do not exist on this endpoint."` [log, r2_t9_pagination.txt]. Use `number`.
- `/orders-received/` returns `line_items` even without `include_children` [r3_a_param_sweep.txt].
- **No rate-limit headers** on responses [r2_t8_t9_console.txt "response headers"]. Docs: 300 requests/minute, burst 1000/minute, tied to the API key's owner, 429 when exceeded [doc:api_authorization.txt].
