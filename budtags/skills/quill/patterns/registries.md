# Quill Registries

Advanced format registration for multiple editor instances with different format sets.

---

## Overview

By default, `Quill.register()` applies formats globally to all editor instances on a page. Registries enable per-instance format customization, allowing different editors to support different formatting capabilities.

**Official Documentation**: https://quilljs.com/docs/registries

---

## The Problem

Global registration affects all Quill instances:

```javascript
// This affects EVERY Quill instance on the page
Quill.register('formats/custom', CustomFormat);

const editor1 = new Quill('#editor1'); // Has CustomFormat
const editor2 = new Quill('#editor2'); // Also has CustomFormat (no way to exclude it)
```

**Limitation**: Cannot create multiple editors with different format capabilities.

**Use Case**: An application might need:
- A full-featured editor for admins
- A restricted editor for regular users
- Different format sets for different content types

---

## The Solution: Custom Registries

Create separate registries for each editor instance using Parchment:

```javascript
import Quill from 'quill';
const Parchment = Quill.import('parchment');

// Create custom registry for limited editor
const limitedRegistry = new Parchment.Registry();

// Register only essential formats
limitedRegistry.register(Parchment.Scroll);
limitedRegistry.register(Parchment.Block);
limitedRegistry.register(Parchment.Inline);
limitedRegistry.register(Parchment.Text);

// Create editor with limited registry
const limitedEditor = new Quill('#limited', {
  registry: limitedRegistry,
  theme: 'snow'
});

// Create editor with full default registry
const fullEditor = new Quill('#full', {
  theme: 'snow'
});
```

**Result**:
- `limitedEditor` has only basic formatting
- `fullEditor` has all default Quill formats

---

## Essential Parchment Formats

Every registry must include these core formats for basic functionality:

### Required Base Formats

```javascript
import Quill from 'quill';
const Parchment = Quill.import('parchment');

const registry = new Parchment.Registry();

// Required for document structure
registry.register(Parchment.Scroll);     // Root container
registry.register(Parchment.Block);      // Block-level elements
registry.register(Parchment.Inline);     // Inline elements
registry.register(Parchment.Text);       // Text nodes

// Required for proper editing behavior
registry.register(Parchment.Break);      // Line breaks
registry.register(Parchment.Container);  // Generic container
registry.register(Parchment.Cursor);     // Selection cursor
```

**Without these formats**, the editor will not function correctly.

---

## Adding Custom Formats to Registry

### Importing Built-in Formats

```javascript
import Quill from 'quill';
const Parchment = Quill.import('parchment');

// Import built-in formats
const Bold = Quill.import('formats/bold');
const Italic = Quill.import('formats/italic');
const Link = Quill.import('formats/link');
const Header = Quill.import('formats/header');

// Create registry with specific formats
const customRegistry = new Parchment.Registry();

// Register base formats
customRegistry.register(Parchment.Scroll);
customRegistry.register(Parchment.Block);
customRegistry.register(Parchment.Inline);
customRegistry.register(Parchment.Text);
customRegistry.register(Parchment.Break);

// Register selected formats
customRegistry.register(Bold);
customRegistry.register(Italic);
customRegistry.register(Link);
customRegistry.register(Header);

const quill = new Quill('#editor', {
  registry: customRegistry
});
```

### Registering Custom Formats

```javascript
import Quill from 'quill';
const Parchment = Quill.import('parchment');
const Inline = Parchment.Inline;

// Create custom format
class MentionFormat extends Inline {
  static blotName = 'mention';
  static tagName = 'span';
  static className = 'mention';

  static create(value) {
    const node = super.create();
    node.setAttribute('data-id', value.id);
    node.textContent = value.value;
    return node;
  }

  static formats(node) {
    return {
      id: node.getAttribute('data-id'),
      value: node.textContent
    };
  }
}

// Create registry and register custom format
const registry = new Parchment.Registry();
registry.register(Parchment.Scroll);
registry.register(Parchment.Block);
registry.register(Parchment.Inline);
registry.register(Parchment.Text);
registry.register(MentionFormat); // Add custom format

const quill = new Quill('#editor', {
  registry: registry
});
```

---

## Toolbar UI Alignment

**Important**: When using custom registries, ensure toolbar configuration matches available formats.

**Problem**:
```javascript
const registry = new Parchment.Registry();
registry.register(Parchment.Scroll);
registry.register(Parchment.Block);
registry.register(Parchment.Inline);
registry.register(Parchment.Text);
// No Bold format registered

const quill = new Quill('#editor', {
  registry: registry,
  modules: {
    toolbar: [
      ['bold'] // ❌ Toolbar has bold button but editor doesn't support it
    ]
  }
});
```

**Solution**: Match toolbar to registry:
```javascript
const quill = new Quill('#editor', {
  registry: registry,
  modules: {
    toolbar: false // ✅ Disable toolbar for minimal editor
  }
});
```

Or provide only supported formats:
```javascript
const Bold = Quill.import('formats/bold');
registry.register(Bold);

const quill = new Quill('#editor', {
  registry: registry,
  modules: {
    toolbar: [
      ['bold'] // ✅ Now bold is supported
    ]
  }
});
```

---

## Complete Working Example

Creating two editors with different capabilities:

```html
<!DOCTYPE html>
<html>
<head>
  <link href="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css" rel="stylesheet" />
</head>
<body>
  <h3>Full Editor (All Formats)</h3>
  <div id="full-editor">
    <p>This editor has all default formats...</p>
  </div>

  <h3>Limited Editor (Basic Only)</h3>
  <div id="limited-editor">
    <p>This editor only supports basic text...</p>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.js"></script>
  <script>
    // Full editor with default registry
    const fullEditor = new Quill('#full-editor', {
      theme: 'snow',
      modules: {
        toolbar: [
          [{ 'header': [1, 2, 3, false] }],
          ['bold', 'italic', 'underline', 'strike'],
          ['link', 'image', 'blockquote', 'code-block'],
          [{ 'list': 'ordered' }, { 'list': 'bullet' }]
        ]
      }
    });

    // Create custom registry for limited editor
    const Parchment = Quill.import('parchment');
    const Bold = Quill.import('formats/bold');
    const Italic = Quill.import('formats/italic');

    const limitedRegistry = new Parchment.Registry();

    // Register essential base formats
    limitedRegistry.register(Parchment.Scroll);
    limitedRegistry.register(Parchment.Block);
    limitedRegistry.register(Parchment.Inline);
    limitedRegistry.register(Parchment.Text);
    limitedRegistry.register(Parchment.Break);
    limitedRegistry.register(Parchment.Container);
    limitedRegistry.register(Parchment.Cursor);

    // Register only bold and italic
    limitedRegistry.register(Bold);
    limitedRegistry.register(Italic);

    // Limited editor with custom registry
    const limitedEditor = new Quill('#limited-editor', {
      registry: limitedRegistry,
      theme: 'snow',
      modules: {
        toolbar: [
          ['bold', 'italic'] // Only show supported formats
        ]
      }
    });

    // Test: Try to apply formats
    console.log('Full editor formats:', fullEditor.getFormat()); // All formats available
    console.log('Limited editor formats:', limitedEditor.getFormat()); // Only bold, italic
  </script>
</body>
</html>
```

---

## Registry vs Formats Option

| Approach | When to Use | Complexity |
|----------|-------------|------------|
| **formats option** | Whitelist formats from default registry | Simple |
| **custom registry** | Different format sets per instance | Advanced |

**Simple format restriction** (formats option):
```javascript
// Still uses default registry, just filters it
const quill = new Quill('#editor', {
  formats: ['bold', 'italic', 'link']
});
```

**Complete format isolation** (custom registry):
```javascript
// Completely separate format set
const registry = new Parchment.Registry();
// ... register only needed formats
const quill = new Quill('#editor', {
  registry: registry
});
```

**See Also**: `categories/configuration.md` for `formats` option documentation.

---

## Common Use Cases

### Admin vs User Editors

```javascript
// Admin editor - full features
const adminEditor = new Quill('#admin', {
  theme: 'snow',
  // Uses default registry
});

// User editor - restricted features
const Parchment = Quill.import('parchment');
const userRegistry = new Parchment.Registry();
// Register minimal formats...

const userEditor = new Quill('#user', {
  registry: userRegistry,
  theme: 'snow'
});
```

### Content Type Specific Editors

```javascript
// Blog post editor - rich formatting
const blogEditor = new Quill('#blog', {
  theme: 'snow'
  // Default registry
});

// Comment editor - plain text + basic formatting
const commentRegistry = new Parchment.Registry();
// Register basic formats only...

const commentEditor = new Quill('#comment', {
  registry: commentRegistry
});
```

---

## Debugging Registry Issues

### Check Registered Formats

```javascript
const quill = new Quill('#editor', {
  registry: customRegistry,
  debug: 'info' // Enable verbose logging
});

// Log all registered formats
console.log('Registered formats:', customRegistry.query('formats'));
```

### Common Errors

**Error**: "Cannot read property 'create' of undefined"
- **Cause**: Missing essential Parchment format (Scroll, Block, Inline, Text)
- **Solution**: Ensure all base formats are registered

**Error**: Toolbar button does nothing
- **Cause**: Format not registered in custom registry
- **Solution**: Register the format or remove toolbar button

---

## Performance Considerations

- **Registry creation**: Minimal overhead
- **Memory usage**: Each registry maintains its own format definitions
- **Recommendation**: Share registries between similar editors

```javascript
// ✅ GOOD: Share registry across similar editors
const basicRegistry = createBasicRegistry();

const editor1 = new Quill('#editor1', { registry: basicRegistry });
const editor2 = new Quill('#editor2', { registry: basicRegistry });

// ❌ AVOID: Creating new registry for each instance
const editor3 = new Quill('#editor3', { registry: createBasicRegistry() });
const editor4 = new Quill('#editor4', { registry: createBasicRegistry() });
```

---

## Related Files

- **Configuration**: See `categories/configuration.md` for `registry` and `formats` options
- **Custom Formats**: See `guides/parchment-blots.md` for creating custom formats
- **Formats List**: See `categories/formats.md` for available built-in formats

---

## Official Resources

- **Registries Documentation**: https://quilljs.com/docs/registries
- **Parchment Library**: https://github.com/quilljs/parchment
- **Format Importing**: See Quill source for format paths
