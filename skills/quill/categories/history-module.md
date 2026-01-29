# History Module

## Overview

The History module records and manages undo/redo functionality in Quill. It tracks user changes and allows reverting or reapplying them.

**Official Documentation:** https://quilljs.com/docs/modules/history

## Configuration

```javascript
const quill = new Quill('#editor', {
  modules: {
    history: {
      delay: 1000,      // Merge changes within 1s into single undo step
      maxStack: 100,    // Max undo/redo stack size
      userOnly: false   // Track all changes (not just user-initiated)
    }
  }
});
```

## Configuration Options

### delay

Time in milliseconds to merge consecutive changes into single undo step:

```javascript
modules: {
  history: {
    delay: 2000  // Merge changes within 2 seconds
  }
}
```

**Default:** `1000` (1 second)

**Use cases:**
- Higher values (2000-3000ms): Better for continuous typing - fewer undo steps
- Lower values (500-1000ms): Better for precise editing - more granular undo
- `0`: Each change is separate undo step (not recommended for typing)

### maxStack

Maximum number of undo/redo operations to track:

```javascript
modules: {
  history: {
    maxStack: 500  // Keep 500 undo steps
  }
}
```

**Default:** `100`

**Use cases:**
- Higher values: More history, more memory usage
- Lower values: Less memory, shorter undo history
- Consider document size and expected editing patterns

### userOnly

Whether to track only user-initiated changes:

```javascript
modules: {
  history: {
    userOnly: true  // Only track user changes
  }
}
```

**Default:** `false` (track all changes)

**Use cases:**
- `true`: Don't track programmatic changes (API calls, paste conversions)
- `false`: Track all changes including programmatic ones

```javascript
// Example with userOnly: true
quill.setText('Hello');  // Not tracked (API call)

// User types "World"    // Tracked (user action)
```

## API Methods

### clear()

Clear undo and redo history:

```typescript
clear(): void
```

```javascript
const history = quill.getModule('history');

// Clear all history
history.clear();

// Useful after:
// - Setting initial content
// - Loading document
// - Resetting editor
```

**Example - Load Content Without Undo:**

```javascript
// Load content
quill.setContents(loadedDelta);

// Clear history so user can't undo to blank state
const history = quill.getModule('history');
history.clear();
```

### cutoff()

Create a cutoff point in history (next change starts new undo step):

```typescript
cutoff(): void
```

```javascript
const history = quill.getModule('history');

// Make some changes
quill.insertText(0, 'First change');

// Force new undo step
history.cutoff();

// Next change will be separate undo step (even if within delay)
quill.insertText(0, 'Second change');
```

**Use cases:**
- Force separation between related changes
- Create logical grouping boundaries
- Reset merge delay timer

### undo()

Undo last change:

```typescript
undo(): void
```

```javascript
const history = quill.getModule('history');

// Undo last change
history.undo();

// Can also trigger with keyboard
quill.keyboard.addBinding({
  key: 'Z',
  shortKey: true,
  handler: function() {
    this.quill.history.undo();
  }
});
```

### redo()

Redo last undone change:

```typescript
redo(): void
```

```javascript
const history = quill.getModule('history');

// Redo last undone change
history.redo();

// Keyboard binding
quill.keyboard.addBinding({
  key: 'Z',
  shortKey: true,
  shiftKey: true,
  handler: function() {
    this.quill.history.redo();
  }
});
```

## Complete Examples

### Basic Setup

```javascript
const quill = new Quill('#editor', {
  modules: {
    history: {
      delay: 1000,
      maxStack: 100,
      userOnly: false
    }
  },
  theme: 'snow'
});

// Get history module
const history = quill.getModule('history');

// Undo/redo buttons
document.getElementById('undo-btn').addEventListener('click', () => {
  history.undo();
});

document.getElementById('redo-btn').addEventListener('click', () => {
  history.redo();
});
```

### Load Content Without Undo

```javascript
const quill = new Quill('#editor', {
  modules: {
    history: {
      delay: 1000,
      userOnly: false
    }
  }
});

// Load saved content
async function loadDocument(docId) {
  const response = await fetch(`/api/documents/${docId}`);
  const data = await response.json();

  // Set content
  quill.setContents(data.content);

  // Clear history so user can't undo to blank
  const history = quill.getModule('history');
  history.clear();
}
```

### Track Undo Stack State

```javascript
const quill = new Quill('#editor', {
  modules: {
    history: {
      delay: 1000,
      maxStack: 100
    }
  }
});

const history = quill.getModule('history');

// Track stack state
quill.on('text-change', (delta, oldDelta, source) => {
  // Access internal stack (not officially documented)
  const undoBtn = document.getElementById('undo-btn');
  const redoBtn = document.getElementById('redo-btn');

  // Enable/disable buttons based on stack
  undoBtn.disabled = history.stack.undo.length === 0;
  redoBtn.disabled = history.stack.redo.length === 0;
});
```

### Programmatic Changes Without History

```javascript
const quill = new Quill('#editor', {
  modules: {
    history: {
      userOnly: true  // Don't track programmatic changes
    }
  }
});

// This won't be added to undo stack
quill.setText('Template text');

// This will be tracked (user-initiated)
// User types in editor...
```

### Custom Undo/Redo UI

```javascript
const quill = new Quill('#editor', {
  modules: {
    toolbar: [['bold', 'italic']],
    history: {
      delay: 1000,
      maxStack: 100
    }
  }
});

const history = quill.getModule('history');

// Create custom undo/redo toolbar
const toolbar = quill.getModule('toolbar');

// Add custom buttons
const undoBtn = document.createElement('button');
undoBtn.innerHTML = '↶ Undo';
undoBtn.className = 'ql-undo';
undoBtn.addEventListener('click', () => history.undo());

const redoBtn = document.createElement('button');
redoBtn.innerHTML = '↷ Redo';
redoBtn.className = 'ql-redo';
redoBtn.addEventListener('click', () => history.redo());

toolbar.container.prepend(redoBtn);
toolbar.container.prepend(undoBtn);

// Update button state
quill.on('text-change', () => {
  undoBtn.disabled = history.stack.undo.length === 0;
  redoBtn.disabled = history.stack.redo.length === 0;
});
```

### Logical Grouping with Cutoff

```javascript
const quill = new Quill('#editor', {
  modules: {
    history: {
      delay: 2000  // 2s merge window
    }
  }
});

const history = quill.getModule('history');

// Function that makes multiple related changes
function insertTemplate() {
  quill.insertText(0, 'Title\n', { header: 1 });
  quill.insertText(7, 'Content goes here...\n');
  quill.insertText(28, 'Signature\n', { bold: true });

  // Force cutoff so all template insertions are one undo step
  history.cutoff();
}

// Template becomes single undo
insertTemplate();

// Next user edit will be separate undo
```

### Auto-Save with History Tracking

```javascript
const quill = new Quill('#editor', {
  modules: {
    history: {
      delay: 1000,
      maxStack: 100
    }
  }
});

const history = quill.getModule('history');

// Track changes for auto-save
let changeCount = 0;
const SAVE_THRESHOLD = 10;

quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user') {
    changeCount++;

    // Auto-save every 10 changes
    if (changeCount >= SAVE_THRESHOLD) {
      saveDocument();
      changeCount = 0;

      // Optional: Create cutoff point after save
      history.cutoff();
    }
  }
});

async function saveDocument() {
  const content = quill.getContents();
  await fetch('/api/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  });
  console.log('Auto-saved');
}
```

## Undo/Redo Behavior

### Stack Management

- Changes are grouped by `delay` window
- Each group becomes one undo step
- Redo stack cleared when new change is made
- Max stack size prevents memory issues

```javascript
// Timeline with delay: 1000ms
// 0ms: User types "H"
// 100ms: User types "e"
// 200ms: User types "l"
// 300ms: User types "l"
// 400ms: User types "o"
// 1500ms: User types " "
// 1600ms: User types "W"

// Results in 2 undo steps:
// 1. "Hello" (merged within 1s)
// 2. " W" (separate after delay)
```

### Programmatic vs User Changes

```javascript
// With userOnly: true
quill.setText('API change');      // Not tracked
// User types "User change"        // Tracked

// With userOnly: false (default)
quill.setText('API change');      // Tracked
// User types "User change"        // Tracked
```

### Redo Invalidation

```javascript
// Make change
quill.insertText(0, 'A');

// Undo it
history.undo();

// Make new change - redo stack is now cleared
quill.insertText(0, 'B');

// Can't redo 'A' anymore
history.redo();  // No effect
```

## TypeScript Support

```typescript
import Quill from 'quill';

interface HistoryOptions {
  delay?: number;
  maxStack?: number;
  userOnly?: boolean;
}

const quill = new Quill('#editor', {
  modules: {
    history: {
      delay: 1000,
      maxStack: 100,
      userOnly: false
    } as HistoryOptions
  }
});

// Get history module
interface HistoryModule {
  clear(): void;
  cutoff(): void;
  undo(): void;
  redo(): void;
  stack: {
    undo: any[];
    redo: any[];
  };
}

const history = quill.getModule('history') as HistoryModule;
history.undo();
history.redo();
history.clear();
```

## Performance Considerations

- Higher `maxStack` values use more memory
- Each undo step stores Delta operations
- Consider document size when setting `maxStack`
- Use `userOnly: true` to reduce tracked changes
- Clear history after loading large documents

## Related Files

- **configuration.md** - Module configuration
- **delta.md** - Delta format used for undo/redo operations
- **keyboard-module.md** - Keyboard shortcuts for undo/redo
- **events.md** - text-change events that trigger history

## Notes

- Default keyboard shortcuts: Ctrl/Cmd+Z (undo), Ctrl/Cmd+Shift+Z (redo)
- History module is enabled by default in Snow and Bubble themes
- Undo/redo works with all content types (text, formatting, embeds)
- Collaborative editing requires custom history implementation
