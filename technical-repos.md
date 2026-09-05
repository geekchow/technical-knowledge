# 技术讲解仓库链接索引 (Technical Explanation Repos)

本文件聚合所有**带讲解文章的独立仓库**（`runnable code + article pack` 的 companion repo）——
与 `technical-knowledge` 内按主题分类的单篇文章不同，这些仓库把「一篇成体系的中/英文章 + 可跑代码」
打包在同一个 repo 里。这里是它们各自的入口链接索引。

Each repo below carries a curated article/series **plus** runnable code, so it lives in its own
repository instead of inside this KB. This page is the pointer index into all of them.

| Repo | 主题 / Topic | 语言 | 文章入口 (index) | 代码 / Stack |
|---|---|---|---|---|
| [micro-service-auth](https://github.com/geekchow/micro-service-auth) | 微服务认证与授权 authn/authz（JWT / OIDC） | 中 / EN | `docs-zh/00-index.md` · `docs/00-index.md` | Keycloak → Kong → OPA → Spring Boot |
| [O11y-Micro-Service](https://github.com/geekchow/O11y-Micro-Service) | 微服务可观测性 Observability | EN | `blog/00-index.md` | OTel · Tempo · Prometheus · Loki · Grafana |
| [mcp-explain](https://github.com/geekchow/mcp-explain) | MCP（Model Context Protocol）学习指南 | 中 / EN | `mcp-guide-zh/00-overview.md` · `mcp-guide/00-overview.md` | 可运行 MCP server (orders-db) |
| [blue-green-eks-fargate-alb](https://github.com/geekchow/blue-green-eks-fargate-alb) | EKS Fargate 上蓝绿发布 | 中 / EN | `blog/blue-green-eks-fargate-alb.zh.md` · `.en.md` | Terraform + K8s ingress + ALB |

---

## 1. micro-service-auth — 微服务认证与授权

讲解并逐步演示微服务系统的认证与授权（authn/authz），配套一个 mobile-banking PoC：客户端经
`Keycloak`(IdP) 登录拿 JWT → `Kong`(网关/PEP) 内省令牌 → `OPA`(PDP) 决策 → `banking-api-service`
(资源服务器) 独立复验 JWT。14 篇结构：基础 → 组件深入 → 令牌机制 → 参考。

**GitHub:** <https://github.com/geekchow/micro-service-auth>

| 语言 | 索引入口 | 源码 |
|---|---|---|
| 中文（14 篇系列） | [`docs-zh/00-index.md`](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/00-index.md) | [`docs-zh/`](https://github.com/geekchow/micro-service-auth/tree/main/docs-zh) |
| English (14-part) | [`docs/00-index.md`](https://github.com/geekchow/micro-service-auth/blob/main/docs/00-index.md) | [`docs/`](https://github.com/geekchow/micro-service-auth/tree/main/docs) |

阅读地图（中文版）：
- **第一部分 基础** — [01 概念](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/01-concepts.md) · [02 项目架构](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/02-this-project-architecture.md) · [03 请求流程](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/03-request-flows.md) · [04 本地演示指南](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/04-local-demo-guide.md)
- **第二部分 组件深入** — [05 组件巡览](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/05-component-tour.md) · [06 Keycloak/IdP](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/06-keycloak-idp.md) · [07 Kong](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/07-kong.md) · [08 OPA](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/08-opa.md) · [09 banking-api-service](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/09-banking-api-service.md) · [10 identity-bootstrap-service](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/10-identity-bootstrap-service.md)
- **第三部分 令牌机制** — [11 JWT 签名/校验/内省](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/11-jwt-signature-validation.md) · [12 JWKS](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/12-jwks.md) · [13 令牌生命周期](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/13-token-lifecycle.md)
- **第四部分 参考** — [14 请求与响应细节](https://github.com/geekchow/micro-service-auth/blob/main/docs-zh/14-request-response-reference.md)

---

## 2. O11y-Micro-Service — 微服务可观测性 10 篇系列

自洽的可观测性博客系列：为什么需要、OTel / Prometheus / Grafana 如何分工、一套可跑的 docker-compose
栈、以及 OTel 内部深潜。从「为什么拆分单体后监控失效」讲到「一次 checkout 请求原子级走查」。

**GitHub:** <https://github.com/geekchow/O11y-Micro-Service>

**入口:** [`blog/00-index.md`](https://github.com/geekchow/O11y-Micro-Service/blob/main/blog/00-index.md) ｜ 底层素材 [`docs/`](https://github.com/geekchow/O11y-Micro-Service/tree/main/docs) ｜ 可跑栈 [`stack/`](https://github.com/geekchow/O11y-Micro-Service/tree/main/stack)

| # | 文章 | 说明 |
|---|---|---|
| 1 | [Why Monitoring Broke](https://github.com/geekchow/O11y-Micro-Service/blob/main/blog/01-why-monitoring-broke.md) | 微服务为何杀死旧监控模型；observability vs monitoring 的精确定义 |
| 2 | [How the Pieces Fit Together](https://github.com/geekchow/O11y-Micro-Service/blob/main/blog/02-how-it-fits-together.md) | 7 个核心概念 + 一次 25 分钟事故跟踪到底 |
| 3 | [Building a Runnable Stack](https://github.com/geekchow/O11y-Micro-Service/blob/main/blog/03-building-a-runnable-stack.md) | 5 服务 Spring Boot 商店 + OTel Java agent + 双层 Collector |
| 4 | [Touring the Stack](https://github.com/geekchow/O11y-Micro-Service/blob/main/blog/04-touring-the-stack.md) | 发一个请求，在 Loki/Tempo/Prometheus/Grafana 找足迹 |
| 5 | [Reproducing an Incident](https://github.com/geekchow/O11y-Micro-Service/blob/main/blog/05-reproducing-an-incident.md) | 翻一个环境变量复现生产事故 |
| 6 | [Why OTel Had to Exist](https://github.com/geekchow/O11y-Micro-Service/blob/main/blog/06-otel-why-what.md) | instrumentation 锁定、N×M 矩阵、信号割裂 |
| 7 | [Anatomy of a Signal](https://github.com/geekchow/O11y-Micro-Service/blob/main/blog/07-otel-signals-and-context.md) | spans/instruments/Logs Bridge + Context 传播 |
| 8 | [Inside the Collector](https://github.com/geekchow/O11y-Micro-Service/blob/main/blog/08-otel-collector.md) | receivers/processors/exporters 与优雅降级 |
| 9 | [Sampling: the Interesting 1%](https://github.com/geekchow/O11y-Micro-Service/blob/main/blog/09-otel-sampling.md) | head vs tail sampling |
| 10 | [One Checkout Request, Atom by Atom](https://github.com/geekchow/O11y-Micro-Service/blob/main/blog/10-otel-walkthrough.md) | 全部概念跑过一次真实请求 |

---

## 3. mcp-explain — MCP 学习指南（中英双语）

MCP（Model Context Protocol，模型上下文协议）教学包：Why → What → 概念地图 → 贯穿示例 → 逐组件深潜 →
完整走查，以 Claude Code 中「滞留订单排查」这一真实场景贯穿始终，附带一个可运行的 MCP server。

**GitHub:** <https://github.com/geekchow/mcp-explain>

| 语言 | 索引入口 |
|---|---|
| 中文 | [`mcp-guide-zh/00-overview.md`](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide-zh/00-overview.md) |
| English | [`mcp-guide/00-overview.md`](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide/00-overview.md) |

阅读路径（中文版 12 页）：
- [01 为什么](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide-zh/01-why.md) → [02 是什么](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide-zh/02-what.md) → [03 概念地图](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide-zh/03-concept-map.md) → [04 贯穿示例](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide-zh/04-running-example.md)
- **深潜 05** — [Host Claude Code](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide-zh/05-deep-dives/01-host-claude-code.md) · [MCP Client](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide-zh/05-deep-dives/02-mcp-client.md) · [Transport](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide-zh/05-deep-dives/03-transport.md) · [MCP Server](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide-zh/05-deep-dives/04-mcp-server.md) · [Auth & Trust](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide-zh/05-deep-dives/05-auth-and-trust.md)
- [06 完整走查](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide-zh/06-walkthrough.md) → [07 下一步](https://github.com/geekchow/mcp-explain/blob/main/mcp-guide-zh/07-next-steps.md)
- **可运行示例**: [`mcp-guide/examples/orders-db-server`](https://github.com/geekchow/mcp-explain/tree/main/mcp-guide/examples/orders-db-server)

---

## 4. blue-green-eks-fargate-alb — EKS Fargate 蓝绿发布

三个 API 在 EKS + Fargate 上的蓝绿发布参考实现，流量在 ALB listener rule 表切换（而非 DNS），回滚在下一次请求即生效。中英双语单篇成文 + 可跑 Terraform/K8s。

**GitHub:** <https://github.com/geekchow/blue-green-eks-fargate-alb>

| 语言 | 文章 |
|---|---|
| 中文 | [`blog/blue-green-eks-fargate-alb.zh.md`](https://github.com/geekchow/blue-green-eks-fargate-alb/blob/main/blog/blue-green-eks-fargate-alb.zh.md) |
| English | [`blog/blue-green-eks-fargate-alb.en.md`](https://github.com/geekchow/blue-green-eks-fargate-alb/blob/main/blog/blue-green-eks-fargate-alb.en.md) |

- **Terraform**: [`terraform/`](https://github.com/geekchow/blue-green-eks-fargate-alb/tree/main/terraform) — VPC, EKS + Fargate profiles, LB controller, ACM, alarms
- **K8s**: [`k8s/base/`](https://github.com/geekchow/blue-green-eks-fargate-alb/tree/main/k8s/base) · [`k8s/legs/`](https://github.com/geekchow/blue-green-eks-fargate-alb/tree/main/k8s/legs) · [`k8s/components/`](https://github.com/geekchow/blue-green-eks-fargate-alb/tree/main/k8s/components)

---

## 维护说明 / Maintenance

- 新增一个带讲解文章的 companion repo 时，在顶部概览表加一行，并按「入口 + 阅读地图 + 代码」三段补充小节。
- 文章链接用 `https://github.com/geekchow/<repo>/blob/<branch>/<path>` 的绝对链接，branch 默认 `main`。
- 本文件与各 repo 内的索引（`docs-zh/00-index.md` 等）互不为副本：这里是**聚合指针**，各 repo 内部索引才是正文的源。
- `technical-knowledge` 内按主题分类的单篇文章见根 [`README.md`](README.md)。