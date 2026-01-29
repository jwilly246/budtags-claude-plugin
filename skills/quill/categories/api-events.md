# Quill Events API

Complete reference for Quill's event system including all 3 events and event management methods.

---

## Overview

Quill provides a robust event system for monitoring editor changes and user interactions. The event system includes:

**Core Events**:
- `text-change` - Fired when document content changes
- `selection-change` - Fired when cursor/selection changes
- `editor-change` - Fired for any change (text or selection)

**Event Methods**:
- `on()` - Register event listener
- `once()` - Register one-time event listener
- `off()` - Remove event listener

All events provide detailed information about what changed and why.

---

## text-change Event

Fired whenever the document content is modified.

**Callback Signature**:
```typescript
(delta: Delta, oldContents: Delta, source: string) => void
```

**Parameters**:
- `delta` - Delta describing the change
- `oldContents` - Document contents before change
- `source` - Change source (`'user'`, `'api'`, `'silent'`)

**Examples**:

**Basic Listener**:
```javascript
quill.on('text-change', (delta, oldDelta, source) => {
  console.log('Text changed!');
  console.log('Change:', delta);
  console.log('Was:', oldDelta);
  console.log('Source:', source);
});
```

**Track User Changes**:
```javascript
quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user') {
    console.log('User made a change');
    saveToAutoDraft();
  }
});
```

**Character Counter**:
```javascript
quill.on('text-change', () => {
  const length = quill.getLength() - 1; // Exclude trailing newline
  document.getElementById('counter').textContent = `${length} characters`;
});
```

**Auto-Save**:
```javascript
let saveTimeout;

quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user') {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
      const content = quill.getContents();
      localStorage.setItem('draft', JSON.stringify(content));
      console.log('Auto-saved');
    }, 1000);
  }
});
```

**Validate Changes**:
```javascript
quill.on('text-change', (delta, oldDelta, source) => {
  const text = quill.getText();

  // Enforce max length
  if (text.length > 1000) {
    quill.setContents(oldDelta, 'silent');
    alert('Maximum length exceeded!');
  }
});
```

**Collaborative Editing**:
```javascript
quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user') {
    // Send change to server
    socket.emit('text-change', delta);
  }
});

// Apply remote changes
socket.on('text-change', (delta) => {
  quill.updateContents(delta, 'api');
});
```

**Track Specific Changes**:
```javascript
quill.on('text-change', (delta) => {
  delta.ops.forEach(op => {
    if (op.insert) {
      console.log('Inserted:', op.insert);
    }
    if (op.delete) {
      console.log('Deleted', op.delete, 'characters');
    }
    if (op.retain && op.attributes) {
      console.log('Formatted:', op.attributes);
    }
  });
});
```

**Undo/Redo Tracking**:
```javascript
const history = [];
const maxHistory = 50;

quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user') {
    history.push({
      delta: delta,
      oldContents: oldDelta,
      timestamp: Date.now()
    });

    if (history.length > maxHistory) {
      history.shift();
    }
  }
});
```

**Important Notes**:
- Fired for **all content changes** (insertions, deletions, formatting)
- **NOT fired** for `source: 'silent'`
- Provides **complete change history** via delta
- Can be triggered by user typing, API calls, or undo/redo

**What Triggers text-change**:
- User typing/deleting text
- Copy/paste operations
- Formatting changes (bold, color, etc.)
- API calls (`insertText`, `deleteText`, `formatText`, etc.)
- Undo/redo operations

**What Does NOT Trigger**:
- Selection changes (cursor movement)
- Focus/blur events
- Read-only state changes
- Changes with `source: 'silent'`

---

## selection-change Event

Fired whenever the cursor position or text selection changes.

**Callback Signature**:
```typescript
(range: { index: number, length: number } | null, oldRange: { index: number, length: number } | null, source: string) => void
```

**Parameters**:
- `range` - New selection range (or `null` if editor lost focus)
- `oldRange` - Previous selection range
- `source` - Change source (`'user'`, `'api'`, `'silent'`)

**Examples**:

**Basic Listener**:
```javascript
quill.on('selection-change', (range, oldRange, source) => {
  if (range) {
    if (range.length === 0) {
      console.log('Cursor at:', range.index);
    } else {
      console.log('Selection:', range.index, 'to', range.index + range.length);
    }
  } else {
    console.log('Editor lost focus');
  }
});
```

**Update Toolbar**:
```javascript
quill.on('selection-change', (range) => {
  if (range) {
    const format = quill.getFormat(range);

    // Update button states
    document.getElementById('bold-btn').classList.toggle('active', format.bold);
    document.getElementById('italic-btn').classList.toggle('active', format.italic);

    // Update color picker
    if (format.color) {
      document.getElementById('color-picker').value = format.color;
    }
  }
});
```

**Focus/Blur Detection**:
```javascript
quill.on('selection-change', (range, oldRange, source) => {
  if (range === null && oldRange !== null) {
    console.log('Editor lost focus (blur)');
    onBlur();
  } else if (range !== null && oldRange === null) {
    console.log('Editor gained focus');
    onFocus();
  }
});
```

**Show Inline Toolbar**:
```javascript
let inlineToolbar = document.getElementById('inline-toolbar');

quill.on('selection-change', (range) => {
  if (range && range.length > 0) {
    const bounds = quill.getBounds(range.index, range.length);

    inlineToolbar.style.left = bounds.left + 'px';
    inlineToolbar.style.top = (bounds.top - 40) + 'px';
    inlineToolbar.style.display = 'block';
  } else {
    inlineToolbar.style.display = 'none';
  }
});
```

**Track Cursor Position**:
```javascript
quill.on('selection-change', (range) => {
  if (range && range.length === 0) {
    const [line, offset] = quill.getLine(range.index);
    const lineNumber = quill.getLines(0, range.index).length;

    console.log(`Line ${lineNumber}, Column ${offset}`);
    document.getElementById('position').textContent = `${lineNumber}:${offset}`;
  }
});
```

**Auto-Complete Trigger**:
```javascript
quill.on('selection-change', (range) => {
  if (range && range.length === 0) {
    const [leaf, offset] = quill.getLeaf(range.index);
    const text = leaf.text || '';
    const beforeCursor = text.substring(0, offset);

    // Check for @ mention
    if (beforeCursor.endsWith('@')) {
      showMentionAutocomplete(range.index);
    }
  }
});
```

**Save Scroll Position**:
```javascript
let lastRange = null;

quill.on('selection-change', (range) => {
  if (range) {
    lastRange = range;
  }
});

// Restore on focus
quill.root.addEventListener('focus', () => {
  if (lastRange) {
    quill.setSelection(lastRange, 'silent');
  }
});
```

**Important Notes**:
- Fired for **cursor movement and selection changes**
- `range === null` indicates editor **lost focus**
- Also fired for `source: 'silent'` (unlike `text-change`)
- Can be triggered by mouse clicks, keyboard arrows, or API calls

**What Triggers selection-change**:
- User clicks in editor
- User uses arrow keys
- User selects text with mouse/keyboard
- API calls (`setSelection`, `focus`, `blur`)
- Focus/blur events

**What Does NOT Trigger**:
- Text content changes (use `text-change`)
- Formatting changes without selection movement

---

## editor-change Event

Meta-event fired for ANY change (either `text-change` OR `selection-change`).

**Callback Signature**:
```typescript
(eventName: 'text-change' | 'selection-change', ...args: any[]) => void
```

**Parameters**:
- `eventName` - Which event occurred (`'text-change'` or `'selection-change'`)
- `...args` - Arguments from the specific event

**Examples**:

**Basic Listener**:
```javascript
quill.on('editor-change', (eventName, ...args) => {
  if (eventName === 'text-change') {
    const [delta, oldDelta, source] = args;
    console.log('Text changed:', delta);
  } else if (eventName === 'selection-change') {
    const [range, oldRange, source] = args;
    console.log('Selection changed:', range);
  }
});
```

**Universal Change Logger**:
```javascript
quill.on('editor-change', (eventName, ...args) => {
  console.log('Editor event:', eventName);
  console.log('Args:', args);

  logActivity({
    type: eventName,
    timestamp: Date.now(),
    data: args
  });
});
```

**Mark as Dirty**:
```javascript
let isDirty = false;

quill.on('editor-change', (eventName, ...args) => {
  if (eventName === 'text-change') {
    const [delta, oldDelta, source] = args;
    if (source === 'user') {
      isDirty = true;
      updateSaveButton();
    }
  }
});
```

**Debounced Activity Tracker**:
```javascript
let activityTimeout;

quill.on('editor-change', () => {
  clearTimeout(activityTimeout);

  showActivityIndicator();

  activityTimeout = setTimeout(() => {
    hideActivityIndicator();
  }, 2000);
});
```

**Important Notes**:
- Convenience method for listening to **both** text and selection changes
- Fired **even with `source: 'silent'`** (unlike `text-change`)
- First argument is **event name**, rest are event-specific arguments

**Use Cases**:
- Universal change detection
- Activity indicators
- Logging all editor interactions
- Dirty state tracking

---

## on()

Registers an event listener.

**Signature**:
```typescript
on(eventName: string, handler: (...args: any[]) => void): void
```

**Parameters**:
- `eventName` - Event name (`'text-change'`, `'selection-change'`, `'editor-change'`)
- `handler` - Callback function

**Returns**: `void`

**Examples**:

**Register Listener**:
```javascript
function handleTextChange(delta, oldDelta, source) {
  console.log('Text changed!');
}

quill.on('text-change', handleTextChange);
```

**Multiple Listeners**:
```javascript
// Multiple listeners for same event
quill.on('text-change', listener1);
quill.on('text-change', listener2);
quill.on('text-change', listener3);

// All three will fire
```

**Arrow Function**:
```javascript
quill.on('selection-change', (range) => {
  console.log('Selection:', range);
});
```

**Method Reference**:
```javascript
class Editor {
  constructor() {
    this.quill = new Quill('#editor');
    this.quill.on('text-change', this.handleChange.bind(this));
  }

  handleChange(delta, oldDelta, source) {
    console.log('Changed:', delta);
  }
}
```

---

## once()

Registers a one-time event listener (automatically removed after first invocation).

**Signature**:
```typescript
once(eventName: string, handler: (...args: any[]) => void): void
```

**Parameters**:
- `eventName` - Event name
- `handler` - Callback function (called only once)

**Returns**: `void`

**Examples**:

**One-Time Listener**:
```javascript
quill.once('text-change', () => {
  console.log('First change detected!');
  // This will only fire once
});
```

**Initial Focus Detection**:
```javascript
quill.once('selection-change', (range) => {
  if (range) {
    console.log('Editor was focused for the first time');
    trackFirstInteraction();
  }
});
```

**Onboarding Trigger**:
```javascript
quill.once('text-change', () => {
  showTooltip('Great! You started typing. Here are some tips...');
});
```

**Important Notes**:
- Listener **automatically removed** after first call
- Useful for initialization or one-time actions
- More efficient than manually removing listener

---

## off()

Removes an event listener.

**Signature**:
```typescript
off(eventName: string, handler?: (...args: any[]) => void): void
```

**Parameters**:
- `eventName` - Event name
- `handler` - Specific callback to remove (optional)

**Returns**: `void`

**Examples**:

**Remove Specific Listener**:
```javascript
function handleChange(delta) {
  console.log('Changed');
}

quill.on('text-change', handleChange);

// Later, remove it
quill.off('text-change', handleChange);
```

**Remove All Listeners for Event**:
```javascript
// Remove ALL text-change listeners
quill.off('text-change');
```

**Cleanup on Destroy**:
```javascript
class EditorComponent {
  constructor() {
    this.quill = new Quill('#editor');
    this.textChangeHandler = this.onTextChange.bind(this);
    this.quill.on('text-change', this.textChangeHandler);
  }

  onTextChange(delta) {
    console.log('Changed');
  }

  destroy() {
    this.quill.off('text-change', this.textChangeHandler);
  }
}
```

**Temporary Listener**:
```javascript
function enableTracking() {
  quill.on('text-change', trackChanges);
}

function disableTracking() {
  quill.off('text-change', trackChanges);
}

function trackChanges(delta) {
  console.log('Tracking:', delta);
}
```

**Important Notes**:
- Must pass **same function reference** to remove specific listener
- Arrow functions **cannot be removed** unless stored in variable
- Omit handler to remove **all listeners** for event

**Cannot Remove (Arrow Function)**:
```javascript
// ❌ Cannot remove - function is anonymous
quill.on('text-change', (delta) => {
  console.log(delta);
});

quill.off('text-change'); // Must remove all listeners
```

**Can Remove (Stored Reference)**:
```javascript
// ✅ Can remove - function stored in variable
const handler = (delta) => console.log(delta);
quill.on('text-change', handler);
quill.off('text-change', handler); // Works!
```

---

## Source Parameter

All events include a `source` parameter indicating the change origin.

**Values**:
- `'user'` - User interaction (typing, clicking, dragging)
- `'api'` - Programmatic API call (insertText, setSelection, etc.)
- `'silent'` - Silent change (suppresses `text-change` but not `selection-change`)

**Examples**:

**Filter by Source**:
```javascript
quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user') {
    console.log('User made a change');
    saveAutoBackup();
  } else if (source === 'api') {
    console.log('Programmatic change');
  }
});
```

**Prevent Loops**:
```javascript
quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user') {
    // Transform user input
    const text = quill.getText();
    if (text.includes('bad-word')) {
      // Use 'api' source to avoid infinite loop
      quill.setText(text.replace('bad-word', '****'), 'api');
    }
  }
});
```

**Silent Source**:
```javascript
// text-change will NOT fire
quill.insertText(0, 'Silent insert', 'silent');

// selection-change WILL fire
quill.setSelection(10, 'silent');

// editor-change WILL fire for both
```

---

## Common Event Patterns

### Auto-Save with Debounce
```javascript
let saveTimeout;

quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user') {
    clearTimeout(saveTimeout);

    document.getElementById('status').textContent = 'Unsaved changes...';

    saveTimeout = setTimeout(() => {
      const content = quill.getContents();
      localStorage.setItem('draft', JSON.stringify(content));
      document.getElementById('status').textContent = 'Saved';
    }, 2000);
  }
});
```

### Undo/Redo Implementation
```javascript
const undoStack = [];
const redoStack = [];

quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user') {
    undoStack.push({
      delta: delta,
      oldContents: oldDelta
    });
    redoStack.length = 0; // Clear redo on new change
  }
});

function undo() {
  if (undoStack.length > 0) {
    const change = undoStack.pop();
    quill.setContents(change.oldContents, 'api');
    redoStack.push(change);
  }
}

function redo() {
  if (redoStack.length > 0) {
    const change = redoStack.pop();
    quill.updateContents(change.delta, 'api');
    undoStack.push(change);
  }
}
```

### Collaborative Editing
```javascript
// Send local changes to server
quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user') {
    socket.emit('edit', {
      delta: delta,
      userId: currentUser.id,
      timestamp: Date.now()
    });
  }
});

// Apply remote changes
socket.on('edit', (data) => {
  if (data.userId !== currentUser.id) {
    quill.updateContents(data.delta, 'api');
  }
});
```

### Smart Toolbar
```javascript
quill.on('selection-change', (range) => {
  const toolbar = document.getElementById('floating-toolbar');

  if (range && range.length > 0) {
    // Show toolbar for selection
    const bounds = quill.getBounds(range.index, range.length);
    const format = quill.getFormat(range);

    toolbar.style.left = bounds.left + 'px';
    toolbar.style.top = (bounds.top - 50) + 'px';
    toolbar.style.display = 'block';

    // Update button states
    updateToolbarButtons(format);
  } else {
    toolbar.style.display = 'none';
  }
});
```

### Word Counter
```javascript
function updateWordCount() {
  const text = quill.getText().trim();
  const words = text.split(/\s+/).filter(w => w.length > 0).length;
  const chars = quill.getLength() - 1;

  document.getElementById('word-count').textContent = `${words} words, ${chars} characters`;
}

quill.on('text-change', updateWordCount);
updateWordCount(); // Initial count
```

---

## Official Documentation

**URL**: https://quilljs.com/docs/api/#events

---

## Next Steps

- **Content API**: See `categories/api-content.md` for methods that trigger events
- **Selection API**: See `categories/api-selection.md` for selection-related events
- **Delta**: See `categories/delta.md` for understanding change deltas
- **Modules**: See `categories/history-module.md` for built-in undo/redo
