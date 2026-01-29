# Quill Formats Reference

Complete list of all formatting options available in Quill.js.

---

## Overview

Quill supports 23 built-in formats organized into three categories:

1. **Inline Formats** - Character-level formatting (bold, color, etc.)
2. **Block Formats** - Line/paragraph-level formatting (headers, lists, etc.)
3. **Embeds** - Non-text content (images, videos, formulas)

**By default**, all formats are enabled and can be configured independently from toolbar controls.

---

## Inline Formats (11 formats)

Applied to individual characters or text ranges.

### background

Background color for text.

**Format Name**: `'background'`
**Values**: Any valid CSS color value

**API Example**:
```javascript
quill.formatText(0, 5, 'background', '#ffff00'); // Yellow highlight
quill.formatText(0, 5, 'background', 'rgb(255, 0, 0)'); // Red highlight
```

**Toolbar Config**:
```javascript
toolbar: [
  [{ 'background': [] }] // Use theme's default colors
  // OR
  [{ 'background': ['#000000', '#e60000', '#ff9900', '#ffff00', '#008a00'] }]
]
```

---

### bold

Bold text weight.

**Format Name**: `'bold'`
**Values**: `true` | `false`

**API Example**:
```javascript
quill.formatText(0, 5, 'bold', true);  // Make bold
quill.formatText(0, 5, 'bold', false); // Remove bold
```

**Keyboard Shortcut**: Cmd/Ctrl + B

**Toolbar Config**:
```javascript
toolbar: [['bold']]
```

---

### color

Text color.

**Format Name**: `'color'`
**Values**: Any valid CSS color value

**API Example**:
```javascript
quill.formatText(0, 5, 'color', '#ff0000');      // Red text
quill.formatText(0, 5, 'color', 'rgb(0,0,255)'); // Blue text
```

**Toolbar Config**:
```javascript
toolbar: [
  [{ 'color': [] }] // Use theme's default colors
  // OR
  [{ 'color': ['#000000', '#e60000', '#ff9900'] }]
]
```

**Note**: Snow theme provides 35 default colors when set to `[]`.

---

### font

Font family.

**Format Name**: `'font'`
**Values**: Font family names (must be registered)

**Default Fonts**: Sans Serif, Serif, Monospace

**API Example**:
```javascript
quill.formatText(0, 5, 'font', 'serif');
quill.formatText(0, 5, 'font', 'monospace');
```

**Toolbar Config**:
```javascript
toolbar: [
  [{ 'font': [] }] // All registered fonts
  // OR
  [{ 'font': ['serif', 'monospace'] }]
]
```

---

### code

Inline code formatting (monospace with background).

**Format Name**: `'code'`
**Values**: `true` | `false`

**API Example**:
```javascript
quill.formatText(0, 10, 'code', true); // Format as inline code
```

**Keyboard Shortcut**: Cmd/Ctrl + E (in some configs)

**Toolbar Config**:
```javascript
toolbar: [['code']]
```

**Note**: Different from `code-block` which is a block format.

---

### italic

Italic text style.

**Format Name**: `'italic'`
**Values**: `true` | `false`

**API Example**:
```javascript
quill.formatText(0, 5, 'italic', true);
```

**Keyboard Shortcut**: Cmd/Ctrl + I

**Toolbar Config**:
```javascript
toolbar: [['italic']]
```

---

### link

Hyperlink with URL.

**Format Name**: `'link'`
**Values**: URL string | `false`

**API Example**:
```javascript
quill.formatText(0, 5, 'link', 'https://quilljs.com');
quill.formatText(0, 5, 'link', false); // Remove link
```

**Keyboard Shortcut**: Cmd/Ctrl + K

**Toolbar Config**:
```javascript
toolbar: [['link']]
```

**Custom Handler Example**:
```javascript
{
  toolbar: {
    handlers: {
      link: function(value) {
        if (value) {
          const href = prompt('Enter link URL:');
          this.quill.format('link', href);
        } else {
          this.quill.format('link', false);
        }
      }
    }
  }
}
```

---

### size

Text size.

**Format Name**: `'size'`
**Values**: Registered size names

**Default Sizes**: `'small'` | `false` (normal) | `'large'` | `'huge'`

**API Example**:
```javascript
quill.formatText(0, 5, 'size', 'large');
quill.formatText(0, 5, 'size', false); // Reset to normal
```

**Toolbar Config**:
```javascript
toolbar: [
  [{ 'size': ['small', false, 'large', 'huge'] }]
]
```

---

### strike

Strikethrough text.

**Format Name**: `'strike'`
**Values**: `true` | `false`

**API Example**:
```javascript
quill.formatText(0, 5, 'strike', true);
```

**Keyboard Shortcut**: Cmd/Ctrl + Shift + X (in some configs)

**Toolbar Config**:
```javascript
toolbar: [['strike']]
```

---

### script

Superscript or subscript.

**Format Name**: `'script'`
**Values**: `'sub'` | `'super'` | `false`

**API Example**:
```javascript
quill.formatText(0, 5, 'script', 'super'); // Superscript (x²)
quill.formatText(0, 5, 'script', 'sub');   // Subscript (H₂O)
quill.formatText(0, 5, 'script', false);   // Remove script
```

**Toolbar Config**:
```javascript
toolbar: [
  [{ 'script': 'sub' }, { 'script': 'super' }]
]
```

---

### underline

Underline text.

**Format Name**: `'underline'`
**Values**: `true` | `false`

**API Example**:
```javascript
quill.formatText(0, 5, 'underline', true);
```

**Keyboard Shortcut**: Cmd/Ctrl + U

**Toolbar Config**:
```javascript
toolbar: [['underline']]
```

---

## Block Formats (7 formats)

Applied to entire lines or paragraphs.

### blockquote

Block quotation.

**Format Name**: `'blockquote'`
**Values**: `true` | `false`

**API Example**:
```javascript
quill.formatLine(0, 10, 'blockquote', true);
```

**Toolbar Config**:
```javascript
toolbar: [['blockquote']]
```

**Note**: Mutually exclusive with `header` and `code-block`.

---

### header

Heading levels.

**Format Name**: `'header'`
**Values**: `1` | `2` | `3` | `4` | `5` | `6` | `false`

**API Example**:
```javascript
quill.formatLine(0, 10, 'header', 1); // H1
quill.formatLine(0, 10, 'header', 2); // H2
quill.formatLine(0, 10, 'header', false); // Remove header
```

**Toolbar Config**:
```javascript
toolbar: [
  [{ 'header': [1, 2, 3, 4, 5, 6, false] }]
  // OR
  [{ 'header': 1 }, { 'header': 2 }] // Buttons for H1 and H2
]
```

**Note**: Mutually exclusive with `blockquote` and `code-block`.

---

### indent

Indentation level.

**Format Name**: `'indent'`
**Values**: `'+1'` | `'-1'` | positive integer

**API Example**:
```javascript
quill.formatLine(0, 10, 'indent', '+1'); // Increase indent
quill.formatLine(0, 10, 'indent', '-1'); // Decrease indent
quill.formatLine(0, 10, 'indent', 3);    // Set to level 3
```

**Toolbar Config**:
```javascript
toolbar: [
  [{ 'indent': '-1'}, { 'indent': '+1' }]
]
```

---

### list

Ordered or unordered lists.

**Format Name**: `'list'`
**Values**: `'ordered'` | `'bullet'` | `'check'` | `false`

**API Example**:
```javascript
quill.formatLine(0, 10, 'list', 'ordered'); // Numbered list
quill.formatLine(0, 10, 'list', 'bullet');  // Bullet list
quill.formatLine(0, 10, 'list', 'check');   // Checklist
quill.formatLine(0, 10, 'list', false);     // Remove list
```

**Toolbar Config**:
```javascript
toolbar: [
  [{ 'list': 'ordered'}, { 'list': 'bullet' }, { 'list': 'check' }]
]
```

---

### align

Text alignment.

**Format Name**: `'align'`
**Values**: `'left'` | `'center'` | `'right'` | `'justify'` | `false`

**API Example**:
```javascript
quill.formatLine(0, 10, 'align', 'center');
quill.formatLine(0, 10, 'align', 'right');
quill.formatLine(0, 10, 'align', false); // Reset to left
```

**Toolbar Config**:
```javascript
toolbar: [
  [{ 'align': [] }] // All alignments
  // OR
  [{ 'align': 'center' }, { 'align': 'right' }, { 'align': 'justify' }]
]
```

---

### direction

Text direction (LTR/RTL).

**Format Name**: `'direction'`
**Values**: `'rtl'` | `false` (LTR)

**API Example**:
```javascript
quill.formatLine(0, 10, 'direction', 'rtl'); // Right-to-left
quill.formatLine(0, 10, 'direction', false); // Left-to-right
```

**Toolbar Config**:
```javascript
toolbar: [
  [{ 'direction': 'rtl' }]
]
```

---

### code-block

Multi-line code block with syntax highlighting.

**Format Name**: `'code-block'`
**Values**: `true` | `false` | language string (with Syntax module)

**API Example**:
```javascript
quill.formatLine(0, 10, 'code-block', true);
```

**Toolbar Config**:
```javascript
toolbar: [['code-block']]
```

**Note**:
- Mutually exclusive with `header` and `blockquote`
- Requires Syntax module for highlighting
- See `categories/syntax-module.md` for setup

---

## Embed Formats (3 formats)

Non-text content embedded in the document.

### formula

Mathematical formulas (LaTeX).

**Format Name**: `'formula'`
**Values**: LaTeX string

**API Example**:
```javascript
quill.insertEmbed(10, 'formula', 'e=mc^2');
quill.insertEmbed(10, 'formula', '\\sqrt{x^2+y^2}');
```

**Toolbar Config**:
```javascript
toolbar: [['formula']]
```

**Dependencies**: Requires KaTeX library

**Setup**:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.0/dist/katex.min.css" />
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.0/dist/katex.min.js"></script>
```

---

### image

Embedded images.

**Format Name**: `'image'`
**Values**: Image URL string

**API Example**:
```javascript
quill.insertEmbed(10, 'image', 'https://quilljs.com/assets/images/icon.png');
```

**Toolbar Config**:
```javascript
toolbar: [['image']]
```

**Custom Handler Example**:
```javascript
{
  toolbar: {
    handlers: {
      image: function() {
        const url = prompt('Enter image URL:');
        if (url) {
          const range = this.quill.getSelection();
          this.quill.insertEmbed(range.index, 'image', url);
        }
      }
    }
  }
}
```

---

### video

Embedded videos (iframe).

**Format Name**: `'video'`
**Values**: Video URL string

**API Example**:
```javascript
quill.insertEmbed(10, 'video', 'https://www.youtube.com/embed/dQw4w9WgXcQ');
```

**Toolbar Config**:
```javascript
toolbar: [['video']]
```

**Supported URLs**: YouTube, Vimeo, and other iframe-compatible video services

---

## Format Configuration

### Whitelist Specific Formats

Restrict editor to only certain formats:

```javascript
const quill = new Quill('#editor', {
  formats: ['bold', 'italic', 'underline', 'link'],
  theme: 'snow'
});
```

**Use Cases**:
- Simple comment editors (only bold/italic)
- Email composers (no custom fonts/colors)
- Controlled formatting environments

---

## Format Compatibility Matrix

| Format Category | Can Combine With | Mutually Exclusive |
|----------------|------------------|-------------------|
| **Inline formats** | All inline formats | None |
| **header** | align, direction, indent | blockquote, code-block |
| **blockquote** | align, direction, indent | header, code-block |
| **code-block** | indent | header, blockquote, list |
| **list** | align, direction, indent | code-block |
| **Embeds** | N/A (standalone) | N/A |

---

## Official Documentation

**URL**: https://quilljs.com/docs/formats

---

## Next Steps

- **Apply Formats**: See `categories/api-formatting.md` for programmatic formatting
- **Toolbar Setup**: See `categories/toolbar-module.md` for UI configuration
- **Custom Formats**: See `guides/parchment-blots.md` for creating custom formats
- **Delta Format**: See `categories/delta.md` for how formats are stored
