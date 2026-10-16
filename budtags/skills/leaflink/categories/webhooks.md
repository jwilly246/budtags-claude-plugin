# LeafLink Webhooks (Inbound Deliveries)

**What the official docs say** (`brands_webhooks.txt`, `brands_webhooks_setup.txt` in `~/budtags-audits/2026-10-15/leaflink_docs_gap_audit/text/`): two subscriptions (orders, products: "created or updated"), an `LL-Signature` header that is base64 HMAC SHA-256 of the request body with the company webhook key, and automatic deactivation after five consecutive days at a 100% failure rate. **Nothing else is documented**: payload shape, field paths, retries, ordering and idempotency are all empirical.

**Empirical sources:**
- Live delivery probe via ngrok, 2026-04-14 (envelope, field paths, cascades, retries).
- Sandbox and prod positive control, 2026-10-16 (raw files in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/`). `patterns/verified-behavior.md` wins on any conflict.

---

## Supported Event Types

**Only 2** (documented). LeafLink does NOT emit webhooks for payments, inventory, or customers; those must keep flowing via `sync_recent`.

| Subscription (LeafLink UI) | Payload `type` | Triggers |
|---|---|---|
| New & Changed Orders | `"order"` | Order create / edit / status transition |
| New & Changed Products | `"product"` | Direct product edit + cascade from order activity (empirical, see below) |

---

## Subscription Management

**LeafLink has no webhook management API.** The official spec has no webhook path, so subscriptions cannot be created, listed or deleted programmatically. Setup is UI-only (documented):

1. An admin opens Settings → Developer access and enables **Enable Webhooks** AND **Enable Developer Options Access** (both required)
2. The admin grants your user Settings > Manage Users > Edit Permissions > **Can Access Developer Options**
3. Settings → Developer Options → **Add Webhook**: enter a name and URL, tick NEW & CHANGED ORDERS and/or NEW & CHANGED PRODUCTS
4. Signatures: Developer Options → **Company Webhook Key** → enter password → **Generate Key** (company Admins only). One key per company signs every webhook.

Implication: your app's "integrations" UI must guide the user through these clicks rather than automating. Use `leaflink_webhook_logs` rows to self-verify ("Orders received ✅" when a row with `event_type=order` exists).

---

## Sandbox Does Not Deliver to Prod

verified 2026-10-16 (sandbox + prod positive control, `webhook_probe/`):

- A prod `PATCH products/843545/` (description only) at 00:20:29 EDT produced prod webhook row 43973 at 00:20:45, 16 s later (`webhook_probe/prod_control_ledger.jsonl`, `webhook_probe/c1_control.txt`).
- 42 sandbox order writes at 04:27-04:28Z produced no webhook rows on the prod receiver (`out/w_order_write_times.txt`, `webhook_probe/w_watch_log.txt`).
- So sandbox writes are safe for the prod receiver, and you cannot test webhook delivery from the sandbox into prod.
- The sandbox is a prod clone the docs say resets nightly at 12:00am EST (`gs.txt`), but it did NOT reset on the night of 10-15/16 (customer 2209361 created 04:51Z was still listed at 15:02Z: `out/r2_setup.txt`, `out/r3_a_param_sweep.txt`). Clean up your own test rows.

---

## Signature Verification

```php
// LeafLink signs with HMAC-SHA256 over the raw request body (documented).
// Header: LL-Signature (title case on wire; HTTP is case-insensitive)
// Format: base64, no prefix, no version tag.
$raw = $request->getContent();
$provided = $request->header('LL-Signature');

$expected = base64_encode(hash_hmac('sha256', $raw, $secret, true));
$valid = hash_equals($expected, $provided ?? '');
```

**Critical**: capture `$request->getContent()` BEFORE any `json_decode` or middleware that might normalize the body. The signature is over the exact bytes LeafLink sent, UTF-8 multi-byte chars included.

**No timestamp header exists** (empirical). Replay protection must rely on SHA-256 body-hash dedup (24h window scoped per org); payload-`modified` cannot be used (see below).

---

## Payload Envelope (empirical, 2026-04-14; identical for both event types)

```json
{
  "action": "edit",              // also "create" / "delete"
  "data": { ... },               // full object body
  "type": "product"              // or "order"
}
```

## Field Paths (empirical, 2026-04-14; not in the official docs)

| Need | Product | Order |
|---|---|---|
| Object id | `data.id` (int) | `data.id` (int) |
| Human number | `data.sku` (string) | `data.number` (UUID string) |
| Modified timestamp | `data.modified` (ISO 8601 +tz) | **Does not exist**; orders only have `data.created_on` |
| License (isolation check) | `data.license.number` (scalar string, e.g. `"AU-P-000247"`) | `data.seller.licenses[*].number` (array; match ANY against org facilities) |
| Line items | — | `data.orderedproduct_set` (NOT `line_items`) |
| Parent relationship | `data.parent.{id,name}` (children only) | — |
| Reservation counter | `data.reserved_qty`; bumps on order activity WITHOUT updating `data.modified` | — |

---

## Cascade Behaviors (empirical; affects dedup + ordering assumptions)

### Parent-product edit → multi-child fan-out

Editing the description/price of a parent product in LeafLink emits **N product webhooks (one per child variant)**, each with the cascaded attribute. The parent itself does NOT emit a standalone webhook. Each child has a distinct `data.id` so normal per-id dedup + ordering works.

### Order activity → inventory cascade

Creating / accepting / transitioning an order emits **N product webhooks** (one per line item, because `reserved_qty` changes) **+ 1 order webhook** for the order itself. A single order action can produce 20+ webhooks for a large order.

### `data.modified` on products: what moves it

- **Order-driven inventory changes do NOT move a listing's `modified`.** Confirmed on the sandbox: `modified` stayed the same through create, accept, fulfil, ship and reject while `quantity` / `reserved_qty` changed (verified 2026-10-16 (sandbox, w_b_inventory.txt B0-B9)). A legitimate product webhook can arrive with a `modified` weeks or months old.
- **Direct API edits DO move it.** Both `modified` and `last_edit` moved on API price and quantity PATCHes (verified 2026-10-16 (sandbox, w_c_units.txt C2, C3; r2_t4_inventory_mgmt.txt T4y)). A failed (400) PATCH moved neither (w_c_units.txt C1).

**Do NOT reject on payload-modified freshness.** Use SHA-256 body-hash dedup (24h) as the primary defense.

---

## Retry Behavior

- **Retries (empirical, 2026-04-14)**: ~14 attempts spread over ~7 minutes on non-2xx responses
- **Auto-deactivation (documented)**: "Webhooks with a 100% failure rate for five consecutive days will be automatically deactivated." The account owner gets an email; reactivate on the Developer Options page.
- **User-agent (empirical)**: `python-requests/<version>`
- **Other headers you'll see (empirical)**: DD + Sentry tracing (`Sentry-Trace`, `Baggage`, `Traceparent`, `Tracestate`, `X-Datadog-*`); harmless, can be ignored

Return any 2xx (we use 202 "accepted" for normal deliveries, 200 "duplicate" for dedup hits) to stop the retry chain.

---

## Receiver Design (BudTags implementation target)

Route: `POST /webhooks/leaflink/{org}` in `routes/api.php` (CSRF-free), `throttle:120,1` per org.

Verification chain (uniform 401 on any failure; don't leak which orgs are configured):
1. Feature flag guard → 404
2. Resolve org by UUID → 401
3. `$raw = $request->getContent()` BEFORE any parse
4. Size guard → 413 if > 1 MB
5. HMAC verify (current secret, fallback previous_secret within 24h) with `hash_equals` → 401
6. `json_decode($raw, true)` → extract `type`, `data.id`, `action`
7. Reject `type` not in `['order', 'product']` → 404
8. License isolation (branch on event type; see field-paths table) → 401. **Risk:** see below.
9. Payload-hash dedup, 24h window scoped by org → 200 "duplicate"
10. Persist `leaflink_webhook_logs` row
11. Dispatch `ProcessLeafLinkWebhook($log_id)` on `leaflink-webhooks` queue with `WithoutOverlapping("leaflink:{type}:{id}")`
12. Return 202

See `app/Http/Controllers/MetrcWebhookController.php` for the structural pattern to mirror.

### License isolation can 401 genuine deliveries

An exact match of `data.license.number` / `data.seller.licenses[*].number` against Budtags facility licences fails for:
- ancillary products: LeafLink's best-practices table says `license` should be "N/A" for ancillary products (`brands_integration-solutions_best-practices.txt`)
- shared-hub licences and any formatting difference between LeafLink's string and ours

Each 401 counts as a failed delivery and is retried. A webhook whose deliveries all fail for five consecutive days is deactivated (documented), and nothing in Budtags notices. Log 401s from step 8 separately so a mismatch is visible.

### Order payloads have no `modified`: guard ordering another way

Order bodies carry no `modified` (empirical, table above). A retried older delivery (retries run ~7 minutes, empirical) that lands after a newer one would roll the order's status and lines back until the next poll. Do not apply an order payload blindly: re-read the order from the API (or compare status progression) before applying, rather than trusting arrival order.

---

## Common Gotchas

- **Header casing**: LeafLink sends `Ll-Signature` (title case); Laravel's `$request->header()` handles it, but if you're reading raw `$_SERVER`, check for `HTTP_LL_SIGNATURE`.
- **Per-subscription URL quirk (empirical)**: when the webhook URL is edited in LeafLink's UI, the change may not propagate to every subscription row atomically. Always verify both Orders + Products subscription rows after a URL change.
- **Signature bytes**: any middleware that pre-reads or normalizes the body before you capture `$raw` will break signature verification. Read the raw content first.
- **`modified` absence for orders**: never assume `data.modified` exists on an order payload. Build ordering logic around `data.id` + an API re-read, not arrival time alone.
- **Sandbox testing**: sandbox writes never reach the prod receiver (above). Test the receiver with prod deliveries or a local replay of a captured body.
