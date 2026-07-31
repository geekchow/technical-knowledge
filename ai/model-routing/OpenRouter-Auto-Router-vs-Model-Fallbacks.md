---
title: "Claude Conversation"
source: "https://claude.ai/share/3ad3e85d-7770-42cb-9b26-1fec910656d6"
author:
published:
created: 2026-04-26
description: "Claude conversation with 2 messages"
tags:
  - "clippings"
---

# OpenRouter Auto Router vs Model Fallbacks

**You**

read the docs of openrouter [https://openrouter.ai/docs/guides/routing/routers/auto-router](https://openrouter.ai/docs/guides/routing/routers/auto-router) [https://openrouter.ai/docs/guides/routing/model-fallbacks](https://openrouter.ai/docs/guides/routing/model-fallbacks)

comparing the auto-router & fallback mechanism and give curl exmple. just plain markdown is enough do not need html

---

**Claude**

## OpenRouter: Auto Router vs Model Fallbacks

---

### Core Philosophy

| Dimension | Auto Router (`openrouter/auto`) | Model Fallbacks (`models` array) |
| --- | --- | --- |
| **Purpose** | Proactive intelligent selection | Reactive failover / resilience |
| **Decision timing** | Before request is sent | Only when an error occurs |
| **Who chooses** | NotDiamond routing AI | You define the priority list |
| **Control** | Low (you can constrain, not dictate) | High (you specify exact ordered list) |
| **Primary goal** | Quality / cost optimization | Availability / reliability |

---

### Auto Router

You set `model` to the special alias `openrouter/auto`. OpenRouter's routing engine (powered by **NotDiamond**) analyzes your prompt and picks the best model from a curated pool — currently top models from Anthropic, OpenAI, Google, DeepSeek, etc.

**Key points:**

- You always pay the rate of whichever model was actually selected — no surcharge for routing.
- The response body tells you which model ran via the `model` field.
- You can restrict the candidate pool via the `plugins.allowed_models` list with wildcard patterns (`anthropic/*`, `openai/gpt-5*`, etc.).
- Streaming and tool-calling are fully supported.

```bash
# Basic Auto Router call
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "openrouter/auto",
    "messages": [
      { "role": "user", "content": "Explain quantum entanglement in simple terms" }
    ]
  }'
```

```bash
# Auto Router with restricted model pool (only Anthropic + GPT-5.1)
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "openrouter/auto",
    "messages": [
      { "role": "user", "content": "Analyze this Java stack trace for memory leaks" }
    ],
    "plugins": [
      {
        "id": "auto-router",
        "allowed_models": ["anthropic/*", "openai/gpt-5.1"]
      }
    ]
  }'
```

**Response** — note the `model` field reveals the actual model chosen:

```json
{
  "id": "gen-...",
  "model": "anthropic/claude-sonnet-4.5",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "..."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 150,
    "total_tokens": 165
  }
}
```

---

### Model Fallbacks

You provide a `models` array (instead of a single `model`). OpenRouter tries them in order — the next one is only invoked if the previous one fails. Failure triggers include:

- Provider downtime
- Rate limiting
- Context length exceeded
- Content moderation refusal

**Key points:**

- Entirely **reactive** — the first model runs normally; fallbacks only activate on error.
- You are in full control of the priority order.
- Priced at the rate of whichever model actually responded (shown in response `model` field).
- If all models in the list fail, OpenRouter returns the last error.

```bash
# Basic fallback: try Claude first, fall back to MythoMax
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "models": [
      "anthropic/claude-3.5-sonnet",
      "gryphe/mythomax-l2-13b"
    ],
    "messages": [
      { "role": "user", "content": "What is the meaning of life?" }
    ]
  }'
```

```bash
# Production-grade chain: premium → mid-tier → cheap fallback
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "models": [
      "openai/gpt-4o",
      "anthropic/claude-3.5-sonnet",
      "google/gemini-flash-1.5",
      "gryphe/mythomax-l2-13b"
    ],
    "messages": [
      { "role": "user", "content": "Summarize the BASEL III capital adequacy requirements" }
    ]
  }'
```

```bash
# Using fallbacks via OpenAI-compatible SDK (extra_body trick)
# model= is attempted first, then the models[] array is tried in order
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "openai/gpt-4o",
    "extra_body": {
      "models": ["anthropic/claude-3.5-sonnet", "gryphe/mythomax-l2-13b"]
    },
    "messages": [
      { "role": "user", "content": "What is the meaning of life?" }
    ]
  }'
```

---

### Side-by-side Comparison

|  | Auto Router | Model Fallbacks |
| --- | --- | --- |
| **API param** | `"model": "openrouter/auto"` | `"models": ["a", "b", "c"]` |
| **Selection logic** | NotDiamond AI (prompt-aware) | Your explicit ordered list |
| **Trigger** | Every request | Only on error of prior model |
| **Control granularity** | Constrain via `plugins.allowed_models` | Full — you pick exactly which models |
| **Latency impact** | Slight overhead for routing analysis | None until a failure occurs |
| **Best for** | Unknown/diverse prompt types, cost-quality balancing | SLA/reliability, known prod workloads |
| **Transparency** | Response `model` field shows winner | Response `model` field shows who answered |
| **Streaming support** | ✅ | ✅ |
| **Tool calling** | ✅ | ✅ |
| **Extra cost** | None (pay selected model's rate) | None (pay responding model's rate) |

---

### When to Use Which

**Use Auto Router when:**

- You have a general-purpose app with varied user prompts (e.g. a chatbot, RAG pipeline with diverse queries).
- You want automatic cost-vs-quality tradeoffs without maintaining a routing layer yourself.
- You're experimenting and want to discover which models suit your workload.

**Use Model Fallbacks when:**

- You have a known, latency-sensitive production workload where the primary model is well-suited.
- You need guaranteed availability / SLA (common in banking IT).
- You want deterministic behavior on the happy path with safety nets only on failure.

**Combine both** — use `openrouter/auto` as the primary in a fallback chain if you want intelligent selection with a hard backstop:

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "models": [
      "openrouter/auto",
      "google/gemini-flash-1.5"
    ],
    "messages": [
      { "role": "user", "content": "Detect anomalies in this transaction log" }
    ]
  }'
```

This gives you smart routing on the happy path, with a cheap hard fallback if the auto-router itself fails.
