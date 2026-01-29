# BudTags Claude Plugin Marketplace

A Claude Code plugin marketplace for BudTags development tools.

## Installation

### 1. Add the marketplace

```bash
/plugin marketplace add jwilly246/budtags-claude-plugin
```

### 2. Install the plugin

```bash
/plugin install budtags@jwilly246
```

## Available Plugins

| Plugin | Description |
|--------|-------------|
| **budtags** | BudTags development toolkit with Metrc, LeafLink, QuickBooks integrations |

### BudTags Plugin Contents

- **19 Skills** - Specialized domain knowledge (Metrc API, LeafLink, TanStack, QuickBooks, etc.)
- **19 Commands** - Slash commands for common workflows
- **20 Agents** - Subagent definitions for Task tool
- **5 Hooks** - Auto-approve, file protection, pre-commit gates

## Updating

```bash
/plugin update budtags@jwilly246
```

## For BudTags Maintainers

If you're developing the plugin locally, use a symlink:

```bash
# Create symlink to plugin subdirectory
ln -s ~/repos/budtags-claude-plugin/budtags /path/to/your-project/.claude
```

## License

UNLICENSED - Proprietary BudTags software
