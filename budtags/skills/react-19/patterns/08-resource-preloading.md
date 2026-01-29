# React 19 Resource Preloading

New APIs for preloading resources to improve page load performance.

## Overview

React 19 introduces four preloading functions from `react-dom`:

```typescript
import { prefetchDNS, preconnect, preload, preinit } from 'react-dom';
```

| Function | Purpose | When to Use |
|----------|---------|-------------|
| `prefetchDNS` | DNS lookup | External domains you'll use later |
| `preconnect` | DNS + TCP + TLS | External domains with imminent requests |
| `preload` | Fetch resource | Fonts, styles, scripts needed soon |
| `preinit` | Fetch & execute | Scripts to run immediately |

---

## prefetchDNS

Perform DNS lookup ahead of time for external domains.

```typescript
import { prefetchDNS } from 'react-dom';

function App() {
  // DNS lookup for external API
  prefetchDNS('https://api.metrc.com');
  prefetchDNS('https://api.quickbooks.com');

  return <MainContent />;
}
```

**Generated HTML:**
```html
<link rel="dns-prefetch" href="https://api.metrc.com">
```

---

## preconnect

Establish early connection (DNS + TCP + TLS handshake).

```typescript
import { preconnect } from 'react-dom';

function App() {
  // Full connection to CDN
  preconnect('https://cdn.example.com');

  // With crossOrigin for fonts
  preconnect('https://fonts.googleapis.com', { crossOrigin: 'anonymous' });

  return <MainContent />;
}
```

**Generated HTML:**
```html
<link rel="preconnect" href="https://cdn.example.com">
<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin="anonymous">
```

---

## preload

Fetch a resource you know you'll need soon.

```typescript
import { preload } from 'react-dom';

function App() {
  // Preload font
  preload('https://fonts.example.com/font.woff2', {
    as: 'font',
    type: 'font/woff2',
    crossOrigin: 'anonymous'
  });

  // Preload CSS
  preload('/styles/critical.css', { as: 'style' });

  // Preload image
  preload('/images/hero.jpg', { as: 'image' });

  // Preload script (doesn't execute)
  preload('/scripts/analytics.js', { as: 'script' });

  return <MainContent />;
}
```

**Generated HTML:**
```html
<link rel="preload" href="/font.woff2" as="font" type="font/woff2" crossorigin="anonymous">
<link rel="preload" href="/styles/critical.css" as="style">
```

### Preload Options

```typescript
preload(href: string, options: {
  as: 'font' | 'style' | 'script' | 'image' | 'fetch';
  crossOrigin?: 'anonymous' | 'use-credentials';
  type?: string;        // MIME type
  nonce?: string;       // CSP nonce
  fetchPriority?: 'high' | 'low' | 'auto';
  imageSrcSet?: string; // For responsive images
  imageSizes?: string;
});
```

---

## preinit

Fetch AND execute a script or insert a stylesheet immediately.

```typescript
import { preinit } from 'react-dom';

function App() {
  // Load and execute script immediately
  preinit('https://cdn.example.com/critical.js', { as: 'script' });

  // Load and apply stylesheet immediately
  preinit('/styles/theme.css', { as: 'style' });

  return <MainContent />;
}
```

**Generated HTML:**
```html
<script async src="https://cdn.example.com/critical.js"></script>
<link rel="stylesheet" href="/styles/theme.css">
```

### preinit Options

```typescript
preinit(href: string, options: {
  as: 'script' | 'style';
  precedence?: string;     // For stylesheets (like 07-metadata)
  crossOrigin?: string;
  integrity?: string;      // SRI hash
  nonce?: string;
  fetchPriority?: 'high' | 'low' | 'auto';
});
```

---

## BudTags Examples

### External API Preconnection

```typescript
// In main layout or App component
function MainLayout({ children }) {
  // Preconnect to APIs we'll definitely use
  preconnect('https://api.metrc.com');
  preconnect('https://sandbox-api.metrc.com');

  // Preconnect to QuickBooks if organization uses it
  const { organization } = useOrganization();
  if (organization.hasQuickBooksIntegration) {
    preconnect('https://quickbooks.api.intuit.com');
  }

  return <div>{children}</div>;
}
```

### Label Preview Resources

```typescript
function LabelPreviewPage() {
  // Preload Labelary resources
  preconnect('https://api.labelary.com');
  preload('/fonts/zebra-barcode.woff2', {
    as: 'font',
    crossOrigin: 'anonymous'
  });

  return <LabelDesigner />;
}
```

### Conditional Preloading

```typescript
function PackageDetails({ pkg }) {
  // Only preload transfer resources if package can be transferred
  if (pkg.canTransfer) {
    preload('/js/transfer-modal.js', { as: 'script' });
  }

  // Preload test lab info if relevant
  if (pkg.requiresTesting) {
    preconnect('https://api.testinglab.com');
  }

  return <PackageInfo pkg={pkg} />;
}
```

---

## When to Use Each

### prefetchDNS
- External domains you might use
- Low priority, minimal cost
- Example: API domains that might be called

### preconnect
- External domains you will definitely use
- Higher priority than prefetchDNS
- Example: CDNs, required API endpoints

### preload
- Resources needed soon but not immediately
- Fonts, images above the fold
- Scripts that will run after initial render

### preinit
- Critical scripts that need to run ASAP
- Above-the-fold stylesheets
- Analytics that must load early

---

## Performance Tips

### Do Preload

```typescript
// ✅ Fonts used on every page
preload('/fonts/main.woff2', { as: 'font' });

// ✅ Critical CSS
preinit('/styles/critical.css', { as: 'style' });

// ✅ APIs that will definitely be called
preconnect('https://api.example.com');
```

### Don't Overuse

```typescript
// ❌ Don't preload everything
// This wastes bandwidth and hurts performance
preload('/image1.jpg', { as: 'image' });
preload('/image2.jpg', { as: 'image' });
preload('/image3.jpg', { as: 'image' });
// ... etc

// ✅ Only preload critical above-the-fold content
preload('/hero.jpg', { as: 'image' });
```

---

## Server-Side Rendering

In SSR, these functions generate `<link>` tags in the HTML head:

```typescript
// Component
function App() {
  prefetchDNS('https://api.example.com');
  preconnect('https://cdn.example.com');
  preload('/font.woff2', { as: 'font' });
  preinit('/critical.js', { as: 'script' });
  return <div>App</div>;
}

// Generated HTML <head>
<head>
  <link rel="dns-prefetch" href="https://api.example.com">
  <link rel="preconnect" href="https://cdn.example.com">
  <link rel="preload" href="/font.woff2" as="font">
  <script async src="/critical.js"></script>
</head>
```

## Next Steps

- Read `07-metadata-stylesheets.md` for stylesheet precedence
- Read `10-suspense-hydration.md` for loading patterns
