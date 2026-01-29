# BudTags Plugin Setup

Interactive setup wizard for configuring which skills, agents, and hooks to enable.

## Instructions

Follow these steps exactly:

### Step 1: Read the Item Registry

Read the file `config/items.json` from this plugin directory to get the available items.

### Step 2: Check Current Configuration Status

Check if `.budtags-configured` exists in the plugin directory. If it does, ask the user:
> "BudTags is already configured. Would you like to reconfigure?"

If they say no, exit gracefully.

### Step 3: Check for laravel-simplifier (Optional)

Check if `~/.claude/plugins/laravel-simplifier` directory exists. If not, mention:
> "Optional: The `laravel-simplifier` plugin enhances PHP/Laravel agents. To install later: `cd ~/.claude && git clone https://github.com/laravel/claude-code laravel-simplifier`"

### Step 4: Ask Configuration Preference

Use AskUserQuestion to ask how they want to configure:

```
Question: "How would you like to configure the BudTags plugin?"
Header: "Setup mode"
Options:
1. Label: "Recommended defaults"
   Description: "Enable commonly-used skills, agents, and hooks"
2. Label: "Everything enabled"
   Description: "Enable all available features"
3. Label: "Minimal"
   Description: "Only core planning and review features"
4. Label: "Custom"
   Description: "Choose exactly which features to enable"
```

### Step 5: Process Selection

**If "Recommended defaults":**
Use items where `default: true` in items.json

**If "Everything enabled":**
Use ALL items from items.json

**If "Minimal":**
- Skills: `create-plan`, `decompose-plan`, `run-plan`, `verify-alignment`
- Agents: `budtags-specialist`, `code-reviewer`, `debugger`
- Hooks: `auto-approve-reads`, `file-protection`

**If "Custom":**
Use AskUserQuestion with `multiSelect: true` to let user pick items.

For skills, present in batches of 4 with format: "Name vX.X.X - Description"
For agents, present in batches of 4 with format: "Name - Description"
For hooks, present all 5 at once.

### Step 6: Write Configuration

Write `.budtags-config.json` in the plugin directory:

```json
{
  "version": "1.0.0",
  "configured_at": "<ISO timestamp>",
  "mode": "<defaults|everything|minimal|custom>",
  "skills": ["skill-id-1", ...],
  "agents": ["agent-id-1", ...],
  "hooks": ["hook-id-1", ...]
}
```

### Step 7: Create Flag File

Write an empty file `.budtags-configured` in the plugin directory.

### Step 8: Show Summary

Tell the user:
```
BudTags plugin configured!
- Skills: X enabled
- Agents: Y enabled
- Hooks: Z enabled

To reconfigure later, run /budtags-setup again.
```

## Important Notes

- The plugin directory is where this command file lives (the budtags-claude-plugin root)
- Use the Write tool to create both config files
- Always show a summary at the end
