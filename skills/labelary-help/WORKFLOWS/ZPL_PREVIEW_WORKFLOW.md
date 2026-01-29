# ZPL Preview Workflow

Step-by-step guide to implementing live ZPL preview functionality in your application.

---

## When to Use This Workflow

Use this workflow when you need to:
- Show users a visual preview of ZPL code before printing
- Implement a "Preview" button in a label designer
- Validate that ZPL code renders correctly
- Debug ZPL layout issues
- Display ZPL previews in web applications (React, Angular, Vue, etc.)

---

## Prerequisites

- ✅ ZPL code to preview
- ✅ Label dimensions (width × height in inches)
- ✅ Printer DPI (typically 203 or 300)
- ✅ Basic React/TypeScript knowledge (for web implementation)

---

## Quick Start (Command Line)

### 1. Test with curl

```bash
# Replace with your ZPL code
ZPL='^xa^cfa,50^fo100,100^fdHello World^fs^xz'

# Generate preview (203 DPI, 4"×6" label)
curl --request POST \
  http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --data "$ZPL" > preview.png

# View preview
open preview.png  # macOS
start preview.png # Windows
```

### 2. Verify Output

- ✅ PNG image created
- ✅ Dimensions: ~812 × 1218 pixels (4" × 6" at 203 DPI)
- ✅ Content matches ZPL layout

---

## Web Implementation (React/TypeScript)

### Step 1: Create API Service

**File:** `src/services/LabelaryService.ts`

```typescript
export interface LabelaryPreviewRequest {
    zplCode: string;
    widthInches: number;
    heightInches: number;
    dpi: number;
}

export class LabelaryService {
    static async getPreview(request: LabelaryPreviewRequest): Promise<string> {
        // Convert DPI to dpmm
        const dpmm = Math.round(request.dpi / 25.4);

        // Build API URL
        const url = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${request.widthInches}x${request.heightInches}/0/`;

        // Make API call
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: request.zplCode,
        });

        if (!response.ok) {
            throw new Error(`Preview failed: ${response.status} ${response.statusText}`);
        }

        // Convert to object URL
        const blob = await response.blob();
        return URL.createObjectURL(blob);
    }
}
```

---

### Step 2: Create Preview Component

**File:** `src/components/ZplPreview.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { LabelaryService } from '../services/LabelaryService';

interface ZplPreviewProps {
    zplCode: string;
    widthInches: number;
    heightInches: number;
    dpi: number;
}

export const ZplPreview: React.FC<ZplPreviewProps> = ({
    zplCode,
    widthInches,
    heightInches,
    dpi,
}) => {
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!zplCode) return;

        const loadPreview = async () => {
            setIsLoading(true);
            setError(null);

            try {
                const url = await LabelaryService.getPreview({
                    zplCode,
                    widthInches,
                    heightInches,
                    dpi,
                });
                setImageUrl(url);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load preview');
            } finally {
                setIsLoading(false);
            }
        };

        loadPreview();

        // Cleanup: revoke object URL when component unmounts
        return () => {
            if (imageUrl) {
                URL.revokeObjectURL(imageUrl);
            }
        };
    }, [zplCode, widthInches, heightInches, dpi]);

    if (isLoading) {
        return (
            <div className="preview-loading">
                <div className="spinner" />
                <p>Generating preview...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="preview-error">
                <p>⚠️ Preview Failed</p>
                <p>{error}</p>
            </div>
        );
    }

    if (!imageUrl) {
        return <div>No preview available</div>;
    }

    return (
        <div className="preview-container">
            <img
                src={imageUrl}
                alt="ZPL Preview"
                style={{
                    imageRendering: 'pixelated',
                    border: '1px solid #ccc',
                }}
            />
        </div>
    );
};
```

---

### Step 3: Add to Your Application

**File:** `src/App.tsx` or your label designer component

```typescript
import React, { useState } from 'react';
import { ZplPreview } from './components/ZplPreview';

function LabelDesigner() {
    const [zplCode, setZplCode] = useState(`^xa
^cfa,50
^fo100,100^fdSample Label^fs
^fo100,200^fdProduct: ABC123^fs
^xz`);

    const [showPreview, setShowPreview] = useState(false);

    return (
        <div>
            <h1>Label Designer</h1>

            {/* ZPL Editor */}
            <textarea
                value={zplCode}
                onChange={(e) => setZplCode(e.target.value)}
                rows={10}
                cols={50}
            />

            {/* Preview Button */}
            <button onClick={() => setShowPreview(!showPreview)}>
                {showPreview ? 'Hide Preview' : 'Show Preview'}
            </button>

            {/* Preview Panel */}
            {showPreview && (
                <ZplPreview
                    zplCode={zplCode}
                    widthInches={4}
                    heightInches={6}
                    dpi={203}
                />
            )}
        </div>
    );
}

export default LabelDesigner;
```

---

## Modal Implementation (BudTags Pattern)

For a production-quality modal with download functionality, rulers, and collapsible ZPL code view:

**See:** `CODE_EXAMPLES.md` for the complete `LabelaryPreviewModal` component from BudTags.

**Key Features:**
- ✅ Draggable modal
- ✅ Loading spinner with branded messaging
- ✅ Error handling with retry button
- ✅ Download PNG functionality
- ✅ Coordinate rulers (X/Y axis)
- ✅ Collapsible ZPL code viewer
- ✅ DPI/dpmm conversion display
- ✅ Memory cleanup (URL.revokeObjectURL)

---

## Advanced Features

### 1. Add Download Functionality

```typescript
const handleDownload = () => {
    if (!imageUrl) return;

    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `label-preview-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

// Add download button
<button onClick={handleDownload} disabled={!imageUrl}>
    Download PNG
</button>
```

### 2. Add Coordinate Rulers

```typescript
const [imageDimensions, setImageDimensions] = useState<{ width: number; height: number } | null>(null);
const imageRef = useRef<HTMLImageElement>(null);

const handleImageLoad = () => {
    if (imageRef.current) {
        setImageDimensions({
            width: imageRef.current.naturalWidth,
            height: imageRef.current.naturalHeight,
        });
    }
};

// Render rulers
{imageDimensions && (
    <div className="rulers">
        {/* X-axis ruler */}
        {Array.from({ length: Math.ceil(imageDimensions.width / 50) + 1 }, (_, i) => {
            const x = i * 50;
            return <div key={i} style={{ position: 'absolute', left: `${x}px` }}>{x}</div>;
        })}
    </div>
)}

<img
    ref={imageRef}
    src={imageUrl}
    onLoad={handleImageLoad}
    alt="Label Preview"
/>
```

**See:** `CODE_EXAMPLES.md` for complete ruler implementation

### 3. Add Rotation Support

```typescript
const [rotation, setRotation] = useState<0 | 90 | 180 | 270>(0);

// Modify API call
const response = await fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Rotation': rotation.toString(),
    },
    body: zplCode,
});

// Add rotation controls
<select value={rotation} onChange={(e) => setRotation(Number(e.target.value) as any)}>
    <option value={0}>0°</option>
    <option value={90}>90°</option>
    <option value={180}>180°</option>
    <option value={270}>270°</option>
</select>
```

### 4. Add Quality Toggle (PNG only)

```typescript
const [quality, setQuality] = useState<'Grayscale' | 'Bitonal'>('Grayscale');

// Modify API call
const response = await fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Quality': quality,
    },
    body: zplCode,
});

// Add quality toggle
<select value={quality} onChange={(e) => setQuality(e.target.value as any)}>
    <option value="Grayscale">Grayscale (preview)</option>
    <option value="Bitonal">Bitonal (printer-quality)</option>
</select>
```

### 5. Enable ZPL Linting

```typescript
const [warnings, setWarnings] = useState<string[]>([]);

// Modify API call
const response = await fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Linter': 'On',
    },
    body: zplCode,
});

// Parse warnings from response header
const warningsHeader = response.headers.get('X-Warnings');
if (warningsHeader) {
    const parsedWarnings = warningsHeader.split('|').reduce((acc, _, i, arr) => {
        if (i % 5 === 4) { // Every 5th element is a warning message
            acc.push(arr[i]);
        }
        return acc;
    }, [] as string[]);
    setWarnings(parsedWarnings);
}

// Display warnings
{warnings.length > 0 && (
    <div className="warnings">
        <h3>⚠️ ZPL Warnings:</h3>
        <ul>
            {warnings.map((w, i) => <li key={i}>{w}</li>)}
        </ul>
    </div>
)}
```

---

## Error Handling

### Common Errors

#### Rate Limit Exceeded (429)

```typescript
if (response.status === 429) {
    setError('Rate limit exceeded (3 req/sec). Please wait before retrying.');

    // Implement automatic retry with delay
    setTimeout(() => {
        loadPreview();
    }, 1000);
}
```

#### Invalid ZPL (400)

```typescript
if (response.status === 400) {
    setError('Invalid ZPL code or label dimensions. Please check your input.');
}
```

#### ZPL Too Large (413)

```typescript
const sizeInMB = new Blob([zplCode]).size / (1024 * 1024);
if (sizeInMB > 1) {
    setError(`ZPL too large: ${sizeInMB.toFixed(2)} MB (max 1 MB)`);
    return;
}
```

---

## Testing

### Unit Tests

```typescript
import { LabelaryService } from './LabelaryService';

describe('LabelaryService', () => {
    it('generates preview for valid ZPL', async () => {
        const url = await LabelaryService.getPreview({
            zplCode: '^xa^cfa,50^fo100,100^fdTest^fs^xz',
            widthInches: 4,
            heightInches: 6,
            dpi: 203,
        });

        expect(url).toMatch(/^blob:/);
    });

    it('throws error for invalid DPI', async () => {
        await expect(
            LabelaryService.getPreview({
                zplCode: '^xa^xz',
                widthInches: 4,
                heightInches: 6,
                dpi: 999, // Invalid
            })
        ).rejects.toThrow();
    });
});
```

---

## Performance Optimization

### 1. Debounce Preview Updates

```typescript
import { useEffect, useState } from 'react';

function useDebounce<T>(value: T, delay: number): T {
    const [debouncedValue, setDebouncedValue] = useState<T>(value);

    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);

        return () => {
            clearTimeout(handler);
        };
    }, [value, delay]);

    return debouncedValue;
}

// Usage
const debouncedZpl = useDebounce(zplCode, 500); // 500ms delay

<ZplPreview zplCode={debouncedZpl} {...config} />
```

### 2. Cache Previews

```typescript
const previewCache = new Map<string, string>();

function getCacheKey(request: LabelaryPreviewRequest): string {
    return `${request.zplCode}-${request.dpi}-${request.widthInches}x${request.heightInches}`;
}

static async getPreview(request: LabelaryPreviewRequest): Promise<string> {
    const cacheKey = getCacheKey(request);

    if (previewCache.has(cacheKey)) {
        return previewCache.get(cacheKey)!;
    }

    const url = await this.fetchPreview(request);
    previewCache.set(cacheKey, url);
    return url;
}
```

---

## Next Steps

- **Need complete modal example?** See `CODE_EXAMPLES.md` for BudTags implementation
- **Need API details?** See `API_REFERENCE.md`
- **Need integration help?** See `INTEGRATION_GUIDE.md`
- **Need to convert images/fonts?** See other WORKFLOWS

---

**You're ready to implement live ZPL preview functionality!**
