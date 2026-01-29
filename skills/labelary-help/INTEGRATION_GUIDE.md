# Labelary API - Integration Guide

Step-by-step guide to integrating the Labelary ZPL rendering API into your web application.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Setup](#quick-setup)
3. [Step-by-Step Integration](#step-by-step-integration)
4. [Testing Your Integration](#testing-your-integration)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You Need

- ✅ Basic understanding of HTTP/REST APIs
- ✅ ZPL code to render (or ZPL generation logic)
- ✅ Label dimensions (width × height in inches)
- ✅ Printer DPI (usually 203 or 300)

### No Requirements

- ❌ No API key needed (free tier)
- ❌ No sign-up required
- ❌ No authentication headers

---

## Quick Setup

### 1. Test with curl

```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --data "^xa^cfa,50^fo100,100^fdHello World^fs^xz" > test.png

# View the generated image
open test.png  # macOS
start test.png # Windows
xdg-open test.png # Linux
```

### 2. Verify Output

- Check that `test.png` was created
- Open image - should show "Hello World" text
- Image should be ~812 × 1218 pixels (4" × 6" at 203 DPI)

**If this works, you're ready to integrate!**

---

## Step-by-Step Integration

### Step 1: Set Up Your Project

#### React/TypeScript Project

```bash
# Create new React app (if needed)
npx create-react-app my-label-app --template typescript

# Or add to existing project
cd my-existing-project
```

#### Install Dependencies

```bash
# For toast notifications (optional but recommended)
npm install react-toastify
```

---

### Step 2: Create API Service

Create a dedicated service module for Labelary API calls.

**File:** `src/services/LabelaryService.ts`

```typescript
export interface LabelaryConfig {
    widthInches: number;
    heightInches: number;
    dpi: number;
}

export interface LabelaryResponse {
    imageUrl: string;
    totalLabels?: number;
}

export class LabelaryService {
    private static readonly BASE_URL = 'http://api.labelary.com/v1';

    /**
     * Convert DPI to dpmm (dots per millimeter)
     */
    private static getDpmm(dpi: number): number {
        const dpmm = Math.round(dpi / 25.4);
        const validDpmm = [6, 8, 12, 24];

        if (!validDpmm.includes(dpmm)) {
            throw new Error(
                `Invalid dpmm: ${dpmm}. Printer DPI ${dpi} must convert to 6, 8, 12, or 24 dpmm.`
            );
        }

        return dpmm;
    }

    /**
     * Render ZPL code to PNG image
     */
    static async renderZplToPng(
        zplCode: string,
        config: LabelaryConfig
    ): Promise<LabelaryResponse> {
        const dpmm = this.getDpmm(config.dpi);
        const url = `${this.BASE_URL}/printers/${dpmm}dpmm/labels/${config.widthInches}x${config.heightInches}/0/`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: zplCode,
        });

        if (!response.ok) {
            throw new Error(`Labelary API error: ${response.status} ${response.statusText}`);
        }

        // Get total label count from response header
        const totalLabels = parseInt(response.headers.get('X-Total-Count') || '0');

        // Convert blob to object URL
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);

        return { imageUrl, totalLabels };
    }

    /**
     * Render ZPL code to PDF
     */
    static async renderZplToPdf(
        zplCode: string,
        config: LabelaryConfig
    ): Promise<Blob> {
        const dpmm = this.getDpmm(config.dpi);
        const url = `${this.BASE_URL}/printers/${dpmm}dpmm/labels/${config.widthInches}x${config.heightInches}/0/`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/pdf',
            },
            body: zplCode,
        });

        if (!response.ok) {
            throw new Error(`Labelary API error: ${response.status} ${response.statusText}`);
        }

        return response.blob();
    }

    /**
     * Extract data from ZPL as JSON
     */
    static async extractZplData(
        zplCode: string,
        config: LabelaryConfig
    ): Promise<any> {
        const dpmm = this.getDpmm(config.dpi);
        const url = `${this.BASE_URL}/printers/${dpmm}dpmm/labels/${config.widthInches}x${config.heightInches}/0/`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
            },
            body: zplCode,
        });

        if (!response.ok) {
            throw new Error(`Labelary API error: ${response.status} ${response.statusText}`);
        }

        return response.json();
    }
}
```

---

### Step 3: Create Preview Component

Create a React component to display ZPL previews.

**File:** `src/components/ZplPreview.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { LabelaryService, LabelaryConfig } from '../services/LabelaryService';

interface ZplPreviewProps {
    zplCode: string;
    config: LabelaryConfig;
}

export const ZplPreview: React.FC<ZplPreviewProps> = ({ zplCode, config }) => {
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!zplCode) return;

        const loadPreview = async () => {
            setIsLoading(true);
            setError(null);

            try {
                const { imageUrl } = await LabelaryService.renderZplToPng(zplCode, config);
                setImageUrl(imageUrl);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load preview');
            } finally {
                setIsLoading(false);
            }
        };

        loadPreview();

        // Cleanup: revoke object URL
        return () => {
            if (imageUrl) {
                URL.revokeObjectURL(imageUrl);
            }
        };
    }, [zplCode, config]);

    if (isLoading) {
        return <div>Loading preview...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    if (!imageUrl) {
        return <div>No preview available</div>;
    }

    return (
        <div>
            <img
                src={imageUrl}
                alt="ZPL Preview"
                style={{ imageRendering: 'pixelated' }}
            />
        </div>
    );
};
```

---

### Step 4: Use the Component

**File:** `src/App.tsx`

```typescript
import React, { useState } from 'react';
import { ZplPreview } from './components/ZplPreview';

function App() {
    const [zplCode] = useState(`^xa
^cfa,50
^fo100,100^fdHello World^fs
^xz`);

    return (
        <div className="App">
            <h1>ZPL Label Preview</h1>
            <ZplPreview
                zplCode={zplCode}
                config={{
                    widthInches: 4,
                    heightInches: 6,
                    dpi: 203,
                }}
            />
        </div>
    );
}

export default App;
```

---

### Step 5: Add Error Handling

Enhance error handling with user-friendly messages.

```typescript
try {
    const { imageUrl } = await LabelaryService.renderZplToPng(zplCode, config);
    setImageUrl(imageUrl);
} catch (err) {
    if (err instanceof Error) {
        // Handle specific error types
        if (err.message.includes('429')) {
            setError('Rate limit exceeded. Please wait before retrying.');
        } else if (err.message.includes('400')) {
            setError('Invalid ZPL or label dimensions.');
        } else if (err.message.includes('413')) {
            setError('ZPL code too large (max 1 MB).');
        } else {
            setError(err.message);
        }
    } else {
        setError('Unknown error occurred');
    }
}
```

---

## Testing Your Integration

### Unit Tests

```typescript
import { LabelaryService } from './LabelaryService';

describe('LabelaryService', () => {
    it('converts DPI to dpmm correctly', () => {
        // Private method testing - use test helper
        expect(LabelaryService['getDpmm'](203)).toBe(8);
        expect(LabelaryService['getDpmm'](300)).toBe(12);
    });

    it('renders valid ZPL to PNG', async () => {
        const zpl = '^xa^cfa,50^fo100,100^fdTest^fs^xz';
        const config = { widthInches: 4, heightInches: 6, dpi: 203 };

        const result = await LabelaryService.renderZplToPng(zpl, config);

        expect(result.imageUrl).toBeTruthy();
        expect(result.imageUrl).toMatch(/^blob:/);
    });

    it('throws error for invalid DPI', async () => {
        const zpl = '^xa^cfa,50^fo100,100^fdTest^fs^xz';
        const config = { widthInches: 4, heightInches: 6, dpi: 999 }; // Invalid

        await expect(
            LabelaryService.renderZplToPng(zpl, config)
        ).rejects.toThrow('Invalid dpmm');
    });
});
```

### Integration Tests

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { ZplPreview } from './ZplPreview';

describe('ZplPreview', () => {
    it('displays loading state initially', () => {
        render(
            <ZplPreview
                zplCode="^xa^xz"
                config={{ widthInches: 4, heightInches: 6, dpi: 203 }}
            />
        );

        expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    it('displays preview image after loading', async () => {
        render(
            <ZplPreview
                zplCode="^xa^cfa,50^fo100,100^fdTest^fs^xz"
                config={{ widthInches: 4, heightInches: 6, dpi: 203 }}
            />
        );

        await waitFor(() => {
            expect(screen.getByAltText('ZPL Preview')).toBeInTheDocument();
        });
    });
});
```

---

## Production Deployment

### 1. Environment Configuration

```typescript
// config.ts
export const LABELARY_CONFIG = {
    baseUrl: process.env.REACT_APP_LABELARY_URL || 'http://api.labelary.com/v1',
    // For premium users:
    // baseUrl: process.env.REACT_APP_LABELARY_URL || 'http://your-private-hostname.com/v1',
};
```

### 2. Rate Limiting

Implement client-side rate limiting for free tier (3 req/sec):

```typescript
class RateLimiter {
    private queue: number[] = [];
    private maxPerSecond: number;

    constructor(maxPerSecond: number = 2) {
        this.maxPerSecond = maxPerSecond; // 2 req/sec for safety margin
    }

    async execute<T>(fn: () => Promise<T>): Promise<T> {
        const now = Date.now();
        this.queue = this.queue.filter(t => now - t < 1000);

        while (this.queue.length >= this.maxPerSecond) {
            await new Promise(resolve => setTimeout(resolve, 100));
            this.queue = this.queue.filter(t => Date.now() - t < 1000);
        }

        this.queue.push(Date.now());
        return fn();
    }
}

export const labelaryRateLimiter = new RateLimiter(2);

// Usage in service
static async renderZplToPng(...) {
    return labelaryRateLimiter.execute(async () => {
        const response = await fetch(url, options);
        // ... rest of implementation
    });
}
```

### 3. Caching

Cache preview images to reduce API calls:

```typescript
const previewCache = new Map<string, { url: string; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

function getCacheKey(zpl: string, config: LabelaryConfig): string {
    return `${zpl}-${config.dpi}-${config.widthInches}x${config.heightInches}`;
}

static async renderZplToPng(
    zplCode: string,
    config: LabelaryConfig
): Promise<LabelaryResponse> {
    const cacheKey = getCacheKey(zplCode, config);
    const cached = previewCache.get(cacheKey);

    // Return cached result if fresh
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
        return { imageUrl: cached.url };
    }

    // Fetch new preview
    const result = await this.fetchPreview(zplCode, config);

    // Cache result
    previewCache.set(cacheKey, {
        url: result.imageUrl,
        timestamp: Date.now(),
    });

    return result;
}
```

### 4. Error Monitoring

Integrate error tracking:

```typescript
import * as Sentry from '@sentry/react';

try {
    const result = await LabelaryService.renderZplToPng(zplCode, config);
    return result;
} catch (error) {
    Sentry.captureException(error, {
        tags: {
            service: 'labelary',
            operation: 'renderZplToPng',
        },
        extra: {
            zplLength: zplCode.length,
            config,
        },
    });
    throw error;
}
```

### 5. Analytics

Track usage:

```typescript
// Track successful renders
analytics.track('Labelary Preview Generated', {
    widthInches: config.widthInches,
    heightInches: config.heightInches,
    dpi: config.dpi,
    zplLength: zplCode.length,
});

// Track errors
analytics.track('Labelary Preview Failed', {
    error: error.message,
    statusCode: response.status,
});
```

---

## Troubleshooting

### Common Issues

#### 1. CORS Errors

**Symptom:**
```
Access to fetch at 'http://api.labelary.com/...' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**

Labelary API supports CORS. If you're getting CORS errors:
- Check browser console for exact error
- Ensure you're using `http://` not `https://` (Labelary is HTTP-only)
- For production, consider proxying through your backend

**Backend Proxy Example (Node.js/Express):**

```javascript
app.post('/api/labelary-proxy', async (req, res) => {
    const { zpl, dpmm, width, height } = req.body;

    try {
        const response = await fetch(
            `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${width}x${height}/0/`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: zpl,
            }
        );

        const blob = await response.blob();
        res.setHeader('Content-Type', 'image/png');
        res.send(Buffer.from(await blob.arrayBuffer()));
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});
```

#### 2. Rate Limit Errors (HTTP 429)

**Symptom:**
```
Labelary API error: 429 Too Many Requests
```

**Solutions:**

1. Implement client-side rate limiting (see [Production Deployment](#production-deployment))
2. Add exponential backoff retry logic:

```typescript
async function fetchWithRetry(fn: () => Promise<Response>, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await fn();
        } catch (error) {
            if (error.message.includes('429') && i < maxRetries - 1) {
                const delay = Math.pow(2, i) * 1000; // Exponential backoff
                await new Promise(resolve => setTimeout(resolve, delay));
                continue;
            }
            throw error;
        }
    }
}
```

3. Upgrade to premium plan for higher limits

#### 3. Invalid DPMM Error (HTTP 400)

**Symptom:**
```
Labelary API error: 400 Invalid dpmm value
```

**Solution:**

Check DPI to dpmm conversion:

```typescript
console.log('DPI:', dpi);
console.log('Calculated dpmm:', Math.round(dpi / 25.4));

// Valid dpmm values: 6, 8, 12, 24
// Valid DPI values: 152, 203, 300, 600
```

#### 4. Large ZPL Errors (HTTP 413)

**Symptom:**
```
Labelary API error: 413 Payload Too Large
```

**Solutions:**

1. Check ZPL size:

```typescript
const sizeInBytes = new Blob([zplCode]).size;
const sizeInMB = sizeInBytes / (1024 * 1024);

if (sizeInMB > 1) {
    throw new Error(`ZPL too large: ${sizeInMB.toFixed(2)} MB (max 1 MB)`);
}
```

2. Optimize ZPL:
   - Remove unnecessary whitespace
   - Use stored formats for repeated elements
   - Compress embedded graphics

#### 5. Memory Leaks (Object URLs)

**Symptom:**

Browser memory usage increases over time.

**Solution:**

Always revoke object URLs:

```typescript
useEffect(() => {
    return () => {
        if (imageUrl) {
            URL.revokeObjectURL(imageUrl);
        }
    };
}, [imageUrl]);
```

---

## Next Steps

- **Production Ready?** Review [Production Deployment](#production-deployment)
- **Need Real Examples?** See [CODE_EXAMPLES.md](CODE_EXAMPLES.md)
- **API Details?** See [API_REFERENCE.md](API_REFERENCE.md)
- **Specific Workflows?** See [WORKFLOWS/](WORKFLOWS/)

---

**Congratulations! You've successfully integrated the Labelary API.**

For additional help, see:
- `skill.md` - Complete skill reference
- `docs/` - Full Labelary documentation
- `WORKFLOWS/` - Task-specific guides
