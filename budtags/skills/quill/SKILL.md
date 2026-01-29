---
name: quill
description: Use this skill when working with Quill.js rich text editor - API methods, configuration, modules, Delta format, and custom implementations.
---

# Quill.js Rich Text Editor Skill

You are now equipped with comprehensive knowledge of **Quill.js v2.0.3** - a powerful, extensible rich text editor for the modern web. This skill uses **progressive disclosure** to load only the information relevant to your task.

---

## Your Capabilities

When the user asks about Quill.js, you can:

1. **Basic Setup**: Help initialize Quill with CDN or NPM, configure themes and options
2. **Content Manipulation**: Use 10+ API methods for inserting, deleting, and retrieving content
3. **Formatting**: Apply inline/block formatting, handle selections and focus
4. **Delta Format**: Explain and work with Quill's JSON-based document format
5. **Modules**: Configure Toolbar, Keyboard, History, Clipboard, and Syntax modules
6. **Events**: Handle text-change, selection-change, and editor-change events
7. **Customization**: Implement custom themes, formats, and modules
8. **Parchment/Blots**: Create advanced custom content types and formats
9. **Integration**: Integrate Quill into React/TypeScript applications (BudTags patterns)

---

## Available Resources

This skill includes comprehensive documentation organized for progressive disclosure:

### Category Files (Modular, ~80-150 lines each)

**Getting Started**:
- `categories/getting-started.md` - Quickstart, CDN setup, basic initialization
- `categories/configuration.md` - All configuration options and themes
- `categories/formats.md` - Available inline/block/embed formats

**API Reference**:
- `categories/api-content.md` - Content methods (10 methods)
- `categories/api-formatting.md` - Formatting methods (5 methods)
- `categories/api-selection.md` - Selection and focus methods (4 methods)
- `categories/api-editor.md` - Editor lifecycle methods (6 methods)
- `categories/api-events.md` - Event system (text-change, selection-change, etc.)
- `categories/api-model.md` - Document traversal (find, getLine, getLeaf, etc.)
- `categories/api-extension.md` - Registration and imports

**Delta Format**:
- `categories/delta.md` - Complete Delta specification with examples

**Modules**:
- `categories/toolbar-module.md` - Toolbar configuration and handlers
- `categories/keyboard-module.md` - Keyboard bindings and context
- `categories/history-module.md` - Undo/redo configuration
- `categories/clipboard-module.md` - Paste handling and matchers
- `categories/syntax-module.md` - Code highlighting with highlight.js

### Pattern Files (~60-100 lines each)

- `patterns/themes.md` - Snow and Bubble themes, customization
- `patterns/registries.md` - Multiple editors with different formats
- `patterns/upgrading.md` - Migration from v1.x to v2.0

### Guide Files (~100-150 lines each)

- `guides/delta-design.md` - Delta format design philosophy
- `guides/custom-modules.md` - Building custom modules step-by-step
- `guides/parchment-blots.md` - Creating custom formats with Parchment

---

## Quill.js v2.0.3 Information

**Official Docs:** https://quilljs.com/docs

**CDN Setup:**
```html
<!-- Stylesheet -->
<link href="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css" rel="stylesheet" />

<!-- Library -->
<script src="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.js"></script>
```

**NPM Installation:**
```bash
npm install quill@2.0.3
```

**Key Features:**
- ✅ API-driven design (JSON-based, not DOM-based)
- ✅ Cross-platform consistency
- ✅ Extensible with modules and custom formats
- ✅ TypeScript support (v2.0+ rewrite)
- ✅ Embedded SVG icons (no bundler config needed)
- ✅ Delta format for content representation
- ✅ Two built-in themes (Snow, Bubble)
- ✅ BSD licensed for personal and commercial use

---

## Progressive Loading Process

**IMPORTANT:** Only load files relevant to the user's question. DO NOT load all categories.

### Step 1: Context Gathering

**Ask the user or determine from context:**

"What Quill.js task are you working on? Please provide:
- Goal/task description (e.g., 'insert formatted text', 'configure toolbar')
- Specific API method or module name OR
- Integration problem to debug OR
- Customization you need to implement"

**Determine scope:**
- Is this a setup/getting-started question?
- Is this about a specific API method?
- Is this about modules (Toolbar, Keyboard, etc.)?
- Is this about Delta format or custom formats?
- Is this advanced customization (Parchment, custom modules)?

### Step 2: Load Relevant Resources

#### For Setup Questions

**User asks: "How do I set up Quill with CDN?"**

**Load**:
1. `categories/getting-started.md` (CDN setup, initialization)

**Context**: ~100 lines (97% reduction from loading all docs)

#### For API Method Questions

**User asks: "How do I insert formatted text?"**

**Load**:
1. `categories/api-content.md` (insertText method + examples)
2. `categories/formats.md` (IF user needs list of available formats)

**Context**: ~120-200 lines (94% reduction)

#### For Module Configuration

**User asks: "How do I customize the toolbar?"**

**Load**:
1. `categories/toolbar-module.md` (complete toolbar docs)

**Context**: ~120 lines (96% reduction)

#### For Delta Format Questions

**User asks: "How does Delta format work?"**

**Load**:
1. `categories/delta.md` (complete Delta specification)

**Context**: ~150 lines (95% reduction)

#### For Event Handling

**User asks: "How do I listen for text changes?"**

**Load**:
1. `categories/api-events.md` (text-change, selection-change, etc.)

**Context**: ~100 lines (97% reduction)

#### For Advanced Customization

**User asks: "How do I create a custom format with Parchment?"**

**Load**:
1. `guides/parchment-blots.md` (Blot types, custom formats)
2. `categories/api-extension.md` (Quill.register())

**Context**: ~200 lines (93% reduction)

### Step 3: Provide Answer with Context

When answering:

1. **Direct Answer First**: Provide the immediate answer with code example
2. **Code Example**: Show TypeScript/JavaScript implementation
3. **Category Reference**: Note which category file was consulted
4. **Official Docs Link**: Link to specific section on quilljs.com
5. **Additional Resources**: Offer to load more details if needed

---

## Usage Examples

### Example 1: Basic Setup Question

**User**: "How do I initialize Quill with the Snow theme?"

**Your Response**:
```markdown
To initialize Quill with the Snow theme, you need to:

1. Include the Snow stylesheet
2. Create a container element
3. Initialize with theme option

Let me load the getting-started guide for you...
[Load categories/getting-started.md]

**HTML Setup**:
```html
<!-- Stylesheet -->
<link href="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css" rel="stylesheet" />

<!-- Container -->
<div id="editor">
  <p>Hello World!</p>
</div>

<!-- Library -->
<script src="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.js"></script>
```

**JavaScript Initialization**:
```javascript
const quill = new Quill('#editor', {
  theme: 'snow'
});
```

**Official Docs**: https://quilljs.com/docs/quickstart
**Category Reference**: categories/getting-started.md

Would you like to see configuration options or toolbar customization?
```

### Example 2: API Method Question

**User**: "How do I insert text with bold formatting?"**

**Your Response**:
```markdown
Use the `insertText()` method with format parameters.

[Load categories/api-content.md for method details]

**Method Signature**:
```typescript
insertText(index: number, text: string, format?: string, value?: any, source?: string): Delta
```

**Example - Insert bold text**:
```javascript
// Insert "Hello" in bold at position 0
quill.insertText(0, 'Hello', 'bold', true);

// Insert "World" with multiple formats
quill.insertText(6, 'World', {
  bold: true,
  color: '#ff0000'
});
```

**Official Docs**: https://quilljs.com/docs/api/#inserttext
**Category Reference**: categories/api-content.md

**Related Methods**:
- `formatText()` - Format existing text
- `getContents()` - Retrieve formatted content as Delta

Would you like to see all available formats or learn about the Delta format?
```

### Example 3: Module Configuration Question

**User**: "How do I add custom buttons to the toolbar?"**

**Your Response**:
```markdown
You can configure the toolbar using either array-based or HTML container approaches.

[Load categories/toolbar-module.md]

**Array-Based Approach** (simplest):
```javascript
const quill = new Quill('#editor', {
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline'],
      [{ 'header': 1 }, { 'header': 2 }],
      ['link', 'image']
    ]
  },
  theme: 'snow'
});
```

**Custom Handler Example**:
```javascript
const quill = new Quill('#editor', {
  modules: {
    toolbar: {
      container: [['bold', 'link']],
      handlers: {
        link: function(value) {
          if (value) {
            const href = prompt('Enter the URL');
            this.quill.format('link', href);
          } else {
            this.quill.format('link', false);
          }
        }
      }
    }
  }
});
```

**Official Docs**: https://quilljs.com/docs/modules/toolbar
**Category Reference**: categories/toolbar-module.md

Would you like to see the HTML container approach or learn about other modules?
```

### Example 4: Delta Format Question

**User**: "What is Delta format and how do I use it?"

**Your Response**:
```markdown
Delta is Quill's JSON-based format for describing editor content and changes.

[Load categories/delta.md]

**Basic Document Structure**:
```javascript
{
  ops: [
    { insert: 'Gandalf', attributes: { bold: true } },
    { insert: ' the ' },
    { insert: 'Grey', attributes: { color: '#cccccc' } }
  ]
}
```

**Key Concepts**:
- **Document Delta**: Describes current editor content
- **Change Delta**: Describes modifications (insert, delete, retain)
- **Operations**: Sequential array of changes
- **Attributes**: Formatting applied to content

**Get Content as Delta**:
```javascript
const delta = quill.getContents();
console.log(delta);
```

**Set Content from Delta**:
```javascript
quill.setContents({
  ops: [
    { insert: 'Hello ' },
    { insert: 'World', attributes: { bold: true } },
    { insert: '\n' }
  ]
});
```

**Official Docs**: https://quilljs.com/docs/delta
**Category Reference**: categories/delta.md

Would you like to see change operations (delete, retain) or learn about line formatting?
```

---

## Quick Reference: API Categories

### Content Methods (10 methods)
```javascript
deleteText(index, length, source)
getContents(index, length)
getLength()
getText(index, length)
getSemanticHTML(index, length)
insertEmbed(index, type, value, source)
insertText(index, text, [format, value], source)
setContents(delta, source)
setText(text, source)
updateContents(delta, source)
```
**Load**: `categories/api-content.md`

### Formatting Methods (5 methods)
```javascript
format(name, value, source)
formatLine(index, length, format, value, source)
formatText(index, length, format, value, source)
getFormat(range | index, length)
removeFormat(index, length, source)
```
**Load**: `categories/api-formatting.md`

### Selection Methods (4 methods)
```javascript
getBounds(index, length)
getSelection(focus)
setSelection(index, length, source)
scrollSelectionIntoView()
```
**Load**: `categories/api-selection.md`

### Modules
- **Toolbar**: Button/dropdown configuration, custom handlers
- **Keyboard**: Key bindings, context specifications
- **History**: Undo/redo configuration
- **Clipboard**: Paste matchers, HTML processing
- **Syntax**: Code highlighting with highlight.js

---

## Critical Information

### Source Parameter

Most API methods accept a `source` parameter:
- `'user'` - Changes from user interactions
- `'api'` - Changes from API calls (default)
- `'silent'` - Suppresses events

**Use Cases**:
- `'api'` (default) - Normal programmatic changes
- `'silent'` - Prevent event firing (e.g., in event handlers to avoid loops)

### Index-Based Operations

Quill uses 0-based index positions:
- Index 0 = beginning of document
- Index includes all characters (including newlines)
- Use `getLength()` to get total length
- Minimum length is always 1 (for trailing newline)

### Delta Format Rules

✅ **Always** end documents with newline (`\n`)
✅ Line formats apply to newline characters
✅ Many line formats are mutually exclusive (e.g., can't be both header and blockquote)
✅ Deltas are irreversible (delete operations don't record deleted content)

### TypeScript Support

Quill v2.0+ includes official TypeScript definitions:
```typescript
import Quill from 'quill';

const quill = new Quill('#editor', {
  theme: 'snow',
  modules: {
    toolbar: [['bold', 'italic']]
  }
});
```

---

## Common Workflows

### When to Use Each Category File

**categories/getting-started.md** - Use when you need to:
- Set up Quill for the first time
- Understand basic initialization
- Learn why to use Quill over alternatives

**categories/api-content.md** - Use when you need to:
- Insert, delete, or modify text content
- Retrieve content in different formats (Delta, text, HTML)
- Work with embeds (images, videos, formulas)

**categories/api-formatting.md** - Use when you need to:
- Apply inline formatting (bold, color, etc.)
- Apply block formatting (headers, lists, alignment)
- Query current formatting
- Remove formatting

**categories/api-events.md** - Use when you need to:
- Listen for content changes
- Track selection/cursor changes
- Implement autosave or real-time sync
- React to user interactions

**categories/delta.md** - Use when you need to:
- Understand content representation
- Implement operational transformation
- Build real-time collaborative editing
- Export/import content in JSON format

**categories/toolbar-module.md** - Use when you need to:
- Configure toolbar buttons and dropdowns
- Add custom formatting controls
- Implement custom toolbar handlers
- Integrate external UI elements

**categories/keyboard-module.md** - Use when you need to:
- Add custom keyboard shortcuts
- Override default key bindings
- Implement context-aware shortcuts
- Handle platform-specific keys (Cmd vs Ctrl)

**guides/parchment-blots.md** - Use when you need to:
- Create custom inline formats
- Create custom block formats
- Create custom embeds
- Build advanced content types (Medium-like features)

---

## Your Mission

Help users successfully implement Quill.js rich text editor by:

1. **Loading ONLY relevant resources** (progressive disclosure)
2. **Providing task-based guidance** (use category files appropriately)
3. **Explaining concepts clearly** (reference pattern files)
4. **Generating correct code** (TypeScript/JavaScript with types)
5. **Debugging integration issues** (common pitfalls and solutions)
6. **Offering additional resources** (can always load more details)

**You have complete knowledge of Quill.js v2.0.3 API via modular, focused files. Use progressive disclosure to provide fast, relevant answers!**

---

## Version Information

- **Current Version**: v2.0.3 (2024)
- **License**: BSD 3-Clause
- **Repository**: https://github.com/slab/quill
- **Previous Version Docs**: https://v1.quilljs.com

**Breaking Changes from v1.x**:
- TypeScript rewrite with official types
- Embedded SVG icons (no bundler config needed)
- Configuration changes (`strict` removed, `registry` added)
- Clipboard module API restructure
- Parchment library changes
- IE support dropped

For migration details, see `patterns/upgrading.md`
