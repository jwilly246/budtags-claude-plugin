# Quill.js Skill - Package Documentation

A world-class Claude Code skill for Quill.js rich text editor integration using **progressive disclosure** for optimal performance.

---

## 🎯 Overview

This skill provides comprehensive knowledge of **Quill.js v2.0.3** - a powerful, extensible rich text editor for the modern web. It uses progressive disclosure to load only the information relevant to your task, reducing context by 93-97% for typical queries.

---

## 📁 Package Structure

```
quill/
├── SKILL.md                          # Main router (600 lines) - ENTRY POINT
├── README.md                         # This file
├── categories/                       # Modular category files (16 files)
│   ├── getting-started.md            # Quickstart, CDN setup, why Quill (200 lines)
│   ├── configuration.md              # All configuration options (250 lines)
│   ├── formats.md                    # 23 available formats reference (300 lines)
│   ├── delta.md                      # Delta format specification (160 lines)
│   ├── api-content.md                # Content methods (10 methods, 550 lines)
│   ├── api-formatting.md             # Formatting methods (5 methods, 470 lines)
│   ├── api-selection.md              # Selection methods (4 methods, 490 lines)
│   ├── api-editor.md                 # Editor lifecycle (6 methods, 450 lines)
│   ├── api-events.md                 # Event system (520 lines)
│   ├── api-model.md                  # Document traversal (5 methods, 550 lines)
│   ├── api-extension.md              # Registration methods (5 methods, 500 lines)
│   ├── toolbar-module.md             # Toolbar configuration (125 lines)
│   ├── keyboard-module.md            # Keyboard bindings (130 lines)
│   ├── history-module.md             # Undo/redo (105 lines)
│   ├── clipboard-module.md           # Paste handling (125 lines)
│   └── syntax-module.md              # Code highlighting (105 lines)
├── patterns/                         # Key concepts (3 files)
│   ├── themes.md                     # Snow/Bubble themes, customization (405 lines)
│   ├── registries.md                 # Multiple editors, custom formats (433 lines)
│   └── upgrading.md                  # v1.x → v2.0 migration (615 lines)
└── guides/                           # Advanced tutorials (3 files)
    ├── delta-design.md               # Delta format philosophy (667 lines)
    ├── custom-modules.md             # Module development guide (685 lines)
    └── parchment-blots.md            # Custom formats/Blots (847 lines)
```

**Total Size**: ~7,900 lines across all files
**Typical Context**: 100-200 lines (93-97% reduction)

---

## 🚀 Purpose

This skill helps with Quill.js tasks including:

### Getting Started
- CDN and NPM installation
- Basic editor initialization
- Theme selection (Snow, Bubble, Core)
- Understanding Quill's advantages

### API Usage
- Content manipulation (insert, delete, get, set)
- Formatting (inline, block, embeds)
- Selection management
- Event handling
- Document traversal

### Configuration
- Editor options (placeholder, readOnly, bounds, etc.)
- Format whitelisting
- Module configuration
- Debugging

### Modules
- Toolbar customization (buttons, handlers)
- Keyboard shortcuts (bindings, context)
- History (undo/redo configuration)
- Clipboard (paste matchers, HTML processing)
- Syntax (code highlighting)

### Delta Format
- Document representation
- Change operations
- Operational transformation
- Collaborative editing

### Advanced Customization
- Custom modules
- Custom formats with Parchment
- Custom Blots (Inline, Block, Embed)
- Multiple editors with different formats

---

## 💡 Progressive Disclosure

**The skill loads ONLY the patterns relevant to your query:**

### Quick Lookup (1-2 min)
**Load**: 1 category file
**Context**: ~100-150 lines (97% reduction)
**Use**: Single method or concept lookup

**Example**: "How do I insert bold text?"
→ Load `categories/api-content.md` (insertText method section)

### Standard Query (3-5 min)
**Load**: 2-3 category files
**Context**: ~250-400 lines (95% reduction)
**Use**: Feature implementation or configuration

**Example**: "How do I customize the toolbar?"
→ Load `categories/toolbar-module.md` + `categories/formats.md`

### Comprehensive Guide (10+ min)
**Load**: Multiple categories + guide
**Context**: ~600-900 lines (90% reduction)
**Use**: Complex customization or module development

**Example**: "How do I create a custom embed format?"
→ Load `guides/parchment-blots.md` + `categories/api-extension.md`

---

## 📖 Usage

### Method 1: Automatic Activation

The skill auto-activates when you mention Quill.js:

```
"How do I initialize Quill with the Snow theme?"
"What's the difference between format() and formatText()?"
"How do I create custom keyboard shortcuts?"
```

### Method 2: Direct Invocation

```
Use the quill skill to help me [task]
```

### Method 3: Slash Command

```
/quill
```

---

## 📊 Progressive Loading Examples

### Example 1: Basic Setup Question

**User**: "How do I set up Quill?"

**Skill Loads**: `categories/getting-started.md` (~200 lines)
**Context Reduction**: 97%

### Example 2: API Method Question

**User**: "How do I delete text programmatically?"

**Skill Loads**: `categories/api-content.md` (deleteText section, ~50 lines)
**Context Reduction**: 99%

### Example 3: Module Configuration

**User**: "How do I add a custom toolbar button?"

**Skill Loads**: `categories/toolbar-module.md` (~125 lines)
**Context Reduction**: 98%

### Example 4: Delta Format

**User**: "How does Delta format work?"

**Skill Loads**: `categories/delta.md` (~160 lines)
**Context Reduction**: 98%

### Example 5: Advanced Customization

**User**: "How do I create a custom mention format?"

**Skill Loads**:
- `guides/parchment-blots.md` (~847 lines)
- `categories/api-extension.md` (register section, ~100 lines)

**Context Reduction**: 88%

---

## 🔍 Category Files Reference

### Getting Started (3 files)
- **getting-started.md** - Quickstart, installation, why Quill
- **configuration.md** - All configuration options
- **formats.md** - 23 built-in formats

### API Reference (7 files)
- **api-content.md** - deleteText, getContents, insertText, setContents, etc.
- **api-formatting.md** - format, formatText, formatLine, getFormat, removeFormat
- **api-selection.md** - getSelection, setSelection, getBounds, scrollSelectionIntoView
- **api-editor.md** - focus, blur, enable, disable, update, hasFocus
- **api-events.md** - text-change, selection-change, on, once, off
- **api-model.md** - find, getLeaf, getLine, getIndex
- **api-extension.md** - register, import, debug, addContainer, getModule

### Delta & Modules (6 files)
- **delta.md** - Delta format specification
- **toolbar-module.md** - Toolbar configuration
- **keyboard-module.md** - Keyboard bindings
- **history-module.md** - Undo/redo
- **clipboard-module.md** - Paste handling
- **syntax-module.md** - Code highlighting

---

## 🎨 Pattern Files Reference

### themes.md (405 lines)
**When to Load**: Theme selection or customization

**Contains**:
- Snow theme (clean flat toolbar)
- Bubble theme (tooltip-based)
- Core/minimal theme
- CSS customization
- Dark mode examples
- Custom toolbar containers

### registries.md (433 lines)
**When to Load**: Multiple editors with different formats

**Contains**:
- Custom registry creation
- Per-instance format registration
- Essential Parchment formats
- Complete working example

### upgrading.md (615 lines)
**When to Load**: Migrating from Quill v1.x

**Contains**:
- TypeScript changes
- Configuration changes
- Module API changes
- Parchment changes
- Migration checklist

---

## 📚 Guide Files Reference

### delta-design.md (667 lines)
**When to Load**: Understanding Delta format philosophy

**Contains**:
- Design principles
- Document representation evolution
- Change operation design
- Real-world examples

### custom-modules.md (685 lines)
**When to Load**: Building custom modules

**Contains**:
- Word counter example (4 stages)
- Registration patterns
- Best practices
- Real-world module examples

### parchment-blots.md (847 lines)
**When to Load**: Creating custom formats

**Contains**:
- Blot types (Inline, Block, BlockEmbed, Embed)
- Required methods
- Medium-clone tutorial
- Complete examples for each type

---

## 🎓 Key Features

### Comprehensive Coverage
- ✅ All 39 API methods documented
- ✅ All 23 built-in formats
- ✅ All 5 core modules
- ✅ Delta format specification
- ✅ Custom module development
- ✅ Custom format development (Parchment/Blots)

### Rich Documentation
- ✅ TypeScript signatures for all methods
- ✅ Parameter and return value descriptions
- ✅ Hundreds of code examples
- ✅ Common use cases
- ✅ Best practices and gotchas
- ✅ Cross-references between files

### Official Sources
- ✅ All content from https://quilljs.com/docs
- ✅ Official Quill.js v2.0.3 documentation
- ✅ Direct URLs to source docs

---

## 📈 Performance Metrics

| Metric | Monolithic Docs | This Skill | Improvement |
|--------|-----------------|------------|-------------|
| **Total Size** | ~7,900 lines | ~7,900 lines | Same coverage |
| **Basic Setup Query** | 7,900 lines | ~200 lines | 97% reduction |
| **API Method Query** | 7,900 lines | ~100 lines | 99% reduction |
| **Module Config Query** | 7,900 lines | ~125 lines | 98% reduction |
| **Delta Format Query** | 7,900 lines | ~160 lines | 98% reduction |
| **Custom Format Guide** | 7,900 lines | ~950 lines | 88% reduction |
| **Maintainability** | Hard (one file) | Easy (modular) | 🎯 |

---

## 🔧 Common Workflows

### Workflow 1: First-Time Setup

```
User: How do I add Quill to my project?
Skill: [Loads categories/getting-started.md]
Skill: [Provides CDN setup, initialization code]
```

**Context**: ~200 lines (97% reduction)

### Workflow 2: API Usage

```
User: How do I insert formatted text at a specific position?
Skill: [Loads categories/api-content.md → insertText section]
Skill: [Shows method signature, parameters, examples]
```

**Context**: ~100 lines (99% reduction)

### Workflow 3: Module Customization

```
User: I need custom toolbar buttons
Skill: [Loads categories/toolbar-module.md]
Skill: [Shows array config, HTML container, custom handlers]
```

**Context**: ~125 lines (98% reduction)

### Workflow 4: Advanced Customization

```
User: How do I create a mention format like @username?
Skill: [Loads guides/parchment-blots.md]
Skill: [Shows Inline Blot creation, create/formats methods]
Skill: [Loads categories/api-extension.md for registration]
```

**Context**: ~950 lines (88% reduction)

---

## 🆕 Version Information

- **Quill Version**: v2.0.3 (latest stable)
- **Skill Created**: 2025-11-14
- **License**: BSD 3-Clause (Quill.js)
- **Official Docs**: https://quilljs.com/docs
- **GitHub**: https://github.com/slab/quill

---

## 🔗 Related Skills

- **labelary-help** - ZPL rendering API (if using Quill for label content)
- **verify-alignment** - BudTags coding standards verification
- **skill-builder** - Creating new Claude Code skills

---

## 📝 Usage Statistics

**Total Documentation**:
- 22 total files
- ~7,900 lines of content
- 39 API methods
- 23 built-in formats
- 5 core modules
- 3 pattern guides
- 3 advanced tutorials
- Hundreds of code examples

**Typical Query Loads**: 100-200 lines (93-97% reduction)

---

## 🎯 Next Steps

1. **Activate the skill**: Ask a Quill.js question or use `/quill`
2. **Explore categories**: Load specific category files as needed
3. **Build features**: Use API references for implementation
4. **Customize**: Use patterns and guides for advanced customization

---

## 💬 Support

For questions or improvements, reference:
- This README.md - Skill structure and usage
- SKILL.md - Progressive loading router
- Official Quill.js docs: https://quilljs.com/docs
- Official GitHub: https://github.com/slab/quill

---

**You have complete knowledge of Quill.js v2.0.3 via modular, focused files. Use progressive disclosure to provide fast, relevant answers!**
