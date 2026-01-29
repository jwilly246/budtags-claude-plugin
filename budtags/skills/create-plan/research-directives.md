# Research Directives by Phase

Detailed research instructions to run alongside each planning phase. Research happens BEFORE and DURING questioning, not after.

---

## Phase 0: Codebase Discovery

**Timing:** BEFORE any user questions

### Package Inventory Research

```bash
# 1. Read composer.json for PHP dependencies
cat composer.json

# Key things to note:
# - Laravel version (require.laravel/framework)
# - PHP version (require.php)
# - Spatie packages (permissions, media-library, etc.)
# - Inertia version

# 2. Read package.json for JS dependencies
cat package.json

# Key things to note:
# - React version
# - Inertia React version
# - TanStack Query version
# - UI libraries (Headless UI, etc.)
# - Build tools (Vite, etc.)
```

### Architecture Mapping Research

```bash
# 3. Use Laravel Boost if available
php artisan boost:models 2>/dev/null || echo "Boost not available"
php artisan boost:routes 2>/dev/null || echo "Boost not available"

# 4. Manual exploration fallback
ls -la app/Models/
ls -la app/Http/Controllers/
ls -la app/Services/
ls -la app/Jobs/
ls -la resources/js/Components/
ls -la resources/js/Pages/
```

### What to Document

```markdown
## Package Versions Found
- Laravel: X.Y
- React: X.Y
- Inertia: X.Y
- TanStack Query: X.Y
- [other relevant packages]

## Architecture Overview
- Models: [count] in app/Models/
- Controllers: [pattern observed]
- Services: [list key services]
- Components: [key reusable components]
```

---

## Phase 1: Discovery

**Timing:** Before asking discovery questions

### Similar Feature Search

```bash
# Search for related keywords in the codebase
grep -r "feature_keyword" app/Http/Controllers/
grep -r "feature_keyword" app/Models/
grep -r "feature_keyword" resources/js/

# Find routes related to feature domain
grep -r "Route::" routes/ | grep "keyword"
```

### What to Document

- Existing features that overlap or relate
- Code that might be extended vs replaced
- Precedents that inform scope decisions

---

## Phase 2: User Stories

**Timing:** Before asking user story questions

### Role/Permission Research

```bash
# Find existing roles and permissions
grep -r "Role::" app/
grep -r "Permission::" app/
grep -r "can(" app/Http/Controllers/
grep -r "authorize" app/Http/Controllers/

# Check policies
ls app/Policies/

# Check permission configs
cat config/permission.php 2>/dev/null || echo "No permission config"
```

### What to Document

- Existing user types/roles
- Permission patterns in similar features
- How multi-role access is handled

---

## Phase 3: Data Model

**Timing:** Before asking data model questions

### Model Pattern Research

```bash
# List all models
ls app/Models/

# Find traits in use
grep -r "use.*Trait" app/Models/
ls app/Models/Traits/ 2>/dev/null

# Find state machines/status patterns
grep -r "const STATUS" app/Models/
grep -r "public const" app/Models/

# Check relationship patterns
grep -r "function.*BelongsTo\|HasMany\|HasOne" app/Models/
```

### What to Document

- Reusable traits available
- State machine patterns in use
- Relationship conventions
- Similar models to reference

---

## Phase 4: Business Rules

**Timing:** Before asking business rules questions

### Validation Pattern Research

```bash
# Find Form Request classes
ls app/Http/Requests/

# Find validation patterns
grep -r "public function rules" app/Http/Requests/

# Find state transition logic
grep -r "transition\|canTransition\|STATUS" app/Services/
grep -r "function.*State\|Status" app/Services/
```

### What to Document

- Existing validation patterns
- Form Request conventions
- State transition implementations
- Error handling patterns

---

## Phase 5: UI/UX

**Timing:** Before asking UI questions

### Component Inventory Research

```bash
# List all components
ls -R resources/js/Components/

# Find form components
ls resources/js/Components/Inputs/ 2>/dev/null
ls resources/js/Components/Forms/ 2>/dev/null

# Find modal patterns
grep -r "Modal" resources/js/Components/
ls resources/js/Components/Modals/ 2>/dev/null

# Find custom hooks
ls resources/js/hooks/ 2>/dev/null

# Find similar pages
ls resources/js/Pages/
```

### What to Document

```markdown
## Reusable Components Found
- Inputs: TextInput, SelectInput, Checkbox, etc.
- Layout: DataTable, Card, Modal, etc.
- Feedback: Toast, Alert, Badge, etc.

## Similar UI Patterns
- [SimilarPage].tsx - can reference for layout
- [SimilarModal].tsx - can reference for form pattern

## Custom Hooks Available
- useXxx - for [purpose]
```

---

## Phase 6: Integration

**Timing:** Before asking integration questions

### Service Layer Research

```bash
# Find existing services
ls app/Services/

# Find API client patterns
grep -r "Http::\|Guzzle\|curl" app/Services/

# Find job patterns
ls app/Jobs/
grep -r "implements ShouldQueue" app/Jobs/

# Find notification patterns
ls app/Notifications/ 2>/dev/null

# Find event patterns
ls app/Events/ 2>/dev/null
ls app/Listeners/ 2>/dev/null
```

### What to Document

- API client patterns to follow
- Job implementation patterns
- Notification templates
- Event/listener patterns

---

## Phase 7: Security

**Timing:** Before asking security questions

### Security Pattern Research

```bash
# Find policies
ls app/Policies/

# Find middleware
ls app/Http/Middleware/

# Find authorization patterns
grep -r "abort_if\|abort_unless\|authorize" app/Http/Controllers/

# Find org-scoping patterns
grep -r "active_org\|organization_id" app/Http/Controllers/
```

### What to Document

- Policy patterns in use
- Middleware available
- Authorization comment styles
- Org-scoping implementation patterns

---

## Phase 8: Performance

**Timing:** Before asking performance questions

### Performance Pattern Research

```bash
# Find caching patterns
grep -r "Cache::\|cache(" app/
grep -r "remember\|rememberForever" app/

# Find eager loading patterns
grep -r "with(\|load(" app/Http/Controllers/

# Check existing indexes in migrations
grep -r "->index(\|->unique(" database/migrations/
```

### What to Document

- Caching strategies in use
- Eager loading patterns
- Index conventions
- Rate limiting implementations

---

## Phase 9: Testing

**Timing:** Before asking testing questions

### Test Pattern Research

```bash
# Find test structure
ls tests/Feature/
ls tests/Unit/

# Find test traits/helpers
grep -r "trait\|use " tests/

# Find factory patterns
ls database/factories/
grep -r "public function definition" database/factories/

# Find security test patterns
grep -r "cannot.*other.*org\|Forbidden\|403" tests/
```

### What to Document

- Test file organization
- Helper traits available
- Factory states defined
- Security test patterns

---

## Research Output Template

After each phase's research, document findings:

```markdown
### Research Findings: Phase {N}

**Relevant Existing Code:**
- {File/Class}: {What it does, why relevant}

**Reusable Patterns:**
- {Pattern}: Found in {location}

**Recommendations:**
- Reuse: {what to reuse}
- Extend: {what to extend}
- Create new: {what must be new}
```

---

## Anti-Patterns

**DO NOT:**
- Skip research and jump to questions
- Assume package versions without checking
- Suggest recreating existing components
- Plan new patterns when established patterns exist
- Add packages to plan without pitching them first

**DO:**
- Research before every phase
- Document what was found
- Present discoveries to user
- Reference existing code in plan
- Make the case for packages (user is open to them, just needs justification)
