---
name: budtags-setup
description: Interactive setup wizard for configuring which BudTags plugin skills, agents, and hooks to enable
version: 1.0.0
category: workflow
---

# BudTags Plugin Setup Wizard

Configure which skills, agents, and hooks are enabled for this plugin.

## Instructions

When this skill is invoked, follow these steps:

### Step 1: Read the Item Registry

Read the file `$PLUGIN_DIR/config/items.json` (or `config/items.json` relative to the plugin root) to get the full list of available:
- **Skills** (with versions)
- **Agents**
- **Hooks**

Each item has: `id`, `name`, `description`, `default` (boolean), and skills also have `version`.

### Step 2: Check for laravel-simplifier (Optional)

Check if `~/.claude/plugins/laravel-simplifier` exists. If not, inform the user:
> "Optional: The `laravel-simplifier` plugin enhances PHP/Laravel agents. To install: `cd ~/.claude && git clone https://github.com/laravel/claude-code laravel-simplifier`"

### Step 3: Ask Configuration Preference

Use AskUserQuestion to ask:

**Question:** "How would you like to configure BudTags plugin?"

**Options:**
1. **Recommended defaults** - "Enable commonly-used skills, agents, and hooks (recommended)"
2. **Everything enabled** - "Enable all available features"
3. **Minimal** - "Enable only core planning and review features"
4. **Custom** - "Choose exactly which features to enable"

### Step 4: Handle Selection

#### If "Recommended defaults":
- Use items where `default: true` in the registry

#### If "Everything enabled":
- Enable all skills, agents, and hooks

#### If "Minimal":
- Skills: `create-plan`, `decompose-plan`, `run-plan`, `verify-alignment`
- Agents: `budtags-specialist`, `code-reviewer`, `debugger`
- Hooks: `auto-approve-reads`, `file-protection`

#### If "Custom":
Present items in batches using AskUserQuestion with `multiSelect: true`.

**Skills batch 1** (first 4):
Show: `name vX.X.X - description` format
Let user toggle which to enable

**Skills batch 2** (next 4), etc.

Continue for all skills, then agents, then hooks.

### Step 5: Write Configuration

Create `.budtags-config.json` in the plugin directory:

```json
{
  "version": "1.0.0",
  "configured_at": "<ISO timestamp>",
  "mode": "<defaults|everything|minimal|custom>",
  "skills": ["skill-id-1", "skill-id-2", ...],
  "agents": ["agent-id-1", "agent-id-2", ...],
  "hooks": ["hook-id-1", "hook-id-2", ...]
}
```

### Step 6: Create Flag File

Create an empty file `.budtags-configured` in the plugin directory to mark setup as complete.

### Step 7: Confirm Completion

Tell the user:
> "BudTags plugin configured! Enabled X skills, Y agents, and Z hooks."
> "To reconfigure later, run `/budtags-setup` again."

---

## Notes

- The plugin directory is typically where this skill file lives (two levels up from SKILL.md)
- If `.budtags-configured` already exists, ask if they want to reconfigure
- Always show a summary of what was enabled at the end
