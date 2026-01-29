# React 19 Skill

A Claude Code skill for React 19 documentation, covering versions 19.0, 19.1, and 19.2.

## What's Included

- **New Hooks:** useActionState, useOptimistic, useFormStatus, use(), useEffectEvent
- **Form Actions:** Automatic pending states, form reset, sequential handling
- **Syntax Changes:** ref as prop, simplified Context provider
- **React 19.2:** Activity component, Performance Tracks
- **Migration Guides:** Step-by-step upgrade paths

## Usage

This skill auto-activates when working with React files (`.tsx`, `.jsx`) or when keywords like "react 19", "useActionState", "Activity", etc. are mentioned.

### Progressive Loading

The skill uses progressive disclosure - only relevant pattern files are loaded based on your question:

| Question | Files Loaded | Context |
|----------|--------------|---------|
| "How do I upgrade?" | upgrade-guide, breaking-changes, migration | ~500 lines |
| "What's new?" | new-hooks, actions-forms, use-api | ~550 lines |
| "What changed with refs?" | ref-changes | ~150 lines |
| "What is Activity?" | activity-component | ~150 lines |

## File Structure

```
react-19/
├── SKILL.md              # Main entry point
├── README.md             # This file
├── patterns/             # Feature documentation
│   ├── 01-upgrade-guide.md
│   ├── 02-new-hooks.md
│   ├── 03-actions-forms.md
│   ├── 04-use-api.md
│   ├── 05-ref-changes.md
│   ├── 06-context-changes.md
│   ├── 07-metadata-stylesheets.md
│   ├── 08-resource-preloading.md
│   ├── 09-error-handling.md
│   ├── 10-suspense-hydration.md
│   ├── 11-activity-component.md
│   ├── 12-use-effect-event.md
│   ├── 13-performance-tracks.md
│   └── 14-breaking-changes.md
└── migrations/           # Version upgrade guides
    ├── from-18-to-19.md
    ├── 19-to-19-1.md
    └── 19-1-to-19-2.md
```

## BudTags Context

This skill includes notes specific to the BudTags stack (Laravel + Inertia + React):

- ✅ Features that apply directly (useOptimistic, useEffectEvent, Activity)
- ⚠️ Features to compare with existing patterns (useActionState vs Inertia useForm)
- ❌ Features we don't use (Server Components, Server Actions)

## Sources

- [React 19 Release](https://react.dev/blog/2024/12/05/react-19)
- [React 19.2 Release](https://react.dev/blog/2025/10/01/react-19-2)
- [React GitHub Changelog](https://github.com/facebook/react/blob/main/CHANGELOG.md)
