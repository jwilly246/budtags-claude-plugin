# GET vs POST Pattern

When to use GET requests vs POST requests with Labelary API.

---

## Quick Decision Tree

```
Is this for production? → Use POST
Is ZPL > 3,000 chars?  → Use POST
Contains sensitive data? → Use POST
Just quick testing?    → Can use GET
Otherwise             → Use POST (safer default)
```

**Rule of thumb:** When in doubt, use POST.

---

## GET Request Pattern

### When to Use GET

✅ Quick testing and debugging
✅ ZPL is small (<3,000 characters)
✅ No sensitive data in ZPL
✅ Simple one-off requests
✅ Sharing label preview links

### GET Endpoint

```
GET /v1/printers/{dpmm}/labels/{width}x{height}/{index}/{zpl}
```

### Example

```bash
curl --get http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data-urlencode "^xa^cfa,50^fo100,100^fdHello World^fs^xz" > label.png
```

### Advantages

- Simple URL structure
- Easy to share (copy/paste URL)
- Browser-friendly (can paste URL directly)
- No request body needed

### Disadvantages

- ❌ URL length limits (~2,000-8,000 chars depending on browser/server)
- ❌ Special characters must be URL-encoded
- ❌ Sensitive data visible in URLs (logs, browser history)
- ❌ Binary data difficult to embed
- ❌ Not recommended for production

### URL Encoding Issues

**Must encode:**
- `#` → `%23`
- `&` → `%26`
- `+` → `%2B`
- ` ` (space) → `%20` or `+`

**With curl:**
```bash
# ✅ CORRECT - Use --data-urlencode
curl --get http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data-urlencode "^xa^fdTest #123^fs^xz"

# ❌ WRONG - Manual encoding error-prone
curl "http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/^xa^fdTest%20%23123^fs^xz"
```

---

## POST Request Pattern

### When to Use POST

✅ Production applications (ALWAYS)
✅ Large ZPL code (>3,000 characters)
✅ Sensitive data (customer info, serial numbers)
✅ Embedded binary data
✅ Character encoding issues with GET
✅ Want to use advanced headers

### POST Endpoint

```
POST /v1/printers/{dpmm}/labels/{width}x{height}/{index}
```

**Note:** No `{zpl}` in URL - ZPL goes in request body

### Example

```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --data "^xa^cfa,50^fo100,100^fdHello World^fs^xz" > label.png
```

### Advantages

- ✅ No size limits (up to 1 MB free tier)
- ✅ No URL encoding needed
- ✅ Sensitive data in body (not logged in URLs)
- ✅ Supports binary data
- ✅ Can use advanced headers (rotation, quality, linting)
- ✅ Production-ready

### Disadvantages

- Slightly more complex (need headers)
- Can't share via URL alone
- Requires HTTP client (not browser-friendly)

---

## Implementation Patterns

### GET - Browser/Testing

**Browser (paste in address bar):**
```
http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/^xa^fdHello^fs^xz
```

**JavaScript:**
```javascript
const zpl = encodeURIComponent('^xa^fdHello World^fs^xz');
const url = `http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/${zpl}`;

// Can use image tag directly
<img src={url} alt="Label preview" />
```

**curl:**
```bash
curl --get http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data-urlencode "^xa^fdHello^fs^xz" > label.png
```

---

### POST - Production

**TypeScript/React (RECOMMENDED):**
```typescript
const fetchLabelPreview = async (zplCode: string, dpi: number, width: number, height: number) => {
    const dpmm = Math.round(dpi / 25.4);
    const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${width}x${height}/0/`;

    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: zplCode,
    });

    if (!response.ok) {
        throw new Error(`Labelary API error: ${response.status}`);
    }

    return await response.blob();
};
```

**curl:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --data "^xa^fdHello World^fs^xz" > label.png
```

**Python:**
```python
import requests

zpl = "^xa^fdHello World^fs^xz"
url = "http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/"

response = requests.post(
    url,
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    data=zpl
)

with open('label.png', 'wb') as f:
    f.write(response.content)
```

---

## POST with File Upload

For very large ZPL (>10,000 characters), use multipart file upload:

```bash
# Save ZPL to file
echo "^xa^fdHello^fs^xz" > label.zpl

# Upload as file
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --form file=@label.zpl > label.png
```

**TypeScript:**
```typescript
const formData = new FormData();
const zplBlob = new Blob([zplCode], { type: 'text/plain' });
formData.append('file', zplBlob, 'label.zpl');

const response = await fetch(apiUrl, {
    method: 'POST',
    body: formData,
});
```

---

## Advanced Headers (POST Only)

These features ONLY work with POST:

```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --header "Accept: application/pdf" \
  --header "X-Rotation: 90" \
  --header "X-Quality: Grayscale" \
  --header "X-Linter: On" \
  --data "@label.zpl" > label.pdf
```

**Available headers:**
- `Accept` - Output format (PNG, PDF, JSON, etc.)
- `X-Rotation` - Rotate label (0, 90, 180, 270)
- `X-Quality` - PNG quality (Grayscale, Bitonal)
- `X-Linter` - Enable ZPL linting
- `X-Page-Size` - PDF page size (Letter, A4, etc.)
- `X-Page-Layout` - Multi-label PDF grid
- `X-Label-Border` - PDF label borders

**GET does NOT support these!**

---

## Size Comparison

### GET - Limited by URL Length

**Browser limits:**
- Chrome: ~8,000 chars
- Firefox: ~65,000 chars
- Safari: ~80,000 chars
- IE: ~2,000 chars (old browsers)

**Server limits:**
- Apache: 8,190 bytes (default)
- Nginx: 4,096 bytes (default)

**Safe limit:** 3,000 characters

### POST - Much Larger

- Free tier: Up to 1 MB request body
- Premium: Higher limits
- Typical ZPL label: 500-5,000 bytes

**Example:**
```
Simple label:      ~200 bytes  → GET or POST
Complex label:   ~2,000 bytes  → GET or POST
Very complex:    ~10,000 bytes → POST only
Multiple labels: ~50,000 bytes → POST only
```

---

## Security Considerations

### GET - Less Secure

❌ URLs logged by:
- Web server access logs
- Proxy servers
- Browser history
- Network monitoring tools

**Example logged URL:**
```
GET /v1/printers/8dpmm/labels/4x6/0/^xa^fdJohn%20Doe^fdSSN%20123-45-6789^fs^xz
```

Sensitive data exposed!

### POST - More Secure

✅ Request body NOT logged in:
- Standard access logs
- Browser history
- URL-based tracking

❌ Still logged in:
- Full request/response logging (if enabled)
- Network packet capture

**Recommendation:** Use HTTPS + POST for sensitive data

---

## Comparison Table

| Feature | GET | POST |
|---------|-----|------|
| Max size | ~3,000 chars | 1 MB (free tier) |
| URL encoding | Required | Not required |
| Browser-friendly | Yes | No |
| Shareable URL | Yes | No |
| Sensitive data | ❌ Exposed | ✅ Protected |
| Advanced headers | ❌ No | ✅ Yes |
| Production use | ❌ Not recommended | ✅ Recommended |
| Binary data | ❌ Difficult | ✅ Easy |
| File upload | ❌ No | ✅ Yes |

---

## Recommendations

### For Development/Testing

Use GET when:
- Quick debugging
- Sharing label preview with team
- Small ZPL snippets
- Browser-based testing

### For Production Applications

**ALWAYS use POST:**
```typescript
// ✅ RECOMMENDED for BudTags
const response = await fetch(apiUrl, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: zplCode,
});
```

### For Sensitive Data

**ALWAYS use POST + HTTPS:**
```typescript
// ✅ Secure
const response = await fetch('https://api.labelary.com/v1/...', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: zplWithCustomerData,
});
```

---

## BudTags Pattern (Production)

Real example from BudTags project:

```typescript
// Always POST for production
const fetchLabelaryImage = async () => {
    const dpmm = Math.round(dpi / 25.4);
    const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/${widthInches}x${heightInches}/0/`;

    const response = await fetch(apiUrl, {
        method: 'POST', // ALWAYS POST
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: zplCode, // ZPL in body, not URL
    });

    if (!response.ok) {
        throw new Error(`Labelary API returned ${response.status}: ${response.statusText}`);
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    setImageUrl(url);
};
```

---

## Related Documentation

- **Getting Started:** `categories/getting-started.md`
- **API Endpoints:** `categories/api-endpoints.md`
- **Error Handling:** `patterns/error-handling.md`
- **Integration:** `patterns/integration.md`
