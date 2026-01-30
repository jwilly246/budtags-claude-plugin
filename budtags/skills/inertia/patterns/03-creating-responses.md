# Pattern 3: Creating Responses (Laravel)

## Basic Responses

### Inertia::render()

The primary method for rendering Inertia pages:

```php
use Inertia\Inertia;

class UsersController extends Controller
{
    public function index()
    {
        return Inertia::render('Users/Index', [
            'users' => User::all(),
        ]);
    }

    public function show(User $user)
    {
        return Inertia::render('Users/Show', [
            'user' => $user,
        ]);
    }
}
```

### Component Path

The first argument is the component path relative to `resources/js/Pages/`:

```php
Inertia::render('Users/Index')     // → Pages/Users/Index.tsx
Inertia::render('Dashboard')       // → Pages/Dashboard.tsx
Inertia::render('Org/Settings')    // → Pages/Org/Settings.tsx
```

---

## Passing Props

### Basic Props

```php
return Inertia::render('Users/Index', [
    'users' => User::paginate(10),
    'filters' => request()->only(['search', 'status']),
    'can' => [
        'create' => auth()->user()->can('create', User::class),
    ],
]);
```

### Eloquent Models

Models are automatically serialized to arrays:

```php
return Inertia::render('Users/Show', [
    'user' => $user,                    // Model → array
    'user' => $user->load('posts'),     // With relationships
    'user' => $user->only(['id', 'name']), // Specific fields
]);
```

### API Resources

Use Laravel API Resources for controlled serialization:

```php
return Inertia::render('Users/Index', [
    'users' => UserResource::collection(User::paginate(10)),
]);
```

---

## Lazy Evaluation

Wrap props in closures to defer evaluation until needed:

```php
return Inertia::render('Users/Index', [
    // Always evaluated
    'users' => User::all(),

    // Only evaluated when this prop is requested
    'companies' => fn () => Company::all(),

    // Only evaluated on partial reload requesting this prop
    'analytics' => fn () => $this->calculateAnalytics(),
]);
```

### Inertia::lazy() (Deprecated in v2)

The `Inertia::lazy()` method has been replaced by closures and `Inertia::defer()`.

---

## Optional Props

Props that are **never** included unless explicitly requested:

```php
return Inertia::render('Users/Index', [
    'users' => User::all(),
    'analytics' => Inertia::optional(fn () => $this->heavyCalculation()),
]);
```

Request with: `router.reload({ only: ['analytics'] })`

---

## Deferred Props (v2.0+)

Props loaded **after** the initial page render:

```php
return Inertia::render('Dashboard', [
    // Immediate
    'user' => $request->user(),

    // Loaded after initial render
    'stats' => Inertia::defer(fn () => $this->calculateStats()),
    'notifications' => Inertia::defer(fn () => $user->notifications),
]);
```

React component handles with `<Deferred>`:

```tsx
import { Deferred } from '@inertiajs/react';

function Dashboard({ user, stats, notifications }) {
  return (
    <div>
      <h1>Welcome, {user.name}</h1>

      <Deferred data="stats" fallback={<Spinner />}>
        <StatsWidget stats={stats} />
      </Deferred>
    </div>
  );
}
```

See `11-deferred-props.md` for more details.

---

## Always Props

Props that are **always** included, even in partial reloads:

```php
return Inertia::render('Users/Index', [
    'users' => User::all(),
    'flash' => Inertia::always(fn () => session('message')),
]);
```

---

## Redirects

### Basic Redirect

```php
public function store(Request $request)
{
    User::create($request->validated());

    return redirect()->route('users.index');
}
```

### Redirect with Flash Message

```php
return redirect()
    ->route('users.index')
    ->with('message', 'User created successfully!');
```

### Redirect Back

```php
return redirect()->back()->with('message', 'Settings updated.');
```

### External Redirect

```php
return Inertia::location('https://example.com');
```

---

## Shorthand Route

For simple pages without controller logic:

```php
// routes/web.php
Route::inertia('/about', 'About');
Route::inertia('/contact', 'Contact', ['email' => 'hello@example.com']);
```

---

## Response Headers

### Custom Headers

```php
return Inertia::render('Users/Index', [
    'users' => User::all(),
])->withHeaders([
    'X-Custom-Header' => 'value',
]);
```

### Caching Headers

```php
return Inertia::render('Static/About')
    ->toResponse($request)
    ->header('Cache-Control', 'public, max-age=3600');
```

---

## BudTags Examples

### Controller with Organization Scoping

```php
public function index(Request $request)
{
    $org = $request->user()->active_org;

    return Inertia::render('Packages/Index', [
        'packages' => Package::where('org_id', $org->id)
            ->latest()
            ->paginate(25),
        'filters' => $request->only(['search', 'status']),
    ]);
}
```

### Controller with Metrc License Context

```php
public function plants(Request $request)
{
    $license = $request->session()->get('license');

    return Inertia::render('Plants/Index', [
        'license' => $license,
        'plants' => fn () => $this->metrcService->getPlants($license),
        'locations' => fn () => $this->metrcService->getLocations($license),
    ]);
}
```

---

## Next Steps

- **Page Components** → Read `04-pages-components.md`
- **Shared Data** → Read `09-shared-data.md`
- **Deferred Props** → Read `11-deferred-props.md`
