Good question — OpenClaw burns tokens even when idle by design, and the causes are pretty well understood. Here's what's happening and how to fix it.

**Why it costs so much when you're not doing anything:**

The biggest culprit is the heartbeat. OpenClaw's heartbeat subsystem wakes the agent at configurable intervals (default 30 min) to execute autonomous cycles, and heartbeats run full model turns, so shorter intervals scale cost quickly. Each wake-up isn't cheap either — every heartbeat trigger is a full API call carrying the complete session context. One user's automated email check, set to run every 5 minutes, burned through $50 in a single day.

On top of that, each conversation must reload configuration files, memory data, and full conversation context, causing token usage to accumulate rapidly even for seemingly simple operations. The system prompt alone bundles a lot: workspace and bootstrap files like AGENTS.md, SOUL.md, TOOLS.md, IDENTITY.md, USER.md, and HEARTBEAT.md are assembled on every run, plus JSON tool schemas also count toward the context budget. And context accumulation is the number one cost driver, responsible for 40-50% of typical token usage — all historical messages get re-sent with every request.

**Mitigations, roughly in order of impact:**

1. **Diagnose first.** Run `/context list` or `/context detail` for a practical breakdown per injected file, tools, skills, and system prompt size, and use `/status` or `/usage full` to see token usage and estimated cost per response.

2. **Tame the heartbeat.** Extend the interval to 30–60 minutes if you're only checking things a few times a day, or disable it entirely with `openclaw config set heartbeat.enabled false` when you're away. Also note that heartbeats are skipped before the model call when HEARTBEAT.md is effectively empty — so keep it minimal if you don't need proactive behavior.

3. **Route cheap tasks to cheap models.** Operators who move heartbeats and cron jobs to cheap or local models while reserving premium models for sessions that need them consistently report 80–95% cost reduction. Don't let Opus-class models handle status checks.

4. **Start new sessions per task and prune context.** The simplest way to save is to start a new chat for different tasks, since input tokens dominate cost. You can also set `contextTokens` to limit context size, use the compact feature to compress history, and clear irrelevant tool-call outputs after each sub-task.

5. **Exploit prompt caching.** If your model's cache TTL is 1h, setting the heartbeat just under it (e.g., 55m) keeps the cache warm so you avoid re-caching the full prompt, and cache-ttl pruning trims the session once the TTL expires so subsequent requests reuse freshly cached context.

6. **Trim the bootstrap files and skills.** Keep SOUL.md/AGENTS.md/MEMORY.md lean and disable skills you don't use — every enabled skill consumes tokens on every call.

7. **Set spending guardrails.** OpenClaw has no native hard dollar cap, so set per-task token budgets, disable re-reasoning on failure, and use daily spend caps at the provider level (Anthropic, OpenAI, OpenRouter all support these). Also clean up orphaned subagents with explicit cleanup settings, since they can keep running in the background after their parent task ends.

One security-related caveat worth knowing: idle burn isn't always just misconfiguration. Researchers have shown trojanized third-party skills can induce 6–9× token amplification in production OpenClaw instances, so be picky about which community skills you install.

If you tell me what your setup looks like (heartbeat interval, model, whether you run long-lived sessions), I can suggest a more specific config.