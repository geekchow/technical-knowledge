# Kubernetes Resource Management — Deep Dive

## The Mental Model First

There are **three layers** of resource control in Kubernetes:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLUSTER                                  │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  ResourceQuota                          │   │
│   │            (namespace-level ceiling)                    │   │
│   │                                                         │   │
│   │   ┌───────────────────────────────────────────────┐     │   │
│   │   │              LimitRange                       │     │   │
│   │   │     (per-object defaults & constraints)       │     │   │
│   │   │                                               │     │   │
│   │   │   ┌─────────────────────────────────────┐     │     │   │
│   │   │   │              Pod                    │     │     │   │
│   │   │   │  ┌──────────────────────────────┐   │     │     │   │
│   │   │   │  │  Container requests/limits   │   │     │     │   │
│   │   │   │  │  cpu: req=250m  limit=500m   │   │     │     │   │
│   │   │   │  │  mem: req=256Mi limit=512Mi  │   │     │     │   │
│   │   │   │  └──────────────────────────────┘   │     │     │   │
│   │   │   └─────────────────────────────────────┘     │     │   │
│   │   └───────────────────────────────────────────────┘     │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

| Layer | Scope | Purpose |
|---|---|---|
| `requests/limits` | Per container | Scheduler hint + runtime enforcement |
| `LimitRange` | Per namespace | Defaults + per-object min/max constraints |
| `ResourceQuota` | Per namespace | Total aggregate cap for a namespace |

---

## Layer 1 — requests & limits

### Concept

```
requests  = what you're GUARANTEED to get    → used by scheduler
limits    = the maximum you're ALLOWED to use → enforced by cgroups at runtime
```

```
Node capacity: 4 CPU, 8Gi memory

┌──────────────────────────────────────────────────────┐
│  NODE                                                │
│                                                      │
│  Pod A        Pod B        Pod C                     │
│  req: 1CPU    req: 1CPU    req: 1CPU                 │
│  lim: 2CPU    lim: 2CPU    lim: 2CPU                 │
│                                                      │
│  Scheduler sees: 3 CPU allocated (requests)          │
│  Scheduler has:  1 CPU remaining to place new pods   │
│                                                      │
│  At runtime: pods can BURST up to 2CPU each          │
│  but CPU is COMPRESSIBLE — throttled, not killed     │
└──────────────────────────────────────────────────────┘
```

### CPU vs Memory — critically different behavior

```
CPU (compressible resource)         Memory (incompressible resource)
─────────────────────────────       ─────────────────────────────────
Exceeds limit? → THROTTLED          Exceeds limit? → OOMKilled (SIGKILL)
No data loss                        Process killed immediately
Container keeps running             Container restarts (per restartPolicy)
```

### QoS Classes — derived automatically from requests/limits

```
┌─────────────────┬──────────────────────────────────────────┬──────────────────────┐
│   QoS Class     │  Condition                               │  Eviction Priority   │
├─────────────────┼──────────────────────────────────────────┼──────────────────────┤
│ Guaranteed      │ requests == limits for ALL containers     │  Last to be evicted  │
│                 │ (both cpu AND memory must be set)         │                      │
├─────────────────┼──────────────────────────────────────────┼──────────────────────┤
│ Burstable       │ At least one container has requests set   │  Middle priority     │
│                 │ but requests != limits                    │                      │
├─────────────────┼──────────────────────────────────────────┼──────────────────────┤
│ BestEffort      │ NO requests or limits set at all         │  First to be evicted │
└─────────────────┴──────────────────────────────────────────┴──────────────────────┘
```

When node is under memory pressure, eviction order: **BestEffort → Burstable → Guaranteed**

For banking/production workloads: always aim for **Guaranteed** on critical services.

```yaml
# Guaranteed QoS — requests == limits
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

### Units Cheatsheet

```
CPU:
  1    = 1 vCPU / 1 core / 1000m
  500m = 0.5 vCPU  (m = millicores)
  100m = 0.1 vCPU

Memory:
  Ki = kibibyte = 1024 bytes
  Mi = mebibyte = 1024 Ki
  Gi = gibibyte = 1024 Mi
  
  vs decimal:
  K  = kilobyte = 1000 bytes   ← avoid, use Ki/Mi/Gi
```

---

## Layer 2 — LimitRange

### Concept

LimitRange is a **namespace-scoped policy** that:
1. Sets **default** requests/limits for containers that don't specify them
2. Enforces **min/max** bounds per container, pod, or PVC
3. Controls **limit/request ratio** (`maxLimitRequestRatio`)

Without LimitRange, a developer forgetting to set resources creates a **BestEffort** pod — gets evicted first under pressure, or worse, no limits means one rogue pod can consume all node resources.

### Full LimitRange Manifest

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: fintech-limits
  namespace: fintech
spec:
  limits:
    # ── Container-level ──────────────────────────────────────
    - type: Container
      default:              # applied if container has NO limits set
        cpu: "500m"
        memory: "256Mi"
      defaultRequest:       # applied if container has NO requests set
        cpu: "100m"
        memory: "128Mi"
      min:                  # container cannot request LESS than this
        cpu: "50m"
        memory: "64Mi"
      max:                  # container cannot set limits MORE than this
        cpu: "2"
        memory: "1Gi"
      maxLimitRequestRatio: # limit / request ratio ceiling
        cpu: "4"            # limit cannot exceed 4x the request
        memory: "2"

    # ── Pod-level (sum of all containers) ────────────────────
    - type: Pod
      max:
        cpu: "4"
        memory: "2Gi"

    # ── PersistentVolumeClaim ─────────────────────────────────
    - type: PersistentVolumeClaim
      min:
        storage: "1Gi"
      max:
        storage: "50Gi"
```

### LimitRange Default Injection Flow

```
Developer submits Pod with NO resource spec
           │
           ▼
    API Server Admission
           │
           ▼
    LimitRange Webhook
           │
    ┌──────┴──────┐
    │             │
 Has limits?   No limits
  Validate     Inject defaults:
  min ≤ x ≤ max  limits  = LimitRange.default
                 requests = LimitRange.defaultRequest
           │
           ▼
    Pod created with resources
```

### Verify LimitRange is working

```bash
kubectl describe limitrange fintech-limits -n fintech

kubectl run test --image=nginx -n fintech
kubectl get pod test -n fintech -o yaml | grep -A 10 resources
# You'll see injected defaults even though you never specified them
```

---

## Layer 3 — ResourceQuota

### Concept

ResourceQuota caps the **total aggregate consumption** of a namespace. It prevents one team/app from monopolizing cluster resources.

```
Namespace: fintech
ResourceQuota: cpu total ≤ 20 cores, memory total ≤ 40Gi

Team A pods:  4 CPU  8Gi   ─┐
Team B pods:  6 CPU  12Gi  ─┼─► total = 10 CPU, 20Gi  ✅ under quota
Team C pods:  2 CPU  4Gi   ─┘

Team D tries to deploy: requests 12 CPU
                        10 + 12 = 22 > 20  ❌ REJECTED
```

### Full ResourceQuota Manifest

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: fintech-quota
  namespace: fintech
spec:
  hard:
    # ── Compute ────────────────────────────────────────────
    requests.cpu: "20"          # total CPU requests across all pods
    limits.cpu: "40"            # total CPU limits across all pods
    requests.memory: "40Gi"
    limits.memory: "80Gi"

    # ── Object count ───────────────────────────────────────
    pods: "50"                  # max number of pods
    services: "20"
    secrets: "50"
    configmaps: "30"
    persistentvolumeclaims: "20"
    services.loadbalancers: "5"  # expensive cloud LBs
    services.nodeports: "0"      # block NodePort in prod namespace

    # ── Storage ────────────────────────────────────────────
    requests.storage: "500Gi"
    gold.storageclass.storage.k8s.io/requests.storage: "100Gi"  # per StorageClass
```

### Scoped ResourceQuota (advanced)

You can apply quotas only to pods matching certain **scopes**:

```yaml
spec:
  hard:
    pods: "10"
  scopeSelector:
    matchExpressions:
      - operator: In
        scopeName: PriorityClass
        values: ["high-priority"]
```

| Scope | Matches |
|---|---|
| `Terminating` | Pods with `activeDeadlineSeconds` set |
| `NotTerminating` | Pods without deadline (long-running) |
| `BestEffort` | Pods with no requests/limits |
| `NotBestEffort` | Pods with at least one request/limit |
| `PriorityClass` | Pods with specific priority class |

**Important**: If ResourceQuota on `requests.cpu` exists in a namespace, **every pod MUST specify `requests.cpu`** — otherwise rejected. LimitRange defaults save you here.

### LimitRange + ResourceQuota working together

```
                  Developer submits Pod
                         │
                         ▼
              ┌─── LimitRange ───┐
              │                  │
           Missing?           Present?
           Inject defaults    Validate min/max
              │                  │
              └─────────┬────────┘
                        │
                        ▼
              ┌─── ResourceQuota ───┐
              │                     │
         namespace total           Reject if
         + this pod ≤ hard limit   over limit
              │
              ▼
         Pod created ✅
```

This is why **always deploy LimitRange before ResourceQuota** in a namespace — otherwise pods without resource specs get rejected by quota check before defaults can be injected.

---

## Monitoring Quota Usage

```bash
# Current usage vs hard limits
kubectl describe resourcequota fintech-quota -n fintech
# Name:            fintech-quota
# Namespace:       fintech
# Resource         Used    Hard
# ───────────────  ──────  ────
# limits.cpu       8       40
# limits.memory    16Gi    80Gi
# pods             12      50
# requests.cpu     4       20
# requests.memory  8Gi     40Gi

# All quotas across all namespaces
kubectl get resourcequota -A

# Get LimitRanges
kubectl get limitrange -n fintech
kubectl describe limitrange fintech-limits -n fintech
```

---

## Exam Scenarios (CKA / CKAD)

---

**Scenario 1 — Create a LimitRange with defaults**
```bash
# Quick imperative? No — LimitRange has no kubectl create shortcut
# Must write YAML. Memorize the structure.

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: dev
spec:
  limits:
  - type: Container
    default:
      cpu: "500m"
      memory: "256Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
EOF
```

---

**Scenario 2 — Pod rejected due to ResourceQuota, diagnose and fix**
```bash
kubectl apply -f pod.yaml
# Error: pods "my-app" is forbidden: exceeded quota: ns-quota,
# requested: requests.cpu=0, used: requests.cpu=19500m, limited: requests.cpu=20

# Step 1: Check quota
kubectl describe resourcequota -n dev

# Step 2: Find biggest consumers
kubectl get pods -n dev -o custom-columns=\
"NAME:.metadata.name,CPU_REQ:.spec.containers[*].resources.requests.cpu" 

# Step 3: Either scale down other deployments or add resources.requests to your pod
# If pod has no requests and quota requires them — that's the error
# Fix: add explicit requests to pod spec or ensure LimitRange defaults exist
```

---

**Scenario 3 — Pod is OOMKilled, investigate and fix**
```bash
kubectl get pod payment-service-xxx
# STATUS: OOMKilled

kubectl describe pod payment-service-xxx
# Last State: Terminated
#   Reason: OOMKilled
#   Exit Code: 137

# Fix: increase memory limit
kubectl set resources deployment payment-service \
  --requests=memory=512Mi \
  --limits=memory=1Gi

# OR edit directly
kubectl edit deployment payment-service
```
Exit code 137 = 128 + 9 (SIGKILL) → always means OOMKill.

---

**Scenario 4 — Block BestEffort pods in a namespace**
```yaml
# ResourceQuota that requires all pods to have requests set
apiVersion: v1
kind: ResourceQuota
metadata:
  name: no-besteffort
  namespace: prod
spec:
  hard:
    pods: "0"            # allows zero BestEffort pods
  scopes:
    - BestEffort
```

---

**Scenario 5 — Verify QoS class of a pod**
```bash
kubectl get pod my-pod -o jsonpath='{.status.qosClass}'
# Guaranteed / Burstable / BestEffort

kubectl describe pod my-pod | grep "QoS Class"
```

---

**Scenario 6 — Set resources imperatively**
```bash
# On existing deployment
kubectl set resources deployment payment-service \
  --containers=app \
  --requests=cpu=250m,memory=256Mi \
  --limits=cpu=500m,memory=512Mi

# Verify
kubectl describe deployment payment-service | grep -A 6 Limits
```

---

**Scenario 7 — LimitRange ratio violation**
```yaml
# LimitRange: maxLimitRequestRatio.cpu = 4
# Pod spec:
resources:
  requests:
    cpu: "100m"
  limits:
    cpu: "800m"   # ratio = 8x > 4x ❌ REJECTED

# Fix:
  limits:
    cpu: "400m"   # ratio = 4x ✅
```

---

## Complete Picture — Request Flow

```
kubectl apply -f pod.yaml
        │
        ▼
┌──────────────────┐
│   API Server     │
│   Validation     │──── schema invalid? ──► Reject 400
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Admission       │
│  Controllers     │
│                  │
│  1. LimitRange   │──── missing resources? inject defaults
│     Admission    │──── violates min/max?  ──► Reject 403
│                  │
│  2. ResourceQuota│──── namespace total    ──► Reject 403
│     Admission    │     would exceed hard
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    Scheduler     │
│                  │
│  node.allocatable│
│  - sum(requests) │──── no node fits? ──► Pending (Insufficient cpu)
│  = available     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    Kubelet       │
│    (node)        │
│                  │
│  cgroups enforced│──── CPU > limit?    throttle
│                  │──── MEM > limit?    OOMKill → restart
└──────────────────┘
```

---

## Banking Context

| Scenario | Resource Control Tool |
|---|---|
| Isolate teams (FX, Equity, Risk) to separate namespaces | ResourceQuota per namespace |
| Prevent developer forgetting resources in UAT | LimitRange defaults |
| Guarantee SLA for critical payment processing pods | `requests == limits` → Guaranteed QoS |
| Cap cloud cost per business unit | ResourceQuota on `requests.cpu/memory` |
| Prevent rogue batch job consuming all memory | LimitRange `max.memory` per container |
| Audit who consumed what | `kubectl describe resourcequota` + Prometheus `kube_resourcequota` metrics |
| PCI-DSS namespace isolation | ResourceQuota + NetworkPolicy + separate namespace |

**Recommended namespace setup for banking:**
```
namespace: payment-prod
  ├── LimitRange: inject safe defaults, cap at 2CPU/2Gi per container
  ├── ResourceQuota: cap namespace at 40CPU/80Gi, no NodePorts, max 5 LBs
  └── All critical services: Guaranteed QoS (requests == limits)

namespace: batch-jobs
  ├── LimitRange: generous limits, high maxLimitRequestRatio for burst
  └── ResourceQuota: separate budget — doesn't compete with payment-prod
```

This ensures your payment service pods are **last to be evicted**, batch jobs can't starve your real-time services, and finance can track cloud spend per business unit.