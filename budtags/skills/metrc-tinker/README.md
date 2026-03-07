# Metrc Tinker - Live API Explorer

Query any Metrc API endpoint via `mcp__laravel-boost__tinker` without writing code.

## Purpose

This skill provides patterns for:
- Setting up Metrc API access via the MCP tinker tool
- Querying endpoints using MetrcApi's **147 public methods** (preferred)
- Raw endpoint access via Reflection (fallback for unwrapped endpoints)
- Exploring response data structures
- Testing parameters before implementation

## Companion Skill

Use **metrc-api** skill for:
- Complete endpoint documentation (258 endpoints)
- Request/response formats
- Implementation patterns in Laravel

Use **metrc-tinker** skill for:
- Live testing and exploration via MCP tinker
- Quick data inspection
- Parameter discovery

## Quick Example

```php
// Via mcp__laravel-boost__tinker

// Setup
$org = \App\Models\Organization::whereHas('secrets', fn($q) =>
    $q->where('secret_type_id', \App\Models\SecretType::lookup('Metrc'))
      ->where('is_active', true)
)->first();

$user = $org->users()->first();
$user->update(['active_org_id' => $org->id]);
$user->refresh();

$api = (new \App\Services\Api\MetrcApi)->set_user($user);
$facility = \App\Models\MetrcFacility::where('organization_id', $org->id)->first();

// Use public methods (preferred)
return $api->strains($facility->name);
```

## Key Changes in v2.0.0

- **Use MCP tinker tool** (`mcp__laravel-boost__tinker`), not `php artisan tinker`
- **Public methods first** — MetrcApi has 147 public methods with caching/rate limiting
- **Reflection as fallback** — only for endpoints without public method wrappers
- **Removed redundant endpoint catalog** — use `metrc-api` skill for that
- **Added day-based queries, bulk cache, search, and mutation examples**

## Security Note

This skill contains NO sensitive data (credentials, org IDs, licenses). All values must be retrieved from the database at runtime.

## Files

- `SKILL.md` - Complete usage guide with public method patterns

## Version

2.0.0 - Rewritten to use public methods + MCP tinker tool

**Last Updated**: 2026-03-05
