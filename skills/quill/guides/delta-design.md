# Designing the Delta Format

Design philosophy and principles behind Quill's Delta document format.

---

## Overview

Delta is Quill's document format designed to support rich text editing with a focus on predictability, consistency, and ease of implementation. This guide explores the design decisions behind Delta.

**Official Documentation**: https://quilljs.com/guides/designing-the-delta-format

---

## Design Principles

### 1. Predictability

**Goal**: Operations should have predictable, deterministic outcomes.

**Why it matters**: Developers need to reason about document transformations without surprises.

**Example**:
```javascript
// Predictable: Bold text is always represented the same way
{ insert: "Hello", attributes: { bold: true } }

// Not: <b>Hello</b> or <strong>Hello</strong> or <span style="font-weight:bold">Hello</span>
```

### 2. Consistency

**Goal**: Documents and changes should be represented uniformly.

**Why it matters**: Simplifies parsing, validation, and transformation logic.

**Example**:
```javascript
// Consistent structure for all operations
const document = {
  ops: [
    { insert: "Text" },
    { insert: "Bold", attributes: { bold: true } },
    { insert: "\n" }
  ]
};

// NOT mixed formats like:
// [{ type: 'text', value: 'Text' }, { html: '<b>Bold</b>' }]
```

### 3. Ease of Implementation

**Goal**: Simple to parse, generate, and manipulate programmatically.

**Why it matters**: Reduces bugs and makes Delta accessible to all skill levels.

**Example**:
```javascript
// Easy to iterate and transform
delta.ops.forEach(op => {
  if (op.attributes?.bold) {
    console.log('Found bold text:', op.insert);
  }
});

// vs parsing HTML: <p>Text <strong>more</strong> <b>text</b></p>
```

---

## Plain Text Representation

**Principle**: Rich text documents should be representable as plain text with metadata.

### Document as String + Formatting

A document is fundamentally a string of characters with formatting information:

```javascript
// Plain text
"Hello World\n"

// Rich text (same content + formatting)
{
  ops: [
    { insert: "Hello " },
    { insert: "World", attributes: { bold: true } },
    { insert: "\n" }
  ]
}
```

**Key insight**: Insert operations describe text insertion points, not DOM structure.

### Why not DOM/HTML?

**Problem with HTML**:
```html
<!-- Multiple valid representations for same content -->
<strong>Bold</strong>
<b>Bold</b>
<span style="font-weight: bold">Bold</span>

<!-- Ambiguous nesting -->
<b><i>Bold and italic</i></b>
<i><b>Bold and italic</b></i>
<!-- Are these equivalent? -->
```

**Delta solution**:
```javascript
// Single canonical representation
{ insert: "Bold and italic", attributes: { bold: true, italic: true } }
```

---

## Compact Constraint

**Principle**: Eliminate redundancy to minimize document size.

### Adjacent Operations Merge

Operations with identical attributes are merged:

```javascript
// ❌ Redundant
{
  ops: [
    { insert: "Hello", attributes: { bold: true } },
    { insert: " ", attributes: { bold: true } },
    { insert: "World", attributes: { bold: true } }
  ]
}

// ✅ Compact
{
  ops: [
    { insert: "Hello World", attributes: { bold: true } }
  ]
}
```

**Implementation**:
```javascript
// Delta automatically compacts operations
const delta = new Delta()
  .insert('Hello', { bold: true })
  .insert(' ', { bold: true })
  .insert('World', { bold: true });

console.log(delta.ops);
// [{ insert: "Hello World", attributes: { bold: true } }]
```

### Omit Default Values

Default or null values are omitted:

```javascript
// ❌ Verbose
{
  insert: "Text",
  attributes: {
    bold: false,
    italic: false,
    underline: false
  }
}

// ✅ Compact
{ insert: "Text" }
```

---

## Canonical Constraint

**Principle**: One-to-one mapping between documents and their Delta representation.

### Problem: Multiple Representations

Without canonicalization, same document could be represented differently:

```javascript
// Same visual result, different representations
[
  { insert: "A" },
  { insert: "B" },
  { insert: "C" }
]

[
  { insert: "AB" },
  { insert: "C" }
]

[
  { insert: "ABC" }
]
```

### Solution: Automatic Normalization

Delta normalizes to canonical form:

```javascript
const delta1 = new Delta([
  { insert: "A" },
  { insert: "B" },
  { insert: "C" }
]);

const delta2 = new Delta([{ insert: "ABC" }]);

// Both normalize to same canonical form
console.log(JSON.stringify(delta1) === JSON.stringify(delta2)); // true
```

**Benefits**:
- Document comparison is simple equality check
- Reduced storage/transmission size
- Predictable serialization

---

## Line Formatting Design

**Principle**: Line-level formats should be distinct from inline formats.

### Why Separate Line Formats?

**Problem**: Mixing inline and block formatting creates ambiguity:

```html
<!-- HTML: unclear where block formatting applies -->
<h1>Title with <strong>bold</strong> word</h1>
<!-- Is bold part of heading, or is heading part of bold? -->
```

**Solution**: Attach line formats to newline character:

```javascript
{
  ops: [
    { insert: "Title with " },
    { insert: "bold", attributes: { bold: true } }, // inline format
    { insert: "\n", attributes: { header: 1 } }     // line format on newline
  ]
}
```

### Line Format Rules

1. **Line formats only on newlines**:
```javascript
// ✅ Correct
{ insert: "\n", attributes: { header: 1 } }

// ❌ Wrong
{ insert: "Title", attributes: { header: 1 } }
```

2. **One newline per line**:
```javascript
// Each line ends with exactly one newline
{
  ops: [
    { insert: "Line 1\n" },
    { insert: "Line 2\n" },
    { insert: "Line 3\n" }
  ]
}
```

3. **Documents end with newline**:
```javascript
// ✅ Valid document
{
  ops: [
    { insert: "Content\n" }
  ]
}

// ❌ Invalid - missing final newline
{
  ops: [
    { insert: "Content" }
  ]
}
```

### Line Format Examples

```javascript
// Heading
{
  ops: [
    { insert: "Chapter 1" },
    { insert: "\n", attributes: { header: 1 } }
  ]
}

// List item
{
  ops: [
    { insert: "Task item" },
    { insert: "\n", attributes: { list: "bullet" } }
  ]
}

// Aligned paragraph with indent
{
  ops: [
    { insert: "Indented centered text" },
    {
      insert: "\n",
      attributes: {
        align: "center",
        indent: 1
      }
    }
  ]
}
```

---

## Embedded Content

**Principle**: Non-text content should integrate seamlessly with text operations.

### Embeds as Objects

Embedded content uses object values instead of strings:

```javascript
// Text insert (string)
{ insert: "Hello" }

// Image embed (object)
{
  insert: {
    image: "https://example.com/photo.jpg"
  }
}

// Video embed (object)
{
  insert: {
    video: "https://youtube.com/embed/abc123"
  }
}
```

### Why Objects?

**Flexibility**: Objects can contain multiple attributes:

```javascript
// Image with metadata
{
  insert: {
    image: {
      url: "https://example.com/photo.jpg",
      width: 300,
      height: 200,
      alt: "Photo description"
    }
  }
}

// Custom embed
{
  insert: {
    mention: {
      id: 123,
      name: "John Doe",
      avatar: "https://example.com/avatar.jpg"
    }
  }
}
```

**Type safety**: Easy to distinguish embeds from text:

```javascript
delta.ops.forEach(op => {
  if (typeof op.insert === 'string') {
    console.log('Text:', op.insert);
  } else {
    console.log('Embed:', Object.keys(op.insert)[0]);
  }
});
```

### Embed Length

**Design decision**: Embeds have length of 1 character.

```javascript
// Document: "Hello [IMAGE] World"
// Length: 5 + 1 + 6 = 12

{
  ops: [
    { insert: "Hello " },        // length 6
    { insert: { image: "..." } }, // length 1
    { insert: " World\n" }        // length 7
  ]
}
// Total length: 14
```

**Why length 1?**:
- Simplifies index calculations
- Consistent with Unicode handling (emoji, special chars)
- Predictable cursor positioning

---

## Describing Changes

**Principle**: Changes should be describable using the same format as documents.

### Three Operation Types

**1. Insert**: Add content
```javascript
{ insert: "New text" }
```

**2. Delete**: Remove characters
```javascript
{ delete: 5 } // Remove 5 characters
```

**3. Retain**: Keep content, optionally modify attributes
```javascript
{ retain: 10 } // Keep 10 characters unchanged
{ retain: 5, attributes: { bold: true } } // Make 5 characters bold
```

### Change Examples

**Insert text at position 5**:
```javascript
{
  ops: [
    { retain: 5 },
    { insert: "new " }
  ]
}
```

**Delete characters 10-15**:
```javascript
{
  ops: [
    { retain: 10 },
    { delete: 5 }
  ]
}
```

**Make characters 5-10 bold**:
```javascript
{
  ops: [
    { retain: 5 },
    { retain: 5, attributes: { bold: true } }
  ]
}
```

---

## Retain Operation and Final Format

**Design choice**: Retain operations specify FINAL format, not delta changes.

### Why Final Format?

**Consider**: Making bold text italic

```javascript
// Document before
{ insert: "Text", attributes: { bold: true } }

// ✅ Retain with final format
{
  ops: [
    {
      retain: 4,
      attributes: {
        bold: true,  // Keep existing
        italic: true // Add new
      }
    }
  ]
}

// ❌ NOT just the change
{
  ops: [
    {
      retain: 4,
      attributes: { italic: true } // Ambiguous: keep bold?
    }
  ]
}
```

### Removing Attributes

Use `null` to remove attributes:

```javascript
// Remove bold, keep other attributes
{
  ops: [
    {
      retain: 4,
      attributes: { bold: null }
    }
  ]
}
```

### Benefits

**Explicitness**: No ambiguity about final state
```javascript
// Clear: text will be bold and italic, not underlined
{ retain: 4, attributes: { bold: true, italic: true, underline: null } }
```

**Simplified implementation**: No need to track current state
```javascript
// Applying retain is straightforward replacement
function applyRetain(text, retain) {
  return Object.assign({}, text.attributes, retain.attributes);
}
```

---

## Real-World Example

### Document Evolution

**Initial document**:
```javascript
{
  ops: [
    { insert: "Hello World\n" }
  ]
}
```

**Change 1**: Make "World" bold
```javascript
{
  ops: [
    { retain: 6 }, // Skip "Hello "
    { retain: 5, attributes: { bold: true } }, // Make "World" bold
    { retain: 1 } // Skip newline
  ]
}
```

**Result**:
```javascript
{
  ops: [
    { insert: "Hello " },
    { insert: "World", attributes: { bold: true } },
    { insert: "\n" }
  ]
}
```

**Change 2**: Insert "Beautiful " before "World"
```javascript
{
  ops: [
    { retain: 6 },
    { insert: "Beautiful " }
  ]
}
```

**Result**:
```javascript
{
  ops: [
    { insert: "Hello Beautiful " },
    { insert: "World", attributes: { bold: true } },
    { insert: "\n" }
  ]
}
```

**Change 3**: Make entire first line a heading
```javascript
{
  ops: [
    { retain: 23 }, // Skip all text
    { retain: 1, attributes: { header: 1 } } // Format newline
  ]
}
```

**Final result**:
```javascript
{
  ops: [
    { insert: "Hello Beautiful " },
    { insert: "World", attributes: { bold: true } },
    { insert: "\n", attributes: { header: 1 } }
  ]
}
```

---

## Advantages of Delta Design

### For Developers

1. **Easy to generate**: Simple JSON structure
2. **Easy to parse**: Iterate over array
3. **Easy to validate**: Check structure and types
4. **Easy to transform**: Map/filter/reduce operations
5. **Easy to debug**: Human-readable JSON

### For Applications

1. **Storage efficient**: Compact representation
2. **Network efficient**: Small payload size
3. **Comparison efficient**: Simple equality checks
4. **OT-compatible**: Supports operational transformation
5. **Version control friendly**: Diff-able JSON

### For Users

1. **Predictable editing**: Consistent behavior
2. **Fast performance**: Efficient operations
3. **Reliable collaboration**: OT support
4. **Cross-platform**: JSON works everywhere

---

## Related Files

- **Delta Format**: See `categories/delta.md` for Delta API reference
- **Content API**: See `categories/api-content.md` for working with Delta
- **Custom Formats**: See `guides/parchment-blots.md` for extending Delta

---

## Official Resources

- **Delta Design Guide**: https://quilljs.com/guides/designing-the-delta-format
- **Delta Specification**: https://github.com/quilljs/delta
- **Operational Transformation**: https://en.wikipedia.org/wiki/Operational_transformation
