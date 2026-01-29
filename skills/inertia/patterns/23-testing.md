# Pattern 23: Testing

## Overview

Test Inertia applications at multiple levels:
- **Feature tests** - Test full request/response cycle
- **Unit tests** - Test individual components
- **Browser tests** - End-to-end with Dusk

---

## Laravel Feature Tests

### Basic Response Test

```php
use Inertia\Testing\AssertableInertia as Assert;

public function test_can_view_users_page()
{
    $user = User::factory()->create();

    $this->actingAs($user)
        ->get('/users')
        ->assertOk()
        ->assertInertia(fn (Assert $page) =>
            $page->component('Users/Index')
        );
}
```

### Assert Props

```php
public function test_users_page_has_users()
{
    $user = User::factory()->create();
    User::factory()->count(5)->create();

    $this->actingAs($user)
        ->get('/users')
        ->assertInertia(fn (Assert $page) =>
            $page
                ->component('Users/Index')
                ->has('users', 6)  // 5 + the acting user
        );
}
```

### Assert Specific Prop Values

```php
public function test_shows_correct_user()
{
    $user = User::factory()->create(['name' => 'John Doe']);

    $this->actingAs($user)
        ->get("/users/{$user->id}")
        ->assertInertia(fn (Assert $page) =>
            $page
                ->component('Users/Show')
                ->has('user', fn (Assert $page) =>
                    $page
                        ->where('id', $user->id)
                        ->where('name', 'John Doe')
                        ->etc()
                )
        );
}
```

### Assert Nested Props

```php
->assertInertia(fn (Assert $page) =>
    $page
        ->has('user.posts', 3)
        ->has('user.posts.0', fn (Assert $page) =>
            $page
                ->where('title', 'First Post')
                ->etc()
        )
);
```

---

## Testing Forms

### Test Form Submission

```php
public function test_can_create_user()
{
    $admin = User::factory()->create();

    $this->actingAs($admin)
        ->post('/users', [
            'name' => 'Jane Doe',
            'email' => 'jane@example.com',
            'password' => 'password',
            'password_confirmation' => 'password',
        ])
        ->assertRedirect('/users');

    $this->assertDatabaseHas('users', [
        'email' => 'jane@example.com',
    ]);
}
```

### Test Validation Errors

```php
public function test_requires_email()
{
    $admin = User::factory()->create();

    $this->actingAs($admin)
        ->post('/users', [
            'name' => 'Jane Doe',
            // Missing email
        ])
        ->assertSessionHasErrors('email');
}
```

### Test Inertia Validation Errors

```php
public function test_returns_validation_errors()
{
    $admin = User::factory()->create();

    $this->actingAs($admin)
        ->post('/users', ['name' => ''])
        ->assertInertia(fn (Assert $page) =>
            $page->has('errors.name')
        );
}
```

---

## Testing Shared Data

```php
public function test_shares_authenticated_user()
{
    $user = User::factory()->create();

    $this->actingAs($user)
        ->get('/dashboard')
        ->assertInertia(fn (Assert $page) =>
            $page->has('user', fn (Assert $page) =>
                $page->where('id', $user->id)->etc()
            )
        );
}
```

---

## Common Assertions

| Method | Description |
|--------|-------------|
| `->component('Name')` | Assert component name |
| `->has('prop')` | Assert prop exists |
| `->has('prop', 5)` | Assert prop is array with count |
| `->where('prop', 'value')` | Assert prop equals value |
| `->missing('prop')` | Assert prop doesn't exist |
| `->etc()` | Allow additional properties |

---

## React Component Tests

### Setup

```bash
npm install -D @testing-library/react @testing-library/jest-dom vitest jsdom
```

### Test Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
  },
});
```

### Basic Component Test

```tsx
// tests/Components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Button from '@/Components/Button';

test('renders button with text', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByRole('button')).toHaveTextContent('Click me');
});

test('calls onClick when clicked', async () => {
  const handleClick = vi.fn();
  render(<Button onClick={handleClick}>Click</Button>);

  await userEvent.click(screen.getByRole('button'));
  expect(handleClick).toHaveBeenCalledOnce();
});
```

### Testing with Inertia Context

```tsx
// Mock usePage
vi.mock('@inertiajs/react', () => ({
  usePage: () => ({
    props: {
      user: { id: 1, name: 'Test User' },
      permissions: ['admin'],
    },
  }),
  Link: ({ children, ...props }) => <a {...props}>{children}</a>,
}));

test('shows admin link for admins', () => {
  render(<Header />);
  expect(screen.getByText('Admin')).toBeInTheDocument();
});
```

---

## BudTags Test Example

```php
public function test_can_view_packages()
{
    $user = User::factory()->create();
    $org = Organization::factory()->create();
    $user->organizations()->attach($org);
    $user->active_org_id = $org->id;
    $user->save();

    Package::factory()->count(3)->create(['org_id' => $org->id]);

    $this->actingAs($user)
        ->get('/packages')
        ->assertOk()
        ->assertInertia(fn (Assert $page) =>
            $page
                ->component('Packages/Index')
                ->has('packages', 3)
        );
}
```

---

## Next Steps

- **Head Component** → Read `24-head-component.md`
- **BudTags Integration** → Read `25-budtags-integration.md`
