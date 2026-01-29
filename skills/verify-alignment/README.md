# Verify Alignment Skill - Package

A world-class Claude Code skill for verifying code alignment with BudTags coding standards, architectural patterns, and conventions using **progressive disclosure** for optimal performance.

---

## 🎯 What's New (v3.0)

**Major Database Schema Update + React 19 Patterns** (2025-12-13):

### Database Schema Changes (CRITICAL)
- ✅ **Table Renames**: `item_bom` → `item_package_recipes`, `bom_templates` → `package_recipe_templates`
- ✅ **New Tables**: `lab_companies`, `lab_facilities` - Lab integration system
- ✅ **New Columns**: `transporter_companies` and `metrc_facilities` updated with feature flags
- ✅ **MetrcFacility Architecture**: Central hub for organization, lab, and transporter facilities

### Lab/Transporter Integration Patterns (NEW)
- ✅ **LabCompany Model**: Global entity with COC generation, pickup requests
- ✅ **TransporterCompany Updates**: `enabled`, `contact_emails`, `request_pickup_enabled` columns
- ✅ **Feature Flags Pattern**: Boolean columns for toggling features
- ✅ **Email Distribution Pattern**: JSON array iteration for multi-recipient emails
- ✅ **Sandbox Filtering**: SF-SBX-* license exclusion for production

### Frontend Patterns (React 19)
- ✅ **Deferred Props Pattern**: `Inertia::defer()` for lazy-loading heavy data
- ✅ **TableSkeleton Component**: Loading state for deferred data
- ✅ **useTransition Pattern**: React 19 async state management for form submissions
- ✅ **Loading State Combination**: `isPending || mutation.isPending` pattern
- ✅ **Hooks-as-Services Clarification**: React Query hooks ARE the service layer (no separate services/ directory)
- ✅ **STALE_TIME Constants**: Centralized cache configuration in app.tsx

### Updated Pattern Files
- `patterns/database.md` - Schema change notes, new table patterns
- `patterns/frontend-critical.md` - Deferred props, useTransition, TableSkeleton
- `patterns/frontend-data-fetching.md` - Hooks-as-services architecture note
- `patterns/integrations.md` - Lab/Transporter company patterns (5 new patterns)
- `scenarios/migration.md` - New table patterns, BOM→recipe name mapping

---

## 📚 Previous Versions

### What Was New in v2.1

**React Query Pattern Expansion** (2025-11-20):

- ✅ **Composite hooks pattern** - Aggregating multiple queries (useQuickBooksData)
- ✅ **useLocalSync pattern** - Sync local state with server props for optimistic updates
- ✅ **Non-React-Query refresh hooks** - useRefreshMetrcItems/Locations pattern
- ✅ **Optimistic update callbacks** - onItemUpdated, onLocalUpdate conventions
- ✅ **Two-click confirmation pattern** - Dangerous action safety
- ✅ **Updated examples** - InventoryStatusMenu, ChangeItemModal references
- ✅ **Enhanced checklist** - Callback props, composite hooks, refresh patterns

**v2.0 Foundation** (2025-11-14):

- ✅ **57-74% context reduction** through modular pattern files
- ✅ **React Query vs Inertia guidance** with decision trees and examples
- ✅ **Inline editing patterns** documented (useInlineTextEdit, useInlineQuantityEdit)
- ✅ **Automated scans** for TypeScript, flash messages, React Query
- ✅ **Scenario templates** for common verification tasks
- ✅ **Comprehensive anti-pattern registry** from real-world findings

---

## 📁 Package Structure

```
verify-alignment/
├── skill.md                    # Main router (465 lines) - ENTRY POINT
├── README.md                   # This file
├── patterns/                   # Modular pattern files (8 files)
│   ├── backend-critical.md           # Security, org scoping, logging (200 lines)
│   ├── backend-style.md              # Method naming, request handling (150 lines)
│   ├── backend-flash-messages.md     # Flash message patterns (200 lines)
│   ├── database.md                   # Schema compliance, migrations (250 lines)
│   ├── frontend-critical.md          # Component patterns (200 lines)
│   ├── frontend-typescript.md        # Type safety + automated scans (250 lines)
│   ├── frontend-data-fetching.md     # React Query vs Inertia (150 lines)
│   └── integrations.md               # API service patterns (150 lines)
└── scenarios/                  # Verification templates (5 files)
    ├── controller-method.md          # Controller method checklist (100 lines)
    ├── migration.md                  # Migration/model checklist (100 lines)
    ├── react-component.md            # React component checklist (100 lines)
    ├── inertia-form.md               # Form submission checklist (100 lines)
    └── react-query-hook.md           # React Query hook checklist (100 lines)
```

**Total Size**: ~2400 lines across all files (vs 1168 lines in monolithic v1.0)
**Typical Context**: 300-700 lines (vs 1168 lines always loaded)

---

## 🚀 Purpose

This skill verifies code alignment with BudTags patterns including:

### Security & Multi-Tenancy (CRITICAL)
- Organization scoping enforcement
- Permission checks with comments
- Cross-org access prevention
- Active org ID access patterns

### Backend Standards
- Method naming (snake_case, verb-first, no store/destroy)
- Request handling (request() helper)
- Logging (LogService only, NEVER Log::)
- Flash messages (->with('message') not ->with('success'))
- Dependency injection patterns
- Service layer appropriateness

### Database & Models
- Schema compliance with database-schema.md
- Column types (UUID vs BIGINT, STRING vs INTEGER, DECIMAL precision)
- Foreign key cascade rules
- Index requirements
- Model $fillable and $casts accuracy
- Relationship correctness

### Frontend Standards
- Self-contained modal components
- TypeScript type safety (NO `any`)
- Toast notifications (typed methods, no alert())
- Inertia.js patterns (useForm)
- React Query vs Inertia decision (NEW)
- Data flow verification
- Inline editing patterns (NEW)

### Integration Patterns
- MetrcApi service usage (set_user(), license type restrictions)
- QuickBooksApi patterns
- Cache strategies
- Error handling

---

## 💡 Progressive Disclosure

**The skill loads ONLY the patterns relevant to your verification:**

### Quick Check (1-2 min)
**Load**: 1-2 pattern files
**Context**: ~300 lines (74% reduction)
**Use**: Single pattern or file verification

### Standard Review (5-10 min)
**Load**: 2-4 pattern files + scenario template
**Context**: ~500 lines (57% reduction)
**Use**: Feature implementation verification

### Comprehensive Audit (15+ min)
**Load**: All relevant patterns + full docs
**Context**: ~700 lines (40% reduction)
**Use**: Multi-file feature audit with automated scans

---

## 📖 Usage

### Method 1: Direct Invocation
```
Use the verify-alignment skill to check [file/feature]
```

### Method 2: Slash Command
```
/verify-alignment
```

### Example Workflows

**Pre-Implementation Review**:
```
User: Use verify-alignment skill to review my plan
User: I'm adding a new inventory adjustment feature
Skill: [Loads backend-critical.md, backend-style.md, scenario: controller-method.md]
Skill: [Reviews plan, identifies method naming issues, suggests corrections]
```

**Post-Implementation Review**:
```
User: /verify-alignment
Skill: What work should I verify?
User: Check app/Http/Controllers/InventoryController.php
Skill: [Loads relevant patterns, provides detailed compliance report]
```

**React Query Pattern Check**:
```
User: Use verify-alignment to check if I should use React Query or Inertia for this dashboard
Skill: [Loads frontend-data-fetching.md, provides decision tree and examples]
```

**TypeScript Compliance Audit**:
```
User: /verify-alignment
Skill: What work should I verify?
User: Run TypeScript type safety scan on resources/js/
Skill: [Loads frontend-typescript.md, runs automated scans, provides compliance report]
```

---

## 🔍 Pattern Files

### Backend Patterns

#### `backend-critical.md` (200 lines)
**When to Load**: ALWAYS for backend work
**Contains**:
- Organization scoping (SECURITY CRITICAL)
- Permission checks
- Logging (LogService only)
- Authorization with comments
- Active org access patterns
- Cross-org access prevention

**Critical Rules**:
- ALL queries scoped to active_org_id
- ALWAYS use LogService::store()
- NEVER load active_org relationship just for ID
- Comments explain security boundaries

#### `backend-style.md` (150 lines)
**When to Load**: ALWAYS for backend work
**Contains**:
- Method naming (snake_case, verb-first)
- Request handling (request() helper)
- Dependency injection (method-level preferred)
- Validation patterns
- Array composition (spread operator)
- Redirect patterns
- Service layer guidelines

**Key Rules**:
- Use create() not store(), delete() not destroy()
- Use request() helper, not Request injection
- Method-level DI unless service used by ALL methods

#### `backend-flash-messages.md` (200 lines)
**When to Load**: IF forms/redirects
**Contains**:
- Backend: ->with('message') pattern
- Frontend: MainLayout auto-handles
- Complex flash data patterns
- Automated scan commands
- Examples from QuickBooksController

**CRITICAL Pattern**:
- Backend: `->with('message')` NOT `->with('success')`
- Frontend: NO manual flash handling (MainLayout does it)

#### `database.md` (250 lines)
**When to Load**: Database/migration work
**Contains**:
- Schema compliance requirements
- Column types (UUID vs BIGINT, DECIMAL precision)
- Foreign key cascade rules
- Index requirements
- Model $fillable and $casts
- Relationship accuracy

**CRITICAL**: ALWAYS reference `.claude/docs/database-schema.md`

### Frontend Patterns

#### `frontend-critical.md` (200 lines)
**When to Load**: ALWAYS for frontend work
**Contains**:
- Self-contained modal components
- useForm hook pattern
- useModalState hook
- Toast notifications (typed methods)
- onSuccess/onError handling
- Data flow verification

**Key Rules**:
- Modals handle own form state and submission
- Use toast.error() NEVER alert()
- Verify data source in HandleInertiaRequests

#### `frontend-typescript.md` (250 lines)
**When to Load**: IF TypeScript issues
**Contains**:
- Type safety requirements
- NO `any` policy
- Error handling with `unknown`
- Automated scan commands
- Compliance thresholds

**Automated Scans**:
- Count `any` violations
- Find worst files
- Check for suppressions
- Per-file thresholds

#### `frontend-data-fetching.md` (150 lines)
**When to Load**: IF data fetching work
**Contains**:
- React Query vs Inertia decision tree
- Query hook patterns
- Mutation patterns
- Cache invalidation strategy
- License-scoped cache keys
- Stale time guidelines

**NEW Pattern**: React Query for read-heavy dashboards, Inertia for forms

### Integration Patterns

#### `integrations.md` (150 lines)
**When to Load**: IF API integration work
**Contains**:
- MetrcApi service patterns (set_user(), license type restrictions)
- QuickBooksApi patterns
- Error handling
- Cache strategies

**CRITICAL**: Metrc license types have different endpoint access

---

## 📋 Scenario Templates

### `controller-method.md` (100 lines)
**Use**: Verifying new controller methods
**Checklist**:
- Method naming & structure (8 checks)
- Request handling (5 checks)
- Organization scoping (4 checks)
- Authorization & security (4 checks)
- Logging (4 checks)
- Return & redirect (4 checks)

### `migration.md` (100 lines)
**Use**: Verifying migrations and models
**Checklist**:
- Schema compliance (4 checks)
- Foreign keys (4 checks)
- Indexes (3 checks)
- Column attributes (4 checks)
- Model fillable & casts (5 checks)

### `react-component.md` (100 lines)
**Use**: Verifying React components
**Checklist**:
- TypeScript types (5 checks)
- Modal components (7 checks)
- Error handling (4 checks)
- Data flow (4 checks)
- Performance (3 checks)

### `inertia-form.md` (100 lines)
**Use**: Verifying Inertia form submissions (MOST COMMON)
**Checklist**:
- Backend flash messages (4 checks)
- Frontend success handling (4 checks)
- Error handling (4 checks)
- TypeScript (2 checks)

### `react-query-hook.md` (100 lines)
**Use**: Verifying React Query usage
**Checklist**:
- Decision appropriateness (5 checks)
- Query hook structure (5 checks)
- Mutation structure (4 checks)
- Cache invalidation (4 checks)

---

## 🎨 What Gets Verified

### Critical Patterns (Always)
1. ✅ **Organization Scoping** - Security boundary enforcement
2. ✅ **Method Naming** - snake_case verb-first convention
3. ✅ **Logging** - LogService usage (never Log facade)
4. ✅ **Flash Messages** - Correct key usage (->with('message'))
5. ✅ **Permission Checks** - Authorization with comments

### Backend Patterns
- Service layer appropriateness
- Dependency injection approach
- Validation patterns
- Array composition (spread operator)
- Variable naming conventions

### Frontend Patterns
- Modal component self-containment
- TypeScript type safety
- React Query vs Inertia decision
- Inline editing patterns (useInlineTextEdit, useInlineQuantityEdit)
- Composite hooks (useQuickBooksData pattern)
- useLocalSync for optimistic updates
- Non-React-Query refresh hooks (useRefreshMetrcItems)
- Callback props for state updates (onItemUpdated, onLocalUpdate)
- Two-click confirmation for dangerous actions
- Cache invalidation strategy

### Database & Model Patterns
- Migration schema compliance
- Column types (UUID vs BIGINT, STRING vs INTEGER)
- Foreign key cascade rules
- Index placement
- Model relationships match schema

---

## 📊 Automated Verification

### TypeScript Type Safety Scan

```bash
# Count violations
grep -r "as any" resources/js --include="*.tsx" | wc -l

# Find worst files (>5 violations = critical)
grep -r "as any\|: any" resources/js --include="*.tsx" -c | sort -t: -k2 -nr | head -10
```

**Thresholds**:
- ✅ 0-10: Excellent
- ⚠️ 11-30: Acceptable
- ❌ >30: Critical

### Flash Message Pattern Scan

```bash
# Backend anti-patterns
grep -r "->with('success'" app/Http/Controllers --include="*.php"

# Frontend anti-patterns
grep -r "flash\?\.success" resources/js --include="*.tsx"
```

**Thresholds**:
- ✅ 0: Excellent
- ⚠️ 1-2: Acceptable
- ❌ >2: Critical

### React Query Usage Scan

```bash
# Find usage
grep -r "useQuery\|useMutation" resources/js --include="*.tsx"

# Check for global invalidation (anti-pattern)
grep -r "invalidateQueries()" resources/js --include="*.tsx"
```

---

## 📈 Performance Comparison

| Metric | v1.0 (Monolithic) | v2.0 (Progressive) | Improvement |
|--------|-------------------|-------------------|-------------|
| **Always Loaded** | 1168 lines | 465 lines (skill.md) | 60% reduction |
| **Quick Check** | 1168 lines | ~300 lines | 74% reduction |
| **Standard Review** | 1168 lines | ~500 lines | 57% reduction |
| **Comprehensive** | 1168 lines | ~700 lines | 40% reduction |
| **Pattern Count** | 8 patterns | 15+ patterns | 87% increase |
| **Maintainability** | Hard (one file) | Easy (modular) | 🎯 |

---

## 🆕 What's New in v2.1 (Latest)

### New Patterns Documented
1. **Composite Hooks** - useQuickBooksData pattern for aggregating multiple queries
2. **useLocalSync** - Sync local state with server props for optimistic updates
3. **Non-React-Query Refresh** - useRefreshMetrcItems/Locations pattern
4. **Callback Props** - onItemUpdated, onLocalUpdate conventions
5. **Two-Click Confirmation** - Safety pattern for dangerous mutations

### Enhanced Documentation
- 5 new advanced patterns in `frontend-data-fetching.md`
- Enhanced react-query-hook scenario with new checklist items
- Updated reference implementations with 10+ example files
- Clear distinction between React Query and non-React-Query refresh patterns

## 🆕 What's New in v2.0

### New Patterns Documented
1. **React Query vs Inertia** - Complete decision tree with examples
2. **Inline Editing** - useInlineTextEdit and useInlineQuantityEdit hooks
3. **Cache Invalidation** - Query key conventions, license-scoped caching
4. **Flash Messages** - Backend AND frontend patterns (most common anti-pattern)
5. **Optimistic Updates** - Pattern for instant UI feedback

### New Automated Scans
- TypeScript type safety scan with thresholds
- Flash message compliance scan
- React Query usage scan

### New Documentation
- `.claude/docs/frontend/data-fetching.md` - Complete React Query guide (400 lines)
- Enhanced `.claude/docs/frontend/components.md` - Inline editing section

---

## 🔧 When to Use This Skill

### Before Writing Code
- Review implementation approach
- Validate planned method names
- Check service layer decisions
- Verify proposed patterns

### After Writing Code
- Audit completed implementation
- Verify compliance with standards
- Identify technical debt
- Ensure security best practices

### During Code Review
- Validate pull request changes
- Check for pattern violations
- Ensure documentation alignment

### When Refactoring
- Verify refactor follows patterns
- Check for over-engineering
- Validate simplification approaches

---

## 📚 Related Skills

- **skill-builder** - For creating new Claude Code skills
- **metrc-api** - Metrc integration patterns
- **quickbooks** - QuickBooks integration patterns
- **zpl** - ZPL programming patterns

---

## 🎓 Support

For questions or improvements, reference:
- `.claude/SKILL_ANATOMY_GUIDE.md` - Skill design patterns
- `.claude/docs/` - Complete project documentation
- This README.md - Skill structure and usage

---

## 📝 Version History

**Version 3.0** (2025-12-13):
- Major database schema update (BOM→recipe, new lab_companies, lab_facilities)
- Added Lab/Transporter company integration patterns (5 new patterns)
- Added MetrcFacility architecture documentation
- Added Deferred Props pattern with Inertia::defer()
- Added React 19 useTransition pattern
- Added TableSkeleton pattern for loading states
- Clarified hooks-as-services architecture
- Documented STALE_TIME constants
- Added feature flags pattern
- Updated migration scenario with new table patterns

**Version 2.1** (2025-11-20):
- Added composite hooks pattern (useQuickBooksData)
- Added useLocalSync pattern for optimistic updates
- Added non-React-Query refresh hooks (useRefreshMetrcItems/Locations)
- Added callback props pattern (onItemUpdated, onLocalUpdate)
- Added two-click confirmation pattern
- Updated reference implementations section
- Enhanced react-query-hook scenario checklist
- Updated frontend-data-fetching.md with 5 new advanced patterns

**Version 2.0** (2025-11-14):
- Major refactoring with progressive disclosure
- Added 8 modular pattern files
- Added 5 scenario templates
- Added React Query vs Inertia guidance
- Added inline editing patterns
- Added automated scans
- Documented anti-patterns from research

**Version 1.0** (2025-11-04):
- Initial monolithic implementation
- 8 critical patterns
- Basic verification process
