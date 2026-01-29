# Quill Content Manipulation API

Complete reference for all 10 content manipulation methods in Quill.js.

---

## Overview

Content manipulation methods allow you to programmatically read and modify the editor's document. These are the most commonly used Quill API methods.

**Core Operations**:
- **Insert**: `insertText`, `insertEmbed`
- **Delete**: `deleteText`
- **Update**: `updateContents`
- **Replace**: `setContents`, `setText`
- **Read**: `getContents`, `getText`, `getSemanticHTML`, `getLength`

All modification methods return a **Delta** object representing the change and accept an optional **source** parameter.

---

## deleteText()

Deletes text from the editor at specified position.

**Signature**:
```typescript
deleteText(index: number, length: number, source?: string): Delta
```

**Parameters**:
- `index` - Starting position (0-based)
- `length` - Number of characters to delete
- `source` - Optional change source (`'user'`, `'api'`, `'silent'`)

**Returns**: Delta representing the deletion

**Examples**:
```javascript
// Delete 5 characters starting at position 0
quill.deleteText(0, 5);

// Delete with explicit source
quill.deleteText(10, 3, 'api');

// Delete entire line (including newline)
const lineLength = quill.getLine(5)[0].length();
quill.deleteText(5, lineLength);
```

**Common Use Cases**:
- Clearing specific text ranges
- Implementing custom delete behavior
- Programmatic content removal

**See Also**: `updateContents` for more complex deletions

---

## getContents()

Retrieves editor contents as a Delta object with formatting preserved.

**Signature**:
```typescript
getContents(index?: number, length?: number): Delta
```

**Parameters**:
- `index` - Optional starting position (default: 0)
- `length` - Optional length (default: rest of document)

**Returns**: Delta object representing document content

**Examples**:
```javascript
// Get entire document
const delta = quill.getContents();
// { ops: [
//   { insert: 'Hello ' },
//   { insert: 'World', attributes: { bold: true } },
//   { insert: '\n' }
// ]}

// Get specific range (characters 5-15)
const partial = quill.getContents(5, 10);

// Get single line
const line = quill.getLine(0);
const lineContent = quill.getContents(line[0].offset(), line[0].length());
```

**Delta Structure**:
```javascript
{
  ops: [
    { insert: 'Plain text' },
    { insert: 'Bold text', attributes: { bold: true } },
    { insert: '\n', attributes: { header: 1 } } // Header line
  ]
}
```

**Use Cases**:
- Saving content to database
- Implementing autosave
- Content validation
- Exporting for other editors

**See Also**: `categories/delta.md` for complete Delta documentation

---

## getLength()

Returns the total length of the editor content.

**Signature**:
```typescript
getLength(): number
```

**Returns**: Number of characters in document (minimum 1 for trailing newline)

**Examples**:
```javascript
const length = quill.getLength();
console.log(length); // e.g., 15

// Empty editor still has length 1 (newline)
const emptyQuill = new Quill('#empty');
console.log(emptyQuill.getLength()); // 1

// Use in range checks
const selection = quill.getSelection();
if (selection && selection.index + selection.length > quill.getLength()) {
  console.error('Selection out of bounds');
}
```

**Important Notes**:
- **Minimum value is 1** (Quill always has a trailing newline)
- Empty editor returns `1`, not `0`
- Useful for validation and range checks

**Use Cases**:
- Validating selections
- Character count display
- Limiting content length

---

## getText()

Extracts plain text without any formatting.

**Signature**:
```typescript
getText(index?: number, length?: number): string
```

**Parameters**:
- `index` - Optional starting position (default: 0)
- `length` - Optional length (default: rest of document)

**Returns**: Plain text string

**Examples**:
```javascript
// Get all text
const text = quill.getText();
// "Hello World\n"

// Get specific range
const partial = quill.getText(0, 5);
// "Hello"

// Get text without trailing newline
const textNoNewline = quill.getText(0, quill.getLength() - 1);

// Search in text
if (quill.getText().includes('keyword')) {
  console.log('Keyword found!');
}
```

**Comparison with getContents()**:
```javascript
// Rich content in editor: "Hello World" (bold)

quill.getContents();
// { ops: [{ insert: 'Hello World', attributes: { bold: true } }] }

quill.getText();
// "Hello World\n" - formatting stripped
```

**Use Cases**:
- Plain text search
- Character counting
- Text-only exports
- Validation against plain text

---

## getSemanticHTML()

Exports editor content as semantic HTML representation.

**Signature**:
```typescript
getSemanticHTML(index?: number, length?: number): string
```

**Parameters**:
- `index` - Optional starting position (default: 0)
- `length` - Optional length (default: rest of document)

**Returns**: HTML string

**Examples**:
```javascript
// Get entire document as HTML
const html = quill.getSemanticHTML();
// "<p>Hello <strong>World</strong></p>"

// Get specific range
const partialHtml = quill.getSemanticHTML(0, 10);

// Save to database or send via API
fetch('/api/save', {
  method: 'POST',
  body: JSON.stringify({ content: quill.getSemanticHTML() })
});
```

**Output Examples**:
```javascript
// Bold text
quill.setText('Hello');
quill.formatText(0, 5, 'bold', true);
quill.getSemanticHTML();
// "<p><strong>Hello</strong></p>"

// Header with link
quill.setText('Click here');
quill.formatLine(0, 1, 'header', 1);
quill.formatText(0, 10, 'link', 'https://example.com');
quill.getSemanticHTML();
// "<h1><a href="https://example.com">Click here</a></h1>"

// List items
quill.setText('Item 1\nItem 2\n');
quill.formatLine(0, 1, 'list', 'bullet');
quill.formatLine(7, 1, 'list', 'bullet');
quill.getSemanticHTML();
// "<ul><li>Item 1</li><li>Item 2</li></ul>"
```

**Important Notes**:
- Output is **semantic HTML** (uses proper tags like `<strong>`, `<em>`)
- **Not guaranteed to be identical** to editor's internal HTML
- **Does not include Quill CSS classes**
- Best for exporting/displaying content outside Quill

**Alternative (Internal HTML)**:
```javascript
// Get Quill's internal HTML (includes editor classes)
const internalHtml = quill.root.innerHTML;
```

**Use Cases**:
- Exporting to CMS
- Email templates
- Displaying content on other pages
- SEO-friendly output

---

## insertEmbed()

Inserts non-text content (images, videos, formulas) at specified position.

**Signature**:
```typescript
insertEmbed(index: number, type: string, value: any, source?: string): Delta
```

**Parameters**:
- `index` - Position to insert (0-based)
- `type` - Embed type (`'image'`, `'video'`, `'formula'`)
- `value` - Embed-specific value (URL, LaTeX string, etc.)
- `source` - Optional change source

**Returns**: Delta representing the insertion

**Examples**:

**Image Embed**:
```javascript
// Insert image at current cursor
const range = quill.getSelection();
quill.insertEmbed(range.index, 'image', 'https://example.com/image.png');

// Insert at specific position
quill.insertEmbed(10, 'image', 'https://example.com/logo.svg');
```

**Video Embed**:
```javascript
// YouTube video
quill.insertEmbed(0, 'video', 'https://www.youtube.com/embed/dQw4w9WgXcQ');

// Vimeo video
quill.insertEmbed(0, 'video', 'https://player.vimeo.com/video/123456789');
```

**Formula Embed** (requires KaTeX):
```javascript
// Simple formula
quill.insertEmbed(5, 'formula', 'e=mc^2');

// Complex LaTeX
quill.insertEmbed(5, 'formula', '\\sqrt{x^2+y^2}');
quill.insertEmbed(5, 'formula', '\\frac{a}{b}');
```

**Custom Handler Example**:
```javascript
// File upload handler
document.getElementById('file-input').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file.type.startsWith('image/')) {
    const reader = new FileReader();
    reader.onload = (event) => {
      const range = quill.getSelection(true);
      quill.insertEmbed(range.index, 'image', event.target.result);
      quill.setSelection(range.index + 1);
    };
    reader.readAsDataURL(file);
  }
});
```

**Important Notes**:
- Embeds are **block-level** elements
- Cursor moves to **after** the embed
- Use `setSelection` to position cursor after insertion

**See Also**:
- `categories/formats.md` for embed types
- `guides/parchment-blots.md` for custom embeds

---

## insertText()

Inserts text at specified position with optional formatting.

**Signature**:
```typescript
insertText(index: number, text: string, source?: string): Delta
insertText(index: number, text: string, format: string, value: any, source?: string): Delta
insertText(index: number, text: string, formats: Record<string, any>, source?: string): Delta
```

**Parameters**:
- `index` - Position to insert (0-based)
- `text` - Text to insert
- `format` - Single format name (optional)
- `value` - Format value (optional)
- `formats` - Multiple formats object (optional)
- `source` - Optional change source

**Returns**: Delta representing the insertion

**Examples**:

**Plain Text**:
```javascript
// Insert plain text
quill.insertText(0, 'Hello World');

// Insert at cursor position
const range = quill.getSelection();
if (range) {
  quill.insertText(range.index, 'Inserted text');
}
```

**Single Format**:
```javascript
// Insert bold text
quill.insertText(0, 'Bold text', 'bold', true);

// Insert colored text
quill.insertText(5, 'Red text', 'color', '#ff0000');

// Insert link
quill.insertText(10, 'Click here', 'link', 'https://example.com');
```

**Multiple Formats**:
```javascript
// Insert text with multiple formats
quill.insertText(0, 'Fancy text', {
  bold: true,
  italic: true,
  color: '#ff0000',
  background: '#ffff00'
});

// Insert formatted text with API source
quill.insertText(5, 'API text', { bold: true }, 'api');
```

**Newline Insertion**:
```javascript
// Insert newline
quill.insertText(10, '\n');

// Insert newline with block format
quill.insertText(10, '\n', 'header', 1);

// Create new list item
quill.insertText(10, '\n', 'list', 'bullet');
```

**Auto-positioning Cursor**:
```javascript
// Insert and move cursor after
const range = quill.getSelection(true); // Focus editor
quill.insertText(range.index, 'New text');
quill.setSelection(range.index + 8); // Position after "New text"
```

**Use Cases**:
- Programmatic content insertion
- Autocomplete/mentions
- Template insertion
- Keyboard shortcut handlers

---

## setContents()

Overwrites entire editor contents with new Delta.

**Signature**:
```typescript
setContents(delta: Delta, source?: string): Delta
```

**Parameters**:
- `delta` - Delta object or array of operations
- `source` - Optional change source

**Returns**: Delta representing the change

**Examples**:

**From Delta Object**:
```javascript
// Replace entire document
quill.setContents({
  ops: [
    { insert: 'Hello ' },
    { insert: 'World', attributes: { bold: true } },
    { insert: '\n' }
  ]
});
```

**From Operations Array**:
```javascript
// Same as above
quill.setContents([
  { insert: 'Hello ' },
  { insert: 'World', attributes: { bold: true } },
  { insert: '\n' }
]);
```

**Loading Saved Content**:
```javascript
// Load from database
fetch('/api/content/123')
  .then(res => res.json())
  .then(data => {
    quill.setContents(data.delta);
  });

// Load from localStorage
const saved = JSON.parse(localStorage.getItem('draft'));
if (saved) {
  quill.setContents(saved);
}
```

**Clear Document**:
```javascript
// Clear all content (leaves single newline)
quill.setContents([{ insert: '\n' }]);
```

**Important Notes**:
- **Completely replaces** existing content
- Selection/cursor is **reset**
- Use `updateContents` for partial updates
- Delta must end with `\n` for valid document

**Use Cases**:
- Loading saved documents
- Resetting editor state
- Implementing templates
- Undo/redo functionality

**See Also**: `updateContents` for incremental changes

---

## setText()

Sets editor content to plain text (removes all formatting).

**Signature**:
```typescript
setText(text: string, source?: string): Delta
```

**Parameters**:
- `text` - Plain text string
- `source` - Optional change source

**Returns**: Delta representing the change

**Examples**:
```javascript
// Set plain text
quill.setText('Hello World');

// Clear editor
quill.setText('');

// Set with explicit source
quill.setText('API content', 'api');

// Newlines are preserved
quill.setText('Line 1\nLine 2\nLine 3');
```

**Comparison with setContents()**:
```javascript
// setText() - plain text only
quill.setText('Hello World');
// Result: "Hello World" (no formatting)

// setContents() - with formatting
quill.setContents([
  { insert: 'Hello World', attributes: { bold: true } }
]);
// Result: "Hello World" (bold)
```

**Important Notes**:
- **Strips all formatting** from text
- **Replaces entire document**
- Cursor/selection is reset
- Faster than `setContents` for plain text

**Use Cases**:
- Loading plain text content
- Clearing formatted content
- Plain text paste override
- Simple text editor mode

---

## updateContents()

Applies Delta changes to specific document positions (incremental updates).

**Signature**:
```typescript
updateContents(delta: Delta, source?: string): Delta
```

**Parameters**:
- `delta` - Delta with `retain`, `insert`, and/or `delete` operations
- `source` - Optional change source

**Returns**: Delta representing the actual change

**Examples**:

**Insert at Position**:
```javascript
// Insert "Hello" at position 5
quill.updateContents({
  ops: [
    { retain: 5 },        // Skip first 5 characters
    { insert: 'Hello ' }  // Insert text
  ]
});
```

**Delete Range**:
```javascript
// Delete 10 characters starting at position 5
quill.updateContents({
  ops: [
    { retain: 5 },    // Skip to position 5
    { delete: 10 }    // Delete next 10 chars
  ]
});
```

**Format Text**:
```javascript
// Make characters 5-10 bold
quill.updateContents({
  ops: [
    { retain: 5 },                         // Skip to position 5
    { retain: 5, attributes: { bold: true } }  // Format next 5 chars
  ]
});
```

**Complex Update**:
```javascript
// Delete 3 chars at position 2, insert "New", format next 5 chars
quill.updateContents({
  ops: [
    { retain: 2 },                          // Skip to position 2
    { delete: 3 },                          // Delete 3 chars
    { insert: 'New ' },                     // Insert text
    { retain: 5, attributes: { bold: true } } // Format
  ]
});
```

**Applying Text Changes**:
```javascript
// Listen for changes and log deltas
quill.on('text-change', (delta, oldDelta, source) => {
  console.log('Change delta:', delta);

  // Apply same change to another editor
  otherQuill.updateContents(delta);
});
```

**Use Cases**:
- Real-time collaboration (applying remote changes)
- Implementing custom editing operations
- Programmatic formatting
- Undo/redo with deltas

**See Also**: `categories/delta.md` for Delta operations reference

---

## Source Parameter

All modification methods accept an optional `source` parameter controlling event behavior.

**Values**:
- `'user'` - Triggered by user interaction (default for UI events)
- `'api'` - Triggered by API call (default for method calls)
- `'silent'` - Suppresses `text-change` event (still fires `editor-change`)

**Examples**:
```javascript
// Default (api source)
quill.insertText(0, 'Hello');

// Explicit user source
quill.insertText(0, 'Hello', 'user');

// Silent (no text-change event)
quill.insertText(0, 'Hello', 'silent');
```

**Event Behavior**:
```javascript
quill.on('text-change', (delta, oldDelta, source) => {
  console.log('Source:', source); // 'user', 'api', or 'silent'
});

// 'silent' changes do NOT trigger this event
```

**See Also**: `categories/api-events.md` for event documentation

---

## Common Patterns

### Auto-save Content
```javascript
let saveTimeout;
quill.on('text-change', () => {
  clearTimeout(saveTimeout);
  saveTimeout = setTimeout(() => {
    const delta = quill.getContents();
    localStorage.setItem('draft', JSON.stringify(delta));
  }, 1000);
});
```

### Character Counter
```javascript
function updateCounter() {
  const length = quill.getLength() - 1; // Exclude trailing newline
  document.getElementById('counter').textContent = `${length} characters`;
}

quill.on('text-change', updateCounter);
updateCounter(); // Initial count
```

### Insert at Cursor
```javascript
function insertAtCursor(text) {
  const range = quill.getSelection(true); // Focus if needed
  quill.insertText(range.index, text);
  quill.setSelection(range.index + text.length);
}

insertAtCursor('Inserted!');
```

### Clear Formatting
```javascript
function clearFormatting() {
  const length = quill.getLength();
  const delta = quill.getContents();

  // Strip attributes from all ops
  const plainDelta = {
    ops: delta.ops.map(op => ({ insert: op.insert }))
  };

  quill.setContents(plainDelta);
}
```

---

## Official Documentation

**URL**: https://quilljs.com/docs/api/#content

---

## Next Steps

- **Formatting**: See `categories/api-formatting.md` for format methods
- **Selection**: See `categories/api-selection.md` for cursor control
- **Events**: See `categories/api-events.md` for change listeners
- **Delta**: See `categories/delta.md` for document model details
