# Quill Themes

Visual theming options for customizing the editor's appearance and toolbar behavior.

---

## Overview

Quill provides two official themes plus a minimal core theme for custom implementations. Themes control both visual styling and UI behavior (toolbar appearance, tooltip positioning, etc.).

**Official Documentation**: https://quilljs.com/docs/themes

---

## Available Themes

### Snow Theme

A clean, flat design with a fixed toolbar. The most popular choice for traditional rich text editing.

**Visual**: White background, subtle borders, toolbar at top of editor.

**Setup**:
```javascript
const quill = new Quill('#editor', {
  theme: 'snow'
});
```

**Stylesheet (CDN)**:
```html
<link href="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css" rel="stylesheet" />
```

**Stylesheet (NPM)**:
```javascript
import 'quill/dist/quill.snow.css';
```

**Features**:
- Fixed toolbar at top
- Dropdown menus for multi-option formats (headers, fonts, etc.)
- Link/image tooltips
- Color picker for text/background colors
- Clean, professional appearance

**Use Cases**:
- Content management systems
- Blog editors
- Form text areas
- Document editing

---

### Bubble Theme

A minimalist theme with tooltip-based formatting controls. The toolbar appears only when text is selected.

**Visual**: Minimal chrome, formatting bubble appears on selection.

**Setup**:
```javascript
const quill = new Quill('#editor', {
  theme: 'bubble'
});
```

**Stylesheet (CDN)**:
```html
<link href="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.bubble.css" rel="stylesheet" />
```

**Stylesheet (NPM)**:
```javascript
import 'quill/dist/quill.bubble.css';
```

**Features**:
- No fixed toolbar (cleaner appearance)
- Tooltip appears on text selection
- Link preview on hover
- Mobile-friendly interface
- Contextual formatting options

**Use Cases**:
- Mobile applications
- Inline editing interfaces
- Commenting systems
- Note-taking apps

---

### Core (Minimal) Theme

Base functionality without any theme styling. Use this for completely custom themes.

**Setup**:
```javascript
const quill = new Quill('#editor', {
  theme: null  // or omit theme option entirely
});
```

**Optional Stylesheet**:
```html
<link href="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.core.css" rel="stylesheet" />
```

**Features**:
- Basic editing functionality
- No toolbar UI
- Minimal default styles
- Full API access

**Use Cases**:
- Building custom themes from scratch
- Headless editor implementations
- Integration with existing UI frameworks

---

## Theme Comparison

| Feature | Snow | Bubble | Core |
|---------|------|--------|------|
| **Toolbar** | Fixed at top | Tooltip on selection | None |
| **Links** | Edit tooltip | Preview tooltip | None |
| **Images** | Upload tooltip | Inline insertion | None |
| **Best For** | Traditional editors | Mobile/inline editing | Custom themes |
| **Complexity** | Medium | Low | Minimal |

---

## Implementation Details

### CDN Setup

Complete HTML example with Snow theme:

```html
<!DOCTYPE html>
<html>
<head>
  <link href="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css" rel="stylesheet" />
</head>
<body>
  <div id="editor">
    <p>Initial content...</p>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.js"></script>
  <script>
    const quill = new Quill('#editor', {
      theme: 'snow'
    });
  </script>
</body>
</html>
```

### NPM Setup

Module-based setup with bundler:

```javascript
import Quill from 'quill';
import 'quill/dist/quill.snow.css';

const quill = new Quill('#editor', {
  theme: 'snow',
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline'],
      ['link', 'image']
    ]
  }
});
```

---

## Customization Approaches

### CSS Overrides

Override theme styles with custom CSS:

```css
/* Customize Snow theme toolbar */
.ql-toolbar.ql-snow {
  background-color: #f5f5f5;
  border-color: #ddd;
  border-radius: 4px 4px 0 0;
}

/* Customize editor background */
.ql-container.ql-snow {
  background-color: #fafafa;
  border-color: #ddd;
  border-radius: 0 0 4px 4px;
}

/* Custom placeholder styling */
.ql-editor.ql-blank::before {
  color: #999;
  font-style: italic;
}

/* Custom selection color */
.ql-editor .ql-selected {
  background-color: #cce4ff;
}
```

### Dark Mode Example

```css
/* Dark theme overrides for Snow */
.ql-toolbar.ql-snow {
  background-color: #2d2d2d;
  border-color: #444;
}

.ql-container.ql-snow {
  background-color: #1e1e1e;
  border-color: #444;
}

.ql-editor {
  color: #e0e0e0;
}

.ql-editor.ql-blank::before {
  color: #666;
}

/* Invert toolbar icons */
.ql-toolbar.ql-snow .ql-stroke {
  stroke: #e0e0e0;
}

.ql-toolbar.ql-snow .ql-fill {
  fill: #e0e0e0;
}
```

### Module Configuration

Customize theme behavior via module options:

```javascript
const quill = new Quill('#editor', {
  theme: 'snow',
  modules: {
    toolbar: {
      container: [
        [{ 'header': [1, 2, 3, false] }],
        ['bold', 'italic', 'underline'],
        ['link', 'image']
      ],
      handlers: {
        // Custom image handler
        image: function() {
          const url = prompt('Enter image URL:');
          if (url) {
            this.quill.insertEmbed(this.quill.getSelection().index, 'image', url);
          }
        }
      }
    }
  }
});
```

---

## Custom Toolbar Container

Snow theme supports external toolbar containers:

```html
<div id="toolbar">
  <button class="ql-bold">Bold</button>
  <button class="ql-italic">Italic</button>
  <select class="ql-header">
    <option value="1">Heading 1</option>
    <option value="2">Heading 2</option>
    <option selected>Normal</option>
  </select>
</div>

<div id="editor">
  <p>Content here...</p>
</div>

<script>
  const quill = new Quill('#editor', {
    theme: 'snow',
    modules: {
      toolbar: '#toolbar'
    }
  });
</script>
```

**See Also**: `categories/toolbar-module.md` for complete toolbar customization.

---

## Building Custom Themes

For completely custom themes, extend the base Theme class:

```javascript
import Quill from 'quill';
const Theme = Quill.import('core/theme');

class CustomTheme extends Theme {
  constructor(quill, options) {
    super(quill, options);

    // Add custom initialization
    this.quill.container.classList.add('custom-theme');
  }
}

// Register custom theme
Quill.register('themes/custom', CustomTheme);

// Use custom theme
const quill = new Quill('#editor', {
  theme: 'custom'
});
```

**Advanced**: Refer to Snow/Bubble source code for implementation patterns.

---

## Theme-Specific Features

### Snow Theme Only

**Tooltips for links**:
```javascript
// Edit existing links by clicking them
// Link tooltip appears with edit/remove options
```

**Image resize handles** (with custom module):
```javascript
// Snow theme provides better integration with image resize modules
```

### Bubble Theme Only

**Link preview**:
```javascript
// Hovering over links shows preview tooltip
// Clicking opens link editor
```

**Selection-based toolbar**:
```javascript
// Toolbar only appears when text is selected
// Reduces visual clutter
```

---

## Performance Considerations

- **Stylesheet size**: Snow (~8KB), Bubble (~6KB), Core (~2KB) minified
- **Load time**: Include stylesheets in `<head>` for faster rendering
- **Custom themes**: Keep CSS overrides minimal to avoid specificity conflicts

---

## Browser Compatibility

All themes support:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile Safari (iOS 11+)
- Chrome Mobile (Android)

**Note**: IE11 support dropped in Quill 2.0+

---

## Related Files

- **Configuration**: See `categories/configuration.md` for `theme` option
- **Toolbar**: See `categories/toolbar-module.md` for toolbar customization
- **Getting Started**: See `categories/getting-started.md` for setup examples

---

## Official Resources

- **Themes Documentation**: https://quilljs.com/docs/themes
- **Snow Demo**: https://quilljs.com/playground/snow
- **Bubble Demo**: https://quilljs.com/playground/bubble
- **GitHub Themes Source**: https://github.com/slab/quill/tree/main/themes
