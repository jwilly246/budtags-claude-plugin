# React 19 Document Metadata & Stylesheets

React 19 supports rendering metadata tags and managing stylesheets directly in components.

## Document Metadata

Render `<title>`, `<meta>`, and `<link>` tags anywhere in your component tree - React hoists them to `<head>`.

### Basic Usage

```typescript
function BlogPost({ post }) {
  return (
    <article>
      {/* These are hoisted to <head> automatically */}
      <title>{post.title}</title>
      <meta name="author" content={post.author} />
      <meta name="description" content={post.excerpt} />
      <meta name="keywords" content={post.tags.join(', ')} />
      <link rel="canonical" href={`https://example.com/posts/${post.slug}`} />

      {/* Actual content */}
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}
```

### Supported Tags

- `<title>` - Document title
- `<meta>` - Meta tags (description, keywords, og:*, etc.)
- `<link>` - Link tags (canonical, author, etc.)

---

## BudTags Context: Inertia Head

**Note:** BudTags uses Inertia.js which has its own `<Head>` component for metadata:

```typescript
import { Head } from '@inertiajs/react';

function PackagesPage() {
  return (
    <>
      <Head title="Packages" />
      <div>Content...</div>
    </>
  );
}
```

**Recommendation:** Continue using Inertia's `<Head>` for:
- Page titles
- Meta tags that Inertia manages

React 19's metadata support is more useful for:
- Server Components (not used in BudTags)
- Non-Inertia pages
- Third-party component libraries

---

## Stylesheet Support

React 19 can manage stylesheet loading with the `precedence` attribute.

### Precedence Attribute

```typescript
function Component() {
  return (
    <>
      <link rel="stylesheet" href="base.css" precedence="default" />
      <link rel="stylesheet" href="theme.css" precedence="high" />
      <div className="themed">Content</div>
    </>
  );
}
```

### How Precedence Works

```typescript
function ComponentA() {
  return (
    <>
      <link rel="stylesheet" href="a.css" precedence="default" />
      <link rel="stylesheet" href="c.css" precedence="high" />
      <div>A</div>
    </>
  );
}

function ComponentB() {
  return (
    <>
      <link rel="stylesheet" href="b.css" precedence="default" />
      <div>B</div>
    </>
  );
}

// Result in <head>:
// <link href="a.css" />  (default, first)
// <link href="b.css" />  (default, second)
// <link href="c.css" />  (high, last)
```

### Features

1. **Deduplication:** Same href loaded once even if rendered multiple times
2. **Ordering:** Controlled by precedence level
3. **Suspense Integration:** Content waits for stylesheet to load

### With Suspense

```typescript
function LazyStyledComponent() {
  return (
    <Suspense fallback={<Skeleton />}>
      <link rel="stylesheet" href="component.css" precedence="default" />
      <div className="styled">
        Content only shows after CSS loads
      </div>
    </Suspense>
  );
}
```

---

## Async Scripts

Render async scripts anywhere - React handles deduplication:

```typescript
function AnalyticsWrapper({ children }) {
  return (
    <>
      <script async src="https://analytics.example.com/script.js" />
      {children}
    </>
  );
}

function App() {
  return (
    <>
      {/* Even if used multiple times, script loads once */}
      <AnalyticsWrapper>
        <Page1 />
      </AnalyticsWrapper>
      <AnalyticsWrapper>
        <Page2 />
      </AnalyticsWrapper>
    </>
  );
}
```

### Script Loading Order

In SSR, async scripts are:
1. Deprioritized behind critical resources
2. Loaded after stylesheets
3. Deduplicated across components

---

## BudTags Examples

### Dynamic OG Tags (If not using Inertia Head)

```typescript
function ProductPage({ product }) {
  return (
    <>
      <title>{product.name} | BudTags</title>
      <meta property="og:title" content={product.name} />
      <meta property="og:description" content={product.description} />
      <meta property="og:image" content={product.imageUrl} />

      <ProductDetails product={product} />
    </>
  );
}
```

### Component-Specific Styles

```typescript
function RichTextEditor({ content }) {
  return (
    <>
      {/* Only loaded when this component renders */}
      <link
        rel="stylesheet"
        href="/css/rich-text-editor.css"
        precedence="default"
      />
      <div className="rich-text-editor">
        {content}
      </div>
    </>
  );
}
```

### Third-Party Scripts

```typescript
function LabelPrinter() {
  return (
    <>
      {/* Labelary preview script */}
      <script async src="https://labelary.com/viewer.js" />
      <div id="label-preview">
        {/* Label content */}
      </div>
    </>
  );
}
```

---

## When to Use

| Feature | Use When |
|---------|----------|
| `<title>` in component | Not using Inertia Head, Server Components |
| `<meta>` tags | Dynamic SEO, OG tags for shares |
| `<link>` stylesheets | Component-specific CSS, lazy-loaded styles |
| `<script async>` | Third-party scripts, analytics |

## Comparison with Inertia

| Feature | Inertia Head | React 19 Native |
|---------|--------------|-----------------|
| Page title | ✅ Preferred | Works |
| Meta tags | ✅ Preferred | Works |
| Dynamic per-component | Limited | ✅ Better |
| Stylesheet management | No | ✅ Yes |
| Script deduplication | No | ✅ Yes |

---

## Limitations

- Libraries like `react-helmet` may still offer more advanced features
- For BudTags, Inertia's `<Head>` is usually sufficient
- Stylesheet precedence is mainly useful for CSS-in-JS or component libraries

## Next Steps

- Read `08-resource-preloading.md` for preloading APIs
- Read `10-suspense-hydration.md` for Suspense integration
