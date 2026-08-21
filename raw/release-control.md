# Prompt: Release Management Strategy for a Multi-Market Shared Codebase

## Role

You are a senior release engineering / DevOps (Development & Operations) architect with deep experience in trunk-based development, branching strategies, and multi-tenant product delivery at scale.

## Background

We run the authentication and authorization platform for a banking system, serving both mobile and web clients.

**Scope of the platform**

- AuthN (Authentication，身份认证) and AuthZ (Authorization，授权) for mobile and web channels.
- OAuth (Open Authorization) support for third-party integrations.
- Functional domains: logon, setup, session management, anti-fraud event management.

**Technology stack**

- All APIs (Application Programming Interfaces) are Java + Spring Boot services.
- Hosted on AWS EKS (Elastic Kubernetes Service) using Fargate nodes.
- API configuration — upstream/downstream endpoints, feature toggles — lives in a single DynamoDB config table.
- User profile data is stored in AWS DynamoDB.
- User logon sessions are persisted in AWS ElastiCache.
- AWS CloudHSM (Hardware Security Module) performs token encryption and decryption.
- Downstream business APIs (outside this project's scope) sit behind a Kong gateway and are protected by a PDP (Policy Decision Point), which validates the session against our session management API.

**Team and ownership model**

- One core team owns all 18 repositories and is directly responsible for the UK (United Kingdom) market.
- The same codebase is shared across 20 markets. Markets differ mainly by configuration, but some carry genuinely different business logic — HK (Hong Kong) and UK diverge significantly.
- Each market has its own dedicated development team, all contributing into the same shared codebase.
- The core team performs a **monthly code cut**, creating a stable release branch to prepare the production release.

## The Problem

We need a release model that satisfies two conflicting forces:

1. **Version control must stay centralized.** We do *not* want each market cutting its own long-lived release branch to develop on — that fragments versions and makes the codebase impossible to reason about or support.
2. **Markets have independent delivery pressure.** Twenty markets have different regulatory deadlines, campaign dates, and release calendars; a single monthly train cannot be the only way anything ships.

## What I Want From You

Recommend the best-practice release management model for this situation. Please cover:

1. **Branching strategy** — concretely, which branches exist, who owns them, how long they live, and how code flows between them. Compare the realistic candidates (trunk-based with release trains, GitFlow variants, release branch per train with cherry-pick backports) and state which you recommend and why.
2. **Decoupling market variation from branching** — how to express per-market differences through feature toggles, configuration (our DynamoDB config table), and code-level extension points, so that market divergence does not become branch divergence. Include how to handle the hard case where HK and UK business logic genuinely differ.
3. **Release cadence** — whether the monthly code cut should stay, and how markets with urgent needs get served (off-cycle trains, hotfix lanes, progressive rollout by market).
4. **Governance and process** — code cut criteria, code freeze rules, cherry-pick/backport policy and its approval path, versioning scheme, and how the 18 repositories are versioned and released relative to one another.
5. **Testing and environment strategy** — how to validate a single artifact against 20 market configurations without a 20× QA (Quality Assurance) cost.
6. **Migration path** — a realistic sequence of steps to move from where we are today to the target model, including what to change first and what risks to watch.

Where a trade-off exists, state the trade-off explicitly and give your recommendation rather than listing options neutrally. Prefer concrete, implementable practice over generic advice; include example branch names, toggle-naming conventions, and a sample release calendar where it helps.
