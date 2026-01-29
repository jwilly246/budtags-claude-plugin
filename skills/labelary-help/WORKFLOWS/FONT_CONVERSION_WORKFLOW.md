# TrueType Font to ZPL Conversion Workflow

Step-by-step guide to converting TrueType fonts to ZPL format for use with custom fonts on Zebra printers.

---

## When to Use This Workflow

Use this workflow when you need to:
- Use custom TrueType fonts in ZPL labels
- Brand labels with company-specific fonts
- Support non-Latin characters (Chinese, Arabic, etc.)
- Create labels with specialized fonts (OCR-A, OCR-B, barcode fonts)
- Reduce font file size with subsetting

---

## Prerequisites

- ✅ TrueType font file (.ttf)
- ✅ Font file size ≤ 200 KB
- ✅ Font license allows embedding/modification
- ✅ Basic understanding of ZPL font commands

---

## Important: Font Licensing

**CRITICAL:** Always check font license before conversion!

**Allowed:**
- ✅ Fonts with commercial use rights
- ✅ Open-source fonts (OFL, Apache, etc.)
- ✅ Fonts you created
- ✅ Fonts explicitly allowing embedding

**Not Allowed:**
- ❌ Fonts prohibiting modification
- ❌ Fonts prohibiting embedding
- ❌ Pirated fonts
- ❌ Fonts without clear license

**Popular Free Fonts:**
- Google Fonts (OFL license)
- Adobe Source fonts (OFL license)
- Liberation fonts (OFL license)

---

## Quick Start (Command Line)

### 1. Convert Font to ZPL

```bash
# Basic conversion
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@Montserrat-Bold.ttf > montserrat.zpl

# View generated ZPL
cat montserrat.zpl
```

**Output Example:**
```zpl
~DU{path},{name},{orientation},{size},{hex_data}
```

### 2. Download Font to Printer

```bash
# Send ZPL to printer (replace with your printer IP)
cat montserrat.zpl | lp -d zebra-printer

# Or save to file for later
cp montserrat.zpl /path/to/printer/fonts/
```

### 3. Use Custom Font in Labels

```zpl
^XA

~< Use custom font with shorthand 'Z'
^FO100,100
^AZ,50,50
^FDHello Custom Font^FS

^XZ
```

---

## Step-by-Step Process

### Step 1: Prepare Your Font File

#### Check Font License

```bash
# View font metadata
fc-query Montserrat-Bold.ttf | grep -E '(family|style|copyright|license)'
```

#### Check File Size

```bash
# Check file size (must be ≤ 200 KB)
ls -lh Montserrat-Bold.ttf

# If too large, subset the font (see Step 2)
```

#### Optimize Font (Optional)

Use font tools to reduce file size:

```bash
# Install fonttools (Python)
pip install fonttools

# Remove unnecessary tables
pyftsubset Montserrat-Bold.ttf \
  --output-file=Montserrat-Bold-Optimized.ttf \
  --layout-features=* \
  --glyph-names \
  --symbol-cmap \
  --legacy-cmap \
  --notdef-glyph \
  --notdef-outline \
  --recommended-glyphs \
  --name-IDs=* \
  --name-legacy \
  --name-languages=*
```

---

### Step 2: Convert Font to ZPL

#### Basic Conversion

```bash
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@MyFont.ttf > myfont.zpl
```

#### With Custom Shorthand Name

Assign a single-letter shorthand (I, K, M, O, W, X, Y, or Z):

```bash
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@MyFont.ttf \
  --form name=Z > myfont.zpl
```

**Valid shorthand letters:** I, K, M, O, W, X, Y, Z

**Usage in ZPL:**
```zpl
^AZ,50,50    ~< Use font 'Z', height 50, width 50
```

#### With Custom Printer Path

Specify where font is stored on printer (optional):

```bash
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@MyFont.ttf \
  --form path=R:MYFONT.TTF > myfont.zpl
```

**Path format:** `[REBA]:[A-Z0-9]{1,16}.TTF`
- **R:** RAM (default)
- **E:** EPROM (permanent)
- **B:** EPROM (alternative)
- **A:** RAM (alternative)

---

### Step 3: Subset Font (Optional but Recommended)

Subsetting reduces font size by including only specific characters.

#### Numeric-Only Font (Barcodes, IDs)

```bash
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@MyFont.ttf \
  --form name=Z \
  --form chars=0123456789 > numeric-font.zpl
```

#### Uppercase Letters Only

```bash
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@MyFont.ttf \
  --form name=Z \
  --form chars=ABCDEFGHIJKLMNOPQRSTUVWXYZ > uppercase-font.zpl
```

#### Alphanumeric + Common Punctuation

```bash
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@MyFont.ttf \
  --form name=Z \
  --form chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,-:()' > subset-font.zpl
```

#### Custom Character Set

```bash
# Include specific characters needed for your labels
CHARS="Product:SKUExpires0123456789-/"

curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@MyFont.ttf \
  --form name=Z \
  --form "chars=$CHARS" > custom-subset.zpl
```

**Benefits of Subsetting:**
- ✅ Reduced ZPL file size (can be 90% smaller!)
- ✅ Faster font download to printer
- ✅ Less printer memory usage
- ✅ Fits within 200 KB API limit

---

### Step 4: Download Font to Printer

#### Method 1: Direct Printer Connection

```bash
# Send to printer via lp
cat myfont.zpl | lp -d zebra-printer

# Or via raw TCP (port 9100)
cat myfont.zpl | nc printer-ip 9100
```

#### Method 2: Via Zebra Setup Utilities

1. Open Zebra Setup Utilities
2. Select printer
3. "Send File" → Select `myfont.zpl`
4. Font downloads to printer

#### Method 3: Store in Printer Memory

```zpl
~< Download font to RAM (temporary)
^XA
^DFR:MYFONT.TTF
{font_data_from_api}
^FS
^XZ

~< Download font to EPROM (permanent)
^XA
^DFE:MYFONT.TTF
{font_data_from_api}
^FS
^XZ
```

---

### Step 5: Use Custom Font in Labels

#### Using Shorthand Name

```zpl
^XA

~< Text with custom font 'Z', size 50
^FO100,100
^AZ,50,50
^FDCustom Font Text^FS

^XZ
```

#### Using Printer Path

```zpl
^XA

~< Load font from printer storage
^CWZ,R:MYFONT.TTF

~< Use the font
^FO100,100
^AZ,50,50
^FDCustom Font Text^FS

^XZ
```

#### With Variable Data

```zpl
^XA

~< Product name with custom font
^FO100,100
^AZ,40,40
^FN1^FS

~< Product SKU with custom font
^FO100,200
^AZ,30,30
^FN2^FS

^XZ

~< Variable data
^FN1^FDProduct Name^FS
^FN2^FDSKU-12345^FS
```

---

## Web Application Integration

### React Component for Font Upload

```typescript
import React, { useState } from 'react';

interface FontConverterProps {
    onFontConverted: (zpl: string, shorthandName: string) => void;
}

export const FontConverter: React.FC<FontConverterProps> = ({ onFontConverted }) => {
    const [isConverting, setIsConverting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [shorthandName, setShorthandName] = useState<string>('Z');
    const [subset, setSubset] = useState<string>('');

    const handleConvert = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        const fileInput = e.currentTarget.querySelector('input[type="file"]') as HTMLInputElement;
        const file = fileInput?.files?.[0];

        if (!file) {
            setError('Please select a font file');
            return;
        }

        if (file.size > 200 * 1024) {
            setError('Font file too large (max 200 KB)');
            return;
        }

        setIsConverting(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('name', shorthandName);

            if (subset) {
                formData.append('chars', subset);
            }

            const response = await fetch('http://api.labelary.com/v1/fonts', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Conversion failed: ${response.status}`);
            }

            const zpl = await response.text();
            onFontConverted(zpl, shorthandName);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Conversion failed');
        } finally {
            setIsConverting(false);
        }
    };

    return (
        <form onSubmit={handleConvert}>
            <h3>Convert TrueType Font to ZPL</h3>

            <div>
                <label>Font File (.ttf):</label>
                <input type="file" accept=".ttf" required />
            </div>

            <div>
                <label>Shorthand Name (I,K,M,O,W,X,Y,Z):</label>
                <select value={shorthandName} onChange={(e) => setShorthandName(e.target.value)}>
                    <option value="I">I</option>
                    <option value="K">K</option>
                    <option value="M">M</option>
                    <option value="O">O</option>
                    <option value="W">W</option>
                    <option value="X">X</option>
                    <option value="Y">Y</option>
                    <option value="Z">Z</option>
                </select>
            </div>

            <div>
                <label>Subset Characters (optional):</label>
                <input
                    type="text"
                    placeholder="e.g., 0123456789"
                    value={subset}
                    onChange={(e) => setSubset(e.target.value)}
                />
                <small>Leave empty for full font</small>
            </div>

            <button type="submit" disabled={isConverting}>
                {isConverting ? 'Converting...' : 'Convert Font'}
            </button>

            {error && <p style={{ color: 'red' }}>{error}</p>}
        </form>
    );
};
```

---

## Advanced Techniques

### 1. Unicode Support

For non-Latin characters:

```bash
# Convert font with Chinese characters
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@NotoSansCJK-Regular.ttf \
  --form name=Z \
  --form chars='产品名称SKU编号' > chinese-font.zpl
```

**Use in ZPL:**
```zpl
^XA
^CI28    ~< Enable UTF-8 encoding
^AZ,50,50
^FD产品名称^FS
^XZ
```

### 2. Multiple Custom Fonts

Use different shorthand names for different fonts:

```bash
# Font 1: Bold for headers
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@Montserrat-Bold.ttf \
  --form name=Y > bold-font.zpl

# Font 2: Regular for body text
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@Montserrat-Regular.ttf \
  --form name=Z > regular-font.zpl
```

**Use in label:**
```zpl
^XA

~< Header with bold font (Y)
^FO100,100
^AY,60,60
^FDProduct Name^FS

~< Body with regular font (Z)
^FO100,200
^AZ,30,30
^FDDescription text here^FS

^XZ
```

### 3. Font Rotation

```zpl
^XA

~< Normal orientation
^FO100,100^AZ,50,50^FDNormal^FS

~< 90° rotation
^FO200,100^AZ,50,50,R^FDRotated^FS

^XZ
```

---

## Troubleshooting

### Error: Font File Too Large

**Symptom:**
```
HTTP 400: Font file size exceeds maximum
```

**Solutions:**

1. **Subset the font:**
```bash
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@font.ttf \
  --form chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' > subset.zpl
```

2. **Use font optimization tools:**
```bash
pip install fonttools
pyftsubset font.ttf --output-file=optimized.ttf --unicodes=U+0020-007F
```

### Error: Font Subsetting Not Allowed

**Symptom:**
```
HTTP 400: Font does not allow subsetting
```

**Solution:**

Font license prohibits subsetting. Use full font or find alternative font.

### Font Not Displaying Correctly

**Problem:** Characters appear as boxes or missing

**Solutions:**

1. **Check character encoding:**
```zpl
^CI28    ~< Enable UTF-8
```

2. **Verify characters in subset:**
```bash
# Make sure all needed characters are included
--form chars='YourCompleteCharacterSet'
```

3. **Test with simple ASCII:**
```zpl
^XA
^AZ,50,50
^FDTEST 123^FS
^XZ
```

### Printer Memory Full

**Problem:** `Memory full` error when downloading font

**Solutions:**

1. **Delete unused fonts from printer:**
```zpl
~< Delete font from RAM
^XA
^DFR:*^FS
^XZ

~< Delete specific font
^XA
^DFR:OLDFONT.TTF^FS
^XZ
```

2. **Use smaller subset:**
```bash
--form chars='OnlyNeededChars'
```

3. **Store in EPROM instead of RAM** (if available)

---

## Best Practices

### ✅ DO:

1. **Always check font license** - Ensure commercial use is allowed
2. **Subset fonts** - Include only needed characters
3. **Test before production** - Print test labels with new font
4. **Document shorthand mappings** - Keep track of which letter = which font
5. **Use permanent storage** - Store in EPROM for fonts used frequently
6. **Validate file size** - Check font is <200 KB before API call

### ❌ DON'T:

1. **Don't use pirated fonts** - Only licensed fonts
2. **Don't skip subsetting** - Full fonts are usually too large
3. **Don't reuse shorthand names** - Each font needs unique letter
4. **Don't forget to download** - ZPL alone doesn't install font
5. **Don't ignore printer memory** - Monitor available space

---

## Example: Complete Workflow

```bash
#!/bin/bash

# 1. Download open-source font
wget https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf

# 2. Check file size
ls -lh Montserrat-Bold.ttf

# 3. Convert with subsetting (uppercase letters + digits only)
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@Montserrat-Bold.ttf \
  --form name=Z \
  --form chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .-:' > montserrat-subset.zpl

# 4. Create test label
cat > test-label.zpl <<'EOF'
^XA

~< Download font
$(cat montserrat-subset.zpl)

~< Use custom font
^FO100,100
^AZ,60,60
^FDPRODUCT NAME^FS

^FO100,200
^AZ,40,40
^FDSKU: ABC-123^FS

^XZ
EOF

# 5. Preview
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data "@test-label.zpl" > test-preview.png

# 6. View
open test-preview.png

# 7. Send to printer (if preview looks good)
# cat montserrat-subset.zpl | lp -d zebra-printer
```

---

## Next Steps

- **Need to convert images?** See `IMAGE_CONVERSION_WORKFLOW.md`
- **Need to preview ZPL?** See `ZPL_PREVIEW_WORKFLOW.md`
- **Need API details?** See `API_REFERENCE.md`
- **Need code examples?** See `CODE_EXAMPLES.md`

---

**You're ready to use custom fonts in ZPL labels!**
