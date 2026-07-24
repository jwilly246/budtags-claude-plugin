# QuickBooks Caching Pattern

**Pattern:** `Cache::flexible()` stale-while-revalidate + one manual per-customer cache
**Constants:** `DEFAULT_CACHE_TIME = 300`, `FLEX_CACHE_TIME = [150, 300]`
**Strategy:** Serve stale immediately, refresh in the background

---

## Overview

QuickBooks reads are cached to reduce API calls and page latency. The wrapper uses Laravel's `Cache::flexible()` (stale-while-revalidate) rather than plain `Cache::remember()`, so a value that has gone stale is returned immediately while a fresh copy is fetched in a deferred callback.

Two constants drive the TTLs (`app/Services/Api/QuickBooksApi.php`):

```php
const DEFAULT_CACHE_TIME = 300;        // 5 minutes
const FLEX_CACHE_TIME = [150, 300];    // stale after 2.5min, expire after 5min
```

`Cache::flexible($key, [$fresh, $stale], $callback)` semantics:
- **0 - 150s:** value is fresh, returned from cache, no work
- **150 - 300s:** value is stale - returned immediately AND a background refresh runs the callback
- **> 300s:** value is gone - callback runs synchronously and the caller waits

There is no `Cache::remember()`, no `Cache::tags()`, and no per-call `$ttl` argument in the real code.

---

## Cache Key Map

Every key is org-scoped with the `qbo:` prefix and colon separators. `$orgId` is the org UUID.

| Method | Key | TTL |
|--------|-----|-----|
| `get_items_cached($orgId)` | `qbo:items:{orgId}` | `DEFAULT_CACHE_TIME` (via `fetch_from_cache_or_api`) |
| `get_all_accounts_cached($orgId)` | `qbo:accounts:{orgId}` | `FLEX_CACHE_TIME` |
| `get_all_invoices_cached($orgId)` | `qbo:all_invoices:{orgId}` | `FLEX_CACHE_TIME` |
| `get_credit_memos_cached($orgId)` | `qbo:credit_memos:{orgId}` | `FLEX_CACHE_TIME` |
| `get_payment_methods_cached($orgId)` | `qbo:payment_methods:{orgId}` | `FLEX_CACHE_TIME` |
| `get_deposit_accounts_cached($orgId)` | `qbo:deposit_accounts:{orgId}` | `FLEX_CACHE_TIME` |
| `get_terms_cached($orgId)` | `qbo:terms:{orgId}` | `FLEX_CACHE_TIME` |
| `get_invoices_cached($orgId, $page, $perPage)` | `qbo:invoices:{orgId}:page:{page}` | `FLEX_CACHE_TIME` |
| `get_customers_by_id_cached($orgId, $ids)` | `qbo:customer:{orgId}:{id}` (one per customer) | `DEFAULT_CACHE_TIME` |
| `SyncQboInvoices` (billing snapshot) | `qbo:invoices:{orgId}` (no `:page:`) | **24h** (`now()->addHours(24)`) |

> Two different shapes share the `qbo:invoices:{orgId}` prefix: the paginated UI cache appends `:page:{n}`, while the billing sync writes the bare `qbo:invoices:{orgId}` snapshot with a 24h TTL. They do not collide, but do not confuse them.

---

## The `flexible`-wrapped families

Most `*_cached` methods are a one-line `Cache::flexible` wrapper returning a `Collection`:

```php
public function get_all_accounts_cached(string $org_id): Collection {
    return collect(Cache::flexible(
        "qbo:accounts:{$org_id}",
        self::FLEX_CACHE_TIME,
        fn () => $this->get_all_accounts()->toArray()
    ));
}
```

`get_credit_memos_cached`, `get_payment_methods_cached`, `get_deposit_accounts_cached`, `get_terms_cached`, and `get_all_invoices_cached` follow the same shape with their own key.

### Paginated invoices

`get_invoices_cached` caches a `{invoices, cached_at}` envelope per page and returns the paginator:

```php
public function get_invoices_cached(string $orgId, int $page = 1, int $perPage = 50): LengthAwarePaginator {
    $cacheKey = "qbo:invoices:{$orgId}:page:{$page}";

    $data = Cache::flexible($cacheKey, self::FLEX_CACHE_TIME, fn () => [
        'invoices' => $this->get_invoices($page, $perPage),
        'cached_at' => now()->toIso8601String(),
    ]);

    return $data['invoices'];
}
```

---

## `fetch_from_cache_or_api` helper

`get_items_cached` goes through a protected helper that adds a `force_fetch` bypass and an optional `$each` callback for warming secondary keys:

```php
protected function fetch_from_cache_or_api(
    string $key,
    callable $call,
    ?callable $each = null,
    bool $force_fetch = false,
    int $seconds_to_cache = self::DEFAULT_CACHE_TIME
): array {
    if ($force_fetch) {
        $data = $call();
        Cache::put($key, $data, $seconds_to_cache);   // hard overwrite, skip cache
        return $data;
    }

    return Cache::flexible($key, [(int) ($seconds_to_cache / 2), $seconds_to_cache], function () use ($call, $each, $seconds_to_cache) {
        $data = $call();
        if ($each) {
            foreach ($data as $item) {
                Cache::set($each($item), $item, $seconds_to_cache);
            }
        }
        return $data;
    });
}
```

Note it synthesizes the flex window as `[seconds/2, seconds]`, so with the default 300 you get the same `[150, 300]` behavior as `FLEX_CACHE_TIME`.

## Manual per-customer cache

`get_customers_by_id_cached` does NOT use `flexible`. It checks `qbo:customer:{orgId}:{id}` per id, fetches only the misses in one query, back-fills the cache, and returns results in the original `$ids` order to keep invoice/customer alignment:

```php
$cached = Cache::get("qbo:customer:{$orgId}:{$id}");
// ... fetch uncached ids in a single call ...
Cache::put("qbo:customer:{$orgId}:{$customer->Id}", $customer, self::DEFAULT_CACHE_TIME);
```

---

## Clearing Cache

Two clear methods exist; each forgets an explicit list of keys (no tag flush):

```php
public function clear_cache(string $orgId): void {
    Cache::forget("qbo:items:{$orgId}");
    Cache::forget("qbo:accounts:{$orgId}");
    Cache::forget("qbo:all_invoices:{$orgId}");
    Cache::forget("qbo:credit_memos:{$orgId}");
    Cache::forget("qbo:payment_methods:{$orgId}");
    Cache::forget("qbo:deposit_accounts:{$orgId}");
    Cache::forget("qbo:terms:{$orgId}");
}

public function clear_invoices_cache(string $orgId): void {
    for ($i = 1; $i <= 100; $i++) {           // paginated invoice cache, pages 1-100
        Cache::forget("qbo:invoices:{$orgId}:page:{$i}");
    }
}
```

**Coverage gaps to be aware of** (verify before assuming a key is cleared):
- `clear_cache()` forgets `qbo:all_invoices:{orgId}` but NOT the paginated `qbo:invoices:{orgId}:page:*` keys and NOT the per-customer `qbo:customer:{orgId}:*` keys.
- `clear_invoices_cache()` only touches `:page:1` through `:page:100`; it does NOT clear the billing sync's bare `qbo:invoices:{orgId}` snapshot.
- Neither method clears the 24h billing snapshot - that is overwritten by the next `qbo:sync-invoices` run.

### When to Clear

Call `clear_invoices_cache($orgId)` after mutating invoices (create/update/send/record-payment) so the next page load reflects the change, and `clear_cache($orgId)` after bulk item/account changes or a Metrc quantity sync.

---

## Best Practices

✅ **ALWAYS keep the `qbo:` prefix and org id in every key**
✅ **ALWAYS use `Cache::flexible` with `FLEX_CACHE_TIME` for the cached read families**
✅ **ALWAYS clear the matching cache after a write** (`clear_invoices_cache` after invoice writes)
✅ **ALWAYS pass the org UUID as `$orgId`, not an integer**

❌ **NEVER reintroduce `Cache::remember` / `Cache::tags`** - the code standard is `flexible`
❌ **NEVER cache write operations** - only reads are cached
❌ **NEVER assume `clear_cache()` clears paginated or per-customer invoice keys** - it does not
❌ **NEVER confuse `qbo:invoices:{orgId}` (24h billing snapshot) with `qbo:invoices:{orgId}:page:{n}`**

---

## Related Patterns

- `patterns/billing-invoice-sync.md` - The 24h `qbo:invoices:{orgId}` snapshot
- `patterns/multi-tenancy.md` - Why keys are org-scoped
- `categories/items.md` - `get_items_cached()` method
- `patterns/logging.md` - Logging cache operations
