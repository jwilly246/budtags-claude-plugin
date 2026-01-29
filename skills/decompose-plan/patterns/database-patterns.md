# Database Patterns (Quick Reference)

Essential patterns for database work in BudTags.

## Migration Pattern

```php
Schema::create('feature_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('organization_id')->constrained()->cascadeOnDelete();
    // ... columns
    $table->timestamps();
    $table->softDeletes(); // if needed

    $table->index(['organization_id', 'status']);
});
```

## Model Pattern

```php
class FeatureItem extends Model
{
    use HasFactory, SoftDeletes, HasOrganization;

    protected $fillable = ['organization_id', 'name', /* ... */];

    protected function casts(): array
    {
        return ['metadata' => 'array', 'active' => 'boolean'];
    }

    public function organization(): BelongsTo
    {
        return $this->belongsTo(Organization::class);
    }
}
```

## Factory Pattern

```php
class FeatureItemFactory extends Factory
{
    public function definition(): array
    {
        return [
            'organization_id' => Organization::factory(),
            'name' => fake()->word(),
        ];
    }

    public function forOrganization(Organization $org): static
    {
        return $this->state(fn () => ['organization_id' => $org->id]);
    }
}
```

## Critical Rules

- **Always** include `organization_id` for tenant data
- **Always** create factory with `forOrganization` state
- Use `HasOrganization` trait on org-scoped models
- Index frequently queried columns
