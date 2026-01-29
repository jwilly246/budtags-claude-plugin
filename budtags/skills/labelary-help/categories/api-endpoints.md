# Labelary API Endpoints

Labelary provides 4 core REST API endpoints for ZPL rendering and conversion.

---

## 1. ZPL to Image/PDF (GET)

Convert ZPL code to various output formats via URL parameters.

### Endpoint

```
GET /v1/printers/{dpmm}/labels/{width}x{height}/{index}/{zpl}
```

### URL Parameters

- `{dpmm}` - Print density: `6dpmm`, `8dpmm`, `12dpmm`, `24dpmm`
- `{width}` - Label width in inches (e.g., `4`)
- `{height}` - Label height in inches (e.g., `6`)
- `{index}` - Label index (base 0), or omit for all labels (PDF only)
- `{zpl}` - ZPL code to render

### Examples

**PNG Output (default):**
```bash
curl --get http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data-urlencode "^xa^cfa,50^fo100,100^fdHello World^fs^xz" > label.png
```

**PDF Output:**
```bash
curl --get http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data-urlencode "^xa^fdHello^fs^xz" \
  --header "Accept: application/pdf" > label.pdf
```

**JSON Output (data extraction):**
```bash
curl --get http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data-urlencode "^xa^ft50,50^a0,50^fdHello^fs^xz" \
  --header "Accept: application/json"
```

### When to Use GET

✅ ZPL is small (<3,000 characters)
✅ No sensitive data in ZPL
✅ Simple testing/debugging
✅ No binary data embedded

❌ Production applications (use POST instead)

---

## 2. ZPL to Image/PDF (POST)

Convert ZPL code to various output formats via request body.

### Endpoint

```
POST /v1/printers/{dpmm}/labels/{width}x{height}/{index}
```

### URL Parameters

- `{dpmm}` - Print density: `6dpmm`, `8dpmm`, `12dpmm`, `24dpmm`
- `{width}` - Label width in inches
- `{height}` - Label height in inches
- `{index}` - Label index (base 0), or omit for all labels (PDF only)

### Request Body

ZPL code as raw text

### Headers

**Required:**
- `Content-Type: application/x-www-form-urlencoded`

**Optional (controls output format):**
- `Accept: image/png` (default)
- `Accept: application/pdf`
- `Accept: application/json`
- `Accept: application/ipl`
- `Accept: application/epl`
- `Accept: application/dpl`
- `Accept: application/sbpl`
- `Accept: application/pcl5`
- `Accept: application/pcl6`

### Examples

**PNG Output:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --data "^xa^cfa,50^fo100,100^fdHello World^fs^xz" > label.png
```

**PDF Output:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Accept: application/pdf" \
  --data "^xa^fdHello^fs^xz" > label.pdf
```

**TypeScript/React:**
```typescript
const response = await fetch(
    `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${width}x${height}/0/`,
    {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: zplCode,
    }
);

const blob = await response.blob();
const imageUrl = URL.createObjectURL(blob);
```

### When to Use POST

✅ Production applications (RECOMMENDED)
✅ Large ZPL code (>3,000 characters)
✅ Sensitive data in ZPL
✅ Embedded binary data
✅ Character encoding issues with GET

---

## 3. Image to ZPL Graphics

Convert raster images (PNG, JPG) to ZPL graphics code.

### Endpoint

```
POST /v1/graphics
```

### Request

**Content-Type:** `multipart/form-data`

**Form Field:** `file` - Image file to convert

### Response

**Default:** ZPL graphics code (^GF command)

**Other formats (via Accept header):**
- `application/json` - JSON with image data
- `application/epl` - EPL format
- `application/ipl` - IPL format
- `application/dpl` - DPL format
- `application/sbpl` - SBPL format
- `application/pcl5` - PCL 5 format
- `application/pcl6` - PCL 6 format

### Examples

**Convert to ZPL:**
```bash
curl --request POST http://api.labelary.com/v1/graphics \
  --form file=@logo.png > logo.zpl
```

**Convert to JSON:**
```bash
curl --request POST http://api.labelary.com/v1/graphics \
  --header "Accept: application/json" \
  --form file=@logo.png
```

**TypeScript/React:**
```typescript
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('http://api.labelary.com/v1/graphics', {
    method: 'POST',
    body: formData,
});

const zplGraphics = await response.text();
console.log(zplGraphics); // ^GFA,1234,...
```

### Use Cases

- Convert logos to ZPL for label printing
- Embed product images in labels
- Convert icons to ZPL graphics
- Generate ZPL from user-uploaded images

**See:** `WORKFLOWS/IMAGE_CONVERSION_WORKFLOW.md` for step-by-step guide

---

## 4. Font to ZPL

Convert TrueType fonts to ZPL font format with optional subsetting.

### Endpoint

```
POST /v1/fonts
```

### Request

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file` - TrueType font file (.ttf)
- `alias` (optional) - Single-letter font alias (e.g., `A`)
- `subset` (optional) - Characters to include (e.g., `0123456789`)

### Response

ZPL font download commands

### Examples

**Full Font:**
```bash
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@CustomFont.ttf > font.zpl
```

**Font with Alias:**
```bash
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@CustomFont.ttf \
  --form alias=C > font.zpl
```

**Subset Font (Numbers Only):**
```bash
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@CustomFont.ttf \
  --form alias=D \
  --form subset="0123456789" > font_numbers.zpl
```

**TypeScript/React:**
```typescript
const formData = new FormData();
formData.append('file', fontFile);
formData.append('alias', 'C');
formData.append('subset', '0123456789ABCDEF');

const response = await fetch('http://api.labelary.com/v1/fonts', {
    method: 'POST',
    body: formData,
});

const zplFont = await response.text();
// Use in ZPL: ^A@C,30,30,E:FONT.TTF^FDCustom Text^FS
```

### Use Cases

- Use custom branding fonts in labels
- Reduce ZPL file size with subsetting
- Support non-standard character sets
- Match brand typography

**See:** `WORKFLOWS/FONT_CONVERSION_WORKFLOW.md` for step-by-step guide

---

## Endpoint Summary

| Endpoint | Method | Input | Output | Use Case |
|----------|--------|-------|--------|----------|
| `/v1/printers/{dpmm}/labels/{width}x{height}/{index}/{zpl}` | GET | ZPL (URL) | PNG/PDF/JSON/etc | Quick testing |
| `/v1/printers/{dpmm}/labels/{width}x{height}/{index}` | POST | ZPL (body) | PNG/PDF/JSON/etc | Production rendering |
| `/v1/graphics` | POST | Image file | ZPL graphics | Image → ZPL |
| `/v1/fonts` | POST | TrueType font | ZPL font | Custom fonts |

---

## Response Headers

All endpoints may return:

- `X-Total-Count` - Number of labels generated
- `X-Warnings` - Linting warnings (pipe-delimited, if linting enabled)

**Example:**
```
X-Total-Count: 1
X-Warnings: 303|1|^GB|2|Value 1 is less than minimum value 3; used 3 instead
```

---

## Official Documentation

- **Getting Started:** `categories/getting-started.md`
- **Complete Parameters:** `categories/parameters.md`
- **Advanced Features:** `categories/advanced-features.md`
- **Error Handling:** `patterns/error-handling.md`
- **Integration Guide:** `INTEGRATION_GUIDE.md`
- **Code Examples:** `CODE_EXAMPLES.md`
