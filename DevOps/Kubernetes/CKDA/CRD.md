# Kubernetes Custom Resource Definitions (CRD)

## Core Concept

Kubernetes ships with built-in resources like `Pod`, `Deployment`, `Service`, etc. But what if your application needs domain-specific primitives — like a `Database`, `KafkaTopic`, or `AIModel`? That's exactly what **CRD (Custom Resource Definition)** solves.

> CRD is Kubernetes' extension mechanism that lets you define your own API resources, making them first-class citizens in the cluster — queryable via `kubectl`, storable in etcd, and watchable by controllers.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes API Server                    │
│                                                                 │
│  Built-in Resources          Custom Resources (via CRD)        │
│  ┌──────────────┐            ┌──────────────────────────────┐  │
│  │  Pod         │            │  CRD: databases.bank.io/v1   │  │
│  │  Deployment  │            │  CR:  my-oracle-db (instance)│  │
│  │  Service     │            └──────────────────────────────┘  │
│  └──────────────┘                         │                    │
└──────────────────────────────────────────│────────────────────┘
                                           │  watch/reconcile
                                           ▼
                              ┌────────────────────────┐
                              │   Custom Controller     │
                              │   (Operator)            │
                              │                         │
                              │  1. Watch CR events     │
                              │  2. Compare desired vs  │
                              │     actual state        │
                              │  3. Take action         │
                              └────────────────────────┘
```

---

## The Three Key Players

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. CRD (schema blueprint)                                  │
│     - Tells the API server: "This new resource type exists" │
│     - Defines group, version, kind, validation schema       │
│                                                             │
│  2. CR (Custom Resource - instance)                         │
│     - An actual object conforming to the CRD schema         │
│     - Lives in etcd like any other k8s object               │
│                                                             │
│  3. Controller / Operator                                   │
│     - Watches CR events (create/update/delete)              │
│     - Implements reconciliation loop                        │
│     - Drives actual state → desired state                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

  CRD : CR  ≈  Class : Instance  ≈  Table Schema : Row
```

---

## CRD Anatomy (YAML Deep-Dive)

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: tradingaccounts.bank.io    # <plural>.<group>  — must match spec
spec:
  group: bank.io                   # API group (like apps, batch)
  scope: Namespaced                # or Cluster
  names:
    plural: tradingaccounts        # kubectl get tradingaccounts
    singular: tradingaccount
    kind: TradingAccount           # used in YAML manifests
    shortNames:
      - ta                         # kubectl get ta
  versions:
    - name: v1
      served: true                 # API serves this version
      storage: true                # stored in etcd as this version
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required: ["owner", "riskLevel"]
              properties:
                owner:
                  type: string
                riskLevel:
                  type: string
                  enum: ["LOW", "MEDIUM", "HIGH"]
                creditLimit:
                  type: number
                  minimum: 0
            status:
              type: object
              properties:
                phase:
                  type: string    # PENDING / ACTIVE / SUSPENDED
                lastUpdated:
                  type: string
      subresources:
        status: {}                 # enables /status subresource
      additionalPrinterColumns:
        - name: Owner
          type: string
          jsonPath: .spec.owner
        - name: Risk
          type: string
          jsonPath: .spec.riskLevel
        - name: Phase
          type: string
          jsonPath: .status.phase
```

---

## Custom Resource Instance (CR)

```yaml
apiVersion: bank.io/v1
kind: TradingAccount
metadata:
  name: alice-account
  namespace: trading
spec:
  owner: alice
  riskLevel: HIGH
  creditLimit: 500000
status:
  phase: ACTIVE
  lastUpdated: "2026-02-21T08:00:00Z"
```

---

## Controller Reconciliation Loop

```
                 ┌──────────────────────────────────┐
                 │         Reconcile Loop            │
                 │                                   │
  CR Event ───► │  1. Fetch CR from API Server      │
  (Add/Update/  │  2. Read current real-world state  │
   Delete)      │  3. Diff desired vs actual         │
                 │  4. Take corrective action         │
                 │  5. Update CR status               │
                 │  6. Requeue if needed              │
                 └──────────────────────────────────┘

  Key property: IDEMPOTENT — running reconcile N times = same as once
```

A Java-flavored pseudo-implementation using controller-runtime:

```java
@Override
public Result reconcile(Request request) {
    // 1. Fetch the CR
    TradingAccount account = client.get(TradingAccount.class, request.getName());
    if (account == null) return Result.noRequeue();

    // 2. Check actual state
    boolean backendAccountExists = bankingService.accountExists(account.getSpec().getOwner());

    // 3. Reconcile
    if (!backendAccountExists) {
        bankingService.createAccount(account.getSpec());
        account.getStatus().setPhase("ACTIVE");
        client.updateStatus(account);
    }

    // 4. Handle deletion via finalizer
    if (account.isMarkedForDeletion()) {
        bankingService.closeAccount(account.getSpec().getOwner());
        removeFinalizer(account);
    }

    return Result.noRequeue();
}
```

---

## Versioning & Conversion

When your CRD evolves, Kubernetes supports multiple versions with a **conversion webhook**:

```
v1alpha1 ──────────────────────────────► v1
  (old CR stored in etcd)    Conversion Webhook converts on-the-fly
                                  │
                           ┌──────▼───────┐
                           │  Your webhook │  (HTTP server you deploy)
                           │  converts     │
                           │  v1alpha1 →   │
                           │  v1 objects   │
                           └──────────────┘
```

---

## CRD vs ConfigMap (common misconception)

| Dimension | ConfigMap | CRD |
|---|---|---|
| Schema validation | None | Full OpenAPI v3 schema |
| RBAC control | Namespace-level | Per-resource type |
| Watch/event support | Basic | Native (List & Watch) |
| Status subresource | No | Yes (spec/status separation) |
| kubectl integration | Limited | Full (get, describe, printer cols) |
| Use case | App config | Domain objects / Operators |

---

## Real Exam Scenarios

### Scenario 1 — Operator Pattern in Banking

> Your team maintains a Kafka-based event streaming platform. Dev teams constantly request new Kafka topics with specific retention and replication settings. Manual provisioning is error-prone.

**Solution:** Define a `KafkaTopic` CRD. Devs submit a CR. Your operator watches it, calls Kafka Admin API, provisions the topic, and writes status back. Fully GitOps-compatible.

```
Dev commits KafkaTopic CR → ArgoCD syncs → Operator reconciles → Kafka topic created
```

---

### Scenario 2 — Status vs Spec Separation

> Why is `spec/status` split important?

- **spec**: desired state (written by user/client)
- **status**: observed state (written ONLY by controller)
- With `subresources.status: {}` enabled, updating status requires a separate API call (`/status` endpoint) with its own RBAC
- This prevents accidental overwrite: `kubectl apply` won't clobber status

---

### Scenario 3 — Finalizers for safe cleanup

```yaml
metadata:
  finalizers:
    - bank.io/cleanup-trading-account
```

When a user deletes a CR, Kubernetes sets `deletionTimestamp` but **won't actually delete** until all finalizers are removed. Your controller runs cleanup logic (close positions, archive data) then removes the finalizer — only then does the object disappear from etcd. Critical for stateful banking resources.

---

### Scenario 4 — Common `kubectl` operations

```bash
# Register the new resource type
kubectl apply -f tradingaccount-crd.yaml

# Verify CRD is established
kubectl get crd tradingaccounts.bank.io
kubectl describe crd tradingaccounts.bank.io

# CRUD on custom resources
kubectl apply -f alice-account.yaml
kubectl get tradingaccounts -n trading
kubectl get ta                          # using shortName
kubectl describe ta alice-account -n trading

# Check schema validation (will reject invalid riskLevel)
kubectl apply -f bad-account.yaml
# Error: spec.riskLevel: Unsupported value: "ULTRA": supported: LOW, MEDIUM, HIGH
```

---

## Key Takeaways

The mental model that makes CRD click: **you are extending the Kubernetes API itself**. Once a CRD is installed, the API server treats your custom resource exactly like a built-in — it handles auth, RBAC, storage, watch events, and API versioning for you. Your controller just focuses on pure business logic in a reconciliation loop. This is the foundation of the **Operator Pattern**, which is how production-grade stateful systems (databases, message brokers, ML pipelines) are managed on Kubernetes today.