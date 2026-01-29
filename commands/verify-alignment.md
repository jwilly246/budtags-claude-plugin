# Verify Code Alignment

You are now equipped with comprehensive knowledge of BudTags coding standards and architectural patterns. Your mission is to verify that code aligns with project conventions.

## Your Mission

Assist the user by:
1. Reading the verify-alignment skill documentation
2. Understanding what code/work needs verification
3. Checking alignment with documented patterns
4. Providing detailed compliance reports
5. Offering to implement fixes

## Available Resources

**Main Skill Documentation**:
- `.claude/skills/verify-alignment/skill.md` - Complete verification instructions and critical patterns

**Project Documentation** (Referenced by skill):
- `.claude/CLAUDE.md` - Project overview
- `.claude/docs/backend/coding-style.md` - Laravel conventions (CRITICAL)
- `.claude/docs/backend/multi-tenancy.md` - Organization scoping (SECURITY CRITICAL)
- `.claude/docs/backend/architecture.md` - Architectural patterns
- `.claude/docs/frontend/components.md` - Component patterns
- `.claude/docs/frontend/structure.md` - React/Inertia structure
- `.claude/docs/integrations/metrc.md` - Metrc API patterns
- `.claude/docs/integrations/quickbooks.md` - QuickBooks patterns

## How to Use This Command

### Step 1: Load the Skill
Read the main skill file to activate verification capabilities:
```
Read: .claude/skills/verify-alignment/skill.md
```

### Step 2: Ask What to Verify
Prompt the user:
```
What work should I verify? Please provide:
- File paths to review
- Feature description or code snippets
- Specific concerns or areas to focus on
```

### Step 3: Load Relevant Documentation
Based on the work type, read appropriate documentation files (skill will guide you).

### Step 4: Perform Verification
Check against critical patterns:
- Organization scoping (security)
- Method naming (snake_case)
- Request handling (request() helper)
- Logging (LogService only)
- Service layer patterns
- Modal component patterns

### Step 5: Generate Report
Provide structured output with:
- ✅ Alignment Summary
- 🎯 Pattern Compliance checklist
- 🔍 Specific Findings with file:line references
- 💡 Recommendations (prioritized)
- 📚 Documentation References

### Step 6: Offer Follow-up
Ask: "Would you like me to implement any of these fixes?"

## Critical Reminders

### Organization Scoping (MOST IMPORTANT!)
**Every database query MUST be scoped to active organization**:
```php
// ✅ CORRECT
$items = request()->user()->active_org->items()->get();
$org_id = request()->user()->active_org_id;

// ❌ WRONG - Security vulnerability!
$items = Item::all();
```

### Method Naming
**Use snake_case with verb-first naming**:
```php
// ✅ CORRECT
public function create()
public function fetch_logs()
public function adjust_bulk()

// ❌ WRONG
public function store()
public function bulkAdjust()
```

### Logging
**ALWAYS use LogService, NEVER Log facade**:
```php
// ✅ CORRECT
LogService::store('Action', 'Description', $model);

// ❌ WRONG
Log::info('Action performed');
```

### Request Handling
**Use request() helper directly**:
```php
// ✅ CORRECT
public function create() {
    $values = request()->validate([...]);
}

// ❌ WRONG
public function create(Request $request) {
    $validated = $request->validate([...]);
}
```

## Instructions

1. **Read the main skill file** at `.claude/skills/verify-alignment/skill.md`
2. **Ask the user** what work needs verification
3. **Load relevant documentation** based on work type
4. **Check critical patterns first** (security, multi-tenancy, logging)
5. **Generate detailed report** with specific findings
6. **Provide actionable fixes** with file:line references
7. **Offer to implement** fixes if user wants

## Example Interactions

**User asks: "Check if my new controller follows patterns"**
- Read skill.md and coding-style.md
- Ask for controller file path
- Verify method naming, organization scoping, request handling
- Report findings with specific violations and fixes

**User asks: "Review my implementation plan before I code"**
- Read skill.md and relevant docs
- Review proposed approach
- Identify pattern violations before implementation
- Suggest corrections to plan

**User asks: "Is LogService::store() the correct way to log?"**
- Read skill.md
- Confirm: YES, this is the ONLY correct way
- Explain: Never use Log facade

Now, read the main skill file and help the user verify their code alignment with BudTags patterns!
