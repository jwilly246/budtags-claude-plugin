# Integration Patterns

React/TypeScript integration patterns for Labelary API based on BudTags project.

---

## React Hook Pattern

### Basic Hook

```typescript
import { useState, useEffect } from 'react';

interface UseLabelaryPreviewProps {
    zplCode: string;
    widthInches: number;
    heightInches: number;
    dpi: number;
}

const useLabelaryPreview = ({ zplCode, widthInches, heightInches, dpi }: UseLabelaryPreviewProps) => {
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!zplCode) return;

        const fetchPreview = async () => {
            setLoading(true);
            setError(null);

            try {
                // Convert DPI to DPMM (CRITICAL!)
                const dpmm = Math.round(dpi / 25.4);

                // Validate DPMM
                if (![6, 8, 12, 24].includes(dpmm)) {
                    throw new Error(`Invalid DPMM: ${dpmm}. Must be 6, 8, 12, or 24.`);
                }

                const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${widthInches}x${heightInches}/0/`;

                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: zplCode,
                });

                if (!response.ok) {
                    throw new Error(`Labelary API error: ${response.status} ${response.statusText}`);
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                setImageUrl(url);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Unknown error');
            } finally {
                setLoading(false);
            }
        };

        fetchPreview();

        // Cleanup: Revoke object URL when unmounting
        return () => {
            if (imageUrl) {
                URL.revokeObjectURL(imageUrl);
            }
        };
    }, [zplCode, widthInches, heightInches, dpi]);

    return { imageUrl, loading, error };
};

export default useLabelaryPreview;
```

**Usage:**
```typescript
const MyComponent = () => {
    const { imageUrl, loading, error } = useLabelaryPreview({
        zplCode: '^xa^fdHello World^fs^xz',
        widthInches: 4,
        heightInches: 6,
        dpi: 203,
    });

    if (loading) return <div>Loading preview...</div>;
    if (error) return <div>Error: {error}</div>;

    return <img src={imageUrl || ''} alt="Label preview" />;
};
```

---

## Modal Preview Component (BudTags Pattern)

### Preview Modal with Rulers

Real example from BudTags project:

```typescript
import React, { useState, useEffect } from 'react';
import Modal from '@/Components/Modal';

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
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!show || !zplCode) return;

        const fetchLabelaryImage = async () => {
            setLoading(true);
            setError(null);

            try {
                // Convert DPI to dpmm
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
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to render label');
            } finally {
                setLoading(false);
            }
        };

        fetchLabelaryImage();

        // Cleanup
        return () => {
            if (imageUrl) {
                URL.revokeObjectURL(imageUrl);
            }
        };
    }, [show, zplCode, widthInches, heightInches, dpi]);

    return (
        <Modal show={show} onClose={onClose} size="3xl">
            <div className="p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">
                    ZPL Label Preview ({widthInches}" × {heightInches}" @ {dpi} DPI)
                </h2>

                {loading && (
                    <div className="flex justify-center items-center h-64">
                        <div className="text-gray-500">Rendering label preview...</div>
                    </div>
                )}

                {error && (
                    <div className="bg-red-50 border border-red-200 rounded p-4 text-red-700">
                        <strong>Error:</strong> {error}
                    </div>
                )}

                {imageUrl && !loading && (
                    <div className="flex justify-center">
                        <div className="border border-gray-300 rounded shadow-lg">
                            <img
                                src={imageUrl}
                                alt={`Label preview ${widthInches}x${heightInches}`}
                                className="max-w-full h-auto"
                            />
                        </div>
                    </div>
                )}

                <div className="mt-6 text-sm text-gray-600">
                    <p>Powered by Labelary API</p>
                    <p>Resolution: {Math.round(dpi / 25.4)} dpmm ({dpi} DPI)</p>
                </div>
            </div>
        </Modal>
    );
};

export default LabelaryPreviewModal;
```

**Usage:**
```typescript
const [showPreview, setShowPreview] = useState(false);
const [zplCode, setZplCode] = useState('');

<button onClick={() => setShowPreview(true)}>Preview Label</button>

<LabelaryPreviewModal
    show={showPreview}
    onClose={() => setShowPreview(false)}
    zplCode={zplCode}
    widthInches={4}
    heightInches={6}
    dpi={203}
/>
```

---

## Service Class Pattern (Laravel Backend)

### Labelary Service

```php
<?php

namespace App\Services\Api;

use Illuminate\Support\Facades\Http;

class LabelaryApi
{
    private const BASE_URL = 'http://api.labelary.com/v1';

    /**
     * Convert ZPL to PNG image
     *
     * @param string $zpl ZPL code to render
     * @param int $dpi Printer DPI (203, 300, 600)
     * @param float $widthInches Label width in inches
     * @param float $heightInches Label height in inches
     * @return string Binary PNG data
     * @throws \Exception
     */
    public function convertZplToPng(
        string $zpl,
        int $dpi,
        float $widthInches,
        float $heightInches
    ): string {
        $dpmm = round($dpi / 25.4);

        // Validate DPMM
        if (!in_array($dpmm, [6, 8, 12, 24])) {
            throw new \Exception("Invalid DPMM: {$dpmm}. Must be 6, 8, 12, or 24.");
        }

        $url = self::BASE_URL . "/printers/{$dpmm}dpmm/labels/{$widthInches}x{$heightInches}/0/";

        $response = Http::withHeaders([
            'Content-Type' => 'application/x-www-form-urlencoded',
        ])->post($url, $zpl);

        if (!$response->successful()) {
            throw new \Exception("Labelary API error: {$response->status()} {$response->body()}");
        }

        return $response->body();
    }

    /**
     * Convert ZPL to PDF
     */
    public function convertZplToPdf(
        string $zpl,
        int $dpi,
        float $widthInches,
        float $heightInches,
        array $options = []
    ): string {
        $dpmm = round($dpi / 25.4);
        $url = self::BASE_URL . "/printers/{$dpmm}dpmm/labels/{$widthInches}x{$heightInches}/0/";

        $headers = [
            'Content-Type' => 'application/x-www-form-urlencoded',
            'Accept' => 'application/pdf',
        ];

        // Add optional PDF headers
        if (isset($options['page_size'])) {
            $headers['X-Page-Size'] = $options['page_size'];
        }
        if (isset($options['rotation'])) {
            $headers['X-Rotation'] = $options['rotation'];
        }

        $response = Http::withHeaders($headers)->post($url, $zpl);

        if (!$response->successful()) {
            throw new \Exception("Labelary API error: {$response->status()}");
        }

        return $response->body();
    }

    /**
     * Extract data from ZPL (JSON output)
     */
    public function extractZplData(
        string $zpl,
        int $dpi,
        float $widthInches,
        float $heightInches
    ): array {
        $dpmm = round($dpi / 25.4);
        $url = self::BASE_URL . "/printers/{$dpmm}dpmm/labels/{$widthInches}x{$heightInches}/0/";

        $response = Http::withHeaders([
            'Content-Type' => 'application/x-www-form-urlencoded',
            'Accept' => 'application/json',
        ])->post($url, $zpl);

        if (!$response->successful()) {
            throw new \Exception("Labelary API error: {$response->status()}");
        }

        return $response->json();
    }
}
```

**Usage:**
```php
$labelaryApi = new LabelaryApi();

// Get PNG
$pngData = $labelaryApi->convertZplToPng(
    zpl: '^xa^fdHello World^fs^xz',
    dpi: 203,
    widthInches: 4,
    heightInches: 6
);

return response($pngData)->header('Content-Type', 'image/png');
```

---

## Caching Pattern

### Client-Side Cache

```typescript
class LabelaryCache {
    private cache: Map<string, Blob> = new Map();
    private readonly MAX_SIZE = 50; // Cache max 50 previews

    private getCacheKey(zpl: string, width: number, height: number, dpi: number): string {
        return `${width}x${height}@${dpi}:${this.hashCode(zpl)}`;
    }

    private hashCode(str: string): number {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = (hash << 5) - hash + char;
            hash |= 0; // Convert to 32bit integer
        }
        return hash;
    }

    async get(
        zpl: string,
        width: number,
        height: number,
        dpi: number
    ): Promise<Blob | null> {
        const key = this.getCacheKey(zpl, width, height, dpi);
        return this.cache.get(key) || null;
    }

    set(zpl: string, width: number, height: number, dpi: number, blob: Blob): void {
        const key = this.getCacheKey(zpl, width, height, dpi);

        // Evict oldest if cache full
        if (this.cache.size >= this.MAX_SIZE) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }

        this.cache.set(key, blob);
    }

    clear(): void {
        this.cache.clear();
    }
}

// Usage
const cache = new LabelaryCache();

async function fetchWithCache(zpl: string, width: number, height: number, dpi: number) {
    // Check cache first
    const cached = await cache.get(zpl, width, height, dpi);
    if (cached) {
        return cached;
    }

    // Fetch from API
    const blob = await fetchLabelaryBlob(zpl, width, height, dpi);

    // Store in cache
    cache.set(zpl, width, height, dpi, blob);

    return blob;
}
```

---

## Debounced Preview Pattern

### Live Preview with Debounce

```typescript
import { useState, useEffect, useRef } from 'react';
import { debounce } from 'lodash';

const LiveZplPreview = () => {
    const [zpl, setZpl] = useState('^xa^fdHello^fs^xz');
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    // Debounced fetch function
    const debouncedFetch = useRef(
        debounce(async (zplCode: string) => {
            setLoading(true);

            try {
                const dpmm = Math.round(203 / 25.4); // 8
                const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/4x6/0/`;

                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: zplCode,
                });

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);

                // Revoke old URL
                if (previewUrl) {
                    URL.revokeObjectURL(previewUrl);
                }

                setPreviewUrl(url);
            } catch (error) {
                console.error('Preview error:', error);
            } finally {
                setLoading(false);
            }
        }, 500) // 500ms debounce
    ).current;

    useEffect(() => {
        if (zpl) {
            debouncedFetch(zpl);
        }

        return () => {
            debouncedFetch.cancel();
        };
    }, [zpl]);

    return (
        <div className="grid grid-cols-2 gap-4">
            <div>
                <textarea
                    value={zpl}
                    onChange={(e) => setZpl(e.target.value)}
                    className="w-full h-64 font-mono text-sm"
                    placeholder="Enter ZPL code..."
                />
            </div>
            <div>
                {loading && <div>Rendering...</div>}
                {previewUrl && <img src={previewUrl} alt="Live preview" />}
            </div>
        </div>
    );
};
```

---

## Error Boundary Pattern

```typescript
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

class LabelaryErrorBoundary extends Component<Props, State> {
    state: State = {
        hasError: false,
        error: null,
    };

    static getDerivedStateFromError(error: Error): State {
        return {
            hasError: true,
            error,
        };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Labelary preview error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                this.props.fallback || (
                    <div className="bg-red-50 border border-red-200 rounded p-4">
                        <h3 className="text-red-800 font-medium">Label Preview Error</h3>
                        <p className="text-red-600 text-sm mt-2">
                            {this.state.error?.message || 'Failed to render label preview'}
                        </p>
                        <button
                            onClick={() => this.setState({ hasError: false, error: null })}
                            className="mt-3 text-sm text-red-700 underline"
                        >
                            Try again
                        </button>
                    </div>
                )
            );
        }

        return this.props.children;
    }
}

// Usage
<LabelaryErrorBoundary>
    <LabelaryPreviewModal {...props} />
</LabelaryErrorBoundary>
```

---

## TypeScript Types

```typescript
// Labelary API types
export type LabelaryDpmm = 6 | 8 | 12 | 24;
export type LabelaryOutputFormat = 'png' | 'pdf' | 'json' | 'ipl' | 'epl' | 'dpl' | 'sbpl' | 'pcl5' | 'pcl6';
export type LabelaryRotation = 0 | 90 | 180 | 270;
export type LabelaryQuality = 'Grayscale' | 'Bitonal';

export interface LabelaryRequest {
    zpl: string;
    dpi: number;
    widthInches: number;
    heightInches: number;
    outputFormat?: LabelaryOutputFormat;
    rotation?: LabelaryRotation;
    quality?: LabelaryQuality;
    linting?: boolean;
}

export interface LabelaryJsonResponse {
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

## Best Practices

### ✅ DO

1. **Always convert DPI to DPMM:**
   ```typescript
   const dpmm = Math.round(dpi / 25.4);
   ```

2. **Always use POST for production:**
   ```typescript
   method: 'POST'
   ```

3. **Always cleanup object URLs:**
   ```typescript
   return () => {
       if (imageUrl) URL.revokeObjectURL(imageUrl);
   };
   ```

4. **Always handle errors:**
   ```typescript
   if (!response.ok) {
       throw new Error(`API error: ${response.status}`);
   }
   ```

5. **Implement rate limiting:**
   ```typescript
   await new Promise(resolve => setTimeout(resolve, 350));
   ```

### ❌ DON'T

1. **Don't use DPI directly in URL**
2. **Don't forget to cleanup object URLs** (memory leak!)
3. **Don't ignore rate limits** (will get 429 errors)
4. **Don't hardcode DPMM values** (use dynamic conversion)
5. **Don't use GET for production** (size/security issues)

---

## Related Documentation

- **Getting Started:** `categories/getting-started.md`
- **API Endpoints:** `categories/api-endpoints.md`
- **DPI Conversion:** `patterns/dpi-conversion.md`
- **Error Handling:** `patterns/error-handling.md`
- **Code Examples:** `CODE_EXAMPLES.md`
- **Workflow:** `WORKFLOWS/ZPL_PREVIEW_WORKFLOW.md`
