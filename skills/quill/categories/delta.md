# Delta Format

## Overview

Delta is a JSON-based format for describing rich text documents and changes. It provides a simple and expressive way to represent document content and transformations.

**Official Documentation:** https://quilljs.com/docs/delta

## Purpose

- **Document Representation:** Store and transmit rich text content
- **Change Description:** Represent modifications to documents
- **Operational Transformation:** Enable collaborative editing
- **Version Control:** Track document history and changes

## Document Delta Structure

A Delta is an array of operations stored in an `ops` property:

```typescript
interface Delta {
  ops: Op[];
}

type Op = InsertOp | DeleteOp | RetainOp;
```

### Insert Operations

Insert operations add content to the document:

```typescript
interface InsertOp {
  insert: string | object;  // Text or embed
  attributes?: Record<string, any>;
}
```

**Text Insert Examples:**

```javascript
// Plain text
{ insert: "Hello World" }

// Bold text
{ insert: "Hello", attributes: { bold: true } }

// Multiple attributes
{
  insert: "Formatted text",
  attributes: {
    bold: true,
    italic: true,
    color: "#ff0000"
  }
}
```

**Embed Insert Examples:**

```javascript
// Image embed
{
  insert: {
    image: "https://example.com/image.png"
  },
  attributes: { width: "300" }
}

// Video embed
{
  insert: {
    video: "https://example.com/video.mp4"
  }
}

// Custom embed
{
  insert: {
    mention: {
      id: 123,
      value: "John Doe"
    }
  }
}
```

### Line Formatting

Line-level formats are represented as attributes on the newline character:

```javascript
// Heading
{
  ops: [
    { insert: "Heading Text" },
    { insert: "\n", attributes: { header: 1 } }
  ]
}

// List item
{
  ops: [
    { insert: "List item" },
    { insert: "\n", attributes: { list: "bullet" } }
  ]
}

// Aligned paragraph
{
  ops: [
    { insert: "Centered text" },
    { insert: "\n", attributes: { align: "center" } }
  ]
}

// Multiple line formats
{
  ops: [
    { insert: "Indented heading" },
    {
      insert: "\n",
      attributes: {
        header: 2,
        indent: 1
      }
    }
  ]
}
```

## Complete Document Example

```javascript
const documentDelta = {
  ops: [
    { insert: "Title", attributes: { bold: true } },
    { insert: "\n", attributes: { header: 1 } },
    { insert: "This is a " },
    { insert: "paragraph", attributes: { italic: true } },
    { insert: " with " },
    { insert: "formatting", attributes: { bold: true, color: "#0000ff" } },
    { insert: ".\n" },
    { insert: "Bullet point 1" },
    { insert: "\n", attributes: { list: "bullet" } },
    { insert: "Bullet point 2" },
    { insert: "\n", attributes: { list: "bullet" } },
    {
      insert: {
        image: "https://example.com/image.png"
      }
    },
    { insert: "\n" }
  ]
};
```

## Change Operations

Deltas can also represent changes to documents using three operation types:

### Delete Operations

Remove characters from the document:

```typescript
interface DeleteOp {
  delete: number;  // Number of characters to delete
}
```

```javascript
// Delete 5 characters
{ delete: 5 }
```

### Retain Operations

Keep existing content, optionally modifying attributes:

```typescript
interface RetainOp {
  retain: number;  // Number of characters to keep
  attributes?: Record<string, any>;
}
```

```javascript
// Retain 10 characters unchanged
{ retain: 10 }

// Retain 5 characters and make them bold
{ retain: 5, attributes: { bold: true } }

// Retain 3 characters and remove italic
{ retain: 3, attributes: { italic: null } }
```

## Change Delta Examples

### Simple Text Insertion

Insert "Hello " at the beginning:

```javascript
{
  ops: [
    { insert: "Hello " }
  ]
}
```

### Text Deletion

Delete first 5 characters:

```javascript
{
  ops: [
    { delete: 5 }
  ]
}
```

### Format Change

Make characters 5-10 bold:

```javascript
{
  ops: [
    { retain: 5 },
    { retain: 5, attributes: { bold: true } }
  ]
}
```

### Complex Change

Delete 3 characters, insert "new", and format next 5 as italic:

```javascript
{
  ops: [
    { retain: 10 },
    { delete: 3 },
    { insert: "new" },
    { retain: 5, attributes: { italic: true } }
  ]
}
```

### Replace Text

Replace characters 5-10 with "replacement":

```javascript
{
  ops: [
    { retain: 5 },
    { delete: 5 },
    { insert: "replacement" }
  ]
}
```

## Delta Rules

### Newline Requirements

**Documents must end with a newline character:**

```javascript
// ✅ CORRECT
{ ops: [{ insert: "Text\n" }] }

// ❌ WRONG
{ ops: [{ insert: "Text" }] }
```

### Delete Operations

**Delete operations are irreversible - they don't retain deleted content:**

```javascript
// This delta only specifies to delete 5 characters
// It doesn't store what was deleted
{ ops: [{ delete: 5 }] }

// To track deletions, store the original content separately
```

### Attribute Removal

**Use `null` to remove attributes:**

```javascript
{
  ops: [
    { retain: 5, attributes: { bold: null } }  // Remove bold
  ]
}
```

### Operational Transformation

Deltas can be composed and transformed for collaborative editing:

```javascript
// Apply change to document
const newDocument = document.compose(change);

// Transform concurrent changes
const transformed = changeA.transform(changeB, true);
```

## Use Cases

### Content Storage

Store document content in database:

```javascript
// Store as JSON
const content = JSON.stringify(quill.getContents());

// Retrieve and set
const delta = JSON.parse(content);
quill.setContents(delta);
```

### Change Tracking

Track user modifications:

```javascript
quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user') {
    console.log('User made changes:', delta);
    // Save delta to change log
  }
});
```

### Collaborative Editing

Synchronize changes between clients:

```javascript
// Send local changes to server
quill.on('text-change', (delta) => {
  socket.emit('change', delta);
});

// Receive and apply remote changes
socket.on('change', (delta) => {
  quill.updateContents(delta);
});
```

### Import/Export

Convert between formats:

```javascript
// Export to Delta
const delta = quill.getContents();

// Import from HTML
const delta = quill.clipboard.convert(htmlContent);
quill.setContents(delta);
```

## Related Files

- **formats.md** - Format attributes used in Delta operations
- **api-content.md** - Methods for getting/setting content as Delta
- **clipboard-module.md** - Converting HTML to Delta
- **events.md** - text-change event provides Delta

## TypeScript Support

```typescript
import Quill from 'quill';
import Delta from 'quill-delta';

const quill = new Quill('#editor');

// Get contents as Delta
const contents: Delta = quill.getContents();

// Set contents from Delta
quill.setContents(new Delta([
  { insert: 'Hello ' },
  { insert: 'World', attributes: { bold: true } },
  { insert: '\n' }
]));

// Apply changes
quill.updateContents(new Delta([
  { retain: 6 },
  { delete: 5 },
  { insert: 'Quill' }
]));
```

## Performance Considerations

- Delta operations are lightweight and efficient
- Large documents should be paginated or lazy-loaded
- Use `retain` operations to minimize change size
- Compose multiple small changes into larger deltas for network efficiency

## External Resources

- **Official Delta Documentation:** https://quilljs.com/docs/delta
- **Delta Library:** https://github.com/quilljs/delta
- **Operational Transformation:** https://en.wikipedia.org/wiki/Operational_transformation
