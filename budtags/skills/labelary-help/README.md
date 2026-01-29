# Labelary API - Claude Code Skill

A comprehensive Claude skill providing complete knowledge of the **Labelary ZPL Rendering API** for converting ZPL (Zebra Programming Language) to images, PDFs, and other printer formats.

## What's Included

- **skill.md** - Main skill file with complete API reference (~23KB, 650+ lines)
- **API_REFERENCE.md** - Detailed endpoint documentation with all parameters and options
- **CODE_EXAMPLES.md** - Real React/TypeScript implementation from BudTags project
- **INTEGRATION_GUIDE.md** - Step-by-step integration walkthrough
- **docs/** - Complete Labelary documentation (8 files):
  - `00-README.md` - Documentation index and quick reference
  - `01-introduction-overview.md` - API basics, GET vs POST
  - `02-parameters-reference.md` - URL parameters reference
  - `03-limits-and-pricing.md` - Free tier limits and premium plans
  - `04-examples-web-scripting.md` - curl, PowerShell, PHP, ColdFusion, Excel VBA examples
  - `05-examples-programming-languages.md` - Java, Python, Ruby, Node.js, C#, Rust, Go examples
  - `06-advanced-features.md` - Rotation, PDF layouts, linting, data extraction
  - `07-image-font-conversion.md` - Image and font conversion endpoints
- **WORKFLOWS/** - Task-specific guides (3 files):
  - `ZPL_PREVIEW_WORKFLOW.md` - Implementing live ZPL preview modals
  - `IMAGE_CONVERSION_WORKFLOW.md` - Converting images to ZPL graphics
  - `FONT_CONVERSION_WORKFLOW.md` - Converting TrueType fonts to ZPL

**Total Size**: ~85KB across 15 files

## What is Labelary?

Labelary is a **free online ZPL rendering engine** that converts Zebra Programming Language (ZPL) code into various output formats via a simple RESTful API.

**Base API URL:** `http://api.labelary.com/v1/`

**Key Features:**
- ✅ Free for personal and commercial use (no sign-up required)
- ✅ 9 output formats: PNG, PDF, IPL, EPL, DPL, SBPL, PCL5, PCL6, JSON
- ✅ Advanced PDF features (multi-label pages, custom layouts, rotations)
- ✅ Image-to-ZPL and Font-to-ZPL conversion
- ✅ Built-in ZPL linting and error detection
- ✅ CORS-enabled for browser-based requests
- ✅ Premium plans for higher rate limits

**Rate Limits (Free Tier):**
- 3 requests per second
- 5,000 requests per day
- No API key required

## Installation

This skill is installed at:
```
.claude/skills/labelary-help/
```

To copy to another project:
```bash
cp -r .claude/skills/labelary-help /path/to/project/.claude/skills/
```

## Usage

Invoke this skill when you need help with:
- Converting ZPL to images/PDFs
- Implementing ZPL preview functionality
- Converting images or fonts to ZPL
- Understanding Labelary API parameters and features

**Invoke:** "Use the labelary-help skill"

**Example queries:**
- "How do I convert ZPL to a PNG image using the Labelary API?"
- "Show me how to implement a ZPL preview modal in React"
- "How do I convert an image to ZPL graphics?"
- "What are the rate limits for the free Labelary tier?"

## Quick Start

### Basic ZPL to PNG Conversion

```bash
curl --get http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data-urlencode "^xa^cfa,50^fo100,100^fdHello World^fs^xz" > label.png
```

### React/TypeScript Integration (from BudTags)

```typescript
const fetchLabelaryImage = async () => {
    const dpmm = Math.round(dpi / 25.4); // Convert DPI to dpmm
    const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${widthInches}x${heightInches}/0/`;

    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: zplCode,
    });

    const blob = await response.blob();
    return URL.createObjectURL(blob);
};
```

**See:** `CODE_EXAMPLES.md` for complete implementation

## File Structure

```
labelary-help/
├── skill.md                        ← Main entry point
├── README.md                       ← This file
├── API_REFERENCE.md                ← Complete API documentation
├── CODE_EXAMPLES.md                ← Real BudTags implementation
├── INTEGRATION_GUIDE.md            ← Integration walkthrough
├── docs/                           ← Full documentation
│   ├── 00-README.md
│   ├── 01-introduction-overview.md
│   ├── 02-parameters-reference.md
│   ├── 03-limits-and-pricing.md
│   ├── 04-examples-web-scripting.md
│   ├── 05-examples-programming-languages.md
│   ├── 06-advanced-features.md
│   └── 07-image-font-conversion.md
└── WORKFLOWS/                      ← Task-specific guides
    ├── ZPL_PREVIEW_WORKFLOW.md
    ├── IMAGE_CONVERSION_WORKFLOW.md
    └── FONT_CONVERSION_WORKFLOW.md
```

## API Endpoints

| Endpoint | Purpose | Output Formats |
|----------|---------|----------------|
| `GET/POST /v1/printers/{dpmm}/labels/{width}x{height}/{index}/` | Convert ZPL to image/PDF | PNG, PDF, IPL, EPL, DPL, SBPL, PCL5, PCL6, JSON |
| `POST /v1/graphics` | Convert image to ZPL | ZPL, JSON, EPL, IPL, DPL, SBPL, PCL5, PCL6 |
| `POST /v1/fonts` | Convert TrueType to ZPL | ZPL (font commands) |

## Common Use Cases

| Use Case | Start Here |
|----------|------------|
| First time using Labelary | `skill.md` → Quick Start Guide |
| Implementing ZPL preview modal | `WORKFLOWS/ZPL_PREVIEW_WORKFLOW.md` |
| Understanding API parameters | `API_REFERENCE.md` |
| React/TypeScript integration | `CODE_EXAMPLES.md` |
| Converting images to ZPL | `WORKFLOWS/IMAGE_CONVERSION_WORKFLOW.md` |
| Converting fonts to ZPL | `WORKFLOWS/FONT_CONVERSION_WORKFLOW.md` |
| Advanced PDF features | `docs/06-advanced-features.md` |
| Rate limits and pricing | `docs/03-limits-and-pricing.md` |
| Curl/shell examples | `docs/04-examples-web-scripting.md` |
| Python/Java/Node examples | `docs/05-examples-programming-languages.md` |

## Integration with Other Skills

This skill works alongside:

- **zpl** (`.claude/skills/zpl/`) - Complete ZPL II programming language reference
  - Use **zpl** to generate ZPL code
  - Use **labelary-help** to render/preview the ZPL

**Workflow:**
1. Generate ZPL using **zpl skill** knowledge
2. Preview/render using **labelary-help skill** API integration
3. Iterate and refine

## Real-World Implementation

This skill includes actual code from the **BudTags** project:

- `LabelaryPreviewModal.tsx` - React component for live ZPL preview
- DPI to dpmm conversion logic
- Error handling patterns
- Image dimension detection
- Download functionality
- Ruler overlay implementation

**See:** `CODE_EXAMPLES.md` for complete code with explanations

## Critical Concepts

### DPI to DPMM Conversion

```javascript
// Labelary uses dpmm (dots per millimeter), not DPI
const dpmm = Math.round(dpi / 25.4);

// Valid values: 6dpmm, 8dpmm, 12dpmm, 24dpmm
// Common: 203 DPI = 8dpmm, 300 DPI = 12dpmm
```

### GET vs POST

- **GET**: Simple requests, small ZPL (<3,000 chars)
- **POST**: Production apps, large ZPL, sensitive data (recommended)

### Output Format Control

```bash
# PNG (default)
--header "Accept: image/png"

# PDF
--header "Accept: application/pdf"

# JSON (data extraction)
--header "Accept: application/json"
```

## Documentation Quality

All documentation files are:
- ✅ AI-optimized for quick consumption
- ✅ Split into focused sections
- ✅ Generated from official Labelary documentation
- ✅ Cross-referenced for easy navigation
- ✅ Includes real code examples

## Premium Plans

If free tier limits are too restrictive:

| Plan | Price | Requests/sec | Requests/day |
|------|-------|--------------|--------------|
| Free | $0 | 3 | 5,000 |
| Plus | $90/month | 6 | 20,000 |
| Business | $228/month | 10 | 40,000 |
| On-Prem | Custom | Unlimited | Unlimited |

**See:** `docs/03-limits-and-pricing.md` for complete details

## Support

**Labelary API Issues:**
- Official docs: https://labelary.com
- This skill provides offline reference

**Skill Issues:**
- This skill was generated from official Labelary documentation
- All code examples are from real BudTags implementation
- Report issues to your project maintainer

## Skill Metadata

- **Version**: 1.0.0
- **Created**: 2025-11-02
- **Source**: Official Labelary API Documentation
- **Pattern**: API Integration (Premium)
- **Real Code From**: BudTags project (React/TypeScript)
- **Total Files**: 15
- **Total Size**: ~85KB

---

**Last Updated**: 2025-11-02
**Skill Type**: API Integration
**Completeness**: Premium (Complete coverage)
