# Integration Question Bank

Reference this during Phase 6 (Integration) to ensure thorough integration coverage.

---

## External API Integration

### General Questions

- Which external services does this feature interact with?
- What data flows TO the external service?
- What data flows FROM the external service?
- Is this synchronous or asynchronous?
- Is this triggered by user action or scheduled?

### Authentication

- How does the API authenticate? (OAuth, API key, JWT)
- Where are credentials stored? (env, database)
- Do credentials expire? How to refresh?
- Are credentials per-organization or application-wide?

### Request/Response

- What are the exact API endpoints used?
- What's the request format? (JSON, XML, form data)
- What's the response format?
- What fields are required? Optional?
- Are there pagination considerations?

### Error Handling

- What errors can the API return?
- How to handle rate limiting?
- How to handle timeout?
- How to handle partial failures?
- What's the retry strategy?
- Should errors be logged? Alerted?

### Failure Modes

- What if the API is completely down?
- What if the API returns invalid data?
- What if the API is very slow?
- Can the feature work in degraded mode without the API?
- How to communicate API failures to users?

### Testing

- Is there a sandbox/test environment?
- Are there test credentials?
- How to mock the API in tests?
- How to test error scenarios?

---

## BudTags-Specific Integrations

### Metrc

- Which Metrc endpoints are involved?
- What license type? (cultivation, retail, etc.)
- Is this read or write to Metrc?
- How does Metrc sync timing work?
- What about Metrc rate limits?
- How to handle Metrc validation errors?

### QuickBooks

- What QuickBooks entities? (Invoice, Customer, Payment)
- OAuth token refresh handling?
- What happens if QB integration not set up for org?
- How to handle QB validation errors?
- Invoice line items format?
- Tax handling?

### LeafLink

- Which LeafLink APIs? (orders, products, inventory)
- Company type? (seller, buyer)
- Webhook handling?
- Data sync strategy?

---

## Existing Codebase Integration

### Models

- Which existing models need modification?
- New relationships to add?
- New scopes to add?
- New attributes to add?

### Services

- Are there existing services to leverage?
- New services to create?
- Service dependencies?

### Controllers

- Existing controllers to modify?
- New controllers to create?
- Controller naming patterns?

### Routes

- Route prefix/group conventions?
- Middleware requirements?
- Route naming convention?

### Jobs & Queues

- Existing job patterns to follow?
- Queue names to use?
- Retry/failure handling patterns?

---

## File Storage

### Upload Questions

- What file types are allowed?
- What's the max file size?
- Are there dimension requirements? (images)
- What about file naming? (original name, uuid, slug)

### Storage Questions

- Where stored? (S3, local, other)
- Public or private access?
- CDN in front?
- Signed URLs needed?

### Processing Questions

- Need to process files? (resize, compress)
- Synchronous or async processing?
- Keep original and processed versions?

### Cleanup Questions

- When to delete files?
- Orphaned file handling?
- Storage cost considerations?

---

## Email/Notifications

### When to Notify

- What events trigger notifications?
- Who receives each notification?
- Immediate or batched/digested?

### Channel Questions

- Email, in-app, or both?
- Push notifications?
- SMS?

### Content Questions

- What's in each notification?
- Template or dynamic content?
- Personalization needed?
- Localization/i18n?

### Delivery Questions

- What if delivery fails?
- Retry strategy?
- Bounce handling?

---

## Background Jobs

### Identification

- What operations are too slow for request?
- What operations should be async?
- What operations are scheduled?

### Job Design

- Idempotency - can job run twice safely?
- Chunking - how to handle large datasets?
- Progress tracking needed?
- User notification of completion?

### Failure Handling

- Retry strategy? (count, backoff)
- Dead letter queue?
- Manual retry interface?
- Alerting on failures?

### Dependencies

- Job dependencies? (one must finish before another)
- Exclusive execution? (only one at a time)
- Resource constraints? (API rate limits)

---

## Events & Webhooks

### Outgoing Webhooks

- What events should trigger webhooks?
- Webhook payload format?
- Retry strategy for failed deliveries?
- Webhook signature for security?

### Incoming Webhooks

- What webhooks do we receive?
- Webhook authentication/verification?
- Idempotency handling?
- Processing strategy? (immediate, queued)

---

## Integration Checklist Template

```markdown
## Integration: {Service Name}

### Overview
- **Direction:** Inbound / Outbound / Bidirectional
- **Trigger:** User action / Scheduled / Webhook
- **Criticality:** Required / Optional / Degraded mode available

### Endpoints Used
| Endpoint | Method | Purpose | Frequency |
|----------|--------|---------|-----------|
| /api/v1/resource | POST | Create resource | Per user action |

### Authentication
- **Method:** {OAuth 2.0, API Key, etc.}
- **Credentials Location:** {env, database}
- **Refresh Strategy:** {if applicable}

### Error Handling
| Error | Response | User Message |
|-------|----------|--------------|
| 401 | Refresh token, retry | - |
| 429 | Backoff, retry | "Please try again later" |
| 500 | Log, alert, retry | "Service temporarily unavailable" |

### Testing
- **Sandbox:** {URL or N/A}
- **Test Credentials:** {env vars}
- **Mock Strategy:** {How to mock in tests}
```
