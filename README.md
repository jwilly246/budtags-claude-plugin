# BudTags Claude Plugin

A comprehensive Claude Code plugin for BudTags development, providing specialized skills, commands, agents, and hooks for working with:

- **Metrc API** - Cannabis compliance and tracking
- **LeafLink** - Wholesale marketplace integration
- **QuickBooks** - Accounting integration
- **TanStack** - Query, Table, and Virtual components
- **Laravel/React/Inertia** - Full-stack development patterns

## Installation

### For Partners (Recommended)

```bash
# Install the plugin
/plugin install budtags/budtags-claude-plugin

# Update to latest version
/plugin update budtags
```

All skills, commands, and agents will be namespaced under `budtags:`:
- `/budtags:metrc-api`
- `/budtags:verify-alignment`
- `/budtags:tanstack-query`

### For BudTags Maintainers (Symlink Setup)

If you're a maintainer who wants short names without the namespace:

```bash
# Backup existing .claude directory
mv /path/to/budtags/.claude /path/to/budtags/.claude-backup

# Create symlink to plugin repo
ln -s ~/repos/budtags-claude-plugin /path/to/budtags/.claude
```

This gives you direct access to all features without namespacing.

## Contents

| Type | Count | Description |
|------|-------|-------------|
| Skills | 19 | Specialized domain knowledge (Metrc, LeafLink, TanStack, etc.) |
| Commands | 19 | Slash commands for common workflows |
| Agents | 20 | Subagent definitions for Task tool |
| Hooks | 5 | Auto-approve, file protection, pre-commit gates |

## Skills

- `budtags-testing` - BudTags testing patterns and PHPUnit practices
- `create-plan` - Implementation planning
- `decompose-plan` - Break down plans into work units
- `inertia` - Inertia.js v2 patterns
- `inertia-react-development` - Inertia + React client-side development
- `labelary-help` - ZPL label rendering via Labelary API
- `leaflink` - LeafLink API integration
- `metrc-api` - Metrc compliance API
- `quickbooks` - QuickBooks Online integration
- `quill` - Quill rich text editor
- `react-19` - React 19 patterns
- `run-plan` - Execute implementation plans
- `skill-builder` - Create new skills
- `tailwindcss-development` - Tailwind CSS v4 styling
- `tanstack-query` - TanStack Query (React Query)
- `tanstack-table` - TanStack Table
- `tanstack-virtual` - TanStack Virtual (virtualization)
- `verify-alignment` - Code alignment verification
- `zpl` - ZPL II label programming

## Commands

Common workflows accessible via `/budtags:command-name`:

- `metrc-help`, `metrc-api` - Metrc API assistance
- `leaflink-help`, `leaflink` - LeafLink integration help
- `quickbooks-help` - QuickBooks integration help
- `tanstack-query`, `tanstack-table`, `tanstack-virtual` - TanStack helpers
- `verify-alignment` - Verify code follows BudTags patterns
- `testing-help` - Testing assistance
- `pre-commit` - Pre-commit checks
- `build-skill` - Create new skills
- `refactor-code` - Code refactoring assistance
- `zpl-help`, `labelary-help` - ZPL label generation

## Agents

20 specialized agents for various development tasks. Key agents include:

- `metrc-specialist` - Metrc API integration expert
- `leaflink-specialist` - LeafLink integration expert
- `quickbooks-specialist` - QuickBooks integration expert
- `tanstack-specialist` - TanStack ecosystem expert
- `react-specialist` - React/Inertia frontend development
- `php-developer` - PHP/Laravel backend development
- `fullstack-developer` - Full-stack development
- `security-auditor` - Security reviews
- `code-reviewer` - Code quality reviews

## Hooks

- `auto-approve-reads.py` - Auto-approve safe read operations
- `file-protection.py` - Protect critical files from accidental modification
- `pre-commit-gate.py` - Enforce pre-commit checks
- `post-edit-tests.py` - Run tests after edits
- `skill-forced-eval-hook.sh` - Force skill evaluation

## Updating

```bash
# Check for updates
/plugin update budtags

# Or manually pull latest
cd ~/repos/budtags-claude-plugin
git pull origin main
```

## License

UNLICENSED - Proprietary BudTags software
