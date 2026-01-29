# CRM & Contacts - LeafLink API Category

Complete reference for customer relationship management endpoints - 12 total operations.

---

## Collection Reference

**OpenAPI Schema:** `schemas/openapi-crm.json`
**Total Endpoints:** 12
**Company Compatibility:** All company types

---

## Endpoint Overview

### Contacts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/contacts/` | List contacts |
| POST | `/contacts/` | Create contact |
| GET | `/contacts/{id}/` | Get contact details |
| PATCH | `/contacts/{id}/` | Update contact |
| DELETE | `/contacts/{id}/` | Delete contact |

### Activity Entries

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/activity-entries/` | List activity log entries |
| POST | `/activity-entries/` | Create activity entry |
| GET | `/activity-entries/{id}/` | Get activity details |
| PATCH | `/activity-entries/{id}/` | Update activity |
| DELETE | `/activity-entries/{id}/` | Delete activity |

### Notes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notes/` | List notes |
| POST | `/notes/` | Create note |

---

## Common Use Cases

### 1. Create Contact

```php
$response = $api->post('/contacts/', [
    'first_name' => 'John',
    'last_name' => 'Smith',
    'email' => 'john@example.com',
    'phone' => '555-0123',
    'company' => $companyId,
    'customer' => $customerId,  // Optional: link to customer
    'title' => 'Purchasing Manager',
    'is_primary' => true
]);
```

### 2. List Contacts for Customer

```php
$response = $api->get('/contacts/', [
    'customer' => $customerId,
    'active' => 'true',
    'is_primary' => 'true'
]);

$contacts = $response->json('results');
```

### 3. Log Activity Entry

```php
$response = $api->post('/activity-entries/', [
    'customer' => $customerId,
    'contact' => $contactId,  // Optional
    'activity_type' => 'call',  // call, email, meeting, note
    'subject' => 'Follow-up call regarding order',
    'description' => 'Discussed delivery timeline and payment terms.',
    'activity_date' => now()->toIso8601String(),
    'user' => $userId
]);
```

### 4. Get Activity History

```php
// Get all activities for a customer
$response = $api->get('/activity-entries/', [
    'customer' => $customerId,
    'activity_date__gte' => '2025-01-01',
    'activity_date__lte' => '2025-01-31',
    'limit' => 100
]);

$activities = $response->json('results');
```

### 5. Update Contact

```php
$response = $api->patch("/contacts/{$contactId}/", [
    'email' => 'new.email@example.com',
    'phone' => '555-9999',
    'is_primary' => true
]);
```

---

## Available Filters

### Contact Filters
- `customer` - Customer ID
- `company` - Company ID
- `email__icontains` - Email search
- `first_name__icontains`, `last_name__icontains` - Name search
- `is_primary` - Primary contact flag
- `active` - Active status

### Activity Filters
- `customer` - Customer ID
- `contact` - Contact ID
- `user` - User who created activity
- `activity_type` - Type of activity
- `activity_date__gte`, `activity_date__lte` - Date range
- `subject__icontains` - Subject search

### Date Filters
- `created_date__gte`, `created_date__lte`
- `modified__gte`, `modified__lte`

---

## Activity Types

Common activity types:
- `call` - Phone call
- `email` - Email correspondence
- `meeting` - In-person or virtual meeting
- `note` - General note/comment
- `order` - Order-related activity
- `visit` - Site visit

---

## Important Notes

### Contact vs Customer

- **Customer** = Company/organization (buyer)
- **Contact** = Individual person at customer company
- One customer can have multiple contacts
- Each contact linked to one customer

### Primary Contacts

- Each customer should have one primary contact
- Primary contact receives important notifications
- Set `is_primary: true` for main point of contact

### Activity Tracking

Activity entries provide:
- Complete interaction history
- Sales pipeline visibility
- Customer relationship insights
- Compliance documentation

---

## Related Resources

- **Scenarios:** `scenarios/customer-workflow.md` - Customer and contact management
- **Schema:** `schemas/openapi-crm.json`

---

## Quick Reference

```php
// Create contact
$api->post('/contacts/', ['first_name' => 'John', 'email' => 'john@example.com', 'customer' => $id]);

// List contacts
$api->get('/contacts/', ['customer' => $customerId, 'active' => 'true']);

// Log activity
$api->post('/activity-entries/', ['customer' => $id, 'activity_type' => 'call', 'subject' => 'Follow-up']);

// Get activities
$api->get('/activity-entries/', ['customer' => $customerId, 'activity_date__gte' => '2025-01-01']);
```
