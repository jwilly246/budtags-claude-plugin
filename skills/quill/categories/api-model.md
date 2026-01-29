# Quill Model & Traversal API

Complete reference for all 5 model traversal methods and the Blot system in Quill.js.

---

## Overview

Model traversal methods provide low-level access to Quill's internal document structure. These methods allow you to:

- Navigate the document tree (Blot hierarchy)
- Convert between document positions and DOM elements
- Access line and leaf nodes
- Implement advanced editing features

**Core Methods**:
- `find()` - Find Quill instance or Blot from DOM node (static method)
- `getIndex()` - Get position of a Blot in the document
- `getLeaf()` - Get leaf Blot at specific position
- `getLine()` - Get line Blot at specific position
- `getLines()` - Get all lines in a range

**Blot Concept**: Quill represents content as a tree of Blots (text, formatting, lines, embeds). These methods expose that tree structure.

---

## Understanding Blots

Before diving into methods, understand the Blot system:

**Blot Hierarchy**:
```
Scroll (root)
├── Block (paragraph, header, list item)
│   ├── Inline (bold, link, etc.)
│   │   └── Text (actual characters)
│   └── Text
└── BlockEmbed (image, video, formula)
```

**Blot Types**:
- **Scroll** - Root container
- **Block** - Line-level elements (paragraphs, headers, lists)
- **Inline** - Character-level formatting (bold, italic, links)
- **Text** - Leaf nodes containing actual text
- **Embed** - Non-text content (images, videos)

**Key Concepts**:
- **Leaf Blot** - Lowest level (Text or Embed)
- **Block Blot** - Line-level container
- **Offset** - Position within a Blot

---

## find() (Static Method)

Finds a Quill instance or Blot from a DOM node.

**Signature**:
```typescript
Quill.find(domNode: Node, bubble?: boolean): Blot | Quill | null
```

**Parameters**:
- `domNode` - DOM element to search from
- `bubble` - If `true`, search up DOM tree to find parent Blot (default: `false`)

**Returns**:
- Quill instance if `domNode` is editor container
- Blot if `domNode` is inside editor
- `null` if not found

**Examples**:

**Find Quill Instance**:
```javascript
const editorElement = document.querySelector('.ql-editor');
const quill = Quill.find(editorElement);

if (quill) {
  console.log('Found Quill instance:', quill);
}
```

**Find Blot from DOM Node**:
```javascript
const paragraph = document.querySelector('.ql-editor p');
const blot = Quill.find(paragraph);

if (blot) {
  console.log('Found Blot:', blot);
  console.log('Blot type:', blot.statics.blotName);
}
```

**Find with Bubble**:
```javascript
// Find nearest Blot by traversing up DOM tree
const textNode = document.querySelector('.ql-editor span').firstChild;
const blot = Quill.find(textNode, true);

console.log('Found parent Blot:', blot);
```

**Handle Click Events**:
```javascript
document.querySelector('.ql-editor').addEventListener('click', (e) => {
  const blot = Quill.find(e.target, true);

  if (blot) {
    console.log('Clicked on:', blot.statics.blotName);

    if (blot.statics.blotName === 'link') {
      console.log('Link URL:', blot.domNode.href);
    }
  }
});
```

**Get Quill from Event**:
```javascript
function handleEditorClick(event) {
  const quill = Quill.find(event.target.closest('.ql-container'));

  if (quill) {
    const range = quill.getSelection();
    console.log('Clicked in editor at:', range);
  }
}
```

**Important Notes**:
- **Static method** - call on `Quill` class, not instance
- Returns `null` if DOM node not part of Quill editor
- Use `bubble: true` to find parent Blot from child elements
- Useful for event handling and DOM manipulation

**Use Cases**:
- Event handling (click, drag, drop)
- Finding Quill instance from DOM
- Custom interactions with editor elements
- Browser extension development

---

## getIndex()

Gets the document position (index) of a Blot.

**Signature**:
```typescript
getIndex(blot: Blot): number
```

**Parameters**:
- `blot` - Blot to find position of

**Returns**: Index (0-based position) in document

**Examples**:

**Get Position of Clicked Element**:
```javascript
quill.root.addEventListener('click', (e) => {
  const blot = Quill.find(e.target, true);

  if (blot) {
    const index = quill.getIndex(blot);
    console.log('Clicked element is at position:', index);
  }
});
```

**Get Line Start Position**:
```javascript
const [line, offset] = quill.getLine(50);
const lineStartIndex = quill.getIndex(line);
console.log('Line starts at:', lineStartIndex);
```

**Find Image Position**:
```javascript
const images = document.querySelectorAll('.ql-editor img');
images.forEach(img => {
  const blot = Quill.find(img);
  if (blot) {
    const index = quill.getIndex(blot);
    console.log('Image at position:', index);
  }
});
```

**Navigate Between Elements**:
```javascript
function getNextLineIndex(currentIndex) {
  const [currentLine] = quill.getLine(currentIndex);
  const currentLineIndex = quill.getIndex(currentLine);
  const nextIndex = currentLineIndex + currentLine.length();

  return nextIndex;
}
```

**Important Notes**:
- Returns position **from start of document**
- Position includes **all previous content** (text, embeds, newlines)
- Useful with other methods like `getLine`, `getLeaf`

**Use Cases**:
- Converting Blot references to positions
- DOM event to document position mapping
- Custom navigation logic
- Element position tracking

---

## getLeaf()

Gets the leaf Blot (Text or Embed) at a specific position.

**Signature**:
```typescript
getLeaf(index: number): [Blot | null, number]
```

**Parameters**:
- `index` - Document position (0-based)

**Returns**: Tuple of `[LeafBlot, offsetWithinBlot]` or `[null, -1]` if invalid

**Examples**:

**Get Leaf at Position**:
```javascript
const [leaf, offset] = quill.getLeaf(10);

if (leaf) {
  console.log('Leaf type:', leaf.statics.blotName);
  console.log('Offset within leaf:', offset);

  if (leaf.statics.blotName === 'text') {
    console.log('Text:', leaf.text);
  }
}
```

**Get Character at Position**:
```javascript
function getCharAt(index) {
  const [leaf, offset] = quill.getLeaf(index);

  if (leaf && leaf.text) {
    return leaf.text[offset];
  }

  return null;
}

console.log('Character at 5:', getCharAt(5));
```

**Get Word Under Cursor**:
```javascript
function getWordAtCursor() {
  const range = quill.getSelection(true);
  const [leaf, offset] = quill.getLeaf(range.index);

  if (leaf && leaf.text) {
    const text = leaf.text;
    let start = offset;
    let end = offset;

    // Find word boundaries
    while (start > 0 && /\w/.test(text[start - 1])) start--;
    while (end < text.length && /\w/.test(text[end])) end++;

    return text.substring(start, end);
  }

  return '';
}
```

**Check if Position is in Link**:
```javascript
function isPositionInLink(index) {
  const [leaf, offset] = quill.getLeaf(index);

  if (leaf) {
    let parent = leaf.parent;
    while (parent) {
      if (parent.statics.blotName === 'link') {
        return true;
      }
      parent = parent.parent;
    }
  }

  return false;
}
```

**Navigate by Character**:
```javascript
function getNextCharacterIndex(currentIndex) {
  const [leaf, offset] = quill.getLeaf(currentIndex);

  if (leaf) {
    const leafIndex = quill.getIndex(leaf);
    const leafLength = leaf.length();

    if (offset < leafLength - 1) {
      // Move within same leaf
      return currentIndex + 1;
    } else {
      // Move to next leaf
      return leafIndex + leafLength;
    }
  }

  return currentIndex;
}
```

**Important Notes**:
- Returns **lowest-level Blot** (Text or Embed)
- Offset is **position within that Blot**
- Useful for character-level operations
- Text Blots have `.text` property with actual text

**Leaf Blot Properties**:
```javascript
const [leaf, offset] = quill.getLeaf(10);

if (leaf) {
  console.log('Blot name:', leaf.statics.blotName);
  console.log('Length:', leaf.length());
  console.log('Parent:', leaf.parent);
  console.log('DOM node:', leaf.domNode);

  if (leaf.text) {
    console.log('Text content:', leaf.text);
  }
}
```

**Use Cases**:
- Character-level navigation
- Word selection
- Custom text processing
- Autocomplete logic
- Syntax highlighting

---

## getLine()

Gets the line Blot (Block) at a specific position.

**Signature**:
```typescript
getLine(index: number): [Block | null, number]
```

**Parameters**:
- `index` - Document position (0-based)

**Returns**: Tuple of `[LineBlot, offsetWithinLine]` or `[null, -1]` if invalid

**Examples**:

**Get Line at Position**:
```javascript
const [line, offset] = quill.getLine(10);

if (line) {
  console.log('Line type:', line.statics.blotName);
  console.log('Offset within line:', offset);
  console.log('Line length:', line.length());
}
```

**Get Line Number**:
```javascript
function getLineNumber(index) {
  const lines = quill.getLines(0, index);
  return lines.length;
}

const lineNum = getLineNumber(50);
console.log('Position 50 is on line:', lineNum);
```

**Select Entire Line**:
```javascript
function selectLine(index) {
  const [line, offset] = quill.getLine(index);

  if (line) {
    const lineIndex = quill.getIndex(line);
    quill.setSelection(lineIndex, line.length());
  }
}
```

**Get Line Format**:
```javascript
const [line, offset] = quill.getLine(10);

if (line) {
  console.log('Is header:', line.statics.blotName === 'header');
  console.log('Is list item:', line.statics.blotName === 'list');
  console.log('Is code block:', line.statics.blotName === 'code-block');

  // Get line attributes
  console.log('Attributes:', line.formats());
}
```

**Format Current Line**:
```javascript
function formatCurrentLine(format, value) {
  const range = quill.getSelection(true);
  const [line, offset] = quill.getLine(range.index);

  if (line) {
    const lineIndex = quill.getIndex(line);
    quill.formatLine(lineIndex, line.length(), format, value);
  }
}

formatCurrentLine('header', 1); // Make H1
```

**Navigate Lines**:
```javascript
function goToNextLine(currentIndex) {
  const [line, offset] = quill.getLine(currentIndex);

  if (line) {
    const lineIndex = quill.getIndex(line);
    const nextIndex = lineIndex + line.length();

    if (nextIndex < quill.getLength()) {
      quill.setSelection(nextIndex);
    }
  }
}
```

**Important Notes**:
- Returns **Block-level Blot** (paragraph, header, list item, etc.)
- Offset is **position within the line**
- Use `line.length()` to get line length
- Line includes trailing newline in length

**Line Blot Properties**:
```javascript
const [line, offset] = quill.getLine(10);

if (line) {
  console.log('Line name:', line.statics.blotName);
  console.log('Line formats:', line.formats());
  console.log('Line length:', line.length());
  console.log('DOM node:', line.domNode);
  console.log('Children:', line.children);
}
```

**Use Cases**:
- Line-based navigation
- Line formatting
- Line number display
- Custom block operations
- Multi-line selection

---

## getLines()

Gets all line Blots in a specific range.

**Signature**:
```typescript
getLines(index: number, length?: number): (Block | BlockEmbed)[]
getLines(range: { index: number, length: number }): (Block | BlockEmbed)[]
```

**Parameters**:
- `index` - Starting position (0-based)
- `length` - Range length (default: rest of document)
- `range` - Range object `{ index, length }`

**Returns**: Array of Block or BlockEmbed Blots

**Examples**:

**Get All Lines**:
```javascript
const allLines = quill.getLines(0, quill.getLength());
console.log('Total lines:', allLines.length);
```

**Get Lines in Range**:
```javascript
// Get lines 10-50
const lines = quill.getLines(10, 40);
console.log('Lines in range:', lines.length);

// Using range object
const range = quill.getSelection();
if (range) {
  const selectedLines = quill.getLines(range);
  console.log('Selected lines:', selectedLines.length);
}
```

**Count Lines**:
```javascript
function getLineCount() {
  return quill.getLines(0, quill.getLength()).length;
}

console.log('Document has', getLineCount(), 'lines');
```

**Iterate Lines**:
```javascript
const lines = quill.getLines(0, quill.getLength());

lines.forEach((line, i) => {
  console.log(`Line ${i + 1}:`, line.statics.blotName);
  console.log('  Formats:', line.formats());
  console.log('  Length:', line.length());
});
```

**Format Multiple Lines**:
```javascript
function formatLines(startIndex, endIndex, format, value) {
  const lines = quill.getLines(startIndex, endIndex - startIndex);

  lines.forEach(line => {
    const lineIndex = quill.getIndex(line);
    quill.formatLine(lineIndex, line.length(), format, value);
  });
}

// Make lines 0-10 headers
formatLines(0, 100, 'header', 1);
```

**Filter Lines by Type**:
```javascript
const lines = quill.getLines(0, quill.getLength());

const headers = lines.filter(line => line.statics.blotName === 'header');
const lists = lines.filter(line => line.statics.blotName === 'list');
const codeBlocks = lines.filter(line => line.statics.blotName === 'code-block');

console.log('Headers:', headers.length);
console.log('List items:', lists.length);
console.log('Code blocks:', codeBlocks.length);
```

**Extract Text by Lines**:
```javascript
function getTextByLines() {
  const lines = quill.getLines(0, quill.getLength());

  return lines.map((line, i) => {
    const lineIndex = quill.getIndex(line);
    const lineText = quill.getText(lineIndex, line.length());
    return `Line ${i + 1}: ${lineText.trim()}`;
  }).join('\n');
}

console.log(getTextByLines());
```

**Go to Line**:
```javascript
function goToLine(lineNumber) {
  const lines = quill.getLines(0, quill.getLength());

  if (lineNumber > 0 && lineNumber <= lines.length) {
    const line = lines[lineNumber - 1];
    const lineIndex = quill.getIndex(line);
    quill.setSelection(lineIndex);
    quill.scrollSelectionIntoView();
  }
}

goToLine(10); // Jump to line 10
```

**Important Notes**:
- Returns **array of Block Blots**
- Includes all lines that **intersect** the range
- Partial line coverage includes entire line
- Array is in document order

**Use Cases**:
- Line counting
- Multi-line operations
- Table of contents generation
- Line-based formatting
- Document statistics

---

## Common Model Patterns

### Custom Context Menu
```javascript
quill.root.addEventListener('contextmenu', (e) => {
  e.preventDefault();

  const blot = Quill.find(e.target, true);
  const menu = document.getElementById('context-menu');

  if (blot) {
    const index = quill.getIndex(blot);
    const [line] = quill.getLine(index);

    // Build context menu based on blot type
    if (blot.statics.blotName === 'link') {
      showLinkMenu(menu, blot, e.pageX, e.pageY);
    } else if (blot.statics.blotName === 'image') {
      showImageMenu(menu, blot, e.pageX, e.pageY);
    } else if (line.statics.blotName === 'header') {
      showHeaderMenu(menu, line, e.pageX, e.pageY);
    }
  }
});
```

### Line Numbers
```javascript
function updateLineNumbers() {
  const lines = quill.getLines(0, quill.getLength());
  const lineNumberContainer = document.getElementById('line-numbers');

  lineNumberContainer.innerHTML = lines
    .map((_, i) => `<div class="line-num">${i + 1}</div>`)
    .join('');
}

quill.on('text-change', updateLineNumbers);
updateLineNumbers();
```

### Smart Enter Key
```javascript
quill.keyboard.addBinding({
  key: 'Enter',
  handler: function(range) {
    const [line, offset] = quill.getLine(range.index);

    // Continue list
    if (line.statics.blotName === 'list') {
      const lineIndex = quill.getIndex(line);
      const lineText = quill.getText(lineIndex, line.length());

      if (lineText.trim() === '') {
        // Empty list item - exit list
        quill.formatLine(range.index, 1, 'list', false);
        return false;
      }
    }

    return true; // Default behavior
  }
});
```

### Document Statistics
```javascript
function getDocumentStats() {
  const lines = quill.getLines(0, quill.getLength());
  const text = quill.getText();

  const stats = {
    lines: lines.length,
    characters: quill.getLength() - 1,
    words: text.trim().split(/\s+/).filter(w => w.length > 0).length,
    headers: lines.filter(l => l.statics.blotName === 'header').length,
    lists: lines.filter(l => l.statics.blotName === 'list').length,
    codeBlocks: lines.filter(l => l.statics.blotName === 'code-block').length
  };

  return stats;
}

console.log(getDocumentStats());
// { lines: 25, characters: 1250, words: 215, headers: 3, lists: 5, codeBlocks: 2 }
```

### Syntax Highlighting
```javascript
function highlightSyntax() {
  const lines = quill.getLines(0, quill.getLength());

  lines.forEach(line => {
    if (line.statics.blotName === 'code-block') {
      const lineIndex = quill.getIndex(line);
      const code = quill.getText(lineIndex, line.length());

      // Apply syntax highlighting (simplified)
      const keywords = ['function', 'const', 'let', 'var', 'return'];
      keywords.forEach(keyword => {
        const regex = new RegExp(`\\b${keyword}\\b`, 'g');
        let match;
        while ((match = regex.exec(code)) !== null) {
          quill.formatText(lineIndex + match.index, keyword.length, {
            color: '#0000ff'
          }, 'silent');
        }
      });
    }
  });
}
```

---

## Official Documentation

**URL**: https://quilljs.com/docs/api/#model

---

## Next Steps

- **Parchment**: See `guides/parchment-blots.md` for creating custom Blots
- **Content**: See `categories/api-content.md` for content manipulation
- **Selection**: See `categories/api-selection.md` for working with ranges
- **Events**: See `categories/api-events.md` for change tracking
