# BudTags Claude Plugin

**Version 1.3.0**

A comprehensive Claude Code plugin for BudTags development - includes cannabis compliance integrations (Metrc, LeafLink), accounting (QuickBooks), modern frontend tooling, planning workflows, and specialized agents.

## CLAUDE.md - Passive Context Index

This plugin includes a compressed `CLAUDE.md` file that provides **passive context** to Claude Code. Unlike skills that require explicit invocation, CLAUDE.md is automatically loaded at session start and always available.

**Why?** [Vercel's research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) found that passive context (AGENTS.md) achieved 100% task completion vs 53% with on-demand skills - because agents often don't invoke skills even when available.

**What it contains:**
- Compressed index pointing to all skill documentation (~3.6KB)
- Critical pattern reminders (org scoping, MetrcApi, flash messages)
- License type restrictions for Metrc API
- Directive: "Prefer retrieval-led reasoning over pre-training-led reasoning"

The model reads this index and retrieves relevant skill files directly, without needing skill invocation decisions.

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
| **QuickBooks** | 2.0.1 | QuickBooks Online OAuth, invoices, customers, payments |

### Frontend Development
| Skill | Version | Description |
|-------|---------|-------------|
| **React 19** | 1.0.0 | React 19 new hooks, Actions, and migration guides |
| **Inertia** | 1.0.1 | Inertia.js v2 patterns for Laravel + React full-stack development |
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
| **Verify Alignment** | 3.0.1 | Verify code against BudTags coding standards |

### Planning & Workflow
| Skill | Version | Description |
|-------|---------|-------------|
| **Create Plan** | 1.1.0 | Research-driven feature planning with codebase discovery |
| **Decompose Plan** | 3.2.0 | Break plans into context-window-sized work units |
| **Run Plan** | 1.3.0 | Autonomously execute decomposed work units |

### Label Printing
| Skill | Version | Description |
|-------|---------|-------------|
| **ZPL** | 1.0.0 | Zebra Programming Language for label printing |
| **Labelary Help** | 1.0.1 | ZPL label preview and conversion via Labelary API |

### Meta
| Skill | Version | Description |
|-------|---------|-------------|
| **Skill Builder** | 1.0.0 | Create new Claude Code skills following patterns |

---

## Agents (20)

Specialized subagents for the Task tool that handle specific domains.

### Core Development
| Agent | Version | Description |
|-------|---------|-------------|
| **PHP Developer** | 1.1.0 | Laravel 11+, PHPUnit, modern PHP 8+, auto-loads verify-alignment |
| **TypeScript Developer** | 2.0.0 | React + Inertia + TypeScript frontend, auto-loads verify-alignment |
| **Fullstack Developer** | 2.0.0 | Laravel + Inertia + React end-to-end, auto-loads verify-alignment |
| **React Specialist** | 1.0.0 | React 19 + Inertia + TypeScript frontend expertise |

### Industry Specialists
| Agent | Version | Description |
|-------|---------|-------------|
| **Metrc Specialist** | 1.0.0 | Metrc cannabis tracking API expertise |
| **LeafLink Specialist** | 1.0.0 | LeafLink marketplace API integration expertise |
| **QuickBooks Specialist** | 1.0.0 | QuickBooks Online OAuth and API integration |

### Infrastructure & Data
| Agent | Version | Description |
|-------|---------|-------------|
| **MySQL Specialist** | 1.0.0 | MySQL performance tuning and query optimization |
| **Redis Specialist** | 1.0.0 | Redis caching, pub/sub, and performance optimization |
| **Terraform Specialist** | 1.0.0 | Infrastructure as code and multi-cloud provisioning |

### Frontend Libraries
| Agent | Version | Description |
|-------|---------|-------------|
| **TanStack Specialist** | 1.0.0 | TanStack Query, Table, Virtual, Form, Router expertise |

### Quality & Review
| Agent | Version | Description |
|-------|---------|-------------|
| **BudTags Specialist** | 1.1.0 | BudTags patterns + test review (verify-alignment + budtags-testing) |
| **Code Reviewer** | 1.1.0 | General PRs and quality checks (use budtags-specialist for BudTags code) |
| **Security Auditor** | 1.1.0 | Security vulnerability audits with Laravel-specific checks |
| **Debugger** | 1.1.0 | Systematic debugging with Laravel/PHP patterns |
| **Mutation Testing** | 1.0.0 | Mutation testing to measure and improve test quality |

### Context & Planning
| Agent | Version | Description |
|-------|---------|-------------|
| **Context Gathering** | 1.0.0 | Gather comprehensive context for new tasks |
| **Context Refinement** | 1.0.0 | Update task context with session discoveries |
| **Knowledge Researcher** | 1.0.0 | Search and synthesize organizational knowledge |
| **Logging** | 1.0.0 | Consolidate and organize work logs for tasks |

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

### Updating CLAUDE.md

When adding new skills, update `CLAUDE.md` to include them in the compressed index:

```
|new-skill:{README.md,SKILL.md}
|new-skill/patterns:{pattern1.md,pattern2.md}
```

Keep the file under 8KB for optimal performance.

### Optional Dependency

The `laravel-simplifier` plugin enhances PHP/Laravel agents:

```bash
cd ~/.claude/plugins && git clone https://github.com/laravel/claude-code laravel-simplifier
```

---

## License

UNLICENSED - Proprietary BudTags software
