# Quill Configuration Options

Complete reference for configuring Quill editor behavior and appearance.

---

## Overview

Quill accepts a configuration object during initialization to customize behavior. The framework distinguishes between:

- **Options** - Tweak existing functionality (this file)
- **Modules** - Add new features (see `categories/*-module.md` files)
- **Themes** - Visual styling (see `patterns/themes.md`)

```javascript
const quill = new Quill('#editor', {
  // Configuration options
  theme: 'snow',
  placeholder: 'Start typing...',
  readOnly: false,
  // ... more options
});
```

---

## Configuration Options Reference

### container (Required)

Specifies the DOM element where Quill will initialize.

**Type**: CSS selector string OR DOM Element

**Examples**:
```javascript
// CSS selector
const quill = new Quill('#editor');

// DOM element
const container = document.getElementById('editor');
const quill = new Quill(container);
```

**Initial Content**: If the container has existing HTML, Quill preserves it as the initial editor content.

```html
<div id="editor">
  <p>This content will be preserved!</p>
  <p>Including <strong>formatting</strong>.</p>
</div>
```

---

### bounds

Confines editor UI elements (tooltips, dropdown menus, etc.) within specified boundaries.

**Type**: CSS selector string OR DOM Element
**Default**: `document.body`

**Purpose**: Prevents UI elements from rendering outside a specific container.

**Current Limitation**: Only restricts left and right boundaries (not top/bottom).

**Example**:
```javascript
const quill = new Quill('#editor', {
  bounds: '#scrolling-container',
  theme: 'snow'
});
```

**Use Case**: Constraining tooltips within a modal or scrollable container.

---

###debug

Sets logging level for Quill diagnostics.

**Type**: `'error'` | `'warn'` | `'log'` | `'info'` | `boolean`
**Default**: `'warn'`

**Behavior**: Affects ALL Quill instances on the page (global setting).

**Levels**:
- `'error'` - Only errors
- `'warn'` - Errors and warnings (default)
- `'log'` - Errors, warnings, and logs
- `'info'` - All messages including debug info
- `false` - Disable all logging
- `true` - Enable all logging (same as `'info'`)

**Example**:
```javascript
const quill = new Quill('#editor', {
  debug: 'info', // Verbose logging
  theme: 'snow'
});
```

**Alternative (Static Method)**:
```javascript
Quill.debug('info'); // Set globally before initialization
```

---

### formats

Whitelist specific formats the editor should allow.

**Type**: `string[]` OR `null`
**Default**: `null` (all formats enabled)

**Purpose**: Restrict which formatting options are available to users.

**Example - Only allow bold and italic**:
```javascript
const quill = new Quill('#editor', {
  formats: ['bold', 'italic'],
  theme: 'snow'
});
```

**Example - Only block formats**:
```javascript
const quill = new Quill('#editor', {
  formats: ['header', 'list', 'blockquote'],
  theme: 'snow'
});
```

**Important**: Using the `registry` option overrides this setting.

**See Also**: `categories/formats.md` for complete list of available formats.

---

### placeholder

Text displayed when the editor is empty.

**Type**: `string`
**Default**: `null` (no placeholder)

**Example**:
```javascript
const quill = new Quill('#editor', {
  placeholder: 'Compose an epic...',
  theme: 'snow'
});
```

**Behavior**:
- Appears when editor contains only empty line
- Disappears as soon as user types
- Styled via CSS `.ql-editor.ql-blank::before`

**Custom Styling**:
```css
.ql-editor.ql-blank::before {
  color: #999;
  content: attr(data-placeholder);
  font-style: italic;
}
```

---

### readOnly

Controls whether the editor allows user input.

**Type**: `boolean`
**Default**: `false`

**Purpose**: Display content without allowing edits.

**Example**:
```javascript
const quill = new Quill('#editor', {
  readOnly: true,
  theme: 'snow'
});
```

**Programmatic Toggle**:
```javascript
quill.enable(false); // Set read-only
quill.enable(true);  // Allow editing
```

**Use Cases**:
- Displaying archived content
- Preview mode
- Permission-based editing restrictions

---

### registry

Advanced format and module registration beyond simple whitelisting.

**Type**: `Registry` object OR `null`
**Default**: `null`

**Purpose**: Create custom format sets for different editor instances on the same page.

**Behavior**: When specified, overrides the `formats` option.

**Example**:
```javascript
import Quill from 'quill';
const Parchment = Quill.import('parchment');

// Create custom registry with limited formats
const registry = new Parchment.Registry();
registry.register(Parchment.Scroll);
registry.register(Parchment.Block);
registry.register(Parchment.Inline);
registry.register(Parchment.Text);

// Use custom registry
const quill = new Quill('#editor', {
  registry: registry
});
```

**See Also**: `patterns/registries.md` for complete guide to multiple editors with different formats.

---

### theme

Specifies the visual theme for the editor.

**Type**: `'snow'` | `'bubble'` | `null` | `false`
**Default**: Minimal theme (when null/false)

**Available Themes**:

**1. Snow** - Clean flat toolbar theme
```javascript
const quill = new Quill('#editor', { theme: 'snow' });
```
Stylesheet: `quill.snow.css`

**2. Bubble** - Tooltip-based minimalist theme
```javascript
const quill = new Quill('#editor', { theme: 'bubble' });
```
Stylesheet: `quill.bubble.css`

**3. Minimal** - No theme (base functionality only)
```javascript
const quill = new Quill('#editor', { theme: null });
```
No stylesheet required (or use base `quill.core.css`)

**Important**: Theme stylesheets must be included manually via `<link>` tag or import.

**CDN Example**:
```html
<link href="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css" rel="stylesheet" />
```

**NPM Example**:
```javascript
import 'quill/dist/quill.snow.css';
```

**See Also**: `patterns/themes.md` for customization and theme differences.

---

## Complete Configuration Example

```javascript
const quill = new Quill('#editor', {
  // Editor behavior
  theme: 'snow',
  placeholder: 'Start writing your masterpiece...',
  readOnly: false,
  bounds: '#container',

  // Format restrictions
  formats: ['bold', 'italic', 'underline', 'link', 'header', 'list'],

  // Debugging (development only)
  debug: 'warn',

  // Module configuration
  modules: {
    toolbar: [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline'],
      ['link'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }]
    ],
    history: {
      delay: 1000,
      maxStack: 50
    }
  }
});
```

---

## Configuration vs Modules

| Feature | Configuration Options | Modules |
|---------|----------------------|---------|
| **Purpose** | Tweak existing behavior | Add new features |
| **Examples** | `placeholder`, `readOnly`, `theme` | `toolbar`, `keyboard`, `history` |
| **When to use** | Adjust editor appearance/behavior | Add formatting UI, shortcuts, undo/redo |
| **Configured via** | Top-level options object | `modules` property |

**Example**:
```javascript
const quill = new Quill('#editor', {
  // Configuration options (tweaks)
  theme: 'snow',
  placeholder: 'Type here...',

  // Modules (features)
  modules: {
    toolbar: [...],
    keyboard: {...}
  }
});
```

---

## Runtime Configuration Changes

Some options can be changed after initialization:

**Read-Only Mode**:
```javascript
quill.enable(false); // Disable editing
quill.enable(true);  // Enable editing
```

**Debugging**:
```javascript
Quill.debug('info'); // Enable verbose logging
```

**Most options CANNOT be changed** after initialization - you must create a new Quill instance.

---

## Official Documentation

**URL**: https://quilljs.com/docs/configuration

---

## Next Steps

- **Modules**: See `categories/toolbar-module.md`, `categories/keyboard-module.md`, etc.
- **Themes**: See `patterns/themes.md` for customization
- **Formats**: See `categories/formats.md` for available formatting options
- **API**: See `categories/api-*.md` files for programmatic control
