# Toolbar Module

## Overview

The Toolbar module provides UI controls for formatting content. It can be configured with an array of formats or bound to an existing HTML container.

**Official Documentation:** https://quilljs.com/docs/modules/toolbar

## Configuration Methods

### Array Configuration

Define toolbar controls as an array:

```javascript
const quill = new Quill('#editor', {
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline', 'strike'],
      ['blockquote', 'code-block'],
      [{ 'header': 1 }, { 'header': 2 }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'script': 'sub'}, { 'script': 'super' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],
      [{ 'direction': 'rtl' }],
      [{ 'size': ['small', false, 'large', 'huge'] }],
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'font': [] }],
      [{ 'align': [] }],
      ['clean']
    ]
  },
  theme: 'snow'
});
```

### Container Configuration

Bind to existing HTML element:

```javascript
const quill = new Quill('#editor', {
  modules: {
    toolbar: '#toolbar-container'
  },
  theme: 'snow'
});
```

```html
<div id="toolbar-container">
  <span class="ql-formats">
    <select class="ql-font"></select>
    <select class="ql-size"></select>
  </span>
  <span class="ql-formats">
    <button class="ql-bold"></button>
    <button class="ql-italic"></button>
    <button class="ql-underline"></button>
    <button class="ql-strike"></button>
  </span>
  <span class="ql-formats">
    <select class="ql-color"></select>
    <select class="ql-background"></select>
  </span>
  <span class="ql-formats">
    <button class="ql-script" value="sub"></button>
    <button class="ql-script" value="super"></button>
  </span>
  <span class="ql-formats">
    <button class="ql-header" value="1"></button>
    <button class="ql-header" value="2"></button>
    <button class="ql-blockquote"></button>
    <button class="ql-code-block"></button>
  </span>
  <span class="ql-formats">
    <button class="ql-list" value="ordered"></button>
    <button class="ql-list" value="bullet"></button>
    <button class="ql-indent" value="-1"></button>
    <button class="ql-indent" value="+1"></button>
  </span>
  <span class="ql-formats">
    <button class="ql-direction" value="rtl"></button>
    <select class="ql-align"></select>
  </span>
  <span class="ql-formats">
    <button class="ql-link"></button>
    <button class="ql-image"></button>
    <button class="ql-video"></button>
  </span>
  <span class="ql-formats">
    <button class="ql-clean"></button>
  </span>
</div>
```

## Container Options

### Grouped Controls

Use `<span class="ql-formats">` to group related controls:

```html
<div id="toolbar">
  <span class="ql-formats">
    <button class="ql-bold"></button>
    <button class="ql-italic"></button>
  </span>
  <span class="ql-formats">
    <button class="ql-list" value="ordered"></button>
    <button class="ql-list" value="bullet"></button>
  </span>
</div>
```

### Custom Values

Provide specific values for dropdown controls:

```html
<!-- Default values (all options) -->
<select class="ql-size"></select>

<!-- Custom values -->
<select class="ql-size">
  <option value="small">Small</option>
  <option selected>Normal</option>
  <option value="large">Large</option>
  <option value="huge">Huge</option>
</select>

<!-- Custom font options -->
<select class="ql-font">
  <option selected>Sans Serif</option>
  <option value="serif">Serif</option>
  <option value="monospace">Monospace</option>
</select>

<!-- Custom header options -->
<select class="ql-header">
  <option value="1">Heading 1</option>
  <option value="2">Heading 2</option>
  <option value="3">Heading 3</option>
  <option selected>Normal</option>
</select>
```

### Color Pickers

Empty `ql-color` and `ql-background` show default color picker:

```html
<!-- Default color picker -->
<select class="ql-color"></select>
<select class="ql-background"></select>

<!-- Custom color options -->
<select class="ql-color">
  <option value="#ff0000">Red</option>
  <option value="#00ff00">Green</option>
  <option value="#0000ff">Blue</option>
</select>
```

## Custom Handlers

Replace default toolbar button behavior:

```javascript
const quill = new Quill('#editor', {
  modules: {
    toolbar: {
      container: [
        ['bold', 'italic'],
        ['link', 'image']
      ],
      handlers: {
        // Custom image handler
        image: imageHandler,
        // Custom link handler
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

function imageHandler() {
  const input = document.createElement('input');
  input.setAttribute('type', 'file');
  input.setAttribute('accept', 'image/*');
  input.click();

  input.onchange = async () => {
    const file = input.files[0];
    const formData = new FormData();
    formData.append('image', file);

    // Upload to server
    const response = await fetch('/upload-image', {
      method: 'POST',
      body: formData
    });
    const data = await response.json();

    // Insert image into editor
    const range = this.quill.getSelection(true);
    this.quill.insertEmbed(range.index, 'image', data.url);
    this.quill.setSelection(range.index + 1);
  };
}
```

### Handler Context

Handler functions are bound to the toolbar instance:

```javascript
handlers: {
  customButton: function(value) {
    // 'this' is the toolbar instance
    console.log(this.quill);        // Access Quill instance
    console.log(this.container);    // Access toolbar container

    const range = this.quill.getSelection();
    if (range) {
      this.quill.insertText(range.index, 'Custom text');
    }
  }
}
```

## Adding Handlers Post-Initialization

Use `addHandler` to add handlers after toolbar is created:

```javascript
const quill = new Quill('#editor', {
  modules: {
    toolbar: [['bold', 'italic'], ['customButton']]
  }
});

// Add handler later
const toolbar = quill.getModule('toolbar');
toolbar.addHandler('customButton', function() {
  console.log('Custom button clicked!');
});
```

## Complete Examples

### Minimal Toolbar

```javascript
const quill = new Quill('#editor', {
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      ['clean']
    ]
  },
  theme: 'snow'
});
```

### Full Featured Toolbar

```javascript
const quill = new Quill('#editor', {
  modules: {
    toolbar: {
      container: [
        [{ 'font': [] }, { 'size': ['small', false, 'large', 'huge'] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ 'color': [] }, { 'background': [] }],
        [{ 'script': 'sub'}, { 'script': 'super' }],
        [{ 'header': 1 }, { 'header': 2 }, 'blockquote', 'code-block'],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }, { 'indent': '-1'}, { 'indent': '+1' }],
        [{ 'direction': 'rtl' }, { 'align': [] }],
        ['link', 'image', 'video', 'formula'],
        ['clean']
      ],
      handlers: {
        image: imageHandler
      }
    }
  },
  theme: 'snow'
});

function imageHandler() {
  const url = prompt('Enter image URL:');
  if (url) {
    const range = this.quill.getSelection();
    this.quill.insertEmbed(range.index, 'image', url);
  }
}
```

### Custom Upload Handler

```javascript
const quill = new Quill('#editor', {
  modules: {
    toolbar: {
      container: [['image', 'video']],
      handlers: {
        image: async function() {
          const input = document.createElement('input');
          input.setAttribute('type', 'file');
          input.setAttribute('accept', 'image/*');
          input.click();

          input.onchange = async () => {
            const file = input.files[0];

            // Show loading state
            const range = this.quill.getSelection(true);
            this.quill.insertText(range.index, 'Uploading...');
            this.quill.setSelection(range.index + 13);

            try {
              // Upload file
              const formData = new FormData();
              formData.append('file', file);

              const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
              });
              const data = await response.json();

              // Remove loading text
              this.quill.deleteText(range.index, 13);

              // Insert image
              this.quill.insertEmbed(range.index, 'image', data.url);
              this.quill.setSelection(range.index + 1);
            } catch (error) {
              // Remove loading text
              this.quill.deleteText(range.index, 13);
              alert('Upload failed: ' + error.message);
            }
          };
        }
      }
    }
  },
  theme: 'snow'
});
```

## TypeScript Support

```typescript
import Quill from 'quill';

interface ToolbarHandler {
  (this: any, value: any): void;
}

interface ToolbarConfig {
  container: string | any[];
  handlers?: Record<string, ToolbarHandler>;
}

const quill = new Quill('#editor', {
  modules: {
    toolbar: {
      container: [
        ['bold', 'italic'],
        ['link', 'image']
      ],
      handlers: {
        image: function(this: any) {
          const range = this.quill.getSelection(true);
          const url = prompt('Enter image URL');
          if (url) {
            this.quill.insertEmbed(range.index, 'image', url);
          }
        }
      }
    } as ToolbarConfig
  }
});
```

## Related Files

- **configuration.md** - Module configuration overview
- **formats.md** - Available format types for toolbar controls
- **themes.md** - Toolbar styling with themes
- **api-formatting.md** - Format methods called by toolbar

## Notes

- Toolbar automatically updates to reflect current selection formatting
- Custom handlers receive `value` parameter (true/false for buttons, selected value for dropdowns)
- Use `clean` button to remove all formatting from selection
- Container selector must point to valid DOM element before Quill initialization
