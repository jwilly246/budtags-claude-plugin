# Syntax Module

## Overview

The Syntax module provides automatic syntax highlighting for code blocks in Quill. It uses highlight.js to detect and highlight programming languages.

**Official Documentation:** https://quilljs.com/docs/modules/syntax

## Requirements

**Requires highlight.js version 9.12.0 or higher.**

## Installation

### Via CDN

```html
<!-- Include highlight.js -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

<!-- Include Quill -->
<link href="https://cdn.jsdelivr.net/npm/quill@2/dist/quill.snow.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/quill@2/dist/quill.js"></script>

<script>
  const quill = new Quill('#editor', {
    modules: {
      syntax: true
    },
    theme: 'snow'
  });
</script>
```

### Via NPM

```bash
npm install highlight.js
```

```javascript
import Quill from 'quill';
import hljs from 'highlight.js';
import 'highlight.js/styles/monokai-sublime.css';

// Register highlight.js with Quill
window.hljs = hljs;

const quill = new Quill('#editor', {
  modules: {
    syntax: true,
    toolbar: [['code-block']]
  },
  theme: 'snow'
});
```

## Configuration

### Basic Setup

Enable syntax highlighting:

```javascript
const quill = new Quill('#editor', {
  modules: {
    syntax: true
  },
  theme: 'snow'
});
```

### With Toolbar

Add code-block button to toolbar:

```javascript
const quill = new Quill('#editor', {
  modules: {
    syntax: true,
    toolbar: [
      ['bold', 'italic'],
      ['code-block'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }]
    ]
  },
  theme: 'snow'
});
```

### Configuration Options

For highlight.js versions before 10.0.0, use `useBR` option:

```javascript
const quill = new Quill('#editor', {
  modules: {
    syntax: {
      hljs: window.hljs,
      useBR: false  // Required for highlight.js < 10.0.0
    }
  }
});
```

## Choosing a Theme

Highlight.js provides many themes for syntax highlighting:

```html
<!-- Available themes -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/monokai.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/vs2015.min.css">
```

**Popular themes:**
- `default` - Light, minimal
- `github` - GitHub-style
- `monokai-sublime` - Dark, colorful
- `atom-one-dark` - Atom editor style
- `vs2015` - Visual Studio style
- `nord` - Nord color scheme

**See all themes:** https://highlightjs.org/static/demo/

## Language Support

Highlight.js automatically detects languages. Common languages include:

- JavaScript / TypeScript
- Python
- Java
- C / C++ / C#
- PHP
- Ruby
- Go
- Rust
- SQL
- HTML / XML
- CSS / SCSS
- Bash / Shell
- JSON
- Markdown
- And 190+ more...

**Full list:** https://github.com/highlightjs/highlight.js/blob/main/SUPPORTED_LANGUAGES.md

### Custom Language Subset

Include only specific languages to reduce bundle size:

```javascript
import hljs from 'highlight.js/lib/core';
import javascript from 'highlight.js/lib/languages/javascript';
import python from 'highlight.js/lib/languages/python';
import xml from 'highlight.js/lib/languages/xml';

// Register specific languages
hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('python', python);
hljs.registerLanguage('html', xml);

window.hljs = hljs;

const quill = new Quill('#editor', {
  modules: {
    syntax: true
  }
});
```

## Complete Examples

### Basic Setup with Toolbar

```html
<!DOCTYPE html>
<html>
<head>
  <link href="https://cdn.jsdelivr.net/npm/quill@2/dist/quill.snow.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
</head>
<body>
  <div id="toolbar">
    <button class="ql-bold">Bold</button>
    <button class="ql-code-block">Code Block</button>
  </div>
  <div id="editor"></div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/quill@2/dist/quill.js"></script>

  <script>
    const quill = new Quill('#editor', {
      modules: {
        syntax: true,
        toolbar: '#toolbar'
      },
      theme: 'snow'
    });
  </script>
</body>
</html>
```

### NPM with Custom Languages

```javascript
import Quill from 'quill';
import hljs from 'highlight.js/lib/core';

// Import only needed languages
import javascript from 'highlight.js/lib/languages/javascript';
import typescript from 'highlight.js/lib/languages/typescript';
import python from 'highlight.js/lib/languages/python';
import java from 'highlight.js/lib/languages/java';
import xml from 'highlight.js/lib/languages/xml';
import css from 'highlight.js/lib/languages/css';
import json from 'highlight.js/lib/languages/json';

// Import theme
import 'highlight.js/styles/github.css';
import 'quill/dist/quill.snow.css';

// Register languages
hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('typescript', typescript);
hljs.registerLanguage('python', python);
hljs.registerLanguage('java', java);
hljs.registerLanguage('html', xml);
hljs.registerLanguage('xml', xml);
hljs.registerLanguage('css', css);
hljs.registerLanguage('json', json);

// Make available globally
window.hljs = hljs;

// Initialize Quill
const quill = new Quill('#editor', {
  modules: {
    syntax: true,
    toolbar: [
      ['bold', 'italic', 'underline'],
      ['code-block'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }]
    ]
  },
  theme: 'snow'
});
```

### Programmatic Code Block

Insert code blocks programmatically:

```javascript
const quill = new Quill('#editor', {
  modules: {
    syntax: true
  },
  theme: 'snow'
});

// Insert code block
const code = `function hello() {
  console.log("Hello, World!");
}`;

const range = quill.getSelection(true);
quill.insertText(range.index, code);
quill.formatLine(range.index, code.length, 'code-block', true);

// Or use setContents
quill.setContents([
  { insert: 'Some text\n' },
  { insert: 'const x = 42;\n', attributes: { 'code-block': true } },
  { insert: 'console.log(x);\n', attributes: { 'code-block': true } }
]);
```

### Custom Styling

Override code block styles:

```css
/* Custom code block appearance */
.ql-editor pre.ql-syntax {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.5;
}

/* Custom scrollbar for code blocks */
.ql-editor pre.ql-syntax::-webkit-scrollbar {
  height: 8px;
}

.ql-editor pre.ql-syntax::-webkit-scrollbar-track {
  background: #2d2d2d;
}

.ql-editor pre.ql-syntax::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 4px;
}

.ql-editor pre.ql-syntax::-webkit-scrollbar-thumb:hover {
  background: #777;
}
```

### Dynamic Theme Switching

Switch highlight.js themes dynamically:

```javascript
const themes = {
  light: 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css',
  dark: 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css'
};

function setHighlightTheme(theme) {
  const link = document.getElementById('highlight-theme');
  link.href = themes[theme];

  // Re-highlight all code blocks
  document.querySelectorAll('pre.ql-syntax').forEach(block => {
    hljs.highlightElement(block);
  });
}

// Usage
setHighlightTheme('dark');
```

### Language Detection Override

Force specific language for code block:

```javascript
// Note: Quill doesn't natively support language specification
// This is a workaround using custom attributes

const quill = new Quill('#editor', {
  modules: {
    syntax: true
  }
});

// Insert code with language hint in data attribute
const range = quill.getSelection(true);
quill.insertText(range.index, 'const x = 42;');
quill.formatLine(range.index, 1, 'code-block', true);

// Manually add language class (after Quill renders)
setTimeout(() => {
  const blocks = document.querySelectorAll('pre.ql-syntax');
  blocks[blocks.length - 1].classList.add('language-javascript');
  hljs.highlightElement(blocks[blocks.length - 1]);
}, 0);
```

## TypeScript Support

```typescript
import Quill from 'quill';
import hljs from 'highlight.js';

// Make hljs available globally
declare global {
  interface Window {
    hljs: typeof hljs;
  }
}

window.hljs = hljs;

interface SyntaxOptions {
  hljs?: typeof hljs;
  useBR?: boolean;
}

const quill = new Quill('#editor', {
  modules: {
    syntax: {
      hljs: window.hljs,
      useBR: false
    } as SyntaxOptions,
    toolbar: [['code-block']]
  },
  theme: 'snow'
});
```

## Common Issues

### Highlight.js Not Found

```javascript
// ❌ WRONG - hljs not defined
const quill = new Quill('#editor', {
  modules: { syntax: true }
});
// Error: hljs is not defined

// ✅ CORRECT - Include highlight.js first
<script src="highlight.min.js"></script>
<script src="quill.js"></script>
<script>
  const quill = new Quill('#editor', {
    modules: { syntax: true }
  });
</script>
```

### Old highlight.js Version

```javascript
// For highlight.js < 10.0.0, use useBR option
const quill = new Quill('#editor', {
  modules: {
    syntax: {
      useBR: false
    }
  }
});
```

### Code Not Highlighting

```javascript
// Ensure code-block format is applied
quill.formatLine(index, length, 'code-block', true);

// Or check if syntax module is loaded
const syntax = quill.getModule('syntax');
console.log(syntax);  // Should not be undefined
```

## Performance Considerations

- Large code blocks can slow down highlighting
- Consider lazy-loading highlight.js for better initial load
- Use custom language subset to reduce bundle size
- Debounce re-highlighting during rapid edits

## Related Files

- **configuration.md** - Module configuration
- **formats.md** - code-block format
- **toolbar-module.md** - Adding code-block button to toolbar
- **themes.md** - Quill theme styling

## External Resources

- **Highlight.js Documentation:** https://highlightjs.org/
- **Highlight.js Demo:** https://highlightjs.org/static/demo/
- **Supported Languages:** https://github.com/highlightjs/highlight.js/blob/main/SUPPORTED_LANGUAGES.md
- **Highlight.js CDN:** https://cdnjs.com/libraries/highlight.js

## Notes

- Syntax module is not enabled by default - must be configured
- Requires highlight.js library to be loaded
- Code blocks preserve formatting and whitespace
- Use `code-block` format for multi-line code, `code` format for inline code
- Syntax highlighting updates automatically as user types
