---
name: budtags-testing
description: BudTags PHPUnit testing patterns, Mockery mocking, multi-tenancy aware test helpers, Metrc API mocking, and model factories
version: 2.3.0
category: project
auto_activate:
  patterns:
    - "tests/**/*.php"
    - "database/factories/**/*.php"
  keywords:
    - "write test"
    - "add test"
    - "create test"
    - "unit test"
    - "feature test"
    - "phpunit"
    - "testing"
    - "mock"
    - "mockery"
    - "factory"
    - "TestCase"
---

# BudTags Testing Skill

You are now equipped with comprehensive knowledge of BudTags' PHPUnit testing infrastructure, based on Nick's gold standard patterns.

---

## Testing Philosophy: Quality Over Coverage

**Tests exist to find bugs, not to increase coverage metrics.**

### Core Principles

1. **Tests Must Have Weight**
   - Every test should be able to FAIL if the code is broken
   - Don't write tests that just "pass" - write tests that would catch real bugs
   - If a test can never fail, it's useless

2. **Test Boundaries and Edge Cases**
   - Test exact limits (65535 chars, not "a lot of chars")
   - Test one-over boundaries (65536 should truncate, 65535 should not)
   - Test empty inputs, null values, and unexpected data shapes

3. **Verify Exact Behavior, Not Just "It Works"**
   ```php
   // ❌ WRONG - Weak assertion that always passes
   $this->assertLessThanOrEqual(65535, strlen($log->notes));

   // ✅ CORRECT - Exact assertion that catches off-by-one errors
   $this->assertEquals(65535, strlen($log->notes));
   ```

4. **Coverage Is Secondary**
   - High coverage with weak assertions = false confidence
   - Low coverage with strong assertions = actual protection
   - We want BOTH: high coverage AND quality tests

### What Makes a Quality Test

| Quality Test | Coverage-Only Test |
|--------------|-------------------|
| Tests boundary conditions (255, 256 chars) | Tests "a long string" |
| Uses `assertEquals` for exact values | Uses `assertNotNull` or `assertTrue` |
| Tests what happens when things go wrong | Only tests happy path |
| Would fail if someone breaks the logic | Passes no matter what |
| Documents expected behavior precisely | Just exercises code paths |

### Example: Quality Boundary Test

```php
public function test_title_at_exactly_255_chars_is_not_truncated(): void {
    $user = $this->mock_user();
    $this->set_request_user($user);
    // create title at exactly the limit
    $exact_limit_title = str_repeat('y', 255);
    // store - should NOT be truncated
    $log = LogService::store($exact_limit_title, 'Description');
    // verify exact length preserved
    $this->assertEquals(255, strlen($log->title));
    $this->assertEquals($exact_limit_title, $log->title);
}

public function test_title_at_256_chars_is_truncated_to_exactly_255(): void {
    $user = $this->mock_user();
    $this->set_request_user($user);
    // create title one char over the limit
    $over_limit_title = str_repeat('y', 256);
    // store - should be truncated to exactly 255
    $log = LogService::store($over_limit_title, 'Description');
    // verify EXACT length
    $this->assertEquals(255, strlen($log->title));
}
```

**These tests would catch an off-by-one error. A coverage-only test would not.**

---

## Quick Reference

| Type | Base Class | Authentication | Example |
|------|-----------|----------------|---------|
| Unit Test | `Tests\TestCase` | None needed | `LabelTest` |
| Feature Test (with org) | `Tests\TestCase` | `$this->login()->mock_api_requests()` | `MetrcNavigatorEndpointsTest` |
| Feature Test (auth only) | `Tests\TestCase` | `User::factory()->create()` + `actingAs()` | `ProfileTest` |

---

## Nick's Style Conventions (MUST FOLLOW)

### 1. Inline Comments Explaining Each Step
Nick's signature style uses **inline comments to document what each line does**, making tests read like a story:
```php
public function test_redirect_from_plants_if_no_permission(): void {
    // create user, org, role, secret, and session data
    // this facility CAN grow
    $this->login()->mock_api_requests();
    // assert that the page loads
    $this->get('/metrc/nav/plants')->assertStatus(200);
    // re-set session data, use the SECOND license
    // this facility can't grow
    $this->mock_session($this->user->active_org, false);
    // assert that the page redirects away
    $this->get('/metrc/nav/plants')->assertRedirect('/metrc/nav');
}
```

### 2. Return Type Declarations
All test methods MUST have `: void` return type:
```php
public function test_something(): void {  // ✅ CORRECT
public function test_something() {        // ❌ WRONG
```

### 3. Test Method Naming
Use `test_method_describes_behavior` pattern (snake_case):
```php
public function test_normalize_handles_null(): void {           // ✅
public function test_get_facility_type_identifies_processors(): void {  // ✅
public function testNormalizeHandlesNull(): void {              // ❌
```

### 4. Transaction-Based Isolation (NO RefreshDatabase)
**NEVER use `RefreshDatabase` trait** - it wipes the database.
The base TestCase uses transactions instead:
```php
class YourTest extends TestCase {
    // Using transaction-based isolation from base TestCase (no RefreshDatabase)
```

---

## Test Infrastructure

### Base TestCase (`tests/TestCase.php`)

```php
abstract class TestCase extends BaseTestCase {
    use CreatesApplication;
    use MockMetrcApi;      // Metrc API mocking
    use MocksForTests;     // Data factory helpers
    use WithFaker;         // Random data generation

    protected function setUp(): void {
        parent::setUp();
        Queue::fake();           // Don't execute jobs
        DB::beginTransaction();  // Wrap test in transaction
        Permission::sync();      // Ensure permissions exist
    }

    protected function tearDown(): void {
        DB::rollBack();          // Rollback all changes
        parent::tearDown();
    }

    protected ?User $user = null;

    protected function login(string $password = 'password'): TestCase {
        // Creates: User → Organization → Admin role → Metrc Secret → Session
        // Returns $this for fluent chaining
    }
}
```

### The `$this->login()` Helper

**Use for Feature tests that need authenticated user WITH organization context.**

What it creates:
1. **User** via UserFactory
2. **Organization** owned by user, set as `active_org_id`
3. **Admin role** assigned to user in organization
4. **Metrc Secret** with `is_active=true`
5. **Session data** via `mock_session()`

```php
public function test_metrc_page_loads(): void {
    // create user, org, role, secret, and session data
    $this->login()->mock_api_requests();
    // $this->user is now available
    // $this->user->active_org is the organization
    $response = $this->get('/metrc/nav/packages');
    $response->assertStatus(200);
}
```

### When NOT to Use `$this->login()`

For tests that TEST the authentication flow itself:
```php
public function test_users_can_authenticate_using_the_login_screen(): void {
    // auth tests use factory directly - don't need org context
    $user = User::factory()->create();
    // post login credentials
    $response = $this->post('/login', [
        'email' => $user->email,
        'password' => 'password',
    ]);
    // should be authenticated
    $this->assertAuthenticated();
}
```

---

## Writing Unit Tests

**Location:** `tests/Unit/`
**Purpose:** Test services, models, and business logic without HTTP layer.

### Gold Standard: `LabelTest.php` (Nick's actual test)

```php
<?php

namespace Tests\Unit;

use App\Models\LabelType;
use App\Models\Strain;
use Tests\TestCase;

class LabelTest extends TestCase {
    public function test_label_has_strain(): void {
        $user = $this->mock_user();
        $org = $this->mock_org($user);
        $label = $this->mock_label($user, $org);
        $this->assertInstanceOf(Strain::class, $label->strain);
    }
    public function test_label_has_label_type(): void {
        $user = $this->mock_user();
        $org = $this->mock_org($user);
        $label = $this->mock_label($user, $org);
        $this->assertInstanceOf(LabelType::class, $label->label_type);
    }
}
```

### Service Test Example (with inline comments)

```php
<?php

namespace Tests\Unit;

use App\Services\LicenseService;
use Tests\TestCase;

class LicenseServiceTest extends TestCase {
    private LicenseService $service;

    protected function setUp(): void {
        parent::setUp();
        $this->service = new LicenseService;
    }

    public function test_normalize_handles_null(): void {
        // null input returns null
        $this->assertNull($this->service->normalize(null));
        // empty string returns null
        $this->assertNull($this->service->normalize(''));
        // whitespace-only returns null
        $this->assertNull($this->service->normalize('   '));
    }

    public function test_is_valid_accepts_adult_use_licenses(): void {
        // all adult use license types should be valid
        $this->assertTrue($this->service->is_valid('AU-P-123456'));   // processor
        $this->assertTrue($this->service->is_valid('AU-R-123456'));   // retailer
        $this->assertTrue($this->service->is_valid('AU-G-A-123456')); // grower class A
    }

    public function test_cross_reference_with_metrc_finds_matching_facility(): void {
        // create user and org
        $user = $this->mock_user();
        $org = $this->mock_org($user);
        // create facility type (required field)
        $facility_type = \App\Models\MetrcFacilityType::firstOrCreate(['name' => 'Processor']);
        // create a facility with recreational license
        $facility = \App\Models\MetrcFacility::create([
            'organization_id' => $org->id,
            'metrc_facility_type_id' => $facility_type->id,
            'name' => 'Test Facility',
            'license_recreational' => 'AU-P-123456',
            'license_medical' => null,
        ]);
        // search should find it
        $result = $this->service->cross_reference_with_metrc('AU-P-123456', $org->id);
        $this->assertNotNull($result);
        $this->assertEquals($facility->id, $result->id);
    }
}
```

---

## Writing Feature Tests

**Location:** `tests/Feature/`
**Purpose:** Test HTTP endpoints, controllers, and full request/response cycles.

### Gold Standard: `MetrcNavigatorEndpointsTest.php` (Nick's actual test)

```php
<?php

namespace Tests\Feature;

use Tests\TestCase;

class MetrcNavigatorEndpointsTest extends TestCase {

    public function test_redirect_from_plants_if_no_permission(): void {
        // create user, org, role, secret, and session data
        // this facility CAN grow
        $this->login()->mock_api_requests();
        // assert that the page loads
        $this->get('/metrc/nav/plants')->assertStatus(200);
        // re-set session data, use the SECOND license
        // this facility can't grow
        $this->mock_session($this->user->active_org, false);
        // assert that the page redirects away
        $this->get('/metrc/nav/plants')->assertRedirect('/metrc/nav');
    }
}
```

### Controller Test Template (Nick's style)

```php
<?php

namespace Tests\Feature;

use Tests\TestCase;

class StrainControllerTest extends TestCase {

    public function test_index_requires_authentication(): void {
        // unauthenticated request should redirect to login
        $response = $this->get('/strains');
        $response->assertRedirect('/login');
    }

    public function test_index_returns_page(): void {
        // create authenticated user with org context
        $this->login()->mock_api_requests();
        // request the page
        $response = $this->get('/strains');
        // should return 200 with correct component
        $response->assertStatus(200);
        $response->assertInertia(fn ($page) =>
            $page->component('Org/StrainsAll')
        );
    }

    public function test_store_creates_strain(): void {
        // create authenticated user with org context
        $this->login()->mock_api_requests();
        // post new strain data
        $response = $this->post('/strains', [
            'name' => 'Blue Dream',
            'type' => 'hybrid',
        ]);
        // should redirect and create record
        $response->assertRedirect();
        $this->assertDatabaseHas('strains', [
            'name' => 'Blue Dream',
            'organization_id' => $this->user->active_org_id,
        ]);
    }

    public function test_store_validates_required_fields(): void {
        // create authenticated user with org context
        $this->login()->mock_api_requests();
        // post empty data
        $response = $this->post('/strains', []);
        // should have validation errors
        $response->assertSessionHasErrors(['name']);
    }
}
```

### Auth Test Template (No Org Context Needed)

```php
<?php

namespace Tests\Feature\Auth;

use App\Models\User;
use Tests\TestCase;

class AuthenticationTest extends TestCase {
    // Using transaction-based isolation from base TestCase (no RefreshDatabase)

    public function test_login_screen_can_be_rendered(): void {
        $response = $this->get('/login');
        $response->assertStatus(200);
    }

    public function test_users_can_authenticate_using_the_login_screen(): void {
        // create a user
        $user = User::factory()->create();
        // post login credentials
        $response = $this->post('/login', [
            'email' => $user->email,
            'password' => 'password',
        ]);
        // should be authenticated
        $this->assertAuthenticated();
    }

    public function test_users_can_not_authenticate_with_invalid_password(): void {
        // create a user
        $user = User::factory()->create();
        // post wrong password
        $this->post('/login', [
            'email' => $user->email,
            'password' => 'wrong-password',
        ]);
        // should still be guest
        $this->assertGuest();
    }
}
```

---

## Mock Traits

### MockMetrcApi (`app/Traits/MockMetrcApi.php`)

#### `mock_session($org, $use_first_license)`

| License | Facility | `CanGrowPlants` |
|---------|----------|-----------------|
| First (`403-X0001`) | Cultivation LLC | `true` |
| Second (`402-X0002`) | Dispensary LLC | `false` |

```php
// use cultivation license (can grow plants)
$this->mock_session($this->user->active_org, true);

// use dispensary license (cannot grow plants)
$this->mock_session($this->user->active_org, false);
```

#### `mock_api_requests()`

Intercepts HTTP to prevent real Metrc API calls:
```php
$this->login()->mock_api_requests();
```

### MocksForTests (`app/Traits/MocksForTests.php`)

| Method | Returns | Creates |
|--------|---------|---------|
| `mock_user($password)` | `User` | User with hashed password |
| `mock_org(User $user)` | `Organization` | Org owned by user |
| `mock_strain(Organization $org)` | `Strain` | Strain in org |
| `mock_label_type(Organization $org)` | `LabelType` | Label type in org |
| `mock_label(User $user, Organization $org)` | `Label` | Label with strain + label_type |

```php
$user = $this->mock_user();
$org = $this->mock_org($user);
$label = $this->mock_label($user, $org);
// $label->strain and $label->label_type exist
```

---

## Mockery (Standard Mocking Library)

**Mockery is the standard mocking library for BudTags tests.** Use it for:
- Mocking external API classes (MetrcApi, QuickBooksApi, LeafLink)
- Testing retry logic and exception handling
- Partial mocks when you need to stub specific methods
- Controlling behavior of injected dependencies

### Basic Mockery Patterns

#### 1. Full Mock (Replace Entire Class)
```php
public function test_handles_api_error(): void {
    // create mock that replaces MetrcApi entirely
    /** @var \App\Services\Api\MetrcApi&\Mockery\MockInterface */
    $mockApi = \Mockery::mock(\App\Services\Api\MetrcApi::class);
    $mockApi->shouldReceive('get_history_from_cache')
        ->once()
        ->andThrow(new \Exception('API Error'));
    // inject mock and test
    $result = $this->service->get_packages($mockApi, 'LIC-001');
    // should handle error gracefully
    $this->assertEmpty($result);
}
```

#### 2. Partial Mock (Stub Specific Methods)
```php
public function test_retry_logic_attempts_multiple_times(): void {
    // partial mock - real class but stub one method
    $attempts = 0;
    /** @var InventoryService&\Mockery\MockInterface */
    $mockService = \Mockery::mock(InventoryService::class)->makePartial();
    $mockService->shouldReceive('deduct_for_package')
        ->andReturnUsing(function () use (&$attempts) {
            $attempts++;
            throw new \Exception('Transient error');
        });
    // call method that uses stubbed method
    $mockService->deduct_for_package_with_retry(12345, 5, 'PKG-001', 'user-id', 'org-id', null, 3);
    // verify retry count
    $this->assertEquals(4, $attempts); // initial + 3 retries
}
```

#### 3. Return Controlled Data
```php
public function test_processes_api_response(): void {
    // mock returns specific data
    /** @var \App\Services\Api\MetrcApi&\Mockery\MockInterface */
    $mockApi = \Mockery::mock(\App\Services\Api\MetrcApi::class);
    $mockApi->shouldReceive('get_history_from_cache')
        ->with('LIC-001', \Mockery::type(\Carbon\Carbon::class), 30)
        ->andReturn([
            ['packages' => [['Label' => 'PKG-1'], ['Label' => 'PKG-2']]],
            ['packages' => [['Label' => 'PKG-3']]],
        ]);
    // test
    $result = $this->service->get_active_packages($mockApi, 'LIC-001', 30);
    $this->assertCount(3, $result);
}
```

### Mockery Expectations

#### Call Count Expectations
```php
$mock->shouldReceive('method')->once();           // exactly 1 time
$mock->shouldReceive('method')->twice();          // exactly 2 times
$mock->shouldReceive('method')->times(3);         // exactly 3 times
$mock->shouldReceive('method')->atLeast()->once(); // 1 or more
$mock->shouldReceive('method')->never();          // should not be called
```

#### Argument Matching
```php
// exact match
$mock->shouldReceive('method')->with('exact-value');

// type matching
$mock->shouldReceive('method')->with(\Mockery::type('string'));
$mock->shouldReceive('method')->with(\Mockery::type(\Carbon\Carbon::class));

// any argument
$mock->shouldReceive('method')->with(\Mockery::any());

// multiple arguments
$mock->shouldReceive('method')->with('arg1', \Mockery::type('int'), \Mockery::any());
```

#### Return Values
```php
$mock->shouldReceive('method')->andReturn('value');           // return value
$mock->shouldReceive('method')->andReturn('a', 'b', 'c');     // return sequence
$mock->shouldReceive('method')->andReturnNull();              // return null
$mock->shouldReceive('method')->andThrow(new \Exception());   // throw exception
$mock->shouldReceive('method')->andReturnUsing(function ($arg) {  // dynamic return
    return $arg * 2;
});
```

### When to Use Mockery vs Real Objects

| Use Mockery | Use Real Objects |
|-------------|------------------|
| External APIs (Metrc, QuickBooks, LeafLink) | Database models (User, Organization) |
| Testing exception/retry handling | Testing business logic with real data |
| Verifying method call counts | Testing model relationships |
| Stubbing expensive/slow operations | Integration tests |
| Controlling exact return values | Tests that need real DB state |

### PHPDoc for Type Hints

Always add PHPDoc when using Mockery to help IDE and static analysis:
```php
/** @var \App\Services\Api\MetrcApi&\Mockery\MockInterface */
$mockApi = \Mockery::mock(\App\Services\Api\MetrcApi::class);

/** @var InventoryService&\Mockery\MockInterface */
$mockService = \Mockery::mock(InventoryService::class)->makePartial();
```

### Complete Mockery Example (Nick's Style)

```php
public function test_get_active_packages_returns_merged_packages_from_cache(): void {
    // create mock MetrcApi
    /** @var \App\Services\Api\MetrcApi&\Mockery\MockInterface */
    $mockApi = \Mockery::mock(\App\Services\Api\MetrcApi::class);
    // configure mock to return test data
    $mockApi->shouldReceive('get_history_from_cache')
        ->once()
        ->with('LIC-001', \Mockery::type(\Carbon\Carbon::class), 3)
        ->andReturn([
            ['packages' => [['Label' => 'PKG-1'], ['Label' => 'PKG-2']]],
            ['packages' => [['Label' => 'PKG-3']]],
            ['packages' => []],
        ]);
    // call service method with mock
    $result = $this->service->get_active_packages_for_summary($mockApi, 'LIC-001', 3);
    // should merge all packages from all days
    $this->assertCount(3, $result);
    $this->assertEquals('PKG-1', $result[0]['Label']);
    $this->assertEquals('PKG-2', $result[1]['Label']);
    $this->assertEquals('PKG-3', $result[2]['Label']);
}
```

---

## Special Cases

### UUID Compatibility with Notification::fake()

Laravel's `Notification::fake()` doesn't work with UUID primary keys. For password reset tests:

```php
public function test_password_can_be_reset_with_valid_token(): void {
    // create a user
    $user = User::factory()->create();
    // create token directly using Password broker (not Notification::fake)
    $token = Password::broker()->createToken($user);
    // post reset request
    $response = $this->post('/reset-password', [
        'token' => $token,
        'email' => $user->email,
        'password' => 'new-password',
        'password_confirmation' => 'new-password',
    ]);
    // should succeed and password should be changed
    $response->assertSessionHasNoErrors();
    $this->assertTrue(Hash::check('new-password', $user->refresh()->password));
}
```

### Soft Delete Assertions

BudTags uses soft deletes on User model:
```php
public function test_user_can_delete_their_account(): void {
    // create a user
    $user = User::factory()->create();
    // delete account
    $this->actingAs($user)->delete('/profile', ['password' => 'password']);
    // should be logged out
    $this->assertGuest();
    // user still exists but has deleted_at set
    $this->assertNotNull($user->fresh()->deleted_at);
}
```

---

## Running Tests

```bash
# Run all tests
php artisan test

# Run with stop on failure
php artisan test --stop-on-failure

# Run specific test file
php artisan test tests/Unit/LabelTest.php

# Run specific test method
php artisan test --filter=test_label_has_strain

# Run test suite
php artisan test --testsuite=Unit
php artisan test --testsuite=Feature

# Coverage (requires PCOV extension)
php artisan test --coverage
php artisan test --coverage-html=storage/coverage
```

---

## Critical Rules

### 1. NEVER Use RefreshDatabase
```php
// ❌ WRONG - Wipes the database
use RefreshDatabase;

// ✅ CORRECT - Transaction isolation from base TestCase
// Using transaction-based isolation from base TestCase (no RefreshDatabase)
```

### 2. ALWAYS Scope to Organization
```php
// ✅ CORRECT
$strain = Strain::factory()->create([
    'organization_id' => $org->id,
]);

// ❌ WRONG - Missing organization scope
$strain = Strain::factory()->create();
```

### 3. Use `$this->login()` for Authenticated Feature Tests
```php
// ✅ CORRECT - Full context (user, org, role, secret, session)
$this->login()->mock_api_requests();

// ⚠️ ONLY for auth flow tests
$user = User::factory()->create();
$this->actingAs($user);
```

### 4. Always Add `: void` Return Type
```php
public function test_something(): void {  // ✅ CORRECT
```

### 5. Use Inline Comments to Document Test Steps
```php
// ✅ CORRECT - Nick's style
public function test_something(): void {
    // create user and org
    $user = $this->mock_user();
    $org = $this->mock_org($user);
    // perform action
    $result = $service->do_thing($org);
    // assert result
    $this->assertNotNull($result);
}

// ❌ WRONG - No documentation of what's happening
public function test_something(): void {
    $user = $this->mock_user();
    $org = $this->mock_org($user);
    $result = $service->do_thing($org);
    $this->assertNotNull($result);
}
```

---

## File Reference

| File | Purpose | Author |
|------|---------|--------|
| `tests/TestCase.php` | Base class with helpers | Nick |
| `tests/Unit/LabelTest.php` | Gold standard unit test | Nick |
| `tests/Feature/MetrcNavigatorEndpointsTest.php` | Gold standard feature test | Nick |
| `app/Traits/MockMetrcApi.php` | Metrc session mocking | Nick |
| `app/Traits/MocksForTests.php` | Data factory helpers | Nick |

**You now have complete knowledge of BudTags testing patterns based on Nick's actual authored tests. Follow these patterns exactly!**
