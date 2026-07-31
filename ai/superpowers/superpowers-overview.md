---
title: "Superpowers — What It Does & How It Orchestrates Skills"
date: 2026-06-11
tags: [AI, Agents, Claude Code, Superpowers]
---

# Superpowers — What It Does & How It Orchestrates Skills

## 1. What this repo is

**Superpowers is a complete software-development methodology for coding agents**, packaged as a
zero-dependency plugin. It is *not* application code — it ships a library of **skills** (markdown
playbooks) plus a single **session-start hook** that bootstraps the agent into using them.

The core idea: when you tell your agent "let's build X", it shouldn't jump straight to writing code.
Instead it should step back, brainstorm a spec, write a plan, execute the plan task-by-task with
fresh subagents and review gates, then verify and integrate. Superpowers encodes that whole loop as
auto-triggering skills so you get the discipline "for free".

It targets many harnesses from one source: Claude Code, Codex CLI/App, Factory Droid, Gemini CLI,
OpenCode, Cursor, GitHub Copilot CLI (see `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`,
`.opencode/`, `gemini-extension.json`).

## 2. The building blocks

| Component | Location | Role |
|-----------|----------|------|
| **Skills** | `skills/*/SKILL.md` | One folder per skill. Frontmatter (`name` + `description`) tells the agent *when* to invoke; body tells it *how* to act. |
| **Session-start hook** | `hooks/session-start` + `hooks/hooks.json` | Injects the `using-superpowers` skill into context at session start so skills auto-trigger. |
| **Cross-platform wrapper** | `hooks/run-hook.cmd` | Polyglot bat/bash script so the hook runs on Windows and Unix. |
| **Support files** | `skills/*/*.md`, `scripts/`, `*-prompt.md` | Subagent prompts, reviewer prompts, examples, helper scripts referenced by skills. |
| **Plugin manifests** | `.*-plugin/`, `gemini-extension.json` | Register the plugin + hook with each harness. |

### The skill catalog

```
using-superpowers ............ Bootstrap: how to find & invoke every other skill
brainstorming ................ Idea → approved design spec (gate before any code)
writing-plans ................ Spec → bite-sized TDD implementation plan
subagent-driven-development .. Execute plan in-session via fresh subagent per task
executing-plans .............. Execute plan in a separate session (no-subagent fallback)
dispatching-parallel-agents .. Fan out 2+ independent tasks concurrently
test-driven-development ...... Red/green TDD discipline for each task
systematic-debugging ......... Root-cause-first bug investigation
requesting-code-review ....... Spawn reviewer subagent to check work
receiving-code-review ........ Evaluate review feedback with rigor, not blind agreement
verification-before-completion Run real verification before claiming "done"
finishing-a-development-branch Decide merge / PR / cleanup at the end
using-git-worktrees .......... Isolated workspace for feature work
writing-skills ............... Meta-skill: author & pressure-test new skills
```

## 3. How orchestration actually works

There is **no central scheduler**. Orchestration is *emergent* from three mechanisms:

1. **Bootstrap injection (the hook).** On `startup | clear | compact`, `hooks.json` runs
   `hooks/session-start`, which reads `skills/using-superpowers/SKILL.md`, JSON-escapes it, and emits
   it as `additionalContext` (with per-harness field names: `additional_context` for Cursor,
   `hookSpecificOutput.additionalContext` for Claude Code, top-level `additionalContext` for Copilot).
   This plants the rule: *"if there's even a 1% chance a skill applies, invoke it before responding."*

2. **Description-as-trigger.** Each skill's frontmatter `description` is a *when-to-use* sentence
   ("Use when encountering any bug…", "before any creative work…"). The agent pattern-matches the
   user's request against these descriptions and invokes the matching skill via the `Skill` tool.

3. **Skill-to-skill handoff.** Skill bodies explicitly name the next skill, forming a chain. E.g.
   brainstorming ends by invoking `writing-plans`; the plan header mandates
   `subagent-driven-development`; that skill calls `test-driven-development` and
   `requesting-code-review` per task; execution ends with `finishing-a-development-branch`.

### Bootstrap sequence

```mermaid
sequenceDiagram
    participant H as Harness (Claude Code / Codex / …)
    participant Hook as session-start hook
    participant A as Agent
    participant U as User

    H->>Hook: SessionStart (startup/clear/compact)
    Hook->>Hook: read using-superpowers/SKILL.md
    Hook->>Hook: JSON-escape + pick per-harness field
    Hook-->>A: inject as additionalContext
    Note over A: Now knows the "1% rule":<br/>invoke a skill before responding
    U->>A: "Let's build X"
    A->>A: match request to a skill description
    A->>A: invoke brainstorming (Skill tool)
    Note over A: handoff chain begins →
```

### The end-to-end development loop

```mermaid
flowchart TD
    Start([User: build a feature]) --> US[using-superpowers<br/>injected at session start]
    US --> BR[brainstorming<br/>explore intent → design spec]
    BR -->|HARD GATE: user approves design| WT[using-git-worktrees<br/>isolate workspace]
    WT --> WP[writing-plans<br/>spec → bite-sized TDD plan]
    WP --> EXEC{subagents<br/>available?}

    EXEC -->|yes, same session| SDD[subagent-driven-development]
    EXEC -->|no / separate session| EP[executing-plans]

    subgraph PerTask [Per task loop]
        direction TB
        IMPL[Dispatch implementer subagent] --> TDD[test-driven-development<br/>red → green → refactor]
        TDD --> SPEC[spec-compliance review subagent]
        SPEC --> QUAL[code-quality review subagent]
        QUAL --> DONE[mark task complete]
    end

    SDD --> PerTask
    EP --> PerTask
    PerTask -->|more tasks| PerTask

    PerTask --> RCR[requesting-code-review]
    RCR --> RECV[receiving-code-review<br/>evaluate feedback with rigor]
    RECV --> VER[verification-before-completion<br/>run real checks, evidence not claims]
    VER --> FIN[finishing-a-development-branch<br/>merge / PR / cleanup]
    FIN --> End([Integrated, verified work])

    DBG[systematic-debugging] -.invoked on any bug/test failure.-> PerTask
    PARA[dispatching-parallel-agents] -.fan out independent tasks.-> PerTask
```

### Decision logic baked into `using-superpowers`

```mermaid
flowchart TD
    Msg([User message received]) --> Maybe{Might any skill<br/>apply? even 1%}
    Maybe -->|definitely not| Respond([Respond / ask clarifications])
    Maybe -->|yes| Inv[Invoke Skill tool]
    Inv --> Ann["Announce: Using SKILL to PURPOSE"]
    Ann --> Chk{Skill has<br/>checklist?}
    Chk -->|yes| Todo[Create one TodoWrite item per step]
    Chk -->|no| Follow[Follow skill exactly]
    Todo --> Follow
    Follow --> Respond

    Plan{About to enter<br/>plan mode?} --> Bs{Already<br/>brainstormed?}
    Bs -->|no| BrainSkill[Invoke brainstorming first]
    Bs -->|yes| Maybe
    BrainSkill --> Maybe
```

## 4. Why it's built this way

- **Skills are code, not prose.** They shape agent behavior, so the repo treats wording (Red Flag
  tables, "your human partner" phrasing, rationalization lists) as carefully tuned and gated behind
  eval evidence (see `CLAUDE.md` and `writing-skills`).
- **Hard gates prevent premature coding.** `brainstorming` refuses to touch code until a design is
  approved — even for "trivial" projects.
- **Fresh subagent per task** keeps each task's context clean and preserves the orchestrator's
  context for coordination; two-stage review (spec → quality) catches drift.
- **Zero dependencies, multi-harness.** One skill library + one hook, re-targeted to every supported
  agent runner. New-harness support is judged by one acceptance test: does "Let's make a react todo
  list" auto-trigger `brainstorming`?

## 5. TL;DR

> A session-start hook injects one bootstrap skill that teaches the agent to auto-invoke skills.
> Each skill's `description` is its trigger; each skill's body hands off to the next. Together they
> form a disciplined loop — **brainstorm → plan → TDD execute with subagent review → verify →
> finish** — with debugging and parallelization woven in on demand. No orchestrator process; the
> orchestration *is* the skills calling each other.
