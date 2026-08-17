# LLM 推理系列 / LLM Inference Series

[← Back to AI](../README.md)

Publish-ready article pairs, each extended from a study note in the repo-root [`raw/`](../../raw/README.md)
directory. Every topic has a parallel Chinese (`.zh.md`) and English (`.en.md`) version — the English
one is a parallel rewrite, not a literal translation.

Foundations for this series live in the sibling topic [LLM 全景指南](../llm-fundamentals/index.md).

## Articles & CSDN Publish Status

### 一次 LLM 推理的完整旅程 / The Full Journey of an LLM Inference Request

Prefill vs decode, TTFT/TPOT, continuous batching, and why API pricing works the way it does. (Source: [`raw/reasoning-process.md`](../../raw/reasoning-process.md))

- [x] [llm-inference-process.zh.md](llm-inference-process.zh.md) — 中文版
- [x] [llm-inference-process.en.md](llm-inference-process.en.md) — English

### KV Cache 完全解析 / KV Cache Explained

Q/K/V fundamentals, why only K/V is cached, the memory math, and the optimization ecosystem (PagedAttention, GQA/MLA, prefix caching). (Source: [`raw/KV-Cache.md`](../../raw/KV-Cache.md))

- [x] [kv-cache.zh.md](kv-cache.zh.md) — 中文版
- [x] [kv-cache.en.md](kv-cache.en.md) — English

### Chat 阶段 vs Agentic 阶段 / Chat vs. Agentic

How the agentic paradigm rewrites inference economics: human out of the loop, input-dominated costs, prefix caching as a lifeline, and the multi-step reliability threshold. (Source: [`raw/chat-vs-agentic.md`](../../raw/chat-vs-agentic.md))

- [x] [chat-vs-agentic.zh.md](chat-vs-agentic.zh.md) — 中文版
- [x] [chat-vs-agentic.en.md](chat-vs-agentic.en.md) — English

### GPU 负责想，CPU 负责做 / GPUs Think, CPUs Do

Why agentic AI sends CPU demand soaring: tool execution, resident sandboxes, inference-pipeline overhead, and task volume decoupled from headcount. (Source: [`raw/agentic-cpu-demand.md`](../../raw/agentic-cpu-demand.md))

- [x] [agentic-cpu-demand.zh.md](agentic-cpu-demand.zh.md) — 中文版
- [x] [agentic-cpu-demand.en.md](agentic-cpu-demand.en.md) — English

### 会续写 ≠ 会帮忙 / Completing Text ≠ Being Helpful

Why and how post-training matters: base model vs assistant, SFT/RLHF/DPO/RLVR as four generations of tools, and why post-training decides usability, differentiation, and failure modes. (Source: [`raw/base-model-vs-assistant.md`](../../raw/base-model-vs-assistant.md))

- [x] [post-training.zh.md](post-training.zh.md) — 中文版
- [ ] [post-training.en.md](post-training.en.md) — English

### FP16 与 INT4 量化 / FP16 and INT4 Quantization

How parameters are stored: floating-point formats, group-wise INT4 quantization mechanics, why 1/4 precision still works, and the memory + speed double win. (Source: [`raw/fp16-int4-quantization.md`](../../raw/fp16-int4-quantization.md))

- [x] [fp16-int4-quantization.zh.md](fp16-int4-quantization.zh.md) — 中文版
- [ ] [fp16-int4-quantization.en.md](fp16-int4-quantization.en.md) — English

---

*Check the box once the article is published to CSDN. Recommended reading order: inference process → KV Cache → Chat vs. Agentic → CPU demand → post-training → quantization.*
