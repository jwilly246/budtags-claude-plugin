# Error Handling Pattern

Common errors, HTTP status codes, and troubleshooting strategies for Labelary API.

---

## HTTP Status Codes

### 200 OK - Success

Request succeeded, response contains rendered label.

**Response headers:**
```
HTTP/1.1 200 OK
Content-Type: image/png
X-Total-Count: 1
```

---

### 400 Bad Request - Invalid Parameters

Request has invalid parameters.

**Common causes:**
1. Invalid DPMM value
2. Invalid label dimensions
3. Malformed ZPL code
4. Invalid header values

#### Invalid DPMM

```
GET /v1/printers/203dpmm/labels/4x6/0/
→ 400 Bad Request: Invalid printer density: 203dpmm
```

**Fix:**
```javascript
// ❌ WRONG
const apiUrl = `http://api.labelary.com/v1/printers/203dpmm/...`;

// ✅ CORRECT - Convert DPI to DPMM
const dpmm = Math.round(203 / 25.4); // 8
const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/...`;
```

See `patterns/dpi-conversion.md` for complete guide.

#### Invalid Dimensions

```
GET /v1/printers/8dpmm/labels/20x30/0/
→ 400 Bad Request: Label dimensions exceed maximum (15" x 15")
```

**Fix:** Use dimensions ≤ 15 inches

```javascript
// ❌ WRONG
const width = 20;
const height = 30;

// ✅ CORRECT
const width = Math.min(widthInches, 15);
const height = Math.min(heightInches, 15);
```

---

### 413 Payload Too Large - Size Limit Exceeded

Request body exceeds size limit.

**Free tier limit:** 1 MB

**Common causes:**
- Very long ZPL code
- Many labels in single request
- Large embedded graphics

**Example:**
```
POST /v1/printers/8dpmm/labels/4x6/0/
Body: [2 MB ZPL]
→ 413 Payload Too Large
```

**Fixes:**

1. **Split requests:**
```typescript
// Split into smaller batches
const batchSize = 50;
for (let i = 0; i < labels.length; i += batchSize) {
    const batch = labels.slice(i, i + batchSize);
    await fetchLabelary(batch.join(''));
}
```

2. **Optimize ZPL:**
```zpl
// ❌ Verbose
^FO100,100^A0N,30,30^FDText^FS
^FO100,150^A0N,30,30^FDMore^FS

// ✅ Use default font
^CF0,30,30
^FO100,100^FDText^FS
^FO100,150^FDMore^FS
```

3. **Compress graphics:**
```zpl
// ❌ Large embedded image
^GFA,10000,10000,50,... [huge hex data] ...

// ✅ Smaller, optimized image
^GFA,2000,2000,25,... [optimized] ...
```

4. **Upgrade to premium:**
- Plus: Higher limits
- Business: Even higher limits

---

### 429 Too Many Requests - Rate Limit Exceeded

Exceeded rate limits.

**Free tier limits:**
- 3 requests per second
- 5,000 requests per day

**Example:**
```
10 requests in 1 second
→ 429 Too Many Requests
Retry-After: 1
```

**Fixes:**

1. **Implement throttling:**
```typescript
class LabelaryClient {
    private requestQueue: Promise<any>[] = [];
    private readonly MAX_CONCURRENT = 3;
    private readonly DELAY_MS = 350; // 3 req/sec = 1 request every 333ms

    async fetchWithThrottle(zpl: string) {
        // Wait if queue full
        if (this.requestQueue.length >= this.MAX_CONCURRENT) {
            await Promise.race(this.requestQueue);
        }

        // Add delay
        await new Promise(resolve => setTimeout(resolve, this.DELAY_MS));

        // Make request
        const promise = fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: zpl,
        }).finally(() => {
            // Remove from queue
            this.requestQueue = this.requestQueue.filter(p => p !== promise);
        });

        this.requestQueue.push(promise);
        return promise;
    }
}
```

2. **Exponential backoff:**
```typescript
async function fetchWithRetry(url: string, options: RequestInit, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        const response = await fetch(url, options);

        if (response.status === 429) {
            const retryAfter = parseInt(response.headers.get('Retry-After') || '1');
            const delay = Math.pow(2, i) * 1000 * retryAfter; // Exponential backoff
            console.warn(`Rate limited. Retrying in ${delay}ms...`);
            await new Promise(resolve => setTimeout(resolve, delay));
            continue;
        }

        return response;
    }

    throw new Error('Max retries exceeded');
}
```

3. **Batch processing:**
```typescript
// Process labels in batches with delays
async function processLabelBatch(labels: string[]) {
    for (const label of labels) {
        await fetchWithThrottle(label);
        await new Promise(resolve => setTimeout(resolve, 350)); // 3 req/sec
    }
}
```

4. **Cache results:**
```typescript
const cache = new Map<string, Blob>();

async function fetchWithCache(zpl: string) {
    const hash = hashCode(zpl);

    if (cache.has(hash)) {
        return cache.get(hash)!;
    }

    const response = await fetch(apiUrl, {
        method: 'POST',
        body: zpl,
    });

    const blob = await response.blob();
    cache.set(hash, blob);
    return blob;
}
```

5. **Upgrade to premium:**
- Plus: 6 req/sec, 20,000 req/day
- Business: 10 req/sec, 40,000 req/day

---

### 500 Internal Server Error - Server Issue

Labelary server error (rare).

**Common causes:**
- Complex ZPL causing rendering issues
- Server overload
- Temporary outage

**Fixes:**

1. **Retry with backoff:**
```typescript
async function fetchWithRetry(url: string, options: RequestInit) {
    const maxRetries = 3;

    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url, options);

            if (response.status === 500 && i < maxRetries - 1) {
                await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
                continue;
            }

            return response;
        } catch (error) {
            if (i === maxRetries - 1) throw error;
        }
    }
}
```

2. **Simplify ZPL:**
```zpl
// ❌ Complex nested commands
^XA^FO0,0^GB800,600,2^FS^FO50,50^GB700,500,1^FS...

// ✅ Simpler version
^XA^FO50,50^FDSimple text^FS^XZ
```

3. **Report to Labelary:**
- Contact support if persistent
- Provide ZPL and parameters

---

## Network Errors

### CORS Errors (Browser)

```
Access to fetch at 'http://api.labelary.com' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**Cause:** Labelary API supports CORS, but some browsers/configurations may block

**Fixes:**

1. **Use HTTPS:**
```typescript
// ✅ HTTPS (better CORS support)
const apiUrl = 'https://api.labelary.com/v1/...';
```

2. **Proxy through your backend:**
```typescript
// Frontend
const response = await fetch('/api/labelary-proxy', {
    method: 'POST',
    body: JSON.stringify({ zpl }),
});

// Backend (Laravel)
Route::post('/api/labelary-proxy', function (Request $request) {
    $response = Http::post('http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/', [
        'body' => $request->input('zpl'),
    ]);
    return response($response->body(), $response->status());
});
```

### Timeout Errors

```
TypeError: Failed to fetch
```

**Cause:** Network timeout, slow connection, large response

**Fix:**
```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

try {
    const response = await fetch(apiUrl, {
        method: 'POST',
        signal: controller.signal,
        body: zpl,
    });
    clearTimeout(timeoutId);
    return response;
} catch (error) {
    if (error.name === 'AbortError') {
        throw new Error('Request timed out');
    }
    throw error;
}
```

---

## ZPL Syntax Errors

### Invalid ZPL

Labelary may return 200 OK but with unexpected output.

**Common issues:**
- Missing ^XA or ^XZ
- Unclosed commands
- Invalid parameters

**Use linting:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "X-Linter: On" \
  --data "^xa^gb1,1,3^fs^xz" -v
```

**Response:**
```
X-Warnings: 303|1|^GB|2|Value 1 is less than minimum value 3; used 3 instead
```

See `categories/advanced-features.md` for linting details.

---

## Error Handling Pattern (TypeScript)

```typescript
interface LabelaryError {
    status: number;
    message: string;
    retryable: boolean;
}

async function fetchLabelary(zpl: string): Promise<Blob> {
    const dpmm = Math.round(dpi / 25.4);
    const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${width}x${height}/0/`;

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: zpl,
        });

        // Handle HTTP errors
        if (!response.ok) {
            const error: LabelaryError = {
                status: response.status,
                message: await response.text(),
                retryable: false,
            };

            switch (response.status) {
                case 400:
                    error.message = 'Invalid request parameters. Check DPI/DPMM conversion and label dimensions.';
                    break;
                case 413:
                    error.message = 'Request too large. Split into smaller batches or optimize ZPL.';
                    break;
                case 429:
                    error.message = 'Rate limit exceeded. Please wait before retrying.';
                    error.retryable = true;
                    break;
                case 500:
                    error.message = 'Labelary server error. Please retry.';
                    error.retryable = true;
                    break;
            }

            throw error;
        }

        return await response.blob();
    } catch (error) {
        // Network errors
        if (error instanceof TypeError) {
            throw {
                status: 0,
                message: 'Network error. Check internet connection.',
                retryable: true,
            } as LabelaryError;
        }

        throw error;
    }
}
```

---

## Validation Checklist

Before making request, validate:

1. ✅ **DPMM:** Valid value (6, 8, 12, 24)
2. ✅ **Dimensions:** ≤ 15 inches
3. ✅ **ZPL:** Starts with ^XA, ends with ^XZ
4. ✅ **Size:** Request < 1 MB
5. ✅ **Rate limit:** Not exceeding 3 req/sec
6. ✅ **Content-Type:** application/x-www-form-urlencoded

---

## Debugging Tips

### Enable Verbose Logging

```typescript
async function fetchWithLogging(zpl: string) {
    console.log('ZPL length:', zpl.length);
    console.log('API URL:', apiUrl);

    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: zpl,
    });

    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));

    return response;
}
```

### Test with Minimal ZPL

```typescript
// Test with simplest possible ZPL
const testZpl = '^xa^fdTest^fs^xz';
const response = await fetchLabelary(testZpl);

// If this works, issue is with your ZPL
// If this fails, issue is with API setup
```

### Use Browser DevTools

- Network tab: Check request/response
- Console: View errors
- Headers: Verify Content-Type

---

## Related Documentation

- **Getting Started:** `categories/getting-started.md`
- **Parameters:** `categories/parameters.md`
- **DPI Conversion:** `patterns/dpi-conversion.md`
- **GET vs POST:** `patterns/get-vs-post.md`
