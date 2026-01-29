# Data Model Question Bank

Reference this during Phase 3 (Data Model) to ensure thorough data modeling.

---

## Entity Identification

### Core Questions

- What are the "nouns" in this feature? (things that exist)
- For each noun: Is it a new entity or an attribute of existing entity?
- Is there a clear primary entity? (the main thing being created/managed)
- Are there supporting entities? (lookup tables, junction tables)
- Are there transactional entities? (events, logs, history)

### Existing Entity Integration

- Does this extend an existing entity? (add columns)
- Does this relate to existing entities? (add relationships)
- Should this be a separate entity or a type/variant of existing?

---

## Attribute Analysis

For EACH attribute, ask:

### Basics

- What is the data type?
- Is it required or optional?
- What is the default value (if any)?
- Is it mutable or immutable once set?

### Constraints

- Min/max length? (strings)
- Min/max value? (numbers)
- Allowed values? (enums)
- Format pattern? (regex)
- Unique? (globally or scoped)

### Source

- Who/what sets this value?
- When is it set? (creation, update, computed)
- Can it be changed? By whom?
- Is it derived/calculated from other fields?

### Display

- Is this user-facing?
- What is the display label?
- Does it need formatting? (currency, date, etc.)
- Is it searchable/filterable?
- Is it sortable?

---

## Relationship Analysis

For EACH relationship, ask:

### Cardinality

- One-to-one, one-to-many, or many-to-many?
- What's the owning side?
- Is the relationship required or optional?

### Lifecycle

- What happens when parent is deleted?
  - CASCADE (delete children)
  - RESTRICT (prevent deletion)
  - SET NULL (orphan children)
  - NO ACTION (database default)
- Can children exist without parent?
- Can relationship be changed after creation?

### Querying

- Will you query in both directions?
- Will you need counts? (withCount)
- Will you need exists checks? (whereHas)
- What's the expected number of related records?

---

## State Machines

For entities with status/state:

### States

- What are ALL possible states?
- What is the initial state?
- What are the terminal states? (can't leave)
- What are intermediate states?
- Is there a "catch-all" or "other" state needed?

### Transitions

- Draw the state machine: which transitions are allowed?
- What triggers each transition? (user action, time, external event)
- Who can trigger each transition? (roles/permissions)
- Is each transition reversible?
- Are there any automatic transitions? (scheduled, conditional)

### Side Effects

- What happens during each transition?
  - Notifications sent?
  - Related records updated?
  - External APIs called?
  - Background jobs queued?
  - Audit log created?

### Guards

- What conditions must be true for each transition?
- What should happen if conditions aren't met?

---

## Temporal Considerations

### Timestamps

- Need created_at? (usually yes)
- Need updated_at? (usually yes)
- Need deleted_at? (soft deletes)
- Need custom timestamps? (approved_at, activated_at)

### Date Ranges

- Does anything have start/end dates?
- Can ranges overlap?
- What happens at range boundaries?
- Time zones matter?

### History & Versioning

- Need to track changes over time?
- Full version history or just audit log?
- Need to restore previous versions?

### Scheduling

- Can records be scheduled for future?
- Auto-expire? Auto-activate?
- What about time-based state changes?

---

## Snapshot Fields

When related data might change but historical accuracy matters:

- Should price be snapshotted at order time?
- Should names be snapshotted? (user name, org name)
- Should settings be snapshotted?

Pattern:
```
pricing_tier_id  → Reference to current tier
price_snapshot   → Price at time of order (won't change)
```

---

## Indexing Strategy

- What are the common query patterns?
- What fields are filtered on frequently?
- What fields are sorted by?
- Composite indexes needed?
- Full-text search needed?

---

## BudTags Specifics

### Organization Scoping

- Does this entity belong to an organization?
- [ ] Add `organization_id` foreign key
- [ ] Add `organization()` relationship
- [ ] Add global scope for org filtering (if applicable)

### IDs

- Use UUIDs for primary keys (BudTags standard)
- Use `$table->uuid('id')->primary()`
- Use `HasUuids` trait on model

### Naming

- Tables: plural, snake_case (advertising_orders)
- Columns: singular, snake_case (pricing_tier_id)
- Relationships: snake_case (pricing_tier, not pricingTier)

---

## Data Model Documentation Template

```markdown
## Entity: {EntityName}

### Purpose
{What does this entity represent?}

### Attributes
| Column | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | yes | auto | Primary key |
| organization_id | uuid | yes | - | Owner organization |
| ... | ... | ... | ... | ... |

### Relationships
| Relationship | Type | Model | Foreign Key |
|--------------|------|-------|-------------|
| organization | belongsTo | Organization | organization_id |
| ... | ... | ... | ... |

### State Machine
{If applicable, draw states and transitions}

### Indexes
| Columns | Type | Purpose |
|---------|------|---------|
| organization_id | btree | Org scoping queries |
| status, created_at | composite | Status filtering |

### Notes
{Any special considerations}
```
