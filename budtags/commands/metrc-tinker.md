# Metrc Tinker - Live API Explorer

Query any Metrc API endpoint via Laravel Tinker without writing code.

## Your Mission

Help the user:
1. Set up Metrc API access in Tinker
2. Query any endpoint to explore data structures
3. Test parameters before implementing
4. Debug API integration issues

## Instructions

### Step 1: Load the Skill

Read the main skill file:
```
Read: .claude/skills/metrc-tinker/SKILL.md
```

### Step 2: Help User Set Up

Provide the setup snippet:

```php
// Get org with Metrc credentials
$org = \App\Models\Organization::whereHas('secrets', fn($q) =>
    $q->where('secret_type_id', \App\Models\SecretType::lookup('Metrc'))
      ->where('is_active', true)
)->first();

// Get user and set active org
$user = \App\Models\User::where('active_org_id', $org->id)->first() ?: $org->users()->first();
$user->update(['active_org_id' => $org->id]);
$user->refresh();

// Get license
$facility = \App\Models\MetrcFacility::where('organization_id', $org->id)->first();
$license = $facility->license_recreational ?: $facility->license_medical;

// Create API instance with reflection
$api = (new \App\Services\Api\MetrcApi)->set_user($user);
$ref = new \ReflectionClass($api);
$get = $ref->getMethod('get');
$post = $ref->getMethod('post');

echo "Ready! License: {$license}\n";
```

### Step 3: Query Endpoints

Help user query their desired endpoint:

```php
// Generic pattern
$response = $get->invoke($api, '{endpoint}', [
    'licenseNumber' => $license,
    // Additional params
]);

$response->json('Data');
```

## Critical Reminders

### License Type Restrictions
- **AU-C** (Cultivation): Can access plants, harvests, packages
- **AU-P** (Processing): Can access packages, items, processing jobs - NO plants
- **AU-R** (Retail): Can access sales, packages - NO plants

### Rate Limiting
Add `usleep(200000)` between calls when looping.

## Companion Skill

For endpoint documentation, use the **metrc-api** skill:
```
Read: .claude/skills/metrc-api/SKILL.md
```

Now load the skill and help the user explore Metrc data!
