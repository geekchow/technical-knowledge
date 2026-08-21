# technical-knowledge

Personal technical knowledge base — Markdown articles grouped into nine top-level categories.
Each category holds topic subdirectories; images, notebooks and code samples live next to the
article that references them.

## Categories

| Category | Contents |
|---|---|
| [AI](./ai/) | LLM fundamentals & inference, Claude Code, prompting, agents, model routing — 49 articles |
| [Cloud](./cloud/) | AWS services — EKS, networking, DynamoDB, Lambda, IAM/KMS — 12 articles |
| [DevOps](./devops/) | CI/CD, Jenkins, Kubernetes, DNS, Linux, shell, observability — 58 articles |
| [Languages](./languages/) | Java, Python, JavaScript and programming paradigms — 35 articles |
| [Mobile](./mobile/) | iOS and Android build, packaging, CloudKit and App Store review — 17 articles |
| [Web](./web/) | Front-end frameworks and markup — 3 articles |
| [Data & ML](./data-ml/) | Data preparation, notebooks, deep learning, local LLMs — 19 articles |
| [Security](./security/) | TLS/HTTPS, authentication, mobile app hardening — 10 articles |
| [Tools](./tools/) | Docker, Git, VS Code and self-hosted services — 10 articles |

Outside the categories, [`docs/`](./docs/) holds the backlog plus any plans and specs, and
[`raw/`](./raw/README.md) holds the unpolished study notes that the published article series are
derived from.

## AI

_LLM fundamentals & inference, Claude Code, prompting, agents, model routing_

**Agents**

- [AI Agent 记忆的 6 个层级：从 CLAUDE.md 到「统一大脑」](ai/agents/ai-agent-memory-6-levels.md)
- [Build an AI Assistant with LangGraph, Vercel, and Next.js: Use Gmail as a Tool Securely](ai/agents/Build-an-AI-Assistant-with-LangGraph-Vercel-and-Next.js-Use-Gmail-as-a-Tool-Securely.md)

**Claude Code**

- [Claude Code Deep Dive (pdf)](ai/claude-code/claude-code-deep-dive-xelatex.pdf)
- [Claude Code 安装指南](ai/claude-code/claude-code.md)
- [claude skill](ai/claude-code/claude-skill.md)
- [Using Claude Code Efficiently](ai/claude-code/guide.md)
- [iOS UI design for AI-powered dictionary app](ai/claude-code/iOS-UI-design-for-AI-powered-dictionary-app.md)
- [One Layer vs Two Layers: Claude Skill Structure](ai/claude-code/One-layer-vs-two-layers-skill.md)
- [skill](ai/claude-code/skill.md)
- [Claude Skills Marketplace](ai/claude-code/skills-marketplace.md)

**Concepts**

- [AI 核心概念梳理：LLM / Prompt / Agent / RAG / MCP / Skill / Context / Harness](ai/concepts/AI核心概念梳理-LLM-Prompt-Agent-RAG-MCP-Skill-Context-Harness.md)
- [LLM 量化版本 是什么版本](ai/concepts/LLM-量化版本-是什么版本.md)
- [为什么大量公司上了 RAG，却很少真正做成？](ai/concepts/why-rag-projects-fail.zh.md) · [Why So Many Companies Adopt RAG, and So Few Actually Succeed](ai/concepts/why-rag-projects-fail.en.md)

**LLM Fundamentals** — 十三篇中文系列，见 [series index](ai/llm-fundamentals/index.md)

- [01 · 为什么会有 LLM：一个任务一个模型的时代是怎么结束的](ai/llm-fundamentals/01-why.zh.md)
- [02 · LLM 到底是什么：定义、边界与生态位置](ai/llm-fundamentals/02-what.zh.md)
- [03 · 七个核心概念：一次摊开整张地图](ai/llm-fundamentals/03-core-concepts.zh.md)
- [04 · Transformer 内部构造：那几十亿个参数到底排成什么样](ai/llm-fundamentals/04-transformer.zh.md)
- [05 · Tokenizer：模型眼里的世界不是文字](ai/llm-fundamentals/05-tokenizer.zh.md)
- [06 · 训练管线：数据如何变成权重](ai/llm-fundamentals/06-training-pipeline.zh.md)
- [07 · 后训练细拆：SFT、RLHF、DPO、RLVR 四代工具](ai/llm-fundamentals/07-post-training.zh.md)
- [08 · 推理引擎：权重如何被读取](ai/llm-fundamentals/08-inference-engine.zh.md)
- [09 · 参数规模与 Scaling Law：7B、70B、670B 为什么如此重要](ai/llm-fundamentals/09-param-scale.zh.md)
- [10 · 上下文窗口：128K 到底意味着什么](ai/llm-fundamentals/10-context-window.zh.md)
- [11 · 幻觉的机制：为什么它编得如此流畅](ai/llm-fundamentals/11-hallucination.zh.md)
- [12 · 开源 vs 闭源：同一份权重，两种交付](ai/llm-fundamentals/12-open-vs-closed.zh.md)
- [13 · 完整重演：带着全部深度重跑运行示例](ai/llm-fundamentals/13-walkthrough.zh.md)

**LLM Inference** — 中英双语文章系列，见 [series index](ai/llm-inference/index.md)

- [一次 LLM 推理的完整旅程](ai/llm-inference/llm-inference-process.zh.md) · [The Full Journey of an LLM Inference Request](ai/llm-inference/llm-inference-process.en.md)
- [KV Cache 完全解析](ai/llm-inference/kv-cache.zh.md) · [KV Cache Explained](ai/llm-inference/kv-cache.en.md)
- [Chat 阶段 vs Agentic 阶段](ai/llm-inference/chat-vs-agentic.zh.md) · [Chat vs. Agentic](ai/llm-inference/chat-vs-agentic.en.md)
- [GPU 负责想，CPU 负责做](ai/llm-inference/agentic-cpu-demand.zh.md) · [GPUs Think, CPUs Do](ai/llm-inference/agentic-cpu-demand.en.md)
- [会续写 ≠ 会帮忙：后训练](ai/llm-inference/post-training.zh.md) · [Completing Text ≠ Being Helpful](ai/llm-inference/post-training.en.md)
- [FP16 与 INT4 量化](ai/llm-inference/fp16-int4-quantization.zh.md) · [FP16 and INT4 Quantization](ai/llm-inference/fp16-int4-quantization.en.md)

**Model Routing**

- [How to user deeprouter api](ai/model-routing/deeprouter.md)
- [OpenRouter Auto Router vs Model Fallbacks](ai/model-routing/OpenRouter-Auto-Router-vs-Model-Fallbacks.md)
- [OpenRouter](ai/model-routing/openrouter.md)

**OpenClaw**

- [openclaw token](ai/openclaw/openclaw-token.md)
- [setup](ai/openclaw/setup.md)

**Prompting**

- [Cognitive Mental Model — Learning New Systems in Software Engineering](ai/prompting/cogntive-skill.md)
- [如何用 AI 整理自己的思路](ai/prompting/how-to-use-ai.md)
- [ChatGPT is the world's best money maker.](ai/prompting/Make-Money.md)
- [Prompts for AI](ai/prompting/prompt.md)
- [ChatGPT is FREE education.](ai/prompting/Study.md)

**Resources**

- [RSS](ai/resources/RSS.md)

**Superpowers**

- [Superpowers — What It Does & How It Orchestrates Skills](ai/superpowers/superpowers-overview.md)
- [Why superpowers](ai/superpowers/why-superpowers.md)

**General**

- [AI](ai/README.md)

## Cloud

_AWS services — EKS, networking, DynamoDB, Lambda, IAM/KMS_

**AWS**

- [备战 AWS Certification 考试](cloud/aws/Certified-Solution-Architect.md)
- [KMS Encrypt Decrypt](cloud/aws/KMS-Encrypt-Decrypt.md)

**AWS › CIDR Allocation**

- [Allocate CIDR dynamically via `cidrsubnet](cloud/aws/cidr-allocation/README.md)

**AWS › DynamoDB**

- [DynamoDB Stream](cloud/aws/dynamodb/dynamoDB-stream.md)

**AWS › EKS**

- [AWS EKS Add-ons Explained](cloud/aws/eks/aws-eks-addon.md)
- [What is AWS EKS?](cloud/aws/eks/AWS-EKS.md)
- [ECS vs EKS](cloud/aws/eks/ECS-vs-EKS.md)

**AWS › IPv4**

- [IPv4 + CIDR + Subnet](cloud/aws/ipv4/IPv4%2BCIDR%2BSubNet.md)

**AWS › Lambda**

- [how cloudwatch log structure](cloud/aws/lambda/how-cloudwatch-log-structure.md)
- [sample](cloud/aws/lambda/sample.md)

**AWS › Networking**

- [A Practical Tour of AWS Networking: VPCs, Subnets, Gateways, and More](cloud/aws/networking/AWS-Network.md)
- [OSI 7-Layer Model in the Context of AWS](cloud/aws/networking/network-layer.md)

**AWS › Step Functions**

- [Video Summary: AWS re:Invent 2024 – Building State Machines with AWS Step Functions Workflow Studio (API217)](cloud/aws/step-functions/step-functions-workflow-studio-summary.md)

**General**

- [Cloud](cloud/README.md)

## DevOps

_CI/CD, Jenkins, Kubernetes, DNS, Linux, shell, observability_

**CI/CD**

- [Continuous Integration & Continuous Delivery](devops/cicd/CICD.md)

**DNS**

- [Using AWS Route 53 as Your Domain's Authoritative DNS Server](devops/dns/aws-route53-ns.md)
- [How does DNS work ?](devops/dns/dig-dns.md)
- [DNS Record Types Explained](devops/dns/dns-record-types.md)
- [How DNS Works: Key Components Explained](devops/dns/dns-work-mechanism.md)

**Jenkins**

- [Groovy- Difference between List, ArrayList and Object Array](devops/jenkins/groovy-list.md)
- [How to build a jenkins plugin?](devops/jenkins/How-to-build-a-jenkins-plugin.md)
- [How to debug jenkins plugins on fly?](devops/jenkins/How-to-debug-jenkins-plugin.md)
- [How to release a Jenkins Plugin to Jenkins-CI artifactory?](devops/jenkins/How-to-release-a-jenkins-plugin.md)
- [how to operation jenkins via api](devops/jenkins/jenkins-api.md)
- [Jenkins 2 Pipeline definition (Configuration as Code)](devops/jenkins/Jenkins-pipeline.md)
- [Jenkins Tips](devops/jenkins/jenkins-tips.md)
- [Make Jenkins pipeline in `configuration as infrastructure` way with job-dsl-plugin](devops/jenkins/job-dsl-plugin-usage.md)
- [pipeline code snippet](devops/jenkins/pipeline-code-snippet.md)
- [how make template pipeline](devops/jenkins/template-pipeline.md)

**Jenkins › Docker**

- [Run jenkins master on docker](devops/jenkins/docker/start-from-docker.md)

**Kubernetes › CKDA**

- [Pod and Config](devops/kubernetes/ckda/Config-for-Pod.md)
- [Crash course for kubernetes](devops/kubernetes/ckda/crash-course-for-kubernetes.md)
- [Kubernetes Custom Resource Definitions (CRD)](devops/kubernetes/ckda/CRD.md)
- [Cron](devops/kubernetes/ckda/cron.md)
- [Kubernetes Debugging Best Practices](devops/kubernetes/ckda/debug.md)
- [Kubernetes Deployment — Deep Dive](devops/kubernetes/ckda/Deployment.md)
- [Step 1: Add this env var](devops/kubernetes/ckda/Docker.md)
- [Kubernetes Egress](devops/kubernetes/ckda/Egress.md)
- [CKAD Exam Sample — Helm Topic](devops/kubernetes/ckda/helm.md)
- [how nodeport works](devops/kubernetes/ckda/how-nodeport-works.md)
- [Ingress](devops/kubernetes/ckda/ingress.md)
- [Kubernetes Jobs & CronJobs: From Concepts to Examples](devops/kubernetes/ckda/Job.md)
- [Why Kubernetes Commands Use `sh -c](devops/kubernetes/ckda/k8s_command_explanation.md)
- [🧭 Kubernetes kubectl Cheat Sheet](devops/kubernetes/ckda/kubectl-cheatsheet.md)
- [🧪 CKAD Mock Exam — Intermediate Level](devops/kubernetes/ckda/mock-exam.md)
- [Kubernetes Pod — Deep Dive](devops/kubernetes/ckda/Pod.md)
- [Kubernetes Resource Management — Deep Dive](devops/kubernetes/ckda/ResourceLimit-Quota.md)
- [Sealed Secret](devops/kubernetes/ckda/Sealed-Secret.md)
- [Kubernetes Security: Deep Dive](devops/kubernetes/ckda/Security.md)
- [Kubernetes Service Types](devops/kubernetes/ckda/Service.md)
- [Storage](devops/kubernetes/ckda/Storage.md)
- [VI tips for K8S yaml edtion](devops/kubernetes/ckda/vi-tips-for-yaml.md)

**Kubernetes › Experience**

- [ssl protocol conflict](devops/kubernetes/experience/ssl-protocol-conflict.md)

**Linux**

- [Understanding GID in Linux](devops/linux/Linux-GID.md)
- [Understanding Linux Groups](devops/linux/linux_groups.md)
- [Linux Permission System](devops/linux/linux_permissions.md)
- [Screen 会话管理](devops/linux/Screen-会话管理.md)

**Networking**

- [forward reverse proxy](devops/networking/forward_reverse_proxy.md)

**Nexus**

- [Sonatype Nexus Repository Manager](devops/nexus/sonatype-nexus-respository-manager-introduction.md)

**Observability**

- [Instrumenting a Java Spring Boot Application on AWS EKS Fargate with Splunk Observability Cloud](devops/observability/splunk-o11y-eks-fargate-java-architecture.md)

**Practices**

- [AgileAlliance](devops/practices/AgileAlliance.md)
- [Git Branching Strategies: Common Models, Trade-offs, and Choosing One for Correlated API Releases](devops/practices/branching-strategy.md)
- [Multiple Mac mini share memory](devops/practices/Multiple-Mac-mini-share-memory.md)
- [Release Management for a Shared Codebase Serving 20 Markets](devops/practices/multi-market-release-management.md)

**Shell**

- [Zsh Subshell Variable Expansion](devops/shell/2026-04-05-AI-Insight-Zsh-Subshell-Variable-Expansion.md)
- [Bash](devops/shell/bash.md)
- [Difference Between `bash` and `sh` --- And Why Lightweight Images Include Only `sh](devops/shell/bash_vs_sh_explained.md)
- [find](devops/shell/find.md)
- [grep](devops/shell/grep.md)
- [network tools](devops/shell/network-tools.md)
- [Permission of file in Bash](devops/shell/permission.md)
- [tree — 列目录并排除指定子目录](devops/shell/tree.md)
- [zsh](devops/shell/zsh.md)

**General**

- [DevOps](devops/README.md)

## Languages

_Java, Python, JavaScript and programming paradigms_

**Java**

- [IntelliJ Tips](languages/java/IntelliJ-tips.md)
- [How install multiple java version on M1 chip Mac](languages/java/Mac-m1-multiple-java.md)
- [trustStore keyStore](languages/java/trustStore-keyStore.md)

**Java › Mono & Flux**

- [Reative flow](languages/java/mono-flux/mono-vs-flux.md)

**Java › Spring Boot**

- [Reactive Programming with Spring 5](languages/java/springboot/00Reactive-with-spring.md)

**Java › WebFlux**

- [How WebFlux improve I/O bound web service througout via async threading](languages/java/webflux/00-async-with-webflux.md)

**JavaScript**

- [Reactive programming](languages/javascript/reactive-programming.md)

**Paradigms**

- [Light state cycle detection bug](languages/paradigms/Light-state-cycle-detection-bug.md)

**Paradigms › Imperative Vs Declarative Program**

- [Declarative vs imperative programming](languages/paradigms/imperative-vs-declarative-program/imperative-declarative.md)

**Python**

- [算法题笔记：最长回文子串、Z 字形变换与合并有序链表](languages/python/algorithm-notes-palindrome-zigzag-merge-lists.md)
- [How to debug Python with VS Code?](languages/python/Debug-Python-With-VS-Code.md)
- [jupyter notebook (notebook)](languages/python/jupyter-notebook.ipynb)
- [postgresql bulk update with python](languages/python/postgresql-bulk-update.md)
- [Python 3 进阶复习手册](languages/python/python-advance.md)
- [requests` pip package](languages/python/python-requests.md)
- [Python threading.Semaphore 机制详解](languages/python/python-threading-semaphore.md)
- [Python 切片 (Slice) 详解](languages/python/slice.md)
- [subprocess shell (notebook)](languages/python/subprocess-shell.ipynb)
- [Why Use uv for Python](languages/python/Why-Use-uv-for-Python.md)

**Python › argparse**

- [argparse](languages/python/argparse/argparse-intro.md)

**Python › Intro Programming**

- [class (notebook)](languages/python/intro-programming/class.ipynb)
- [decorator of python (notebook)](languages/python/intro-programming/decorator-of-python.ipynb)
- [dictionary (notebook)](languages/python/intro-programming/dictionary.ipynb)
- [functional programming with python (notebook)](languages/python/intro-programming/functional-programming-with-python.ipynb)
- [python exception handling (notebook)](languages/python/intro-programming/python-exception-handling.ipynb)

**Python › NumPy**

- [numpy learning (notebook)](languages/python/numpy/numpy-learning.ipynb)

**Python › Pythonschema**

- [pythonschema` could do json schema validation](languages/python/pythonschema/sample.md)

**General**

- [Languages](languages/README.md)

## Mobile

_iOS and Android build, packaging and architecture_

**Android**

- [Android App bundle vs Android APK](mobile/android/android-app-bundle.md)
- [android fundamental](mobile/android/android-fundamental.md)
- [Android X Introduction](mobile/android/androidx-intro.md)
- [Set up Google Play services](mobile/android/google-service.md)
- [gradle](mobile/android/gradle.md)
- [Difference Between Proguard and R8 in Android](mobile/android/proguard-vs-r8.md)

**iOS**

- [UIKit View Preview（AI Insight）](mobile/ios/2026-05-03-AI-Insight-UIKit-View-Preview.md)
- [CloudKit multi-device synchronization](mobile/ios/CloudKit-multi-device-synchronization.md)
- [CloudKit Schema Deploy UI](mobile/ios/CloudKit-Schema-Deploy-UI.md)
- [iOS certificate and provisioning profile planning](mobile/ios/iOS-certificate-and-provisioning-profile-planning.md)
- [What an ipa package contains, and the relationship among them?](mobile/ios/ipa-introduction.md)
- [UIKit view preview in iOS development](mobile/ios/UIKit-view-preview-in-iOS-development.md)
- [What do Workspace, Project , Target, Scheme, Build Settings, Configurations, Build Phases mean regarding iOS development?](mobile/ios/xcode-basic-concept.md)
- [xcodebuild` Introduction](mobile/ios/xcodebuild.md)
- [会意典应用被拒审核问题（App Store 审核被拒排查）](mobile/ios/会意典应用被拒审核问题.md)

**iOS › Best Way To Build Ios App**

- [iOS Mobile App Development Guide: Best Practices for Building iPhone Mobile Apps](mobile/ios/best-way-to-build-ios-app/best-way-to-buid-ios-app.md)

**iOS › Redux Ios**

- [redux for ios](mobile/ios/redux-ios/redux-for-ios.md)

**General**

- [Mobile](mobile/README.md)

## Web

_Front-end frameworks and markup_

**Frontend › AngularJS**

- [Angular development](web/frontend/angularjs/angular-development.md)
- [A hybrid mobile application base on angularjs](web/frontend/angularjs/hybrid-app-base-on-angularjs-spa.mm.md)

**Frontend › HTML & CSS**

- [html element span](web/frontend/html-css/span.md)

**General**

- [Web](web/README.md)

## Data & ML

_Data preparation, notebooks, deep learning, local LLMs_

**Data Preparation**

- [01 pandas basic (notebook)](data-ml/data-preparation/01-pandas-basic.ipynb)
- [02 matlab data visiualization (notebook)](data-ml/data-preparation/02-matlab-data-visiualization.ipynb)
- [03 pandas explore data (notebook)](data-ml/data-preparation/03-pandas-explore-data.ipynb)
- [04 deal missing data (notebook)](data-ml/data-preparation/04-deal-missing-data.ipynb)
- [05 normalize data (notebook)](data-ml/data-preparation/05-normalize-data.ipynb)
- [06 sample data (notebook)](data-ml/data-preparation/06-sample-data.ipynb)
- [07 build model (notebook)](data-ml/data-preparation/07-build-model.ipynb)

**Deep Learning**

- [What’s the difference between CNN and RNN?](data-ml/deep-learning/CNN-vs-RNN.md)

**LLaMA**

- [Exploring LLMs with MLX and the Neural Accelerators in the M5 GPU](data-ml/llama/Exploring-LLMs-with-MLX-and-the-Neural-Accelerators-in-the-M5-GPU.md)
- [llama 2 model setup](data-ml/llama/setup.md)

**Notebooks**

- [stock price predict with LSTM (notebook)](data-ml/notebooks/stock-price-predict-with-LSTM.ipynb)

**General**

- [Data & ML](data-ml/README.md)

## Security

_TLS/HTTPS, authentication, mobile app hardening_

**Auth**

- [JWT](security/auth/JWT.md)
- [microservice security](security/auth/microservice-security.md)
- [🏦 **1. High-Level Flow Overview**](security/auth/mobile_banking_auth.md)

**Mobile Security**

- [Mobile App Certificate Pinning: Underlying Principle and a Swift Example](security/mobile-security/Cert-Pinning-Swift.md)
- [Certificate pinning](security/mobile-security/cert-pinning.md)
- [How Charles Proxy Works: From HTTP Proxy to HTTPS MITM Traffic Inspection](security/mobile-security/Charles-network-sniff.md)
- [Mobile API Token Security](security/mobile-security/Mobile-API-Token-Security.md)
- [Runtime application self-protection](security/mobile-security/RASP-for-mobile.md)

**TLS**

- [how https works](security/tls/how-https-works.md)
- [ssl](security/tls/ssl.md)

**General**

- [Security](security/README.md)

## Tools

_Docker, Git, VS Code and self-hosted services_

**Docker**

- [Why some container exit immediately](tools/docker/docker-container-exit-immediately.md)
- [docker](tools/docker/docker.md)
- [pull ubuntu:trusty](tools/docker/experiment.md)

**Git**

- [Git Aliases Reference Guide](tools/git/git-aliases-guide.md)
- [Git, Finally Understood: A Snapshot Database and a Handful of Pointers](tools/git/git-mental-model-snapshots-pointers.en.md)
- [把 Git 想清楚：快照数据库 + 一堆指针](tools/git/git-mental-model-snapshots-pointers.zh.md)
- [git push hanging](tools/git/git-push-hanging.md)
- [Git Tags in the Release Process: Lightweight, Annotated, and Signed](tools/git/git-tags-in-the-release-process.en.md)
- [Git 标签与发布流程：轻量标签、附注标签与签名标签](tools/git/git-tags-in-the-release-process.zh.md)

**VS Code**

- [VS-Code](tools/vscode/VS-Code.md)

**General**

- [Tools](tools/README.md)
