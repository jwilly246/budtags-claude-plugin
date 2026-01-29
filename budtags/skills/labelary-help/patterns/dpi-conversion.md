# DPI to DPMM Conversion Pattern

**CRITICAL:** Labelary uses DPMM (dots per millimeter), NOT DPI (dots per inch)!

---

## The Problem

Most developers think in DPI (dots per inch) because:
- Printer specs list DPI (e.g., "203 DPI Zebra printer")
- Design tools use DPI
- Users understand DPI better

But Labelary API requires DPMM (dots per millimeter):
```
/v1/printers/8dpmm/labels/4x6/0/
             ^^^^^^
```

**Invalid DPI values will cause HTTP 400 errors!**

---

## Conversion Formula

```javascript
const dpmm = Math.round(dpi / 25.4);
```

**Why 25.4?**
- 1 inch = 25.4 millimeters
- DPI / 25.4 = dots per millimeter

**Always round** to nearest integer!

---

## Common Conversions

| DPI | Calculation | DPMM | Labelary Value |
|-----|-------------|------|----------------|
| 152 DPI | 152 / 25.4 = 5.98 | 6 | `6dpmm` |
| 203 DPI | 203 / 25.4 = 7.99 | 8 | `8dpmm` ⭐ |
| 300 DPI | 300 / 25.4 = 11.81 | 12 | `12dpmm` ⭐ |
| 600 DPI | 600 / 25.4 = 23.62 | 24 | `24dpmm` |

⭐ **Most common:** 203 DPI (8dpmm) and 300 DPI (12dpmm)

---

## Valid DPMM Values

Labelary ONLY accepts these 4 values:

✅ `6dpmm` - Low resolution (152 DPI)
✅ `8dpmm` - Standard resolution (203 DPI)
✅ `12dpmm` - High resolution (300 DPI)
✅ `24dpmm` - Very high resolution (600 DPI)

❌ Any other value returns HTTP 400 error:
```
Invalid dpmm value: 10dpmm
```

---

## Implementation Pattern

### TypeScript/JavaScript

```typescript
/**
 * Convert DPI to valid Labelary DPMM value
 * @param dpi - Dots per inch (e.g., 203, 300, 600)
 * @returns Valid DPMM value for Labelary API
 */
function convertDpiToDpmm(dpi: number): 6 | 8 | 12 | 24 {
    const dpmm = Math.round(dpi / 25.4);

    // Ensure valid value
    const validDpmm: (6 | 8 | 12 | 24)[] = [6, 8, 12, 24];

    if (!validDpmm.includes(dpmm as any)) {
        console.warn(`Unusual DPMM value: ${dpmm}, closest valid: ${closestValid(dpmm)}`);
        return closestValid(dpmm);
    }

    return dpmm as 6 | 8 | 12 | 24;
}

function closestValid(dpmm: number): 6 | 8 | 12 | 24 {
    const validValues = [6, 8, 12, 24];
    return validValues.reduce((prev, curr) =>
        Math.abs(curr - dpmm) < Math.abs(prev - dpmm) ? curr : prev
    ) as 6 | 8 | 12 | 24;
}

// Usage
const dpmm = convertDpiToDpmm(203); // 8
const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/4x6/0/`;
```

### React Hook Pattern (BudTags)

```typescript
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

        // Cleanup
        return () => {
            if (imageUrl) {
                URL.revokeObjectURL(imageUrl);
            }
        };
    }, [zplCode, widthInches, heightInches, dpi]);

    return { imageUrl, loading, error };
};
```

---

## Common Mistakes

### ❌ WRONG: Using DPI directly

```typescript
// ❌ This will fail with HTTP 400!
const apiUrl = `http://api.labelary.com/v1/printers/203dpmm/labels/4x6/0/`;
```

**Error:**
```
HTTP 400 Bad Request
Invalid printer density: 203dpmm
```

### ❌ WRONG: Not rounding

```typescript
// ❌ Results in invalid 11.81dpmm
const dpmm = 300 / 25.4;
const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/4x6/0/`;
```

### ❌ WRONG: Hardcoding DPI instead of DPMM

```typescript
// ❌ Brittle, assumes 203 DPI
const apiUrl = `http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/`;

// What if user changes printer to 300 DPI?
```

### ✅ CORRECT: Dynamic conversion

```typescript
// ✅ Works for any DPI
const dpmm = Math.round(dpi / 25.4);
const apiUrl = `http://api.labelary.com/v1/printers/${dpmm}dpmm/labels/4x6/0/`;
```

---

## Zebra Printer DPI Reference

Common Zebra printer models and their DPI:

| Printer Model | DPI | DPMM |
|---------------|-----|------|
| ZD410 | 203 | 8 |
| ZD420 | 203 or 300 | 8 or 12 |
| ZD421 | 203 or 300 | 8 or 12 |
| ZD620 | 203 or 300 | 8 or 12 |
| ZT410 | 203, 300, or 600 | 8, 12, or 24 |
| ZT420 | 203, 300, or 600 | 8, 12, or 24 |

**Most common:** 203 DPI (8dpmm)

---

## Validation Checklist

Before making Labelary API request:

1. ✅ **Convert DPI to DPMM** using formula
2. ✅ **Round to nearest integer**
3. ✅ **Validate against [6, 8, 12, 24]**
4. ✅ **Use DPMM in URL**, not DPI
5. ✅ **Test with common DPI values** (203, 300)

---

## Testing

```typescript
// Test conversion
describe('DPI to DPMM conversion', () => {
    it('converts 203 DPI to 8 dpmm', () => {
        expect(Math.round(203 / 25.4)).toBe(8);
    });

    it('converts 300 DPI to 12 dpmm', () => {
        expect(Math.round(300 / 25.4)).toBe(12);
    });

    it('converts 600 DPI to 24 dpmm', () => {
        expect(Math.round(600 / 25.4)).toBe(24);
    });

    it('converts 152 DPI to 6 dpmm', () => {
        expect(Math.round(152 / 25.4)).toBe(6);
    });
});
```

---

## Why This Matters

**Incorrect DPMM causes:**
- ❌ HTTP 400 errors (API rejection)
- ❌ Wrong label preview size
- ❌ Mismatched dimensions
- ❌ Poor user experience

**Correct DPMM ensures:**
- ✅ Accurate label preview
- ✅ Correct sizing
- ✅ Printer compatibility
- ✅ No API errors

---

## Quick Reference

**Formula:**
```javascript
dpmm = Math.round(dpi / 25.4)
```

**Valid values:**
```
6dpmm, 8dpmm, 12dpmm, 24dpmm
```

**Most common:**
```
203 DPI → 8dpmm
300 DPI → 12dpmm
```

**Remember:**
- Always round
- Always validate
- Never use DPI directly in URL
- Always convert dynamically (don't hardcode)

---

## Related Documentation

- **Getting Started:** `categories/getting-started.md`
- **Parameters:** `categories/parameters.md`
- **Error Handling:** `patterns/error-handling.md`
- **Integration:** `patterns/integration.md`
