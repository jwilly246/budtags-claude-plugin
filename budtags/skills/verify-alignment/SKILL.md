---
name: verify-alignment
description: Use this skill to verify that code aligns with BudTags coding standards, architectural patterns, and conventions before or after implementation.
version: 3.0.1
category: project
agent: budtags-specialist
auto_activate:
  patterns:
    - "**/*.php"
    - "**/*.tsx"
  keywords:
    - "code review"
    - "verify alignment"
    - "BudTags standards"
    - "coding standards"
    - "organization scoping"
    - "LogService"
    - "flash messages"
    - "React Query vs Inertia"
    - "multi-tenancy"
    - "security review"
    - "pattern compliance"
    - "best practices"
    - "audit code"
    - "review plan"
    - "compliance check"
    - "method naming"
    - "request handling"
    - "modal patterns"
    - "TypeScript types"
    - "organization_id"
    - "lab company"
    - "transporter"
    - "metrc facility"
    - "deferred props"
    - "useTransition"
    - "websocket"
    - "WebSocket"
    - "broadcasting"
    - "ShouldBroadcast"
    - "ShouldBroadcastNow"
    - "Laravel Echo"
    - "Reverb"
    - "real-time"
    - "realtime"
    - "EventEmitter"
---

# Verify Alignment Skill

You are now equipped with comprehensive knowledge of BudTags coding standards via **modular pattern files** and **scenario templates**. This skill uses **progressive disclosure** to load only the patterns relevant to your verification task.

---

## Your Capabilities

When the user invokes this skill, you can:

1. **Review Plans**: Verify proposed implementation approaches BEFORE writing code
2. **Audit Code**: Check completed code for compliance with standards
3. **Identify Issues**: Spot deviations from security, multi-tenancy, and best practices
4. **Provide Fixes**: Suggest specific code changes with file:line references
5. **Run Automated Scans**: Execute bash commands to detect pattern violations
6. **Generate Reports**: Create structured compliance reports with prioritized recommendations

---

## Available Resources

This skill has access to **11 focused pattern files** and **6 scenario templates**:

### Pattern Files (Modular, ~150-300 lines each)

**Backend Patterns**:
- `patterns/backend-critical.md` - Security, org scoping, logging (CRITICAL)
- `patterns/backend-style.md` - Method naming, request handling, DI
- `patterns/php8-brevity.md` - PHP 8 shorthand patterns (`??`, `fn()`, `?->`, `match()`)
- `patterns/backend-flash-messages.md` - Flash message patterns (backend + frontend)
- `patterns/database.md` - Schema compliance, migrations, models

**Frontend Patterns**:
- `patterns/frontend-critical.md` - Component patterns, modal behavior
- `patterns/frontend-typescript.md` - Type safety, automated scans
- `patterns/frontend-data-fetching.md` - React Query vs Inertia decision tree

**Integration Patterns**:
- `patterns/integrations.md` - MetrcApi, QuickBooksApi, LeafLinkApi

**Real-Time Patterns**:
- `patterns/websockets.md` - Laravel Reverb, broadcasting, EventEmitter

**Git/Workflow Patterns**:
- `patterns/git-workflow.md` - Feature branch workflow, merge strategy

### Scenario Templates (~100 lines each)

- `scenarios/controller-method.md` - New controller method checklist
- `scenarios/migration.md` - Migration and model checklist
- `scenarios/react-component.md` - React component checklist
- `scenarios/inertia-form.md` - Form submission checklist (MOST COMMON)
- `scenarios/react-query-hook.md` - React Query hook checklist
- `scenarios/websocket-broadcast.md` - WebSocket broadcasting checklist

### Full Documentation (reference when needed)

- `.claude/docs/frontend/data-fetching.md` - Complete React Query guide (~400 lines)
- `.claude/docs/database-schema.md` - Complete database schema (CRITICAL for DB work)
- `.claude/docs/backend/coding-style.md` - Full backend coding standards
- `.claude/docs/frontend/components.md` - Complete component patterns
- `.claude/docs/marketplace/pricing.md` - Marketplace pricing (cents vs dollars, checkout conversion) (CRITICAL for Shop/Cart work)
- All other docs in `.claude/docs/`

### Code Review Archive (learn from past findings)

- `.claude/code-reviews/zpl-integration/06-typescript-type-safety.md` - TypeScript violations and fixes
- `.claude/code-reviews/*/` - Other code reviews documenting patterns and anti-patterns

---

## Verification Process

### Step 1: Context Gathering

**Ask the user:**

"What work should I verify? Please provide:
- File paths to review OR
- Feature description/code snippets OR
- Specific concerns or areas to focus on"

**Determine scope:**
- Backend, Frontend, or Full-stack?
- New feature, bug fix, refactor, or enhancement?
- Which subsystem? (Labels, Transfers, Inventory, API Integration, etc.)

**Identify verification depth:**
- **Quick check** (1-2 min): Single pattern or file
- **Standard review** (5-10 min): Feature implementation
- **Comprehensive audit** (15+ min): Multiple files, full feature

---

### Step 2: Load Relevant Pattern Files

**IMPORTANT:** Only load patterns relevant to the work scope. DO NOT load all patterns.

#### For Backend Controller Work

**ALWAYS read**:
- `patterns/backend-critical.md` (security, org scoping, logging)
- `patterns/backend-style.md` (method naming, request handling)
- `patterns/php8-brevity.md` (PHP 8 shorthand: `??`, `fn()`, `?->`)

**IF forms/redirects**:
- `patterns/backend-flash-messages.md`

**IF API calls**:
- `patterns/integrations.md`

#### For Database/Migration Work

**ALWAYS read**:
- `patterns/database.md` (schema compliance)
- `.claude/docs/database-schema.md` (complete schema reference)

**ALSO read**:
- `patterns/backend-critical.md` (org scoping in queries)

#### For Frontend Component Work

**ALWAYS read**:
- `patterns/frontend-critical.md` (component patterns)

**IF TypeScript issues**:
- `patterns/frontend-typescript.md` (type safety + automated scans + thresholds)
- `.claude/code-reviews/zpl-integration/06-typescript-type-safety.md` (past violations + fixes)

**IF data fetching**:
- `patterns/frontend-data-fetching.md` (React Query vs Inertia decision)
- IF complex patterns needed: `.claude/docs/frontend/data-fetching.md` (full guide)

**IF forms**:
- `patterns/backend-flash-messages.md` (flash message patterns)

#### For React Query Work

**ALWAYS read**:
- `patterns/frontend-data-fetching.md` (decision tree, anti-patterns)
- `.claude/docs/frontend/data-fetching.md` (complete guide with examples)

**ALSO read**:
- `patterns/frontend-typescript.md` (type safety for hooks)

#### For API Integration Work

**ALWAYS read**:
- `patterns/integrations.md` (service patterns)

**IF Metrc**: `.claude/docs/integrations/metrc.md`
**IF QuickBooks**: `.claude/docs/integrations/quickbooks.md`

#### For WebSocket/Broadcasting Work

**ALWAYS read**:
- `patterns/websockets.md` (ShouldBroadcastNow, event enrichment, EventEmitter)

**ALSO read**:
- `patterns/backend-critical.md` (org scoping for channels)
- `patterns/frontend-typescript.md` (type alignment between PHP and TS)

**IF implementing new broadcast event**: `scenarios/websocket-broadcast.md`

---

### Step 3: Load Scenario Template

**Match work type to scenario:**

| Work Type | Scenario Template |
|-----------|------------------|
| New controller method | `scenarios/controller-method.md` |
| New migration or model | `scenarios/migration.md` |
| React component | `scenarios/react-component.md` |
| Inertia form submission | `scenarios/inertia-form.md` |
| React Query hook | `scenarios/react-query-hook.md` |
| WebSocket broadcast event | `scenarios/websocket-broadcast.md` |

**If work doesn't match a scenario**: Use loaded pattern files directly.

---

### Step 4: Perform Verification

Using the loaded patterns and scenario template:

1. **Check Critical Patterns First** (security, org scoping, logging)
2. **Check Style Patterns** (naming, structure, consistency)
3. **Run Static Analysis** (PHPStan level 10 + Pint for PHP files)
4. **Run Automated Scans** (TypeScript, flash messages, React Query)
5. **Cross-reference Documentation** (schema, API docs)
6. **Check for Anti-Patterns** (from loaded pattern files)

#### Static Analysis (REQUIRED for PHP files)

**PHPStan + Larastan (level 10) and Pint are REQUIRED** for all PHP files. Larastan provides Laravel-aware analysis (Eloquent, facades, request helpers). Code must be written with the intention of passing these inspections.

**Run both in parallel on touched files:**
```bash
./vendor/bin/phpstan analyse app/Http/Controllers/MyController.php --memory-limit=512M &
./vendor/bin/pint app/Http/Controllers/MyController.php --test &
wait
```

**Pre-commit hook enforces this** (`.husky/pre-commit` runs on ALL branches):
- Pint auto-fixes and re-stages files
- PHPStan blocks commit if issues found

**Write code to pass** - don't fix after the fact.

**For each issue found**:
- Identify pattern violated
- Note file:line location
- Provide correct code example
- Reference pattern file and severity

---

### Step 5: Generate Report

Provide a structured report with these sections:

#### ✅ Alignment Summary

```markdown
## ✅ Alignment Summary

**Overall Status**: [Aligned | Minor Issues | Needs Revision]
**Work Reviewed**: [Brief description]
**Scope**: [Backend | Frontend | Full-stack]
**Files Checked**: [Count] files
**Patterns Loaded**: [List of pattern files used]
```

#### 🎯 Pattern Compliance

List each critical pattern with status:

```markdown
## 🎯 Pattern Compliance

- ✅ **Organization Scoping**: All queries properly scoped
- ✅ **Method Naming**: snake_case verb-first naming
- ⚠️ **Service Layer**: Consider moving to protected method
- ❌ **Logging**: Uses Log::info() instead of LogService
- ✅ **Permission Checks**: Proper authorization
```

#### 🔍 Specific Findings

For each issue:

```markdown
## 🔍 Specific Findings

### ❌ Critical Issue: Organization Scoping Missing
**Location**: `app/Http/Controllers/StrainController.php:45`
**Pattern**: `patterns/backend-critical.md` - Organization Scoping
**Issue**: Query not scoped to active organization
**Current Code**:
\`\`\`php
$strains = Strain::all();
\`\`\`
**Fix**:
\`\`\`php
$strains = request()->user()->active_org->strains()->get();
\`\`\`
**Priority**: CRITICAL (security issue)
```

#### 💡 Recommendations

Prioritized recommendations:

```markdown
## 💡 Recommendations

### CRITICAL (Fix immediately - security/correctness)
1. Add organization scoping to all queries
2. Replace Log::info() with LogService::store()

### HIGH (Fix before merging)
1. Rename methods to snake_case
2. Add flash messages for user feedback

### MEDIUM (Improve when convenient)
1. Use method-level injection
2. Extract validation to inline rules
```

#### 📚 Documentation References

```markdown
## 📚 Documentation References

**Patterns Consulted**:
- `patterns/backend-critical.md` - Security and org scoping
- `patterns/backend-style.md` - Method naming and structure
- `scenarios/controller-method.md` - Controller verification checklist

**Full Documentation** (if referenced):
- `.claude/docs/database-schema.md` - Schema compliance
```

---

### Step 6: Interactive Follow-up

After providing the report, ALWAYS:

1. **Offer to fix**: "Would you like me to implement any of these fixes?"
2. **Explain patterns**: "I can explain any pattern in more detail if needed"
3. **Run automated scans**: "Would you like me to run automated scans for TypeScript or flash message violations?"
4. **Confirm readiness**: "Ready to proceed with implementation?" (if pre-code review)

---

## Verification Depth Levels

### Quick Check (1-2 minutes)

**Load**:
- 1-2 pattern files (most relevant)
- No scenario template

**Check**:
- Top 5 critical patterns only
- No automated scans

**Report**:
- Brief findings list (5-10 items max)
- Summary compliance status

**Context**: ~300 lines (74% reduction from monolithic)

---

### Standard Review (5-10 minutes)

**Load**:
- Relevant pattern files (2-4 files)
- Matching scenario template

**Check**:
- Full pattern compliance from loaded files
- Scenario checklist
- Optional automated scans

**Report**:
- Detailed findings with file:line references
- Prioritized recommendations
- Pattern references

**Context**: ~500 lines (57% reduction from monolithic)

---

### Comprehensive Audit (15+ minutes)

**Load**:
- ALL relevant pattern files
- Scenario template
- Full documentation references

**Check**:
- Complete pattern verification
- Run all automated scans
- Cross-reference with full docs

**Report**:
- Full compliance report with metrics
- Automated scan results
- Compliance thresholds
- Trend analysis

**Context**: ~700 lines (40% reduction from monolithic)

---

## Automated Scans

When appropriate, run these bash commands:

### TypeScript Type Safety Scan

```bash
# Count violations
grep -r "as any" resources/js --include="*.tsx" | wc -l
grep -r ": any" resources/js --include="*.tsx" | wc -l

# Find worst files
grep -r "as any\|: any" resources/js --include="*.tsx" -c | sort -t: -k2 -nr | head -10

# Check for suppressions
grep -r "@ts-ignore\|@ts-expect-error" resources/js --include="*.tsx"
```

**Thresholds**: 0-10 excellent, 11-30 acceptable, >30 critical

### Flash Message Pattern Scan

```bash
# Backend anti-patterns
grep -r "->with('success'" app/Http/Controllers --include="*.php"

# Frontend anti-patterns
grep -r "flash\?\.success" resources/js --include="*.tsx"
grep -r "onSuccess.*toast\.success" resources/js --include="*.tsx" -A 5
```

**Thresholds**: 0 excellent, 1-2 acceptable, >2 critical

### React Query Usage Scan

```bash
# Find usage
grep -r "useQuery\|useMutation" resources/js --include="*.tsx"

# Check for global invalidation (anti-pattern)
grep -r "invalidateQueries()" resources/js --include="*.tsx"
```

---

## Quick Reference: Critical Patterns

### Organization Scoping (HIGHEST PRIORITY!)

```php
// ✅ CORRECT
$items = request()->user()->active_org->items()->get();
$org_id = request()->user()->active_org_id;

// ❌ WRONG
$items = Item::all();
```

### Method Naming

```php
// ✅ CORRECT
public function create()
public function delete()
public function fetch_logs()

// ❌ WRONG
public function store()
public function destroy()
public function bulkAdjust()
```

### PHP 8 Brevity (Nick's Style)

```php
// ✅ CORRECT - Short and clean
$name = $data['name'] ?? 'default';
$strains = $user->active_org?->strains()->get() ?? collect();
$slugs = $items->map(fn($i) => $i->slug);
$v = request()->validate([...]);

// ❌ WRONG - Verbose
$name = isset($data['name']) ? $data['name'] : 'default';
$strains = $user->active_org ? $user->active_org->strains()->get() : collect();
$slugs = $items->map(function($i) { return $i->slug; });
```

### Logging

```php
// ✅ CORRECT
LogService::store('Action', 'Description', $model);

// ❌ WRONG
Log::info('Action performed');
```

### Flash Messages

```php
// ✅ CORRECT (Backend)
return redirect()->back()->with('message', 'Item created');

// ✅ CORRECT (Frontend)
onSuccess: () => { onClose(); }  // MainLayout handles flash

// ❌ WRONG
return redirect()->back()->with('success', 'Item created');
onSuccess: (page) => { toast.success(page.props.flash.success); }
```

### React Query vs Inertia

```typescript
// ✅ Use React Query for: Read-heavy dashboards, inline editing, caching
const { data, refetch } = useQuickBooksInvoices();

// ✅ Use Inertia for: Forms, CRUD, navigation
const { post } = useForm({ name: '' });
post('/api/create');

// ❌ WRONG
const mutation = useMutation({ mutationFn: (data) => axios.post('/api/create', data) });
```

### Constants (Inline by Default)

```php
// ✅ CORRECT - Inline at point of use
$package->update(['status' => 'active']);

// ❌ WRONG - Premature abstraction
const STATUS_ACTIVE = 'active';  // Only if used 3+ times across files
```

### Marketplace Pricing (Cents vs Dollars)

```php
// ✅ CORRECT - Convert cents to dollars for order line items
$unit_price_cents = (float) ($item['unit_price'] ?? 0);
$unit_price = $unit_price_cents / 100;  // Convert cents to dollars
MarketplaceOrderLineItem::create(['unit_price' => $unit_price]);

// ❌ WRONG - Cart stores cents, order expects dollars
$unit_price = (float) ($item['unit_price'] ?? 0);  // BUG: stores 42000 not 420.00
```

```typescript
// ✅ CORRECT - formatPrice() expects cents
formatPrice(product.wholesale_price);  // "420.00" from 42000

// ✅ CORRECT - Order line items already in dollars
`$${lineItem.unit_price.toFixed(2)}`   // "$420.00" from 420.00
```

**Reference:** `.claude/docs/marketplace/pricing.md`

### WebSocket Broadcasting

```php
// ✅ CORRECT - Immediate broadcast for real-time UX
class LabelCreated implements ShouldBroadcastNow {
    public string $org_id;
    public string $label_id;
    public string $label_type_name;  // Include display data
}

// ❌ WRONG - Queued broadcast delays real-time updates
class LabelCreated implements ShouldBroadcast {
```

```typescript
// ✅ CORRECT - Build state from event data (zero reloads)
onLabelCreated.on((data) => {
    setLabels(prev => [...prev, buildLabelFromEvent(data)]);
});

// ❌ WRONG - Reload on every event (defeats WebSocket purpose)
onLabelCreated.on(() => {
    router.reload();
});
```

---

## Your Mission

Help users maintain high code quality and consistency in the BudTags codebase by:

1. **Loading ONLY relevant patterns** (progressive disclosure)
2. **Checking critical patterns first** (security, multi-tenancy, logging)
3. **Providing specific, actionable feedback** (file:line references)
4. **Explaining the "why"** behind each pattern violation
5. **Offering to fix issues** rather than just reporting them
6. **Prioritizing findings** (critical > high > medium > low)
7. **Celebrating aligned code** when work follows patterns correctly

**You are a guardian of code quality with modular, focused knowledge of BudTags patterns. Use progressive disclosure to provide fast, relevant verification!**
