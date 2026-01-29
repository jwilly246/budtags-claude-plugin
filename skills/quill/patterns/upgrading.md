# Upgrading to Quill 2.0

Migration guide for upgrading from Quill v1.x to v2.0 with breaking changes and new features.

---

## Overview

Quill 2.0 introduces significant improvements including TypeScript support, embedded SVG icons, and various API refinements. This guide covers breaking changes and migration steps.

**Official Documentation**: https://quilljs.com/docs/upgrading-to-2-0

---

## Major Changes Summary

| Change | v1.x | v2.0 | Impact |
|--------|------|------|--------|
| **TypeScript** | Separate @types package | Built-in types | Remove @types/quill |
| **Icons** | External SVG files | Embedded in JS | Remove bundler SVG config |
| **Configuration** | `strict` option | Removed | Update config |
| **Configuration** | - | `registry` option added | New feature |
| **Clipboard** | `convert()` API | Changed signature | Update calls |
| **Keyboard** | Case-insensitive | Case-sensitive | Update bindings |
| **Parchment** | List formatting | Changed markup | May affect custom styles |
| **Delta** | Some methods | Deprecated | Use alternatives |
| **IE Support** | Supported | Dropped | Modern browsers only |

---

## TypeScript Support

### Before (v1.x)

```bash
npm install quill
npm install --save-dev @types/quill
```

```typescript
import Quill from 'quill';
// Types from @types/quill
```

### After (v2.0)

```bash
npm install quill
# No @types package needed!
```

```typescript
import Quill from 'quill';
// Types included in quill package
```

**Action Required**:
1. Remove `@types/quill` from package.json dependencies
2. Run `npm uninstall @types/quill`
3. Update imports if using type-only imports

```typescript
// ✅ v2.0 - Types included
import Quill from 'quill';
import type { QuillOptions, Range } from 'quill';

const options: QuillOptions = {
  theme: 'snow'
};

const quill = new Quill('#editor', options);
```

---

## SVG Icons Embedded

### Before (v1.x)

Bundler configuration required for SVG imports:

```javascript
// Webpack config
module.exports = {
  module: {
    rules: [
      {
        test: /\.svg$/,
        use: ['html-loader']
      }
    ]
  }
};
```

### After (v2.0)

Icons are embedded in JavaScript bundle - no bundler configuration needed!

**Action Required**:
1. Remove SVG loader configuration from bundler config
2. Remove any SVG-specific webpack/rollup rules
3. Icons work out of the box

```javascript
// ✅ No special configuration needed
import Quill from 'quill';

const quill = new Quill('#editor', {
  theme: 'snow' // Icons work automatically
});
```

---

## Configuration Changes

### Removed: `strict` Option

The `strict` option has been removed.

```javascript
// ❌ v1.x
const quill = new Quill('#editor', {
  strict: false
});

// ✅ v2.0
const quill = new Quill('#editor', {
  // strict option removed
});
```

**Action Required**: Remove `strict` from configuration objects.

### Added: `registry` Option

New option for custom format registries.

```javascript
// ✅ v2.0 - New feature
import Quill from 'quill';
const Parchment = Quill.import('parchment');

const registry = new Parchment.Registry();
registry.register(Parchment.Scroll);
registry.register(Parchment.Block);
// ... register other formats

const quill = new Quill('#editor', {
  registry: registry
});
```

**See Also**: `patterns/registries.md` for complete registry documentation.

### Removed: `scrollingContainer` Option

The `scrollingContainer` option has been removed.

```javascript
// ❌ v1.x
const quill = new Quill('#editor', {
  scrollingContainer: '#scrolling-element'
});

// ✅ v2.0
const quill = new Quill('#editor', {
  // scrollingContainer removed
  // Use CSS overflow on container instead
});
```

**Action Required**:
1. Remove `scrollingContainer` option
2. Apply scrolling via CSS on container element:

```css
#editor-container {
  overflow-y: auto;
  max-height: 400px;
}
```

---

## Clipboard Module API Changes

### `convert()` Method Signature

**Before (v1.x)**:
```javascript
const delta = quill.clipboard.convert(html);
```

**After (v2.0)**:
```javascript
const delta = quill.clipboard.convert({ html: html });
```

**Complete Example**:

```javascript
// ❌ v1.x
const htmlContent = '<p>Hello <strong>world</strong></p>';
const delta = quill.clipboard.convert(htmlContent);
quill.setContents(delta);

// ✅ v2.0
const htmlContent = '<p>Hello <strong>world</strong></p>';
const delta = quill.clipboard.convert({ html: htmlContent });
quill.setContents(delta);
```

**Action Required**: Update all `clipboard.convert()` calls to pass object with `html` property.

### Text Conversion

```javascript
// ✅ v2.0 - Convert plain text
const delta = quill.clipboard.convert({ text: 'Plain text content' });

// ✅ v2.0 - Convert HTML
const delta = quill.clipboard.convert({ html: '<p>HTML content</p>' });
```

---

## Keyboard Module Changes

### Case-Sensitive Bindings

Keyboard bindings are now case-sensitive for the `key` property.

**Before (v1.x)**:
```javascript
// Case-insensitive
modules: {
  keyboard: {
    bindings: {
      custom: {
        key: 'B', // Accepted
        shortKey: true,
        handler: function() { /* ... */ }
      }
    }
  }
}
```

**After (v2.0)**:
```javascript
// Case-sensitive - use lowercase
modules: {
  keyboard: {
    bindings: {
      custom: {
        key: 'b', // Must be lowercase
        shortKey: true,
        handler: function() { /* ... */ }
      }
    }
  }
}
```

**Action Required**: Convert all `key` values in keyboard bindings to lowercase.

**Migration Example**:
```javascript
// ❌ v1.x
bindings: {
  bold: { key: 'B', shortKey: true, handler: boldHandler },
  italic: { key: 'I', shortKey: true, handler: italicHandler }
}

// ✅ v2.0
bindings: {
  bold: { key: 'b', shortKey: true, handler: boldHandler },
  italic: { key: 'i', shortKey: true, handler: italicHandler }
}
```

**See Also**: `categories/keyboard-module.md` for complete keyboard documentation.

---

## Parchment Changes

### List Formatting Markup

List item markup has changed in v2.0.

**Before (v1.x)**:
```html
<ul>
  <li data-list="bullet">Item 1</li>
  <li data-list="bullet">Item 2</li>
</ul>
```

**After (v2.0)**:
```html
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
</ul>
```

**Impact**:
- Custom CSS targeting `data-list` attribute may break
- List styles now applied to `<li>` element directly

**Action Required**: Update custom CSS selectors:

```css
/* ❌ v1.x */
li[data-list="bullet"] {
  list-style-type: disc;
}

/* ✅ v2.0 */
ul > li {
  list-style-type: disc;
}
```

### Code Block Formatting

Code block structure has changed.

**Before (v1.x)**:
```html
<pre data-language="javascript">
  <code>const x = 1;</code>
</pre>
```

**After (v2.0)**:
```html
<div class="ql-code-block-container">
  <pre class="ql-code-block">const x = 1;</pre>
</div>
```

**Action Required**: Update CSS targeting code blocks:

```css
/* ❌ v1.x */
pre[data-language] {
  background: #f5f5f5;
}

/* ✅ v2.0 */
.ql-code-block-container .ql-code-block {
  background: #f5f5f5;
}
```

### Parchment Exports

Some Parchment exports have moved or been renamed.

```javascript
// ❌ v1.x
const Parchment = Quill.import('parchment');
const Inline = Parchment.Inline;

// ✅ v2.0 - Import directly from parchment package
import { Inline } from 'parchment';

// OR use Quill.import
const Inline = Quill.import('parchment').Inline;
```

**See Also**: `guides/parchment-blots.md` for custom format creation.

---

## Delta Deprecations

Some Delta methods are deprecated in v2.0.

### Deprecated Methods

| Method | Status | Alternative |
|--------|--------|-------------|
| `delta.concat()` | Deprecated | `delta.compose()` |
| `delta.diff()` | Deprecated | Use operational transform library |
| `delta.transform()` | Deprecated | Use operational transform library |

**Migration Example**:

```javascript
// ❌ v1.x - concat deprecated
const combined = delta1.concat(delta2);

// ✅ v2.0 - use compose
const combined = delta1.compose(delta2);
```

**Action Required**: Replace deprecated methods with recommended alternatives.

**See Also**: `categories/delta.md` for Delta documentation.

---

## Internet Explorer Support Dropped

Quill 2.0 **does not support Internet Explorer**.

**Supported Browsers**:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile Safari (iOS 11+)
- Chrome Mobile (Android)

**Action Required**:
- Remove IE polyfills if only used for Quill
- Update browser support documentation
- Consider staying on v1.x if IE support is required

---

## Migration Checklist

### Package Updates

- [ ] Update `quill` to v2.0+ in package.json
- [ ] Remove `@types/quill` from dependencies
- [ ] Run `npm install` or `yarn install`

### Code Updates

- [ ] Remove `strict` option from config
- [ ] Remove `scrollingContainer` option from config
- [ ] Update `clipboard.convert()` calls to use object syntax
- [ ] Convert keyboard binding keys to lowercase
- [ ] Remove bundler SVG loader configuration

### CSS Updates

- [ ] Update selectors targeting `data-list` attributes
- [ ] Update code block CSS selectors
- [ ] Test custom theme styles

### Testing

- [ ] Test all editor instances
- [ ] Verify toolbar functionality
- [ ] Test keyboard shortcuts
- [ ] Test clipboard paste operations
- [ ] Verify list formatting displays correctly
- [ ] Test code blocks with syntax highlighting

---

## Example: Complete Migration

### Before (v1.x)

```javascript
import Quill from 'quill';
import '@types/quill';

const quill = new Quill('#editor', {
  theme: 'snow',
  strict: false,
  scrollingContainer: '#container',
  modules: {
    toolbar: [...],
    keyboard: {
      bindings: {
        bold: { key: 'B', shortKey: true }
      }
    }
  }
});

// Convert HTML
const delta = quill.clipboard.convert('<p>Test</p>');
```

### After (v2.0)

```javascript
import Quill from 'quill';
// No @types import needed

const quill = new Quill('#editor', {
  theme: 'snow',
  // strict removed
  // scrollingContainer removed
  modules: {
    toolbar: [...],
    keyboard: {
      bindings: {
        bold: { key: 'b', shortKey: true } // lowercase
      }
    }
  }
});

// Convert HTML with object syntax
const delta = quill.clipboard.convert({ html: '<p>Test</p>' });
```

### CSS Updates

```css
/* Before (v1.x) */
li[data-list="bullet"] {
  list-style-type: disc;
}

pre[data-language="javascript"] {
  background: #f5f5f5;
}

/* After (v2.0) */
ul > li {
  list-style-type: disc;
}

.ql-code-block-container .ql-code-block {
  background: #f5f5f5;
}

/* Add scrolling via CSS instead of scrollingContainer option */
#editor-container {
  overflow-y: auto;
  max-height: 400px;
}
```

---

## New Features in v2.0

While upgrading, consider adopting these new features:

### Registry Support

Create editors with different format sets:

```javascript
import Quill from 'quill';
const Parchment = Quill.import('parchment');

const limitedRegistry = new Parchment.Registry();
// Register only needed formats

const quill = new Quill('#editor', {
  registry: limitedRegistry
});
```

**See**: `patterns/registries.md`

### Better TypeScript Support

```typescript
import Quill from 'quill';
import type { QuillOptions, DeltaStatic, Sources } from 'quill';

const handleTextChange = (
  delta: DeltaStatic,
  oldDelta: DeltaStatic,
  source: Sources
) => {
  // Fully typed parameters
};

quill.on('text-change', handleTextChange);
```

---

## Getting Help

### Common Issues

**Build errors after upgrade**:
- Clear node_modules and reinstall
- Clear bundler cache (webpack, vite, etc.)
- Update bundler configuration

**Styles not working**:
- Ensure correct stylesheet is imported (quill.snow.css)
- Update custom CSS selectors for new markup
- Check browser console for errors

**TypeScript errors**:
- Remove @types/quill completely
- Restart TypeScript server
- Update import statements

---

## Related Files

- **Configuration**: See `categories/configuration.md` for v2.0 options
- **Clipboard**: See `categories/clipboard-module.md` for convert() usage
- **Keyboard**: See `categories/keyboard-module.md` for bindings
- **Registries**: See `patterns/registries.md` for new registry feature

---

## Official Resources

- **Upgrade Guide**: https://quilljs.com/docs/upgrading-to-2-0
- **Changelog**: https://github.com/slab/quill/blob/main/CHANGELOG.md
- **Release Notes**: https://github.com/slab/quill/releases/tag/v2.0.0
- **Migration Issues**: https://github.com/slab/quill/issues
