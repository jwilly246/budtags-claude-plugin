# BudTags-Specific Question Bank

Reference this throughout planning to ensure BudTags pattern compliance.

---

## Reusability Discovery (RUN FIRST)

### Package Version Check

Before planning ANY feature, verify installed packages:

```bash
# Check PHP/Laravel packages
cat composer.json | grep -E '"(laravel|spatie|inertia)"'

# Check JS packages
cat package.json | grep -E '"(react|@tanstack|@inertiajs|@headlessui)"'
```

### Reusability Questions

**Components:**
- What existing UI components can be reused for this feature?
- Is there a similar modal, form, or page that can serve as a template?
- Are there custom hooks that provide needed functionality?

**Services:**
- Is there an existing service that handles similar logic?
- Can this extend an existing service rather than create a new one?
- Are there utility functions that already do what's needed?

**Models:**
- Are there existing traits that provide needed functionality?
- Is there a similar model with patterns to follow?
- Can relationships be added to existing models vs creating new ones?

**Patterns:**
- What's the established naming convention for this type of feature?
- How do similar features handle authorization?
- What's the standard flow for this type of operation?

### Reusability Checklist

Before writing ANY new code, verify:

- [ ] Searched for existing components that could be reused
- [ ] Checked for similar pages/modals as templates
- [ ] Looked for existing services with similar functionality
- [ ] Found relevant traits that could be applied
- [ ] Identified patterns from similar features
- [ ] Documented what WILL be reused vs created new

### Package Awareness Questions

**Before suggesting a new package, research:**
- Is this functionality available in an already-installed package?
- Is the package compatible with our Laravel/React versions?
- Who maintains it? Last release date? GitHub stars/activity?
- What's the bundle size / dependency footprint?

**When pitching a package:**
- Explain the problem it solves
- Show what we'd have to build without it
- Note any downsides (complexity, size, learning curve)
- Get explicit buy-in before adding to plan

**User is open to packages** - just make a reasonable case for them.

---

## Organization Scoping (HIGHEST PRIORITY)

### Critical Questions

- Is this feature organization-scoped? (almost always YES)
- Does every database table have `organization_id`?
- Does every query use `request()->user()->active_org`?
- Are relationships crossing organization boundaries blocked?

### Verification Checklist

- [ ] Every model has `organization_id` column
- [ ] Every model has `organization()` relationship
- [ ] Every controller method scopes queries to active org
- [ ] Tests verify users can't access other orgs' data
- [ ] Background jobs receive org_id explicitly (no request context)

### Common Mistakes

- Querying by ID alone: `Order::find($id)` ❌
- Should be: `request()->user()->active_org->orders()->find($id)` ✅
- Or: `Order::where('organization_id', $org_id)->find($id)` ✅

---

## Naming Conventions

### PHP/Backend

| Type | Convention | Example |
|------|------------|---------|
| Tables | plural, snake_case | `advertising_orders` |
| Columns | singular, snake_case | `pricing_tier_id` |
| Models | singular, PascalCase | `AdvertisingOrder` |
| Controllers | PascalCase, suffix | `AdvertisingController` |
| Methods | snake_case, verb-first | `fetch_all`, `create`, `delete` |
| Relationships | snake_case | `pricing_tier()` not `pricingTier()` |
| Routes | dash-separated | `marketplace-advertising` not `marketplace.advertising` |

### Frontend/TypeScript

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `AdvertisingTab.tsx` |
| Files | PascalCase | `AdvertisingTabContent.tsx` |
| Types | PascalCase | `AdvertisingOrder` |
| Props | camelCase | `pricingTiers` |
| Functions | camelCase | `fetchOrders` |

---

## Controller Patterns

### Method Naming

| Action | Method Name | NOT |
|--------|-------------|-----|
| List all | `fetch_all()` | `index()` |
| Get one | `fetch()` | `show()` |
| Create | `create()` | `store()` |
| Update | `update()` | - |
| Delete | `delete()` | `destroy()` |
| Custom | `verb_noun()` | `nounVerb()` |

### Request Handling

```php
// ✅ CORRECT
public function create()
{
    $values = request()->validate([...]);
    $user = request()->user();
    $org = $user->active_org;
}

// ❌ WRONG
public function create(Request $request)
{
    $validated = $request->validate([...]);
}
```

### Authorization Comments

```php
// ✅ CORRECT - Explain what's being protected
// prevent users from viewing orders from other organizations
abort_if($order->organization_id !== request()->user()->active_org_id, 403);
```

---

## Data Fetching Patterns

### When to Use What

| Scenario | Pattern | Why |
|----------|---------|-----|
| Form submissions | Inertia useForm | Flash messages, redirects, validation errors |
| CRUD operations | Inertia useForm | Full page state, server validation |
| Read-heavy dashboard | React Query | Caching, background refresh |
| Inline editing | React Query mutations | Optimistic updates |
| Real-time data | React Query + polling | Auto-refresh |

### Inertia useForm Pattern (MANDATORY for all forms)

```typescript
import { useForm } from '@inertiajs/react';

// In modal or form component
const { data, setData, post, processing, errors, reset } = useForm({
    name: '',
    email: '',
});

const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    post(route('users-create'), {
        onSuccess: () => {
            reset();
            onClose(); // MainLayout handles flash automatically
        },
    });
};

// Input binding
<InputText
    value={data.name}
    onChange={(e) => setData('name', e.target.value)}
    errors={errors.name}
/>
```

### ⛔ FORBIDDEN Form Patterns

```typescript
// ❌ NEVER use useState for form fields
const [name, setName] = useState('');

// ❌ NEVER use axios/fetch for mutations
axios.post('/api/users', formData);

// ❌ NEVER use react-hook-form
const { register } = useForm(); // This is react-hook-form, NOT Inertia

// ❌ NEVER lift form state to parent
<CreateModal formData={formData} setFormData={setFormData} />

// ❌ NEVER manage errors manually
const [errors, setErrors] = useState({});
```

### ✅ Modal Must Own Its Form State

```typescript
// Parent component - only controls visibility
const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
<CreateUserModal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} />

// Modal component - owns ALL form state
export const CreateUserModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
    isOpen, onClose
}) => {
    // Form state lives HERE, not in parent
    const { data, setData, post, processing, errors, reset } = useForm({
        name: '',
        email: '',
    });
    // ...
};
```

### React Query Pattern (for read-only data)

```typescript
// Read-heavy data
const { data, isLoading } = useQuery({
    queryKey: ['orders', orgId],
    queryFn: () => axios.get('/api/orders').then(r => r.data),
    staleTime: 5 * 60 * 1000,
});
```

---

## Logging

### CRITICAL: Never Use Log Facade

```php
// ✅ CORRECT
LogService::store('Advertising', 'Created ad order', $order);

// ❌ WRONG - NEVER DO THIS
Log::info('Created ad order');
```

### LogService Format

```php
LogService::store(
    'Category',      // Short category name
    'Description',   // What happened
    $model           // Related model (optional)
);
```

---

## Flash Messages

### Backend

```php
// ✅ CORRECT
return redirect()->back()->with('message', 'Order created successfully');

// ❌ WRONG - Don't use 'success' key
return redirect()->back()->with('success', 'Order created');
```

### Frontend

```typescript
// ✅ CORRECT - MainLayout handles flash automatically
router.post('/orders', data, {
    onSuccess: () => {
        onClose();
    },
});

// ❌ WRONG - Don't manually show toast for flash
router.post('/orders', data, {
    onSuccess: (page) => {
        toast.success(page.props.flash.success);
    },
});
```

---

## Form Requests

### Always Use Form Request Classes

```php
// ✅ CORRECT
public function create(CreateOrderRequest $request)
{
    $values = $request->validated();
}

// ❌ WRONG - Don't inline validation in controllers
public function create()
{
    $values = request()->validate([...]);
}
```

### Form Request Pattern

```php
class CreateOrderRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true; // Or permission check
    }

    public function rules(): array
    {
        return [
            'name' => 'required|string|max:255',
            'pricing_tier_id' => 'required|uuid|exists:pricing_tiers,id',
        ];
    }

    public function messages(): array
    {
        return [
            'name.required' => 'Please enter a name.',
        ];
    }
}
```

---

## Testing Patterns

### PHPUnit (Not Pest)

```php
// ✅ CORRECT - PHPUnit
class OrderControllerTest extends TestCase
{
    public function test_user_can_create_order(): void
    {
        // ...
    }
}

// ❌ WRONG - Don't use Pest
test('user can create order', function () {
    // ...
});
```

### Factory Usage

```php
// ✅ CORRECT - Use factories
$order = AdvertisingOrder::factory()->approved()->create();

// ❌ WRONG - Don't create models manually
$order = new AdvertisingOrder();
$order->status = 'approved';
$order->save();
```

### Organization Scoping Tests (REQUIRED)

```php
// MUST have this test
public function test_user_cannot_view_other_organization_orders(): void
{
    $user = User::factory()->create();
    $otherOrg = Organization::factory()->create();
    $otherOrder = AdvertisingOrder::factory()
        ->for($otherOrg)
        ->create();

    $this->actingAs($user)
        ->get("/orders/{$otherOrder->id}")
        ->assertForbidden();
}
```

---

## TypeScript Patterns

### No `any` Types

```typescript
// ✅ CORRECT
const orders: AdvertisingOrder[] = props.orders;

// ❌ WRONG
const orders = props.orders as any;
```

### Use Existing Components

```typescript
// ✅ CORRECT - Use existing components
import { Button } from '@/Components/Button';
import { TextInput } from '@/Components/Inputs';
import { DataTable } from '@/Components/DataTable';
import { Badge } from '@/Components/Badge';
import { ToggleSwitch } from '@/Components/ToggleSwitch';

// ❌ WRONG - Don't create new basic components
const MyButton = () => <button>...</button>;
```

---

## Pre-Implementation Checklist

Before starting any implementation:

- [ ] Organization scoping strategy documented
- [ ] Method names follow snake_case verb-first pattern
- [ ] Routes do NOT use named routes (no `->name()`)
- [ ] Form Request classes planned (not inline validation)
- [ ] LogService calls planned (not Log facade)
- [ ] Flash messages use 'message' key
- [ ] Tests include org scoping verification
- [ ] Data fetching pattern chosen (Inertia vs React Query)
- [ ] TypeScript types defined (no `any`)
- [ ] Existing components identified for reuse
