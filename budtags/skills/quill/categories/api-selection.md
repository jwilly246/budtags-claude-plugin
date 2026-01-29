# Quill Selection API

Complete reference for all 4 selection and positioning methods in Quill.js.

---

## Overview

Selection methods control cursor position and text selection within the editor. These methods are essential for:

- Getting/setting cursor position
- Programmatically selecting text
- Positioning tooltips and UI elements
- Scrolling content into view

**Core Methods**:
- `getSelection()` - Get current cursor/selection
- `setSelection()` - Set cursor position or select text
- `getBounds()` - Get pixel coordinates for positioning
- `scrollSelectionIntoView()` - Ensure selection is visible

---

## getSelection()

Retrieves the current user selection or cursor position.

**Signature**:
```typescript
getSelection(focus?: boolean): { index: number, length: number } | null
```

**Parameters**:
- `focus` - If `true`, focus editor before getting selection (default: `false`)

**Returns**:
- Range object `{ index, length }` if selection exists
- `null` if editor is not focused

**Examples**:

**Get Current Selection**:
```javascript
// Get selection (null if not focused)
const range = quill.getSelection();
if (range) {
  console.log('Cursor at:', range.index);
  console.log('Selection length:', range.length);
} else {
  console.log('Editor not focused');
}
```

**Focus and Get Selection**:
```javascript
// Focus editor and get selection (always returns range)
const range = quill.getSelection(true);
console.log('Selection:', range);
// { index: 10, length: 5 }
```

**Check if Text is Selected**:
```javascript
const range = quill.getSelection();
if (range) {
  if (range.length === 0) {
    console.log('Cursor at position', range.index);
  } else {
    console.log(`Selected ${range.length} characters starting at ${range.index}`);
  }
}
```

**Get Selected Text**:
```javascript
const range = quill.getSelection();
if (range && range.length > 0) {
  const text = quill.getText(range.index, range.length);
  console.log('Selected text:', text);
}
```

**Insert at Cursor**:
```javascript
function insertAtCursor(text) {
  const range = quill.getSelection(true);
  quill.insertText(range.index, text);
  quill.setSelection(range.index + text.length);
}

insertAtCursor('Hello!');
```

**Important Notes**:
- Returns `null` when editor **not focused** (unless `focus: true`)
- **Cursor position**: `{ index: n, length: 0 }`
- **Text selection**: `{ index: n, length: > 0 }`
- Use `focus: true` for programmatic operations requiring selection

**Common Pitfall**:
```javascript
// ❌ WRONG - may return null if editor lost focus
const range = quill.getSelection();
quill.insertText(range.index, 'text'); // Error if range is null

// ✅ CORRECT - ensures range exists
const range = quill.getSelection(true);
quill.insertText(range.index, 'text');
```

**Use Cases**:
- Inserting content at cursor
- Getting selected text
- Format toolbar state updates
- Custom editing operations

---

## setSelection()

Sets the cursor position or selects a text range.

**Signature**:
```typescript
setSelection(index: number, length?: number, source?: string): void
setSelection(range: { index: number, length: number }, source?: string): void
```

**Parameters**:
- `index` - Position to place cursor or start selection (0-based)
- `length` - Number of characters to select (default: 0 for cursor only)
- `range` - Range object `{ index, length }`
- `source` - Optional change source (`'user'`, `'api'`, `'silent'`)

**Returns**: `void`

**Examples**:

**Position Cursor**:
```javascript
// Place cursor at position 10
quill.setSelection(10);

// Same as above
quill.setSelection(10, 0);

// Place cursor at end of document
quill.setSelection(quill.getLength());
```

**Select Text Range**:
```javascript
// Select characters 5-15
quill.setSelection(5, 10);

// Select entire document
quill.setSelection(0, quill.getLength());

// Using range object
quill.setSelection({ index: 5, length: 10 });
```

**Focus Editor**:
```javascript
// Focus editor (place cursor at start)
quill.setSelection(0, 0);

// Focus and restore last selection
const lastRange = quill.getSelection();
// ... user clicks away ...
quill.setSelection(lastRange);
```

**Position After Insert**:
```javascript
// Insert text and move cursor after it
const range = quill.getSelection(true);
const text = 'Inserted text';
quill.insertText(range.index, text);
quill.setSelection(range.index + text.length);
```

**Select Word at Cursor**:
```javascript
function selectWordAtCursor() {
  const range = quill.getSelection(true);
  const text = quill.getText();

  // Find word boundaries
  let start = range.index;
  let end = range.index;

  while (start > 0 && /\w/.test(text[start - 1])) start--;
  while (end < text.length && /\w/.test(text[end])) end++;

  quill.setSelection(start, end - start);
}
```

**Expand Selection**:
```javascript
// Expand selection by 5 characters in each direction
const range = quill.getSelection();
if (range) {
  const newIndex = Math.max(0, range.index - 5);
  const newLength = range.length + 10;
  quill.setSelection(newIndex, newLength);
}
```

**Event Source**:
```javascript
// Silent selection (no selection-change event)
quill.setSelection(10, 5, 'silent');

// User source (triggers as if user selected)
quill.setSelection(10, 5, 'user');
```

**Important Notes**:
- Automatically **focuses editor**
- `length: 0` creates cursor, `length > 0` creates selection
- Triggers `selection-change` event (unless source is `'silent'`)
- Bounded by document length (won't exceed `getLength()`)

**Use Cases**:
- Moving cursor after insertions
- Programmatic text selection
- Focus management
- Custom keyboard shortcuts

---

## getBounds()

Retrieves pixel coordinates and dimensions for a position or range (for tooltip/UI positioning).

**Signature**:
```typescript
getBounds(index: number, length?: number): {
  bottom: number,
  height: number,
  left: number,
  right: number,
  top: number,
  width: number
}
```

**Parameters**:
- `index` - Position to measure (0-based)
- `length` - Range length (default: 0)

**Returns**: Bounds object with pixel coordinates relative to editor container

**Examples**:

**Get Cursor Position**:
```javascript
// Get cursor pixel position
const range = quill.getSelection();
if (range) {
  const bounds = quill.getBounds(range.index);
  console.log('Cursor at:', bounds);
  // {
  //   bottom: 120,
  //   height: 20,
  //   left: 150,
  //   right: 152,
  //   top: 100,
  //   width: 2
  // }
}
```

**Position Tooltip at Cursor**:
```javascript
function showTooltip(message) {
  const range = quill.getSelection();
  if (!range) return;

  const bounds = quill.getBounds(range.index);
  const tooltip = document.getElementById('tooltip');

  tooltip.textContent = message;
  tooltip.style.left = bounds.left + 'px';
  tooltip.style.top = (bounds.bottom + 5) + 'px';
  tooltip.style.display = 'block';
}

showTooltip('Formatting help...');
```

**Position Popup Menu**:
```javascript
function showContextMenu(event) {
  event.preventDefault();

  const range = quill.getSelection(true);
  const bounds = quill.getBounds(range.index, range.length);

  const menu = document.getElementById('context-menu');
  menu.style.left = event.pageX + 'px';
  menu.style.top = event.pageY + 'px';
  menu.style.display = 'block';

  // Alternative: Position at selection bounds
  // menu.style.left = bounds.right + 'px';
  // menu.style.top = bounds.top + 'px';
}

quill.root.addEventListener('contextmenu', showContextMenu);
```

**Inline Toolbar (Bubble Theme Style)**:
```javascript
function updateInlineToolbar() {
  const range = quill.getSelection();

  if (range && range.length > 0) {
    const bounds = quill.getBounds(range.index, range.length);
    const toolbar = document.getElementById('inline-toolbar');

    // Center toolbar above selection
    const toolbarWidth = toolbar.offsetWidth;
    const selectionCenter = bounds.left + (bounds.width / 2);

    toolbar.style.left = (selectionCenter - toolbarWidth / 2) + 'px';
    toolbar.style.top = (bounds.top - toolbar.offsetHeight - 5) + 'px';
    toolbar.style.display = 'block';
  } else {
    document.getElementById('inline-toolbar').style.display = 'none';
  }
}

quill.on('selection-change', updateInlineToolbar);
```

**Bounds for Range**:
```javascript
// Get bounds for characters 10-20
const bounds = quill.getBounds(10, 10);

// Bounds span the entire selection
console.log('Selection starts at:', bounds.left, bounds.top);
console.log('Selection ends at:', bounds.right, bounds.bottom);
console.log('Selection dimensions:', bounds.width, 'x', bounds.height);
```

**Coordinate System**:
```javascript
// Coordinates are relative to editor container
const editorRect = quill.container.getBoundingClientRect();
const bounds = quill.getBounds(0);

// Convert to page coordinates
const pageX = editorRect.left + bounds.left;
const pageY = editorRect.top + bounds.top;
```

**Important Notes**:
- Coordinates are **relative to editor container**
- Bounds represent the **visible area** of the range
- For multi-line selections, bounds span from start to end
- Use for **tooltip, popover, and menu positioning**

**Use Cases**:
- Tooltip positioning
- Context menu placement
- Inline toolbars
- Autocomplete dropdowns
- Custom UI overlays

---

## scrollSelectionIntoView()

Scrolls the current selection into the visible viewport.

**Signature**:
```typescript
scrollSelectionIntoView(): void
```

**Parameters**: None

**Returns**: `void`

**Examples**:

**Basic Usage**:
```javascript
// Ensure current selection is visible
quill.scrollSelectionIntoView();
```

**After Programmatic Selection**:
```javascript
// Select text and ensure it's visible
quill.setSelection(500, 10);
quill.scrollSelectionIntoView();
```

**After Content Change**:
```javascript
// Insert text at end and scroll to it
const length = quill.getLength();
quill.insertText(length, 'New content at end');
quill.setSelection(length);
quill.scrollSelectionIntoView();
```

**Search and Scroll**:
```javascript
function findAndScrollTo(searchTerm) {
  const text = quill.getText();
  const index = text.indexOf(searchTerm);

  if (index !== -1) {
    quill.setSelection(index, searchTerm.length);
    quill.scrollSelectionIntoView();
  }
}

findAndScrollTo('important');
```

**Scroll to Line**:
```javascript
function scrollToLine(lineNumber) {
  const lines = quill.getLines(0, quill.getLength());
  if (lineNumber < lines.length) {
    const line = lines[lineNumber];
    const index = quill.getIndex(line);
    quill.setSelection(index);
    quill.scrollSelectionIntoView();
  }
}

scrollToLine(10);
```

**Scroll After Blur/Focus**:
```javascript
// When editor regains focus, scroll to last selection
let lastRange = null;

quill.on('selection-change', (range) => {
  if (range) {
    lastRange = range;
  }
});

document.getElementById('editor').addEventListener('focus', () => {
  if (lastRange) {
    quill.setSelection(lastRange);
    quill.scrollSelectionIntoView();
  }
});
```

**Important Notes**:
- Scrolls **editor container**, not the page
- Only affects **scrollable editors** (with overflow)
- Automatically called by `setSelection` in some cases
- **No effect** if selection already visible

**Alternative (Advanced)**:
```javascript
// Scroll to specific pixel coordinates
const bounds = quill.getBounds(100);
quill.scrollRectIntoView(bounds); // Experimental API
```

**Use Cases**:
- Search and highlight
- Programmatic selection
- Jump to line/position
- Restoring scroll position
- Ensuring inserted content is visible

---

## Common Selection Patterns

### Save and Restore Selection
```javascript
let savedRange = null;

function saveSelection() {
  savedRange = quill.getSelection();
}

function restoreSelection() {
  if (savedRange) {
    quill.setSelection(savedRange);
  }
}

// Use around operations that might lose focus
saveSelection();
// ... perform operation ...
restoreSelection();
```

### Select All
```javascript
function selectAll() {
  quill.setSelection(0, quill.getLength());
}

// Keyboard shortcut
quill.keyboard.addBinding({
  key: 'A',
  shortKey: true,
  handler: function() {
    selectAll();
    return false; // Prevent default
  }
});
```

### Smart Word Selection
```javascript
function selectWordUnderCursor() {
  const range = quill.getSelection(true);
  const [leaf, offset] = quill.getLeaf(range.index);

  if (leaf && leaf.text) {
    const text = leaf.text;
    let start = offset;
    let end = offset;

    // Find word boundaries
    while (start > 0 && /\w/.test(text[start - 1])) start--;
    while (end < text.length && /\w/.test(text[end])) end++;

    const leafIndex = quill.getIndex(leaf);
    quill.setSelection(leafIndex + start, end - start);
  }
}
```

### Autocomplete Dropdown
```javascript
let autocompleteList = null;

function showAutocomplete(suggestions) {
  const range = quill.getSelection(true);
  const bounds = quill.getBounds(range.index);

  autocompleteList = document.getElementById('autocomplete');
  autocompleteList.innerHTML = suggestions
    .map(s => `<div class="item">${s}</div>`)
    .join('');

  autocompleteList.style.left = bounds.left + 'px';
  autocompleteList.style.top = bounds.bottom + 'px';
  autocompleteList.style.display = 'block';

  // Position completion items
  autocompleteList.querySelectorAll('.item').forEach(item => {
    item.addEventListener('click', () => {
      insertCompletion(item.textContent);
    });
  });
}

function insertCompletion(text) {
  const range = quill.getSelection(true);
  // Delete partial word and insert completion
  quill.deleteText(range.index - currentWord.length, currentWord.length);
  quill.insertText(range.index - currentWord.length, text);
  quill.setSelection(range.index - currentWord.length + text.length);

  autocompleteList.style.display = 'none';
}
```

### Scroll to Top/Bottom
```javascript
function scrollToTop() {
  quill.setSelection(0, 0);
  quill.scrollSelectionIntoView();
}

function scrollToBottom() {
  const length = quill.getLength();
  quill.setSelection(length, 0);
  quill.scrollSelectionIntoView();
}
```

### Highlight Search Results
```javascript
function highlightSearchResults(searchTerm) {
  const text = quill.getText();
  const indices = [];
  let index = text.indexOf(searchTerm);

  // Find all matches
  while (index !== -1) {
    indices.push(index);
    index = text.indexOf(searchTerm, index + 1);
  }

  // Highlight all matches
  indices.forEach(i => {
    quill.formatText(i, searchTerm.length, {
      background: '#ffff00'
    }, 'silent');
  });

  // Scroll to first match
  if (indices.length > 0) {
    quill.setSelection(indices[0], searchTerm.length);
    quill.scrollSelectionIntoView();
  }
}
```

### Maintain Selection After Format
```javascript
function formatPreservingSelection(format, value) {
  const range = quill.getSelection(true);

  if (range && range.length > 0) {
    quill.formatText(range.index, range.length, format, value);
    quill.setSelection(range); // Restore selection
  }
}

formatPreservingSelection('bold', true);
```

---

## Selection Events

Track selection changes to update UI or trigger actions:

```javascript
quill.on('selection-change', (range, oldRange, source) => {
  if (range) {
    if (range.length === 0) {
      console.log('Cursor at:', range.index);
    } else {
      console.log('Selected:', range.index, 'to', range.index + range.length);
    }
  } else {
    console.log('Editor lost focus');
  }
});
```

**See Also**: `categories/api-events.md` for event details

---

## Official Documentation

**URL**: https://quilljs.com/docs/api/#selection

---

## Next Steps

- **Content**: See `categories/api-content.md` for content manipulation
- **Formatting**: See `categories/api-formatting.md` for format methods
- **Events**: See `categories/api-events.md` for selection-change event
- **Model**: See `categories/api-model.md` for getLeaf/getLine methods
