# Pattern 18: Asset Versioning

## Overview

Asset versioning ensures users always have the latest JavaScript/CSS after deployments by forcing a full page reload when assets change.

---

## How It Works

1. Server sends asset version hash with each response
2. On navigation, Inertia compares versions
3. If different, triggers full page reload instead of XHR swap

---

## Server Configuration

### HandleInertiaRequests

```php
// app/Http/Middleware/HandleInertiaRequests.php
public function version(Request $request): ?string
{
    return parent::version($request);
}
```

### Default Behavior

The default `parent::version()` uses:
- Vite: Hash of `public/build/manifest.json`
- Mix: Hash of `public/mix-manifest.json`

### Custom Version

```php
public function version(Request $request): ?string
{
    // Based on build manifest
    return md5_file(public_path('build/manifest.json'));

    // Based on deployment timestamp
    // return file_get_contents(base_path('.deployment_version'));

    // Based on git commit
    // return trim(exec('git rev-parse --short HEAD'));
}
```

---

## When Version Changes

When the server version differs from client:

1. Inertia detects mismatch
2. Forces full page reload
3. User gets fresh assets
4. Page state is lost (intentional)

---

## Vite Integration

Vite automatically generates unique file hashes:

```
build/
├── manifest.json
├── assets/
│   ├── app-abc123.js
│   └── app-def456.css
```

The manifest hash changes when any asset changes.

---

## Deployment Considerations

### Zero-Downtime Deploys

During deployment:
1. Old assets still served briefly
2. Version changes
3. Users get full reload on next navigation

### Cache Headers

Vite assets can be cached aggressively:

```nginx
location /build {
    add_header Cache-Control "public, max-age=31536000, immutable";
}
```

---

## Manual Version Trigger

Force version refresh programmatically:

```php
// After clearing cache
Artisan::call('view:clear');

// Touch manifest to change hash
touch(public_path('build/manifest.json'));
```

---

## Debugging

Check current version:

```tsx
import { usePage } from '@inertiajs/react';

function DebugVersion() {
  const { version } = usePage();
  console.log('Asset version:', version);
  return null;
}
```

---

## Next Steps

- **Progress Indicators** → Read `19-progress-indicators.md`
- **Error Handling** → Read `17-error-handling.md`
