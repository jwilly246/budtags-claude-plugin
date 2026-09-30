---
name: backfill
description: Safe production data repair and backfills - schema check, existing-value check, full-range measurement, read-only prod validation of the new logic, dry run with sample diffs, approval, apply, re-verify. Use for any prod data write, repair, backfill, restore, or one-off fix command, including the data-patch half of an urgent incident.
version: 1.0.0
category: project
auto_activate:
  keywords:
    - "backfill"
    - "data repair"
    - "repair the data"
    - "fix the data"
    - "prod write"
    - "restore"
    - "dry run"
    - "patch the data"
---

# Production Data Repair / Backfill

Every past bad prod write came from skipping one of these steps: costs written into the selling-price field (Evo Gold Crown sheet, 2026-09), a lookback window guessed at 60 days when real shipments went back 107, an int-keyed array spread that renumbered template ids to 0 found. Each was catchable read-only before anything was written or deployed. Run the steps in order; none is optional.

Prod access, tinker quoting, the `fn()`-only closure rule and the Mailgun-cap hazard: see the `triage` skill, Phase 1. Tinker is the only DB path on the box.

---

## Step 1: Target PROD

Customer, order, item and package questions are about PROD. The local DB and staging are stale copies. If a prod READ is blocked, run the identical read-only script on staging (`make ssh ENV=linode-staging`), label the answer as staging, and flag anything newer than staging's last refresh. The Step 6 validation and every write still need prod.

## Step 2: Real schema

Query the real columns of every table you will read or write (`Schema::getColumnListing('table')` in tinker, or `SHOW COLUMNS`). Never write a column name from memory. Known traps: `logs` has `timestamp`, not `created_at`.

## Step 3: Existing values in the target fields

Before writing a value, read what is already there for 3-5 real rows and state which field it belongs in:

- cost vs price, unit vs total, per-unit vs per-package, grams vs each
- a non-empty value already there means STOP: say whether the write replaces, fills blanks only, or should be skipped
- source-of-truth rule: the owning system's value wins (LeafLink for synced product fields, Distru for Distru-owned costs, Metrc for package state); a sync never clears the other side's non-empty value

If the mapping is ambiguous, ask ONE AskUserQuestion showing those real rows.

## Step 4: Measure the full range, never guess a tunable

Query the whole affected population with NO lookback limit first: count, min/max date, distribution by org. Any window, threshold or batch size in the command is set from that measurement (and noted in the command's docblock), not picked by feel.

## Step 5: Write the command, `--dry-run` by default

- Artisan command; dry run is the default and `--apply` (or equivalent) is required to write
- Scoped per org (`--org=`), idempotent, logs every write via `LogService::store()`
- Keeps an undo path (stash old values in the log notes or a `--restore` flag)
- Int-keyed arrays: `array_replace()`, NEVER `[...$array, $intKey => $value]` (spread renumbers int keys)
- Tests for the transform, including the edge cases Step 4 found

## Step 6: Validate the NEW logic on prod, read-only, BEFORE deploy

Unit tests are not enough. Run the changed code path against real prod data without deploying:

- Copy the release: `cp -a /var/www/html/budtags/current /var/www/html/budtags/validate-backfill`, overlay the changed files, run the dry run there, then `rm -rf` that copy. Or scp a tinker script that binds private methods: `\Closure::bind(fn ($m, ...$a) => $this->{$m}(...$a), $cmd, $cmd)`.
- Cross-check the result with an INDEPENDENT probe (a raw Metrc/LeafLink/Distru query, a count straight from the table). The two must agree.

## Step 7: Show the dry run, then wait

Report before anything is written:

```markdown
## Backfill dry run: {name}
| Org | Rows in scope | Would change | Skipped (already set) | Skipped (other) |
|-----|---------------|--------------|-----------------------|-----------------|

**Samples** (5 real rows): {id} {field}: {before} -> {after}
**Fields written**: {list}   **Fields never touched**: {list}
**Measured range**: {earliest..latest, source of the number}
**Undo**: {exact command}
**Apply**: {exact command}
```

Then STOP. The user approves the apply. Deploy stays with the user.

## Step 8: Apply once, then re-verify

After approval: apply, then re-run the same read queries. Written count must equal the dry-run count; spot-check the same 5 sample rows. Report any difference; do not paper over it with a second write.

---

## Urgent incidents

Same steps, faster: Steps 2, 3 and 7 are never skipped even when a customer is blocked. A one-off tinker patch is fine instead of a command (Step 5) when it touches a handful of rows, but it still shows its before/after rows and gets the OK first.
