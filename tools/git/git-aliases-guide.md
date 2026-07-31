# Git Aliases Reference Guide

A comprehensive collection of convenient Git aliases for your zsh shell to speed up your development workflow.

## Installation

Add these aliases to your `~/.zshrc` file and run:

```bash
source ~/.zshrc
```

Or restart your terminal.

---

## Basic Operations

| Alias | Command | Usage Example |
|-------|---------|---------------|
| `gs` | `git status` | `gs` - Check repository status |
| `ga` | `git add` | `ga file.txt` - Stage specific file |
| `gaa` | `git add .` | `gaa` - Stage all changes |
| `gc` | `git commit` | `gc` - Open editor for commit message |
| `gcm` | `git commit -m` | `gcm "fix: bug in login"` - Quick commit with message |
| `gca` | `git commit --amend` | `gca` - Amend the last commit |

### Usage Examples:

```bash
# Quick workflow to commit changes
gaa
gcm "feat: add user authentication"

# Modify last commit message
gca

# Check what's changed
gs
```

---

## Push & Pull Operations

| Alias | Command | Usage Example |
|-------|---------|---------------|
| `gp` | `git push` | `gp` - Push to remote |
| `gpf` | `git push --force-with-lease` | `gpf` - Safe force push (checks remote first) |
| `gpl` | `git pull` | `gpl` - Pull from remote |
| `gplr` | `git pull --rebase` | `gplr` - Pull and rebase local commits |

### Usage Examples:

```bash
# Standard push
gp

# Force push safely (after rebasing)
gpf

# Pull latest changes without merge commit
gplr
```

---

## Branch Management

| Alias | Command | Usage Example |
|-------|---------|---------------|
| `gco` | `git checkout` | `gco main` - Switch to main branch |
| `gcob` | `git checkout -b` | `gcob feature/new-api` - Create and switch to new branch |
| `gb` | `git branch` | `gb` - List all branches |
| `gbd` | `git branch -d` | `gbd old-feature` - Delete branch |

### Usage Examples:

```bash
# Create new feature branch
gcob feature/user-profile

# Switch back to main
gco main

# List all branches
gb

# Delete merged branch
gbd feature/completed-task
```

---

## Merge & Rebase

| Alias | Command | Usage Example |
|-------|---------|---------------|
| `gm` | `git merge` | `gm feature/new-api` - Merge branch into current |
| `gr` | `git rebase` | `gr main` - Rebase current branch onto main |
| `gri` | `git rebase -i` | `gri HEAD~3` - Interactive rebase last 3 commits |
| `grc` | `git rebase --continue` | `grc` - Continue rebase after resolving conflicts |
| `gra` | `git rebase --abort` | `gra` - Abort rebase and return to original state |

### Usage Examples:

```bash
# Update feature branch with latest main
gco feature/my-work
gr main

# Clean up last 5 commits before pushing
gri HEAD~5

# After fixing conflicts during rebase
ga conflicted-file.js
grc

# Something went wrong, abort rebase
gra
```

---

## Diff & Inspection

| Alias | Command | Usage Example |
|-------|---------|---------------|
| `gd` | `git diff` | `gd` - Show unstaged changes |
| `gdc` | `git diff --cached` | `gdc` - Show staged changes |
| `gl` | `git log --oneline --graph --decorate` | `gl` - Compact log view |
| `gla` | `git log --oneline --graph --decorate --all` | `gla` - All branches log |
| `glg` | Pretty formatted log | `glg` - Colorful detailed log |
| `glga` | Pretty formatted log (all branches) | `glga` - Colorful log with all branches |

### Usage Examples:

```bash
# See what you've changed before staging
gd

# Review what will be committed
gdc

# View commit history
gl

# See all branches in graphical log
glga
```

---

## Stash Operations

| Alias | Command | Usage Example |
|-------|---------|---------------|
| `gst` | `git stash` | `gst` - Stash current changes |
| `gstp` | `git stash pop` | `gstp` - Apply and remove latest stash |
| `gstl` | `git stash list` | `gstl` - List all stashes |

### Usage Examples:

```bash
# Save work in progress to switch branches
gst
gco hotfix/urgent-bug
# ... fix bug ...
gco feature/my-work
gstp

# View all stashed changes
gstl
```

---

## Reset & Clean

| Alias | Command | Usage Example |
|-------|---------|---------------|
| `gf` | `git fetch` | `gf` - Fetch from remote |
| `grh` | `git reset HEAD` | `grh file.txt` - Unstage file |
| `grhh` | `git reset --hard HEAD` | `grhh` - Discard all local changes |
| `gclean` | `git clean -fd` | `gclean` - Remove untracked files and directories |

### Usage Examples:

```bash
# Unstage accidentally added file
grh config/secrets.yml

# Discard all local changes (dangerous!)
grhh

# Remove all untracked files
gclean
```

---

## Utility Aliases

| Alias | Command | Usage Example |
|-------|---------|---------------|
| `gundo` | `git reset --soft HEAD~1` | `gundo` - Undo last commit, keep changes staged |
| `gwip` | `git add . && git commit -m "WIP"` | `gwip` - Quick work-in-progress commit |
| `gunwip` | Undo WIP commit | `gunwip` - Remove WIP commit if it's the last one |

### Usage Examples:

```bash
# Made a commit too early? Undo it
gundo
# Edit files more
gaa
gcm "Complete implementation"

# Save work in progress quickly
gwip

# Continue working later and remove WIP commit
gunwip
gaa
gcm "Completed feature"
```

---

## Common Workflows

### Starting a New Feature
```bash
gco main
gpl
gcob feature/new-feature
# ... make changes ...
gaa
gcm "feat: implement new feature"
gp
```

### Updating Feature Branch with Latest Main
```bash
gco feature/my-branch
gf
gr origin/main
# ... resolve conflicts if any ...
gpf
```

### Quick Save and Context Switch
```bash
# Save current work
gst

# Switch to urgent task
gco hotfix/critical-bug
# ... fix and commit ...

# Return to original work
gco feature/original-work
gstp
```

### Cleaning Up Commits Before PR
```bash
# Interactive rebase to squash/reword commits
gri HEAD~5
# ... edit commits in editor ...
gpf
```

### Oops, Wrong Commit
```bash
# Undo last commit but keep changes
gundo

# Make corrections
gaa
gcm "Correct commit message"
```

---

## Tips

- **`gpf` vs `gp --force`**: Always use `gpf` (force-with-lease) instead of regular force push. It's safer because it checks if someone else pushed to the branch first.

- **Before `grhh`**: This command discards ALL local changes permanently. Make sure you really want to lose your work!

- **`gplr` advantage**: Using rebase during pull keeps your commit history linear and cleaner than merge commits.

- **`gwip` for experiments**: Great for saving experimental code quickly without thinking about the commit message.

---

## Complete Alias List

```bash
# Basic Operations
alias gs='git status'
alias ga='git add'
alias gaa='git add .'
alias gc='git commit'
alias gcm='git commit -m'
alias gca='git commit --amend'

# Push/Pull
alias gp='git push'
alias gpf='git push --force-with-lease'
alias gpl='git pull'
alias gplr='git pull --rebase'

# Branches
alias gco='git checkout'
alias gcob='git checkout -b'
alias gb='git branch'
alias gbd='git branch -d'

# Merge/Rebase
alias gm='git merge'
alias gr='git rebase'
alias gri='git rebase -i'
alias grc='git rebase --continue'
alias gra='git rebase --abort'

# Diff/Log
alias gd='git diff'
alias gdc='git diff --cached'
alias gl='git log --oneline --graph --decorate'
alias gla='git log --oneline --graph --decorate --all'
alias glg='git log --graph --pretty=format:"%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset" --abbrev-commit'
alias glga='git log --graph --pretty=format:"%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset" --abbrev-commit --all'

# Stash
alias gst='git stash'
alias gstp='git stash pop'
alias gstl='git stash list'

# Reset/Clean
alias gf='git fetch'
alias grh='git reset HEAD'
alias grhh='git reset --hard HEAD'
alias gclean='git clean -fd'

# Utilities
alias gundo='git reset --soft HEAD~1'
alias gwip='git add . && git commit -m "WIP"'
alias gunwip='git log -n 1 | grep -q -c "WIP" && git reset HEAD~1'
```

---

## Customization

Feel free to modify these aliases in your `~/.zshrc` file to match your personal preferences. You can:

- Change alias names to your preferred shortcuts
- Add additional parameters to commands
- Create new aliases for your specific workflows
- Combine multiple commands into custom aliases

After making changes, remember to reload your configuration:
```bash
source ~/.zshrc
```

Happy coding! 🚀
