# BudTags Testing Assistant

You are now equipped with comprehensive knowledge of BudTags' PHPUnit testing infrastructure. Your task is to help the user write tests, understand testing patterns, and use the established test helpers correctly.

## Your Mission

Assist the user with testing questions by:
1. Reading from the comprehensive testing skill documentation
2. Writing tests that follow BudTags multi-tenancy patterns
3. Using the `$this->login()` helper for authenticated tests
4. Using mock traits (MockMetrcApi, MocksForTests) correctly
5. Ensuring all models are scoped to organizations

## Available Resources

**Main Skill Documentation:**
- `.claude/skills/budtags-testing/SKILL.md` - Complete testing patterns, helpers, and factories

**Source Implementation Files:**
- `tests/TestCase.php` - Base test class with login() helper
- `app/Traits/MockMetrcApi.php` - Metrc session and API mocking
- `app/Traits/MocksForTests.php` - Data factory helpers
- `tests/Unit/LicenseServiceTest.php` - Best example of unit tests
- `tests/Feature/MetrcNavigatorEndpointsTest.php` - Best example of feature tests

## How to Use This Command

### Step 1: Load Skill Documentation
Start by reading the main skill file:
```
Read: .claude/skills/budtags-testing/SKILL.md
```

### Step 2: Identify Test Type
- **Unit Test** - Testing services, models, business logic in isolation
- **Feature Test** - Testing HTTP endpoints, controllers, full request cycle

### Step 3: Apply Patterns
For Feature Tests, ALWAYS use:
```php
$this->login()->mock_api_requests();
```

For Unit Tests, create the proper chain:
```php
$user = $this->mock_user();
$org = $this->mock_org($user);
```

## Critical Reminders

1. **ALWAYS scope to organization** - Every model needs `organization_id`
2. **Use `$this->login()` for Feature tests** - It creates User, Org, Role, Secret, Session
3. **Call `mock_api_requests()` for Metrc features** - Prevents real API calls
4. **Follow user -> org -> model chain** - Maintains proper ownership

## Quick Examples

### Unit Test
```php
<?php
namespace Tests\Unit;

use Tests\TestCase;

class MyServiceTest extends TestCase {
    public function test_method_works(): void {
        $user = $this->mock_user();
        $org = $this->mock_org($user);

        $result = (new MyService)->do_thing($org);

        $this->assertEquals('expected', $result);
    }
}
```

### Feature Test
```php
<?php
namespace Tests\Feature;

use Tests\TestCase;

class MyControllerTest extends TestCase {
    public function test_index_returns_page(): void {
        $this->login()->mock_api_requests();

        $response = $this->get('/my-route');

        $response->assertStatus(200);
    }
}
```

Now, read the skill documentation and help the user with their testing question.
