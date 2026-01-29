# Metrc API Object Limiting

## Overview

The Metrc API enforces **object limiting** to ensure reliable performance and fair usage for all users. This critical constraint limits the number of objects that can be submitted in a single API request.

**⚠️ CRITICAL CONSTRAINT:**
- **Maximum 10 objects per request** for all POST, PUT, and DELETE operations
- Exceeding this limit results in **HTTP 413 "Request Entity Too Large"** error
- Applies to any endpoint that accepts an array of objects in the request body

---

## The 10 Object Limit

### Which Endpoints Are Affected?

Any API endpoint that accepts an **array of objects** in the request body:

- `POST /packages/v1/create` - Creating multiple packages
- `POST /packages/v1/adjust` - Adjusting multiple packages
- `POST /plants/v1/create/plantings` - Creating multiple plants
- `POST /sales/v1/receipts` - Recording multiple sales receipts
- `PUT /packages/v1/item` - Changing item for multiple packages
- `DELETE /plants/v1/{ids}` - Destroying multiple plants
- And many more...

### HTTP 413 Error Response

When you exceed the 10 object limit, Metrc returns:

```http
HTTP/1.1 413 Request Entity Too Large
Content-Type: application/json

{
  "Message": "The content being submitted is too large"
}
```

---

## Chunking Strategy (Required for Bulk Operations)

To process more than 10 objects, you must **chunk** your requests into batches of 10 or fewer.

### Example: Creating 35 Packages

**❌ WRONG - Will fail with HTTP 413:**
```javascript
const packages = [...]; // 35 packages

await axios.post('/packages/v1/create', packages, {
  params: { licenseNumber: facility }
});
// ERROR: HTTP 413 - Request Entity Too Large
```

**✅ CORRECT - Chunk into batches of 10:**
```javascript
const packages = [...]; // 35 packages
const BATCH_SIZE = 10;

// Split into chunks
const chunks = [];
for (let i = 0; i < packages.length; i += BATCH_SIZE) {
  chunks.push(packages.slice(i, i + BATCH_SIZE));
}

// Process each chunk sequentially (to respect rate limits)
for (const chunk of chunks) {
  await axios.post('/packages/v1/create', chunk, {
    params: { licenseNumber: facility }
  });

  // Optional: Add delay between batches to avoid rate limiting
  await new Promise(resolve => setTimeout(resolve, 500));
}

// Result: 4 API calls (10 + 10 + 10 + 5 packages)
```

---

## Receiving Created Object IDs

**IMPORTANT:** When you make a successful POST request, Metrc now returns the newly created object IDs in the response.

### Response Format

```javascript
// Request: Create 3 packages
POST /packages/v1/create
[
  { Tag: "1A4000000000001", ... },
  { Tag: "1A4000000000002", ... },
  { Tag: "1A4000000000003", ... }
]

// Response: Array of created IDs (order preserved)
HTTP 200 OK
[12345, 12346, 12347]
```

**Key Points:**
- **Order is preserved** - IDs correspond to the order of objects in your request
- Eliminates need for follow-up GET requests to find created records
- Available for all POST endpoints that create new records

### Example: Tracking Created Packages

```javascript
const packagesTo Create = [
  { Tag: "1A4000000000001", Item: "Flower", Quantity: 10, ... },
  { Tag: "1A4000000000002", Item: "Edible", Quantity: 5, ... },
  { Tag: "1A4000000000003", Item: "Concentrate", Quantity: 2, ... }
];

const response = await axios.post('/packages/v1/create', packagesToCreate, {
  params: { licenseNumber: facility }
});

// response.data = [12345, 12346, 12347]
const createdIds = response.data;

// Map tags to IDs
const tagToId = packagesToCreate.map((pkg, i) => ({
  tag: pkg.Tag,
  metrcId: createdIds[i]
}));

console.log(tagToId);
// [
//   { tag: "1A4000000000001", metrcId: 12345 },
//   { tag: "1A4000000000002", metrcId: 12346 },
//   { tag: "1A4000000000003", metrcId: 12347 }
// ]
```

---

## Error Handling Best Practices

### Handle HTTP 413 Gracefully

```javascript
async function createPackagesSafely(packages, facility) {
  const BATCH_SIZE = 10;
  const createdIds = [];

  try {
    // Split into chunks
    const chunks = [];
    for (let i = 0; i < packages.length; i += BATCH_SIZE) {
      chunks.push(packages.slice(i, i + BATCH_SIZE));
    }

    // Process each chunk
    for (const chunk of chunks) {
      const response = await axios.post('/packages/v1/create', chunk, {
        params: { licenseNumber: facility }
      });

      createdIds.push(...response.data);

      // Add delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    return { success: true, ids: createdIds };

  } catch (error) {
    if (error.response?.status === 413) {
      // This should never happen with proper chunking, but handle it anyway
      throw new Error('Request too large - reduce batch size below 10 objects');
    }

    throw error;
  }
}
```

---

## Common Pitfalls

### 1. Forgetting to Chunk Large Datasets

**Problem:**
```javascript
// User wants to create 100 packages at once
const packages = generatePackages(100);
await createPackages(packages); // ❌ Will fail with HTTP 413
```

**Solution:**
Always check array length before making requests:
```javascript
if (packages.length > 10) {
  // Must chunk into batches
  return await createPackagesSafely(packages, facility);
} else {
  // Can send directly
  return await axios.post('/packages/v1/create', packages, {
    params: { licenseNumber: facility }
  });
}
```

### 2. Not Handling Partial Success

**Problem:**
If you're chunking 35 packages (4 batches), and batch 3 fails, what happens to batches 1 and 2?

**Solution:**
Implement transactional rollback or partial success handling:
```javascript
const results = [];
const failures = [];

for (let i = 0; i < chunks.length; i++) {
  try {
    const response = await axios.post('/packages/v1/create', chunks[i], {
      params: { licenseNumber: facility }
    });

    results.push({
      batch: i + 1,
      ids: response.data,
      success: true
    });
  } catch (error) {
    failures.push({
      batch: i + 1,
      error: error.message,
      packages: chunks[i]
    });

    // Decision: Continue or stop?
    if (stopOnFirstError) break;
  }
}

return { results, failures };
```

### 3. Not Accounting for Rate Limits

**Problem:**
Chunking helps with object limits, but you can still hit rate limits if you send chunks too fast.

**Solution:**
Add delays between batches and handle 429 responses:
```javascript
for (const chunk of chunks) {
  try {
    await axios.post('/packages/v1/create', chunk, {
      params: { licenseNumber: facility }
    });

    // Wait 500ms between batches
    await new Promise(resolve => setTimeout(resolve, 500));

  } catch (error) {
    if (error.response?.status === 429) {
      // Rate limit hit - wait for Retry-After header
      const retryAfter = parseInt(error.response.headers['retry-after'] || 60);
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));

      // Retry this chunk
      // ... (implement retry logic)
    }
  }
}
```

---

## Performance Implications

### API Call Overhead

When chunking, you trade object limit compliance for increased API calls:

| Objects | Without Chunking | With Chunking (10 max) | Overhead |
|---------|------------------|------------------------|----------|
| 10      | 1 API call       | 1 API call             | 0%       |
| 50      | 1 API call ❌    | 5 API calls ✅         | 400%     |
| 100     | 1 API call ❌    | 10 API calls ✅        | 900%     |

**Impact:**
- More API calls = more time (network latency per call)
- More API calls = higher rate limit risk
- But required for compliance with Metrc's object limiting

### Optimization Strategies

1. **Batch Smartly**: Group related operations (e.g., all packages for same harvest)
2. **Parallel Requests**: If rate limits allow, consider parallel batches (use with caution)
3. **Cache Results**: Avoid redundant operations by caching created IDs
4. **Use Webhooks**: Reduce polling needs (if your tier supports it)

---

## Related Patterns

- **[Rate Limiting](./rate-limiting.md)** - Handle 429 responses and Retry-After headers
- **[Error Handling](./error-handling.md)** - Comprehensive error handling strategies
- **[Batch Operations](./batch-operations.md)** - General batch processing patterns

---

## Quick Reference

```
✅ DO:
- Chunk arrays into batches of 10 or fewer
- Handle HTTP 413 errors gracefully
- Add delays between batches to avoid rate limits
- Track created IDs from POST responses
- Implement partial success handling

❌ DON'T:
- Send more than 10 objects in a single request
- Ignore HTTP 413 errors
- Send batches too quickly (rate limits)
- Assume all objects succeed or fail together
```
