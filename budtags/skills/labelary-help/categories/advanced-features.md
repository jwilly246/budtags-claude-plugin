# Advanced Features

Advanced Labelary API features including multi-label PDFs, rotation, data extraction, and ZPL linting.

---

## 1. Multi-Label PDF Sheets

Render multiple labels on a single PDF page with custom layouts.

### Single Label PDF

Include index in URL:

```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Accept: application/pdf" \
  --data "^xa^fdLabel 1^fs^xz" > label.pdf
```

### All Labels PDF

**Omit index** to render all labels from ZPL:

```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/ \
  --header "Accept: application/pdf" \
  --data "@labels.zpl" > all_labels.pdf
```

**Note:** Only works with `Accept: application/pdf`

### Custom Page Layout

Use `X-Page-Layout` header to specify grid:

```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x3/ \
  --header "Accept: application/pdf" \
  --header "X-Page-Size: Letter" \
  --header "X-Page-Layout: 2x3" \
  --header "X-Label-Border: Dashed" \
  --data "@labels.zpl" > sheet.pdf
```

**Creates:** 2x3 grid (6 labels per page) on Letter-size paper with dashed borders

### All PDF Headers

```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/ \
  --header "Accept: application/pdf" \
  --header "X-Page-Size: A4" \
  --header "X-Page-Orientation: Landscape" \
  --header "X-Page-Layout: 3x2" \
  --header "X-Page-Align: Center" \
  --header "X-Page-Vertical-Align: Center" \
  --header "X-Label-Border: Solid" \
  --data "@labels.zpl" > sheet.pdf
```

**Use cases:**
- Print sheets of labels (Avery-style)
- Create multi-label test sheets
- Generate label catalogs

---

## 2. Label Rotation

Rotate rendered labels 90°, 180°, or 270°.

### Rotation Header

```
X-Rotation: 0 | 90 | 180 | 270
```

### Examples

**90° clockwise:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "X-Rotation: 90" \
  --data "^xa^fdHello World^fs^xz" > rotated.png
```

**180° (upside down):**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "X-Rotation: 180" \
  --data "^xa^fdHello World^fs^xz" > rotated.png
```

**TypeScript:**
```typescript
const response = await fetch(apiUrl, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Rotation': '90',
    },
    body: zplCode,
});
```

**Use cases:**
- Adjust for printer orientation
- Preview different label orientations
- Match physical label rotation

---

## 3. Data Extraction (JSON Output)

Extract text and field data from ZPL labels for validation and testing.

### JSON Output

Use `Accept: application/json` header:

```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Accept: application/json" \
  --data "^xa^ft50,50^a0,50^fdHello^fs^ft50,100^a0,30^fdWorld^fs^xz"
```

### Response Format

```json
{
  "labels": [
    {
      "fields": [
        {
          "x": 50,
          "y": 50,
          "data": "Hello"
        },
        {
          "x": 50,
          "y": 100,
          "data": "World"
        }
      ]
    }
  ]
}
```

### Use Cases

**Validate label content:**
```typescript
const response = await fetch(apiUrl, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
    },
    body: zplCode,
});

const data = await response.json();
const fields = data.labels[0].fields;

// Verify expected text appears
const hasProductName = fields.some(f => f.data === 'Product Name');
assert(hasProductName, 'Product name missing from label');
```

**Extract barcode human-readable text:**
```typescript
const barcodeText = fields.find(f =>
    f.x === 100 && f.y === 200
)?.data;
```

**Test ZPL templates:**
```javascript
// Render template with test data
const zpl = renderTemplate({ name: 'Test Product' });

// Extract and validate
const json = await fetchLabelaryJSON(zpl);
assert(json.labels[0].fields[0].data === 'Test Product');
```

---

## 4. ZPL Linting

Detect ZPL errors and warnings during rendering.

### Enable Linting

Use `X-Linter: On` header:

```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "X-Linter: On" \
  --data "^xa^gb1,1,3^fs^xz" -v
```

### Response Header

Warnings returned in `X-Warnings` header:

```
X-Warnings: 303|1|^GB|2|Value 1 is less than minimum value 3; used 3 instead
```

### Warning Format

```
byte_index|byte_size|command|parameter|message
```

**Fields:**
- `byte_index` - Position in ZPL where issue occurs
- `byte_size` - Length of problematic command
- `command` - ZPL command with issue (e.g., `^GB`)
- `parameter` - Parameter number (1-indexed)
- `message` - Human-readable warning message

### Multiple Warnings

Pipe-delimited:

```
X-Warnings: 303|1|^GB|2|Value 1 is less than minimum value 3|450|2|^FO|1|Value exceeds label boundary
```

### TypeScript Example

```typescript
const response = await fetch(apiUrl, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Linter': 'On',
    },
    body: zplCode,
});

// Check for warnings
const warnings = response.headers.get('X-Warnings');
if (warnings) {
    const warningList = warnings.split('|').reduce((acc, val, idx) => {
        if (idx % 5 === 0) acc.push([]);
        acc[acc.length - 1].push(val);
        return acc;
    }, [] as string[][]);

    warningList.forEach(([byteIndex, byteSize, command, param, message]) => {
        console.warn(`ZPL Warning: ${command} parameter ${param}: ${message}`);
    });
}
```

### Common Warnings

**Value out of range:**
```
^GB|2|Value 1 is less than minimum value 3; used 3 instead
```

**Field outside label:**
```
^FO|1|Value exceeds label boundary
```

**Invalid parameter:**
```
^BC|3|Invalid barcode data
```

### Use Cases

- Debug ZPL template issues
- Validate user-generated ZPL
- Catch common ZPL mistakes
- Ensure label compatibility

---

## 5. PNG Quality Control

Control PNG output quality and file size.

### X-Quality Header

**Values:**
- (default) - Full color
- `Grayscale` - Grayscale (smaller file)
- `Bitonal` - Black/white only (smallest file)

### Examples

**Grayscale:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "X-Quality: Grayscale" \
  --data "^xa^fdHello^fs^xz" > label_gray.png
```

**Bitonal (black & white only):**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "X-Quality: Bitonal" \
  --data "^xa^fdHello^fs^xz" > label_bw.png
```

### File Size Comparison

Example 4x6 label:
- Full color: ~45 KB
- Grayscale: ~30 KB (-33%)
- Bitonal: ~8 KB (-82%)

**Use cases:**
- Reduce bandwidth for preview images
- Match printer capabilities (thermal printers are bitonal)
- Faster loading for web apps

---

## 6. Label Count

Get count of labels in ZPL via `X-Total-Count` response header.

### Response Header

```
X-Total-Count: 5
```

### Example

```typescript
const response = await fetch(apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: zplCode,
});

const labelCount = parseInt(response.headers.get('X-Total-Count') || '0');
console.log(`Generated ${labelCount} labels`);
```

**Use cases:**
- Validate expected label count
- Display count to user
- Batch processing feedback

---

## 7. Alternative Printer Formats

Convert ZPL to other printer languages.

### Supported Formats

| Format | Accept Header | Use Case |
|--------|---------------|----------|
| IPL | `application/ipl` | Intermec printers |
| EPL | `application/epl` | Eltron printers |
| DPL | `application/dpl` | Datamax printers |
| SBPL | `application/sbpl` | SATO printers |
| PCL5 | `application/pcl5` | HP PCL 5 printers |
| PCL6 | `application/pcl6` | HP PCL 6 printers |

### Example - Convert ZPL to EPL

```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Accept: application/epl" \
  --data "^xa^fdHello^fs^xz" > label.epl
```

**Use cases:**
- Support multiple printer brands
- Migrate between printer types
- Test cross-platform compatibility

---

## TypeScript Type Definitions

```typescript
interface LabelaryRequest {
    dpmm: 6 | 8 | 12 | 24;
    widthInches: number;
    heightInches: number;
    index?: number;
    zplCode: string;
    outputFormat?: 'png' | 'pdf' | 'json' | 'ipl' | 'epl' | 'dpl' | 'sbpl' | 'pcl5' | 'pcl6';
    rotation?: 0 | 90 | 180 | 270;
    quality?: 'Grayscale' | 'Bitonal';
    linting?: boolean;
    // PDF-only
    pageSize?: 'Letter' | 'Legal' | 'A4' | 'A5' | 'A6';
    pageOrientation?: 'Portrait' | 'Landscape';
    pageLayout?: string; // e.g., '2x3'
    pageAlign?: 'Left' | 'Right' | 'Center' | 'Justify';
    pageVerticalAlign?: 'Top' | 'Bottom' | 'Center' | 'Justify';
    labelBorder?: 'None' | 'Dashed' | 'Solid';
}

interface LabelaryJsonResponse {
    labels: Array<{
        fields: Array<{
            x: number;
            y: number;
            data: string;
        }>;
    }>;
}
```

---

## Official Documentation

- **Getting Started:** `categories/getting-started.md`
- **API Endpoints:** `categories/api-endpoints.md`
- **Parameters:** `categories/parameters.md`
- **Error Handling:** `patterns/error-handling.md`
- **Integration Patterns:** `patterns/integration.md`
- **Code Examples:** `CODE_EXAMPLES.md`
