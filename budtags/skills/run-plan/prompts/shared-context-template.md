# Shared Context

Cross-agent continuity log for work unit execution.

**READ before starting. UPDATE after completing. TRUST this completely - do not re-explore the codebase.**

---

## Critical Patterns (ALWAYS FOLLOW)

### Organization Scoping (SECURITY)
```php
// ALWAYS scope queries to active organization
$items = request()->user()->active_org->items()->get();
// or
->where('organization_id', request()->user()->active_org_id)
```

### Method Naming (snake_case, verb-first)
```php
public function create() {}      // not store()
public function delete() {}      // not destroy()
public function fetch_all() {}   // not getAll() or index()
public function update_status() {}
```

### Request Handling
```php
// Use request() helper directly
public function create() {
    $values = request()->validate([...]);
}
// NOT: public function create(Request $request)
```

### Logging
```php
LogService::store('Action', 'Description', $model);
// NEVER use Log:: facade
```

### Flash Messages
```php
->with('message', 'Item created');  // 'message' key
// NOT: ->with('success', '...')
```

### Forms (Frontend)
```tsx
import { useForm } from '@inertiajs/react';
const { data, setData, post, processing, errors } = useForm({...});
// NEVER useState for form fields, NEVER axios for mutations
```

---

## Core PHP Services (Always Available)

| Service | Location | Purpose |
|---------|----------|---------|
| LogService | `app/Services/LogService.php` | Activity logging - ALWAYS use this |
| CacheService | `app/Services/CacheService.php` | Cache operations |

---

## Available UI Components (Core)

**USE THESE - never create new basic components.**

| Component | Import | Key Props | Notes |
|-----------|--------|-----------|-------|
| Button | `@/Components/Button` | `primary`, `danger`, `disabled` | No `type` attr |
| TextInput | `@/Components/Inputs` | `value`, `onChange`, `errors` | |
| TextArea | `@/Components/Inputs` | `value`, `onChange`, `errors` | |
| Select | `@/Components/Inputs` | `value`, `onChange`, `options` | |
| Checkbox | `@/Components/Inputs` | `checked`, `onChange` | |
| Badge | `@/Components/Badge` | `color`, `children` | Status indicators |
| DataTable | `@/Components/DataTable` | `columns`, `data` | Tables |
| ToggleSwitch | `@/Components/ToggleSwitch` | `checked`, `onChange` | |
| FuzzyPicker | `@/Components/FuzzyPicker` | `options`, `value`, `onChange` | Searchable select |
| DateRangePicker | `@/Components/DateRangePicker` | `startDate`, `endDate` | |
| Modal | `@/Components/Modal` | `isOpen`, `onClose`, `title` | Modal owns form |
| WarningBox | `@/Components/WarningBox` | `message`, `type` | Alerts |
| BoxMain | `@/Components/BoxMain` | `children` | Content container |
| Headline | `@/Components/Headline` | `children`, `level` | Section headers |

---

## Layouts (Always Available)

| Layout | Location | Use For |
|--------|----------|---------|
| AuthenticatedLayout | `@/Layouts/AuthenticatedLayout` | All authenticated pages |
| GuestLayout | `@/Layouts/GuestLayout` | Login, register, public pages |

---

## Type Locations

| Type Category | Location | Notes |
|---------------|----------|-------|
| Global types | `resources/js/types/index.d.ts` | Shared interfaces |
| Page props | `resources/js/types/index.d.ts` | PageProps, User, etc. |
| Feature types | `resources/js/types/{feature}.d.ts` | Feature-specific |

---

## Test Patterns

| Pattern | Location | Notes |
|---------|----------|-------|
| Base TestCase | `tests/TestCase.php` | Extend this for all tests |
| Factories | `database/factories/` | Use for model creation |
| Test traits | `tests/Traits/` | Reusable test helpers |

**Test naming:** `test_user_can_create_item()` (snake_case with test_ prefix)

---

## Domain-Specific Components (from create-plan)

| Component | Location | Key Props | Notes |
|-----------|----------|-----------|-------|
<!-- Pre-populated by decompose-plan -->

---

## Existing TypeScript Types (from create-plan)

| Type/Interface | Location | Description |
|----------------|----------|-------------|
<!-- Pre-populated by decompose-plan -->

---

## Existing PHP Services (from create-plan)

| Service | Location | Purpose |
|---------|----------|---------|
<!-- Pre-populated by decompose-plan -->

---

## Existing Routes (from create-plan)

| Method | URI | Controller@Method | Notes |
|--------|-----|-------------------|-------|
<!-- Pre-populated by decompose-plan -->

---

## Naming Conventions (Feature-Specific)

| Domain | Pattern | Example | Set By |
|--------|---------|---------|--------|
| Cache keys | | | |
| URL paths | | | |
| TypeScript types | | | |

---

## Cache Keys (created)

| Key | Purpose | TTL | Set By |
|-----|---------|-----|--------|

---

## TypeScript Types (created)

| Type/Interface | Location | Description | Set By |
|----------------|----------|-------------|--------|

---

## PHP Services & Classes (created)

| Class | Location | Purpose | Set By |
|-------|----------|---------|--------|

---

## Enums Created

| Enum | Location | Values | Set By |
|------|----------|--------|--------|

---

## Routes Added

| Method | URI | Controller@Method | Set By |
|--------|-----|-------------------|--------|

---

## Database Columns & Naming

| Table | Column | Type | Notes | Set By |
|-------|--------|------|-------|--------|

---

## Implementation Decisions

| Decision | Rationale | Set By |
|----------|-----------|--------|

---

## Notes for Future Work Units

<!-- Add any context that subsequent work units should know -->
