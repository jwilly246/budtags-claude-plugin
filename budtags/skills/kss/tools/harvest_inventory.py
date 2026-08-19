#!/usr/bin/env python3
"""Live wire inventory of every KSS test-API endpoint.

For each endpoint: pull up to MAX_PAGES pages at PageSize=500 (explicit status
filters so silent defaults hide nothing), flatten records with dot-paths, and
record per field: presence count, null count, observed JSON types, and up to 3
distinct truncated examples. Output: one JSON inventory file.

GET-only. ~50 requests total against a 1028/hr limit.
"""
import json
import urllib.request
import urllib.error
import os
import time

KEY = open('/Users/budtags/Desktop/budtags/meeting-plans-endo-2026-08-12/ksskey').read().strip()
BASE = 'https://api.test.kssdata.com/api/v1'
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory')
os.makedirs(OUTDIR, exist_ok=True)
MAX_PAGES = 2
REQUESTS_MADE = 0


def get(path, params=None):
    global REQUESTS_MADE
    qs = '&'.join(f'{k}={v}' for k, v in (params or {}).items())
    url = f'{BASE}{path}' + (f'?{qs}' if qs else '')
    req = urllib.request.Request(url, headers={'x-api-key': KEY})
    REQUESTS_MADE += 1
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except Exception:
            body = None
        return e.code, body
    finally:
        time.sleep(0.15)


def flatten(record, prefix=''):
    """Yield (dotpath, value) pairs; arrays of objects recurse as path[]."""
    for k, v in record.items():
        path = f'{prefix}{k}'
        if isinstance(v, dict):
            yield from flatten(v, path + '.')
        elif isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
            yield (path, f'<array of {len(v)} objects>')
            for item in v:
                yield from flatten(item, path + '[].')
        else:
            yield (path, v)


def jtype(v):
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'boolean'
    if isinstance(v, (int, float)):
        return 'number'
    if isinstance(v, list):
        return 'array'
    return 'string'


def inventory_records(records):
    fields = {}
    n = len(records)
    for rec in records:
        seen_paths = set()
        for path, val in flatten(rec):
            base = path
            info = fields.setdefault(base, {'count': 0, 'nulls': 0, 'types': set(), 'examples': []})
            if base not in seen_paths:
                info['count'] += 1
                seen_paths.add(base)
            t = jtype(val)
            info['types'].add(t)
            if t == 'null':
                info['nulls'] += 1
            else:
                s = str(val)[:60]
                if s not in info['examples'] and len(info['examples']) < 3:
                    info['examples'].append(s)
    out = {}
    for name, info in sorted(fields.items()):
        out[name] = {
            'present': info['count'],
            'of': n,
            'nulls': info['nulls'],
            'types': sorted(info['types'] - {'null'}) or ['null'],
            'examples': info['examples'],
        }
    return out


def walk(path, params=None, pages=MAX_PAGES):
    params = dict(params or {})
    params.setdefault('PageSize', 500)
    all_records = []
    meta = {'statuses': [], 'has_next_final': None}
    for page in range(1, pages + 1):
        params['Page'] = page
        status, body = get(path, params)
        meta['statuses'].append(status)
        if status != 200 or not isinstance(body, dict):
            meta['error_body'] = body
            break
        data = body.get('Data', [])
        all_records.extend(data)
        meta['has_next_final'] = body.get('HasNextPage')
        if not body.get('HasNextPage'):
            break
    return all_records, meta


results = {}

def run(name, path, params=None, pages=MAX_PAGES):
    records, meta = walk(path, params, pages)
    results[name] = {
        'path': path,
        'params': {k: v for k, v in (params or {}).items()},
        'sampled': len(records),
        'http': meta['statuses'],
        'has_next_after_sample': meta['has_next_final'],
        'error_body': meta.get('error_body'),
        'fields': inventory_records(records),
    }
    print(f"{name:35s} {meta['statuses']} sampled={len(records)} hasNext={meta['has_next_final']}")
    return records


# ---- list endpoints (explicit status params so silent defaults hide nothing) ----
states = run('states', '/states')
locations = run('locations', '/locations')
salesReps = run('salesReps', '/salesReps')
users = run('users', '/users', {'Active': 'true,false'})
suppliers = run('suppliers', '/suppliers', {'Active': 'true,false'})
suppliers_ct = run('suppliers_creditTerms', '/suppliers/creditTerms')
vendors = run('vendors', '/vendors', {'Active': 'true,false'})
productCategories = run('productCategories', '/productCategories')
products = run('products', '/products', {'Statuses': '0,1,2,3,4,5'})
customers = run('customers', '/customers', {'AccountStatuses': 'Active,Inactive,OutOfBus'})
customers_ct = run('customers_creditTerms', '/customers/creditTerms')
deliveryDays = run('deliveryDays', '/deliveryDays')
allocations = run('allocations', '/allocations')
arAging = run('arAging', '/arAging')
inventory = run('inventory', '/inventory')
inventory_batches = run('inventory_batches', '/inventory/batches')
retailerInventory = run('retailerInventory', '/retailerInventory')
invoices = run('invoices', '/invoices', {'Statuses': '1,2,3,4,5,7'})
invoices_ct = run('invoices_creditTerms', '/invoices/creditTerms')
menuPromotions = run('menuPromotions', '/menuPromotions')
promotionsProducts = run('promotionsProducts', '/promotionsProducts')
payments_types = run('payments_types', '/payments/types')
payments = run('payments', '/payments')
payments_openInvoices = run('payments_openInvoices', '/payments/openInvoices')
payments_applications = run('payments_applications', '/payments/applications')
purchases = run('purchases', '/purchases',
                {'Statuses': 'New,Accepted,Received,Confirmed,Verified'})

# ---- dependent endpoints, seeded from list results ----
if customers:
    cids = ','.join(str(c['CustomerID']) for c in customers[:20])
    run('customerPricing', '/customerPricing', {'CustomerIDs': cids}, pages=1)
    run('customers_detail', f"/customers/{customers[0]['CustomerID']}", pages=1)
if invoices:
    iids = ','.join(str(i['InvoiceID']) for i in invoices[:20] if 'InvoiceID' in i)
    if iids:
        run('invoiceTransactions', '/invoiceTransactions',
            {'InvoiceIDs': iids, 'Statuses': '1,2,3,4,5,7'}, pages=1)
        run('invoiceCOAs', '/invoiceCOAs', {'InvoiceIDs': iids}, pages=1)
        run('invoices_detail', f"/invoices/{invoices[0]['InvoiceID']}", pages=1)
        run('invoiceTransactions_detail',
            f"/invoiceTransactions/{invoices[0]['InvoiceID']}", pages=1)
        run('invoiceCOAs_detail', f"/invoiceCOAs/{invoices[0]['InvoiceID']}", pages=1)
if purchases:
    pids = ','.join(str(p['PurchaseID']) for p in purchases[:20])
    run('purchaseTrans', '/purchaseTrans', {'PurchaseIDs': pids}, pages=1)
    run('purchases_detail', f"/purchases/{purchases[0]['PurchaseID']}", pages=1)
if locations:
    run('locations_detail', f"/locations/{locations[0]['LocationID']}", pages=1)
if suppliers:
    run('suppliers_detail', f"/suppliers/{suppliers[0]['SupplierID']}", pages=1)
if users:
    run('users_detail', f"/users/{users[0]['UserID']}", pages=1)
if products:
    run('products_detail', f"/products/{products[0]['ProductID']}", pages=1)

with open(os.path.join(OUTDIR, 'wire-inventory.json'), 'w') as f:
    json.dump(results, f, indent=1, default=str)

print(f'\nTotal HTTP requests: {REQUESTS_MADE}')
print(f'Endpoints inventoried: {len(results)}')
print('Wrote', os.path.join(OUTDIR, 'wire-inventory.json'))
