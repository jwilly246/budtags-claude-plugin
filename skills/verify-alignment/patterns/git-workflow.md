# Git Workflow Pattern

## Feature Branch Workflow (ALWAYS FOLLOW)

This project uses **Feature Branch Workflow** (also known as Topic Branching). All feature work MUST happen on dedicated branches with explicit merge commits to preserve history.

**Git Config**: `merge.ff = false` is set globally to enforce this pattern.

---

## Creating Feature Branches

**ALWAYS** create a separate branch before starting feature work:

```bash
# Check current state first
git branch          # What branch am I on?
git status          # Any uncommitted changes?

# Create feature branch
git checkout -b feature-name
```

### Correct Flow

```bash
# Starting new feature from main branch
git checkout main
git checkout -b add-user-authentication

# ... make commits on feature branch ...
git add .
git commit -m "Add login form component"
git commit -m "Add authentication controller"
```

### Wrong Flow

```bash
# Committing directly to parent branch without creating feature branch
git checkout main
git add .
git commit -m "Add authentication"  # WRONG! No feature branch
```

---

## Merging Features

**ALWAYS** use `--no-ff` to create explicit merge commits:

```bash
# Switch to parent branch
git checkout main

# Merge with explicit merge commit
git merge --no-ff feature-branch -m "Merge: Add user authentication feature"
```

### Why --no-ff Matters

**With --no-ff (Correct)**:
```
main ──────────────────────────────────→
       \                              /
        → feature-branch (work) ─────→ merge commit
```
- Visual history shows where features were developed
- Can revert entire feature with single revert
- Clear audit trail of when features integrated

**Without --no-ff (Wrong)**:
```
main ── commit ── commit ── commit ──→  (linear, loses context)
```
- Branch history lost
- Harder to identify related commits
- No clear feature boundaries

---

## Branch Naming Conventions

Use descriptive, hyphen-separated names:

```bash
# Correct
git checkout -b add-bulk-item-creation
git checkout -b fix-login-redirect
git checkout -b refactor-label-service

# Avoid
git checkout -b stuff
git checkout -b wip
git checkout -b test123
```

---

## Pre-Operation Checklist

**BEFORE any git operations, ALWAYS:**

1. **Check current branch**: `git branch`
2. **Check working tree status**: `git status`
3. **Confirm you're on the correct branch for the work**

```bash
# Before starting work
git branch          # Am I on the right branch?
git status          # Is my working directory clean?

# Before merging
git checkout main   # Switch to target branch
git branch          # Confirm I switched
git status          # Confirm clean state
```

---

## When to ASK the User

**Always ask the user before:**

- Creating a new branch (which parent branch?)
- Merging branches (which direction? which merge message?)
- Pushing to remote
- Any destructive operations (reset, force push, etc.)

**Example clarification questions:**

- "Should I create a feature branch for this work? What name would you like?"
- "Ready to merge `feature-branch` into `main` with `--no-ff`?"
- "Should I push this branch to origin?"

---

## Merge Commit Message Format

Use descriptive merge messages:

```bash
# Correct
git merge --no-ff feature-branch -m "Merge: Add bulk item creation to CreateItemModal"
git merge --no-ff fix-auth -m "Merge: Fix authentication redirect loop"

# Avoid
git merge --no-ff feature-branch -m "merge"
git merge --no-ff feature-branch -m "done"
```

---

## Branch Cleanup

After merging, optionally delete the feature branch:

```bash
# Delete local branch after merge
git branch -d feature-branch

# Delete remote branch (if pushed)
git push origin --delete feature-branch
```

---

## Quick Reference

```bash
# Start new feature
git checkout parent-branch
git checkout -b feature-name

# Work on feature
git add .
git commit -m "Description of change"

# Merge feature (from parent branch)
git checkout parent-branch
git merge --no-ff feature-name -m "Merge: Feature description"

# Cleanup (optional)
git branch -d feature-name
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| Committing directly to main | No feature isolation | Create feature branch first |
| Fast-forward merges | Loses branch history | Use `--no-ff` |
| Generic branch names | Hard to identify purpose | Use descriptive names |
| Merging without checking status | Risk of conflicts/errors | Always check branch & status first |
| Force pushing to shared branches | Destroys others' work | Never force push to main/shared |
| Skipping merge commit messages | No context for merge | Write descriptive merge message |
