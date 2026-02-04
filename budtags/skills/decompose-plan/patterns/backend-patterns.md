# Backend Patterns (Quick Reference)

Essential patterns for backend work in BudTags.

## Controller Pattern

```php
class FeatureController extends Controller
{
    public function fetch_all(): Response  // snake_case!
    {
        $org = request()->user()->active_org;

        $items = $org->featureItems()
            ->with('relationship')
            ->latest()
            ->paginate(15);

        return Inertia::render('Feature/Index', ['items' => $items]);
    }

    public function create(): RedirectResponse
    {
        $v = request()->validate([
            'name' => 'required|string|max:255',
        ]);

        $item = request()->user()->active_org->featureItems()->create($v);

        LogService::store('Created Feature', "Created: {$item->name}", $item);

        return redirect()->route('features-index')->with('message', 'Created.');
    }
}
```

## Route Pattern

```php
Route::middleware(['auth', 'verified'])->prefix('features')->group(function () {
    Route::get('/', [FeatureController::class, 'fetch_all']);
    Route::post('/', [FeatureController::class, 'create']);
    Route::get('/{feature}', [FeatureController::class, 'fetch_one']);
});
```

## Critical Rules

- **snake_case** method names: `fetch_all`, `fetch_one`, `create`, `delete`
- **request()** helper, not Request injection
- **Organization scoping**: Always query through `$org->relationship()`
- **LogService::store()**, never Log facade
- **Flash**: `->with('message', 'text')`, not 'success'
- **No named routes**: Do not add `->name()` to routes
