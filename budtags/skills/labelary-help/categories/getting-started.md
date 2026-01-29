# Getting Started with Labelary API

## Overview

Labelary is a free online service that converts ZPL (Zebra Programming Language) code into images, PDFs, and other printer formats.

**Base URL:** `http://api.labelary.com/v1/`

**Authentication:** None required (free tier)

**No sign-up required** - Start using immediately

---

## Quick Start: Convert ZPL to PNG

### Using GET Request

```bash
curl --get http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data-urlencode "^xa^cfa,50^fo100,100^fdHello World^fs^xz" > label.png
```

**URL Structure:**
```
http://api.labelary.com/v1/printers/{dpmm}/labels/{width}x{height}/{index}/{zpl}
```

### Using POST Request (Recommended for Production)

```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data "^xa^cfa,50^fo100,100^fdHello World^fs^xz" \
  --header "Content-Type: application/x-www-form-urlencoded" > label.png
```

**Why POST?**
- Handles larger ZPL code (>3,000 characters)
- No URL encoding issues
- More secure for sensitive data
- Works with embedded binary data

---

## Basic React/TypeScript Implementation

Real example from BudTags project:

```typescript
const fetchLabelaryImage = async () => {
    // Convert DPI to dpmm (dots per millimeter)
    // 203 DPI = 8 dpmm, 300 DPI = 12 dpmm, 600 DPI = 24 dpmm
    const dpmm = Math.round(dpi / 25.4);

    // Labelary API endpoint
    const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${widthInches}x${heightInches}/0/`;

    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: zplCode,
    });

    if (!response.ok) {
        throw new Error(`Labelary API returned ${response.status}: ${response.statusText}`);
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    setImageUrl(url);
};
```

**Don't forget:** Always revoke object URLs when done:
```typescript
// Cleanup
return () => {
    if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
    }
};
```

---

## Output Formats

Control output format with the `Accept` header:

| Format | Accept Header | Use Case |
|--------|---------------|----------|
| PNG | `image/png` (default) | Web preview, display |
| PDF | `application/pdf` | Multi-label sheets, printing |
| JSON | `application/json` | Data extraction, validation |

**Example - Get PDF:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Accept: application/pdf" \
  --data "^xa^fdHello^fs^xz" > label.pdf
```

---

## Rate Limits (Free Tier)

- **3 requests per second**
- **5,000 requests per day**
- **50 labels per request**
- **1 MB request body size**
- **15" maximum label dimensions**

**Exceeded limits:**
- HTTP 429 (Too Many Requests) - rate limit exceeded
- HTTP 413 (Payload Too Large) - size limit exceeded

**Need more?** Premium plans available:
- **Plus**: $90/month - 6 req/sec, 20,000 req/day
- **Business**: $228/month - 10 req/sec, 40,000 req/day

---

## Next Steps

**For detailed API reference:**
- See `categories/api-endpoints.md` - All 4 endpoints
- See `categories/parameters.md` - Complete parameter reference

**For advanced features:**
- See `categories/advanced-features.md` - PDF layouts, rotation, linting

**For integration help:**
- See `patterns/integration.md` - React/TypeScript patterns
- See `WORKFLOWS/ZPL_PREVIEW_WORKFLOW.md` - Live preview modal

**For troubleshooting:**
- See `patterns/error-handling.md` - Common errors and fixes
- See `patterns/dpi-conversion.md` - DPI to DPMM conversion

---

## Critical: DPI to DPMM Conversion

**Labelary uses DPMM (dots per millimeter), NOT DPI!**

```javascript
// Always convert DPI to dpmm
const dpmm = Math.round(dpi / 25.4);

// Common conversions:
// 152 DPI = 6 dpmm
// 203 DPI = 8 dpmm
// 300 DPI = 12 dpmm
// 600 DPI = 24 dpmm
```

**Valid dpmm values:** `6dpmm`, `8dpmm`, `12dpmm`, `24dpmm`

**Invalid dpmm values will return HTTP 400 error!**

See `patterns/dpi-conversion.md` for complete details.
