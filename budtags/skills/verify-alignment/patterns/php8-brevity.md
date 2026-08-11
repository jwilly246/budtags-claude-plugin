# PHP 8 Brevity Patterns

**Source:** Nick's original code patterns, PHP 8.3 features
**Last Updated:** 2026-06-10
**Pattern Count:** 10 patterns (shorthand + functional style)

---

## Overview

These patterns encourage **shorter, cleaner code** using PHP 8 features. Nick's original code used many of these patterns - we should match his concise style while maintaining PHPStan level 10 compliance.

**Goal:** Code should feel native to Nick's style - short, clean, easy to read.

---

## Pattern 1: Null Coalesce (`??`)

**Rule:** Use `??` instead of `isset()` ternaries.

### ✅ CORRECT

```php
$name = $data['name'] ?? 'default';
$order_id = $values['order_id'] ?? null;
$driver_name = $driver['Name'] ?? null;

// Chained fallbacks
$license = session('license') ?? request()->input('license') ?? null;
```

### ❌ WRONG (Verbose)

```php
$name = isset($data['name']) ? $data['name'] : 'default';
$order_id = isset($values['order_id']) ? $values['order_id'] : null;
```

### Automated Scan

```bash
grep -rn "isset.*\?.*:" app --include="*.php"
```

---

## Pattern 2: Null Coalesce Assignment (`??=`)

**Rule:** Use `??=` for default value assignment.

### ✅ CORRECT

```php
$options['limit'] ??= 10;
$config['timeout'] ??= 30;
$data['status'] ??= 'pending';
```

### ❌ WRONG (Verbose)

```php
if (!isset($options['limit'])) {
    $options['limit'] = 10;
}

$options['limit'] = $options['limit'] ?? 10;
```

---

## Pattern 3: Arrow Functions (`fn()`)

**Rule:** Use `fn()` for simple one-expression closures.

### ✅ CORRECT

```php
// Collections
$slugs = $strains->map(fn($s) => $s->slug);
$active = $items->filter(fn($i) => $i->is_active);
$names = $users->pluck(fn($u) => $u->name);

// Validation rules
Rule::unique('strains')->where(fn($q) => $q->where('organization_id', $org->id));

// Lazy loading in Inertia
'packages' => fn() => $this->fetch_packages(),
```

### ❌ WRONG (Verbose)

```php
$slugs = $strains->map(function($s) {
    return $s->slug;
});

$active = $items->filter(function($i) {
    return $i->is_active;
});
```

### When to Use Full Closures

Use `function()` when:
- Multiple statements needed
- Need to use `use()` for variables (arrow functions auto-capture)
- Logic is complex enough to benefit from multiple lines

```php
// ✅ Full closure appropriate - multiple statements
$results = $items->map(function($item) {
    $processed = $this->processItem($item);
    LogService::store('Processed', "Item {$item->id}", $item);
    return $processed;
});
```

### Automated Scan

```bash
# Find simple closures that could be arrow functions
grep -rn "function\s*(\$[a-z])\s*{\s*return" app --include="*.php"
```

---

## Pattern 4: Null-Safe Operator (`?->`)

**Rule:** Use `?->` to chain through nullable values.

### ✅ CORRECT

```php
// Short and clean
$strains = request()->user()->active_org?->strains()->get() ?? collect();
$name = $user->profile?->display_name ?? $user->name;
$license = $org?->metrc_key?->license_number;

// With fallback
$templates = auth()->user()->active_org?->label_types()->orderBy('name')->get() ?? collect();
```

### ❌ WRONG (Verbose)

```php
$strains = null;
if (request()->user() && request()->user()->active_org) {
    $strains = request()->user()->active_org->strains()->get();
}
$strains = $strains ?? collect();

// Or the long ternary
$strains = request()->user()->active_org
    ? request()->user()->active_org->strains()->get()
    : collect();
```

### Common Pattern

```php
// Nick's pattern: optional chain + null coalesce for default
$items = $user->active_org?->items()->get() ?? collect();
```

---

## Pattern 5: Match Expression

**Rule:** Use `match()` for simple value mapping. Keep `switch` for complex logic.

### ✅ CORRECT

```php
// Simple value mapping
$color = match($status) {
    'active' => 'green',
    'pending' => 'yellow',
    'cancelled' => 'red',
    default => 'gray',
};

// With expressions
$message = match(true) {
    $count === 0 => 'No items',
    $count === 1 => 'One item',
    $count < 10 => 'A few items',
    default => 'Many items',
};
```

### ❌ WRONG (Verbose for simple cases)

```php
switch ($status) {
    case 'active':
        $color = 'green';
        break;
    case 'pending':
        $color = 'yellow';
        break;
    case 'cancelled':
        $color = 'red';
        break;
    default:
        $color = 'gray';
}
```

### When to Keep Switch

Use `switch` when:
- Multiple statements per case
- Fallthrough behavior needed
- Complex side effects in each case

### Automated Scan

```bash
grep -rn "switch\s*(" app --include="*.php"
```

---

## Pattern 6: Short Variable Names

**Rule:** Use short, conventional names in tight scopes.

### ✅ CORRECT (Nick's Style)

```php
// $v for validated data
$v = request()->validate([...]);

// $q for query closures
->where(fn($q) => $q->where('org_id', $org->id))

// $s, $t, $i for loop items
foreach($strains as $s) { ... }
foreach($templates as $t) { ... }
foreach($items as &$i) { ... }

// Short in compact scopes
$org = request()->user()->active_org;
$u = request()->user();
```

### ❌ WRONG (Unnecessarily verbose in tight scope)

```php
// Too long for simple validated data
$validatedData = request()->validate([...]);
$validatedFormData = request()->validate([...]);

// Too long in simple loops
foreach($strains as $strain) {
    echo $strain->name;  // Could be $s->name
}
```

### Balance Readability

- **Short names:** Tight scopes, loops, closures
- **Descriptive names:** Class properties, method parameters, complex logic

---

## Pattern 7: compact() for View Data

**Rule:** Use `compact()` for simple view/Inertia data.

### ✅ CORRECT

```php
// Simple data passing
$templates = $org->label_types()->get();
$strains = $org->strains()->get();
return view('templates.all', compact('templates', 'strains'));

// Inertia equivalent
return Inertia::render('Templates', compact('templates', 'strains'));
```

### ❌ WRONG (Verbose)

```php
return view('templates.all', [
    'templates' => $templates,
    'strains' => $strains,
]);
```

### When to Use Array Syntax

Use explicit array when:
- Keys differ from variable names
- Adding computed values
- Mixing with other data

```php
// ✅ Array syntax appropriate here
return Inertia::render('Dashboard', [
    'user' => $user,
    'item_count' => $items->count(),  // Computed
    'org_name' => $org->name,         // Key differs
]);
```

---

## Pattern 8: Named Arguments (PHP 8)

**Rule:** Use named arguments for clarity with many parameters or boolean flags.

### ✅ CORRECT

```php
// Clear what each parameter means
$label = new LabelOptions(
    type: $template,
    cannabinoids: 0,
    harvest: '',
    skip_lab_data: true,
    custom_value1: '',
    custom_value2: '',
);

// Especially for boolean flags
$api->fetch_packages(
    license: $license,
    force_refresh: true,
    include_inactive: false,
);
```

### ❌ WRONG (Unclear positional args)

```php
// What do these booleans mean?
$api->fetch_packages($license, true, false);

// Hard to remember parameter order
$label = new LabelOptions($template, 0, '', true, '', '');
```

---

## Pattern 9: Collection Pipelines, Never foreach to Build Data

**Rule:** If a `foreach` exists to BUILD a value (array, collection, sum, lookup map), it must be a collection pipeline. `foreach` is acceptable ONLY for pure side effects (dispatching jobs, writing logs, calling APIs) where no value is accumulated.

This is the #1 imperative pattern that keeps creeping back in. Flag it every time.

### ✅ CORRECT

```php
// Transform
$labels = $packages->map(fn($p) => $p->Label);

// Filter + transform
$active_names = $items->filter(fn($i) => $i->is_active)->pluck('name');

// Build a keyed lookup
$by_label = $packages->keyBy('Label');
$prices_by_sku = $rows->mapWithKeys(fn($r) => [$r->sku => $r->price]);

// Aggregate
$total = $lines->sum(fn($l) => $l->qty * $l->price);

// Group
$by_brand = $products->groupBy('brand_id');

// Flatten nested data
$all_tags = $orders->flatMap(fn($o) => $o->tags);

// Partition into two buckets
[$matched, $unmatched] = $items->partition(fn($i) => $i->metrc_id !== null);

// Plain arrays: wrap in collect() and pipe
$slugs = collect($raw_names)->map(fn($n) => Str::slug($n))->all();
```

### ❌ WRONG (Imperative accumulation)

```php
// Building an array with foreach
$labels = [];
foreach ($packages as $p) {
    $labels[] = $p->Label;
}

// Filtering with foreach + if
$active_names = [];
foreach ($items as $i) {
    if ($i->is_active) {
        $active_names[] = $i->name;
    }
}

// Building a lookup with foreach
$by_label = [];
foreach ($packages as $p) {
    $by_label[$p->Label] = $p;
}

// Accumulating a sum
$total = 0;
foreach ($lines as $l) {
    $total += $l->qty * $l->price;
}
```

### When foreach IS Acceptable

```php
// ✅ Pure side effects, nothing accumulated
foreach ($orders as $order) {
    SyncOrderJob::dispatch($order);
}

// ✅ But prefer each() only when chaining; standalone foreach is fine for side effects
```

**Litmus test:** Is there a variable initialized to `[]`, `0`, `''`, or `collect()` immediately before the loop, and appended/added to inside it? That is accumulation — rewrite as a pipeline.

### Automated Scan

```bash
# Empty-array init directly followed by foreach = accumulation smell
grep -rn -B1 "foreach" app --include="*.php" | grep -E "=\s*(\[\]|collect\(\)|0|'')\s*;" | head -20
```

---

## Pattern 10: Guard Clauses & Expression-Style Conditionals

**Rule:** No nested `if/else` pyramids and no `if/else` whose only job is assigning a variable. Use early returns (guard clauses) for preconditions, and ternary/`match()`/`??` for conditional values. Conditionals should produce VALUES, not mutate state across branches.

### ✅ CORRECT - Guard Clauses

```php
public function apply_receipt(Order $order): void
{
    if ($order->received_at) return;
    if (!$order->lines->count()) return;

    $org = $order->organization;
    if (!$org->hasFeature('marketplace-seller')) return;

    // Happy path at zero indentation
    $order->lines->each(fn($l) => $this->receive_line($l));
}
```

### ❌ WRONG - Nested Pyramid

```php
public function apply_receipt(Order $order): void
{
    if (!$order->received_at) {
        if ($order->lines->count()) {
            $org = $order->organization;
            if ($org->hasFeature('marketplace-seller')) {
                foreach ($order->lines as $l) {
                    $this->receive_line($l);
                }
            }
        }
    }
}
```

### ✅ CORRECT - Conditional Values as Expressions

```php
// Ternary for two-way
$status = $order->paid_at ? 'paid' : 'unpaid';

// match(true) for multi-way
$tier = match(true) {
    $total >= 10000 => 'platinum',
    $total >= 1000  => 'gold',
    default         => 'standard',
};

// ?? / ?-> for null-driven branching (see Patterns 1 & 4)
$display_name = $brand->parent?->name ?? $brand->name;
```

### ❌ WRONG - if/else Assignment

```php
// Branching just to assign — make it an expression
if ($order->paid_at) {
    $status = 'paid';
} else {
    $status = 'unpaid';
}

if ($total >= 10000) {
    $tier = 'platinum';
} elseif ($total >= 1000) {
    $tier = 'gold';
} else {
    $tier = 'standard';
}
```

### When if/else IS Acceptable

- Branches with multiple statements / genuinely different side effects
- Branches that need logging or early API calls per-branch
- Readability would suffer from forcing a `match(true)` (rare — be honest)

**Litmus test:** Does every branch end by assigning the SAME variable (or returning)? Then it's a value — use ternary/`match()`. Is the `else` just the happy path after a precondition check? Invert the condition and return early.

### Automated Scan

```bash
# if/else blocks that only assign one variable
grep -rn -A2 "} else {" app --include="*.php" | grep -E "^\s*\\\$[a-z_]+ =" | head -20

# Deep nesting (3+ indent levels of if)
grep -rn "            if (" app --include="*.php" | head -20
```

---

## Verification Checklist

When reviewing for brevity:

- [ ] No `isset($x) ? $x : $y` patterns (use `??`)
- [ ] No verbose null assignment checks (use `??=`)
- [ ] Simple closures use `fn()` not `function() { return; }`
- [ ] Nullable chains use `?->` not nested ifs
- [ ] Simple switch statements evaluated for `match()`
- [ ] Loop variables appropriately short in tight scopes
- [ ] Simple view data uses `compact()` where appropriate
- [ ] Boolean parameters use named arguments
- [ ] NO `foreach` that builds data — collection pipelines (`map`/`filter`/`reduce`/`keyBy`/`mapWithKeys`/`sum`/`groupBy`/`flatMap`) only
- [ ] NO if/else that only assigns a variable — ternary / `match()` / `??` instead
- [ ] Preconditions use early-return guard clauses, not nested if pyramids

---

## Automated Scans

Add to verification workflow:

```bash
# Find isset ternaries
grep -rn "isset.*\?.*:" app --include="*.php" | wc -l

# Find verbose closures
grep -rn "function\s*(\$[a-z])\s*{" app --include="*.php" | head -20

# Find switch statements to evaluate
grep -rn "switch\s*(" app --include="*.php" | wc -l

# Find long null checks
grep -rn "if\s*(\!\s*\$" app --include="*.php" | head -20
```

### Thresholds

| Pattern | Target | Acceptable | Needs Work |
|---------|--------|------------|------------|
| isset ternaries | 0 | 1-5 | >5 |
| verbose closures | 0 | 1-10 | >10 |
| switch (eval needed) | N/A | N/A | Evaluate each |

---

## Related Patterns

- **backend-style.md** - Method naming, request handling
- **backend-critical.md** - Security patterns (take priority)
- `.claude/docs/backend/coding-style.md` - Complete style guide
