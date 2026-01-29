# Keyboard Module

## Overview

The Keyboard module handles keyboard bindings and shortcuts in Quill. It provides a powerful system for defining custom keyboard behaviors with context-aware handlers.

**Official Documentation:** https://quilljs.com/docs/modules/keyboard

## Configuration

```javascript
const quill = new Quill('#editor', {
  modules: {
    keyboard: {
      bindings: {
        // Custom binding name
        customBold: {
          key: 'B',
          shiftKey: true,
          handler: function(range, context) {
            this.quill.format('bold', true);
          }
        }
      }
    }
  }
});
```

## Key Bindings

### String Shorthands

Use string values for common keys:

```javascript
bindings: {
  // Letter keys
  tab: {
    key: 'Tab',
    handler: function() {
      // Tab pressed
    }
  },

  // Special keys
  enter: {
    key: 'Enter',
    handler: function() {
      // Enter pressed
    }
  },

  // Number keys
  numberOne: {
    key: '1',
    handler: function() {
      // 1 pressed
    }
  }
}
```

### Numeric Key Codes

Use key codes for special keys:

```javascript
bindings: {
  escape: {
    key: 27,  // Escape key
    handler: function() {
      console.log('Escape pressed');
    }
  }
}
```

### Modifier Keys

Combine keys with modifiers:

```javascript
bindings: {
  // Ctrl+B (Cmd+B on Mac with shortKey)
  bold: {
    key: 'B',
    shortKey: true,
    handler: function(range, context) {
      this.quill.format('bold', true);
    }
  },

  // Shift+Enter
  softBreak: {
    key: 'Enter',
    shiftKey: true,
    handler: function(range, context) {
      this.quill.insertText(range.index, '\n');
      this.quill.setSelection(range.index + 1);
      return false;  // Prevent default
    }
  },

  // Ctrl+Shift+S
  saveWithShift: {
    key: 'S',
    ctrlKey: true,
    shiftKey: true,
    handler: function() {
      console.log('Ctrl+Shift+S pressed');
    }
  },

  // Alt+A
  altA: {
    key: 'A',
    altKey: true,
    handler: function() {
      console.log('Alt+A pressed');
    }
  }
}
```

Available modifier properties:
- `shortKey` - Platform-aware (Cmd on Mac, Ctrl on Windows/Linux)
- `ctrlKey` - Ctrl key
- `metaKey` - Cmd key (Mac) or Windows key
- `shiftKey` - Shift key
- `altKey` - Alt key

## Platform-Aware `shortKey`

Use `shortKey` for cross-platform shortcuts:

```javascript
bindings: {
  bold: {
    key: 'B',
    shortKey: true,  // Cmd+B on Mac, Ctrl+B on Windows
    handler: function(range, context) {
      this.quill.format('bold', !context.format.bold);
    }
  },

  save: {
    key: 'S',
    shortKey: true,  // Cmd+S on Mac, Ctrl+S on Windows
    handler: function() {
      this.saveContent();
      return false;  // Prevent browser save dialog
    }
  }
}
```

## Context Specifications

Bindings can be context-aware using these properties:

### Collapsed Selection

Execute only when selection is collapsed (cursor, not range):

```javascript
bindings: {
  customEnter: {
    key: 'Enter',
    collapsed: true,  // Only when cursor (no selection)
    handler: function(range, context) {
      console.log('Enter with cursor only');
    }
  }
}
```

### Empty Line

Execute only when current line is empty:

```javascript
bindings: {
  emptyEnter: {
    key: 'Enter',
    empty: true,  // Only on empty lines
    handler: function(range, context) {
      console.log('Enter on empty line');
    }
  }
}
```

### Format Context

Execute only when specific format is active:

```javascript
bindings: {
  // Only when text is bold
  boldEnter: {
    key: 'Enter',
    format: ['bold'],
    handler: function(range, context) {
      console.log('Enter while bold');
    }
  },

  // Only when in code-block
  codeEnter: {
    key: 'Enter',
    format: { 'code-block': true },
    handler: function(range, context) {
      // Custom behavior for code blocks
    }
  },

  // Only when NOT in list
  noListEnter: {
    key: 'Enter',
    format: { 'list': false },
    handler: function(range, context) {
      console.log('Enter outside of list');
    }
  }
}
```

### Offset Position

Execute only at specific offset in line:

```javascript
bindings: {
  // Only at start of line
  startEnter: {
    key: 'Enter',
    offset: 0,
    handler: function(range, context) {
      console.log('Enter at line start');
    }
  }
}
```

### Prefix/Suffix Regex

Execute only when text before/after cursor matches pattern:

```javascript
bindings: {
  // Auto-complete markdown heading
  mdHeading: {
    key: ' ',
    collapsed: true,
    prefix: /^#{1,6}$/,  // Match 1-6 # symbols
    handler: function(range, context) {
      const level = context.prefix.length;
      this.quill.deleteText(range.index - level, level);
      this.quill.formatLine(range.index, 1, 'header', level);
      this.quill.setSelection(range.index);
      return false;
    }
  },

  // Auto-complete markdown list
  mdList: {
    key: ' ',
    collapsed: true,
    prefix: /^[-*]\s?$/,
    handler: function(range, context) {
      this.quill.deleteText(range.index - context.prefix.length, context.prefix.length);
      this.quill.formatLine(range.index, 1, 'list', 'bullet');
      return false;
    }
  },

  // Match @mentions
  mention: {
    key: ' ',
    collapsed: true,
    prefix: /@[\w]+$/,
    handler: function(range, context) {
      const mention = context.prefix.slice(1);  // Remove @
      console.log('Mention:', mention);
      // Show mention autocomplete
    }
  }
}
```

### Combining Context

Multiple context conditions can be combined:

```javascript
bindings: {
  complexBinding: {
    key: 'Enter',
    collapsed: true,      // Cursor only
    empty: true,          // Empty line
    format: ['list'],     // Inside list
    handler: function(range, context) {
      // Remove list formatting on double-enter
      this.quill.format('list', false);
    }
  }
}
```

## Handler Function

### Parameters

```typescript
handler: function(range: Range, context: Context): boolean | void
```

**Range object:**
```typescript
interface Range {
  index: number;  // Selection start
  length: number; // Selection length (0 for cursor)
}
```

**Context object:**
```typescript
interface Context {
  collapsed: boolean;              // Selection is collapsed
  empty: boolean;                  // Line is empty
  offset: number;                  // Cursor offset in line
  prefix: string;                  // Text before cursor
  suffix: string;                  // Text after cursor
  format: Record<string, any>;     // Current formats
  event: KeyboardEvent;            // Original keyboard event
}
```

### Return Values

Handler return value controls event propagation:

```javascript
bindings: {
  preventDefault: {
    key: 'S',
    shortKey: true,
    handler: function() {
      this.saveContent();
      return false;  // Prevent default browser behavior
    }
  },

  allowDefault: {
    key: 'B',
    shortKey: true,
    handler: function(range, context) {
      console.log('Bold toggled');
      // No return = allow default behavior
    }
  },

  explicitAllow: {
    key: 'I',
    shortKey: true,
    handler: function() {
      this.trackAction('italic');
      return true;  // Explicitly allow default
    }
  }
}
```

- `return false` - Prevent default behavior and stop propagation
- `return true` or no return - Allow default behavior
- Handler has access to `this.quill` for editor instance

## Complete Examples

### Markdown Shortcuts

```javascript
const quill = new Quill('#editor', {
  modules: {
    keyboard: {
      bindings: {
        // # + space = heading
        heading: {
          key: ' ',
          collapsed: true,
          prefix: /^#{1,6}$/,
          handler: function(range, context) {
            const level = context.prefix.length;
            this.quill.deleteText(range.index - level, level);
            this.quill.formatLine(range.index, 1, 'header', level);
            this.quill.setSelection(range.index);
            return false;
          }
        },

        // - or * + space = bullet list
        bulletList: {
          key: ' ',
          collapsed: true,
          prefix: /^[-*]\s?$/,
          handler: function(range, context) {
            this.quill.deleteText(range.index - context.prefix.length, context.prefix.length);
            this.quill.formatLine(range.index, 1, 'list', 'bullet');
            return false;
          }
        },

        // 1. + space = ordered list
        orderedList: {
          key: ' ',
          collapsed: true,
          prefix: /^\d+\.\s?$/,
          handler: function(range, context) {
            this.quill.deleteText(range.index - context.prefix.length, context.prefix.length);
            this.quill.formatLine(range.index, 1, 'list', 'ordered');
            return false;
          }
        },

        // ``` + space = code block
        codeBlock: {
          key: ' ',
          collapsed: true,
          prefix: /^```$/,
          handler: function(range, context) {
            this.quill.deleteText(range.index - 3, 3);
            this.quill.formatLine(range.index, 1, 'code-block', true);
            return false;
          }
        }
      }
    }
  }
});
```

### Custom Save Handler

```javascript
bindings: {
  save: {
    key: 'S',
    shortKey: true,
    handler: function(range, context) {
      const content = this.quill.getContents();

      fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      })
      .then(() => console.log('Saved!'))
      .catch(err => console.error('Save failed:', err));

      return false;  // Prevent browser save dialog
    }
  }
}
```

### Tab Indentation

```javascript
bindings: {
  indent: {
    key: 'Tab',
    handler: function(range, context) {
      this.quill.format('indent', '+1');
      return false;
    }
  },

  outdent: {
    key: 'Tab',
    shiftKey: true,
    handler: function(range, context) {
      this.quill.format('indent', '-1');
      return false;
    }
  }
}
```

## Performance Considerations

- Avoid complex regex patterns in `prefix` - they run on every keystroke
- Keep handler functions lightweight
- Debounce expensive operations
- Test bindings across browsers and platforms

## TypeScript Support

```typescript
import Quill from 'quill';

interface KeyboardBinding {
  key: string | number;
  shortKey?: boolean;
  ctrlKey?: boolean;
  metaKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  collapsed?: boolean;
  empty?: boolean;
  format?: string[] | Record<string, any>;
  offset?: number;
  prefix?: RegExp;
  suffix?: RegExp;
  handler: (range: any, context: any) => boolean | void;
}

const bindings: Record<string, KeyboardBinding> = {
  bold: {
    key: 'B',
    shortKey: true,
    handler: function(range, context) {
      this.quill.format('bold', !context.format.bold);
      return false;
    }
  }
};

const quill = new Quill('#editor', {
  modules: {
    keyboard: { bindings }
  }
});
```

## Related Files

- **configuration.md** - Module configuration
- **toolbar-module.md** - Toolbar handlers (often triggered by keyboard)
- **api-formatting.md** - Format methods used in handlers
- **events.md** - Keyboard events

## Notes

- Default Quill bindings can be overridden by using same key combination
- Bindings are checked in order; first matching binding wins
- Use `shortKey` for better cross-platform compatibility
- Test keyboard shortcuts don't conflict with browser/OS shortcuts
