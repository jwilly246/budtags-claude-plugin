# Security Question Bank

Reference this during Phase 7 (Security) to ensure comprehensive security coverage.

---

## Authentication

- Which endpoints require authentication?
- Are there any intentionally public endpoints?
- How is authentication verified? (session, token, API key)
- What happens when authentication fails?
- Are there different authentication methods for different routes?
- How are API tokens scoped and rotated?
- Is there rate limiting on authentication attempts?

## Authorization

### Role-Based

- What roles can access this feature?
- Are roles hierarchical? (admin > manager > user)
- Can roles be combined?
- What's the default permission for new roles?

### Permission-Based

- What specific permissions are required?
- Are permissions additive or exclusive?
- Can permissions be granted at organization level?
- Can permissions be granted per-resource?

### Resource-Based

- Can users only access their own resources?
- Can users access resources of other users in their org?
- Are there shared/public resources within an org?
- What about resources created by deleted users?

## Data Access Control (CRITICAL for BudTags)

### Organization Scoping

- [ ] Is EVERY query scoped to `request()->user()->active_org`?
- [ ] Are there any global queries that bypass org scoping?
- [ ] What about queries in background jobs? (no request context)
- [ ] What about queries in console commands?
- [ ] Are relationships properly scoped? (can't traverse to other orgs)

### Cross-Organization Exposure

- Can user A see user B's data from another org?
- Can URL manipulation expose other org's data?
- Are IDs predictable? (UUIDs preferred over sequential)
- Are there any aggregate endpoints that might leak data?
- What about search/autocomplete exposing other orgs?

### Soft Deletes & Archives

- Can soft-deleted records be accessed?
- Can archived records be accessed?
- What about records belonging to deactivated orgs?

## Input Validation

### Data Types

- Are all inputs type-checked?
- Are enums validated against allowed values?
- Are UUIDs validated?
- Are dates validated for format and range?
- Are numbers validated for range?

### Strings

- Max length enforced?
- HTML/script tags stripped?
- SQL injection prevented?
- Unicode handling correct?
- Null bytes handled?

### Files

- File type validated? (not just extension)
- File size limited?
- Image dimensions validated?
- Malicious file content scanned?
- Filename sanitized?

### Arrays & Objects

- Max array size limited?
- Nested depth limited?
- Unexpected keys rejected or ignored?

## Output Encoding

- Is HTML output escaped? (XSS prevention)
- Is JSON output properly encoded?
- Are user-controlled values in URLs encoded?
- Are error messages exposing sensitive info?
- Are stack traces hidden in production?

## CSRF Protection

- Are all state-changing routes protected?
- Is CSRF token validated?
- Are API routes properly exempted or protected differently?

## Rate Limiting

- Which endpoints need rate limiting?
- What are appropriate limits?
- Per-user or per-IP?
- What response for limit exceeded?
- Is there abuse detection?

## Sensitive Data Handling

### Identification

- What data is PII? (names, emails, addresses)
- What data is financial? (prices, payments)
- What data is confidential? (internal notes, rejection reasons)

### Storage

- Should any data be encrypted at rest?
- Should any data be hashed? (passwords, tokens)
- What about encryption keys - where stored?

### Transmission

- All traffic over HTTPS?
- Sensitive data in headers or body? (not URL)
- API responses exclude sensitive fields?

### Logging

- Is sensitive data excluded from logs?
- Are request bodies logged? Should they be?
- Are error messages sanitized?

### Retention

- How long is data retained?
- Is there a data deletion process?
- What about backups?

## Session Security

- Session timeout appropriate?
- Session invalidated on logout?
- Session invalidated on password change?
- Concurrent session handling?
- Session fixation prevented?

## API Security

- Are API endpoints versioned?
- Is there API documentation that might expose too much?
- Are deprecated endpoints secured?
- Are error responses consistent? (don't leak info)

## Audit Logging

- Are security-relevant actions logged?
- Who/what/when captured?
- Are logs tamper-proof?
- Can logs be correlated with user sessions?

---

## Security Checklist Template

```markdown
## Security Verification

### Authentication
- [ ] All protected routes require authentication
- [ ] Authentication failures return generic errors
- [ ] Rate limiting on auth endpoints

### Authorization
- [ ] Permission checks on all actions
- [ ] Organization scoping on all queries
- [ ] Resource ownership verified

### Input Validation
- [ ] All inputs validated via Form Request
- [ ] File uploads validated (type, size, content)
- [ ] No raw user input in queries

### Output
- [ ] HTML properly escaped
- [ ] Error messages don't leak info
- [ ] Sensitive data excluded from responses

### Data Protection
- [ ] Sensitive data not logged
- [ ] HTTPS only
- [ ] Appropriate retention policies
```
