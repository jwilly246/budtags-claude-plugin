# Database & Model Patterns

**Source:** `.claude/docs/database-schema.md`, `.claude/docs/backend/models.md`
**Last Updated:** 2025-12-13
**Pattern Count:** Database compliance rules

> **IMPORTANT (Dec 2025):** The database-schema.md was significantly updated. Key changes:
> - Tables renamed: `item_bom` → `item_package_recipes`, `bom_templates` → `package_recipe_templates`
> - New tables added: `lab_companies`, `lab_facilities`
> - New columns on `transporter_companies` and `metrc_facilities`

---

## Overview

All migrations and models MUST match `.claude/docs/database-schema.md`. Schema drift causes bugs, broken relationships, and data integrity issues.

**Critical Rule:** Read `database-schema.md` BEFORE creating/modifying migrations or models.

---

## Pattern 1: Schema Compliance

**Rule:** Migrations MUST match documented schema exactly.

### ✅ CORRECT - Matches Schema

```php
// Matches database-schema.md entry for non_metrc_items table
Schema::create('non_metrc_items', function (Blueprint $table) {
    $table->id();  // BIGINT AUTO as documented
    $table->foreignUuid('organization_id')
        ->constrained('organizations')
        ->cascadeOnDelete()  // Cascade rule as documented
        ->cascadeOnUpdate();
    $table->string('name');  // STRING (VARCHAR 255) as documented
    $table->text('description')->nullable();  // TEXT NULLABLE as documented
    $table->decimal('current_quantity', 10, 2)->default(0);  // DECIMAL(10,2) DEFAULT 0
    $table->timestamps();  // As documented
});
```

### ❌ WRONG - Schema Drift

```php
// ❌ Doesn't match schema
Schema::create('non_metrc_items', function (Blueprint $table) {
    $table->uuid('id')->primary();  // ❌ Should be BIGINT AUTO
    $table->unsignedBigInteger('organization_id');  // ❌ Missing cascade rules
    $table->text('name');  // ❌ Should be VARCHAR(255)
    $table->float('current_quantity');  // ❌ Should be DECIMAL(10,2) with default 0
    // ❌ Missing timestamps
});
```

---

## Pattern 2: Column Types (CRITICAL)

**Rule:** Use exact column types from schema. Common mistakes: UUID vs BIGINT, STRING vs INTEGER, DECIMAL precision.

### Type Mapping

| Schema Type | Laravel Migration | Notes |
|-------------|------------------|-------|
| `BIGINT AUTO` | `$table->id()` | Auto-incrementing primary key |
| `UUID` | `$table->uuid('id')->primary()` | UUID primary key |
| `STRING` | `$table->string('name')` | VARCHAR(255) |
| `TEXT` | `$table->text('description')` | Unlimited text |
| `INTEGER` | `$table->integer('count')` | 4-byte integer |
| `DECIMAL(10,2)` | `$table->decimal('price', 10, 2)` | Precise decimals |
| `BOOLEAN` | `$table->boolean('active')` | True/false |
| `TIMESTAMP` | `$table->timestamp('created_at')` | DateTime |
| `DATE` | `$table->date('harvest_date')` | Date only |
| `JSON` | `$table->json('data')` | JSON column |

### ✅ CORRECT Type Usage

```php
$table->decimal('current_quantity', 10, 2)->default(0);  // Not float!
$table->string('metrc_employee_id');  // String, not integer!
$table->foreignUuid('organization_id');  // UUID foreign key
$table->text('notes')->nullable();  // TEXT for long content
```

### ❌ WRONG Type Usage

```php
$table->float('current_quantity');  // ❌ Use decimal for precision
$table->integer('metrc_employee_id');  // ❌ Metrc IDs are strings!
$table->unsignedBigInteger('organization_id');  // ❌ Use foreignUuid
$table->string('notes');  // ❌ Use text for long content
```

---

## Pattern 3: Foreign Key Cascade Rules

**Rule:** Foreign keys MUST have proper cascade rules matching schema.

### ✅ CORRECT - Cascade Rules

```php
// CASCADE ON DELETE AND UPDATE (most common)
$table->foreignUuid('organization_id')
    ->constrained('organizations')
    ->cascadeOnDelete()
    ->cascadeOnUpdate();

// NULL ON DELETE (preserve records when parent deleted)
$table->foreignId('created_by')->nullable()
    ->constrained('users')
    ->nullOnDelete();

// RESTRICT (prevent deletion if children exist)
$table->foreignId('label_type_id')
    ->constrained('label_types')
    ->restrictOnDelete();
```

### ❌ WRONG - Missing Cascade Rules

```php
// ❌ No cascade rules - orphaned records!
$table->foreignUuid('organization_id')
    ->constrained('organizations');

// ❌ Wrong cascade rule
$table->foreignId('created_by')
    ->constrained('users')
    ->cascadeOnDelete();  // Should be nullOnDelete!
```

---

## Pattern 4: Indexes

**Rule:** Add indexes on foreign keys and frequently queried columns.

### ✅ CORRECT - Proper Indexes

```php
Schema::create('labels', function (Blueprint $table) {
    $table->id();
    $table->foreignUuid('organization_id')
        ->constrained('organizations')
        ->cascadeOnDelete();  // Auto-indexed by foreign key

    // Explicit indexes for queries
    $table->string('tag')->index();  // Frequently searched
    $table->timestamp('created_at')->index();  // Frequently filtered

    // Compound index for common query
    $table->index(['organization_id', 'approved']);
});
```

---

## Pattern 5: Nullable/Non-Nullable Status

**Rule:** Nullable status MUST match schema exactly.

### ✅ CORRECT

```php
$table->string('name');  // NOT NULL by default
$table->text('description')->nullable();  // Explicitly nullable
$table->decimal('current_quantity', 10, 2)->default(0);  // NOT NULL with default
$table->foreignId('created_by')->nullable();  // Nullable foreign key
```

### ❌ WRONG

```php
$table->string('name')->nullable();  // ❌ Schema says NOT NULL
$table->text('description');  // ❌ Schema says NULLABLE
```

---

## Pattern 6: Default Values

**Rule:** Default values MUST match schema.

### ✅ CORRECT

```php
$table->decimal('current_quantity', 10, 2)->default(0);
$table->boolean('approved')->default(false);
$table->integer('version')->default(1);
$table->string('status')->default('pending');
```

### ❌ WRONG

```php
$table->decimal('current_quantity', 10, 2);  // ❌ Missing default 0
$table->boolean('approved');  // ❌ Missing default false
```

---

## Pattern 7: Model Relationships

**Rule:** Model relationships MUST match schema documentation exactly.

### ✅ CORRECT - Relationships Match Schema

```php
class NonMetrcItem extends Model {
    // Relationships match database-schema.md
    public function organization(): BelongsTo {
        return $this->belongsTo(Organization::class);
    }

    public function logs(): HasMany {
        return $this->hasMany(NonMetrcInventoryLog::class);
    }

    public function creator(): BelongsTo {
        return $this->belongsTo(User::class, 'created_by');
    }
}
```

### ❌ WRONG - Missing/Incorrect Relationships

```php
class NonMetrcItem extends Model {
    // ❌ Missing logs() relationship (documented in schema)

    // ❌ Wrong relationship type
    public function organization(): HasOne {  // Should be BelongsTo!
        return $this->hasOne(Organization::class);
    }
}
```

---

## Pattern 8: Model $fillable and $casts

**Rule:** `$fillable` includes all user-assignable fields. `$casts` matches column types.

### ✅ CORRECT

```php
class NonMetrcItem extends Model {
    protected $fillable = [
        'organization_id',  // All fields from schema
        'name',
        'description',
        'category',
        'current_quantity',
        'min_quantity',
        'unit',
        'location',
    ];

    protected $casts = [
        'current_quantity' => 'decimal:2',  // Matches DECIMAL(10,2)
        'min_quantity' => 'decimal:2',
        'data' => 'array',  // JSON column
    ];
}
```

### ❌ WRONG

```php
class NonMetrcItem extends Model {
    protected $fillable = [
        'name',  // ❌ Missing other fields!
    ];

    protected $casts = [
        'current_quantity' => 'float',  // ❌ Should be decimal:2
        // ❌ Missing data cast
    ];
}
```

---

## Pattern 9: Pivot Tables

**Rule:** Pivot table names MUST be alphabetical.

### ✅ CORRECT

```php
// ✅ Alphabetical: label_type_strain
Schema::create('label_type_strain', function (Blueprint $table) {
    $table->id();
    $table->foreignId('label_type_id')
        ->constrained('label_types')
        ->cascadeOnDelete();
    $table->foreignId('strain_id')
        ->constrained('strains')
        ->cascadeOnDelete();
});
```

### ❌ WRONG

```php
// ❌ Not alphabetical: strain_label_type
Schema::create('strain_label_type', function (Blueprint $table) {
    // ...
});
```

---

## Pattern 10: Timestamps and Soft Deletes

**Rule:** Add timestamps/soft deletes where documented in schema.

### ✅ CORRECT

```php
Schema::create('labels', function (Blueprint $table) {
    $table->id();
    // ... columns ...
    $table->timestamps();  // As documented
    $table->softDeletes();  // If documented for this table
});
```

---

## Data Type Accuracy (CRITICAL Cases)

### Metrc Employee ID (STRING, not INTEGER!)

```php
// ✅ CORRECT
$table->string('metrc_employee_id');

// ❌ WRONG
$table->integer('metrc_employee_id');  // Metrc IDs are strings!
```

### Quantities and Prices (DECIMAL, not FLOAT!)

```php
// ✅ CORRECT - Precise decimals
$table->decimal('quantity', 10, 2);
$table->decimal('price', 10, 2);

// ❌ WRONG - Floating point errors!
$table->float('quantity');
$table->float('price');
```

### UUIDs

```php
// ✅ CORRECT - UUID foreign key
$table->foreignUuid('organization_id')
    ->constrained('organizations');

// ❌ WRONG - BIGINT for UUID column
$table->unsignedBigInteger('organization_id');
```

---

## Verification Checklist

### Migration Compliance
- [ ] Matches schema in `.claude/docs/database-schema.md`
- [ ] Column types correct (UUID vs BIGINT, STRING vs INTEGER, DECIMAL precision)
- [ ] Foreign keys have cascade rules
- [ ] Indexes on foreign keys and frequently queried columns
- [ ] Nullable/non-nullable matches schema
- [ ] Default values match schema
- [ ] Timestamps added where documented
- [ ] Soft deletes where documented
- [ ] Pivot table names alphabetical

### Model Compliance
- [ ] `$fillable` includes all user-assignable fields from schema
- [ ] `$casts` matches column types (decimal, boolean, JSON, array)
- [ ] Relationships match schema documentation
- [ ] Relationship types correct (BelongsTo vs HasMany vs BelongsToMany)
- [ ] Foreign key column names match (`label_type_id` not `labelTypeId`)

---

## Common Violations

### Violation 1: Wrong Column Type

```php
// ❌ WRONG
$table->float('current_quantity');

// ✅ FIX
$table->decimal('current_quantity', 10, 2)->default(0);
```

### Violation 2: Missing Cascade Rules

```php
// ❌ WRONG
$table->foreignUuid('organization_id')
    ->constrained('organizations');

// ✅ FIX
$table->foreignUuid('organization_id')
    ->constrained('organizations')
    ->cascadeOnDelete()
    ->cascadeOnUpdate();
```

### Violation 3: Wrong $casts Type

```php
// ❌ WRONG
protected $casts = [
    'current_quantity' => 'float',
];

// ✅ FIX
protected $casts = [
    'current_quantity' => 'decimal:2',
];
```

### Violation 4: Missing Relationships

```php
// ❌ Model missing logs() relationship documented in schema

// ✅ FIX - Add relationship
public function logs(): HasMany {
    return $this->hasMany(NonMetrcInventoryLog::class);
}
```

---

## Pattern 11: Auto-Load Frequently Used Relationships

**Rule:** Use `protected $with` for relationships that are almost always needed. Prevents N+1 queries.

> **Source:** Nick's refactoring of Secret model (Jan 2026) - added `protected $with = ['owner']`.

### ✅ CORRECT - Auto-Load Always-Needed Relationship

```php
class Secret extends Model {
    // Owner is needed whenever we display secrets
    protected $with = ['owner'];

    public function owner(): BelongsTo {
        return $this->belongsTo(User::class, 'user_id');
    }
}
```

### ✅ Also CORRECT - Explicit Eager Load (For Optional Relationships)

```php
// Only load when needed
$secrets = Secret::with(['owner', 'secret_type'])->get();
```

### ❌ WRONG - Repeated N+1 Queries

```php
// N+1 problem: Queries owner for each secret
$secrets = Secret::all();
foreach ($secrets as $secret) {
    echo $secret->owner->name;  // N+1!
}
```

### When to Use `$with`

| Use `protected $with` | Use explicit `->with()` |
|----------------------|------------------------|
| Relationship accessed in 80%+ of use cases | Relationship rarely needed |
| Simple BelongsTo relationships | HasMany with many records |
| Display data (name, email) | Heavy nested relationships |

---

## Pattern 12: Cascade Delete Decisions

**Rule:** Choose cascade behavior based on data ownership semantics.

> **Source:** Nick's refactoring (Jan 2026) - changed Secret's `user_id` to `cascadeOnDelete()`.

### `cascadeOnDelete()` - Child Data Belongs to Parent

```php
// If user is deleted, their API keys should be deleted too
// (keys are meaningless without the user)
$table->foreignUuid('user_id')
    ->constrained('users')
    ->cascadeOnDelete();

// If org is deleted, all its data goes with it
$table->foreignUuid('organization_id')
    ->constrained('organizations')
    ->cascadeOnDelete()
    ->cascadeOnUpdate();
```

### `nullOnDelete()` - Child Data Should Be Preserved

```php
// If user is deleted, keep the record but clear the reference
// (for audit trails, historical data)
$table->foreignUuid('created_by')
    ->nullable()
    ->constrained('users')
    ->nullOnDelete();

// Orders are business records - preserve even if customer deleted
$table->foreignUuid('customer_id')
    ->nullable()
    ->constrained('customers')
    ->nullOnDelete();
```

### Decision Matrix

| Relationship Type | Delete Behavior | Rationale |
|------------------|-----------------|-----------|
| `secret.user_id` (owner) | `cascadeOnDelete` | Keys belong to user |
| `secret.organization_id` | `cascadeOnDelete` | Keys belong to org |
| `log.created_by` | `nullOnDelete` | Preserve audit history |
| `order.created_by` | `nullOnDelete` | Orders are business records |
| `user.borrowed_metrc_key_id` | `nullOnDelete` | User survives key deletion |

---

## Pattern 13: Column Removal Checklist

**Rule:** When removing columns, search for ALL references across the codebase.

> **Source:** Bug found in user-api-keys branch (Jan 2026) - `SecretController::update()` still referenced removed `updated_by` column.

### Required Search Steps

**1. Search Model:**
```bash
grep -n "column_name" app/Models/YourModel.php
```
Check: `$fillable`, `$casts`, relationships, accessors/mutators

**2. Search Controllers:**
```bash
grep -rn "column_name" app/Http/Controllers/ --include="*.php"
```
Check: Assignments in `create()`/`update()`, query filters, response data

**3. Search Frontend:**
```bash
grep -rn "column_name" resources/js --include="*.tsx"
```
Check: TypeScript types, components displaying the column, form submissions

**4. Search Tests:**
```bash
grep -rn "column_name" tests/ --include="*.php"
```
Check: Factory definitions, assertions, test data fixtures

### Common Missed Locations

| Location | Why It's Missed |
|----------|-----------------|
| Controller `update()` methods | Still assigning the removed column |
| TypeScript types | Interface not updated |
| Factory `definition()` | Still generating the column |
| Test assertions | Checking removed column value |
| Related relationship names | `last_updater` relationship when `updated_by` removed |

### Example: Removing `updated_by` column

```bash
# Search for direct column references
grep -rn "updated_by" app/ --include="*.php"
grep -rn "updated_by" resources/js --include="*.tsx"
grep -rn "updated_by" tests/ --include="*.php"

# Also search for relationship names that might use the column
grep -rn "last_updater" app/ --include="*.php"
```

---

## Impact of Violations

| Violation | Impact | Severity |
|-----------|--------|----------|
| Wrong column type | Data corruption, precision loss | **CRITICAL** |
| Missing cascade rules | Orphaned records, data integrity issues | **CRITICAL** |
| Schema drift | Broken features, migration conflicts | **HIGH** |
| Missing indexes | Slow queries, performance issues | **MEDIUM** |
| Wrong $casts | Type conversion errors | **MEDIUM** |
| Missing relationships | Broken Eloquent queries | **HIGH** |
| Column removal without search | Runtime errors after migration | **CRITICAL** |

---

## Related Patterns

- **backend-critical.md** - Organization scoping in queries
- **backend-style.md** - Model conventions
- `.claude/docs/database-schema.md` - **ALWAYS reference before DB work**
- `.claude/docs/backend/models.md` - Model patterns and relationships
