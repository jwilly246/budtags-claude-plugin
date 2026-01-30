# BudTags Plugin Uninstall

Remove BudTags plugin configuration files and optionally uninstall completely.

## Instructions

Follow these steps exactly:

### Step 1: Confirm Uninstall

Use AskUserQuestion to confirm what the user wants to do:

```
Question: "What would you like to remove?"
Header: "Uninstall"
Options:
1. Label: "Reset config only"
   Description: "Remove .budtags-configured and .budtags-config.json, keep plugin installed"
2. Label: "Full uninstall"
   Description: "Remove config files and disable plugin in settings, keep cached files"
3. Label: "Full uninstall + delete files"
   Description: "Remove everything including downloaded plugin files from cache"
4. Label: "Cancel"
   Description: "Don't remove anything"
```

### Step 2: Process Selection

**If "Cancel":**
Exit gracefully with: "Uninstall cancelled. No changes made."

**If "Reset config only", "Full uninstall", or "Full uninstall + delete files":**

Delete these files from the plugin directory using Bash:
```bash
rm -f "${CLAUDE_PLUGIN_ROOT}/.budtags-configured" "${CLAUDE_PLUGIN_ROOT}/.budtags-config.json"
```

### Step 3: Handle Full Uninstall (if selected)

**Only if "Full uninstall" or "Full uninstall + delete files" was selected:**

1. Read the user's `~/.claude/settings.json` file
2. Look for the `plugins` object
3. Find and set the budtags plugin entry to `false` (the key may vary, look for entries containing "budtags")
4. Write the updated settings file back

Example transformation:
```json
// Before
{
  "plugins": {
    "budtags@budtags-claude-plugin": true
  }
}

// After
{
  "plugins": {
    "budtags@budtags-claude-plugin": false
  }
}
```

### Step 4: Delete Cached Plugin Files (if selected)

**Only if "Full uninstall + delete files" was selected:**

Delete the cached plugin directory:
```bash
rm -rf ~/.claude/plugins/cache/budtags-claude-plugin
```

### Step 5: Show Summary

**For "Reset config only":**
```
BudTags configuration reset.

Removed:
- .budtags-configured
- .budtags-config.json

Plugin is still installed. Run /budtags:budtags-setup to reconfigure.
```

**For "Full uninstall":**
```
BudTags plugin disabled.

Removed:
- .budtags-configured
- .budtags-config.json
- Disabled plugin in ~/.claude/settings.json

Cached plugin files kept at ~/.claude/plugins/cache/budtags-claude-plugin

Restart Claude Code to complete uninstall.

To reinstall later, set the plugin back to true in settings.
```

**For "Full uninstall + delete files":**
```
BudTags plugin completely removed.

Removed:
- .budtags-configured
- .budtags-config.json
- Disabled plugin in ~/.claude/settings.json
- Deleted ~/.claude/plugins/cache/budtags-claude-plugin

Restart Claude Code to complete uninstall.

To reinstall later, re-add the plugin from the marketplace.
```

## Important Notes

- The plugin directory is `${CLAUDE_PLUGIN_ROOT}` (where this command file lives)
- Use `rm -f` to avoid errors if files don't exist
- For full uninstall, modify `~/.claude/settings.json`, not `settings.local.json`
- Always tell user to restart Claude Code after full uninstall
- The plugin cache at `~/.claude/plugins/cache/` is managed by Claude Code, don't delete it manually
