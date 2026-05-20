# LeafLink Webhooks (Inbound Deliveries)

**Live-validated 2026-04-14 via ngrok probe.** LeafLink's docs (`developer.leaflink.com/legacy/v2/brands/webhooks/`) leave many fields undocumented; this file captures what was empirically confirmed against a real delivery.

---

## Supported Event Types

**Only 2.** LeafLink does NOT emit webhooks for payments, inventory, or customers — those must continue flowing via `sync_recent`.

| Subscription (LeafLink UI) | Payload `type` | Triggers |
|---|---|---|
| New & Changed Orders | `"order"` | Order create / edit / status transition |
| New & Changed Products | `"product"` | Direct product edit + cascade from order activity (see below) |

---

## Subscription Management

**LeafLink has no webhook management API.** You cannot create/list/delete subscriptions programmatically. Setup is UI-only:

1. Settings → Developer access → toggle **Enable Webhooks** AND **Enable Developer Options Access** (both required)
2. Open the Developer Options page → **+ Add Webhook**
3. Enter URL, name, secret, and check both Order / Product subscription boxes

Implication: your app's "integrations" UI must guide the user through these clicks rather than automating. Use `leaflink_webhook_logs` rows to self-verify ("Orders received ✅" when a row with `event_type=order` exists).

---

## Signature Verification

```php
// LeafLink signs with HMAC-SHA256 over the raw request body.
// Header: LL-Signature (title case on wire; HTTP is case-insensitive)
// Format: base64, no prefix, no version tag.
$raw = $request->getContent();
$provided = $request->header('LL-Signature');

$expected = base64_encode(hash_hmac('sha256', $raw, $secret, true));
$valid = hash_equals($expected, $provided ?? '');
```

**Critical**: capture `$request->getContent()` BEFORE any `json_decode` or middleware that might normalize the body — the signature is over the exact bytes LeafLink sent, UTF-8 multi-byte chars included.

**No timestamp header exists.** Replay protection must rely on SHA-256 body-hash dedup (24h window scoped per org) — payload-`modified` cannot be used (see below).

---

## Payload Envelope (identical for both event types)

```json
{
  "action": "edit",              // also "create" / "delete"
  "data": { ... },               // full object body
  "type": "product"              // or "order"
}
```

## Field Paths

| Need | Product | Order |
|---|---|---|
| Object id | `data.id` (int) | `data.id` (int) |
| Human number | `data.sku` (string) | `data.number` (UUID string) |
| Modified timestamp | `data.modified` (ISO 8601 +tz) | **Does not exist** — orders only have `data.created_on` |
| License (isolation check) | `data.license.number` (scalar string, e.g. `"AU-P-000247"`) | `data.seller.licenses[*].number` (array — match ANY against org facilities) |
| Line items | — | `data.orderedproduct_set` (NOT `line_items`) |
| Parent relationship | `data.parent.{id,name}` (children only) | — |
| Reservation counter | `data.reserved_qty` — bumps on order activity WITHOUT updating `data.modified` | — |

---

## Cascade Behaviors (IMPORTANT — affects dedup + ordering assumptions)

### Parent-product edit → multi-child fan-out

Editing the description/price of a parent product in LeafLink emits **N product webhooks (one per child variant)**, each with the cascaded attribute. The parent itself does NOT emit a standalone webhook. Each child has a distinct `data.id` so normal per-id dedup + ordering works.

### Order activity → inventory cascade

Creating / accepting / transitioning an order emits **N product webhooks** (one per line item, because `reserved_qty` changes) **+ 1 order webhook** for the order itself. A single order action can produce 20+ webhooks for a large order.

### `data.modified` is unreliable for products

LeafLink only updates `data.modified` on direct product attribute edits — NOT when `reserved_qty` changes from order activity. A legitimate product webhook can arrive with a `modified` timestamp weeks or months old.

**Do NOT reject on payload-modified freshness.** Use SHA-256 body-hash dedup (24h) as the primary defense.

---

## Retry Behavior (empirical)

- **Retries**: ~14 attempts spread over ~7 minutes on non-2xx responses
- **Auto-deactivation**: webhooks with 100% failure rate for 5 consecutive days are disabled
- **User-agent**: `python-requests/<version>`
- **Other headers you'll see**: DD + Sentry tracing (`Sentry-Trace`, `Baggage`, `Traceparent`, `Tracestate`, `X-Datadog-*`) — harmless, can be ignored

Return any 2xx (we use 202 "accepted" for normal deliveries, 200 "duplicate" for dedup hits) to stop the retry chain.

---

## Receiver Design (BudTags implementation target)

Route: `POST /webhooks/leaflink/{org}` in `routes/api.php` (CSRF-free), `throttle:120,1` per org.

Verification chain (uniform 401 on any failure — don't leak which orgs are configured):
1. Feature flag guard → 404
2. Resolve org by UUID → 401
3. `$raw = $request->getContent()` BEFORE any parse
4. Size guard → 413 if > 1 MB
5. HMAC verify (current secret, fallback previous_secret within 24h) with `hash_equals` → 401
6. `json_decode($raw, true)` → extract `type`, `data.id`, `action`
7. Reject `type` not in `['order', 'product']` → 404
8. License isolation (branch on event type — see field-paths table) → 401
9. Payload-hash dedup, 24h window scoped by org → 200 "duplicate"
10. Persist `leaflink_webhook_logs` row
11. Dispatch `ProcessLeafLinkWebhook($log_id)` on `leaflink-webhooks` queue with `WithoutOverlapping("leaflink:{type}:{id}")`
12. Return 202

See `app/Http/Controllers/MetrcWebhookController.php` for the structural pattern to mirror.

---

## Common Gotchas

- **Header casing**: LeafLink sends `Ll-Signature` (title case) — Laravel's `$request->header()` handles it, but if you're reading raw `$_SERVER`, check for `HTTP_LL_SIGNATURE`.
- **Per-subscription URL quirk**: when the webhook URL is edited in LeafLink's UI, the change may not propagate to every subscription row atomically. Always verify both Orders + Products subscription rows after a URL change.
- **Signature bytes**: any middleware that pre-reads or normalizes the body before you capture `$raw` will break signature verification. Read the raw content first.
- **`modified` absence for orders**: never assume `data.modified` exists on an order payload. Build ordering logic around `data.id` + arrival timestamp instead.
