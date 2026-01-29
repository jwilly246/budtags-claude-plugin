# Sandbox Category

**Collection File**: `collections/metrc-sandbox.postman_collection.json`
**Total Endpoints**: 1
**License Compatibility**: Testing environment only

---

## POST Endpoints

- `POST /sandbox/v2/clear` - Clear all sandbox data
  - ⚠️ **TESTING ENVIRONMENT ONLY**
  - Use case: Reset sandbox to clean state for testing
  - **DO NOT use in production!**

---

## Example

```php
// ONLY in testing/sandbox environment!
if (config('app.env') === 'sandbox') {
    $api->post("/sandbox/v2/clear?licenseNumber={$license}", []);
    echo "Sandbox data cleared";
}
```

---

## ⚠️ CRITICAL WARNING

**This endpoint DELETES ALL DATA in the sandbox environment.**
- Never use in production
- Use for automated testing resets
- Clears all packages, plants, harvests, sales, etc.

---

## Related

- Use for integration testing
- Reset between test runs
- Ensure clean test state
