# QuickBooks Integration Skill - Package

A comprehensive, self-contained Claude skill providing complete QuickBooks Online API integration documentation with all operations, workflows, and best practices for the BudTags application.

## What's Included

This skill package contains:

- **skill.md** - Main skill file (invoke with Skill tool)
- **OPERATIONS_CATALOG.md** - Complete catalog of all 40+ QuickBooks operations
- **OAUTH_FLOW.md** - OAuth 2.0 authentication deep dive
- **WORKFLOWS/** - Step-by-step workflow guides:
  - `INVOICE_WORKFLOW.md` - Invoice creation, updating, sending
  - `PAYMENT_WORKFLOW.md` - Payment recording
  - `CREDIT_MEMO_WORKFLOW.md` - Credit memos and application
  - `METRC_SYNC_WORKFLOW.md` - Metrc-to-QuickBooks inventory sync
- **ENTITY_TYPES.md** - TypeScript type definitions reference
- **ERROR_HANDLING.md** - Common errors and solutions
- **CODE_EXAMPLES.md** - Real code examples from BudTags codebase
- **README.md** - This file

**Total Size**: ~120KB
**Total Operations**: 40+ operations across 8 categories

---

## Installation

### For You (Already Installed)
This skill is already installed in your project at:
```
.claude/skills/quickbooks/
```

### For Your Partner

1. **Copy the entire directory**:
   ```bash
   # Copy this entire folder:
   .claude/skills/quickbooks/

   # To their project's skills directory:
   their-project/.claude/skills/quickbooks/
   ```

2. **Verify installation**:
   - The directory structure should match:
     ```
     .claude/skills/quickbooks/
     ├── skill.md
     ├── OPERATIONS_CATALOG.md
     ├── OAUTH_FLOW.md
     ├── ENTITY_TYPES.md
     ├── ERROR_HANDLING.md
     ├── CODE_EXAMPLES.md
     ├── README.md
     └── WORKFLOWS/
         ├── INVOICE_WORKFLOW.md
         ├── PAYMENT_WORKFLOW.md
         ├── CREDIT_MEMO_WORKFLOW.md
         └── METRC_SYNC_WORKFLOW.md
     ```

3. **Done!** Claude will automatically detect and load the skill.

---

## How to Use

### Method 1: Skill Tool (Recommended)
```
You: Use the quickbooks skill to show me how to create an invoice

Claude: [Invokes skill, provides comprehensive invoice creation guide with code examples]
```

### Method 2: Direct Questions
Just ask Claude about QuickBooks integration - it will automatically use this skill:
```
You: How do I record a payment against an invoice in QuickBooks?

Claude: Use the create_payment() method...
[Provides details from skill with complete code examples]
```

### Method 3: Workflow-Specific Questions
```
You: Show me the Metrc-to-QuickBooks sync workflow

Claude: [Provides complete sync workflow with item mapping and quantity updates]
```

---

## What Claude Can Do With This Skill

When this skill is active, Claude can:

✅ **Guide OAuth Setup** - Walk through complete OAuth 2.0 authentication flow
✅ **Create Invoices** - Generate invoices with line items, customers, payment terms
✅ **Record Payments** - Show how to record payments against invoices
✅ **Manage Credits** - Create and apply credit memos
✅ **Sync Inventory** - Explain Metrc-to-QuickBooks item mapping and quantity sync
✅ **Handle Errors** - Troubleshoot common QuickBooks API errors (SyncToken, validation, etc.)
✅ **Provide Code Examples** - Show real code from QuickBooksApi.php
✅ **Explain Data Types** - Reference TypeScript types and entity structures

---

## Example Interactions

### Getting Started
```
You: What QuickBooks operations are available?

Claude: I have complete documentation for 40+ QuickBooks operations across 8 categories:

📋 Core Operations:
- Authentication & Token Management (4 methods)
- Customer Operations (8 methods)
- Invoice Operations (9 methods)
- Item/Product Operations (7 methods)
- Credit Memo Operations (5 methods)
- Payment Operations (3 methods)
- Account Operations (5 methods)
- Utilities (3 methods)

What category would you like to explore?
```

### Creating an Invoice
```
You: How do I create an invoice with multiple line items?

Claude: Use the create_invoice() method:

```php
$invoice = $qbo->create_invoice([
    'customer_id' => '123',
    'line_items' => [
        [
            'item_id' => '456',
            'quantity' => 10,
            'unit_price' => 25.00,
            'description' => 'Premium Cannabis Flower'
        ]
    ]
]);
```

[Provides complete example with all options]

See WORKFLOWS/INVOICE_WORKFLOW.md for complete invoice management guide.
```

### OAuth Troubleshooting
```
You: I'm getting "Invalid OAuth state" error

Claude: This error indicates a CSRF state mismatch. Common causes:
1. Browser session expired during OAuth flow
2. User navigated away and came back
3. Session storage issue

Solution: Restart the OAuth flow by redirecting to /quickbooks/login

[Provides complete troubleshooting steps from OAUTH_FLOW.md]
```

### Metrc Sync
```
You: How do I sync inventory from Metrc to QuickBooks?

Claude: The Metrc-to-QuickBooks sync involves:

1. **Item Mapping** - Map Metrc items to QuickBooks items (one-time setup)
2. **Quantity Sync** - Update QBO quantities from Metrc packages

```php
$result = $qbo->sync_quantities_from_metrc();
// Returns: ['synced' => 15, 'failed' => 0, 'skipped' => 3]
```

[Provides complete workflow from METRC_SYNC_WORKFLOW.md]
```

---

## Skill Features

### 1. Complete Operations Catalog
All 40+ operations organized by category with:
- Method signatures
- Parameters (required and optional)
- Return types
- Usage examples
- Common use cases

### 2. Workflow Guides
Step-by-step guides for:
- **Invoice Workflow** - Creating, updating, sending invoices
- **Payment Workflow** - Recording payments with all options
- **Credit Memo Workflow** - Issuing refunds and applying credits
- **Metrc Sync Workflow** - Item mapping and quantity sync

### 3. OAuth Authentication Guide
Comprehensive OAuth 2.0 documentation:
- Complete authentication flow
- Token storage and refresh
- Multi-tenant support
- Troubleshooting common issues

### 4. Error Handling
Common QuickBooks API errors:
- SyncToken mismatch/stale object errors
- Authentication/token errors
- Validation errors
- Business logic errors
- Connection/network errors
- Rate limiting

### 5. TypeScript Types
Complete type definitions for:
- Customer, Invoice, Company
- Payment methods, Accounts
- Line items, Addresses
- All QuickBooks entities

### 6. Real Code Examples
27 code examples from actual BudTags codebase:
- Controller implementations
- Error handling patterns
- Frontend integration
- Batch operations

---

## Sharing This Package

### Option 1: Zip File (Already Available)
```bash
# Zip already created at:
C:\Users\Jason\Downloads\quickbooks-skill.zip

# Share with your partner
# They extract to their .claude/skills/ directory
```

### Option 2: Git Repository
If your project is in git:
```bash
# Commit the skill package
git add .claude/skills/quickbooks/
git commit -m "Add QuickBooks integration skill"
git push

# Partner pulls the repo
git pull

# Skill is automatically available
```

### Option 3: Cloud Storage
Upload the `quickbooks/` folder to:
- Dropbox
- Google Drive
- OneDrive
- Any file sharing service

Partner downloads and places in their `.claude/skills/` directory.

---

## Package Structure

```
.claude/skills/quickbooks/
├── skill.md (~12KB)
│   └── Main skill file with overview and quick start
│
├── OPERATIONS_CATALOG.md (~31KB)
│   └── Complete catalog of all 40+ operations
│
├── OAUTH_FLOW.md (~16KB)
│   └── OAuth 2.0 authentication guide
│
├── ENTITY_TYPES.md (~9KB)
│   └── TypeScript type definitions
│
├── ERROR_HANDLING.md (~10KB)
│   └── Common errors and solutions
│
├── CODE_EXAMPLES.md (~17KB)
│   └── Real code from BudTags codebase
│
├── README.md (this file, ~10KB)
│   └── Installation and usage instructions
│
└── WORKFLOWS/ (~40KB total)
    ├── INVOICE_WORKFLOW.md (~16KB)
    │   └── Complete invoice management guide
    ├── PAYMENT_WORKFLOW.md (~6KB)
    │   └── Payment recording workflow
    ├── CREDIT_MEMO_WORKFLOW.md (~6KB)
    │   └── Credit memo operations
    └── METRC_SYNC_WORKFLOW.md (~12KB)
        └── Metrc-to-QuickBooks sync guide
```

---

## QuickBooks SDK Information

**Package:** `quickbooks/v3-php-sdk`
**Version:** `^6.2`
**Type:** Official Intuit QuickBooks Online PHP SDK
**Authentication:** OAuth 2.0
**API Version:** QuickBooks Online API v3

**Key Features:**
- DataService for queries and CRUD operations
- Facade pattern for entity creation
- Automatic token refresh
- Multi-tenant support (organization-scoped)
- Caching layer for performance

---

## Updates & Maintenance

### Keeping the Skill Updated

If QuickBooks SDK or BudTags integration changes:

1. **Update operations** in `OPERATIONS_CATALOG.md`
2. **Add new workflows** to `WORKFLOWS/` directory
3. **Update code examples** in `CODE_EXAMPLES.md`
4. **Document new errors** in `ERROR_HANDLING.md`
5. **Update types** in `ENTITY_TYPES.md`

### Version Control

Consider adding to your git repo:
```bash
git add .claude/skills/quickbooks/
git commit -m "Update QuickBooks skill with new operations"
```

This allows you and your partner to stay in sync.

---

## Troubleshooting

### Skill Not Working?

1. **Check directory location**:
   ```
   .claude/skills/quickbooks/skill.md  <- Must exist
   ```

2. **Verify file structure**:
   - `skill.md` exists
   - `WORKFLOWS/` folder has 4 .md files
   - All markdown files are present

3. **Restart Claude Code**:
   - Close and reopen your IDE
   - Claude will reload all skills

4. **Check Claude Code logs**:
   - Look for skill loading errors
   - Verify no file reading errors

### Workflow Files Not Loading?

- Ensure markdown files are valid (not corrupted during copy)
- Check file permissions (must be readable)
- Verify paths don't have special characters

---

## Database Models Used

This skill documents integration with these BudTags models:

- **QboAccessKey** - Stores OAuth tokens per user/organization
- **QboItemMapping** - Maps Metrc items to QuickBooks items
- **QboSyncLog** - Tracks quantity sync operations

See `WORKFLOWS/METRC_SYNC_WORKFLOW.md` for complete model documentation.

---

## Pricing Reference for Marketplace Invoices

When generating invoices from marketplace orders, be aware of currency conversion:

- **Products/Cart:** Prices stored in **CENTS** (e.g., 42000 = $420.00)
- **Order Line Items:** Prices stored in **DOLLARS** (e.g., 420.00)
- **QuickBooks Invoices:** Prices in **DOLLARS**

**IMPORTANT:** When creating QuickBooks invoices from marketplace orders, use the dollar values from `marketplace_order_line_items` directly. Do NOT convert again!

See `.claude/docs/marketplace/pricing.md` for full currency conversion rules.

---

## License & Attribution

- **QuickBooks Online API**: © Intuit Inc.
- **QuickBooks PHP SDK**: Official Intuit SDK
- **Skill Package**: Created for BudTags project
- **Free to share** with development partners

---

## Support

### For QuickBooks API Questions:
- **Documentation**: https://developer.intuit.com/app/developer/qbo/docs/api/accounting/most-commonly-used/invoice
- **Intuit Developer**: https://developer.intuit.com/

### For Skill Package Issues:
- Check this README
- Reference workflow files in `WORKFLOWS/`
- Review `ERROR_HANDLING.md` for troubleshooting

---

## Changelog

**v1.0** - October 2025
- Initial release
- Complete QuickBooks Online API integration coverage
- 40+ operations across 8 categories
- 4 comprehensive workflow guides
- OAuth 2.0 authentication documentation
- Metrc-to-QuickBooks sync guide
- Real code examples from BudTags
- Self-contained, shareable package

---

**Made with ❤️ for the BudTags project**

*Empowering developers to integrate QuickBooks Online with cannabis compliance software efficiently and correctly.*
