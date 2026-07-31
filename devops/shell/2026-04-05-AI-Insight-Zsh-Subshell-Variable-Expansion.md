---
Source-AI: ChatGPT
Category: Technical
Time-Context: Coding Session
Topics: [Zsh, Shell Scripting, Environment Variables, Subshell, Quoting]
tags:
  - ai-distilled
---

# Zsh Subshell Variable Expansion

## Summary
Phil's `zsh -lc` command wasn't expanding `$LOCAL_UPSTREAM_KEY` due to a combination of single-quote isolation, a non-exported variable, and subshell environment boundary issues.

## Key Takeaway
Single quotes in `zsh -lc '...'` completely disable variable expansion at the outer shell level — the variable must already be exported and present in the subshell's environment. The cleanest fix is to avoid the subshell entirely.

## Key Insights
- **Single quotes kill outer expansion** — `'${VAR}'` inside `zsh -lc '...'` passes the literal string `${VAR}` to the subshell; expansion only happens if the variable exists inside that subshell.
- **Unexported variables don't cross subshell boundaries** — `VAR=value` (without `export`) is shell-local; child shells never see it. Always use `export VAR=value` in `.zprofile`/`.zshrc` for variables intended to be available everywhere.
- **`zsh -lc` is login but not fully interactive** — `.zprofile` is loaded but `.zshrc` behaviour can differ, so sourcing it manually inside `-lc` is not always reliable.
- The quickest diagnostic is `zsh -lc 'echo $VAR'` — if empty, the variable is not exported or not loaded in the subshell.

## Technical Details

### Quick diagnostic

```bash
zsh -lc 'echo $LOCAL_UPSTREAM_KEY'
# If empty → not exported / not loaded in subshell
```

### Fix options (in order of preference)

**Option 3 — Avoid subshell entirely (recommended)**
```bash
AUTH="Authorization: Bearer ${LOCAL_UPSTREAM_KEY}"
curl https://deeprouter.top/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{ "model": "gpt-4o-mini", "messages": [{"role": "user", "content": "who are you?"}], "temperature": 0.7 }' | jq
```

**Option 1 — Export the variable properly**
```bash
# In ~/.zprofile or ~/.zshrc:
export LOCAL_UPSTREAM_KEY="your_key"
# Then the original command works as-is
```

**Option 2 — Pass env explicitly to the subshell**
```bash
LOCAL_UPSTREAM_KEY=your_key zsh -lc '
AUTH="Authorization: Bearer ${LOCAL_UPSTREAM_KEY}"
curl https://deeprouter.top/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d "{ \"model\": \"gpt-4o-mini\", ... }" | jq
'
```

**Option 4 — Use double quotes (expansion in outer shell)**
```bash
zsh -lc "source ~/.zprofile; AUTH=\"Authorization: Bearer ${LOCAL_UPSTREAM_KEY}\"; curl ..."
# Expansion happens in the outer shell — inner \$AUTH is then a literal reference
```

### Root cause summary

| Issue | Cause |
|---|---|
| Single-quote isolation | `'...'` passes `${VAR}` literally — outer shell never expands it |
| Non-exported variable | `VAR=x` without `export` — invisible to subshells |
| Subshell env boundary | `zsh -lc` creates a new process; parent env only crosses if exported |

## Related Topics
Zsh Shell Quoting Rules
Shell Variable Export and Scope
Subshell Environment Inheritance
Shell Scripting Best Practices
