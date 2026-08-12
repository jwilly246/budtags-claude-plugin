---
name: triage
description: Production error-log triage - read prod logs, cluster by root cause, adversarially verify each diagnosis, deliver a ranked report. Findings-only by default; fixes happen on branches only when explicitly requested. Use when reviewing prod errors, investigating overnight failures, or asked to "check the logs".
version: 1.0.0
category: project
auto_activate:
  keywords:
    - "triage"
    - "prod errors"
    - "prod logs"
    - "production errors"
    - "error log"
    - "check the logs"
---

# Production Log Triage

Encodes the established ritual: gather → cluster by root cause → falsify each diagnosis → ranked report. **Default mode is findings-only** — deliver the report and STOP. Move to fixes only when the user explicitly asked for fixes in this session (then: one branch per fix, tests, full gate, never deploy without approval).

---

## Phase 1: GATHER (three sources, not one)

Prod access: `ssh -i terraform/deploy_keys/linode-production_ssh_key root@172.234.216.52`. App dir is `/var/www/html/budtags/current` — NEVER grep the stale pre-atomic tree at `/var/www/html/budtags/app` (June-era code; it lies about what is deployed).

**1. The `logs` table (LogService) — always first.** Columns: `id, timestamp, user_id, loggable_type, loggable_id, title, notes` (NO created_at, NO description). `timestamp` is EDT local time. `title` is unindexed TEXT — always bound with a `timestamp` window or `orderByDesc('id')->limit(N)`. Identical repeats within 10 min coalesce into one row with a `[Repeated Nx, ...]` notes suffix, so row counts UNDERCOUNT events.

Tinker recipe (multi-statement, verified quoting):

```bash
ssh -i terraform/deploy_keys/linode-production_ssh_key root@172.234.216.52 \
  "cd /var/www/html/budtags/current && sudo -u www-data env XDG_CONFIG_HOME=/tmp/psysh HOME=/tmp \
   php artisan tinker --execute='...PHP here, escape every \$ as \\\$...'"
```

- Use `fn()` arrow closures ONLY. A multi-line `function () { }` closure parse-fails SILENTLY: prints nothing (reads as "zero rows"), writes an Error 0 row, and **emails all staff via the exception handler** — repeated probes can burn the 100/day Mailgun cap and kill prod email for 24h. Empty tinker output = check laravel.log for a psysh ParseErrorException before trusting the negative.
- No `mysql` client on the box; tinker is the only DB path.

**2. `storage/logs/laravel.log`** (EDT timestamps; the server clock/file mtimes are UTC) — stack traces the logs table doesn't carry.

**3. Apache logs** — `/var/log/apache2/other_vhosts_access.log` (UTC) gives path+referer for request-shaped errors (this is what proved the Evo feature-denial spam was a UI bug, not URL-forcing). The apache ERROR log is where PHP OOM fatals live — they never reach laravel.log.

---

## Phase 2: CLUSTER by root cause, not by title

- One upstream cause fans into many titles (the LeafLink `paid_at=4662` order produced "Fallback Sync Failed" x9 + "Marketplace Sync Failed" x6 + "Error 22007" x3 — ONE bug).
- Pre-filter known noise before ranking; check memory/runbooks for the current list (e.g. "Distru Count Error" = 5s count-probe timeouts, failure already soft).
- Check the recent diff and deploy times FIRST — a regression from yesterday's release is likelier than year-old code breaking spontaneously. Release dirs (`releases/<ts>`) are UTC; logs are EDT.

## Phase 3: FALSIFY each diagnosis

For every cluster's proposed root cause, run one live probe whose output would differ if the diagnosis is wrong (prod tinker query, apache log grep, targeted code read). Verify prod state ON prod — the local DB dump is stale and has produced false diagnoses before. Show raw probe output in the report.

---

## Phase 4: DELIVER — ranked report, then stop

Write `PROD-TRIAGE-<YYYY-MM-DD>.md` at the repo root (untracked). Per cluster, ranked most-severe first:

```markdown
## N. {Root cause, one line}  — {severity}
- **Signal**: {titles + row counts + window; note coalesced repeats}
- **Root cause**: {file:line evidence}
- **Falsification probe**: {what was run, raw output, why it held}
- **Proposed fix**: {one sentence + effort estimate}
- **Noise?**: {if arguably ignorable, say why}
```

Then STOP. Findings first; the user decides what gets fixed. If (and only if) this session's request already included fixing: proceed per confirmed cluster on its own branch via the `fix` skill's flow (falsification already done), full gate before declaring done, and deployment stays with the user.
