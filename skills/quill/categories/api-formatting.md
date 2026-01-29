# Quill Formatting API

Complete reference for all 5 formatting methods in Quill.js.

---

## Overview

Formatting methods apply inline and block-level styles to text. Quill distinguishes between:

- **Inline formats** - Character-level formatting (bold, color, links)
- **Block formats** - Line-level formatting (headers, lists, alignment)

**Core Methods**:
- `format()` - Format current selection
- `formatText()` - Format specific range (inline)
- `formatLine()` - Format specific lines (block)
- `getFormat()` - Retrieve active formats
- `removeFormat()` - Strip all formatting

All methods return a **Delta** representing the change (except `getFormat`).

---

## format()

Applies formatting to the current user selection (cursor position).

**Signature**:
```typescript
format(name: string, value: any, source?: string): Delta
```

**Parameters**:
- `name` - Format name (e.g., `'bold'`, `'color'`, `'header'`)
- `value` - Format value (`true`, color string, number, etc.)
- `source` - Optional change source (`'user'`, `'api'`, `'silent'`)

**Returns**: Delta representing the formatting change

**Examples**:

**Inline Formatting**:
```javascript
// User selects text, then:
quill.format('bold', true);        // Make selection bold
quill.format('color', '#ff0000');  // Change text color to red
quill.format('italic', true);      // Make selection italic

// Toggle format
const currentFormat = quill.getFormat();
quill.format('bold', !currentFormat.bold);
```

**Block Formatting**:
```javascript
// User has cursor on a line, then:
quill.format('header', 1);         // Make line H1
quill.format('list', 'ordered');   // Make line numbered list item
quill.format('align', 'center');   // Center-align line
```

**Remove Format**:
```javascript
// Remove specific format
quill.format('bold', false);
quill.format('header', false);
quill.format('link', false);
```

**Toolbar Button Handler**:
```javascript
document.getElementById('bold-btn').addEventListener('click', () => {
  const format = quill.getFormat();
  quill.format('bold', !format.bold); // Toggle
});
```

**Important Notes**:
- Requires **active selection** or cursor position
- If no selection, sets format for **next typed character**
- Works with both inline and block formats
- Use `formatText()` or `formatLine()` for programmatic ranges

**Use Cases**:
- Custom toolbar buttons
- Keyboard shortcuts
- Context menu actions
- Format toggles

---

## formatText()

Applies inline formatting to a specific text range.

**Signature**:
```typescript
formatText(index: number, length: number, source?: string): Delta
formatText(index: number, length: number, format: string, value: any, source?: string): Delta
formatText(index: number, length: number, formats: Record<string, any>, source?: string): Delta
```

**Parameters**:
- `index` - Starting position (0-based)
- `length` - Number of characters to format
- `format` - Single format name (optional)
- `value` - Format value (optional)
- `formats` - Multiple formats object (optional)
- `source` - Optional change source

**Returns**: Delta representing the formatting change

**Examples**:

**Single Format**:
```javascript
// Make characters 0-5 bold
quill.formatText(0, 5, 'bold', true);

// Change color of characters 10-20
quill.formatText(10, 10, 'color', '#0000ff');

// Add link to characters 5-15
quill.formatText(5, 10, 'link', 'https://example.com');

// Underline text
quill.formatText(0, 5, 'underline', true);
```

**Multiple Formats**:
```javascript
// Apply multiple formats at once
quill.formatText(0, 10, {
  bold: true,
  italic: true,
  color: '#ff0000',
  background: '#ffff00'
});

// Remove multiple formats
quill.formatText(0, 10, {
  bold: false,
  italic: false,
  underline: false
});
```

**Format Selection**:
```javascript
// Format current selection
const range = quill.getSelection();
if (range && range.length > 0) {
  quill.formatText(range.index, range.length, 'bold', true);
}
```

**Format Entire Document**:
```javascript
// Make all text bold
quill.formatText(0, quill.getLength(), 'bold', true);
```

**Search and Format**:
```javascript
// Find and highlight all instances of a word
const text = quill.getText();
const searchTerm = 'important';
let index = text.indexOf(searchTerm);

while (index !== -1) {
  quill.formatText(index, searchTerm.length, {
    background: '#ffff00',
    bold: true
  });
  index = text.indexOf(searchTerm, index + 1);
}
```

**Available Inline Formats**:
- `bold`, `italic`, `underline`, `strike`
- `code` (inline code)
- `script` (`'sub'` or `'super'`)
- `color`, `background`
- `font`, `size`
- `link`

**Important Notes**:
- **Only affects inline formats** (use `formatLine` for blocks)
- Length of `0` formats next typed character at index
- Does **not** create new text (use `insertText` for that)

**See Also**: `categories/formats.md` for complete format list

---

## formatLine()

Applies block-level formatting to one or more lines.

**Signature**:
```typescript
formatLine(index: number, length: number, source?: string): Delta
formatLine(index: number, length: number, format: string, value: any, source?: string): Delta
formatLine(index: number, length: number, formats: Record<string, any>, source?: string): Delta
```

**Parameters**:
- `index` - Starting position (0-based)
- `length` - Range length (formats all lines within range)
- `format` - Single format name (optional)
- `value` - Format value (optional)
- `formats` - Multiple formats object (optional)
- `source` - Optional change source

**Returns**: Delta representing the formatting change

**Examples**:

**Headers**:
```javascript
// Make line at position 0 an H1
quill.formatLine(0, 1, 'header', 1);

// Make lines 10-20 H2
quill.formatLine(10, 10, 'header', 2);

// Remove header (back to paragraph)
quill.formatLine(0, 1, 'header', false);
```

**Lists**:
```javascript
// Make line a bullet list item
quill.formatLine(5, 1, 'list', 'bullet');

// Make line a numbered list item
quill.formatLine(10, 1, 'list', 'ordered');

// Make line a checklist item
quill.formatLine(15, 1, 'list', 'check');

// Remove list formatting
quill.formatLine(5, 1, 'list', false);
```

**Alignment**:
```javascript
// Center-align line
quill.formatLine(0, 1, 'align', 'center');

// Right-align line
quill.formatLine(5, 1, 'align', 'right');

// Justify line
quill.formatLine(10, 1, 'align', 'justify');

// Reset to left (default)
quill.formatLine(0, 1, 'align', false);
```

**Code Blocks**:
```javascript
// Make line a code block
quill.formatLine(0, 1, 'code-block', true);

// Remove code block
quill.formatLine(0, 1, 'code-block', false);
```

**Multiple Block Formats**:
```javascript
// Apply multiple block formats
quill.formatLine(0, 1, {
  header: 2,
  align: 'center'
});

// Indented list item
quill.formatLine(5, 1, {
  list: 'bullet',
  indent: 2
});
```

**Format Multiple Lines**:
```javascript
// Make lines 0-50 a numbered list
quill.formatLine(0, 50, 'list', 'ordered');

// Make entire document centered
quill.formatLine(0, quill.getLength(), 'align', 'center');
```

**Format Current Line**:
```javascript
// Format line where cursor is
const range = quill.getSelection();
if (range) {
  const [line, offset] = quill.getLine(range.index);
  quill.formatLine(range.index - offset, line.length(), 'header', 1);
}
```

**Available Block Formats**:
- `header` (1-6 or `false`)
- `list` (`'ordered'`, `'bullet'`, `'check'`, or `false`)
- `blockquote` (`true` or `false`)
- `code-block` (`true` or `false`)
- `align` (`'left'`, `'center'`, `'right'`, `'justify'`, or `false`)
- `direction` (`'rtl'` or `false`)
- `indent` (`'+1'`, `'-1'`, or number)

**Format Conflicts**:
Some block formats are mutually exclusive:
```javascript
// header, blockquote, and code-block cannot coexist
quill.formatLine(0, 1, 'header', 1);        // Line becomes H1
quill.formatLine(0, 1, 'blockquote', true); // H1 removed, becomes blockquote
quill.formatLine(0, 1, 'code-block', true); // Blockquote removed, becomes code
```

**Important Notes**:
- Formats **entire lines**, even if range is mid-line
- Affects all lines that intersect the range
- Some formats are mutually exclusive

**See Also**: `categories/formats.md` for format compatibility

---

## getFormat()

Retrieves the active formatting at a range or position.

**Signature**:
```typescript
getFormat(range?: { index: number, length: number }): Record<string, any>
getFormat(index?: number, length?: number): Record<string, any>
```

**Parameters**:
- `range` - Range object (optional, defaults to current selection)
- `index` - Starting position (optional)
- `length` - Range length (optional)

**Returns**: Object with active format names and values

**Examples**:

**Get Current Selection Format**:
```javascript
// Get formats at current cursor/selection
const format = quill.getFormat();
console.log(format);
// { bold: true, italic: true, color: '#ff0000' }

// Check specific format
if (format.bold) {
  console.log('Selection is bold');
}
```

**Get Format at Position**:
```javascript
// Get format at specific position
const format = quill.getFormat(10);
console.log(format);

// Get format across range
const rangeFormat = quill.getFormat(5, 10);
```

**Get Format with Range Object**:
```javascript
const range = { index: 10, length: 5 };
const format = quill.getFormat(range);
```

**Toggle Format Button**:
```javascript
function updateToolbar() {
  const format = quill.getFormat();

  // Update button states
  document.getElementById('bold-btn').classList.toggle('active', format.bold);
  document.getElementById('italic-btn').classList.toggle('active', format.italic);

  // Update color picker
  if (format.color) {
    document.getElementById('color-picker').value = format.color;
  }
}

quill.on('selection-change', updateToolbar);
```

**Inclusive Formatting**:
When range spans multiple formats, only **common formats** are returned:
```javascript
// Text: "Hello World" where "Hello" is bold and "World" is italic
quill.getFormat(0, 11);
// {} - no common formats

// Text: "Hello World" where both are bold and "Hello" is also italic
quill.getFormat(0, 11);
// { bold: true } - bold is common to both
```

**Block Format Detection**:
```javascript
const format = quill.getFormat();

if (format.header === 1) {
  console.log('Current line is H1');
}

if (format.list === 'bullet') {
  console.log('Current line is bullet list');
}

if (format.align === 'center') {
  console.log('Current line is centered');
}
```

**Use Cases**:
- Updating toolbar button states
- Conditional formatting logic
- Format validation
- Building custom format UI

---

## removeFormat()

Removes all formatting from a text range (returns to plain text).

**Signature**:
```typescript
removeFormat(index: number, length: number, source?: string): Delta
```

**Parameters**:
- `index` - Starting position (0-based)
- `length` - Number of characters to clear
- `source` - Optional change source

**Returns**: Delta representing the removal

**Examples**:

**Remove Selection Formatting**:
```javascript
// Clear formatting from current selection
const range = quill.getSelection();
if (range && range.length > 0) {
  quill.removeFormat(range.index, range.length);
}
```

**Clear Specific Range**:
```javascript
// Remove all formatting from characters 0-10
quill.removeFormat(0, 10);

// Clear entire document formatting
quill.removeFormat(0, quill.getLength());
```

**Clear Formatting Button**:
```javascript
document.getElementById('clear-format-btn').addEventListener('click', () => {
  const range = quill.getSelection();
  if (range) {
    if (range.length === 0) {
      // No selection, clear entire document
      quill.removeFormat(0, quill.getLength());
    } else {
      // Clear selection
      quill.removeFormat(range.index, range.length);
    }
  }
});
```

**What Gets Removed**:
```javascript
// Before: "Hello World" (bold, italic, red, size large, H1, centered)
quill.removeFormat(0, 11);
// After: "Hello World" (plain paragraph text)
```

**Important Notes**:
- Removes **all inline and block formats**
- Text content is preserved
- Equivalent to setting all formats to `false`
- Does **not** remove embeds (images, videos)

**Alternative (Manual Format Removal)**:
```javascript
// Same as removeFormat, but explicit
quill.formatText(0, 10, {
  bold: false,
  italic: false,
  underline: false,
  color: false,
  background: false,
  link: false
});

quill.formatLine(0, 10, {
  header: false,
  list: false,
  align: false,
  blockquote: false
});
```

**Use Cases**:
- "Clear Formatting" toolbar button
- Paste as plain text
- Cleaning pasted content
- Resetting to default styles

---

## Common Formatting Patterns

### Format Toolbar Buttons
```javascript
const formats = {
  'bold-btn': { name: 'bold', value: true },
  'italic-btn': { name: 'italic', value: true },
  'underline-btn': { name: 'underline', value: true },
  'h1-btn': { name: 'header', value: 1 },
  'h2-btn': { name: 'header', value: 2 }
};

Object.entries(formats).forEach(([btnId, fmt]) => {
  document.getElementById(btnId).addEventListener('click', () => {
    const current = quill.getFormat();
    const isActive = current[fmt.name] === fmt.value;
    quill.format(fmt.name, isActive ? false : fmt.value);
  });
});
```

### Custom Color Picker
```javascript
document.getElementById('color-picker').addEventListener('change', (e) => {
  quill.format('color', e.target.value);
});

// Update picker when selection changes
quill.on('selection-change', () => {
  const format = quill.getFormat();
  if (format.color) {
    document.getElementById('color-picker').value = format.color;
  }
});
```

### Format Painter
```javascript
let copiedFormat = null;

// Copy format
document.getElementById('copy-format-btn').addEventListener('click', () => {
  copiedFormat = quill.getFormat();
  console.log('Format copied:', copiedFormat);
});

// Paste format
document.getElementById('paste-format-btn').addEventListener('click', () => {
  if (copiedFormat) {
    const range = quill.getSelection();
    if (range && range.length > 0) {
      quill.formatText(range.index, range.length, copiedFormat);
    }
  }
});
```

### Smart Lists
```javascript
// Auto-continue list on Enter
quill.keyboard.addBinding({
  key: 'Enter',
  handler: function(range) {
    const format = quill.getFormat(range.index);

    if (format.list) {
      const [line] = quill.getLine(range.index);
      const lineText = line.domNode.textContent;

      // If line is empty, exit list
      if (lineText.trim() === '') {
        quill.formatLine(range.index, 1, 'list', false);
        return false; // Prevent default Enter
      }
    }

    return true; // Allow default behavior
  }
});
```

### Format Validation
```javascript
function enforceFormatRules() {
  const delta = quill.getContents();
  let needsUpdate = false;

  delta.ops.forEach((op, index) => {
    if (op.attributes) {
      // Remove unauthorized formats
      if (op.attributes.color && !isValidColor(op.attributes.color)) {
        delete op.attributes.color;
        needsUpdate = true;
      }
    }
  });

  if (needsUpdate) {
    quill.setContents(delta, 'silent');
  }
}

quill.on('text-change', enforceFormatRules);
```

---

## Format Method Comparison

| Method | Purpose | Range | Format Types |
|--------|---------|-------|--------------|
| `format()` | Format current selection | User's selection | Inline & Block |
| `formatText()` | Format specific text range | Programmatic | Inline only |
| `formatLine()` | Format specific lines | Programmatic | Block only |
| `getFormat()` | Read active formats | Query | All |
| `removeFormat()` | Clear all formatting | Programmatic | All |

**When to use each**:
- `format()` - User-triggered toolbar actions
- `formatText()` - Programmatic inline styling (search highlighting, links)
- `formatLine()` - Programmatic block styling (headers, lists, alignment)
- `getFormat()` - Toolbar state updates, format detection
- `removeFormat()` - "Clear formatting" feature, paste as plain text

---

## Official Documentation

**URL**: https://quilljs.com/docs/api/#formatting

---

## Next Steps

- **Content**: See `categories/api-content.md` for insert/delete methods
- **Selection**: See `categories/api-selection.md` for cursor control
- **Formats**: See `categories/formats.md` for all available formats
- **Toolbar**: See `categories/toolbar-module.md` for UI formatting controls
