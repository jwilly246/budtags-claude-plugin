# Pattern — Eventual Consistency

Distru documents that **Strains and Assemblies** are **eventually consistent** — there is up to ~1 second of read-after-write lag between a write and the resource appearing on a list query.

> This is unique to Distru among Budtags' integrations. Canix and LeafLink are documented as strongly consistent for the same operations.

## What this means in practice

When you write a Strain or an Assembly:

1. The **write response is authoritative** — the returned `id` and fields are correct.
2. An immediate `GET /strains` or `GET /assemblies` may **not return the new record yet**.
3. The record is guaranteed to be visible after approximately 1 second.

## What this does NOT mean

- It does **not** mean writes are unreliable. They are committed.
- It does **not** mean other resources have this lag. Orders, Products, Companies, Batches, etc. are not documented with this caveat.
- It does **not** mean the lag is exactly 1s — treat 1s as a documented floor; in practice it may be longer under load.

## Wrong reactions (do not do)

- **Polling immediately and concluding "the write failed"** when the resource is missing from the next list query. The write succeeded; the index hasn't caught up.
- **Querying in a tight loop** to wait for the resource to appear. This wastes API budget and the rate limit.
- **Bumping `updated_at_from` filters** based on the write response and missing the just-written record. The record's `updated_at` is set, but the indexer may not have updated yet.

## Right reactions

- **Trust the write response body.** Capture the `id` from the POST/PUT and persist it locally.
- **If you must re-fetch** (e.g., to confirm a related field set on the canonical record), back off **1.5 seconds minimum** and prefer a direct GET by id (`/strains/{id}` if available) over a list query.
- **For incremental sync**, save the high-water mark as `now() - 5s` rather than the latest record's `updated_at`. This widens the next window enough to catch any laggard.

## Code reference

```php
// Creating an assembly: trust the response, don't immediately re-list
$response = $api->post('/assemblies', $payload);
$assemblyId = $response['data']['id'];
$importJob->update(['last_assembly_id' => $assemblyId]);

// If you MUST re-fetch (rare), sleep first
sleep(2);
$verification = $api->get("/assemblies/{$assemblyId}");
```

## Incremental sync resilience

```php
// Save the high-water mark with a small buffer to absorb consistency lag
$importJob->update([
    'last_synced_at' => now()->subSeconds(5)->toIso8601String(),
]);
```

## Cross-references

- Manufacturing endpoint: `categories/manufacturing.md`
- Filtering and incremental sync: `patterns/filtering.md`
- Write semantics: `patterns/write-safety.md`
