# Image to ZPL Conversion Workflow

Step-by-step guide to converting raster images (PNG, JPG, etc.) to ZPL graphics code for embedding in labels.

---

## When to Use This Workflow

Use this workflow when you need to:
- Embed logos in ZPL labels
- Convert product images to ZPL graphics
- Add raster graphics to Zebra labels
- Generate ZPL `^GF` (Graphics Field) commands from images
- Optimize images for printer memory constraints

---

## Prerequisites

- ✅ Image file (PNG, JPG, GIF, BMP)
- ✅ Image dimensions ≤ 2,000 × 2,000 pixels
- ✅ Image file size ≤ 200 KB
- ✅ Basic understanding of ZPL graphics commands

---

## Quick Start (Command Line)

### 1. Convert Image to ZPL

```bash
# Convert image.png to ZPL graphics code
curl --request POST http://api.labelary.com/v1/graphics \
  --form file=@image.png > image.zpl

# View generated ZPL
cat image.zpl
```

**Output Example:**
```zpl
^GFA,{total_bytes},{total_bytes},{bytes_per_row},{hex_data}
```

### 2. Embed in ZPL Label

```bash
# Create complete label with image
cat > label.zpl <<'EOF'
^XA
^FO100,100
$(cat image.zpl)
^FS
^XZ
EOF

# Preview the label
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data "@label.zpl" > label-with-image.png
```

---

## Step-by-Step Process

### Step 1: Prepare Your Image

#### Resize to Appropriate Dimensions

Images are rendered at printer resolution (203 DPI, 300 DPI, etc.).

**Calculate size in inches:**
```
Width in inches = Pixels / DPI
Height in inches = Pixels / DPI
```

**Example:**
- Image: 400 × 400 pixels
- Printer: 203 DPI
- Result: ~2" × 2" on label

**Resize with ImageMagick:**
```bash
# Resize to 400x400 pixels (2" x 2" at 203 DPI)
convert input.png -resize 400x400 output.png

# Convert to monochrome (recommended for smaller ZPL)
convert input.png -resize 400x400 -monochrome output.png
```

#### Optimize File Size

```bash
# Compress PNG
pngquant --quality=65-80 input.png -o output.png

# Reduce dimensions
convert input.png -resize 50% output.png

# Convert to monochrome (1-bit)
convert input.png -colorspace Gray -threshold 50% output.png
```

**Limits:**
- ✅ Max dimensions: 2,000 × 2,000 pixels
- ✅ Max file size: 200 KB

---

### Step 2: Convert Image to ZPL

#### Using curl (Recommended)

```bash
curl --request POST http://api.labelary.com/v1/graphics \
  --form file=@logo.png > logo.zpl
```

#### Using JavaScript/TypeScript

```typescript
async function convertImageToZpl(imageFile: File): Promise<string> {
    const formData = new FormData();
    formData.append('file', imageFile);

    const response = await fetch('http://api.labelary.com/v1/graphics', {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`Image conversion failed: ${response.status}`);
    }

    return response.text();
}

// Usage
const fileInput = document.querySelector('input[type="file"]');
const imageFile = fileInput.files[0];
const zplGraphics = await convertImageToZpl(imageFile);
console.log(zplGraphics);
```

#### Using Python

```python
import requests

def convert_image_to_zpl(image_path):
    url = 'http://api.labelary.com/v1/graphics'

    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f'Conversion failed: {response.status_code}')

# Usage
zpl_graphics = convert_image_to_zpl('logo.png')
print(zpl_graphics)
```

---

### Step 3: Embed in ZPL Label

#### Basic Embedding

```zpl
^XA

^FO100,100        ~< Position: X=100, Y=100
^GFA,{bytes},{bytes},{row_bytes},{hex_data}
^FS

^XZ
```

#### Example with Text and Image

```zpl
^XA

~< Company logo at top
^FO50,50
^GFA,1234,1234,20,00FF00FF...
^FS

~< Product name
^FO50,300
^CF0,60
^FDProduct Name^FS

~< Barcode
^FO50,400
^BY3
^BCN,100,Y,N,N
^FD123456^FS

^XZ
```

#### React Component Example

```typescript
interface ImageEmbedProps {
    imageFile: File;
    positionX: number;
    positionY: number;
}

async function generateZplWithImage({ imageFile, positionX, positionY }: ImageEmbedProps): Promise<string> {
    // Convert image to ZPL graphics
    const graphicsZpl = await convertImageToZpl(imageFile);

    // Embed in complete label
    const zpl = `^XA
^FO${positionX},${positionY}
${graphicsZpl}
^FS
^XZ`;

    return zpl;
}
```

---

## Advanced Features

### 1. Convert to Other Printer Languages

#### EPL (Eltron Programming Language)

```bash
curl --request POST http://api.labelary.com/v1/graphics \
  --form file=@logo.png \
  --header "Accept: application/epl" > logo.epl
```

#### IPL (Intermec Printer Language)

```bash
curl --request POST http://api.labelary.com/v1/graphics \
  --form file=@logo.png \
  --header "Accept: application/ipl" > logo.ipl
```

#### PCL (HP Printer Control Language)

```bash
curl --request POST http://api.labelary.com/v1/graphics \
  --form file=@logo.png \
  --header "Accept: application/pcl5" > logo.pcl
```

### 2. Get JSON Metadata

```bash
curl --request POST http://api.labelary.com/v1/graphics \
  --form file=@logo.png \
  --header "Accept: application/json"
```

**Response:**
```json
{
  "format": "zpl",
  "command": "^GFA",
  "dimensions": {
    "width": 400,
    "height": 400
  },
  "bytes": 1234
}
```

---

## Optimization Strategies

### 1. Reduce Image Dimensions

Smaller images = smaller ZPL = faster printing

```bash
# Calculate required size
# For 1" image at 203 DPI: 203 pixels
# For 2" image at 203 DPI: 406 pixels

convert logo.png -resize 406x406 logo-optimized.png
```

### 2. Convert to Monochrome

ZPL printers are typically monochrome. Converting beforehand reduces file size.

```bash
# Threshold-based conversion
convert logo.png -threshold 50% -monochrome logo-mono.png

# Dithering for better quality
convert logo.png -colorspace Gray -ordered-dither o8x8 logo-dithered.png
```

### 3. Use Stored Graphics

For repeated images, store once in printer memory and recall:

```zpl
~< Download graphics to printer memory
^XA
^DFE:LOGO.GRF
^GFA,1234,1234,20,00FF00FF...
^FS
^XZ

~< Use stored graphics in labels
^XA
^FO100,100
^XGE:LOGO.GRF
^FS
^XZ
```

### 4. Compression

Some printers support compressed graphics (`^GFA` with compression):

```zpl
~< Uncompressed
^GFA,1234,1234,20,00FF00FF...

~< Compressed (if printer supports)
^GFC,1234,1234,20,{compressed_hex_data}
```

---

## Web Application Integration

### React Component for Image Upload

```typescript
import React, { useState } from 'react';

interface ImageToZplConverterProps {
    onZplGenerated: (zpl: string) => void;
}

export const ImageToZplConverter: React.FC<ImageToZplConverterProps> = ({ onZplGenerated }) => {
    const [isConverting, setIsConverting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        // Validate file size
        if (file.size > 200 * 1024) {
            setError('Image too large (max 200 KB)');
            return;
        }

        setIsConverting(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('http://api.labelary.com/v1/graphics', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Conversion failed: ${response.status}`);
            }

            const zpl = await response.text();
            onZplGenerated(zpl);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Conversion failed');
        } finally {
            setIsConverting(false);
        }
    };

    return (
        <div>
            <h3>Convert Image to ZPL</h3>
            <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                disabled={isConverting}
            />
            {isConverting && <p>Converting...</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
};
```

### Usage in Label Designer

```typescript
function LabelDesigner() {
    const [zplCode, setZplCode] = useState('');

    const handleImageConverted = (graphicsZpl: string) => {
        // Embed graphics at position (100, 100)
        const completeZpl = `^XA
^FO100,100
${graphicsZpl}
^FS
^XZ`;

        setZplCode(completeZpl);
    };

    return (
        <div>
            <ImageToZplConverter onZplGenerated={handleImageConverted} />
            <textarea value={zplCode} readOnly rows={10} cols={50} />
        </div>
    );
}
```

---

## Troubleshooting

### Error: Image Too Large

**Symptom:**
```
HTTP 400: Image dimensions exceed maximum
```

**Solution:**
```bash
# Check image dimensions
identify image.png

# Resize if needed
convert image.png -resize 2000x2000\> output.png
```

### Error: File Size Too Large

**Symptom:**
```
HTTP 400: Image file size exceeds maximum
```

**Solution:**
```bash
# Compress image
pngquant --quality=65-80 input.png -o output.png

# Or reduce dimensions
convert input.png -resize 50% output.png
```

### Poor Print Quality

**Problem:** Image looks pixelated or blurry when printed

**Solutions:**

1. **Increase resolution before conversion:**
```bash
convert logo.png -resize 200% -quality 100 logo-highres.png
curl --request POST http://api.labelary.com/v1/graphics \
  --form file=@logo-highres.png > logo.zpl
```

2. **Use monochrome conversion with dithering:**
```bash
convert logo.png -colorspace Gray -ordered-dither o8x8 logo-dithered.png
```

3. **Adjust contrast:**
```bash
convert logo.png -level 20%,80% logo-contrast.png
```

### ZPL Too Large for Printer

**Problem:** Printer memory error when printing label with image

**Solutions:**

1. **Reduce image size:**
```bash
convert logo.png -resize 50% logo-small.png
```

2. **Use stored graphics (download once, reuse many times):**
```zpl
~< Download to printer (do once)
^XA
^DFE:LOGO.GRF
{graphics_zpl}
^FS
^XZ

~< Recall in each label
^XA
^FO100,100^XGE:LOGO.GRF^FS
^XZ
```

3. **Use compression (if printer supports):**
Check printer documentation for `^GFC` support

---

## Best Practices

### ✅ DO:

1. **Optimize images before conversion** - Resize and compress to minimum necessary size
2. **Use monochrome images** - Most Zebra printers are monochrome
3. **Test with printer preview** - Always preview before batch printing
4. **Store repeated images** - Use printer memory for logos used on many labels
5. **Validate file size** - Check image is <200 KB before API call

### ❌ DON'T:

1. **Don't use huge images** - Resize to label size first
2. **Don't convert color images** - Convert to monochrome beforehand
3. **Don't embed multiple large images** - Use stored graphics instead
4. **Don't skip testing** - Always test print before production
5. **Don't ignore printer memory limits** - Some printers have limited RAM

---

## Example: Complete Workflow

```bash
#!/bin/bash

# 1. Prepare image
convert company-logo.png \
  -resize 400x400 \
  -colorspace Gray \
  -threshold 50% \
  logo-prepared.png

# 2. Convert to ZPL
curl --request POST http://api.labelary.com/v1/graphics \
  --form file=@logo-prepared.png > logo.zpl

# 3. Create label with logo and text
cat > product-label.zpl <<'EOF'
^XA

~< Company logo
^FO50,50
$(cat logo.zpl)
^FS

~< Product info
^FO50,500
^CF0,40
^FDProduct: ABC-123^FS

^FO50,560
^CF0,30
^FDExpires: 2025-12-31^FS

~< Barcode
^FO50,620
^BY3
^BCN,100,Y,N,N
^FDABC123^FS

^XZ
EOF

# 4. Preview the complete label
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data "@product-label.zpl" > preview.png

# 5. View preview
open preview.png
```

---

## Next Steps

- **Need to convert fonts?** See `FONT_CONVERSION_WORKFLOW.md`
- **Need to preview ZPL?** See `ZPL_PREVIEW_WORKFLOW.md`
- **Need API details?** See `API_REFERENCE.md`
- **Need code examples?** See `CODE_EXAMPLES.md`

---

**You're ready to embed images in ZPL labels!**
