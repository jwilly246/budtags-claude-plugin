# Labelary API - Code Examples

Real-world implementation examples from the **BudTags** project, demonstrating best practices for integrating the Labelary API in React/TypeScript applications.

---

## Table of Contents

1. [Complete React Component](#complete-react-component-labelarypreviewmodal)
2. [TypeScript Type Definitions](#typescript-type-definitions)
3. [Core API Integration Function](#core-api-integration-function)
4. [DPI to DPMM Conversion](#dpi-to-dpmm-conversion)
5. [Error Handling](#error-handling)
6. [Image Display with Rulers](#image-display-with-rulers)
7. [Download Functionality](#download-functionality)
8. [Memory Management](#memory-management)
9. [Usage Example](#usage-example)
10. [Best Practices Summary](#best-practices-summary)

---

## Complete React Component: LabelaryPreviewModal

This is the **actual production component** from BudTags that displays live ZPL previews using the Labelary API.

**File:** `resources/js/Components/LabelDesigner/LabelaryPreviewModal.tsx`

```typescript
import React, { useState, useEffect, useRef } from 'react';
import Modal from '../Modal';
import Button from '../Button';
import { toast } from 'react-toastify';
import useModalState from '../../Hooks/useModalState';

interface LabelaryPreviewModalProps {
    show: boolean;
    onClose: () => void;
    zplCode: string;
    widthInches: number;
    heightInches: number;
    dpi: number;
}

const LabelaryPreviewModal: React.FC<LabelaryPreviewModalProps> = ({
    show,
    onClose,
    zplCode,
    widthInches,
    heightInches,
    dpi,
}) => {
    const { cancelButtonRef } = useModalState(show);
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [imageDimensions, setImageDimensions] = useState<{ width: number; height: number } | null>(null);
    const imageRef = useRef<HTMLImageElement>(null);

    // Fetch new preview when modal opens or ZPL changes
    useEffect(() => {
        if (show && zplCode) {
            fetchLabelaryImage();
        }

        return () => {
            // Cleanup: revoke object URL when modal closes
            if (imageUrl) {
                URL.revokeObjectURL(imageUrl);
            }
        };
    }, [show, zplCode]);

    const fetchLabelaryImage = async () => {
        setIsLoading(true);
        setError(null);
        setImageDimensions(null); // Reset dimensions when fetching new image

        try {
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
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch preview from Labelary';
            setError(errorMessage);
            toast.error('Failed to generate ZPL preview');
        } finally {
            setIsLoading(false);
        }
    };

    const handleDownload = () => {
        if (!imageUrl) return;

        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = `label-preview-${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        toast.success('Preview image downloaded');
    };

    const handleImageLoad = () => {
        if (imageRef.current) {
            setImageDimensions({
                width: imageRef.current.naturalWidth,
                height: imageRef.current.naturalHeight
            });
        }
    };

    return (
        <Modal
            show={show}
            onClose={onClose}
            title="ZPL Preview (Labelary)"
            draggable={true}
            width="w-[650px]"
            maxHeight="max-h-[85vh]"
        >
            {/* Info Banner */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4 text-sm text-blue-800">
                <div className="flex items-start gap-2">
                    <span className="text-lg">ℹ️</span>
                    <div>
                        <p className="font-semibold mb-1">True ZPL Preview</p>
                        <p className="text-xs">
                            Rendered at {dpi} DPI ({Math.round(dpi / 25.4)} dpmm) • {widthInches}" × {heightInches}"
                        </p>
                        <p className="text-xs mt-1 text-blue-600">
                            This is exactly how your label will print on a Zebra printer.
                        </p>
                    </div>
                </div>
            </div>

            {/* Download Control */}
            <div className="flex items-center justify-end mb-4">
                <Button secondary onClick={handleDownload} disabled={!imageUrl || isLoading}>
                    📥 Download PNG
                </Button>
            </div>

            {/* Preview Area */}
            <div className="border border-gray-300 rounded-lg bg-gray-50 overflow-auto" style={{ maxHeight: '50vh' }}>
                {isLoading && (
                    <div className="flex items-center justify-center py-20">
                        <div className="text-center">
                            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                            <p className="text-gray-600 text-sm">Rendering ZPL preview...</p>
                            <p className="text-gray-400 text-xs mt-1">Powered by Labelary</p>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="flex items-center justify-center py-20">
                        <div className="text-center">
                            <span className="text-4xl mb-4 block">⚠️</span>
                            <p className="text-red-600 font-semibold mb-2">Preview Failed</p>
                            <p className="text-gray-600 text-sm">{error}</p>
                            <Button secondary onClick={fetchLabelaryImage} className="mt-4">
                                Retry
                            </Button>
                        </div>
                    </div>
                )}

                {imageUrl && !isLoading && !error && (
                    <div className="flex items-center justify-center p-8">
                        {/* Container with rulers */}
                        <div className="relative inline-block">
                            {/* Rulers (only show after image loads and we have dimensions) */}
                            {imageDimensions && (
                                <>
                                    {/* X-axis ruler (top) */}
                                    <div
                                        className="absolute bg-gray-200 border-b border-gray-400"
                                        style={{
                                            width: `${imageDimensions.width}px`,
                                            height: '20px',
                                            top: '-20px',
                                            left: '20px'
                                        }}
                                    >
                                        {Array.from({ length: Math.ceil(imageDimensions.width / 50) + 1 }, (_, i) => {
                                            const x = i * 50;
                                            if (x > imageDimensions.width) return null;
                                            return (
                                                <div
                                                    key={i}
                                                    className="absolute text-xs text-gray-600 font-mono"
                                                    style={{
                                                        left: `${x}px`,
                                                        top: '2px',
                                                        transform: 'translateX(-50%)'
                                                    }}
                                                >
                                                    {x}
                                                </div>
                                            );
                                        })}
                                    </div>

                                    {/* Y-axis ruler (left) */}
                                    <div
                                        className="absolute bg-gray-200 border-r border-gray-400"
                                        style={{
                                            width: '20px',
                                            height: `${imageDimensions.height}px`,
                                            top: '0px',
                                            left: '0px'
                                        }}
                                    >
                                        {Array.from({ length: Math.ceil(imageDimensions.height / 50) + 1 }, (_, i) => {
                                            const y = i * 50;
                                            if (y > imageDimensions.height) return null;
                                            return (
                                                <div
                                                    key={i}
                                                    className="absolute text-xs text-gray-600 font-mono"
                                                    style={{
                                                        top: `${y}px`,
                                                        left: '2px',
                                                        transform: 'translateY(-50%) rotate(-90deg)',
                                                        transformOrigin: 'left center'
                                                    }}
                                                >
                                                    {y}
                                                </div>
                                            );
                                        })}
                                    </div>
                                </>
                            )}

                            {/* Label image - display at natural size without forcing dimensions */}
                            <img
                                ref={imageRef}
                                src={imageUrl}
                                alt="Label Preview"
                                onLoad={handleImageLoad}
                                style={{
                                    imageRendering: 'pixelated',
                                    marginLeft: '20px',
                                    display: 'block'
                                }}
                                className="border border-gray-300 shadow-lg"
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* ZPL Code Section (Collapsible) */}
            <details className="mt-4">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900 select-none">
                    View ZPL Code
                </summary>
                <div className="mt-2 bg-gray-900 text-green-400 p-4 rounded-lg text-xs font-mono overflow-x-auto max-h-60 overflow-y-auto">
                    <pre>{zplCode}</pre>
                </div>
            </details>

            {/* Footer */}
            <div className="flex justify-end gap-2 mt-4 pt-4 border-t">
                <Button secondary onClick={onClose} _ref={cancelButtonRef}>
                    Close
                </Button>
            </div>
        </Modal>
    );
};

export default LabelaryPreviewModal;
```

---

## TypeScript Type Definitions

### Props Interface

```typescript
interface LabelaryPreviewModalProps {
    show: boolean;              // Modal visibility
    onClose: () => void;        // Close handler
    zplCode: string;            // ZPL code to render
    widthInches: number;        // Label width in inches
    heightInches: number;       // Label height in inches
    dpi: number;                // Printer DPI (will convert to dpmm)
}
```

### Image Dimensions State

```typescript
interface ImageDimensions {
    width: number;   // Natural image width in pixels
    height: number;  // Natural image height in pixels
}
```

### API Request Type

```typescript
interface LabelaryApiRequest {
    method: 'POST';
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded';
    };
    body: string; // ZPL code
}
```

---

## Core API Integration Function

### Fetch Labelary Image

```typescript
const fetchLabelaryImage = async () => {
    setIsLoading(true);
    setError(null);
    setImageDimensions(null);

    try {
        // 1. Convert DPI to dpmm
        const dpmm = Math.round(dpi / 25.4);

        // 2. Build API URL
        const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${widthInches}x${heightInches}/0/`;

        // 3. Make POST request
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: zplCode,
        });

        // 4. Check response
        if (!response.ok) {
            throw new Error(`Labelary API returned ${response.status}: ${response.statusText}`);
        }

        // 5. Convert to blob and create object URL
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setImageUrl(url);
    } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch preview from Labelary';
        setError(errorMessage);
        toast.error('Failed to generate ZPL preview');
    } finally {
        setIsLoading(false);
    }
};
```

### Key Points:

1. **POST Method**: Uses POST (not GET) for production reliability
2. **Content-Type**: `application/x-www-form-urlencoded` for raw ZPL
3. **Error Handling**: Comprehensive try/catch with user feedback
4. **Blob Handling**: Converts response to blob, creates object URL
5. **State Management**: Updates loading/error states appropriately

---

## DPI to DPMM Conversion

### Simple Conversion

```typescript
// Convert DPI to dpmm (dots per millimeter)
const dpmm = Math.round(dpi / 25.4);
```

### With Validation

```typescript
function getDpmm(dpi: number): number {
    const dpmm = Math.round(dpi / 25.4);
    const validDpmm = [6, 8, 12, 24];

    if (!validDpmm.includes(dpmm)) {
        throw new Error(`Invalid dpmm: ${dpmm}. Printer DPI ${dpi} converts to unsupported dpmm. Valid: 6, 8, 12, 24`);
    }

    return dpmm;
}

// Usage
try {
    const dpmm = getDpmm(203); // 8
    const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${w}x${h}/0/`;
} catch (error) {
    console.error('DPI conversion failed:', error);
}
```

### Common DPI Values

```typescript
const DPI_TO_DPMM_MAP: Record<number, number> = {
    152: 6,   // 6 dpmm
    203: 8,   // 8 dpmm (most common)
    300: 12,  // 12 dpmm
    600: 24,  // 24 dpmm
};

function getDpmmFromMap(dpi: number): number {
    const dpmm = DPI_TO_DPMM_MAP[dpi];
    if (!dpmm) {
        throw new Error(`Unsupported DPI: ${dpi}. Supported: 152, 203, 300, 600`);
    }
    return dpmm;
}
```

---

## Error Handling

### Error States

```typescript
const [error, setError] = useState<string | null>(null);
const [isLoading, setIsLoading] = useState<boolean>(false);
```

### Comprehensive Error Handling

```typescript
try {
    const response = await fetch(apiUrl, options);

    // Handle HTTP errors
    if (!response.ok) {
        // Rate limit exceeded
        if (response.status === 429) {
            throw new Error('Rate limit exceeded. Please wait before retrying.');
        }
        // Payload too large
        if (response.status === 413) {
            throw new Error('ZPL code too large. Maximum 1 MB allowed.');
        }
        // Bad request (invalid parameters)
        if (response.status === 400) {
            throw new Error('Invalid request. Check label dimensions and ZPL code.');
        }
        // Generic error
        throw new Error(`Labelary API returned ${response.status}: ${response.statusText}`);
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    setImageUrl(url);
    setError(null); // Clear any previous errors
} catch (err: unknown) {
    // Type-safe error handling
    const errorMessage = err instanceof Error
        ? err.message
        : 'Failed to fetch preview from Labelary';

    setError(errorMessage);
    toast.error('Failed to generate ZPL preview');
    console.error('Labelary API error:', err);
} finally {
    setIsLoading(false);
}
```

### Error Display UI

```tsx
{error && (
    <div className="flex items-center justify-center py-20">
        <div className="text-center">
            <span className="text-4xl mb-4 block">⚠️</span>
            <p className="text-red-600 font-semibold mb-2">Preview Failed</p>
            <p className="text-gray-600 text-sm">{error}</p>
            <Button secondary onClick={fetchLabelaryImage} className="mt-4">
                Retry
            </Button>
        </div>
    </div>
)}
```

---

## Image Display with Rulers

### Ruler Component Pattern

```tsx
{imageDimensions && (
    <>
        {/* X-axis ruler (top) */}
        <div
            className="absolute bg-gray-200 border-b border-gray-400"
            style={{
                width: `${imageDimensions.width}px`,
                height: '20px',
                top: '-20px',
                left: '20px'
            }}
        >
            {Array.from({ length: Math.ceil(imageDimensions.width / 50) + 1 }, (_, i) => {
                const x = i * 50;
                if (x > imageDimensions.width) return null;
                return (
                    <div
                        key={i}
                        className="absolute text-xs text-gray-600 font-mono"
                        style={{
                            left: `${x}px`,
                            top: '2px',
                            transform: 'translateX(-50%)'
                        }}
                    >
                        {x}
                    </div>
                );
            })}
        </div>

        {/* Y-axis ruler (left) */}
        <div
            className="absolute bg-gray-200 border-r border-gray-400"
            style={{
                width: '20px',
                height: `${imageDimensions.height}px`,
                top: '0px',
                left: '0px'
            }}
        >
            {Array.from({ length: Math.ceil(imageDimensions.height / 50) + 1 }, (_, i) => {
                const y = i * 50;
                if (y > imageDimensions.height) return null;
                return (
                    <div
                        key={i}
                        className="absolute text-xs text-gray-600 font-mono"
                        style={{
                            top: `${y}px`,
                            left: '2px',
                            transform: 'translateY(-50%) rotate(-90deg)',
                            transformOrigin: 'left center'
                        }}
                    >
                        {y}
                    </div>
                );
            })}
        </div>
    </>
)}
```

### Image with Pixelated Rendering

```tsx
<img
    ref={imageRef}
    src={imageUrl}
    alt="Label Preview"
    onLoad={handleImageLoad}
    style={{
        imageRendering: 'pixelated',  // Crisp pixel rendering
        marginLeft: '20px',
        display: 'block'
    }}
    className="border border-gray-300 shadow-lg"
/>
```

### Get Natural Image Dimensions

```typescript
const handleImageLoad = () => {
    if (imageRef.current) {
        setImageDimensions({
            width: imageRef.current.naturalWidth,
            height: imageRef.current.naturalHeight
        });
    }
};
```

---

## Download Functionality

```typescript
const handleDownload = () => {
    if (!imageUrl) return;

    // Create temporary link element
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `label-preview-${Date.now()}.png`;

    // Trigger download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // User feedback
    toast.success('Preview image downloaded');
};
```

### Download Button

```tsx
<Button
    secondary
    onClick={handleDownload}
    disabled={!imageUrl || isLoading}
>
    📥 Download PNG
</Button>
```

---

## Memory Management

### Cleanup Object URLs

```typescript
useEffect(() => {
    if (show && zplCode) {
        fetchLabelaryImage();
    }

    // Cleanup function: revoke object URL when modal closes
    return () => {
        if (imageUrl) {
            URL.revokeObjectURL(imageUrl);
        }
    };
}, [show, zplCode]);
```

### Why This Matters:

- `URL.createObjectURL()` creates a DOMString pointing to blob in memory
- Without cleanup, memory leaks occur
- Always revoke when component unmounts or URL changes

---

## Usage Example

### In Parent Component

```typescript
import LabelaryPreviewModal from './LabelaryPreviewModal';

function CanvasLabelDesigner() {
    const [showPreview, setShowPreview] = useState(false);
    const [zplCode, setZplCode] = useState('');

    const handlePreview = () => {
        // Generate ZPL code
        const generatedZpl = generateZplFromElements(elements);
        setZplCode(generatedZpl);
        setShowPreview(true);
    };

    return (
        <>
            <Button onClick={handlePreview}>
                Preview ZPL
            </Button>

            <LabelaryPreviewModal
                show={showPreview}
                onClose={() => setShowPreview(false)}
                zplCode={zplCode}
                widthInches={4}
                heightInches={6}
                dpi={203}
            />
        </>
    );
}
```

---

## Best Practices Summary

### ✅ DO:

1. **Use POST method** for production (not GET)
2. **Convert DPI to dpmm** before API call
3. **Handle errors gracefully** with user feedback
4. **Clean up object URLs** in useEffect cleanup
5. **Show loading states** during API calls
6. **Validate inputs** before making requests
7. **Use TypeScript** for type safety
8. **Implement retry logic** for transient errors

### ❌ DON'T:

1. **Don't use GET** for large ZPL or production
2. **Don't hardcode DPI** - always convert to dpmm
3. **Don't ignore errors** - users need feedback
4. **Don't leak memory** - always revoke object URLs
5. **Don't skip loading states** - provide UI feedback
6. **Don't use `any` type** - be explicit with types

---

## Additional Integration Patterns

### Rate Limiting

```typescript
class RateLimiter {
    private queue: number[] = [];
    private maxPerSecond: number;

    constructor(maxPerSecond: number) {
        this.maxPerSecond = maxPerSecond;
    }

    async execute<T>(fn: () => Promise<T>): Promise<T> {
        // Remove timestamps older than 1 second
        const now = Date.now();
        this.queue = this.queue.filter(t => now - t < 1000);

        // Wait if at limit
        while (this.queue.length >= this.maxPerSecond) {
            await new Promise(resolve => setTimeout(resolve, 100));
            this.queue = this.queue.filter(t => Date.now() - t < 1000);
        }

        this.queue.push(Date.now());
        return fn();
    }
}

// Usage
const limiter = new RateLimiter(2); // 2 req/sec (safety margin for free tier)
await limiter.execute(() => fetch(apiUrl, options));
```

### Caching Previews

```typescript
const previewCache = new Map<string, string>();

async function fetchLabelaryImageCached(zplCode: string, dpi: number, width: number, height: number) {
    const cacheKey = `${zplCode}-${dpi}-${width}-${height}`;

    if (previewCache.has(cacheKey)) {
        return previewCache.get(cacheKey)!;
    }

    const dpmm = Math.round(dpi / 25.4);
    const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${width}x${height}/0/`;

    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: zplCode,
    });

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    previewCache.set(cacheKey, url);
    return url;
}
```

---

**See Also:**
- `API_REFERENCE.md` - Complete API documentation
- `INTEGRATION_GUIDE.md` - Step-by-step integration walkthrough
- `WORKFLOWS/ZPL_PREVIEW_WORKFLOW.md` - Detailed preview workflow
