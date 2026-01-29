# Getting Started with Quill.js

Quick setup guide for initializing Quill rich text editor in your project.

---

## Quickstart (CDN)

The fastest way to get Quill running is using the CDN:

### Step 1: Include Stylesheet

Add the theme stylesheet to your HTML `<head>`:

```html
<link href="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css" rel="stylesheet" />
```

**Available Themes**:
- `quill.snow.css` - Clean flat toolbar theme
- `quill.bubble.css` - Minimal tooltip-based theme

### Step 2: Create Editor Container

Add a container element where the editor will initialize:

```html
<div id="editor">
  <p>Hello World!</p>
  <p>Some initial <strong>bold</strong> text</p>
  <p><br /></p>
</div>
```

**Important**: The container's existing content becomes the editor's initial state.

### Step 3: Include Library

Add the Quill library before your closing `</body>` tag:

```html
<script src="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.js"></script>
```

### Step 4: Initialize

Create a new Quill instance with theme configuration:

```javascript
const quill = new Quill('#editor', {
  theme: 'snow'
});
```

**That's it!** You now have a fully functional rich text editor.

---

## NPM Installation

For modern build workflows, install via npm:

```bash
npm install quill@2.0.3
```

**Import in your JavaScript/TypeScript**:

```javascript
import Quill from 'quill';
import 'quill/dist/quill.snow.css'; // or quill.bubble.css

const quill = new Quill('#editor', {
  theme: 'snow'
});
```

**TypeScript Support**: Quill v2.0+ includes official TypeScript definitions - no @types package needed!

---

## Why Quill?

Understanding Quill's advantages over traditional editors:

### 1. API-Driven Design

**Traditional editors** expose HTML/DOM for manipulation, leading to:
- Browser inconsistencies
- Security vulnerabilities (XSS)
- Complex state management

**Quill** uses a JSON-based document model (Delta format):
- Predictable, consistent behavior across browsers
- Secure by design (no arbitrary HTML injection)
- Easy to serialize, validate, and transform

**Example**:
```javascript
// Instead of: innerHTML = '<strong>Hello</strong>'
// Use:
quill.insertText(0, 'Hello', 'bold', true);

// Get content as JSON:
const delta = quill.getContents();
// { ops: [{ insert: 'Hello', attributes: { bold: true } }] }
```

### 2. Custom Content and Formatting

Quill's document model is extensible:
- Create custom inline formats (e.g., mentions, hashtags)
- Create custom block formats (e.g., tweets, dividers)
- Create custom embeds (e.g., charts, videos)
- All formats integrate seamlessly with existing features

**No DOM manipulation required** - extend the document model, not the UI.

### 3. Cross-Platform Consistency

Quill normalizes behavior across:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Operating systems (Windows, Mac, Linux)

**Unified behavior** for:
- Copy/paste handling
- Keyboard shortcuts
- Selection management
- Text input methods (IME support)

### 4. Ease of Implementation

**Minimal setup**:
- No complex configuration required
- Works out of the box with sensible defaults
- Two themes included
- Comprehensive documentation

**Real magic**: "The real magic of Quill comes in its flexibility and extensibility."

---

## Basic Options

Configure Quill behavior with initialization options:

```javascript
const quill = new Quill('#editor', {
  theme: 'snow',
  placeholder: 'Compose an epic...',
  readOnly: false,
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline'],
      ['link', 'image']
    ]
  }
});
```

**Common Options**:
- `theme` - Visual theme ('snow', 'bubble', or null for minimal)
- `placeholder` - Text shown when editor is empty
- `readOnly` - Disable editing (display only)
- `modules` - Configure built-in modules (Toolbar, Keyboard, etc.)

**See Also**: `categories/configuration.md` for all options

---

## Next Steps

### Learn Core Concepts:
- **Configuration**: See `categories/configuration.md` for all options
- **Formats**: See `categories/formats.md` for available formatting
- **Delta Format**: See `categories/delta.md` for document model

### Explore API:
- **Content Methods**: See `categories/api-content.md` for insert/delete/get methods
- **Formatting Methods**: See `categories/api-formatting.md` for applying formats
- **Events**: See `categories/api-events.md` for change listeners

### Configure Modules:
- **Toolbar**: See `categories/toolbar-module.md` for customization
- **Keyboard**: See `categories/keyboard-module.md` for shortcuts
- **History**: See `categories/history-module.md` for undo/redo

### Advanced Topics:
- **Custom Modules**: See `guides/custom-modules.md` for building modules
- **Custom Formats**: See `guides/parchment-blots.md` for Parchment/Blots

---

## Resources

- **Official Docs**: https://quilljs.com/docs/quickstart
- **Interactive Playground**: https://quilljs.com/playground/snow
- **GitHub**: https://github.com/slab/quill (37,622+ stars)
- **License**: BSD 3-Clause (free for personal and commercial use)
- **Version**: v2.0.3 (latest stable)

---

## Complete Example

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Quill Editor</title>
  <link href="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css" rel="stylesheet" />
</head>
<body>
  <div id="editor">
    <p>Start editing here...</p>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.js"></script>
  <script>
    const quill = new Quill('#editor', {
      theme: 'snow',
      placeholder: 'Compose an epic...',
      modules: {
        toolbar: [
          [{ 'header': [1, 2, 3, false] }],
          ['bold', 'italic', 'underline', 'strike'],
          ['link', 'image', 'code-block'],
          [{ 'list': 'ordered'}, { 'list': 'bullet' }],
          ['clean']
        ]
      }
    });

    // Listen for text changes
    quill.on('text-change', (delta, oldDelta, source) => {
      console.log('Text changed!', delta);
    });
  </script>
</body>
</html>
```

---

**You're ready to use Quill! For specific features, load the appropriate category file.**
