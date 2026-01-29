# Test Patterns (Quick Reference)

Essential patterns for testing in BudTags.

## Feature Test Setup

```php
class FeatureControllerTest extends TestCase
{
    use RefreshDatabase;

    private User $user;
    private Organization $org;

    protected function setUp(): void
    {
        parent::setUp();
        $this->org = Organization::factory()->create();
        $this->user = User::factory()->create(['active_org_id' => $this->org->id]);
        $this->org->users()->attach($this->user);
    }
}
```

## Organization Scoping Test

```php
public function test_fetch_all_returns_only_org_items(): void
{
    $orgItems = FeatureItem::factory()->forOrganization($this->org)->count(3)->create();
    $otherOrg = Organization::factory()->create();
    FeatureItem::factory()->forOrganization($otherOrg)->count(2)->create();

    $response = $this->actingAs($this->user)->get(route('features-index'));

    $response->assertOk();
    $response->assertInertia(fn ($page) => $page->has('items.data', 3));
}

public function test_cannot_access_other_org_items(): void
{
    $otherOrg = Organization::factory()->create();
    $otherItem = FeatureItem::factory()->forOrganization($otherOrg)->create();

    $response = $this->actingAs($this->user)->get(route('features-show', $otherItem));

    $response->assertNotFound(); // or assertForbidden()
}
```

## Model Unit Test

```php
public function test_belongs_to_organization(): void
{
    $item = FeatureItem::factory()->forOrganization($this->org)->create();
    $this->assertInstanceOf(Organization::class, $item->organization);
}
```

## Critical Rules

- **Always test org scoping** - both inclusion AND exclusion
- **Use factories** with `forOrganization()` state, never raw data
- **Set `active_org_id`** on test user in setUp
- **RefreshDatabase** trait on all tests
- Test **validation errors**: `assertSessionHasErrors(['field'])`
