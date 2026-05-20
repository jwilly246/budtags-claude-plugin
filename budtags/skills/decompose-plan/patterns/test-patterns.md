# Test Patterns (Quick Reference)

Essential patterns for testing in BudTags. For full testing philosophy and conventions, see the `budtags-testing` skill.

## Core Principles (from budtags-testing skill)

1. **Test behaviors, not implementation** — black-box testing, assert outputs not internals
2. **One reason to fail** — each test verifies exactly one behavior
3. **Tests should be self-contained** — each test builds its own data, don't over-abstract setUp
4. **Quality over coverage** — exact assertions (`assertEquals`) over weak ones (`assertNotNull`)
5. **Testability reflects code quality** — if it's hard to test, refactor the code, don't add more mocks

## PHP Feature Test Setup

```php
class FeatureControllerTest extends TestCase
{
    // Using transaction-based isolation from base TestCase (NO RefreshDatabase)

    public function test_index_returns_org_items(): void {
        // create user, org, role, secret, and session data
        $this->login()->mock_api_requests();
        // create items for this org
        $items = FeatureItem::factory()
            ->forOrganization($this->user->active_org)
            ->count(3)
            ->create();
        // request the page
        $response = $this->get(route('features-index'));
        // should return only org items
        $response->assertOk();
        $response->assertInertia(fn ($page) => $page->has('items.data', 3));
    }
}
```

## Organization Scoping Test

```php
public function test_fetch_all_returns_only_org_items(): void {
    // create user, org, role, secret, and session data
    $this->login()->mock_api_requests();
    // create items for this org
    FeatureItem::factory()->forOrganization($this->user->active_org)->count(3)->create();
    // create items for a DIFFERENT org (should not be returned)
    $other_org = $this->mock_org($this->mock_user());
    FeatureItem::factory()->forOrganization($other_org)->count(2)->create();
    // request the page
    $response = $this->get(route('features-index'));
    // should return only this org's items
    $response->assertOk();
    $response->assertInertia(fn ($page) => $page->has('items.data', 3));
}

public function test_cannot_access_other_org_items(): void {
    // create user, org, role, secret, and session data
    $this->login()->mock_api_requests();
    // create item in a different org
    $other_org = $this->mock_org($this->mock_user());
    $other_item = FeatureItem::factory()->forOrganization($other_org)->create();
    // try to access it
    $response = $this->get(route('features-show', $other_item));
    // should be denied
    $response->assertNotFound(); // or assertForbidden()
}
```

## Model Unit Test

```php
public function test_belongs_to_organization(): void {
    // create user and org
    $user = $this->mock_user();
    $org = $this->mock_org($user);
    // create item in org
    $item = FeatureItem::factory()->forOrganization($org)->create();
    // verify relationship
    $this->assertInstanceOf(Organization::class, $item->organization);
    $this->assertEquals($org->id, $item->organization_id);
}
```

## Vitest Component Test

```tsx
import { render, screen } from '@/testing';
import { vi, describe, it, expect } from 'vitest';

// mock Inertia BEFORE importing component
const mock = inertiaReactMock();
vi.mock('@inertiajs/react', () => mock);

import { ComponentUnderTest } from '@/Components/ComponentUnderTest';

describe('ComponentUnderTest', () => {
    it('renders the expected content', () => {
        render(<ComponentUnderTest items={[{ id: 1, name: 'Test' }]} />);
        expect(screen.getByText('Test')).toBeInTheDocument();
    });

    it('handles empty state', () => {
        render(<ComponentUnderTest items={[]} />);
        expect(screen.getByText('No items found')).toBeInTheDocument();
    });
});
```

## Critical Rules

- **NEVER use RefreshDatabase** — base TestCase uses transaction-based isolation
- **Always test org scoping** — both inclusion AND exclusion
- **Use `$this->login()->mock_api_requests()`** for feature tests needing auth + org context
- **Use factories** with `forOrganization()` state, never raw data
- **Use `composer test-fast`** to run PHP tests, **`npm test`** for Vitest
- **Each test builds its own data** — don't share test data via class properties
- Test **validation errors**: `assertSessionHasErrors(['field'])`
- All PHP test methods must have `: void` return type
- Use inline comments to document test steps (Nick's style)
