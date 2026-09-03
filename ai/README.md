# AI

LLM fundamentals and inference, agent harness, Claude Code, prompting, agents, model routing.

[← Back to index](../README.md)

**Agents**

- [AI Agent 记忆的 6 个层级：从 CLAUDE.md 到「统一大脑」](agents/ai-agent-memory-6-levels.md)
- [Build an AI Assistant with LangGraph, Vercel, and Next.js: Use Gmail as a Tool Securely](agents/Build-an-AI-Assistant-with-LangGraph-Vercel-and-Next.js-Use-Gmail-as-a-Tool-Securely.md)

**Claude Code**

- [Claude Code Deep Dive (pdf)](claude-code/claude-code-deep-dive-xelatex.pdf)
- [Claude Code 安装指南](claude-code/claude-code.md)
- [claude skill](claude-code/claude-skill.md)
- [Using Claude Code Efficiently](claude-code/guide.md)
- [iOS UI design for AI-powered dictionary app](claude-code/iOS-UI-design-for-AI-powered-dictionary-app.md)
- [One Layer vs Two Layers: Claude Skill Structure](claude-code/One-layer-vs-two-layers-skill.md)
- [skill](claude-code/skill.md)
- [Claude Skills Marketplace](claude-code/skills-marketplace.md)

**Concepts**

- [AI 核心概念梳理：LLM / Prompt / Agent / RAG / MCP / Skill / Context / Harness](concepts/AI核心概念梳理-LLM-Prompt-Agent-RAG-MCP-Skill-Context-Harness.md)
- [LLM 量化版本 是什么版本](concepts/LLM-量化版本-是什么版本.md)
- [为什么大量公司上了 RAG，却很少真正做成？](concepts/why-rag-projects-fail.zh.md) · [Why So Many Companies Adopt RAG, and So Few Actually Succeed](concepts/why-rag-projects-fail.en.md)

**DeepSeek Harness** — 十二篇中文系列，见 [series index](deepseek-harness/index.md)

- [01 · 为什么需要 harness：模型再强，也不会自己去读文件](deepseek-harness/01-why.zh.md)
- [02 · DeepSeek Harness 是什么：定义、边界与生态位置](deepseek-harness/02-what.zh.md)
- [03 · 概念地图：八个概念、八个角色、一个运行示例](deepseek-harness/03-concept-map.zh.md)
- [04 · Cordis 内核：为什么「一切皆插件」不是口号](deepseek-harness/04-cordis.zh.md)
- [05 · 组装层：Profile、Bundle、Patch 与 Agent Preset](deepseek-harness/05-composition.zh.md)
- [06 · 会话日志：唯一真相源，以及「模型可见即已记录」](deepseek-harness/06-session-log.zh.md)
- [07 · Agent Loop：一个 turn 到底发生了什么](deepseek-harness/07-agent-loop.zh.md)
- [08 · 系统提示装配：模型看见的前缀是被「拼」出来的](deepseek-harness/08-system-prompt.zh.md)
- [09 · LLM 接缝：把厂商协议关进一个可替换的盒子](deepseek-harness/09-llm-adapter.zh.md)
- [10 · 工具注册表与执行管线：一次工具调用要过五道关](deepseek-harness/10-tools.zh.md)
- [11 · 能力接缝：文件、命令、沙箱、审批、子代理](deepseek-harness/11-capability-seams.zh.md)
- [12 · 完整重演：一句话请求的完整旅程 + 动手练习](deepseek-harness/12-walkthrough.zh.md)
**LLM Fundamentals** — 十三篇中文系列，见 [series index](llm-fundamentals/index.md)

- [01 · 为什么会有 LLM：一个任务一个模型的时代是怎么结束的](llm-fundamentals/01-why.zh.md)
- [02 · LLM 到底是什么：定义、边界与生态位置](llm-fundamentals/02-what.zh.md)
- [03 · 七个核心概念：一次摊开整张地图](llm-fundamentals/03-core-concepts.zh.md)
- [04 · Transformer 内部构造：那几十亿个参数到底排成什么样](llm-fundamentals/04-transformer.zh.md)
- [05 · Tokenizer：模型眼里的世界不是文字](llm-fundamentals/05-tokenizer.zh.md)
- [06 · 训练管线：数据如何变成权重](llm-fundamentals/06-training-pipeline.zh.md)
- [07 · 后训练细拆：SFT、RLHF、DPO、RLVR 四代工具](llm-fundamentals/07-post-training.zh.md)
- [08 · 推理引擎：权重如何被读取](llm-fundamentals/08-inference-engine.zh.md)
- [09 · 参数规模与 Scaling Law：7B、70B、670B 为什么如此重要](llm-fundamentals/09-param-scale.zh.md)
- [10 · 上下文窗口：128K 到底意味着什么](llm-fundamentals/10-context-window.zh.md)
- [11 · 幻觉的机制：为什么它编得如此流畅](llm-fundamentals/11-hallucination.zh.md)
- [12 · 开源 vs 闭源：同一份权重，两种交付](llm-fundamentals/12-open-vs-closed.zh.md)
- [13 · 完整重演：带着全部深度重跑运行示例](llm-fundamentals/13-walkthrough.zh.md)

**LLM Inference** — 中英双语文章系列，见 [series index](llm-inference/index.md)

- [一次 LLM 推理的完整旅程](llm-inference/llm-inference-process.zh.md) · [The Full Journey of an LLM Inference Request](llm-inference/llm-inference-process.en.md)
- [KV Cache 完全解析](llm-inference/kv-cache.zh.md) · [KV Cache Explained](llm-inference/kv-cache.en.md)
- [Chat 阶段 vs Agentic 阶段](llm-inference/chat-vs-agentic.zh.md) · [Chat vs. Agentic](llm-inference/chat-vs-agentic.en.md)
- [GPU 负责想，CPU 负责做](llm-inference/agentic-cpu-demand.zh.md) · [GPUs Think, CPUs Do](llm-inference/agentic-cpu-demand.en.md)
- [会续写 ≠ 会帮忙：后训练](llm-inference/post-training.zh.md) · [Completing Text ≠ Being Helpful](llm-inference/post-training.en.md)
- [FP16 与 INT4 量化](llm-inference/fp16-int4-quantization.zh.md) · [FP16 and INT4 Quantization](llm-inference/fp16-int4-quantization.en.md)

**Model Routing**

- [How to user deeprouter api](model-routing/deeprouter.md)
- [OpenRouter Auto Router vs Model Fallbacks](model-routing/OpenRouter-Auto-Router-vs-Model-Fallbacks.md)
- [OpenRouter](model-routing/openrouter.md)

**Multimodal** — 十篇中文系列，见 [series index](multimodal/index.md)

- [01 · 为什么需要多模态：纯文本 LLM 撞上的四堵墙](multimodal/01-why.zh.md)
- [02 · 多模态 LLM 是什么：定义、边界与生态位置](multimodal/02-what.zh.md)
- [03 · 概念地图：七个概念、五个角色、一个运行示例](multimodal/03-concept-map.zh.md)
- [04 · 视觉编码器：像素如何变成语义](multimodal/04-vision-encoder.zh.md)
- [05 · 对齐投影器：最小也最关键的模块](multimodal/05-projector.zh.md)
- [06 · LLM 主干与融合策略：前缀拼接 vs 交叉注意力](multimodal/06-llm-backbone-fusion.zh.md)
- [07 · 训练管线：三阶段如何把三个模块焊在一起](multimodal/07-training-pipeline.zh.md)
- [08 · 模态解码器与 Any-to-Any](multimodal/08-any-to-any.zh.md)
- [09 · 完整重演：一张截图的完整旅程 + 动手练习](multimodal/09-walkthrough.zh.md)

**OpenClaw**

- [openclaw token](openclaw/openclaw-token.md)
- [setup](openclaw/setup.md)

**Prompting**

- [Cognitive Mental Model — Learning New Systems in Software Engineering](prompting/cogntive-skill.md)
- [如何用 AI 整理自己的思路](prompting/how-to-use-ai.md)
- [ChatGPT is the world's best money maker.](prompting/Make-Money.md)
- [Prompts for AI](prompting/prompt.md)
- [ChatGPT is FREE education.](prompting/Study.md)

**Resources**

- [RSS](resources/RSS.md)

**Superpowers**

- [Superpowers — What It Does & How It Orchestrates Skills](superpowers/superpowers-overview.md)
- [Why superpowers](superpowers/why-superpowers.md)

**Transformer & Attention** — 十二篇中文系列，见 [series index](transformer/index.md)

- [01 · 为什么会有 Transformer：一句话必须一个词一个词地读，是怎么被打破的](transformer/01-why.zh.md)
- [02 · Transformer 到底是什么：定义、边界与生态位置](transformer/02-what.zh.md)
- [03 · 概念地图：八个概念、五个角色，一次摊开整张地图](transformer/03-concept-map.zh.md)
- [04 · 运行示例：一句话的完整旅程（浅层追踪）](transformer/04-running-example.zh.md)
- [05 · 嵌入层与位置编码器：从整数到「带位置感的向量」](transformer/05-embedding-position.zh.md)
- [06 · 注意力核心：QKV 与缩放点积](transformer/06-attention-core.zh.md)
- [07 · 多头与因果掩码：并行的多种关系，与不许偷看的铁律](transformer/07-multi-head-mask.zh.md)
- [08 · 工程变体：KV Cache、GQA/MQA/MLA 与 FlashAttention](transformer/08-attention-variants.zh.md)
- [09 · 前馈网络 FFN：那七成参数在干什么](transformer/09-ffn.zh.md)
- [10 · 残差与归一化：让 32 层不至于崩掉的那些胶水](transformer/10-residual-norm.zh.md)
- [11 · 输出头与采样器：从 4096 个数到一个汉字](transformer/11-output-head.zh.md)
- [12 · 完整重演：一句话如何变成「猫」+ 动手练习](transformer/12-walkthrough.zh.md)

**General**

- [AI](README.md)
