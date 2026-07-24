# QuickBooks Billing / Overdue Invoice Sync Pattern

**Pattern:** Service-user token -> per-org invoice fetch -> Redis snapshot -> org billing state
**Command:** `qbo:sync-invoices {--org=}`
**Schedule:** daily at 06:00, `withoutOverlapping()`, `environments('production')`

---

## Overview

BudTags dunning (payment warnings and action-blocking) is driven off the org's own QuickBooks invoices. A single BudTags-owned QuickBooks connection - the **service user** - reads invoices for every org that has a `qbo_customer_id`, caches a per-org snapshot in Redis, and stamps overdue state onto the `organizations` row.

Unlike the interactive `/quickbooks` features (which use the current user's active-org token), this pipeline runs unattended from one company-wide token. See `patterns/multi-tenancy.md` for why it queries `QboAccessKey` by bare `user_id`.

**Key files:**
- `app/Console/Commands/SyncQboInvoices.php` - the command
- `config/quickbooks.php` - service user + thresholds
- `app/Enums/InvoiceStatus.php` - the status enum
- `app/Console/Kernel.php` - the schedule entry

---

## Command Flow

`qbo:sync-invoices` (signature `qbo:sync-invoices {--org= : Specific organization ID to sync}`) runs `handle()` in five steps:

### 1. Resolve the service user

```php
protected function resolve_service_user(): ?User {
    $user_id = config('quickbooks.service_user_id');   // env QBO_SERVICE_USER_ID
    if (!$user_id) {
        return null;                                   // -> "No QBO service user configured" + FAILURE
    }
    return User::query()->find($user_id);
}
```

### 2. Initialize the API from the service user's token

The token is fetched by `user_id` only (NOT the org-scoped relationship) because the service user's `active_org_id` may not match the org the token was minted for, and the token works company-wide:

```php
$token = QboAccessKey::where('user_id', $user->id)->latest()->first();

if (!$token) {
    $this->error('QBO service user has no OAuth token. Re-authenticate at /quickbooks.');
    LogService::store_keyed(
        'qbo-invoice-sync-auth',
        'QBO Invoice Sync Auth Failed',
        "Service user ID {$user->id} has no QBO token. Re-authenticate at /quickbooks.",
    );
    return null;
}

$api = app(QuickBooksApi::class);
$api->set_service_from_token($token);   // may throw if refresh fails -> keyed log, return null
```

Both the missing-token and the failed-refresh paths log through `store_keyed('qbo-invoice-sync-auth', ...)` so the daily cadence does not append an identical failure row every morning (see [Auth Failure & Recovery](#auth-failure--recovery)).

### 3. Select target orgs

```php
protected function get_target_orgs(): Collection {
    if ($this->option('org')) {
        return Organization::where('id', $this->option('org'))
            ->whereNotNull('qbo_customer_id')->get();
    }
    return Organization::whereNotNull('qbo_customer_id')->get();
}
```

Orgs without a `qbo_customer_id` are never touched. An empty set logs "No organizations with qbo_customer_id found. Nothing to sync." and returns `SUCCESS`.

### 4. Sync each org

```php
protected function sync_org_invoices(QuickBooksApi $api, Organization $org): void {
    $invoices = $api->get_customer_invoices((string) $org->qbo_customer_id);

    $snapshots = $invoices->map(fn ($invoice) => [
        'qbo_invoice_id' => (string) $invoice->Id,
        'qbo_customer_id' => (int) $org->qbo_customer_id,
        'doc_number' => $invoice->DocNumber ?? '',
        'total_amount' => (float) $invoice->TotalAmt,
        'balance' => (float) $invoice->Balance,
        'due_date' => $invoice->DueDate ?? null,
        'txn_date' => $invoice->TxnDate ?? null,
        'status' => $this->determine_status($invoice)->value,
        'invoice_link' => $invoice->InvoiceLink ?? null,
        'synced_at' => now()->toISOString(),
    ])->all();

    Cache::put("qbo:invoices:{$org->id}", $snapshots, now()->addHours(24));  // 24h Redis snapshot

    $this->update_org_billing_state($org, $snapshots);
}
```

The snapshot shape matches the `QboInvoiceSnapshot` TypeScript type (see `ENTITY_TYPES.md`). `invoice_link` is QBO's hosted "Pay Online" URL and is only populated when online payments (ACH / credit card) are enabled on the invoice at the QBO company level; when off it is `null` and the billing page shows no pay button.

> The 24h snapshot key is the bare `qbo:invoices:{org_id}` - distinct from the paginated UI cache `qbo:invoices:{org_id}:page:{n}`. Neither `clear_cache()` nor `clear_invoices_cache()` clears this snapshot; the next daily run overwrites it. See `patterns/caching.md`.

### 5. Summarize

Per-org exceptions increment `failed`, warn to console, and `LogService::store('QBO Invoice Sync Failed', ..., $org)` (with the `Organization` as the `loggable`). The command ends with a `QBO Invoice Sync` summary log and returns `FAILURE` if any org failed, else `SUCCESS`.

---

## Status Determination

`determine_status()` returns an `InvoiceStatus` enum from the QBO invoice's balance and due date:

```php
protected function determine_status(object $invoice): InvoiceStatus {
    $balance = (float) ($invoice->Balance ?? 0);
    if (abs($balance) < 0.01) {
        return InvoiceStatus::Paid;                 // balance ~ 0
    }
    $due_date = $invoice->DueDate ?? null;
    if ($due_date && Carbon::parse($due_date)->lt(now()->startOfDay())) {
        return InvoiceStatus::Overdue;              // has balance AND past due
    }
    return InvoiceStatus::Unpaid;                    // has balance, not yet due
}
```

`InvoiceStatus` (`app/Enums/InvoiceStatus.php`):

```php
enum InvoiceStatus: string {
    case Paid = 'paid';
    case Unpaid = 'unpaid';
    case Overdue = 'overdue';
    case Voided = 'voided';
}
```

> `determine_status()` only ever returns Paid / Unpaid / Overdue. `Voided` exists in the enum and the snapshot union but is not emitted by this command.

---

## Org Billing State

`update_org_billing_state()` computes overdue metrics from the snapshots and writes them onto the `organizations` row. Thresholds come from config:

```php
$overdue = collect($snapshots)->filter(fn ($i) => $i['status'] === InvoiceStatus::Overdue->value);
$oldest_overdue_date = $overdue->min('due_date');
$total_overdue_amount = $overdue->sum('balance');
$days_overdue = $oldest_overdue_date
    ? (int) abs(now()->diffInDays(Carbon::parse($oldest_overdue_date)))
    : 0;

$warn_days = config()->integer('quickbooks.warn_days');    // default 14
$block_days = config()->integer('quickbooks.block_days');  // default 30

$update = [
    'oldest_overdue_date' => $oldest_overdue_date,
    'total_overdue_amount' => $overdue->isEmpty() ? null : round($total_overdue_amount, 2),
];

if ($days_overdue >= $block_days) {
    $update['payment_warning_at'] = $org->payment_warning_at ?? now();
    $update['payment_blocked_at'] = $org->block_override ? null : ($org->payment_blocked_at ?? now());
} elseif ($days_overdue >= $warn_days) {
    $update['payment_warning_at'] = $org->payment_warning_at ?? now();
    $update['payment_blocked_at'] = null;
} else {
    $update['payment_warning_at'] = null;
    $update['payment_blocked_at'] = null;
}

$org->update($update);
```

**Key behaviors:**
- `days_overdue` is measured from the OLDEST overdue invoice's due date.
- `payment_warning_at` / `payment_blocked_at` are **sticky** - once set they keep their original timestamp (`?? now()`) until the org drops back below the warn threshold, which clears both.
- `block_override = true` suppresses blocking: the org still gets a warning past `block_days` but `payment_blocked_at` stays null. It is the manual escape hatch.

### Organization billing columns

Added in `2026_03_08_000001_add_organization_id_to_qbo_access_keys` (billing columns ride along), plus `qbo_customer_id` from `2025_09_14`:

| Column | Type | Meaning |
|--------|------|---------|
| `qbo_customer_id` | integer, nullable | QBO Customer Id this org maps to; gates whether the org is synced |
| `payment_blocked_at` | timestamp, nullable | Set once past `block_days` (unless `block_override`); non-null = destructive actions blocked |
| `payment_warning_at` | timestamp, nullable | Set once past `warn_days`; non-null = warning banner |
| `oldest_overdue_date` | date, nullable | Due date of the oldest overdue invoice |
| `total_overdue_amount` | decimal(10,2), nullable | Sum of overdue balances (null when none) |
| `block_override` | boolean, default false | Manual bypass: never set `payment_blocked_at` when true |

The billing page (`/orgs/active/billing`) and the shared Inertia banner prop read these columns plus the Redis snapshot, surfaced through the `BillingStatus` / `QboInvoiceSnapshot` types.

---

## Configuration

`config/quickbooks.php`:

```php
return [
    'service_user_id' => env('QBO_SERVICE_USER_ID'),
    'warn_days'  => (int) env('QBO_WARN_DAYS', 14),
    'block_days' => (int) env('QBO_BLOCK_DAYS', 30),
];
```

`.env` (see `.env.example`):
```
QBO_SERVICE_USER_ID=
QBO_WARN_DAYS=14
QBO_BLOCK_DAYS=30
```

---

## Schedule

`app/Console/Kernel.php`:

```php
$schedule->command('qbo:sync-invoices')
    ->dailyAt('06:00')
    ->withoutOverlapping()
    ->environments('production');
```

**Production only, on purpose.** Staging restores production's database (which can carry the service user's QBO token), and QBO rotates the refresh token on every use - a staging refresh would invalidate the token chain production depends on. Do not run this outside production.

---

## Auth Failure & Recovery

When the service-user token is missing or its refresh fails, the command cannot recover on its own - a human must reconnect. To keep a daily job from flooding the log, both failure paths use keyed logging:

```php
LogService::store_keyed(
    'qbo-invoice-sync-auth',
    'QBO Invoice Sync Auth Failed',
    "Service user ID {$user->id} auth error: {$e->getMessage()}",
);
```

`store_keyed` remembers the last row written under `qbo-invoice-sync-auth` via a cache pointer, so identical failures bump one row's repeat counter instead of adding a new row each morning. The result is a single live "sync is down since X" entry. See `patterns/logging.md`.

**Recovery (human, interactive):** sign in as the service user and reconnect at `/quickbooks/login`, which redirects to QBO and back through the `/quickbooks/auth` callback (`set_login_tokens`). That upserts a fresh `QboAccessKey` for the service user, and the next scheduled run picks it up. Once the failure message changes or stops, the keyed row stops bumping.

---

## QboSyncLog (separate audit trail)

`QboSyncLog` records the **interactive Metrc -> QuickBooks quantity sync** (`QuickBooksController::sync_quantities`), NOT the billing command above (the billing command uses `LogService`). It is documented here because it is the other half of QBO sync bookkeeping.

**Table** `qbo_sync_logs` (from `2025_10_29` non-metrc inventory migration):

```php
$table->foreignUuid('organization_id')->constrained('organizations')->cascadeOnDelete();
$table->foreignUuid('user_id')->nullable()->constrained('users')->nullOnDelete();
$table->enum('entity_type', ['items', 'customers', 'invoices', 'accounts', 'all'])->default('all');
$table->enum('status', ['success', 'failed', 'partial'])->default('success');
$table->integer('items_synced')->default(0);
$table->integer('items_failed')->default(0);
$table->text('error_message')->nullable();
$table->timestamps();
```

**Model** (`App\Models\QboSyncLog`): `Prunable` with a 14-day horizon, and `belongsTo` Organization + User.

```php
public function prunable(): Builder {
    return static::query()->where('created_at', '<', now()->subDays(14));
}
```

**Write pattern** (from `sync_quantities`): `status` is derived from the sync result and `error_message` holds up to the first three error strings:

```php
$status = ($result['failed'] === 0) ? 'success' : (($result['synced'] > 0) ? 'partial' : 'failed');

QboSyncLog::create([
    'organization_id' => $this->org_id(),
    'user_id' => $user->id,
    'entity_type' => 'items',
    'status' => $status,
    'items_synced' => $result['synced'],
    'items_failed' => $result['failed'],
    'error_message' => !empty($result['errors']) ? implode('; ', array_slice($result['errors'], 0, 3)) : null,
]);
```

The QBO dashboard reads the latest row for a "last synced" indicator. Rows older than 14 days are removed by the scheduled `model:prune`.

---

## Best Practices

- ALWAYS gate synced orgs on `qbo_customer_id` (`whereNotNull`) - it is the enrollment flag.
- ALWAYS resolve the service-user token by bare `user_id` here - the org-scoped relationship is wrong for a company-wide token.
- ALWAYS use `store_keyed('qbo-invoice-sync-auth', ...)` for the auth-failure log, never plain `store()`.
- ALWAYS respect `block_override` - it must suppress `payment_blocked_at` even past `block_days`.
- NEVER run `qbo:sync-invoices` outside production - it would rotate and invalidate the shared refresh token.
- NEVER confuse the 24h `qbo:invoices:{org_id}` snapshot with the paginated `:page:{n}` UI cache, or `QboSyncLog` (quantity sync) with this command's `LogService` output.

---

## Related Patterns

- `patterns/multi-tenancy.md` - Service-user token model and org scoping
- `patterns/caching.md` - The `qbo:invoices:{org_id}` 24h snapshot and cache key map
- `patterns/logging.md` - `store_keyed()` keyed logging
- `patterns/authentication.md` - `/quickbooks/auth` re-auth flow
- `ENTITY_TYPES.md` - `QboInvoiceSnapshot`, `BillingStatus`, `InvoiceStatus`
