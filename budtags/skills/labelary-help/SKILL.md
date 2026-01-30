---
name: labelary-help
description: Use this skill when working with the Labelary ZPL rendering API for converting ZPL to images/PDFs, implementing ZPL preview functionality, or converting images/fonts to ZPL format.
version: 1.0.1
---

# Labelary API Skill

You are now equipped with comprehensive knowledge of the **Labelary ZPL Rendering API** via **modular category files** and **pattern guides**. This skill uses **progressive disclosure** to load only the information relevant to your task.

---

## Your Capabilities

When the user asks about Labelary or ZPL rendering, you can:

1. **Convert ZPL to Images/PDFs**: Generate PNG, PDF, or other format outputs from ZPL code via simple REST API calls
2. **Preview ZPL Labels**: Help implement real-time ZPL preview functionality in web applications
3. **Convert Images to ZPL**: Transform raster images (PNG, JPG) into ZPL graphics code
4. **Convert Fonts to ZPL**: Convert TrueType fonts to ZPL font format with optional subsetting
5. **Advanced PDF Features**: Configure multi-label PDFs, page layouts, rotations, and borders
6. **Data Extraction**: Extract text data from ZPL labels in JSON format for validation/testing
7. **Lint ZPL Code**: Detect potential errors and warnings in ZPL templates
8. **Integration Patterns**: Provide real-world React/TypeScript implementation examples from BudTags project

---

## Available Resources

This skill has access to **4 category files**, **4 pattern files**, and **3 workflow guides**:

### Category Files (Modular, ~100-150 lines each)

**Core Operations**:
- `categories/getting-started.md` - Quickstart, CDN setup, basic usage, DPI/DPMM intro
- `categories/api-endpoints.md` - 4 core endpoints (ZPL→PNG/PDF, Image→ZPL, Font→ZPL)
- `categories/parameters.md` - Complete parameter reference (URL params, headers, options)
- `categories/advanced-features.md` - PDF layouts, rotation, linting, data extraction, quality

### Pattern Files (~80-120 lines each)

- `patterns/dpi-conversion.md` - DPI to DPMM conversion (CRITICAL!)
- `patterns/get-vs-post.md` - When to use GET vs POST requests
- `patterns/error-handling.md` - Rate limits, errors, troubleshooting
- `patterns/integration.md` - React/TypeScript integration patterns

### Workflow Guides (~100-200 lines each)

- `WORKFLOWS/ZPL_PREVIEW_WORKFLOW.md` - Implementing live ZPL preview modals
- `WORKFLOWS/IMAGE_CONVERSION_WORKFLOW.md` - Converting images to ZPL graphics
- `WORKFLOWS/FONT_CONVERSION_WORKFLOW.md` - Converting TrueType fonts to ZPL

### Full Documentation (reference when needed)

- `API_REFERENCE.md` - Complete API endpoint reference with all parameters and options
- `CODE_EXAMPLES.md` - Real implementation examples from BudTags project (React/TypeScript)
- `INTEGRATION_GUIDE.md` - Step-by-step guide to integrating Labelary in your application
- `docs/` directory - 8 complete Labelary documentation files

---

## Labelary API Information

**Base URL:** `http://api.labelary.com/v1/`

**Authentication:** None required (free tier)

**Rate Limits (Free Tier):**
- 3 requests per second
- 5,000 requests per day
- No sign-up required

**Key Features:**
- ✅ Free for personal and commercial use
- ✅ No API key required (free tier)
- ✅ 9 output formats (PNG, PDF, IPL, EPL, DPL, SBPL, PCL5, PCL6, JSON)
- ✅ GET and POST request methods
- ✅ Advanced PDF features (multi-label pages, layouts, rotations)
- ✅ Image-to-ZPL and Font-to-ZPL conversion
- ✅ Built-in ZPL linting and error detection
- ✅ Premium plans available for higher limits

---

## Progressive Loading Process

**IMPORTANT:** Only load files relevant to the user's question. DO NOT load all categories.

### Step 1: Context Gathering

**Ask the user or determine from context:**

"What Labelary API task are you working on? Please provide:
- Goal/task description (e.g., 'convert ZPL to PNG', 'implement preview modal')
- Specific endpoint or feature OR
- Integration problem to debug OR
- Error you're encountering"

**Determine scope:**
- Is this a getting started / setup question?
- Is this about a specific endpoint?
- Is this about DPI/DPMM conversion issues?
- Is this about integration patterns (React/TypeScript)?
- Is this about error handling or rate limits?

### Step 2: Load Relevant Resources

#### For Setup/Getting Started Questions

**User asks: "How do I convert ZPL to PNG?"**

**Load**:
1. `categories/getting-started.md` (quickstart, basic usage)

**Context**: ~100 lines (97% reduction from full docs)

---

#### For Endpoint-Specific Questions

**User asks: "What's the format for the image-to-ZPL endpoint?"**

**Load**:
1. `categories/api-endpoints.md` (all 4 endpoints with examples)

**Context**: ~150 lines (95% reduction)

---

#### For Parameter Questions

**User asks: "What Accept headers are available?"**

**Load**:
1. `categories/parameters.md` (complete parameter reference)

**Context**: ~150 lines (95% reduction)

---

#### For DPI/DPMM Conversion Issues

**User asks: "I'm getting HTTP 400 errors with dpmm"**

**Load**:
1. `patterns/dpi-conversion.md` (CRITICAL conversion pattern)
2. IF still unclear: `patterns/error-handling.md`

**Context**: ~120-200 lines (94% reduction)

---

#### For GET vs POST Questions

**User asks: "Should I use GET or POST?"**

**Load**:
1. `patterns/get-vs-post.md` (complete decision tree + examples)

**Context**: ~120 lines (96% reduction)

---

#### For Error Handling

**User asks: "I'm getting rate limited / HTTP 429 errors"**

**Load**:
1. `patterns/error-handling.md` (all errors, fixes, retry strategies)

**Context**: ~120 lines (96% reduction)

---

#### For React/TypeScript Integration

**User asks: "How do I implement ZPL preview in React?"**

**Load**:
1. `patterns/integration.md` (React hooks, modal components, caching)
2. IF workflow needed: `WORKFLOWS/ZPL_PREVIEW_WORKFLOW.md`

**Context**: ~200-300 lines (90% reduction)

---

#### For Advanced Features

**User asks: "How do I create multi-label PDF sheets?"**

**Load**:
1. `categories/advanced-features.md` (PDF layouts, rotation, linting, data extraction)

**Context**: ~150 lines (95% reduction)

---

### Step 3: Provide Answer with Context

When answering:

1. **Direct Answer First**: Provide the immediate answer
2. **Code Example**: Show TypeScript/JavaScript or curl implementation
3. **Category Reference**: Note which category/pattern file was consulted
4. **Additional Resources**: Offer to load more details if needed

---

## Usage Examples

### Example 1: Getting Started Question

**User**: "How do I convert ZPL to PNG?"

**Your Response**:
```markdown
To convert ZPL to PNG, use a POST request to the Labelary API.

Let me load the getting started guide for you...
[Load categories/getting-started.md]

**Basic Example:**
\```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --data "^xa^cfa,50^fo100,100^fdHello World^fs^xz" > label.png
\```

**TypeScript/React:**
\```typescript
const dpmm = Math.round(203 / 25.4); // 8
const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/4x6/0/`;

const response = await fetch(apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: zplCode,
});

const blob = await response.blob();
const imageUrl = URL.createObjectURL(blob);
\```

**Category Reference**: categories/getting-started.md

Would you like to see more advanced features or integration patterns?
```

---

### Example 2: DPI Conversion Error

**User**: "I'm getting HTTP 400 error: Invalid printer density"

**Your Response**:
```markdown
This error occurs when you use DPI instead of DPMM in the URL.

[Load patterns/dpi-conversion.md]

**The Problem:**
Labelary uses DPMM (dots per millimeter), NOT DPI!

**Conversion Formula:**
\```javascript
const dpmm = Math.round(dpi / 25.4);

// Common conversions:
// 203 DPI → 8 dpmm
// 300 DPI → 12 dpmm
// 600 DPI → 24 dpmm
\```

**Valid DPMM values:** `6dpmm`, `8dpmm`, `12dpmm`, `24dpmm`

**❌ WRONG:**
\```typescript
const apiUrl = `http://api.labelary.com/v1/printers/203dpmm/...`;
\```

**✅ CORRECT:**
\```typescript
const dpmm = Math.round(203 / 25.4); // 8
const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/...`;
\```

**Pattern Reference**: patterns/dpi-conversion.md

This should fix your HTTP 400 error!
```

---

### Example 3: Integration Question

**User**: "How do I implement ZPL preview modal in React?"

**Your Response**:
```markdown
Use a custom hook with useEffect to fetch the preview.

[Load patterns/integration.md]

**React Hook Pattern:**
\```typescript
const useLabelaryPreview = ({ zplCode, widthInches, heightInches, dpi }) => {
    const [imageUrl, setImageUrl] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!zplCode) return;

        const fetchPreview = async () => {
            setLoading(true);
            const dpmm = Math.round(dpi / 25.4);
            const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${widthInches}x${heightInches}/0/`;

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: zplCode,
            });

            const blob = await response.blob();
            setImageUrl(URL.createObjectURL(blob));
            setLoading(false);
        };

        fetchPreview();

        return () => {
            if (imageUrl) URL.revokeObjectURL(imageUrl);
        };
    }, [zplCode, widthInches, heightInches, dpi]);

    return { imageUrl, loading };
};
\```

**Pattern Reference**: patterns/integration.md

Would you like to see the complete modal component or workflow guide?
```

---

### Example 4: Rate Limit Error

**User**: "Getting HTTP 429 Too Many Requests errors"

**Your Response**:
```markdown
You're exceeding the free tier rate limit (3 requests/second).

[Load patterns/error-handling.md]

**Free Tier Limits:**
- 3 requests per second
- 5,000 requests per day

**Solution - Implement Throttling:**
\```typescript
class LabelaryClient {
    private readonly DELAY_MS = 350; // 3 req/sec

    async fetchWithThrottle(zpl: string) {
        await new Promise(resolve => setTimeout(resolve, this.DELAY_MS));
        return fetch(apiUrl, { method: 'POST', body: zpl });
    }
}
\```

**Solution - Exponential Backoff:**
\```typescript
async function fetchWithRetry(url, options, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        const response = await fetch(url, options);

        if (response.status === 429) {
            const delay = Math.pow(2, i) * 1000;
            await new Promise(resolve => setTimeout(resolve, delay));
            continue;
        }

        return response;
    }
}
\```

**Pattern Reference**: patterns/error-handling.md

This will prevent rate limit errors!
```

---

## Quick Reference: Critical Patterns

### DPI to DPMM Conversion (MOST IMPORTANT!)

**Labelary uses DPMM, NOT DPI!**

```javascript
// Always convert
const dpmm = Math.round(dpi / 25.4);

// Valid values: 6, 8, 12, 24
// Most common: 8 (203 DPI), 12 (300 DPI)
```

**See:** `patterns/dpi-conversion.md`

---

### GET vs POST

**Use POST for production (ALWAYS):**

```typescript
// ✅ RECOMMENDED
const response = await fetch(apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: zplCode,
});
```

**See:** `patterns/get-vs-post.md`

---

### Cleanup Object URLs

**Always revoke to prevent memory leaks:**

```typescript
useEffect(() => {
    // ... fetch logic

    return () => {
        if (imageUrl) {
            URL.revokeObjectURL(imageUrl);
        }
    };
}, [zplCode]);
```

**See:** `patterns/integration.md`

---

### Rate Limiting

**Free tier: 3 req/sec, 5,000 req/day**

```typescript
// Add delay between requests
await new Promise(resolve => setTimeout(resolve, 350));
```

**See:** `patterns/error-handling.md`

---

### Output Formats

Control with `Accept` header:

```typescript
headers: {
    'Accept': 'image/png',        // PNG (default)
    'Accept': 'application/pdf',  // PDF
    'Accept': 'application/json', // Data extraction
}
```

**See:** `categories/parameters.md`

---

## Common Workflows

### When to Use Each Resource

**categories/getting-started.md** - Use when you need to:
- Set up Labelary for the first time
- Understand basic ZPL to PNG/PDF conversion
- Get quick start code examples

**categories/api-endpoints.md** - Use when you need to:
- Know the exact endpoint URL format
- Understand request/response formats
- See examples for all 4 endpoints

**categories/parameters.md** - Use when you need to:
- Complete list of URL parameters
- All available HTTP headers
- Advanced configuration options

**categories/advanced-features.md** - Use when you need to:
- Multi-label PDF sheets
- Label rotation
- ZPL linting
- Data extraction (JSON output)

**patterns/dpi-conversion.md** - Use when you need to:
- Fix HTTP 400 "Invalid DPMM" errors
- Understand DPI to DPMM conversion
- Validate DPMM values

**patterns/get-vs-post.md** - Use when you need to:
- Decide between GET or POST
- Understand size limits
- Learn security considerations

**patterns/error-handling.md** - Use when you need to:
- Fix HTTP errors (400, 413, 429, 500)
- Implement rate limiting
- Handle network errors

**patterns/integration.md** - Use when you need to:
- React/TypeScript integration
- Custom hooks
- Modal components
- Caching strategies

---

## Your Mission

Help users successfully integrate Labelary ZPL rendering API by:

1. **Loading ONLY relevant resources** (progressive disclosure)
2. **Checking DPI/DPMM conversion FIRST** (most common error!)
3. **Providing task-based guidance** (use category files appropriately)
4. **Explaining patterns clearly** (reference pattern files)
5. **Generating correct code** (TypeScript/JavaScript/curl)
6. **Debugging integration issues** (error handling, rate limits)
7. **Offering additional resources** (can always load more details)

**You have complete knowledge of the Labelary API via modular, focused files. Use progressive disclosure to provide fast, relevant answers!**

---

## Expected Context Reduction

| Query Type | Before | After | Reduction |
|------------|--------|-------|-----------|
| Getting started | 488 lines | ~100 lines | 79% |
| Endpoint details | 488 lines | ~150 lines | 69% |
| DPI conversion | 488 lines | ~120 lines | 75% |
| Integration patterns | 488 lines | ~120 lines | 75% |
| Error handling | 488 lines | ~120 lines | 75% |
| **Average** | **488 lines** | **~120 lines** | **~75%** |

---

## Version Information

- **API Version:** v1
- **Free Tier:** 3 req/sec, 5,000 req/day
- **Premium Plans:** Available for higher limits
- **Official Docs:** http://labelary.com/service.html

---

**Pro Tip:** When users have HTTP 400 errors, ALWAYS check DPI to DPMM conversion first (`patterns/dpi-conversion.md`) - this is the #1 most common error!
