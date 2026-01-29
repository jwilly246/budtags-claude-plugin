# Scenario: New Migration or Model

**Use this checklist when verifying migrations and model changes.**

> **Note (Dec 2025):** Key table changes:
> - Tables renamed: `item_bom` → `item_package_recipes`, `bom_templates` → `package_recipe_templates`
> - New tables: `lab_companies`, `lab_facilities`
> - New columns on `transporter_companies` and `metrc_facilities`

---

## Required Pattern Files

- `patterns/database.md` - **CRITICAL - Schema compliance**
- `.claude/docs/database-schema.md` - **ALWAYS reference**
- `patterns/backend-critical.md` - Org scoping in queries
- `patterns/integrations.md` - Lab/Transporter facility patterns

---

## Migration Verification Checklist

### Schema Compliance
- [ ] Matches schema in `.claude/docs/database-schema.md` EXACTLY
- [ ] Column types correct (UUID vs BIGINT, STRING vs INTEGER, DECIMAL precision)
- [ ] Primary key type matches schema (BIGINT AUTO vs UUID)

### Foreign Keys
- [ ] Foreign keys have proper cascade rules
- [ ] `cascadeOnDelete()` where documented
- [ ] `nullOnDelete()` for nullable foreign keys
- [ ] `restrictOnDelete()` where appropriate

### Indexes
- [ ] Foreign keys auto-indexed
- [ ] Explicit indexes on frequently queried columns
- [ ] Compound indexes for common queries

### Column Attributes
- [ ] Nullable/non-nullable matches schema
- [ ] Default values match schema
- [ ] String lengths match (VARCHAR 255 vs TEXT)
- [ ] Decimal precision correct (e.g., DECIMAL(10,2))

### Timestamps & Soft Deletes
- [ ] Timestamps added where documented (`$table->timestamps()`)
- [ ] Soft deletes where documented (`$table->softDeletes()`)

### Data Type Accuracy (CRITICAL Cases)
- [ ] `metrc_employee_id` is STRING not INTEGER
- [ ] Quantities/prices use DECIMAL not FLOAT
- [ ] UUIDs use `foreignUuid()` not `unsignedBigInteger()`

---

## Model Verification Checklist

### Fillable & Casts
- [ ] `$fillable` includes all user-assignable fields from schema
- [ ] `$casts` matches column types
- [ ] DECIMAL columns cast to `'decimal:2'` not `'float'`
- [ ] JSON columns cast to `'array'` or `'json'`
- [ ] Boolean columns cast to `'boolean'`

### Relationships
- [ ] Relationships match schema documentation
- [ ] Relationship types correct (BelongsTo vs HasMany vs BelongsToMany)
- [ ] Foreign key column names match convention
- [ ] No missing relationships documented in schema

### Pivot Tables
- [ ] Pivot table names alphabetical (e.g., `label_type_strain` not `strain_label_type`)

---

## New Table Patterns (Dec 2025)

### Lab/Transporter Company Tables

When creating lab or transporter company tables:

```php
// Lab Company - Global entity
Schema::create('lab_companies', function (Blueprint $table) {
    $table->id();
    $table->string('name')->unique();
    $table->string('phone')->nullable();
    $table->boolean('enabled')->default(true)->index();
    $table->json('contact_emails')->nullable();
    $table->boolean('request_pickup_enabled')->default(false);
    $table->boolean('generate_coc_enabled')->default(false);  // Labs only
    $table->timestamps();
});
```

**Checklist:**
- [ ] `name` is unique
- [ ] `enabled` is boolean with index
- [ ] `contact_emails` is JSON (cast as `array` in model)
- [ ] Feature flags are boolean with defaults

### MetrcFacility Company FK Pattern

When adding company FK to `metrc_facilities`:

```php
Schema::table('metrc_facilities', function (Blueprint $table) {
    $table->foreignId('lab_company_id')
        ->nullable()
        ->constrained('lab_companies')
        ->nullOnDelete();
    $table->index('lab_company_id');
});
```

**Checklist:**
- [ ] FK is nullable (not all facilities have lab/transporter company)
- [ ] Uses `nullOnDelete()` (preserve facility if company deleted)
- [ ] Has explicit index

### Recipe Tables (Renamed from BOM)

**IMPORTANT:** Never use `item_bom` or `bom_templates` - use the new names:

| Old Name (Wrong) | New Name (Correct) |
|------------------|-------------------|
| `item_bom` | `item_package_recipes` |
| `bom_templates` | `package_recipe_templates` |
| `bom_template_components` | `package_recipe_template_components` |
| `metrc_item_bom_templates` | `metrc_item_recipe_templates` |

---

## Common Violations

### Wrong Column Type
```php
// ❌ WRONG
$table->float('current_quantity');

// ✅ FIX
$table->decimal('current_quantity', 10, 2)->default(0);
```

### Missing Cascade Rules
```php
// ❌ WRONG
$table->foreignUuid('organization_id')->constrained('organizations');

// ✅ FIX
$table->foreignUuid('organization_id')
    ->constrained('organizations')
    ->cascadeOnDelete()
    ->cascadeOnUpdate();
```

### Wrong Model $casts
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

---

## Example: Compliant Migration

```php
Schema::create('non_metrc_items', function (Blueprint $table) {
    $table->id();  // BIGINT AUTO as documented
    $table->foreignUuid('organization_id')
        ->constrained('organizations')
        ->cascadeOnDelete()
        ->cascadeOnUpdate();
    $table->string('name');  // VARCHAR(255) as documented
    $table->text('description')->nullable();
    $table->decimal('current_quantity', 10, 2)->default(0);
    $table->timestamps();
});
```

## Example: Compliant Model

```php
class NonMetrcItem extends Model {
    protected $fillable = [
        'organization_id',
        'name',
        'description',
        'current_quantity',
    ];

    protected $casts = [
        'current_quantity' => 'decimal:2',
    ];

    public function organization(): BelongsTo {
        return $this->belongsTo(Organization::class);
    }
}
```
