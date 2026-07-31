# AI 核心概念从头梳理

> **视频来源**：[AI的核心概念从头梳理 | LLM、Prompt、Agent、RAG、MCP、Skill、Context、Harness Engineering](https://www.bilibili.com/video/BV1wydDBDEuC)  
> **作者**：御豪同学 | **发布**：2026-04-22 | **时长**：49:08

---

## 一、核心框架：三层架构

理解所有 AI 概念的钥匙是 **"模型 + 工程 + 应用"** 三层架构：

```mermaid
graph LR
    subgraph APP["🖥️ 应用层（Application Layer）"]
        direction TB
        A1[AI 产品 / Copilot]
        A2[自动化系统]
        A3[智能助手]
        A1 ~~~ A2 ~~~ A3
    end
    subgraph ENG["⚙️ 工程层（Engineering Layer）"]
        direction TB
        E1[Prompt Engineering]
        E2[Context Engineering]
        E3[AI Agent]
        E4[RAG]
        E5[MCP / Tool]
        E6[Workflow]
        E7[Skill]
        E8[Harness Engineering]
        E1 ~~~ E2 ~~~ E3 ~~~ E4
        E5 ~~~ E6 ~~~ E7 ~~~ E8
    end
    subgraph MOD["🧠 模型层（Model Layer）"]
        direction TB
        M1[LLM 大语言模型]
        M2[Embedding Model]
        M3[Multimodal Model]
        M1 ~~~ M2 ~~~ M3
    end

    APP --> ENG
    ENG --> MOD

    style APP fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    style ENG fill:#dcfce7,stroke:#22c55e,color:#14532d
    style MOD fill:#fef9c3,stroke:#eab308,color:#713f12
```

---

## 二、大模型的本质：一个函数

```mermaid
flowchart LR
    C["📋 Context Window\n（System Prompt\n+ 历史对话\n+ 用户输入\n+ 工具返回\n+ RAG检索结果）"]
    F["🧠 LLM\nf(context)"]
    T["🔤 Next Token\n（循环输出）"]

    C -->|输入| F -->|输出| T
    T -->|追加到 Context| C

    style C fill:#fef3c7,stroke:#f59e0b,color:#1c1917
    style F fill:#e0e7ff,stroke:#6366f1,color:#1e1b4b
    style T fill:#dcfce7,stroke:#22c55e,color:#14532d
```

> **核心洞察**：模型本身无状态，所有"智能"体现都依赖 Context 的质量。

---

## 三、Prompt → Context Engineering 演进

```mermaid
graph LR
    P["Prompt\n基础输入"]
    PE["Prompt Engineering\n系统优化输入"]
    CE["Context Engineering\n管理整个上下文窗口"]
    HE["Harness Engineering\n构建可靠 Agent 系统"]

    P -->|"方法论化"| PE -->|"扩展范围"| CE -->|"工程化落地"| HE

    style P fill:#fee2e2,stroke:#ef4444,color:#7f1d1d
    style PE fill:#ffedd5,stroke:#f97316,color:#7c2d12
    style CE fill:#fef9c3,stroke:#eab308,color:#713f12
    style HE fill:#dcfce7,stroke:#22c55e,color:#14532d
```

---

## 四、AI Agent 架构（ReAct 循环）

```mermaid
sequenceDiagram
    actor User
    participant Agent
    participant LLM
    participant Tool
    participant Memory

    User->>Agent: 输入任务
    Agent->>Memory: 读取长期记忆（RAG）
    Agent->>LLM: 组装 Context，发起推理
    LLM-->>Agent: Thought + Action
    
    loop 执行循环
        Agent->>Tool: 调用工具（MCP/Function Call）
        Tool-->>Agent: Observation（工具返回）
        Agent->>Memory: 更新短期记忆（Context）
        Agent->>LLM: 继续推理
        LLM-->>Agent: 判断：继续行动 or 输出结果
    end

    Agent-->>User: 最终答案
```

---

## 五、Memory 体系：短期 vs 长期

```mermaid
graph TB
    subgraph ST["⚡ 短期记忆（Short-term Memory）"]
        CW["Context Window\n会话期间有效\n受 Token 限制"]
    end
    subgraph LT["🗄️ 长期记忆（Long-term Memory）= RAG"]
        KB["知识库 / 文档"]
        VDB["向量数据库\n（Embedding 存储）"]
        RET["检索器（Retriever）"]
    end

    Query["用户问题"] --> RET
    KB -->|"向量化"| VDB
    VDB --> RET
    RET -->|"注入 Context"| CW
    CW --> LLM["🧠 LLM"]

    style ST fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    style LT fill:#f3e8ff,stroke:#a855f7,color:#3b0764
```

---

## 六、RAG 完整工作流

```mermaid
flowchart LR
    subgraph INGEST["📥 离线索引阶段"]
        direction TB
        D1[原始文档]
        D2[文本切片 Chunking]
        D3[Embedding 向量化]
        D4[(向量数据库)]
        D1 --> D2 --> D3 --> D4
    end

    subgraph QUERY["🔍 在线检索阶段"]
        direction TB
        Q1[用户问题]
        Q2[问题向量化]
        Q3[相似度检索 Top-K]
        Q4[相关文档片段]
        Q1 --> Q2 --> Q3 --> Q4
    end

    subgraph GENERATE["💬 生成阶段"]
        direction TB
        G1["组装 Context\n(问题 + 检索结果 + System Prompt)"]
        G2[LLM 推理生成]
        G3[最终答案]
        G1 --> G2 --> G3
    end

    D4 -->|"向量检索"| Q3
    Q4 -->|"注入 Context"| G1

    style INGEST fill:#fef9c3,stroke:#eab308,color:#713f12
    style QUERY fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    style GENERATE fill:#dcfce7,stroke:#22c55e,color:#14532d
```

---

## 七、MCP 协议架构

```mermaid
graph LR
    subgraph AGENT["Agent 侧"]
        AC["MCP Client\n（内嵌于 Agent）"]
    end
    subgraph PROTO["标准协议层"]
        MP["MCP Protocol\nJSON-RPC over\nStdio / SSE / HTTP"]
    end
    subgraph SERVERS["工具服务侧"]
        S1["MCP Server\n文件系统"]
        S2["MCP Server\nWeb 搜索"]
        S3["MCP Server\n数据库"]
        S4["MCP Server\n自定义 API"]
    end

    AC <-->|"标准协议"| MP
    MP <-->|"统一接口"| S1
    MP <-->|"统一接口"| S2
    MP <-->|"统一接口"| S3
    MP <-->|"统一接口"| S4

    style AGENT fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    style PROTO fill:#fef9c3,stroke:#eab308,color:#713f12
    style SERVERS fill:#dcfce7,stroke:#22c55e,color:#14532d
```

> MCP 之于 AI 工具，就像 **USB 协议之于外设**：统一标准，即插即用。

---

## 八、Tool 调用机制

```mermaid
sequenceDiagram
    participant LLM
    participant Agent
    participant Tool as Tool/MCP Server

    LLM->>Agent: 输出 Function Call\n{name, arguments}
    Agent->>Tool: 执行工具调用
    Tool-->>Agent: 返回结果 Observation
    Agent->>LLM: 将 Observation 追加到 Context
    LLM->>Agent: 继续推理或给出最终答案
```

---

## 九、Skill 封装结构

```mermaid
graph TB
    SK["🎯 Skill（技能模块）"]
    SP["System Prompt\n角色定义 + 任务描述"]
    TL["Tools\n可用工具列表"]
    LG["Logic Flow\n内部逻辑/步骤"]
    EX["Examples\nFew-shot 示例"]
    CT["Context Rules\n上下文管理策略"]

    SK --> SP
    SK --> TL
    SK --> LG
    SK --> EX
    SK --> CT

    style SK fill:#e0e7ff,stroke:#6366f1,stroke-width:2px,color:#1e1b4b
```

---

## 十、Harness Engineering 体系

```mermaid
mindmap
  root((Harness\nEngineering))
    Eval 评估
      基准测试
      人工标注
      LLM-as-Judge
    Guardrail 护栏
      输入过滤
      输出约束
      安全边界
    Observability 可观测性
      Trace 追踪
      Log 日志
      Metrics 指标
    Testing 测试
      单元测试
      集成测试
      端到端测试
    Reliability 可靠性
      重试机制
      降级策略
      超时控制
```

---

## 十一、全局概念关系图

```mermaid
graph TD
    LLM["🧠 LLM\n大语言模型"]

    CTX["📋 Context Window\n上下文窗口"]
    PE["✍️ Prompt Engineering"]
    CE["🔧 Context Engineering"]

    MEM_S["⚡ 短期记忆\nContext 内"]
    MEM_L["🗄️ 长期记忆\nRAG"]

    TOOL["🔨 Tool\n工具调用"]
    MCP["🔌 MCP\n标准协议"]
    CLI["💻 CLI\n命令行替代"]

    WF["📊 Workflow\n固定流程"]
    AGENT["🤖 AI Agent\n自主决策"]
    SKILL["🎯 Skill\n能力封装"]

    HE["🛡️ Harness Engineering\n可靠性工程"]

    CTX -->|"输入给"| LLM
    PE -->|"优化"| CTX
    CE -->|"管理整个"| CTX

    MEM_S -->|"存在于"| CTX
    MEM_L -->|"RAG 检索注入"| CTX

    TOOL -->|"结果注入"| CTX
    MCP -->|"标准化"| TOOL
    CLI -->|"替代"| MCP

    LLM -->|"驱动"| WF
    LLM -->|"驱动"| AGENT

    AGENT -->|"使用"| TOOL
    AGENT -->|"使用"| MEM_S
    AGENT -->|"使用"| MEM_L
    SKILL -->|"封装"| AGENT

    HE -->|"保障"| AGENT

    style LLM fill:#fef9c3,stroke:#eab308,stroke-width:2px,color:#713f12
    style AGENT fill:#dbeafe,stroke:#3b82f6,stroke-width:2px,color:#1e3a5f
    style CTX fill:#fce7f3,stroke:#ec4899,stroke-width:2px,color:#831843
    style HE fill:#dcfce7,stroke:#22c55e,stroke-width:2px,color:#14532d
```

---

## 十二、关键结论

| 概念 | 所属层 | 核心作用 |
|------|--------|----------|
| LLM | 模型层 | 语言理解与生成的核心引擎 |
| Prompt Engineering | 工程层 | 优化单次输入质量 |
| Context Engineering | 工程层 | 管理整个上下文窗口的内容 |
| RAG | 工程层 | 为模型提供长期/外部知识 |
| Tool / MCP | 工程层 | 扩展模型与外部世界的交互 |
| AI Agent | 工程/应用层 | 自主规划和执行复杂任务 |
| Skill | 工程/应用层 | 将特定能力模块化封装复用 |
| Harness Engineering | 工程层 | 让 Agent 系统从能用变为可靠 |

**技术演进主线**：
```
Prompt → Prompt Engineering → Context Engineering → Harness Engineering
工具调用 → Function Calling → MCP（标准化协议）
单次对话 → Workflow（固定流程）→ Agent（动态决策）
```

---

*整理时间：2026-06-07*
