# Clipboard Module

## Overview

The Clipboard module handles paste behavior in Quill. It processes pasted HTML content through DOM traversal and allows customization via matchers.

**Official Documentation:** https://quilljs.com/docs/modules/clipboard

## How It Works

When content is pasted:

1. HTML is inserted into hidden DOM container
2. DOM tree is traversed
3. Matchers are applied to transform nodes
4. Result is converted to Delta format
5. Delta is inserted into editor

## Configuration

```javascript
const quill = new Quill('#editor', {
  modules: {
    clipboard: {
      matchVisual: false,  // Don't adjust pasted content to match visual
      matchers: [
        // Custom matchers
        ['img', imageMatcherFunction],
        [Node.TEXT_NODE, textMatcherFunction]
      ]
    }
  }
});
```

## Adding Matchers

### Using Configuration

Define matchers in configuration:

```javascript
const quill = new Quill('#editor', {
  modules: {
    clipboard: {
      matchers: [
        // CSS selector
        ['b', boldMatcher],
        ['strong', boldMatcher],

        // Node type
        [Node.TEXT_NODE, textMatcher],
        [Node.ELEMENT_NODE, elementMatcher]
      ]
    }
  }
});

function boldMatcher(node, delta) {
  return delta.compose(new Delta().retain(delta.length(), { bold: true }));
}
```

### Using addMatcher()

Add matchers after initialization:

```typescript
addMatcher(selector: string | number, callback: (node: any, delta: Delta) => Delta): void
```

```javascript
const quill = new Quill('#editor');
const clipboard = quill.getModule('clipboard');

// Add matcher for <b> tags
clipboard.addMatcher('b', function(node, delta) {
  return delta.compose(new Delta().retain(delta.length(), { bold: true }));
});

// Add matcher for all text nodes
clipboard.addMatcher(Node.TEXT_NODE, function(node, delta) {
  // Transform text content
  return delta;
});
```

## Matcher Function

Matcher functions receive the DOM node and current Delta, and return a modified Delta:

```typescript
type MatcherFunction = (node: HTMLElement | Text, delta: Delta) => Delta;
```

### Parameters

- `node`: DOM node being processed (HTMLElement or Text node)
- `delta`: Current Delta representing node content

### Return Value

Return a Delta that replaces the default conversion:

```javascript
function customMatcher(node, delta) {
  // Option 1: Return modified delta
  return delta.compose(new Delta().retain(delta.length(), { color: 'red' }));

  // Option 2: Return completely new delta
  return new Delta().insert(node.textContent, { bold: true });

  // Option 3: Return empty delta to ignore node
  return new Delta();
}
```

## Matcher Execution Order

Matchers are executed in order of specificity:

1. Most specific CSS selectors (e.g., `div.class#id`)
2. Less specific CSS selectors (e.g., `div`)
3. Node type matchers (e.g., `Node.ELEMENT_NODE`)

Later matchers override earlier ones for the same selector:

```javascript
// First matcher
clipboard.addMatcher('span', function(node, delta) {
  return delta.compose(new Delta().retain(delta.length(), { color: 'red' }));
});

// Second matcher (overrides first for spans)
clipboard.addMatcher('span', function(node, delta) {
  return delta.compose(new Delta().retain(delta.length(), { color: 'blue' }));
});
```

## Complete Examples

### Remove Formatting on Paste

Strip all formatting and paste as plain text:

```javascript
const quill = new Quill('#editor', {
  modules: {
    clipboard: {
      matchers: [
        [Node.ELEMENT_NODE, function(node, delta) {
          // Remove all formatting
          return delta.compose(new Delta().retain(delta.length(), {
            bold: false,
            italic: false,
            underline: false,
            strike: false,
            color: false,
            background: false,
            font: false,
            size: false
          }));
        }]
      ]
    }
  }
});
```

### Convert Images to Links

Replace pasted images with links to image URLs:

```javascript
clipboard.addMatcher('img', function(node, delta) {
  const url = node.getAttribute('src');
  return new Delta().insert(url, { link: url });
});
```

### Preserve Specific Attributes

Keep only specific formatting:

```javascript
clipboard.addMatcher(Node.ELEMENT_NODE, function(node, delta) {
  const ops = delta.ops.map(op => {
    if (op.attributes) {
      // Keep only bold, italic, link
      const allowedAttrs = {};
      if (op.attributes.bold) allowedAttrs.bold = true;
      if (op.attributes.italic) allowedAttrs.italic = true;
      if (op.attributes.link) allowedAttrs.link = op.attributes.link;

      return {
        insert: op.insert,
        attributes: Object.keys(allowedAttrs).length > 0 ? allowedAttrs : undefined
      };
    }
    return op;
  });

  return new Delta(ops);
});
```

### Custom HTML Tag Handling

Convert custom HTML tags to Quill formats:

```javascript
// Convert <mark> to yellow highlight
clipboard.addMatcher('mark', function(node, delta) {
  return delta.compose(
    new Delta().retain(delta.length(), { background: '#ffff00' })
  );
});

// Convert <kbd> to code format
clipboard.addMatcher('kbd', function(node, delta) {
  return delta.compose(
    new Delta().retain(delta.length(), { code: true })
  );
});

// Convert custom data attributes
clipboard.addMatcher('[data-mention]', function(node, delta) {
  const userId = node.getAttribute('data-mention');
  return new Delta().insert('@', { mention: userId });
});
```

### Clean Microsoft Word Formatting

Remove Word-specific formatting:

```javascript
const quill = new Quill('#editor', {
  modules: {
    clipboard: {
      matchers: [
        // Remove Word-specific classes
        ['[class^="Mso"]', function(node, delta) {
          node.removeAttribute('class');
          return delta;
        }],

        // Remove Word-specific styles
        [Node.ELEMENT_NODE, function(node, delta) {
          if (node.style) {
            // Remove mso-* styles
            const styles = node.style;
            for (let i = styles.length - 1; i >= 0; i--) {
              const prop = styles[i];
              if (prop.startsWith('mso-')) {
                node.style.removeProperty(prop);
              }
            }
          }
          return delta;
        }]
      ]
    }
  }
});
```

### Transform Links

Modify pasted links:

```javascript
clipboard.addMatcher('a', function(node, delta) {
  const href = node.getAttribute('href');

  // Convert relative URLs to absolute
  if (href && !href.startsWith('http')) {
    const absolute = new URL(href, window.location.href).href;
    return delta.compose(
      new Delta().retain(delta.length(), { link: absolute })
    );
  }

  // Add target="_blank" to external links
  if (href && href.startsWith('http')) {
    return delta.compose(
      new Delta().retain(delta.length(), {
        link: href,
        target: '_blank'
      })
    );
  }

  return delta;
});
```

## dangerouslyPasteHTML

Insert raw HTML directly (bypasses matchers):

```typescript
dangerouslyPasteHTML(html: string, source?: string): void
dangerouslyPasteHTML(index: number, html: string, source?: string): void
```

**WARNING:** This method is dangerous because it can introduce XSS vulnerabilities. Only use with trusted HTML.

```javascript
const clipboard = quill.getModule('clipboard');

// Append HTML to end
clipboard.dangerouslyPasteHTML('<p>Trusted HTML content</p>');

// Insert HTML at specific index
clipboard.dangerouslyPasteHTML(10, '<strong>Inserted</strong>');

// With source
clipboard.dangerouslyPasteHTML(0, '<p>Content</p>', 'api');
```

**Safe Alternative:**

```javascript
// ✅ SAFE: Convert HTML to Delta first
const delta = clipboard.convert(trustedHtml);
quill.setContents(delta);

// ❌ DANGEROUS: Direct HTML insertion
clipboard.dangerouslyPasteHTML(untrustedHtml);  // XSS risk!
```

## Convert Method

Convert HTML to Delta without inserting:

```typescript
convert(html: string): Delta
```

```javascript
const clipboard = quill.getModule('clipboard');

// Convert HTML to Delta
const html = '<p>Hello <strong>World</strong></p>';
const delta = clipboard.convert(html);

console.log(delta);
// {
//   ops: [
//     { insert: 'Hello ' },
//     { insert: 'World', attributes: { bold: true } },
//     { insert: '\n' }
//   ]
// }

// Can then insert the delta
quill.setContents(delta);
```

**Use cases:**
- Preview pasted content before insertion
- Transform HTML for storage
- Validate content before pasting

## Advanced Examples

### Sanitize and Validate

Validate pasted content before insertion:

```javascript
const clipboard = quill.getModule('clipboard');

quill.clipboard.addMatcher(Node.ELEMENT_NODE, function(node, delta) {
  // Block script tags
  if (node.tagName === 'SCRIPT') {
    return new Delta();
  }

  // Block inline event handlers
  const attrs = node.attributes;
  for (let i = attrs.length - 1; i >= 0; i--) {
    const attr = attrs[i];
    if (attr.name.startsWith('on')) {
      node.removeAttribute(attr.name);
    }
  }

  return delta;
});
```

### Preserve Code Blocks

Maintain code formatting when pasting from code editors:

```javascript
clipboard.addMatcher('pre', function(node, delta) {
  // Convert <pre> to code-block
  return delta.compose(
    new Delta()
      .retain(delta.length(), { 'code-block': true })
      .delete(1)  // Remove extra newline
  );
});

clipboard.addMatcher('code', function(node, delta) {
  // If inside <pre>, it's a code block
  if (node.parentElement.tagName === 'PRE') {
    return delta;
  }

  // Otherwise, inline code
  return delta.compose(
    new Delta().retain(delta.length(), { code: true })
  );
});
```

### Smart List Detection

Convert HTML lists to Quill lists:

```javascript
clipboard.addMatcher('li', function(node, delta) {
  const parent = node.parentElement;
  const listType = parent.tagName === 'OL' ? 'ordered' : 'bullet';

  // Add list formatting to newline
  return delta.compose(
    new Delta()
      .retain(delta.length() - 1)
      .retain(1, { list: listType })
  );
});
```

## TypeScript Support

```typescript
import Quill from 'quill';
import Delta from 'quill-delta';

interface ClipboardModule {
  addMatcher(
    selector: string | number,
    callback: (node: any, delta: Delta) => Delta
  ): void;
  dangerouslyPasteHTML(html: string, source?: string): void;
  dangerouslyPasteHTML(index: number, html: string, source?: string): void;
  convert(html: string): Delta;
}

const quill = new Quill('#editor');
const clipboard = quill.getModule('clipboard') as ClipboardModule;

clipboard.addMatcher('strong', (node: HTMLElement, delta: Delta): Delta => {
  return delta.compose(new Delta().retain(delta.length(), { bold: true }));
});

const converted: Delta = clipboard.convert('<p>HTML</p>');
```

## Performance Considerations

- Complex matchers can slow down paste operations
- Avoid heavy DOM manipulation in matchers
- Use specific selectors instead of Node.ELEMENT_NODE when possible
- Cache repeated calculations
- Test with large pastes (entire documents)

## Related Files

- **delta.md** - Delta format used for clipboard operations
- **configuration.md** - Module configuration
- **api-content.md** - Methods for setting content
- **formats.md** - Available format attributes

## Notes

- Clipboard module is enabled by default in Snow and Bubble themes
- Matchers are powerful but can introduce complexity
- Always sanitize untrusted HTML to prevent XSS
- Test paste behavior across different sources (Word, Google Docs, web pages)
- Some browsers may strip certain HTML/attributes before Quill sees it
