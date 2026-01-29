# Cloning Medium with Parchment

Guide to creating custom formats using Parchment Blots, demonstrated by rebuilding Medium.com's editor.

---

## Overview

Parchment is Quill's document model that defines how content is represented in the DOM. This guide builds custom formats (Blots) to recreate Medium's editor features, from basic formatting to complex embeds.

**Official Documentation**: https://quilljs.com/guides/cloning-medium-with-parchment

---

## Parchment Concepts

### What are Blots?

Blots are the building blocks of Quill's document model. Each Blot represents a piece of content:

- **Text Blot**: Plain text characters
- **Inline Blot**: Inline formatting (bold, italic, links)
- **Block Blot**: Block-level elements (paragraphs, headings)
- **Embed Blot**: Non-text content (images, videos, dividers)

### Tree Structure

Quill represents documents as a tree of Blots:

```
Scroll (root)
├── Block (paragraph)
│   ├── Inline (bold)
│   │   └── Text ("Hello")
│   └── Text (" World")
├── Block (heading)
│   └── Text ("Title")
└── BlockEmbed (image)
```

### Blot Types

| Type | Purpose | Examples |
|------|---------|----------|
| **Inline** | Inline formatting | Bold, italic, links |
| **Block** | Block containers | Paragraphs, headings, blockquotes |
| **Embed** | Inline non-text | Images (inline) |
| **BlockEmbed** | Block-level non-text | Video, divider, tweet |

---

## Required Methods

All custom Blots must implement these methods:

### `create(value)`

Create the DOM node for this Blot:

```javascript
static create(value) {
  const node = super.create();
  // Configure node based on value
  return node;
}
```

### `formats(node)`

Extract format value from DOM node:

```javascript
static formats(node) {
  return node.getAttribute('data-value');
}
```

### `value()`

Return the Blot's value (for embedding in Delta):

```javascript
value() {
  return this.domNode.getAttribute('data-value');
}
```

### `format(name, value)`

Apply or remove a format:

```javascript
format(name, value) {
  if (name === 'bold' && value) {
    this.domNode.style.fontWeight = 'bold';
  }
}
```

---

## Basic Formatting: Bold & Italic

### Implementation

```javascript
import Quill from 'quill';
const Inline = Quill.import('blots/inline');

class BoldBlot extends Inline {
  static blotName = 'bold';
  static tagName = 'strong';
}

class ItalicBlot extends Inline {
  static blotName = 'italic';
  static tagName = 'em';
}

// Register formats
Quill.register(BoldBlot);
Quill.register(ItalicBlot);
```

### Usage

```javascript
const quill = new Quill('#editor');

// Apply formatting
quill.format('bold', true);
quill.format('italic', true);

// Delta representation
// { insert: "text", attributes: { bold: true, italic: true } }
```

### How It Works

1. **blotName**: Format name used in Delta and API calls
2. **tagName**: HTML tag to render (`<strong>`, `<em>`)
3. **Inline class**: Handles inline formatting automatically

**Result HTML**:
```html
<p>
  <strong><em>Bold and italic text</em></strong>
</p>
```

---

## Links: Value-Based Formats

Links require storing a URL value, not just true/false.

### Implementation

```javascript
import Quill from 'quill';
const Inline = Quill.import('blots/inline');

class LinkBlot extends Inline {
  static blotName = 'link';
  static tagName = 'a';

  static create(url) {
    const node = super.create();
    // Set href attribute
    node.setAttribute('href', url);
    // Security: prevent JavaScript URLs
    node.setAttribute('rel', 'noopener noreferrer');
    node.setAttribute('target', '_blank');
    return node;
  }

  static formats(node) {
    // Extract URL from href attribute
    return node.getAttribute('href');
  }
}

Quill.register(LinkBlot);
```

### Usage

```javascript
// Apply link format with URL value
quill.format('link', 'https://example.com');

// Delta representation
// { insert: "Click here", attributes: { link: "https://example.com" } }

// Remove link
quill.format('link', false);
```

**Result HTML**:
```html
<p>
  <a href="https://example.com" rel="noopener noreferrer" target="_blank">
    Click here
  </a>
</p>
```

---

## Block-Level Formats

### Blockquote

```javascript
import Quill from 'quill';
const Block = Quill.import('blots/block');

class BlockquoteBlot extends Block {
  static blotName = 'blockquote';
  static tagName = 'blockquote';
}

Quill.register(BlockquoteBlot);
```

### Headers

```javascript
import Quill from 'quill';
const Block = Quill.import('blots/block');

class HeaderBlot extends Block {
  static blotName = 'header';
  static tagName = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'];

  static create(value) {
    // value is 1-6 for h1-h6
    const tagName = this.tagName[value - 1] || this.tagName[0];
    return super.create(tagName);
  }

  static formats(node) {
    // Return header level (1-6)
    return this.tagName.indexOf(node.tagName.toLowerCase()) + 1;
  }
}

Quill.register(HeaderBlot);
```

### Usage

```javascript
// Apply header format
quill.format('header', 1); // H1
quill.format('header', 2); // H2

// Apply blockquote
quill.format('blockquote', true);

// Delta representation
// { insert: "Heading\n", attributes: { header: 1 } }
// { insert: "Quote\n", attributes: { blockquote: true } }
```

**Result HTML**:
```html
<h1>Heading</h1>
<blockquote>Quote</blockquote>
```

---

## Dividers: First Embed Type

Dividers are block-level non-text content.

### Implementation

```javascript
import Quill from 'quill';
const BlockEmbed = Quill.import('blots/block/embed');

class DividerBlot extends BlockEmbed {
  static blotName = 'divider';
  static tagName = 'hr';
}

Quill.register(DividerBlot);
```

### Usage

```javascript
// Insert divider at current position
const range = quill.getSelection();
quill.insertEmbed(range.index, 'divider', true);

// Delta representation
// { insert: { divider: true } }
```

**Result HTML**:
```html
<p>Text before</p>
<hr>
<p>Text after</p>
```

### Key Differences from Inline

- **BlockEmbed**: Creates block-level element
- **No text content**: Divider has length of 1 in Delta
- **Self-closing**: No child Blots

---

## Images: Object Values

Images need multiple attributes (URL, alt text, dimensions).

### Implementation

```javascript
import Quill from 'quill';
const BlockEmbed = Quill.import('blots/block/embed');

class ImageBlot extends BlockEmbed {
  static blotName = 'image';
  static tagName = 'img';

  static create(value) {
    const node = super.create();

    if (typeof value === 'string') {
      // Simple string URL
      node.setAttribute('src', value);
    } else {
      // Object with multiple attributes
      node.setAttribute('src', value.url);
      if (value.alt) {
        node.setAttribute('alt', value.alt);
      }
      if (value.width) {
        node.setAttribute('width', value.width);
      }
      if (value.height) {
        node.setAttribute('height', value.height);
      }
    }

    return node;
  }

  static formats(node) {
    return {
      url: node.getAttribute('src'),
      alt: node.getAttribute('alt'),
      width: node.getAttribute('width'),
      height: node.getAttribute('height')
    };
  }

  static value(node) {
    return {
      url: node.getAttribute('src'),
      alt: node.getAttribute('alt'),
      width: node.getAttribute('width'),
      height: node.getAttribute('height')
    };
  }
}

Quill.register(ImageBlot);
```

### Usage

```javascript
// Simple image insert
quill.insertEmbed(index, 'image', 'https://example.com/image.jpg');

// Image with metadata
quill.insertEmbed(index, 'image', {
  url: 'https://example.com/image.jpg',
  alt: 'Description',
  width: 300,
  height: 200
});

// Delta representation
// {
//   insert: {
//     image: {
//       url: "https://example.com/image.jpg",
//       alt: "Description",
//       width: 300,
//       height: 200
//     }
//   }
// }
```

**Result HTML**:
```html
<img
  src="https://example.com/image.jpg"
  alt="Description"
  width="300"
  height="200"
/>
```

---

## Videos: Iframe Embeds

Video embeds use iframes for YouTube, Vimeo, etc.

### Implementation

```javascript
import Quill from 'quill';
const BlockEmbed = Quill.import('blots/block/embed');

class VideoBlot extends BlockEmbed {
  static blotName = 'video';
  static tagName = 'iframe';

  static create(url) {
    const node = super.create();

    node.setAttribute('src', url);
    node.setAttribute('frameborder', '0');
    node.setAttribute('allowfullscreen', true);
    node.setAttribute('width', '560');
    node.setAttribute('height', '315');

    return node;
  }

  static formats(node) {
    return node.getAttribute('src');
  }

  static value(node) {
    return node.getAttribute('src');
  }
}

Quill.register(VideoBlot);
```

### Usage

```javascript
// Insert YouTube video
quill.insertEmbed(
  index,
  'video',
  'https://www.youtube.com/embed/dQw4w9WgXcQ'
);

// Delta representation
// { insert: { video: "https://www.youtube.com/embed/dQw4w9WgXcQ" } }
```

**Result HTML**:
```html
<iframe
  src="https://www.youtube.com/embed/dQw4w9WgXcQ"
  frameborder="0"
  allowfullscreen
  width="560"
  height="315"
></iframe>
```

---

## Tweets: Non-Void Nodes

Tweets are complex embeds with child content and third-party integration.

### Implementation

```javascript
import Quill from 'quill';
const BlockEmbed = Quill.import('blots/block/embed');

class TweetBlot extends BlockEmbed {
  static blotName = 'tweet';
  static tagName = 'div';
  static className = 'tweet-embed';

  static create(tweetId) {
    const node = super.create();
    node.setAttribute('data-tweet-id', tweetId);

    // Create placeholder
    node.innerHTML = `
      <div class="tweet-loading">
        Loading tweet ${tweetId}...
      </div>
    `;

    // Load Twitter widget
    if (window.twttr) {
      window.twttr.widgets.createTweet(
        tweetId,
        node,
        { theme: 'light' }
      );
    }

    return node;
  }

  static formats(node) {
    return node.getAttribute('data-tweet-id');
  }

  static value(node) {
    return node.getAttribute('data-tweet-id');
  }
}

Quill.register(TweetBlot);
```

### Required: Twitter Widget Script

```html
<!-- Include Twitter widget script -->
<script async src="https://platform.twitter.com/widgets.js"></script>
```

### Usage

```javascript
// Insert tweet by ID
quill.insertEmbed(index, 'tweet', '1234567890123456789');

// Delta representation
// { insert: { tweet: "1234567890123456789" } }
```

**Result HTML** (after Twitter widget loads):
```html
<div class="tweet-embed" data-tweet-id="1234567890123456789">
  <blockquote class="twitter-tweet">
    <!-- Twitter widget renders here -->
  </blockquote>
</div>
```

### Non-Void Node Features

- **Child content**: Contains Twitter widget markup
- **Async loading**: Integrates with third-party library
- **Placeholder**: Shows loading state
- **Data attributes**: Stores tweet ID for re-rendering

---

## Complete Example: Medium Clone

Combining all formats to create Medium-like editor:

```html
<!DOCTYPE html>
<html>
<head>
  <link href="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css" rel="stylesheet" />
  <style>
    .ql-editor {
      font-family: 'Georgia', serif;
      font-size: 18px;
      line-height: 1.6;
    }

    .ql-editor h1 {
      font-size: 42px;
      font-weight: 700;
      margin: 20px 0;
    }

    .ql-editor h2 {
      font-size: 32px;
      font-weight: 700;
      margin: 16px 0;
    }

    .ql-editor blockquote {
      border-left: 3px solid #ccc;
      padding-left: 20px;
      margin-left: 0;
      font-style: italic;
      color: #666;
    }

    .ql-editor img {
      max-width: 100%;
      display: block;
      margin: 20px auto;
    }

    .ql-editor hr {
      border: none;
      border-top: 3px solid #333;
      margin: 40px 0;
      width: 100px;
      margin-left: auto;
      margin-right: auto;
    }

    .ql-editor iframe {
      display: block;
      margin: 20px auto;
    }
  </style>
</head>
<body>
  <div id="editor">
    <h1>Building a Medium Clone</h1>
    <p>This editor recreates Medium's formatting using custom Parchment Blots.</p>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.js"></script>
  <script>
    // Import Parchment classes
    const Inline = Quill.import('blots/inline');
    const Block = Quill.import('blots/block');
    const BlockEmbed = Quill.import('blots/block/embed');

    // Bold
    class BoldBlot extends Inline {
      static blotName = 'bold';
      static tagName = 'strong';
    }

    // Italic
    class ItalicBlot extends Inline {
      static blotName = 'italic';
      static tagName = 'em';
    }

    // Link
    class LinkBlot extends Inline {
      static blotName = 'link';
      static tagName = 'a';

      static create(url) {
        const node = super.create();
        node.setAttribute('href', url);
        node.setAttribute('target', '_blank');
        return node;
      }

      static formats(node) {
        return node.getAttribute('href');
      }
    }

    // Blockquote
    class BlockquoteBlot extends Block {
      static blotName = 'blockquote';
      static tagName = 'blockquote';
    }

    // Header
    class HeaderBlot extends Block {
      static blotName = 'header';
      static tagName = ['h1', 'h2'];

      static create(value) {
        return super.create(this.tagName[value - 1]);
      }

      static formats(node) {
        return this.tagName.indexOf(node.tagName.toLowerCase()) + 1;
      }
    }

    // Divider
    class DividerBlot extends BlockEmbed {
      static blotName = 'divider';
      static tagName = 'hr';
    }

    // Image
    class ImageBlot extends BlockEmbed {
      static blotName = 'image';
      static tagName = 'img';

      static create(value) {
        const node = super.create();
        node.setAttribute('src', typeof value === 'string' ? value : value.url);
        return node;
      }

      static value(node) {
        return node.getAttribute('src');
      }
    }

    // Register all formats
    Quill.register(BoldBlot);
    Quill.register(ItalicBlot);
    Quill.register(LinkBlot);
    Quill.register(BlockquoteBlot);
    Quill.register(HeaderBlot);
    Quill.register(DividerBlot);
    Quill.register(ImageBlot);

    // Create editor
    const quill = new Quill('#editor', {
      theme: 'snow',
      modules: {
        toolbar: [
          [{ 'header': [1, 2, false] }],
          ['bold', 'italic', 'link'],
          ['blockquote', 'divider'],
          ['image']
        ]
      }
    });

    // Add divider button handler
    const toolbar = quill.getModule('toolbar');
    toolbar.addHandler('divider', function() {
      const range = quill.getSelection();
      quill.insertEmbed(range.index, 'divider', true);
    });
  </script>
</body>
</html>
```

---

## Advanced Topics

### Formatting Child Blots

Some Blots allow formatting child content:

```javascript
class CustomBlock extends Block {
  format(name, value) {
    // Allow bold/italic within this block
    if (['bold', 'italic'].includes(name)) {
      super.format(name, value);
    }
  }
}
```

### Optimizing Performance

```javascript
class OptimizedBlot extends Inline {
  static create(value) {
    const node = super.create();
    // Cache expensive operations
    node._cachedValue = value;
    return node;
  }

  optimize(context) {
    super.optimize(context);
    // Custom optimization logic
  }
}
```

### Handling Edge Cases

```javascript
class SafeImageBlot extends BlockEmbed {
  static create(value) {
    const node = super.create();

    // Validate URL
    try {
      const url = new URL(value);
      if (url.protocol === 'http:' || url.protocol === 'https:') {
        node.setAttribute('src', value);
      }
    } catch (e) {
      console.error('Invalid image URL:', value);
    }

    return node;
  }
}
```

---

## Debugging Blots

### Check Registration

```javascript
const Bold = Quill.import('formats/bold');
console.log('Bold registered:', Bold !== null);
```

### Inspect Blot Tree

```javascript
const scroll = quill.scroll;
scroll.descendants(ImageBlot).forEach(image => {
  console.log('Image src:', image.value());
});
```

### Debug Delta Conversion

```javascript
const delta = quill.getContents();
console.log('Delta:', JSON.stringify(delta, null, 2));

// Verify Blots match Delta
delta.ops.forEach(op => {
  if (op.insert.image) {
    console.log('Image in delta:', op.insert.image);
  }
});
```

---

## Related Files

- **Formats**: See `categories/formats.md` for built-in formats
- **Registries**: See `patterns/registries.md` for custom format sets
- **Upgrading**: See `patterns/upgrading.md` for Parchment v2.0 changes

---

## Official Resources

- **Parchment Guide**: https://quilljs.com/guides/cloning-medium-with-parchment
- **Parchment Library**: https://github.com/quilljs/parchment
- **Blot Examples**: https://github.com/quilljs/quill/tree/main/blots
