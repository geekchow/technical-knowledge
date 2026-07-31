# 07 · 下一步：动手验证与延伸阅读

> **你在哪里**：指南结束后的出口。这里是把纸面理解变成手感的练习，和继续深入的路标。

## 动手练习（按顺序，每个都在验证一个深潜）

1. **验证推理引擎（深潜 2）**：`ollama run llama3.2` 跑一个小模型，观察首字延迟（prefill）和逐字速度（decode）；把 prompt 加长十倍，感受 TTFT 的变化；
2. **验证参数规模（深潜 3）**：同一问题分别问 1B、8B 模型（`ollama run llama3.2:1b` vs `llama3.1:8b`），用"写代码+解释原理"类复合问题，亲眼看能力阶梯；再看两个模型文件的体积，对照 参数量 × 字节数 的公式；
3. **验证量化（深潜 3）**：对比同一模型的 q4 与 q8 版本的体积、速度与回答质量，体会"精度换显存"的交易；
4. **验证开源定制权（深潜 4）**：在 HuggingFace 上找一个 LoRA 微调教程，用 100 条自己领域的数据微调一个小模型——这是闭源路线给不了的体验；
5. **验证基座 vs 对话模型（深潜 1）**：找一个 base 模型（如 `llama3.1:8b-text`）问它问题，观察它"续写而不回答"的行为——SFT 的价值瞬间具象化。

## 延伸阅读

**本仓库博客系列**（与本指南同源，推理侧的展开）：
1. [一次 LLM 推理的完整旅程](../llm-inference/llm-inference-process.zh.md) —— prefill/decode 与计费的物理解释
2. [KV Cache 完全解析](../llm-inference/kv-cache.zh.md) —— 显存账与优化生态
3. [Chat vs Agentic](../llm-inference/chat-vs-agentic.zh.md) —— 使用范式如何改写推理经济学
4. [GPU 负责想，CPU 负责做](../llm-inference/agentic-cpu-demand.zh.md) —— Agentic 时代的算力结构

**外部资源**：
- Karpathy《Let's build GPT》/《Intro to LLMs》—— 从零手写，训练侧最好的直觉来源
- 《Scaling Laws for Neural Language Models》(Kaplan 2020) 与《Training Compute-Optimal LLMs》(Chinchilla 2022) —— 深潜 3 的原始出处
- Llama 3 / DeepSeek-V3 / DeepSeek-R1 技术报告 —— 开源阵营最透明的三份"训练管线实录"
- HuggingFace Open LLM Leaderboard —— 追踪开源前沿（记住深潜 3 的跑分警告）

## 一张卡片带走全部

| 问题 | 一句话答案 |
|---|---|
| 训练 vs 推理？ | 写入 vs 读取：训练把数据压进权重（一次、极贵），推理只读权重生成回答（无限次、逐 token） |
| 开源 vs 闭源？ | 同一份权重的两种交付：公开下载（控制权归你）vs API 出租（frontier 能力+零运维）；技术栈相同，合约不同 |
| 参数规模为什么重要？ | 它同时决定能力上限（Scaling Law/涌现）、显存门槛（参数×字节数）、单 token 成本（decode 读全部权重）——一个数字，三重命运 |

返回 [总览](00-overview.md)
