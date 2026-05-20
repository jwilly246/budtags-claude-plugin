# Sandbox Category

**Collection File**: `collections/metrc-sandbox.postman_collection.json`
**Total Endpoints**: 3
**License Compatibility**: Sandbox environment only. All endpoints return an error in production.

---

## POST Endpoints

- `POST /sandbox/v2/integrator/setup?userKey={userKey}` - Provision the integrator's sandbox facilities
  - Use case: One-time integrator onboarding to seed initial sandbox facilities and tags
  - Authenticated via `userKey` query param (not `licenseNumber`)

- `POST /sandbox/v2/facility/tags?licenseNumber={license}` - Generate tags on demand for a sandbox facility
  - **Bulletin 233** (effective 2026-04-23)
  - Body: `{ "TagType": "Marijuana Package", "Count": 100 }`. One tag type per call, max 1,000 per call.
  - Tags are created, shipped, and received synchronously, so they are immediately usable for packages/plant batches.
  - Response: `{ "TagType": "...", "Count": N, "Labels": ["1A4...001", "1A4...002", ...] }`
  - Validates `TagType` against the facility's license type (case-insensitive)
  - Discover valid `TagType` values via `GET /sandbox/v2/tagtypes` (below)

## GET Endpoints

- `GET /sandbox/v2/tagtypes?licenseNumber={license}` - List tag types available for a sandbox facility
  - **Bulletin 233** (effective 2026-04-23)
  - Use case: Validate `TagType` strings before calling `POST /sandbox/v2/facility/tags`
  - Response: list of `{ Id, Name, SkuNumber, MaxGroupSize, TagInventoryType }` objects
  - `TagInventoryType` is either `"Package"` or `"Plant"`. Common `Name` values include `"Marijuana Package"`, `"Marijuana Plant"`, `"Cannabis Package"`, `"Medical Package"`, `"Medical Plant"`, `"Hemp Package"`, `"Hemp Plant"`.

---

## Examples

### Discover valid tag types

```php
abort_unless($api->isSandbox(), 500, 'Sandbox only.');

$tag_types = $api->get('/sandbox/v2/tagtypes', ['licenseNumber' => $license])->json();
// [ { Id: 1, Name: "Marijuana Package", TagInventoryType: "Package", ... }, ... ]
```

### Generate package tags on demand

```php
abort_unless($api->isSandbox(), 500, 'Sandbox only.');

$result = $api->post(
    "/sandbox/v2/facility/tags?licenseNumber={$license}",
    ['TagType' => 'Marijuana Package', 'Count' => 100],
)->json();

// $result['Labels'] now contains 100 tag strings ready to use
```

### BudTags service wrappers

```php
$api->sandbox_tag_types($license);                                // list of tag types
$api->sandbox_generate_tags($license, 'Marijuana Package', 100);  // generate + clear tag caches
```

---

## Important Notes

- **Sandbox-only.** Calling these against production returns an error.
- **One `TagType` per request.** If you need both package and plant tags, send two POSTs.
- **Max 1,000 tags per request.** Per-type on-hand limits may further cap availability based on facility configuration.
- After generating tags, the regular `/tags/v2/package/available` and `/tags/v2/plant/available` caches should be invalidated so the new labels appear in BudTags' tag pickers.
- Requires a completed integrator sandbox setup (`POST /sandbox/v2/integrator/setup`) and a facility accessible to the integrator with an associated employee record.

---

## Related

- `categories/tags.md` - The standard (non-sandbox) tag availability endpoints
- `scenarios/replace-plant-tags.md` - Tag replacement workflow
- `patterns/authentication.md` - Integrator setup prerequisites
