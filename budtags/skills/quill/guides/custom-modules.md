# Building a Custom Module

Step-by-step guide to creating custom Quill modules, from simple functions to production-ready implementations.

---

## Overview

Quill modules extend editor functionality beyond basic text editing. This guide builds a word counter module through four progressive stages, demonstrating best practices for custom module development.

**Official Documentation**: https://quilljs.com/guides/building-a-custom-module

---

## Module Basics

### What are Modules?

Modules add features to Quill editors:
- **Built-in modules**: Toolbar, Keyboard, History, Clipboard, Syntax
- **Custom modules**: Add application-specific functionality

### Registration Pattern

**Global registration** (affects all instances):
```javascript
Quill.register('modules/counter', CounterModule);

const quill = new Quill('#editor', {
  modules: {
    counter: true
  }
});
```

**Per-instance registration**:
```javascript
const quill = new Quill('#editor', {
  modules: {
    counter: CounterModule
  }
});
```

---

## Stage 1: Basic Function

Start with simplest implementation - a function that runs on initialization.

### Implementation

```javascript
function Counter() {
  console.log('Counter module initialized');
}

// Register globally
Quill.register('modules/counter', Counter);

// Use in editor
const quill = new Quill('#editor', {
  modules: {
    counter: true
  }
});
```

### Limitations

- No access to Quill instance
- No configuration options
- Runs once at initialization
- Cannot interact with editor

**Use case**: Simple one-time setup tasks.

---

## Stage 2: Configuration Options

Add constructor to accept Quill instance and options.

### Implementation

```javascript
function Counter(quill, options) {
  const container = document.querySelector(options.selector);

  quill.on('text-change', function() {
    const text = quill.getText();

    if (options.unit === 'word') {
      container.innerText = text.split(/\s+/).length + ' words';
    } else {
      container.innerText = text.length + ' characters';
    }
  });
}

// Register module
Quill.register('modules/counter', Counter);

// Use with options
const quill = new Quill('#editor', {
  modules: {
    counter: {
      selector: '#counter-display',
      unit: 'word'
    }
  }
});
```

### HTML Structure

```html
<div id="editor">
  <p>Start typing...</p>
</div>

<div id="counter-display">0 words</div>

<script>
  const quill = new Quill('#editor', {
    theme: 'snow',
    modules: {
      counter: {
        selector: '#counter-display',
        unit: 'word'
      }
    }
  });
</script>
```

### Features

- ✅ Access to Quill instance
- ✅ Configurable options
- ✅ Updates on text changes
- ✅ Character or word counting

### Limitations

- No cleanup on destroy
- Global event listener
- No validation
- Basic word counting logic

---

## Stage 3: Class-Based Implementation

Refactor to ES6 class for better organization and encapsulation.

### Implementation

```javascript
class Counter {
  constructor(quill, options) {
    this.quill = quill;
    this.options = options;
    this.container = document.querySelector(options.selector);

    // Bind event handler
    this.update = this.update.bind(this);

    // Listen for text changes
    quill.on('text-change', this.update);

    // Initial count
    this.update();
  }

  calculate() {
    const text = this.quill.getText();

    if (this.options.unit === 'word') {
      // Filter empty strings from split
      return text.split(/\s+/).filter(word => word.length > 0).length;
    } else {
      // Subtract 1 for trailing newline Quill adds
      return text.length - 1;
    }
  }

  update() {
    const count = this.calculate();
    const label = this.options.unit === 'word' ? 'words' : 'characters';
    this.container.innerText = `${count} ${label}`;
  }
}

// Register module
Quill.register('modules/counter', Counter);
```

### Usage

```javascript
const quill = new Quill('#editor', {
  theme: 'snow',
  modules: {
    counter: {
      selector: '#counter-display',
      unit: 'word'
    }
  }
});

// Access module instance
const counterModule = quill.getModule('counter');
console.log('Current count:', counterModule.calculate());
```

### Features

- ✅ Organized code structure
- ✅ Reusable calculate() method
- ✅ Proper method binding
- ✅ Improved counting accuracy
- ✅ Public API via getModule()

### Limitations

- Still no cleanup
- No option validation
- No error handling

---

## Stage 4: Production Polish

Add production-ready features: defaults, validation, cleanup, edge cases.

### Complete Implementation

```javascript
class Counter {
  static DEFAULTS = {
    selector: '#counter',
    unit: 'word'
  };

  constructor(quill, options) {
    this.quill = quill;

    // Merge options with defaults
    this.options = Object.assign({}, Counter.DEFAULTS, options);

    // Validate options
    this.validate();

    // Find container
    this.container = document.querySelector(this.options.selector);

    if (!this.container) {
      console.error(`Counter: Element not found: ${this.options.selector}`);
      return;
    }

    // Bind methods
    this.update = this.update.bind(this);
    this.handleTextChange = this.handleTextChange.bind(this);

    // Register event listener
    quill.on('text-change', this.handleTextChange);

    // Initial count
    this.update();
  }

  validate() {
    const validUnits = ['word', 'character'];

    if (!validUnits.includes(this.options.unit)) {
      console.warn(
        `Counter: Invalid unit "${this.options.unit}". Using "word".`
      );
      this.options.unit = 'word';
    }

    if (typeof this.options.selector !== 'string') {
      console.error('Counter: selector must be a string');
      this.options.selector = Counter.DEFAULTS.selector;
    }
  }

  calculate() {
    const text = this.quill.getText();

    if (this.options.unit === 'word') {
      // Handle edge cases:
      // - Empty document
      // - Multiple spaces
      // - Leading/trailing whitespace
      const words = text
        .trim()
        .split(/\s+/)
        .filter(word => word.length > 0);

      return words.length === 1 && words[0] === '' ? 0 : words.length;
    } else {
      // Subtract trailing newline that Quill adds
      return Math.max(0, text.length - 1);
    }
  }

  update() {
    if (!this.container) return;

    const count = this.calculate();
    const unit = this.options.unit;
    const label = count === 1 ? unit : unit + 's';

    this.container.innerText = `${count} ${label}`;
    this.container.setAttribute('data-count', count);
  }

  handleTextChange(delta, oldDelta, source) {
    // Could filter by source if needed
    // if (source === 'user') { ... }
    this.update();
  }

  destroy() {
    // Cleanup: remove event listener
    this.quill.off('text-change', this.handleTextChange);
  }
}

// Set defaults for ES5 environments
Counter.DEFAULTS = Counter.DEFAULTS || {
  selector: '#counter',
  unit: 'word'
};

// Register module
Quill.register('modules/counter', Counter);
```

### Advanced Usage

```html
<div id="editor">
  <p>Start typing to see the counter update...</p>
</div>

<div id="word-counter" class="counter"></div>
<div id="char-counter" class="counter"></div>

<style>
  .counter {
    font-size: 12px;
    color: #666;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-top: 8px;
  }

  .counter[data-count="0"] {
    color: #ccc;
  }
</style>

<script>
  // Word counter instance
  const quill1 = new Quill('#editor', {
    theme: 'snow',
    modules: {
      counter: {
        selector: '#word-counter',
        unit: 'word'
      }
    }
  });

  // Separate character counter
  const CharCounter = Quill.import('modules/counter');
  const charCounter = new CharCounter(quill1, {
    selector: '#char-counter',
    unit: 'character'
  });
</script>
```

### Features

- ✅ Default options
- ✅ Option validation with warnings
- ✅ Edge case handling (empty document, whitespace)
- ✅ Proper pluralization
- ✅ Data attribute for styling
- ✅ Cleanup method
- ✅ Error handling
- ✅ Graceful failures
- ✅ Production-ready code

---

## Module Registration Patterns

### Global Registration

Register once, use across all instances:

```javascript
// Register globally
Quill.register('modules/counter', Counter);

// Use in multiple editors
const editor1 = new Quill('#editor1', {
  modules: { counter: { selector: '#counter1', unit: 'word' } }
});

const editor2 = new Quill('#editor2', {
  modules: { counter: { selector: '#counter2', unit: 'character' } }
});
```

### Per-Instance Registration

Register different implementation per instance:

```javascript
class AdvancedCounter extends Counter {
  // Extended functionality
}

const quill = new Quill('#editor', {
  modules: {
    counter: AdvancedCounter // Use custom class directly
  }
});
```

### Importing Registered Modules

```javascript
// Import globally registered module
const Counter = Quill.import('modules/counter');

// Create instance manually
const counter = new Counter(quill, { selector: '#counter' });
```

---

## Best Practices

### Constructor Responsibilities

1. **Store references**: Save quill instance and options
2. **Validate options**: Check for required/valid values
3. **Find DOM elements**: Locate containers early
4. **Bind methods**: Ensure correct `this` context
5. **Register listeners**: Set up event handlers
6. **Initialize state**: Run initial updates

### Event Handling

**Bind methods in constructor**:
```javascript
constructor(quill, options) {
  this.handleChange = this.handleChange.bind(this);
  quill.on('text-change', this.handleChange);
}
```

**Use named methods** (not anonymous functions) for easier cleanup:
```javascript
// ✅ Good - can be removed
quill.on('text-change', this.handleChange);
quill.off('text-change', this.handleChange);

// ❌ Bad - cannot be removed
quill.on('text-change', () => { this.update(); });
```

### Cleanup

Always provide destroy method:

```javascript
destroy() {
  // Remove event listeners
  this.quill.off('text-change', this.handleChange);

  // Clear timers
  if (this.timer) {
    clearTimeout(this.timer);
  }

  // Clean up DOM modifications
  if (this.customElement) {
    this.customElement.remove();
  }

  // Nullify references
  this.quill = null;
  this.container = null;
}
```

### Error Handling

Handle missing elements gracefully:

```javascript
constructor(quill, options) {
  this.container = document.querySelector(options.selector);

  if (!this.container) {
    console.warn(`Element not found: ${options.selector}`);
    return; // Early exit if critical element missing
  }

  // Continue initialization...
}
```

### Defaults and Validation

```javascript
static DEFAULTS = {
  selector: '#element',
  option1: 'value1',
  option2: true
};

constructor(quill, options) {
  this.options = Object.assign({}, Constructor.DEFAULTS, options);
  this.validate();
}

validate() {
  // Check required options
  if (!this.options.selector) {
    throw new Error('selector is required');
  }

  // Validate option values
  if (typeof this.options.option2 !== 'boolean') {
    console.warn('option2 should be boolean, using default');
    this.options.option2 = Constructor.DEFAULTS.option2;
  }
}
```

---

## Real-World Module Examples

### Auto-Save Module

```javascript
class AutoSave {
  static DEFAULTS = {
    interval: 5000, // 5 seconds
    endpoint: '/api/save',
    key: 'quill-content'
  };

  constructor(quill, options) {
    this.quill = quill;
    this.options = Object.assign({}, AutoSave.DEFAULTS, options);

    this.save = this.save.bind(this);

    // Auto-save on text change (debounced)
    quill.on('text-change', this.scheduleAutoSave.bind(this));
  }

  scheduleAutoSave() {
    if (this.timer) clearTimeout(this.timer);

    this.timer = setTimeout(this.save, this.options.interval);
  }

  async save() {
    const delta = this.quill.getContents();

    try {
      await fetch(this.options.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: delta })
      });

      console.log('Auto-saved successfully');
    } catch (error) {
      console.error('Auto-save failed:', error);
    }
  }

  destroy() {
    if (this.timer) clearTimeout(this.timer);
    this.quill.off('text-change', this.scheduleAutoSave);
  }
}

Quill.register('modules/autoSave', AutoSave);
```

### Mention Module (Simplified)

```javascript
class MentionModule {
  constructor(quill, options) {
    this.quill = quill;
    this.options = options;

    this.handleTextChange = this.handleTextChange.bind(this);
    quill.on('text-change', this.handleTextChange);
  }

  handleTextChange(delta, oldDelta, source) {
    if (source !== 'user') return;

    const ops = delta.ops;
    const lastOp = ops[ops.length - 1];

    // Check if user typed '@'
    if (lastOp?.insert === '@') {
      this.showMentionList();
    }
  }

  showMentionList() {
    // Show popup with user list
    console.log('Show mention suggestions...');
    // Implementation depends on UI framework
  }

  insertMention(user) {
    const range = this.quill.getSelection();
    this.quill.insertText(range.index, user.name, 'mention', user);
  }

  destroy() {
    this.quill.off('text-change', this.handleTextChange);
  }
}

Quill.register('modules/mention', MentionModule);
```

---

## Testing Modules

```javascript
// Create test instance
const quill = new Quill('#test-editor');

// Get module instance
const counter = quill.getModule('counter');

// Test methods
console.assert(counter.calculate() === 0, 'Empty editor should have 0 count');

quill.setText('Hello World');
console.assert(counter.calculate() === 2, 'Should count 2 words');

// Test cleanup
counter.destroy();
```

---

## Related Files

- **Toolbar Module**: See `categories/toolbar-module.md` for built-in module example
- **Configuration**: See `categories/configuration.md` for module options
- **API Events**: See `categories/api-events.md` for event handling

---

## Official Resources

- **Custom Module Guide**: https://quilljs.com/guides/building-a-custom-module
- **Module Examples**: https://github.com/quilljs/quill/tree/main/modules
- **Community Modules**: https://github.com/quilljs/awesome-quill
