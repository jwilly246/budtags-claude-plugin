---
name: create-plan
description: Thorough, question-driven feature planning. Asks questions you haven't thought of. Fills gaps with questions, not assumptions. Produces comprehensive plan documents ready for decomposition.
version: 1.0.0
category: workflow
auto_activate:
  keywords:
    - "create plan"
    - "plan feature"
    - "new feature"
    - "design feature"
    - "plan this"
---

# Create Plan Skill

**PURPOSE:** Transform a feature idea into a comprehensive, implementation-ready plan through active codebase research and thorough questioning.

**PHILOSOPHY:** 5 hours planning, 1 hour coding. Research before asking. Ask questions you haven't thought of. Fill gaps with questions, not assumptions. Reuse before creating.

---

## CRITICAL RULES

```
╔══════════════════════════════════════════════════════════════════╗
║  THIS SKILL RESEARCHES THE CODEBASE, ASKS QUESTIONS, AND WRITES ║
║  A PLAN DOCUMENT.                                                ║
║                                                                   ║
║  ✅ DO: Research the codebase BEFORE asking questions            ║
║  ✅ DO: Identify reusable code, patterns, and components         ║
║  ✅ DO: Check installed packages before suggesting new ones      ║
║  ✅ DO: Ask probing questions before making decisions            ║
║  ✅ DO: Challenge assumptions                                     ║
║  ✅ DO: Cover edge cases and error scenarios                      ║
║  ✅ DO: Explore integration points thoroughly                     ║
║  ✅ DO: Document decisions WITH rationale                         ║
║  ✅ DO: Produce a plan ready for /decompose-plan                  ║
║                                                                   ║
║  ❌ DO NOT: Make assumptions without asking                       ║
║  ❌ DO NOT: Skip codebase research                                ║
║  ❌ DO NOT: Assume package versions - READ them                   ║
║  ❌ DO NOT: Install packages without explicit permission          ║
║  ❌ DO NOT: Skip domains (security, testing, edge cases)          ║
║  ❌ DO NOT: Write implementation code                             ║
║  ❌ DO NOT: Rush through phases to "get to coding"                ║
║  ❌ DO NOT: Accept vague answers - dig deeper                     ║
║                                                                   ║
║  WHEN IN DOUBT: RESEARCH FIRST, THEN ASK. NEVER ASSUME.         ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Command

```
/create-plan <feature-name>
```

**Example:**
```
/create-plan marketplace-advertising
```

---

## Workflow Overview

The skill progresses through **11 phases**, starting with codebase research. Don't rush - each phase matters.

```
Phase 0: Codebase Discovery → Research existing code, packages, patterns (MANDATORY)
Phase 1: Discovery          → What are we building? Why?
Phase 2: User Stories       → Who uses it? What do they do?
Phase 3: Data Model         → What entities? Relationships?
Phase 4: Business Rules     → Edge cases? Constraints? State machines?
Phase 5: UI/UX              → Where does it live? How does it look?
Phase 6: Integration        → External APIs? Existing systems?
Phase 7: Security           → Access control? Data protection?
Phase 8: Performance        → Scale? Caching? Rate limiting?
Phase 9: Testing Strategy   → What to test? How to verify?
Phase 10: Synthesis         → Write the plan document
```

**Phase 0 is MANDATORY:** Always research the codebase before asking questions.
**Between phases:** Summarize what was decided, confirm understanding, then proceed.

---

## Phase 0: Codebase Discovery (MANDATORY)

**Goal:** Research the codebase before asking ANY user questions. Understand what exists, what can be reused, and what patterns to follow.

### 0.1 Package Inventory

Run these checks FIRST:

```bash
# Read composer.json - note Laravel version, installed packages
cat composer.json

# Read package.json - note React version, UI libraries, tooling
cat package.json

# Check for Laravel Boost (if installed)
composer show spatie/laravel-boost 2>/dev/null || echo "Laravel Boost not installed"
```

**Document:**
- Laravel version (e.g., `^11.0`)
- PHP version requirement
- React/Inertia version
- Key packages: Spatie permissions, Tanstack Query, etc.
- UI framework: Tailwind, Headless UI, etc.

### 0.2 Architecture Mapping

Use Laravel Boost (if available) or manual exploration:

```bash
# With Laravel Boost
php artisan boost:models  # List all models with relationships
php artisan boost:routes  # List all routes

# Without Laravel Boost - manual exploration
ls -la app/Models/
ls -la app/Http/Controllers/
ls -la resources/js/Components/
ls -la app/Services/
```

**Document:**
- Existing models and their relationships
- Controller organization pattern
- Component library structure
- Service layer patterns

### 0.3 Similar Feature Search

Search for features similar to what the user is requesting:

```bash
# Grep for related keywords in controllers, models, components
grep -r "keyword" app/Http/Controllers/
grep -r "keyword" app/Models/
grep -r "keyword" resources/js/

# Find similar implementations
find . -name "*Similar*.php" -o -name "*Related*.tsx"
```

**Actions:**
- Read 2-3 similar implementations to understand patterns
- Note reusable code, services, or components
- Identify established conventions

### 0.4 Component & Service Inventory

Catalog reusable assets:

**Frontend Components:**
```bash
ls resources/js/Components/
ls resources/js/Components/Inputs/
ls resources/js/Components/Modals/
ls resources/js/hooks/
```

**Backend Services:**
```bash
ls app/Services/
ls app/Models/Traits/
```

### 0.5 Document Findings

Before Phase 1, present to user:

```markdown
## Phase 0 Summary: Codebase Discovery

### Package Versions
| Package | Version |
|---------|---------|
| Laravel | {version from composer.json} |
| React | {version from package.json} |
| Inertia | {version} |
| TanStack Query | {version} |

### Similar Features Found
- **{FeatureName}**: {location} - {what it does}
- **{FeatureName}**: {location} - {what it does}

### Reusable Components Discovered
- **UI Components**: Button, TextInput, DataTable, Modal...
- **Services**: {ServiceName} pattern in app/Services/
- **Traits**: {TraitName} in app/Models/Traits/

### Patterns Observed
- Controller naming: {pattern}
- Route structure: {pattern}
- Modal patterns: {pattern}

### Proceeding to Phase 1: Discovery
```

---

## Phase 1: Discovery

**Goal:** Understand the feature at a high level.

### Research Directive (run alongside questions)

Before asking discovery questions, search for existing related features:
1. Search for keywords related to the feature in controllers, models, routes
2. Read any similar existing features to understand precedents
3. Note if this extends, replaces, or interacts with existing functionality

**Present discoveries:** "I found existing {feature} in {location} that may be related to what you're describing."

### Questions to Ask

**Business Value:**
- What problem does this solve?
- Who requested this feature? Why?
- What's the expected ROI or business impact?
- Is this MVP or full-featured? What's the timeline pressure?

**Scope Definition:**
- In one sentence, what does this feature do?
- What does this feature explicitly NOT do? (scope boundaries)
- Are there existing features this replaces, extends, or interacts with?
- Is this a new domain or extending an existing one?

**Success Criteria:**
- How will we know this feature is successful?
- What metrics matter? (usage, revenue, time saved, etc.)
- What's the minimum viable version?

### Red Flags to Probe

- Vague descriptions ("make it better", "improve the flow")
- Scope creep indicators ("and also...", "while we're at it...")
- Missing stakeholder clarity ("users want..." - which users?)

---

## Phase 2: User Stories

**Goal:** Understand ALL user types and their complete journeys.

### Research Directive (run alongside questions)

Before asking user story questions, check existing role/permission implementations:
1. Search for existing roles, permissions, policies in the codebase
2. Find how other features handle multi-role access
3. Check existing user type distinctions (admin vs seller vs buyer, etc.)

**Present discoveries:** "I found these existing user roles/permissions: {list}. The {SimilarFeature} handles role-based access by {pattern}."

### Questions to Ask

**User Types:**
- Who are ALL the users of this feature?
- What role/permission level does each user type have?
- Are there admin/internal users with different capabilities?
- Are there unauthenticated users involved?

**For EACH User Type:**
- What can they create/read/update/delete?
- What's their primary goal with this feature?
- What's their typical workflow (step by step)?
- What information do they need to see?
- What actions do they need to take?
- What feedback do they need after actions?

**Edge Cases:**
- What if a user tries to do something they shouldn't?
- What if a user is in multiple roles?
- What happens when a user leaves the organization?
- What about first-time users vs. experienced users?

### Output: User Story Matrix

| User Type | Can Create | Can Read | Can Update | Can Delete | Special Actions |
|-----------|------------|----------|------------|------------|-----------------|
| Seller    | Orders     | Own orders, pricing | Own pending orders | Own pending orders | Cancel, view analytics |
| Admin     | Pricing tiers | All orders | Order status | Pricing tiers | Approve, reject, activate |

---

## Phase 3: Data Model

**Goal:** Define all entities, their attributes, and relationships.

### Research Directive (run alongside questions)

Before asking data model questions, examine existing models:
1. Read existing models to understand attribute patterns, relationships, traits
2. Find models with similar purposes or patterns
3. Check for reusable traits (HasOrganization, HasStatus, etc.)
4. Note existing state machine implementations

**Present discoveries:** "I found these relevant model patterns: {Model} uses {Trait} for {purpose}. The {SimilarModel} has a status state machine you could follow."

### Questions to Ask

**Entities:**
- What are the core "things" in this feature?
- For each entity: What attributes does it have?
- Which fields are required vs optional?
- Which fields have constraints (length, format, range)?
- Are there calculated/derived fields?

**Relationships:**
- How do entities relate to each other?
- What are the cardinalities? (one-to-one, one-to-many, many-to-many)
- Are relationships required or optional?
- What happens when a related entity is deleted? (cascade, restrict, nullify)

**State Machines:**
- Do any entities have status/state?
- What are ALL the possible states?
- What transitions are allowed? (draw the state machine)
- Who/what can trigger each transition?
- Are transitions reversible?

**Temporal Aspects:**
- Does anything need date ranges? (start/end dates)
- Is historical data needed? (audit trails, versioning)
- Do records expire? Auto-archive?
- Time zones matter?

**BudTags Specifics:**
- Is this organization-scoped? (almost always yes)
- Is this user-specific within an organization?
- Should it use UUIDs or auto-increment IDs?

### Output: Schema Draft

```
Entity: AdvertisingOrder
├── id (uuid)
├── organization_id (fk, required) ── ORGANIZATION SCOPING
├── status (enum: pending → approved → ...) ── STATE MACHINE
├── price_snapshot (int, cents) ── IMMUTABLE COPY
├── requested_start_date (date, required)
├── actual_start_date (date, nullable) ── SET LATER
└── timestamps
```

---

## Phase 4: Business Rules

**Goal:** Capture ALL the rules, constraints, and edge cases.

### Research Directive (run alongside questions)

Before asking business rules questions, find existing validation patterns:
1. Search for Form Request classes with similar validation
2. Find existing state machines and transition logic
3. Look for validation helpers or services
4. Check how other features handle edge cases

**Present discoveries:** "I found these existing validation patterns: {FormRequest} validates {similar fields}. The {Service} handles state transitions using {pattern}."

### Questions to Ask

**Validation Rules:**
- What makes data valid or invalid?
- Are there field-level validations? (format, length, range)
- Are there cross-field validations? (end date > start date)
- Are there business rule validations? (can't order if already have active)

**State Transition Rules:**
- What conditions must be met for each state transition?
- What happens during each transition? (side effects)
- Can transitions fail? What happens then?
- Are there timed/scheduled transitions?

**Edge Cases (THE HARD QUESTIONS):**
- What if the user submits twice rapidly? (idempotency)
- What if payment fails after approval?
- What if an admin deletes a pricing tier that has active orders?
- What if the referenced image is deleted from storage?
- What if two admins try to approve the same order simultaneously?
- What happens at the boundary of date ranges?
- What if the organization is deactivated mid-process?

**Constraints:**
- Are there limits? (max orders per org, max images, etc.)
- Are there rate limits? (submissions per day)
- Are there exclusivity rules? (only one active ad at a time)
- Are there scheduling conflicts possible?

**Error Handling:**
- What errors can occur?
- How should each error be communicated to the user?
- Are errors recoverable? How?
- Should errors be logged? Alerted?

---

## Phase 5: UI/UX

**Goal:** Understand where this lives in the app and how users interact.

### Research Directive (run alongside questions)

Before asking UI questions, catalog what exists:
1. List all components in `resources/js/Components/`
2. Find similar pages/modals to the feature being planned
3. Identify form patterns already in use
4. Note any custom hooks in `resources/js/hooks/`
5. Check existing page layouts and navigation patterns

**Present discoveries:** "I found these existing components you could reuse: Button, TextInput, DataTable, Modal. There's also an existing {SimilarModal} that has a similar pattern to what you're describing. The {SimilarPage} shows how navigation is structured."

### Questions to Ask

**Navigation & Placement:**
- Where does this feature live in the navigation?
- Is it a new page, a new tab, or a new section?
- Does it need its own route or attach to existing routes?
- Who sees the navigation item? (permission-based visibility)

**Layout & Components:**
- What existing components can be reused?
- Are there similar UIs in the app to use as reference?
- What's the information hierarchy? (primary, secondary, tertiary)

**Forms & Modals (CRITICAL - BudTags uses Inertia useForm):**
- Are there forms in this feature? List each one.
- For each form: What fields? What validation?
- Are forms in modals or inline on pages?
- Should modals be self-contained (own their form state)?
- What happens on successful submission? (close modal, redirect, show message)
- What happens on validation error? (inline errors from useForm)

**Data Fetching Pattern Decision:**
| Scenario | Use This |
|----------|----------|
| Form submission, CRUD | Inertia useForm |
| Read-only dashboard data | React Query |
| Real-time/polling data | React Query |
| Navigation with data | Inertia page props |

- Which pattern does each part of this feature need?
- Are there existing similar forms/modals to use as reference?

**Interactions:**
- What actions can users take?
- Do actions need confirmation? (delete, irreversible actions)
- What feedback after actions? (toast, redirect, inline update)
- Are there bulk actions?

**States & Loading:**
- What does the empty state look like?
- What does the loading state look like?
- What does the error state look like?
- What does the success state look like?

**Responsive & Accessibility:**
- Does this need to work on mobile?
- Are there accessibility requirements?
- Does it need keyboard navigation?

**Real-time:**
- Does anything need live updates?
- WebSocket/SSE or polling?
- What frequency?

---

## Phase 6: Integration

**Goal:** Understand all integration points with external systems and existing code.

### Research Directive (run alongside questions)

Before asking integration questions, map existing integrations:
1. Find existing API clients in `app/Services/`
2. Check for existing job patterns in `app/Jobs/`
3. Look for notification patterns in `app/Notifications/`
4. Find existing webhook handlers
5. Check file storage patterns

**Present discoveries:** "I found existing integrations: {Service} handles {ExternalAPI} calls with retry logic. The {Job} pattern shows how background processing is structured."

### Questions to Ask

**External APIs:**
- Does this integrate with external services? (Metrc, QuickBooks, LeafLink, etc.)
- What data flows to/from each service?
- What authentication is needed?
- What happens when the external service is down?
- Are there webhooks involved?
- What's the retry strategy for failures?

**Existing Code:**
- What existing models/services does this interact with?
- What existing controllers need modification?
- Are there shared utilities to leverage?
- Are there existing patterns to follow?

**File Storage:**
- Are there file uploads?
- What file types, sizes, dimensions?
- Where are files stored? (S3, local)
- How are files served? (direct, signed URLs, CDN)

**Email/Notifications:**
- Should users be notified? When?
- Email, in-app notification, or both?
- What's the notification content?
- Are there admin notifications?

**Background Jobs:**
- Are there long-running operations?
- What needs to be queued?
- What happens if a job fails?
- Are there scheduled jobs?

---

## Phase 7: Security

**Goal:** Identify and address ALL security concerns.

### Research Directive (run alongside questions)

Before asking security questions, find existing auth patterns:
1. Check existing policies in `app/Policies/`
2. Find middleware patterns in `app/Http/Middleware/`
3. Look for authorization patterns in existing controllers
4. Check how org-scoping is enforced in similar features

**Present discoveries:** "I found these security patterns: {Policy} handles {authorization}. The {Controller} enforces org-scoping using {pattern}. Existing middleware: {list}."

### Questions to Ask

**Authentication:**
- Which routes require authentication?
- Are there any public routes?
- Session-based or API token?

**Authorization:**
- What permissions are required for each action?
- Is this role-based or permission-based?
- Are there organization-level permissions?
- Are there resource-level permissions? (can only edit own)

**Data Access:**
- Can users see other organizations' data? (MUST be NO)
- Can users see other users' data within their org?
- What about soft-deleted or archived data?

**Input Validation:**
- What inputs come from users?
- What sanitization is needed?
- Are there file upload security concerns?
- SQL injection, XSS, CSRF covered?

**Sensitive Data:**
- Is any data sensitive? (PII, financial, etc.)
- Does it need encryption at rest?
- Does it need to be excluded from logs?
- Data retention requirements?

**Rate Limiting:**
- Should actions be rate limited?
- Per user, per organization, or global?
- What are the limits?

### Output: Security Checklist

- [ ] All queries scoped to `request()->user()->active_org`
- [ ] Authorization checks on every action
- [ ] Input validation via Form Request classes
- [ ] File upload validation (type, size, dimensions)
- [ ] Rate limiting on public endpoints
- [ ] No sensitive data in logs

---

## Phase 8: Performance

**Goal:** Ensure the feature will perform well at scale.

### Research Directive (run alongside questions)

Before asking performance questions, check existing patterns:
1. Find caching implementations in existing code
2. Look for query optimization patterns (eager loading, etc.)
3. Check existing indexes in migrations
4. Find rate limiting implementations

**Present discoveries:** "I found these performance patterns: {Model} uses eager loading for {relationships}. The {Controller} caches {data} for {duration}. Existing indexes: {list}."

### Questions to Ask

**Scale Expectations:**
- How many records are expected? (10s, 1000s, millions)
- How many concurrent users?
- What's the read vs write ratio?
- Peak load times?

**Query Performance:**
- What are the common queries?
- What indexes are needed?
- Are there N+1 query risks?
- Are there expensive joins?

**Caching:**
- What can be cached?
- Cache invalidation strategy?
- Cache duration?
- Redis vs in-memory?

**Rate Limiting:**
- What operations should be limited?
- What are reasonable limits?
- How to handle limit exceeded?

---

## Phase 9: Testing Strategy

**Goal:** Define how to verify the feature works correctly.

### Research Directive (run alongside questions)

Before asking testing questions, find existing test patterns:
1. Find test patterns in `tests/Feature/` for similar features
2. Check for test helper traits in `tests/`
3. Look at existing factories and their states
4. Find how security/org-scoping tests are structured

**Present discoveries:** "I found these test patterns: {TestClass} tests {feature} with {pattern}. The {Factory} has useful states: {states}. Security tests follow {pattern}."

### Questions to Ask

**Unit Tests:**
- What services/helpers need unit tests?
- What are the key methods to test?
- What edge cases in business logic?

**Feature Tests:**
- What are the happy path scenarios?
- What are the error scenarios?
- What are the security scenarios? (MUST have org scoping tests)
- What state transitions to test?

**Browser Tests:**
- Are there complex UI interactions to test?
- Multi-step workflows?
- JavaScript-dependent features?

**Integration Tests:**
- External API integration tests?
- How to mock external services?

### Output: Test Scenarios List

```
Feature: AdvertisingSellerController
├── test_seller_can_view_advertising_settings
├── test_seller_can_submit_ad_order
├── test_seller_cannot_view_other_org_orders  ← SECURITY
├── test_seller_can_cancel_pending_order
├── test_seller_cannot_cancel_active_order
└── test_order_snapshots_price_at_creation
```

---

## Phase 10: Synthesis

**Goal:** Compile everything into the plan document.

### Plan Document Structure

```markdown
# {FEATURE_NAME} Implementation Plan

## Overview
{2-3 sentences on what we're building and why}

## Requirements Summary
| Area | Requirements |
|------|-------------|
| ... | ... |

## Database Schema
{Tables, columns, relationships, indexes}

## Models
{Model definitions, relationships, scopes, factories}

## Backend Implementation
{Controllers, services, routes, form requests}

## Frontend Implementation
{Data fetching strategy, components, types}

## Integration Points
{External APIs, existing code touchpoints}

## Implementation Phases
{Ordered checklist of phases}

## Key Files to Create
{File manifest}

## Key Files to Modify
{Modification manifest}

## Verification Plan
{How to test it works}

## BudTags Alignment Checklist
{Pattern compliance verification}
```

### Final Questions Before Writing

- Have we covered all user types?
- Have we identified all edge cases?
- Have we addressed all security concerns?
- Have we documented all decisions with rationale?
- Is the plan detailed enough for `/decompose-plan`?

---

## Question Banks

For comprehensive question coverage, reference:

- `question-banks/data-model.md` - Deep data modeling questions
- `question-banks/security.md` - Security audit questions
- `question-banks/edge-cases.md` - Common edge case scenarios
- `question-banks/integration.md` - Integration point questions
- `question-banks/budtags-specific.md` - BudTags pattern questions

---

## Package Awareness Rules

### CRITICAL: Never Assume Versions

- Always READ `composer.json` and `package.json` before referencing packages
- Don't assume Laravel 11 - check the actual version
- Don't assume React 19 - check the actual version
- Don't assume TanStack Query v5 - check the actual version

### Package Suggestion Protocol

1. **Check if functionality exists in already-installed packages FIRST**
2. If new package would help, **make the case for it:**
   - What problem does it solve?
   - What's the alternative without it? (more code, reinventing the wheel, etc.)
   - Is it well-maintained? What's the community like?
   - Any downsides? (bundle size, complexity, learning curve)
3. Get explicit approval before adding to the plan
4. User is open to packages - just needs reasonable justification

### Package Research Workflow

```markdown
## Before suggesting any package:

1. Read composer.json and package.json
2. Check if functionality exists in already-installed packages
3. If new package would help, pitch it:
   - "This feature needs X. Package Y does this well because..."
   - "Without it, we'd have to build [effort]. With it, we get [benefit]."
   - "It's maintained by [who], last release [when], [N] stars."
4. Get buy-in, then add to plan
```

### Laravel Boost Integration

BudTags projects have Laravel Boost installed. Leverage it for introspection:

```bash
# Model introspection
php artisan boost:models  # List all models with relationships

# Route introspection
php artisan boost:routes  # List all routes

# Use in Phase 0 for rapid codebase mapping
```

---

## Research Directives Reference

For detailed research instructions per phase, see: `research-directives.md`

---

## Conversation Flow Guidelines

### How to Ask Questions

1. **Group related questions** - Don't ask one at a time
2. **Prioritize** - Ask critical questions first
3. **Give context** - Explain why you're asking
4. **Offer examples** - Help the user understand the question
5. **Accept "I don't know"** - Then help figure it out together

### How to Handle Responses

1. **Summarize understanding** - "So if I understand correctly..."
2. **Identify gaps** - "You mentioned X but not Y..."
3. **Challenge vagueness** - "Can you be more specific about..."
4. **Document decisions** - "We've decided to... because..."

### Phase Transitions

After each phase:
```markdown
## Phase {N} Summary

**Decisions Made:**
- Decision 1: {choice} because {rationale}
- Decision 2: {choice} because {rationale}

**Open Questions:**
- Question 1 (will address in Phase {M})

**Proceeding to Phase {N+1}: {Phase Name}**
```

---

## Anti-Patterns

❌ "I'll assume X for now..." - ASK INSTEAD
❌ Skipping security questions because "it's internal"
❌ Accepting "same as feature Y" without documenting specifics
❌ Rushing through edge cases
❌ Writing the plan before all questions are answered
❌ Making UX decisions without understanding user workflows
❌ Ignoring error scenarios

---

## Success Criteria

The planning is complete when:

- [ ] Phase 0 codebase research completed
- [ ] Package versions documented (not assumed)
- [ ] Reusable code identified and cataloged
- [ ] All 10 question phases have been covered
- [ ] User stories are documented for ALL user types
- [ ] Data model is fully defined with state machines
- [ ] Edge cases are identified and addressed
- [ ] Security concerns are documented
- [ ] Integration points are mapped
- [ ] Testing strategy is defined
- [ ] Plan document includes reusable code references
- [ ] Plan document is comprehensive enough for `/decompose-plan`
- [ ] User confirms the plan matches their vision

---

## Output

When planning is complete:

1. Write `{FEATURE_NAME}-FEATURE-PLAN.md` in project root
2. Summarize key decisions and their rationale
3. Note any deferred decisions or open questions
4. Suggest running `/decompose-plan {FEATURE_NAME}-FEATURE-PLAN.md`

**DO NOT start implementing. Planning is its own phase.**
