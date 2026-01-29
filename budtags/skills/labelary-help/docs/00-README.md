<!-- Source: Labelary API Documentation -->
<!-- Section: Navigation and Quick Reference -->
<!-- Generated: 2025-11-02 19:43:59 -->

# Labelary API Documentation

Complete reference for the Labelary ZPL rendering API, organized into easily-digestible sections optimized for AI consumption and quick reference.

## What is Labelary?

Labelary is an online ZPL rendering engine that converts Zebra Programming Language (ZPL) code into various output formats (PNG, PDF, IPL, EPL, DPL, SBPL, PCL, JSON) via a simple RESTful API.

**Base API URL:** `http://api.labelary.com/v1/printers/{dpmm}/labels/{width}x{height}/{index}/`

## Documentation Structure

### Core Documentation

**[01-introduction-overview.md](01-introduction-overview.md)**
- What is Labelary and how it works
- GET vs POST request methods
- Available output formats (PNG, PDF, IPL, EPL, etc.)
- When to use each request method

**[02-parameters-reference.md](02-parameters-reference.md)**
- `dpmm` - Print density (6, 8, 12, 24 dots per millimeter)
- `width` x `height` - Label dimensions in inches
- `index` - Label selection (base 0)
- `zpl` - ZPL code to render

**[03-limits-and-pricing.md](03-limits-and-pricing.md)**
- Free tier limits (3 req/sec, 5,000 req/day)
- Premium plans (Plus, Business, On-Prem)
- Usage limits table
- Pricing information

### Code Examples

**[04-examples-web-scripting.md](04-examples-web-scripting.md)**
- Live API examples
- curl (GET, POST, multipart)
- Postman collection
- PowerShell scripts
- ColdFusion
- PHP
- Excel VBA

**[05-examples-programming-languages.md](05-examples-programming-languages.md)**
- Java (HttpClient API)
- Python (Requests library)
- Ruby
- Node.js
- D Language
- C# (.NET)
- VB.NET
- Rust (Reqwest)
- Go

### Advanced Usage

**[06-advanced-features.md](06-advanced-features.md)**
- Rotating labels (`X-Rotation` header)
- PDF with multiple labels per page
- PDF page size and orientation
- PDF page layout (columns x rows)
- PDF label borders
- Label counting (`X-Total-Count` response header)
- Print quality (Grayscale vs Bitonal)
- ZPL linting and error detection
- Data extraction (JSON output)

**[07-image-font-conversion.md](07-image-font-conversion.md)**
- Converting images to ZPL graphics
- Converting TrueType fonts to ZPL fonts
- Font subsetting
- API endpoints and examples

## Quick Start

### Basic PNG Conversion (GET)
```bash
curl --get http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data-urlencode "^xa^cfa,50^fo100,100^fdHello World^fs^xz" > label.png
```

### Basic PDF Conversion (POST)
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data "^xa^cfa,50^fo100,100^fdHello World^fs^xz" \
  --header "Accept: application/pdf" > label.pdf
```

### Convert Image to ZPL
```bash
curl --request POST http://api.labelary.com/v1/graphics \
  --form file=@image.png > image.zpl
```

## Common Use Cases

| Use Case | Start Here |
|----------|------------|
| First time using Labelary | [01-introduction-overview.md](01-introduction-overview.md) |
| Understanding API parameters | [02-parameters-reference.md](02-parameters-reference.md) |
| Checking rate limits | [03-limits-and-pricing.md](03-limits-and-pricing.md) |
| Finding code examples | [04-examples-web-scripting.md](04-examples-web-scripting.md) or [05-examples-programming-languages.md](05-examples-programming-languages.md) |
| Rotating labels, PDF layouts | [06-advanced-features.md](06-advanced-features.md) |
| Converting images/fonts | [07-image-font-conversion.md](07-image-font-conversion.md) |

## API Endpoint Summary

| Endpoint | Purpose |
|----------|---------|
| `GET /v1/printers/{dpmm}/labels/{width}x{height}/{index}/{zpl}` | Convert ZPL via URL |
| `POST /v1/printers/{dpmm}/labels/{width}x{height}/{index}` | Convert ZPL via request body |
| `POST /v1/graphics` | Convert image to ZPL graphics |
| `POST /v1/fonts` | Convert TTF font to ZPL font |

## Output Formats

Control output format with the `Accept` header:
- `image/png` (default)
- `application/pdf`
- `application/ipl`
- `application/epl`
- `application/dpl`
- `application/sbpl`
- `application/pcl5`
- `application/pcl6`
- `application/json` (data extraction)

## File Organization

- **Total files:** 8 (7 content + 1 README)
- **Average size:** ~150-200 lines per file
- **Optimal for:** AI context windows, quick reference, focused learning

## Integration with BudTags

This documentation is part of the BudTags project's ZPL label generation workflow:
- Used in `ZplTemplateService.php` for label preview
- Canvas Label Designer integration
- Template validation and testing

## Generated

Documentation split created: 2025-11-02 19:43:59

---
*Source: Labelary API Documentation (labelary.com)*
*Free API - No sign-up required*