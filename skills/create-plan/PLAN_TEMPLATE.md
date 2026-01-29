# Plan Document Template

Use this template when writing the final plan document in Phase 10.

---

# {FEATURE_NAME} Implementation Plan

## Overview

{2-3 sentences describing what this feature does and its business value}

---

## Requirements Summary

| Area | Requirements |
|------|-------------|
| **{User Type 1}** | {What they can do} |
| **{User Type 2}** | {What they can do} |
| **Billing** | {Payment/billing requirements if any} |
| **Analytics** | {Tracking/reporting requirements if any} |
| **Integration** | {External system requirements if any} |

---

## Database Schema

### Migration: `{timestamp}_create_{feature}_tables.php`

**Table 1: `{table_name}`** ({purpose})
- `id` (uuid), {list other columns}
- {foreign keys}
- {indexes}
- timestamps

**Table 2: `{table_name}`** ({purpose})
- {columns}

{Repeat for each table}

---

## Models

### Model Definitions

**`{ModelName}`** - `app/Models/{ModelName}.php`
```php
// Status constants (if applicable)
public const STATUS_PENDING = 'pending';
public const STATUS_ACTIVE = 'active';

// Relationships (snake_case)
public function organization(): BelongsTo
{
    return $this->belongsTo(Organization::class);
}

public function {related_entity}(): {RelationType}
{
    return $this->{relationship}({RelatedModel}::class);
}

// Scopes (if applicable)
public function scopeActive(Builder $query): Builder
{
    return $query->where('status', self::STATUS_ACTIVE);
}
```

{Repeat for each model}

### Model Factories

**`{ModelName}Factory`**
```php
public function definition(): array
{
    return [
        'id' => fake()->uuid(),
        'organization_id' => Organization::factory(),
        // ... other fields
    ];
}

// Useful states
public function {state_name}(): static
{
    return $this->state(fn () => [
        // state-specific values
    ]);
}
```

---

## Backend Implementation

### Form Request Classes

**`{RequestName}`** - `app/Http/Requests/{RequestName}.php`
```php
public function rules(): array
{
    return [
        'field_name' => 'required|string|max:255',
        // ... validation rules
    ];
}
```

### Controllers

**1. `{ControllerName}`** - {Purpose}

```php
class {ControllerName} extends Controller {
    /**
     * {Description of method}
     */
    public function {method_name}(): {ReturnType}
    {
        // Organization scoping
        $org = request()->user()->active_org;

        // Implementation notes
        // ...
    }
}
```

{Repeat for each controller}

### Routes (routes/web.php)

```php
// {Feature} routes
Route::group([
    'middleware' => ['auth', '{additional-middleware}'],
    'prefix' => '/{prefix}',
], function () {
    Route::get('/{path}', [{Controller}::class, '{method}'])->name('{route-name}');
    // ... more routes
});
```

### Services

| Service | Purpose |
|---------|---------|
| `{ServiceName}` | {What it does} |

---

## Frontend Implementation

### Data Fetching Strategy

| Component | Pattern | Reason |
|-----------|---------|--------|
| **{Component}** | Inertia | {Why - forms, CRUD, etc.} |
| **{Component}** | React Query | {Why - caching, real-time, etc.} |

### Components to Create

**`{ComponentName}.tsx`** - `resources/js/Components/{Path}/{ComponentName}.tsx`
- {What it does}
- {Key features}
- Use `{ExistingComponent}` for {purpose}

### Components to Modify

**`{ExistingComponent}.tsx`**
- {What to add/change}

### Types

**Add to:** `resources/js/types/{file}.tsx`
```typescript
export type {TypeName} = {
    id: string;
    organization_id: string;
    // ... other fields
    created_at: string;
    updated_at: string;
};
```

---

## Integration Points

### External APIs

| Service | Operations | Notes |
|---------|------------|-------|
| {Service} | {What operations} | {Error handling, etc.} |

### Existing Code Modifications

| File | Changes |
|------|---------|
| `{file}` | {What to add/modify} |

---

## Implementation Phases

### Phase 1: {Phase Name}
- [ ] {Task 1}
- [ ] {Task 2}
- [ ] {Task with tests}

### Phase 2: {Phase Name}
- [ ] {Task 1}
- [ ] {Task 2}

{Continue for all phases}

---

## Key Files to Create

| File | Purpose |
|------|---------|
| `app/Models/{Model}.php` | {Purpose} |
| `app/Http/Controllers/{Controller}.php` | {Purpose} |
| `resources/js/Components/{Component}.tsx` | {Purpose} |
| `tests/Feature/{Test}.php` | {Purpose} |

## Key Files to Modify

| File | Changes |
|------|---------|
| `routes/web.php` | Add {feature} routes |
| `app/Models/Organization.php` | Add {relationship} relationship |
| `resources/js/types/index.d.ts` | Add TypeScript types |

---

## Verification Plan

### {User Type} Flow
1. {Step 1}
2. {Step 2}
3. Verify {expected outcome}

### Security Tests
- Verify {security requirement 1}
- Verify {security requirement 2}

### Integration Tests
- {Integration verification}

---

## Key Decisions

### Decision 1: {Title}
- **Context:** {Why this decision was needed}
- **Options Considered:** {What alternatives existed}
- **Choice:** {What was decided}
- **Rationale:** {Why this choice}

### Decision 2: {Title}
{Same format}

---

## Open Questions / Deferred Decisions

- [ ] {Question that needs future resolution}
- [ ] {Deferred decision with context}

---

## BudTags Alignment Checklist

- [ ] Controllers use snake_case method names
- [ ] Request handling uses `request()` helper
- [ ] All queries scoped to `request()->user()->active_org`
- [ ] Authorization comments on security-sensitive methods
- [ ] LogService used for all state changes
- [ ] Flash messages use `'message'` key
- [ ] Form Request classes for validation
- [ ] Model relationships use snake_case
- [ ] Routes use dashes not dots
- [ ] Factories created with useful states
- [ ] React Query for read-heavy, Inertia for forms
- [ ] TypeScript types have no `any`
- [ ] Tests cover security scenarios (org scoping)
