# Metrc API Reference Skill - Package

A comprehensive, modular Claude skill providing complete Metrc API v2 reference using **progressive disclosure** - loading only the information relevant to each task.

## What's Included

This skill package uses a **progressive disclosure architecture** with:

- **skill.md** - Main orchestration file (~200 lines) - routes to relevant resources
- **categories/** - 26 modular category files (~50-80 lines each)
  - Focused endpoint documentation per category
  - Examples: packages.md, plants.md, sales.md
- **scenarios/** - 8 task-based workflow templates (~80-100 lines each)
  - Step-by-step implementation guides
  - Examples: create-packages-from-harvest.md, move-plants-to-flowering.md
- **patterns/** - 6 pattern files (~40-80 lines each)
  - Authentication, license-types, pagination, batch-operations, date-formats, error-handling
  - Extracted from original METRC_API_RULES.md
- **collections/** - All 26 Postman collection files (366KB total)
  - Full endpoint details (methods, paths, parameters, request/response structures)
  - Valid Postman Collection v2.1.0 format (can be imported into Postman)
- **METRC_API_RULES.md.backup** - Original comprehensive rules (preserved for reference)

**Total Size**: ~520KB (with modular files)
**Total Endpoints**: 290+ endpoints
**Context Efficiency**: 60-85% reduction in context usage vs monolithic approach

---

## Installation

### For You (Already Installed)
This skill is already installed in your project at:
```
.claude/skills/metrc-api/
```

### For Your Partner

1. **Copy the entire directory**:
   ```bash
   # Copy this entire folder:
   .claude/skills/metrc-api/

   # To their project's skills directory:
   their-project/.claude/skills/metrc-api/
   ```

2. **Verify installation**:
   - The directory structure should match:
     ```
     .claude/skills/metrc-api/
     ├── skill.md
     ├── METRC_API_RULES.md
     ├── README.md
     └── collections/
         └── (26 .json files)
     ```

3. **Done!** Claude will automatically detect and load the skill.

---

## How to Use

### Method 1: Skill Tool (Recommended)
```
You: Use the metrc-api skill to show me all package endpoints

Claude: [Invokes skill, provides comprehensive list of 31 package endpoints]
```

### Method 2: Direct Questions
Just ask Claude about Metrc API - it will automatically use this skill:
```
You: How do I get active packages from Metrc?

Claude: Use GET /packages/v2/active with licenseNumber parameter...
[Provides details from skill]
```

### Method 3: Specific Category Questions
```
You: Show me all plant endpoints

Claude: [Lists 33 plant endpoints, warns about cultivation license requirement]
```

---

## What Claude Can Do With This Skill

When this skill is active, Claude can:

✅ **Find Endpoints** - Search 258 endpoints by name, category, method, or purpose
✅ **Provide Exact Details** - Read collection JSON files for request/response formats
✅ **Check License Compatibility** - Warn about cultivation vs retail restrictions
✅ **Explain Patterns** - Reference authentication, pagination, batch operations
✅ **Generate Code** - Create Laravel/PHP code examples with correct formats
✅ **Debug Integration Issues** - Help troubleshoot common Metrc API problems

---

## Example Interactions

### Getting Started
```
You: What Metrc endpoints are available?

Claude: I have complete documentation for all 290+ Metrc API v2 endpoints across 26 categories:

📦 Core Operations:
- Packages (32 endpoints)
- Plants (36 endpoints) - Cultivation only
- Sales (36 endpoints) - Retail only
- Transfers (28 endpoints)
- Harvests (15 endpoints)

[Lists all 26 categories]

What category would you like to explore?
```

### Searching for Specific Endpoint
```
You: How do I create packages from a harvest?

Claude: Use POST /harvests/v2/packages

License compatibility: All license types
Required: licenseNumber query parameter

Let me read the exact format from the collection file...

[Shows complete request structure with all fields]

Example code:
[Provides Laravel/PHP implementation]
```

### License Restriction Check
```
You: Can I use plant endpoints with a retail license?

Claude: ❌ NO. Plant endpoints are ONLY for Cultivation licenses (AU-C-######).

Retail licenses (AU-R-######) will receive 401/403 errors when accessing:
- /plants/v2/*
- /plantbatches/v2/*

Retail licenses CAN access:
- /packages/v2/*
- /sales/v2/*
- /transfers/v2/*

[Provides complete license compatibility matrix]
```

### Debugging Integration Issues
```
You: I'm getting "No valid endpoint found" error from Metrc

Claude: This typically indicates a license type mismatch. Let me check...

What license type are you using? (Cultivation, Processing, or Retail)
What endpoint are you calling?

[Helps diagnose and fix the issue]
```

---

## Skill Features

### 1. Complete Endpoint Catalog
All 290+ endpoints organized by category with:
- HTTP methods (GET, POST, PUT, DELETE)
- URL paths
- Required parameters
- License compatibility

### 2. Detailed Collection Files
26 Postman collection JSON files containing:
- Full request/response structures
- Query parameters
- Request body schemas
- Example values

### 3. Integration Patterns (METRC_API_RULES.md)
Comprehensive guide covering:
- Authentication requirements
- Common query parameters
- Request/response patterns
- Endpoint naming conventions
- Date & time formats
- Pagination patterns
- Batch operations
- **License type restrictions** (CRITICAL!)
- Error handling
- Best practices

---

## Sharing This Package

### Option 1: Direct Copy
```bash
# Zip the entire directory
zip -r metrc-api-skill.zip .claude/skills/metrc-api/

# Share the zip file with your partner
# They extract to their .claude/skills/ directory
```

### Option 2: Git Repository
If your project is in git:
```bash
# Commit the skill package
git add .claude/skills/metrc-api/
git commit -m "Add Metrc API reference skill"
git push

# Partner pulls the repo
git pull

# Skill is automatically available
```

### Option 3: Cloud Storage
Upload the `metrc-api/` folder to:
- Dropbox
- Google Drive
- OneDrive
- Any file sharing service

Partner downloads and places in their `.claude/skills/` directory.

---

## Package Structure

```
.claude/skills/metrc-api/
├── skill.md (~370 lines)
│   └── Main orchestration file with progressive disclosure routing
│
├── categories/ (26 files, ~50-80 lines each)
│   ├── packages.md - 32 endpoints (all licenses)
│   ├── plants.md - 36 endpoints (CULTIVATION ONLY)
│   ├── plantbatches.md - 21 endpoints (CULTIVATION ONLY)
│   ├── sales.md - 36 endpoints (RETAIL ONLY)
│   ├── harvests.md - 15 endpoints
│   ├── items.md - 16 endpoints
│   ├── transfers.md - 28 endpoints
│   ├── labtests.md - 8 endpoints
│   ├── processingjob.md - 17 endpoints
│   ├── locations.md - 7 endpoints
│   ├── sublocations.md - 6 endpoints
│   ├── strains.md - 6 endpoints
│   ├── tags.md - 3 endpoints
│   ├── transporters.md - 10 endpoints
│   ├── patients.md - 5 endpoints (retail medical)
│   ├── patientsstatus.md - 1 endpoint
│   ├── patientcheckins.md - 5 endpoints
│   ├── caregiversstatus.md - 1 endpoint
│   ├── additivestemplates.md - 5 endpoints
│   ├── unitsofmeasure.md - 2 endpoints
│   ├── wastemethods.md - 1 endpoint
│   ├── retailid.md - 6 endpoints
│   ├── facilities.md - 1 endpoint
│   ├── employees.md - 2 endpoints
│   ├── sandbox.md - 1 endpoint
│   └── webhooks.md - 5 endpoints
│
├── scenarios/ (8 files, ~80-100 lines each)
│   ├── create-packages-from-harvest.md
│   ├── move-plants-to-flowering.md
│   ├── record-sales-receipt.md
│   ├── check-in-incoming-transfer.md
│   ├── record-lab-test-results.md
│   ├── adjust-package-quantity.md
│   ├── create-new-strain.md
│   └── replace-plant-tags.md
│
├── patterns/ (6 files, ~40-80 lines each)
│   ├── authentication.md - API key setup, base URLs
│   ├── license-types.md - Cultivation vs Processing vs Retail (CRITICAL!)
│   ├── pagination.md - pageNumber/pageSize patterns
│   ├── batch-operations.md - Array-based requests
│   ├── date-formats.md - ISO 8601 requirements
│   └── error-handling.md - HTTP codes, retry strategies
│
├── collections/ (26 files, 366KB total)
│   └── (All Postman collection JSON files - unchanged)
│
├── METRC_API_RULES.md.backup (355 lines)
│   └── Original comprehensive rules (preserved for reference)
│
└── README.md (this file)
    └── Installation, usage, and structure documentation
```

**Total Files**: 1 main + 26 categories + 8 scenarios + 6 patterns + 26 collections = **67 files**
**Total Size**: ~520KB (with modular progressive disclosure architecture)

---

## Updates & Maintenance

### Keeping the Skill Updated

If Metrc releases API updates:

1. **Get new Postman collection** from Metrc
2. **Re-run the split script** (from original split directory):
   ```bash
   python split_collection.py
   ```
3. **Replace collections/** folder with new split files
4. **Update skill.md** if new categories are added
5. **Update METRC_API_RULES.md** if patterns change

### Version Control

Consider adding to your git repo:
```bash
git add .claude/skills/metrc-api/
git commit -m "Update Metrc API skill to v2.x"
```

This allows you and your partner to stay in sync.

---

## Troubleshooting

### Skill Not Working?

1. **Check directory location**:
   ```
   .claude/skills/metrc-api/skill.md  <- Must exist
   ```

2. **Verify file structure**:
   - `skill.md` exists
   - `collections/` folder has 26 .json files
   - `METRC_API_RULES.md` exists

3. **Restart Claude Code**:
   - Close and reopen your IDE
   - Claude will reload all skills

4. **Check Claude Code logs**:
   - Look for skill loading errors
   - Verify no JSON parsing errors

### Collection Files Not Loading?

- Ensure JSON files are valid (not corrupted during copy)
- Check file permissions (must be readable)
- Verify paths don't have special characters

---

## License & Attribution

- **Metrc API Documentation**: © Metrc LLC
- **Postman Collection**: Provided by Metrc
- **Skill Package**: Created for BudTags project
- **Free to share** with development partners

---

## Support

### For Metrc API Questions:
- **Documentation**: https://api-ca.metrc.com/Documentation
- **Metrc Support**: Contact through your state's Metrc portal

### For Skill Package Issues:
- Check this README
- Reference `METRC_API_RULES.md`
- Review `skill.md` for usage examples

---

## Changelog

**v2.0.1** - February 2026
- Clarified rate limiting architecture: GET requests use Redis-based rate limiter, POST/PUT/DELETE are object-limited only (max 10/request, no `sleep()` needed between chunks)
- Updated batch-operations pattern to remove incorrect `sleep()` guidance between POST chunks

**v2.0** - January 2026
- Updated from new Postman collection
- Added 47 new endpoints (290+ total)
- New RetailId category (QR codes, package merge, consumer lookup)
- Expanded Sales with hub deliveries and retailer delivery routes
- Expanded Packages with donation flags, trade samples, decontamination
- Expanded Transfers with hub operations and PDF manifest
- Added Items brand management
- Added ProcessingJob job types management
- Added Transporters driver/vehicle CRUD
- Added Plants merge, strain change, additives templates
- Enhanced auto-activation keywords
- All Postman collection JSONs updated

**v1.0** - January 2025
- Initial release
- Complete Metrc API v2 coverage
- 258 endpoints across 26 categories
- Comprehensive license restriction documentation
- Self-contained, shareable package

---

**Made with ❤️ for the cannabis compliance community**

*Empowering developers to integrate with Metrc API efficiently and correctly.*
