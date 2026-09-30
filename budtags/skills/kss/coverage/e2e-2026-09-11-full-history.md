# Full-history E2E — 2026-09-11 (test environment, Supplier key, two runs one hour apart)

First full-history import (no invoice window) through `kss:e2e-verify`, after main was merged into
`feature/kss-integration` and the resumable invoice line fetch landed. Everything below is MEASURED on the
wire; it supersedes the 90-day-window numbers in `e2e-2026-08-20.md` where the two disagree.

## Outcome

| Run | Requests | Wall clock | What happened |
|---|---:|---:|---|
| 1 (13:55) | 1,028 (wall) | 4.5 min | 13 bounded entities OK in ~168 requests; `/invoices` mirrored all 21,743 headers, then lines + COA audit until the hourly wall at 860 entity requests: 8,400 invoices stamped, 13,343 owed. Cap deferred payments / ar_aging / purchases / promotions. |
| 2 (15:01) | 753 | 6.7 min | Same org. Headers re-walked (44); lines fetched ONLY for the 13,343 owed invoices (496 requests, 325 batches); 4 deferred entities landed; ETag probe 2 → 1 requests (page-1 304). ALL 15 bands IN BAND, first-party firewall 0 deltas. |

Final mirror: 21,743 invoices, all stamped (`lines_synced_for` = `kss_time_updated`, 0 stale), 270,570 lines,
68,134 retailer-inventory rows, 1,995 payments / 2,239 applications, 362 aging accounts, 228 purchases /
4,944 lines, 437-row warehouse snapshot (latest generation only, prior generation pruned as ruled).

## Findings

1. **Page cap is 500 on every endpoint, line endpoints included** (497 rows seen on one `/invoiceTransactions`
   page). The "lines cost 2 requests per 40-id batch" estimate was wrong because the cost is ROW-bound:
   11.2 lines per invoice → ~449 rows per 40-invoice batch → avg 1.3 pages (max 3). Full-history line cost
   ≈ 270k lines / ~350 rows per page ≈ **700 requests**, so the backfill is exactly two hourly runs.
2. **`/invoiceCOAs` returned 2.3 rows per LINE** (217,966 COA rows for 93,451 lines on run 1) and cost 540
   requests against 265 for the lines — about 2x the walk it audits, for two fields the line feed already
   carries. Ruled OFF for imports and the sweep the same day (`ImportOptions::$crossCheckKssCoas`,
   `--audit-coas` on the harness). The 2.3x surplus is unexplained until a complete audited pass reports.
3. **Resume works as designed**: run 2 never re-asked about the 8,400 invoices run 1 stamped, and the batch
   cut at the wall (lines landed, audit not) was correctly left unstamped and re-fetched.
4. **A full RE-import after the backfill costs ~44 header pages + changed invoices only**; the 13 bounded
   entities are ~168 requests. Steady-state hourly ceiling for one org: ~250 requests when much changed.
5. **`/invoiceTransactions` carries two undocumented fields**: `ReasonID`, `Reason` (unknown-wire-key audit).
6. **`/promotionsProducts` still 500s**; its retry backoff is ~87 s of wall clock per pass, no requests wasted.
7. Reconciliation reports on a complete pass (all keyed, one row each): 656 open invoices whose
   `/payments/openInvoices` echo disagrees with the invoice mirror on totals/dates/term/PO; 21 open invoices
   the depletion mirror does not carry; 25 AR accounts with no bridged partner; 5 AR accounts billed against
   >1 customer; 12 batches whose receipt-line expiry disagrees with the batch; 9 non-interco purchases with
   pallet tags matching no Budtags order (218 interco held out); 1,995 SupplierCredit memos ($946k) against 0
   referenced seller credits (expected: no first-party ledger exists on the harness org).

## Operating numbers to plan against

- Key: 1,028/hour SLIDING. Two consecutive hours are needed for a first full-history import of a
  ~22k-invoice account; every later full import fits in one.
- The cheapest remaining lever (NOT built): a `StartDate` lookback on the SWEEP's header walk (44 → ~6
  pages per pass). Deliberately unused because `StartDate` filters on invoice date and old invoices' status /
  balance flips must still be seen.

## 2026-09-15: runs 3 and 4 (after the audit fixes)

Run 3 (15:09, all entities, `--max-requests=1000`) was the first pass over the seven data fixes from the
2026-09-12 audit; every one showed up on real rows (CA licence types, short-ship `reason_id`/`reason`,
`pending_sales`, `supplier_ids`, brand partner on products, Supplier-Rep-wins `assigned_rep`, and 2,633
batches minted from invoice-line batch codes with their COA documents, beside 438 feed-owned batches).
Invoices met the wall at 860 requests: 25,920 lines stamped, 1,047 invoices left for the next window.

Two harness bands went out of band for harness reasons: the batch-code band predates the minted
batches and now counts feed-owned rows only (a new `minted_batches` band asserts the minted rows); the
warehouse-rows band widened to 15% because the TEST dataset resets every Sunday (431 rows that day).

Run 4 (`--entities=invoices,payments,ar_aging,purchases,promotions`, next quota window): _pending_.
