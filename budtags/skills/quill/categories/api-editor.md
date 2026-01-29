# Quill Editor Lifecycle API

Complete reference for all 6 editor lifecycle and state management methods in Quill.js.

---

## Overview

Editor lifecycle methods control focus, interactivity, and editor state updates. These methods manage:

- **Focus**: `focus()`, `blur()`, `hasFocus()`
- **Interactivity**: `enable()`, `disable()`
- **Synchronization**: `update()`
- **Scrolling**: `scrollRectIntoView()` (experimental)

**Common Use Cases**:
- Managing editor focus state
- Creating read-only modes
- Manual state synchronization
- Custom scroll behavior

---

## focus()

Gives focus to the editor and restores last selection.

**Signature**:
```typescript
focus(options?: { preventScroll?: boolean }): void
```

**Parameters**:
- `options.preventScroll` - If `true`, prevents scrolling to editor (default: `false`)

**Returns**: `void`

**Examples**:

**Basic Focus**:
```javascript
// Focus editor (scrolls into view)
quill.focus();
```

**Focus Without Scrolling**:
```javascript
// Focus but don't scroll (useful for off-screen editors)
quill.focus({ preventScroll: true });
```

**Focus on Page Load**:
```javascript
// Auto-focus editor when page loads
window.addEventListener('load', () => {
  quill.focus();
});
```

**Focus After Modal Open**:
```javascript
function openEditorModal() {
  const modal = document.getElementById('editor-modal');
  modal.style.display = 'block';

  // Focus editor after modal animation
  setTimeout(() => {
    quill.focus();
  }, 300);
}
```

**Restore Selection**:
```javascript
// focus() restores the last selection automatically
const range = quill.getSelection(); // { index: 10, length: 5 }
quill.blur();
// ... user does something else ...
quill.focus(); // Selection restored to { index: 10, length: 5 }
```

**Focus vs setSelection**:
```javascript
// focus() - Restores last selection
quill.focus();

// setSelection() - Sets specific selection AND focuses
quill.setSelection(0, 0); // Focus at start
```

**Important Notes**:
- Restores **last selection/cursor position**
- Triggers `selection-change` event
- Scrolls editor into view (unless `preventScroll: true`)
- If no previous selection, cursor placed at start

**Use Cases**:
- Auto-focus on page load
- Return focus after dialog/modal
- Focus after programmatic changes
- Keyboard navigation

---

## blur()

Removes focus from the editor.

**Signature**:
```typescript
blur(): void
```

**Parameters**: None

**Returns**: `void`

**Examples**:

**Basic Blur**:
```javascript
// Remove focus from editor
quill.blur();
```

**Blur on Save**:
```javascript
document.getElementById('save-btn').addEventListener('click', () => {
  const content = quill.getContents();
  saveToDatabase(content);

  quill.blur(); // Remove focus after save
});
```

**Blur on Escape**:
```javascript
quill.keyboard.addBinding({
  key: 'Escape',
  handler: function() {
    quill.blur();
    return false;
  }
});
```

**Toggle Focus**:
```javascript
function toggleFocus() {
  if (quill.hasFocus()) {
    quill.blur();
  } else {
    quill.focus();
  }
}
```

**Blur Before Validation**:
```javascript
function validateContent() {
  quill.blur(); // Ensure all changes committed

  const text = quill.getText().trim();
  if (text.length < 10) {
    alert('Content too short!');
    quill.focus(); // Return focus
    return false;
  }

  return true;
}
```

**Important Notes**:
- Triggers `selection-change` event with `null` range
- Hides cursor/selection
- Does **not** disable editor (use `disable()` for that)
- Selection is **saved** and restored on next `focus()`

**Event Behavior**:
```javascript
quill.on('selection-change', (range, oldRange, source) => {
  if (range === null) {
    console.log('Editor lost focus (blur)');
  }
});
```

**Use Cases**:
- Removing focus after save/submit
- Hiding toolbar/UI when not editing
- Form validation flows
- Modal/dialog interactions

---

## hasFocus()

Checks if the editor currently has focus.

**Signature**:
```typescript
hasFocus(): boolean
```

**Parameters**: None

**Returns**: `true` if editor is focused, `false` otherwise

**Examples**:

**Check Focus State**:
```javascript
if (quill.hasFocus()) {
  console.log('Editor is focused');
} else {
  console.log('Editor is not focused');
}
```

**Conditional Operations**:
```javascript
function insertTextIfFocused(text) {
  if (quill.hasFocus()) {
    const range = quill.getSelection();
    quill.insertText(range.index, text);
  } else {
    console.warn('Editor must be focused to insert text');
  }
}
```

**Toggle Focus Button**:
```javascript
function updateFocusButton() {
  const btn = document.getElementById('focus-btn');

  if (quill.hasFocus()) {
    btn.textContent = 'Blur';
    btn.classList.add('active');
  } else {
    btn.textContent = 'Focus';
    btn.classList.remove('active');
  }
}

quill.on('selection-change', updateFocusButton);
```

**Prevent Operations When Unfocused**:
```javascript
document.getElementById('format-btn').addEventListener('click', () => {
  if (!quill.hasFocus()) {
    quill.focus(); // Focus first
  }

  quill.format('bold', true);
});
```

**Auto-save Only When Focused**:
```javascript
function autoSave() {
  if (quill.hasFocus()) {
    const content = quill.getContents();
    localStorage.setItem('draft', JSON.stringify(content));
  }
}

setInterval(autoSave, 5000);
```

**UI State Management**:
```javascript
function updateUI() {
  const toolbar = document.getElementById('toolbar');

  if (quill.hasFocus()) {
    toolbar.classList.add('active');
  } else {
    toolbar.classList.remove('inactive');
  }
}

quill.on('selection-change', updateUI);
```

**Important Notes**:
- Reflects **current focus state**
- More reliable than `getSelection() !== null`
- Useful for conditional UI updates
- Use instead of tracking focus events manually

**Use Cases**:
- Conditional editing operations
- UI state management
- Focus indicators
- Validation logic
- Auto-save conditions

---

## enable()

Enables or disables user editing capability.

**Signature**:
```typescript
enable(enabled?: boolean): void
```

**Parameters**:
- `enabled` - `true` to enable editing, `false` to disable (default: `true`)

**Returns**: `void`

**Examples**:

**Enable Editing**:
```javascript
// Enable editor (allow editing)
quill.enable(true);
```

**Disable Editing**:
```javascript
// Disable editor (read-only)
quill.enable(false);
```

**Shorthand (disable())**:
```javascript
// Equivalent to enable(false)
quill.disable();
```

**Toggle Edit Mode**:
```javascript
let isEditable = true;

function toggleEditMode() {
  isEditable = !isEditable;
  quill.enable(isEditable);

  const btn = document.getElementById('edit-btn');
  btn.textContent = isEditable ? 'Lock' : 'Unlock';
}
```

**Permission-Based Editing**:
```javascript
const userCanEdit = checkUserPermissions();
quill.enable(userCanEdit);

if (!userCanEdit) {
  document.getElementById('toolbar').style.display = 'none';
}
```

**Disable During Save**:
```javascript
async function saveContent() {
  quill.enable(false); // Prevent edits during save

  try {
    await fetch('/api/save', {
      method: 'POST',
      body: JSON.stringify(quill.getContents())
    });
    console.log('Saved!');
  } finally {
    quill.enable(true); // Re-enable after save
  }
}
```

**Disable on Specific Events**:
```javascript
// Disable editing when max length reached
quill.on('text-change', () => {
  const length = quill.getLength() - 1; // Exclude trailing newline

  if (length >= 1000) {
    quill.enable(false);
    alert('Maximum length reached');
  }
});
```

**Display-Only Mode**:
```javascript
// Create display-only editor
const displayQuill = new Quill('#display', {
  theme: 'snow',
  readOnly: true, // Built-in option
  modules: {
    toolbar: false // Hide toolbar
  }
});

// Equivalent to:
displayQuill.enable(false);
```

**Conditional Editing**:
```javascript
function checkEditingAllowed() {
  const now = new Date();
  const deadline = new Date('2024-12-31');

  if (now > deadline) {
    quill.enable(false);
    showMessage('Editing period has ended');
  }
}

checkEditingAllowed();
```

**Important Notes**:
- Sets editor to **read-only** when disabled
- User can still **select text** when disabled
- Toolbar buttons are **still clickable** (disable separately)
- Does **not** affect programmatic API calls
- Adds/removes `.ql-disabled` CSS class

**CSS Styling**:
```css
/* Style disabled editor */
.ql-editor.ql-disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}
```

**Difference from readOnly Option**:
```javascript
// Constructor option (static)
const quill = new Quill('#editor', {
  readOnly: true
});

// enable() method (dynamic)
quill.enable(false);
```

**Use Cases**:
- Permission-based editing
- Read-only preview mode
- Preventing edits during async operations
- Temporary disable during validation
- Display archived content

---

## disable()

Shorthand for `enable(false)` - disables user editing.

**Signature**:
```typescript
disable(): void
```

**Parameters**: None

**Returns**: `void`

**Examples**:

**Basic Usage**:
```javascript
// Disable editing
quill.disable();

// Equivalent to:
quill.enable(false);
```

**All Other Behaviors**:
See `enable()` method above - `disable()` is just a convenience method.

---

## update()

Manually synchronizes editor state (checks for updates).

**Signature**:
```typescript
update(source?: string): void
```

**Parameters**:
- `source` - Optional change source (`'user'`, `'api'`, `'silent'`)

**Returns**: `void`

**Examples**:

**Basic Update**:
```javascript
// Synchronously check for editor updates
quill.update();
```

**Update with Source**:
```javascript
// Update with specific source
quill.update('api');
```

**After DOM Manipulation**:
```javascript
// Direct DOM manipulation (NOT recommended)
quill.root.innerHTML = '<p>New content</p>';

// Force Quill to sync with DOM changes
quill.update();
```

**After External Changes**:
```javascript
// Another script modified the editor DOM
externalScript.modifyEditor();

// Ensure Quill is aware of changes
quill.update();
```

**Periodic Sync**:
```javascript
// Force periodic synchronization (rarely needed)
setInterval(() => {
  quill.update('silent');
}, 10000);
```

**Important Notes**:
- **Rarely needed** - Quill auto-syncs in most cases
- Use only after **external DOM manipulation**
- Triggers change events if differences detected
- **Avoid manual DOM changes** - use Quill API instead

**When You Might Need This**:
1. Integrating with libraries that directly modify DOM
2. Debugging state synchronization issues
3. After programmatic HTML changes (discouraged)

**Better Alternative**:
```javascript
// ❌ AVOID - Direct DOM manipulation
quill.root.innerHTML = '<p>New content</p>';
quill.update();

// ✅ PREFER - Use Quill API
quill.setContents([
  { insert: 'New content\n' }
]);
```

**Use Cases**:
- Integrating with third-party libraries
- Debugging synchronization issues
- Workarounds for edge cases
- Custom undo/redo implementations

---

## scrollRectIntoView()

Scrolls to specific pixel coordinates within the editor (experimental).

**Signature**:
```typescript
scrollRectIntoView(rect: {
  top: number,
  right: number,
  bottom: number,
  left: number
}): void
```

**Parameters**:
- `rect` - Bounds object with pixel coordinates

**Returns**: `void`

**Status**: Experimental (may change in future versions)

**Examples**:

**Scroll to Position**:
```javascript
// Get bounds for position 100
const bounds = quill.getBounds(100);

// Scroll to those bounds
quill.scrollRectIntoView(bounds);
```

**Scroll to Selection**:
```javascript
const range = quill.getSelection(true);
const bounds = quill.getBounds(range.index, range.length);
quill.scrollRectIntoView(bounds);
```

**Custom Scroll Logic**:
```javascript
function scrollToCustomPosition(x, y) {
  quill.scrollRectIntoView({
    top: y,
    left: x,
    bottom: y + 20,
    right: x + 100
  });
}
```

**Important Notes**:
- **Experimental API** - subject to change
- Use `scrollSelectionIntoView()` for most cases
- Accepts bounds from `getBounds()`
- Scrolls **editor container**, not page

**Preferred Alternative**:
```javascript
// ✅ PREFER - Stable API
quill.setSelection(100);
quill.scrollSelectionIntoView();

// ⚠️ EXPERIMENTAL
const bounds = quill.getBounds(100);
quill.scrollRectIntoView(bounds);
```

**Use Cases**:
- Custom scroll behavior
- Advanced positioning logic
- Experimental features

---

## Common Lifecycle Patterns

### Read-Only Toggle
```javascript
let isReadOnly = false;

function toggleReadOnly() {
  isReadOnly = !isReadOnly;
  quill.enable(!isReadOnly);

  const btn = document.getElementById('toggle-btn');
  btn.textContent = isReadOnly ? 'Enable Editing' : 'Disable Editing';

  const toolbar = document.getElementById('toolbar');
  toolbar.style.display = isReadOnly ? 'none' : 'block';
}
```

### Auto-Focus First Empty Field
```javascript
const editors = [quill1, quill2, quill3];

function focusFirstEmpty() {
  for (const editor of editors) {
    const text = editor.getText().trim();
    if (text === '') {
      editor.focus();
      break;
    }
  }
}
```

### Permission-Based Access
```javascript
async function initializeEditor() {
  const permissions = await fetchUserPermissions();

  if (permissions.canEdit) {
    quill.enable(true);
  } else if (permissions.canView) {
    quill.enable(false);
    quill.focus({ preventScroll: true });
  } else {
    document.getElementById('editor-container').style.display = 'none';
  }
}
```

### Focus Indicator
```javascript
function updateFocusIndicator() {
  const container = document.getElementById('editor-container');

  if (quill.hasFocus()) {
    container.classList.add('focused');
  } else {
    container.classList.remove('focused');
  }
}

quill.on('selection-change', updateFocusIndicator);
```

### Save and Lock
```javascript
async function saveAndLock() {
  if (!quill.hasFocus()) {
    quill.focus();
  }

  quill.enable(false); // Lock editor

  try {
    const content = quill.getContents();
    await saveToServer(content);

    showMessage('Saved successfully!');
  } catch (error) {
    quill.enable(true); // Unlock on error
    showError('Save failed: ' + error.message);
  }
}
```

---

## Official Documentation

**URL**: https://quilljs.com/docs/api/#editor

---

## Next Steps

- **Selection**: See `categories/api-selection.md` for focus-related selection methods
- **Events**: See `categories/api-events.md` for selection-change event
- **Configuration**: See `categories/configuration.md` for readOnly option
- **Content**: See `categories/api-content.md` for content methods
