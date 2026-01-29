# Quill Extension & Registration API

Complete reference for all 5 extension, module, and registration methods in Quill.js.

---

## Overview

Extension methods allow you to customize and extend Quill's functionality by:

- Registering custom formats, modules, and themes
- Importing Quill's internal classes (Parchment, Delta, etc.)
- Enabling debug logging
- Adding custom UI containers
- Accessing module instances

**Core Methods**:
- `Quill.register()` - Register custom formats/modules/themes (static)
- `Quill.import()` - Import Quill internal classes (static)
- `Quill.debug()` - Enable debug logging (static)
- `addContainer()` - Add custom UI container (instance)
- `getModule()` - Access module instance (instance)

**Static vs Instance**:
- **Static methods** (`register`, `import`, `debug`) - Called on `Quill` class
- **Instance methods** (`addContainer`, `getModule`) - Called on quill instance

---

## Quill.register() (Static)

Registers custom formats, modules, or themes with Quill.

**Signature**:
```typescript
Quill.register(path: string, def: any, suppressWarning?: boolean): void
Quill.register(defs: Record<string, any>, suppressWarning?: boolean): void
```

**Parameters**:
- `path` - Registration path (e.g., `'formats/custom'`, `'modules/myModule'`)
- `def` - Class or object to register
- `defs` - Object with multiple registrations
- `suppressWarning` - Suppress overwrite warnings (default: `false`)

**Returns**: `void`

**Examples**:

**Register Custom Format**:
```javascript
import Quill from 'quill';
const Inline = Quill.import('blots/inline');

// Define custom format
class HighlightBlot extends Inline {
  static blotName = 'highlight';
  static tagName = 'mark';
}

// Register it
Quill.register('formats/highlight', HighlightBlot);

// Now you can use it
const quill = new Quill('#editor');
quill.formatText(0, 5, 'highlight', true);
```

**Register Custom Module**:
```javascript
class CustomModule {
  constructor(quill, options) {
    this.quill = quill;
    this.options = options;

    quill.on('text-change', () => {
      console.log('Custom module detected change');
    });
  }
}

// Register module
Quill.register('modules/customModule', CustomModule);

// Use in config
const quill = new Quill('#editor', {
  modules: {
    customModule: {
      option1: 'value1'
    }
  }
});
```

**Register Multiple Items**:
```javascript
// Register multiple at once
Quill.register({
  'formats/highlight': HighlightBlot,
  'formats/mention': MentionBlot,
  'modules/counter': CounterModule
});
```

**Suppress Overwrite Warning**:
```javascript
// Re-register without warning
Quill.register('formats/bold', CustomBoldBlot, true);
```

**Register Custom Theme**:
```javascript
import { BaseTheme } from 'quill';

class CustomTheme extends BaseTheme {
  constructor(quill, options) {
    super(quill, options);
    // Custom theme initialization
  }
}

Quill.register('themes/custom', CustomTheme);

// Use it
const quill = new Quill('#editor', {
  theme: 'custom'
});
```

**Registration Paths**:
- `formats/[name]` - Custom inline/block formats
- `modules/[name]` - Custom modules
- `themes/[name]` - Custom themes
- `blots/[name]` - Custom Blot types (advanced)

**Important Notes**:
- Must register **before** creating Quill instances
- Registration is **global** (affects all instances)
- Overwrites existing registrations (with warning unless suppressed)
- Custom formats must extend Parchment Blots

**Use Cases**:
- Custom formatting (mentions, hashtags, custom styles)
- Custom modules (counters, validators, integrations)
- Custom themes
- Extending Quill functionality

**See Also**: `guides/parchment-blots.md` for creating custom formats

---

## Quill.import() (Static)

Imports Quill's internal classes and modules (Parchment, Delta, etc.).

**Signature**:
```typescript
Quill.import(path: string): any
```

**Parameters**:
- `path` - Import path (e.g., `'blots/block'`, `'core/module'`, `'delta'`)

**Returns**: Imported class or module

**Examples**:

**Import Parchment Blots**:
```javascript
import Quill from 'quill';

const Block = Quill.import('blots/block');
const Inline = Quill.import('blots/inline');
const Embed = Quill.import('blots/embed');

// Use as base classes for custom formats
class CustomBlock extends Block {
  // ...
}
```

**Import Delta**:
```javascript
const Delta = Quill.import('delta');

// Create deltas programmatically
const delta = new Delta()
  .insert('Hello ')
  .insert('World', { bold: true })
  .insert('\n');

quill.setContents(delta);
```

**Import Parchment**:
```javascript
const Parchment = Quill.import('parchment');

// Access Parchment classes
const Scroll = Parchment.Scroll;
const Container = Parchment.Container;
```

**Import Existing Formats**:
```javascript
// Get existing format definitions
const Bold = Quill.import('formats/bold');
const Link = Quill.import('formats/link');
const Header = Quill.import('formats/header');

console.log('Bold tag:', Bold.tagName); // 'STRONG'
console.log('Link tag:', Link.tagName); // 'A'
```

**Import Modules**:
```javascript
const Toolbar = Quill.import('modules/toolbar');
const Keyboard = Quill.import('modules/keyboard');
const History = Quill.import('modules/history');

// Extend or customize
class CustomToolbar extends Toolbar {
  // Custom toolbar logic
}

Quill.register('modules/toolbar', CustomToolbar, true);
```

**Import Base Module**:
```javascript
const Module = Quill.import('core/module');

// Extend for custom modules
class CustomModule extends Module {
  constructor(quill, options) {
    super(quill, options);
    // Custom initialization
  }
}
```

**Common Import Paths**:

**Blots**:
- `'blots/block'` - Block-level Blot base class
- `'blots/inline'` - Inline Blot base class
- `'blots/embed'` - Embed Blot base class
- `'blots/scroll'` - Root scroll container
- `'blots/text'` - Text Blot

**Formats** (all built-in formats):
- `'formats/bold'`, `'formats/italic'`, `'formats/underline'`
- `'formats/link'`, `'formats/image'`, `'formats/video'`
- `'formats/header'`, `'formats/list'`, `'formats/blockquote'`
- And all others from `categories/formats.md`

**Modules**:
- `'modules/toolbar'` - Toolbar module
- `'modules/keyboard'` - Keyboard bindings module
- `'modules/history'` - Undo/redo module
- `'modules/clipboard'` - Clipboard handling
- `'modules/syntax'` - Syntax highlighting

**Core**:
- `'core/module'` - Base Module class
- `'core/theme'` - Base Theme class
- `'delta'` - Delta class
- `'parchment'` - Parchment library

**Important Notes**:
- Returns `undefined` for invalid paths
- Case-sensitive paths
- Use for extending built-in functionality
- Essential for custom format development

**Use Cases**:
- Creating custom formats
- Extending built-in formats
- Creating custom modules
- Working with Delta programmatically
- Accessing internal APIs

---

## Quill.debug() (Static)

Enables debug logging for all Quill instances.

**Signature**:
```typescript
Quill.debug(level: 'error' | 'warn' | 'log' | 'info' | boolean): void
```

**Parameters**:
- `level` - Debug level or boolean
  - `'error'` - Only errors
  - `'warn'` - Errors and warnings (default)
  - `'log'` - Errors, warnings, and logs
  - `'info'` - All messages including debug info
  - `false` - Disable all logging
  - `true` - Enable all logging (same as `'info'`)

**Returns**: `void`

**Examples**:

**Enable Verbose Logging**:
```javascript
import Quill from 'quill';

// Enable all logging before creating instances
Quill.debug('info');

const quill = new Quill('#editor', {
  theme: 'snow'
});

// Console will show detailed debug info
```

**Development vs Production**:
```javascript
// Enable debugging in development
if (process.env.NODE_ENV === 'development') {
  Quill.debug('log');
} else {
  Quill.debug('error'); // Production: errors only
}
```

**Disable All Logging**:
```javascript
// Completely silent
Quill.debug(false);
```

**Debug Levels**:
```javascript
// Only errors (crashes, critical issues)
Quill.debug('error');

// Errors + warnings (default - deprecated APIs, etc.)
Quill.debug('warn');

// Errors + warnings + logs (general info)
Quill.debug('log');

// Everything (verbose debugging)
Quill.debug('info');
```

**Debugging Custom Formats**:
```javascript
Quill.debug('info');

class CustomFormat extends Inline {
  static create(value) {
    console.log('CustomFormat.create called with:', value);
    return super.create(value);
  }
}

Quill.register('formats/custom', CustomFormat);
```

**Important Notes**:
- **Global setting** - affects ALL Quill instances
- Call **before** creating instances for full effect
- Can be called at runtime to change level
- Uses native `console` methods
- Persists until page reload (unless changed)

**Use Cases**:
- Development debugging
- Troubleshooting issues
- Custom format development
- Performance analysis
- Integration debugging

---

## addContainer()

Adds a sibling container to the editor (for custom UI elements).

**Signature**:
```typescript
addContainer(className: string, refNode?: Element): Element
addContainer(domNode: Element, refNode?: Element): Element
```

**Parameters**:
- `className` - CSS class for new container OR
- `domNode` - Pre-created DOM element
- `refNode` - Reference node for positioning (default: editor)

**Returns**: Created or inserted DOM element

**Examples**:

**Add Toolbar Container**:
```javascript
const quill = new Quill('#editor');

// Add toolbar container above editor
const toolbarContainer = quill.addContainer('ql-toolbar');
toolbarContainer.innerHTML = `
  <button class="ql-bold">B</button>
  <button class="ql-italic">I</button>
`;
```

**Add Status Bar**:
```javascript
const statusBar = quill.addContainer('status-bar');
statusBar.innerHTML = '<span id="word-count">0 words</span>';

// Position below editor
statusBar.style.borderTop = '1px solid #ccc';
statusBar.style.padding = '10px';

// Update word count
quill.on('text-change', () => {
  const text = quill.getText().trim();
  const words = text.split(/\s+/).filter(w => w.length > 0).length;
  document.getElementById('word-count').textContent = `${words} words`;
});
```

**Add with DOM Node**:
```javascript
// Create custom container
const container = document.createElement('div');
container.className = 'custom-ui';
container.innerHTML = '<button>Custom Action</button>';

// Add to Quill
quill.addContainer(container);
```

**Position Relative to Reference**:
```javascript
const toolbar = quill.getModule('toolbar').container;

// Add container before toolbar
const notice = quill.addContainer('notice-banner', toolbar);
notice.textContent = 'You are in edit mode';
```

**Add Multiple Containers**:
```javascript
// Top banner
const topBanner = quill.addContainer('top-banner');
topBanner.textContent = 'Draft mode';

// Bottom banner
const bottomBanner = quill.addContainer('bottom-banner');
bottomBanner.textContent = 'Auto-saving...';
```

**Custom Module UI**:
```javascript
class CustomModule {
  constructor(quill, options) {
    this.quill = quill;

    // Add module's UI container
    this.container = quill.addContainer('custom-module-ui');
    this.container.innerHTML = '<div>Custom Module Controls</div>';

    // Add event listeners
    this.container.querySelector('button').addEventListener('click', () => {
      this.performAction();
    });
  }

  performAction() {
    console.log('Custom action triggered');
  }
}

Quill.register('modules/custom', CustomModule);
```

**Important Notes**:
- Containers are **siblings** to editor, not children
- Added **before** editor by default
- Use `refNode` to control position
- Containers are **not** part of editable content
- Useful for module UI, toolbars, status bars

**Container Structure**:
```html
<div class="ql-container">
  <div class="custom-container"></div>  <!-- addContainer() -->
  <div class="ql-editor">...</div>       <!-- Actual editor -->
</div>
```

**Use Cases**:
- Custom toolbars
- Status bars
- Character counters
- Custom module UI
- Notifications/banners

---

## getModule()

Retrieves a registered module instance.

**Signature**:
```typescript
getModule(name: string): any
```

**Parameters**:
- `name` - Module name (e.g., `'toolbar'`, `'keyboard'`, `'history'`)

**Returns**: Module instance or `undefined` if not found

**Examples**:

**Get Toolbar Module**:
```javascript
const quill = new Quill('#editor', {
  theme: 'snow',
  modules: {
    toolbar: [['bold', 'italic']]
  }
});

const toolbar = quill.getModule('toolbar');
console.log('Toolbar container:', toolbar.container);
```

**Get History Module**:
```javascript
const history = quill.getModule('history');

// Access history methods
history.undo();
history.redo();
history.clear();

// Check history state
console.log('Undo stack:', history.stack.undo);
console.log('Redo stack:', history.stack.redo);
```

**Get Keyboard Module**:
```javascript
const keyboard = quill.getModule('keyboard');

// Add custom binding
keyboard.addBinding({
  key: 'B',
  shortKey: true,
  handler: function(range, context) {
    this.quill.formatText(range, 'bold', true);
  }
});
```

**Get Custom Module**:
```javascript
class CounterModule {
  constructor(quill, options) {
    this.quill = quill;
    this.count = 0;

    quill.on('text-change', () => {
      this.count++;
    });
  }

  getCount() {
    return this.count;
  }
}

Quill.register('modules/counter', CounterModule);

const quill = new Quill('#editor', {
  modules: { counter: true }
});

const counter = quill.getModule('counter');
console.log('Changes:', counter.getCount());
```

**Check if Module Exists**:
```javascript
const clipboard = quill.getModule('clipboard');

if (clipboard) {
  console.log('Clipboard module is active');
} else {
  console.log('Clipboard module not found');
}
```

**Access Module Options**:
```javascript
const quill = new Quill('#editor', {
  modules: {
    toolbar: {
      container: '#toolbar',
      handlers: {
        custom: customHandler
      }
    }
  }
});

const toolbar = quill.getModule('toolbar');
console.log('Toolbar options:', toolbar.options);
```

**Interact with Modules**:
```javascript
// Programmatically trigger toolbar action
const toolbar = quill.getModule('toolbar');
const boldButton = toolbar.container.querySelector('.ql-bold');
boldButton.click();

// Access clipboard
const clipboard = quill.getModule('clipboard');
clipboard.onPaste(event); // Custom paste handling
```

**Built-in Modules**:
- `'toolbar'` - Toolbar module
- `'keyboard'` - Keyboard bindings
- `'history'` - Undo/redo
- `'clipboard'` - Copy/paste handling
- `'syntax'` - Code syntax highlighting (if enabled)
- `'uploader'` - File upload handling

**Important Notes**:
- Returns `undefined` if module not registered or not enabled
- Module must be enabled in config
- Returns **instance**, not class definition
- Use to interact with module functionality

**Use Cases**:
- Programmatic undo/redo
- Custom toolbar interactions
- Accessing module state
- Adding keyboard bindings
- Module communication

---

## Common Extension Patterns

### Custom Highlight Format
```javascript
import Quill from 'quill';
const Inline = Quill.import('blots/inline');

class HighlightBlot extends Inline {
  static blotName = 'highlight';
  static tagName = 'mark';
  static className = 'highlight';

  static create(color) {
    const node = super.create();
    node.style.backgroundColor = color;
    return node;
  }

  static formats(domNode) {
    return domNode.style.backgroundColor;
  }
}

Quill.register('formats/highlight', HighlightBlot);

// Use it
const quill = new Quill('#editor');
quill.formatText(0, 5, 'highlight', '#ffff00');
```

### Mention System
```javascript
const Embed = Quill.import('blots/embed');

class MentionBlot extends Embed {
  static blotName = 'mention';
  static tagName = 'span';
  static className = 'mention';

  static create(data) {
    const node = super.create();
    node.setAttribute('data-id', data.id);
    node.setAttribute('data-value', data.value);
    node.textContent = `@${data.value}`;
    return node;
  }

  static value(domNode) {
    return {
      id: domNode.getAttribute('data-id'),
      value: domNode.getAttribute('data-value')
    };
  }
}

Quill.register('formats/mention', MentionBlot);

// Insert mention
quill.insertEmbed(10, 'mention', { id: '123', value: 'John' });
```

### Custom Counter Module
```javascript
class WordCounterModule {
  constructor(quill, options) {
    this.quill = quill;
    this.container = quill.addContainer('word-counter');
    this.container.style.cssText = 'text-align: right; padding: 5px;';

    quill.on('text-change', () => this.update());
    this.update();
  }

  update() {
    const text = this.quill.getText().trim();
    const words = text.split(/\s+/).filter(w => w.length > 0).length;
    const chars = this.quill.getLength() - 1;

    this.container.textContent = `${words} words, ${chars} characters`;
  }
}

Quill.register('modules/wordCounter', WordCounterModule);

const quill = new Quill('#editor', {
  modules: {
    wordCounter: true
  }
});
```

### Programmatic Module Control
```javascript
const quill = new Quill('#editor', {
  theme: 'snow',
  modules: {
    toolbar: [['bold', 'italic']],
    history: {
      delay: 1000,
      maxStack: 50
    }
  }
});

// Get modules
const history = quill.getModule('history');
const toolbar = quill.getModule('toolbar');

// Custom undo/redo buttons
document.getElementById('undo-btn').addEventListener('click', () => {
  history.undo();
});

document.getElementById('redo-btn').addEventListener('click', () => {
  history.redo();
});

// Clear history
document.getElementById('clear-history-btn').addEventListener('click', () => {
  history.clear();
});
```

### Debug Mode Toggle
```javascript
let debugEnabled = false;

function toggleDebug() {
  debugEnabled = !debugEnabled;
  Quill.debug(debugEnabled ? 'info' : 'warn');

  console.log('Debug mode:', debugEnabled ? 'ON' : 'OFF');
}

// Toggle with keyboard shortcut
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.shiftKey && e.key === 'D') {
    e.preventDefault();
    toggleDebug();
  }
});
```

---

## Official Documentation

**URL**: https://quilljs.com/docs/api/#extension

---

## Next Steps

- **Custom Formats**: See `guides/parchment-blots.md` for creating custom formats
- **Custom Modules**: See `guides/custom-modules.md` for module development
- **Toolbar**: See `categories/toolbar-module.md` for toolbar customization
- **Keyboard**: See `categories/keyboard-module.md` for keyboard bindings
- **Configuration**: See `categories/configuration.md` for module configuration
