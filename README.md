# BudTags Claude Plugin

A comprehensive Claude Code plugin for BudTags development - includes cannabis compliance integrations (Metrc, LeafLink), accounting (QuickBooks), modern frontend tooling, planning workflows, and specialized agents.

## Installation

```bash
/plugin install budtags@jwilly246/budtags-claude-plugin
```

## First-Time Setup

After installation, run the setup wizard to configure which features to enable:

```
/budtags:budtags-setup
```

Choose from:
- **Recommended defaults** - Commonly-used skills, agents, and hooks
- **Everything enabled** - All available features
- **Minimal** - Core planning and review features only
- **Custom** - Pick exactly which features to enable

---

## Skills (19)

Domain-specific knowledge that Claude can reference during development.

### Cannabis Industry Integrations
| Skill | Version | Description |
|-------|---------|-------------|
| **Metrc API** | 2.0.0 | Cannabis compliance tracking API integration |
| **LeafLink** | 1.0.0 | LeafLink wholesale marketplace API integration |

### Accounting & Business
| Skill | Version | Description |
|-------|---------|-------------|
| **QuickBooks** | 2.0.0 | QuickBooks Online OAuth, invoices, customers, payments |

### Frontend Development
| Skill | Version | Description |
|-------|---------|-------------|
| **React 19** | 1.0.0 | React 19 new hooks, Actions, and migration guides |
| **Inertia** | 1.0.0 | Inertia.js v2 patterns for Laravel + React full-stack development |
| **Inertia React Dev** | 1.0.0 | Inertia.js v2 React client-side development patterns |
| **Tailwind CSS** | 1.0.0 | Tailwind CSS v4 styling patterns and utilities |
| **TanStack Query** | 1.0.0 | React Query v5 data fetching, caching, mutations |
| **TanStack Table** | 1.0.0 | Headless table components with sorting, filtering, pagination |
| **TanStack Virtual** | 1.0.0 | Virtualized list rendering for large datasets |
| **Quill** | 1.0.0 | Quill.js rich text editor API and configuration |

### Testing & Quality
| Skill | Version | Description |
|-------|---------|-------------|
| **BudTags Testing** | 2.3.0 | PHPUnit test patterns, Mockery mocking, multi-tenancy test helpers |
| **Verify Alignment** | 3.0.0 | Verify code against BudTags coding standards |

### Planning & Workflow
| Skill | Version | Description |
|-------|---------|-------------|
| **Create Plan** | 1.0.0 | Research-driven feature planning with codebase discovery |
| **Decompose Plan** | 3.0.0 | Break plans into context-window-sized work units |
| **Run Plan** | 1.0.0 | Autonomously execute decomposed work units |

### Label Printing
| Skill | Version | Description |
|-------|---------|-------------|
| **ZPL** | 1.0.0 | Zebra Programming Language for label printing |
| **Labelary Help** | 1.0.0 | ZPL label preview and conversion via Labelary API |

### Meta
| Skill | Version | Description |
|-------|---------|-------------|
| **Skill Builder** | 1.0.0 | Create new Claude Code skills following patterns |

---

## Agents (20)

Specialized subagents for the Task tool that handle specific domains.

### Core Development
| Agent | Description |
|-------|-------------|
| **PHP Developer** | Laravel, PHPUnit, Composer, and modern PHP 8+ |
| **TypeScript Developer** | TypeScript/Node.js backend and React frontend |
| **Fullstack Developer** | End-to-end feature implementation (Laravel + React) |
| **React Specialist** | React 19 + Inertia + TypeScript frontend expertise |

### Industry Specialists
| Agent | Description |
|-------|-------------|
| **Metrc Specialist** | Metrc cannabis tracking API expertise |
| **LeafLink Specialist** | LeafLink marketplace API integration expertise |
| **QuickBooks Specialist** | QuickBooks Online OAuth and API integration |

### Infrastructure & Data
| Agent | Description |
|-------|-------------|
| **MySQL Specialist** | MySQL performance tuning and query optimization |
| **Redis Specialist** | Redis caching, pub/sub, and performance optimization |
| **Terraform Specialist** | Infrastructure as code and multi-cloud provisioning |

### Frontend Libraries
| Agent | Description |
|-------|-------------|
| **TanStack Specialist** | TanStack Query, Table, Virtual, Form, Router expertise |

### Quality & Review
| Agent | Description |
|-------|-------------|
| **BudTags Specialist** | Code review for BudTags patterns and security |
| **Code Reviewer** | General code review for best practices and clean code |
| **Security Auditor** | Security vulnerability audits and compliance checks |
| **Debugger** | Systematic debugging and root cause analysis |
| **Mutation Testing** | Mutation testing to measure and improve test quality |

### Context & Planning
| Agent | Description |
|-------|-------------|
| **Context Gathering** | Gather comprehensive context for new tasks |
| **Context Refinement** | Update task context with session discoveries |
| **Knowledge Researcher** | Search and synthesize organizational knowledge |
| **Logging** | Consolidate and organize work logs for tasks |

---

## Commands (21)

Slash commands available via `/budtags:<command>`.

### Setup & Management
| Command | Description |
|---------|-------------|
| `budtags-setup` | Configure which skills, agents, and hooks to enable |
| `budtags-uninstall` | Remove config or fully uninstall the plugin |

### Planning Workflow
| Command | Description |
|---------|-------------|
| `decompose-plan` | Break a plan into context-window-sized work units |
| `run-plan` | Execute decomposed work units autonomously |
| `create-prompt` | Create a new prompt file |
| `run-prompt` | Execute a prompt file |

### Code Quality
| Command | Description |
|---------|-------------|
| `verify-alignment` | Verify code against BudTags coding standards |
| `refactor-code` | Refactor code following patterns |
| `pre-commit` | Run pre-commit validation |

### API Help
| Command | Description |
|---------|-------------|
| `metrc-api` | Metrc API reference and patterns |
| `metrc-help` | Interactive Metrc API guidance |
| `leaflink` | LeafLink API reference |
| `leaflink-help` | Interactive LeafLink API guidance |
| `quickbooks-help` | QuickBooks Online API guidance |

### Frontend Help
| Command | Description |
|---------|-------------|
| `tanstack-query` | TanStack Query patterns and examples |
| `tanstack-table` | TanStack Table patterns and examples |
| `tanstack-virtual` | TanStack Virtual patterns and examples |

### Testing & Tools
| Command | Description |
|---------|-------------|
| `testing-help` | PHPUnit and testing guidance |
| `labelary-help` | Labelary ZPL preview API guidance |
| `zpl-help` | ZPL label programming guidance |
| `build-skill` | Create a new skill following patterns |

---

## Hooks (5)

Automated behaviors that run during Claude Code operations.

| Hook | Description | Default |
|------|-------------|---------|
| **Auto-Approve Reads** | Automatically approve safe file read operations | Enabled |
| **File Protection** | Confirm before editing sensitive files (.env, etc.) | Enabled |
| **Pre-Commit Gate** | Validate commits before allowing | Enabled |
| **Skill Eval** | Evaluate skill usage on prompt submission | Enabled |
| **Post-Edit Tests** | Run related tests after file edits | Disabled |

---

## Uninstalling

```
/budtags:budtags-uninstall
```

Options:
- **Reset config only** - Remove config files, keep plugin installed (for reconfiguring)
- **Full uninstall** - Disable plugin in settings, keep cached files
- **Full uninstall + delete files** - Remove everything including cached plugin files

## Updating

```bash
/plugin update budtags@jwilly246/budtags-claude-plugin
```

---

## For BudTags Maintainers

If developing the plugin locally, use a symlink:

```bash
ln -s ~/repos/budtags-claude-plugin/budtags ~/.claude/plugins/budtags-dev
```

Then enable in `~/.claude/settings.json`:
```json
{
  "plugins": {
    "budtags@budtags-dev": true
  }
}
```

### Optional Dependency

The `laravel-simplifier` plugin enhances PHP/Laravel agents:

```bash
cd ~/.claude/plugins && git clone https://github.com/laravel/claude-code laravel-simplifier
```

---

## License

UNLICENSED - Proprietary BudTags software
