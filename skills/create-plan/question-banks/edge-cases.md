# Edge Cases Question Bank

Reference this during Phase 4 (Business Rules) to ensure thorough edge case coverage.

---

## Timing & Concurrency

- What if two users perform the same action at the exact same time?
- What if a record is modified while someone is viewing it?
- What if a related record is deleted during a transaction?
- What if the user refreshes mid-operation?
- What if the user clicks submit twice rapidly?
- What if a background job processes stale data?
- What about race conditions in status transitions?

## Boundaries & Limits

- What happens at zero? (zero items, zero balance, etc.)
- What happens at the maximum limit?
- What happens just over the limit?
- What about very long text inputs?
- What about special characters? Unicode? Emoji?
- What about dates at year boundaries?
- What about time zones and DST transitions?
- What about leap years?

## State Transitions

- What if someone tries to skip a state?
- What if someone tries to go backwards in state?
- What if the state becomes invalid due to external changes?
- What happens to in-flight operations when state changes?
- Can an entity be in two states simultaneously?
- What if a required transition trigger never occurs?

## Data Integrity

- What if required related data is missing?
- What if referenced data is deleted (orphans)?
- What if cached data becomes stale?
- What if a calculation produces invalid results?
- What about floating point precision issues?
- What if historical data needed for calculation is gone?

## User Behavior

- What if the user cancels mid-operation?
- What if the user's session expires during operation?
- What if the user changes organizations mid-operation?
- What if the user loses permission mid-operation?
- What if the user opens multiple tabs?
- What if the user uses browser back/forward?
- What about copy/paste of unexpected data?

## System Failures

- What if the database write fails after some operations succeeded?
- What if an external API is down?
- What if an external API returns unexpected data?
- What if file upload succeeds but record creation fails?
- What if email/notification sending fails?
- What if a background job fails repeatedly?
- What about partial failures in bulk operations?

## Business Logic

- What if the pricing changes while an order is pending?
- What if a required resource is archived?
- What if organization settings change mid-process?
- What if feature flags toggle during operation?
- What if scheduled operations overlap?
- What if auto-expire and manual action happen simultaneously?

## Multi-Tenancy (BudTags Specific)

- What if user switches organizations during operation?
- What if an organization is deactivated with active records?
- What if a user is removed from organization with pending work?
- What about cross-organization data exposure?
- What if organization limits are reached?

## Cleanup & Maintenance

- What happens to orphaned records over time?
- What about accumulating soft-deleted data?
- What about stale files in storage?
- What about expired sessions/tokens?
- What about completed/cancelled records (archive)?

---

## Edge Case Documentation Template

For each edge case identified:

```markdown
### Edge Case: {Description}

**Scenario:** {When does this happen?}
**Current Behavior:** {What happens now, if applicable}
**Desired Behavior:** {What should happen}
**Implementation:** {How to handle it}
**Test:** {How to verify the handling}
```
