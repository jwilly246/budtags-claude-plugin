# Complete Parameter Reference

All URL parameters, headers, and configuration options for Labelary API.

---

## URL Parameters

### Path Parameters

#### `{dpmm}` - Print Density (REQUIRED)

Dots per millimeter. Controls label resolution.

**Valid values:**
- `6dpmm` - 152 DPI
- `8dpmm` - 203 DPI (most common)
- `12dpmm` - 300 DPI
- `24dpmm` - 600 DPI

**Conversion formula:**
```javascript
const dpmm = Math.round(dpi / 25.4);
```

**Most Zebra printers use:**
- 203 DPI (8dpmm) - Standard resolution
- 300 DPI (12dpmm) - High resolution

⚠️ **Invalid dpmm values return HTTP 400 error!**

See `patterns/dpi-conversion.md` for complete conversion guide.

---

#### `{width}` and `{height}` - Label Dimensions (REQUIRED)

Label size in inches.

**Format:** `{width}x{height}` (e.g., `4x6`, `2x1`, `4.5x6.5`)

**Valid values:**
- Any numeric value (integer or decimal)
- Maximum: 15 inches
- Minimum: Depends on content

**Common label sizes:**
- `4x6` - Standard shipping label
- `4x3` - Half-sheet label
- `2x1` - Small product label
- `3x2` - Medium product label

**Examples:**
```
/v1/printers/8dpmm/labels/4x6/0/        # 4" wide, 6" tall
/v1/printers/8dpmm/labels/2.25x1.25/0/  # 2.25" wide, 1.25" tall
```

⚠️ **Width and height must match ZPL label size!**

---

#### `{index}` - Label Index (OPTIONAL for PDF)

Zero-based index of label to render (for ZPL with multiple labels).

**Valid values:**
- `0` - First label (index 0)
- `1` - Second label (index 1)
- etc.
- Omit - Render all labels (PDF only)

**Examples:**
```
/v1/printers/8dpmm/labels/4x6/0/   # Render first label
/v1/printers/8dpmm/labels/4x6/1/   # Render second label
/v1/printers/8dpmm/labels/4x6/     # Render ALL labels (PDF only)
```

**Single label ZPL:** Always use index `0`
**Multi-label PDF:** Omit index to render all labels on one PDF sheet

---

#### `{zpl}` - ZPL Code (GET only)

ZPL code to render (GET requests only).

**Encoding:**
- Must be URL-encoded
- Use `--data-urlencode` with curl
- Encode `#` as `%23`

**Example:**
```bash
curl --get http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data-urlencode "^xa^cfa,50^fo100,100^fdHello World^fs^xz"
```

⚠️ **For POST requests, put ZPL in request body, not URL!**

---

## HTTP Headers (Request)

### Accept Header - Output Format

Controls the output format returned by the API.

| Accept Header | Output Format | File Extension | Use Case |
|---------------|---------------|----------------|----------|
| `image/png` | PNG image | `.png` | Web preview, display (default) |
| `application/pdf` | PDF document | `.pdf` | Multi-label sheets, printing |
| `application/json` | JSON data | `.json` | Data extraction, validation |
| `application/ipl` | Intermec IPL | `.ipl` | Intermec printers |
| `application/epl` | Eltron EPL | `.epl` | Eltron printers |
| `application/dpl` | Datamax DPL | `.dpl` | Datamax printers |
| `application/sbpl` | SATO SBPL | `.sbpl` | SATO printers |
| `application/pcl5` | HP PCL 5 | `.pcl` | HP PCL 5 printers |
| `application/pcl6` | HP PCL 6 | `.pcl` | HP PCL 6 printers |

**Default:** `image/png` (if no Accept header specified)

**Examples:**
```bash
# PNG (default)
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data "^xa^fdHello^fs^xz" > label.png

# PDF
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Accept: application/pdf" \
  --data "^xa^fdHello^fs^xz" > label.pdf

# JSON (data extraction)
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Accept: application/json" \
  --data "^xa^ft50,50^a0,50^fdHello^fs^xz"
```

---

### Content-Type Header - Request Body Format

**Required for POST requests with ZPL in body:**

```
Content-Type: application/x-www-form-urlencoded
```

**For multipart uploads (images/fonts):**

```
Content-Type: multipart/form-data
```

---

### Advanced Headers (PDF and PNG Configuration)

#### X-Rotation - Rotate Label

Rotate the rendered label.

**Valid values:** `0`, `90`, `180`, `270` (degrees)

**Example:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "X-Rotation: 90" \
  --data "^xa^fdHello^fs^xz" > label.png
```

---

#### X-Quality - PNG Quality

Control PNG output quality.

**Valid values:**
- `Grayscale` - Grayscale output (smaller file size)
- `Bitonal` - Black and white only (smallest file size)

**Default:** Full color

**Example:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "X-Quality: Grayscale" \
  --data "^xa^fdHello^fs^xz" > label.png
```

---

#### X-Linter - Enable ZPL Linting

Enable linting to detect ZPL errors and warnings.

**Valid values:**
- `On` - Enable linting (warnings in response header)
- `Off` - Disable linting (default)

**Example:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "X-Linter: On" \
  --data "^xa^gb1,1,3^fs^xz" -v
```

**Response includes:**
```
X-Warnings: 303|1|^GB|2|Value 1 is less than minimum value 3; used 3 instead
```

**Warning format:** `byte_index|byte_size|command|parameter|message`

See `categories/advanced-features.md` for complete linting details.

---

### PDF-Only Headers

These headers only apply when `Accept: application/pdf` is used.

#### X-Page-Size - PDF Page Size

**Valid values:**
- `Letter` - 8.5" x 11" (default)
- `Legal` - 8.5" x 14"
- `A4` - 210mm x 297mm
- `A5` - 148mm x 210mm
- `A6` - 105mm x 148mm

**Example:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/ \
  --header "Accept: application/pdf" \
  --header "X-Page-Size: A4" \
  --data "@labels.zpl" > sheet.pdf
```

---

#### X-Page-Orientation - PDF Page Orientation

**Valid values:**
- `Portrait` (default)
- `Landscape`

---

#### X-Page-Layout - Labels Per Page

Specify grid layout for multi-label PDFs.

**Format:** `{columns}x{rows}` (e.g., `2x3`, `3x4`)

**Examples:**
- `2x3` - 2 columns, 3 rows (6 labels per page)
- `3x4` - 3 columns, 4 rows (12 labels per page)
- `1x10` - 1 column, 10 rows (single-column sheet)

**Example:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x3/ \
  --header "Accept: application/pdf" \
  --header "X-Page-Layout: 2x3" \
  --data "@labels.zpl" > sheet.pdf
```

---

#### X-Page-Align - Horizontal Alignment

**Valid values:**
- `Left` (default)
- `Right`
- `Center`
- `Justify`

---

#### X-Page-Vertical-Align - Vertical Alignment

**Valid values:**
- `Top` (default)
- `Bottom`
- `Center`
- `Justify`

---

#### X-Label-Border - PDF Label Borders

Add borders around labels on PDF sheets.

**Valid values:**
- `None` - No borders (default)
- `Dashed` - Dashed borders
- `Solid` - Solid borders

**Example:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x3/ \
  --header "Accept: application/pdf" \
  --header "X-Page-Layout: 2x3" \
  --header "X-Label-Border: Dashed" \
  --data "@labels.zpl" > sheet.pdf
```

---

## HTTP Headers (Response)

### X-Total-Count - Label Count

Number of labels generated from the ZPL code.

**Example:**
```
X-Total-Count: 5
```

**Use case:** Know how many labels were in the ZPL

---

### X-Warnings - Linting Warnings

Pipe-delimited list of linting warnings (only if `X-Linter: On`).

**Format:** `byte_index|byte_size|command|parameter|message`

**Example:**
```
X-Warnings: 303|1|^GB|2|Value 1 is less than minimum value 3; used 3 instead|450|2|^FO|1|Value exceeds label boundary
```

**Multiple warnings:** Separated by pipe character `|`

---

## Request Body Limits

### Free Tier Limits

- **Max request body size:** 1 MB
- **Max labels per request:** 50
- **Max label dimensions:** 15" x 15"

### Rate Limits

- **3 requests per second**
- **5,000 requests per day**

**Exceeded limits:**
- HTTP 429 (Too Many Requests) - rate limit
- HTTP 413 (Payload Too Large) - size limit

See `patterns/error-handling.md` for handling rate limits.

---

## Parameter Combinations

### Common Combinations

**Basic PNG preview:**
```
POST /v1/printers/8dpmm/labels/4x6/0/
Content-Type: application/x-www-form-urlencoded
```

**PDF with layout:**
```
POST /v1/printers/8dpmm/labels/4x3/
Accept: application/pdf
X-Page-Size: Letter
X-Page-Layout: 2x3
X-Label-Border: Dashed
```

**Data extraction:**
```
POST /v1/printers/8dpmm/labels/4x6/0/
Accept: application/json
```

**Linting enabled:**
```
POST /v1/printers/8dpmm/labels/4x6/0/
X-Linter: On
```

**Rotated grayscale:**
```
POST /v1/printers/8dpmm/labels/4x6/0/
X-Rotation: 90
X-Quality: Grayscale
```

---

## Official Documentation

- **Getting Started:** `categories/getting-started.md`
- **API Endpoints:** `categories/api-endpoints.md`
- **Advanced Features:** `categories/advanced-features.md`
- **DPI Conversion:** `patterns/dpi-conversion.md`
- **Error Handling:** `patterns/error-handling.md`
