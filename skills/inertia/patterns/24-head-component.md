# Pattern 24: Head Component

## Overview

The `<Head>` component manages document head elements (title, meta tags) from within your React components.

---

## Basic Usage

### Page Title

```tsx
import { Head } from '@inertiajs/react';

export default function Dashboard() {
  return (
    <>
      <Head title="Dashboard" />
      <div>Dashboard content</div>
    </>
  );
}
```

### Title Template

In `createInertiaApp`, define a title template:

```tsx
createInertiaApp({
  title: title => `${title} - My App`,
  // ...
});
```

Result: "Dashboard - My App"

---

## Meta Tags

```tsx
<Head>
  <title>My Page</title>
  <meta name="description" content="Page description for SEO" />
  <meta property="og:title" content="My Page" />
  <meta property="og:description" content="Share description" />
  <meta property="og:image" content="/images/og-image.jpg" />
</Head>
```

---

## Dynamic Content

```tsx
export default function UserProfile({ user }) {
  return (
    <>
      <Head>
        <title>{user.name}'s Profile</title>
        <meta name="description" content={`View ${user.name}'s profile`} />
      </Head>
      <div>{/* Profile content */}</div>
    </>
  );
}
```

---

## Multiple Head Components

Children are merged, later components override earlier:

```tsx
// Layout
function Layout({ children }) {
  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      {children}
    </>
  );
}

// Page - title overrides layout
function Page() {
  return (
    <>
      <Head title="Specific Page" />
      <div>Content</div>
    </>
  );
}
```

---

## Canonical URLs

```tsx
<Head>
  <link rel="canonical" href="https://example.com/page" />
</Head>
```

---

## Structured Data (JSON-LD)

```tsx
<Head>
  <script type="application/ld+json">
    {JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "My Company",
      "url": "https://example.com",
    })}
  </script>
</Head>
```

---

## Favicon

```tsx
<Head>
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="icon" type="image/png" href="/favicon.png" />
</Head>
```

---

## BudTags Pattern

```tsx
// In MainLayout
export default function MainLayout({ children, title }) {
  return (
    <>
      <Head>
        <title>{title || 'Budtags'}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div className="min-h-screen">
        <Navbar />
        <main>{children}</main>
      </div>
    </>
  );
}

// In Page
export default function PackagesIndex({ packages }) {
  return (
    <MainLayout title="Packages">
      <Head>
        <meta name="description" content="Manage your inventory packages" />
      </Head>
      <PackagesTable packages={packages} />
    </MainLayout>
  );
}
```

---

## Head Props vs Children

Two ways to set title:

```tsx
// Via prop (simpler)
<Head title="My Page" />

// Via children (more control)
<Head>
  <title>My Page</title>
  <meta name="description" content="..." />
</Head>
```

---

## SSR Considerations

Head elements work during SSR, rendering into `@inertiaHead` directive:

```blade
<!DOCTYPE html>
<html>
<head>
    @inertiaHead
</head>
<body>
    @inertia
</body>
</html>
```

---

## Next Steps

- **BudTags Integration** → Read `25-budtags-integration.md`
- **Pages & Components** → Read `04-pages-components.md`
