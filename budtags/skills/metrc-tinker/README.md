# Metrc Tinker - Live API Explorer

Query any Metrc API endpoint via Laravel Tinker without writing code.

## Purpose

This skill provides patterns for:
- Setting up Metrc API access in Tinker
- Querying ANY endpoint using reflection
- Exploring response data structures
- Testing parameters before implementation

## Companion Skill

Use **metrc-api** skill for:
- Complete endpoint documentation (258 endpoints)
- Request/response formats
- Implementation patterns in Laravel

Use **metrc-tinker** skill for:
- Live testing and exploration
- Quick data inspection
- Parameter discovery

## Quick Example

```php
// Setup (once per session)
$org = \App\Models\Organization::whereHas('secrets', fn($q) =>
    $q->where('secret_type_id', \App\Models\SecretType::lookup('Metrc'))
      ->where('is_active', true)
)->first();

$user = $org->users()->first();
$user->update(['active_org_id' => $org->id]);
$user->refresh();

$api = (new \App\Services\Api\MetrcApi)->set_user($user);
$ref = new \ReflectionClass($api);
$get = $ref->getMethod('get');

$facility = \App\Models\MetrcFacility::where('organization_id', $org->id)->first();
$license = $facility->license_recreational ?: $facility->license_medical;

// Query any endpoint
$response = $get->invoke($api, '/packages/v2/active', ['licenseNumber' => $license]);
$response->json('Data');
```

## Security Note

This skill contains NO sensitive data (credentials, org IDs, licenses). All values must be retrieved from the database at runtime.

## Files

- `SKILL.md` - Complete usage guide with all endpoint patterns

## Version

1.0.0 - Initial release

**Last Updated**: 2026-01-31
