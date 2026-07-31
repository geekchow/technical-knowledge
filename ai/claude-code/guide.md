# Using Claude Code Efficiently

## Core Workflow Tips

**Be specific with context**
- Tell Claude *what* and *why*, not just what to do
- Reference specific files/functions: "fix the bug in `auth.ts:42`"
- Share error messages, not just "it doesn't work"

**Leverage parallel operations**
- Claude can read multiple files, run searches simultaneously
- Ask for multiple related things at once instead of one at a time

## Key Commands

| Command | Purpose |
|---|---|
| `/compact` | Compress conversation to free context |
| `/clear` | Start fresh context |
| `/cost` | Check token usage |
| `/fast` | Toggle faster output mode |
| `#` | Add instructions to memory (CLAUDE.md) |

## Effective Prompting

**Give Claude the right scope**
```
# Too vague
"Fix the login"

# Better
"Users get a 401 error when logging in with Google OAuth. 
Check the callback handler in src/auth/"
```

**Use plan mode for complex tasks**
- Say "plan first, don't make changes" before large refactors
- Review the plan, then say "proceed"

## Project Setup

**Create a `CLAUDE.md`** in your project root:
```markdown
# Project conventions
- Use bun, not npm
- Run tests with: bun test
- Code style: no semicolons
```
Claude reads this automatically on every session.

## Context Management

- Keep conversations focused — start new sessions for unrelated tasks
- Use `/compact` when context gets large rather than starting over
- Reference specific line numbers to avoid Claude reading unnecessary files

## Power Features

- **Multi-file edits**: Claude handles diffs atomically across files
- **Git integration**: Ask Claude to commit, create PRs, or explain diffs
- **Test-driven**: Ask Claude to write tests first, then implement
- **Explain before change**: "Explain what this function does, then refactor it"

## What Claude Does Best

- Refactoring with clear before/after intent
- Debugging with full error context provided
- Boilerplate generation (tests, configs, types)
- Code review and identifying issues

## Common Pitfalls

- Don't ask Claude to guess at requirements — be explicit
- Don't chain too many unrelated changes in one session
- If Claude is going in the wrong direction, stop early and redirect rather than letting it compound