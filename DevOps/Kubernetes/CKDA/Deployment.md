# Kubernetes Deployment — Deep Dive

## Concept

A **Deployment** is a higher-level abstraction that manages a **ReplicaSet**, which in turn manages **Pods**. It's the standard way to run stateless workloads in production.

Core value proposition:
- **Declarative** — you describe desired state, controller reconciles reality
- **Rolling updates** — zero-downtime version upgrades
- **Rollback** — instantly revert to a previous revision
- **Self-healing** — crashed pods are automatically replaced

The ownership chain:
```
Deployment → ReplicaSet(s) → Pods
```
When you update a Deployment, it creates a **new ReplicaSet** and gradually shifts pods from old to new — the old RS is kept (scaled to 0) for rollback purposes.

---

## Anatomy of a Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: fintech
  annotations:
    kubernetes.io/change-cause: "upgrade to v1.3.0 — CVE-2024-1234 patch"  # rollout history message
spec:
  replicas: 3

  selector:                    # IMMUTABLE — how Deployment finds its Pods
    matchLabels:
      app: payment-service

  revisionHistoryLimit: 5      # how many old ReplicaSets to keep (default: 10)

  progressDeadlineSeconds: 120 # mark rollout as failed if not done in 2 min

  strategy:
    type: RollingUpdate        # RollingUpdate | Recreate
    rollingUpdate:
      maxUnavailable: 1        # max pods that can be unavailable during update
      maxSurge: 1              # max pods above desired count during update

  template:                    # this IS a Pod spec, with metadata
    metadata:
      labels:
        app: payment-service   # must match selector above
        version: v1.3.0
    spec:
      containers:
        - name: app
          image: payment-service:1.3.0
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10

      terminationGracePeriodSeconds: 60   # SIGTERM → wait → SIGKILL
      
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: payment-service
                topologyKey: kubernetes.io/hostname
```

---

## Update Strategies

### RollingUpdate (default)
Zero-downtime; old and new pods coexist temporarily.

```
replicas=4, maxUnavailable=1, maxSurge=1

Start:   [v1][v1][v1][v1]          (4 running)
Step 1:  [v1][v1][v1][v1][v2]      (surge +1, now 5)
Step 2:  [v1][v1][v1][v2]          (kill one v1, now 4)
Step 3:  [v1][v1][v2][v2]
Step 4:  [v1][v2][v2][v2]
Done:    [v2][v2][v2][v2]
```

**Critical for banking**: if the new pod fails readinessProbe, rollout **pauses** — old pods keep serving traffic. This is your safety net.

### Recreate
Kills ALL old pods first, then starts new ones. Causes downtime. Use only when you cannot run two versions simultaneously (e.g., schema-breaking DB migration without backward compatibility).

```
[v1][v1][v1] → [] → [v2][v2][v2]
```

---

## Rollout Lifecycle & Commands

```bash
# Apply a change
kubectl apply -f deployment.yaml

# Watch rollout progress in real time
kubectl rollout status deployment/payment-service

# Pause mid-rollout (canary-style manual gate)
kubectl rollout pause deployment/payment-service

# Resume
kubectl rollout resume deployment/payment-service

# View revision history
kubectl rollout history deployment/payment-service
# REVISION  CHANGE-CAUSE
# 1         initial deploy v1.2.0
# 2         upgrade to v1.3.0 — CVE-2024-1234 patch

# Inspect a specific revision
kubectl rollout history deployment/payment-service --revision=2

# Rollback to previous
kubectl rollout undo deployment/payment-service

# Rollback to specific revision
kubectl rollout undo deployment/payment-service --to-revision=1

# Manually trigger rollout without changing image (force pod restart)
kubectl rollout restart deployment/payment-service
```

---

## Scaling

```bash
# Imperative (for quick ops / exams)
kubectl scale deployment payment-service --replicas=6

# Declarative (preferred in prod)
# Edit replicas in the YAML and kubectl apply

# HPA — auto-scale based on CPU/memory
kubectl autoscale deployment payment-service --min=3 --max=10 --cpu-percent=70
```

HPA manifest:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: payment-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: payment-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: AverageValue
          averageValue: 400Mi
```

---

## Deployment vs ReplicaSet internals

Understanding this is critical for exams and debugging:

```bash
kubectl get replicasets -n fintech
# NAME                          DESIRED   CURRENT   READY
# payment-service-7d9f8c4b6     3         3         3    ← active (v1.3.0)
# payment-service-6c8e7b3a5     0         0         0    ← retained for rollback (v1.2.0)
```

ReplicaSet name = `<deployment-name>-<pod-template-hash>`. The hash is derived from the pod template spec — same template = same hash = same RS reused (no new rollout).

**What triggers a new rollout (new RS)?**
Any change to `spec.template` — image, env vars, resource limits, labels, configmap reference, etc.

**What does NOT trigger a rollout?**
Changing `spec.replicas` or `spec.strategy` — these update in place.

---

## Deployment Conditions

```bash
kubectl describe deployment payment-service
# Conditions:
#   Available      True   MinimumReplicasAvailable
#   Progressing    True   NewReplicaSetAvailable
```

| Condition | Meaning |
|---|---|
| `Available=True` | At least `minReadySeconds` worth of ready pods |
| `Progressing=True` | Rollout in progress or complete |
| `Progressing=False` | **Deadline exceeded** — rollout stuck/failed |

`progressDeadlineSeconds` is your rollout timeout. When exceeded, the Deployment is marked as failed but pods are NOT automatically rolled back — you must intervene.

---

## minReadySeconds

Often overlooked, critical for stability:

```yaml
spec:
  minReadySeconds: 20   # pod must be Ready for 20s before being considered "available"
```

Without this, a pod that passes readinessProbe briefly then crashes would still allow the rollout to proceed too fast. Set this to allow your app to fully warm up (caches, connection pools, etc.) before the next pod is replaced.

---

## Exam Scenarios (CKA / CKAD style)

---

**Scenario 1 — Create a Deployment imperatively (fastest in exam)**
```bash
kubectl create deployment nginx-app \
  --image=nginx:1.25 \
  --replicas=3 \
  --port=80 \
  --dry-run=client -o yaml > deployment.yaml
# edit if needed, then:
kubectl apply -f deployment.yaml
```

---

**Scenario 2 — Update image and verify rollout**
```bash
# Imperative image update
kubectl set image deployment/payment-service app=payment-service:1.4.0

# Watch it roll
kubectl rollout status deployment/payment-service
# Waiting for deployment "payment-service" rollout to finish: 1 out of 3 new replicas have been updated...
# deployment "payment-service" successfully rolled out
```

---

**Scenario 3 — Rollout stuck, pods not becoming ready**
```bash
kubectl rollout status deployment/payment-service
# Waiting for deployment "payment-service" rollout to finish: 1 out of 3...
# (hangs)

kubectl get pods
# payment-service-new-xxx   0/1   CrashLoopBackOff

kubectl describe deployment payment-service   # check Conditions
kubectl logs payment-service-new-xxx          # find root cause

# Roll back
kubectl rollout undo deployment/payment-service
kubectl rollout status deployment/payment-service  # confirm recovery
```

---

**Scenario 4 — Scale to 0 (maintenance / kill switch)**
```bash
kubectl scale deployment payment-service --replicas=0
# All pods terminated, Deployment object retained
kubectl scale deployment payment-service --replicas=3
# Pods come back
```
Useful in banking for emergency stop during incident or off-hours batch maintenance.

---

**Scenario 5 — Canary deployment (manual, no Istio)**
```yaml
# production-deployment.yaml — 9 replicas of stable
# canary-deployment.yaml    — 1 replica of new version
# Both targeted by the same Service via shared label: app: payment-service
```
Traffic split ≈ 90/10 based on replica ratio. Promote by scaling up canary and scaling down stable.

---

**Scenario 6 — Resource quota enforcement causing failed deployment**
```bash
kubectl describe replicaset payment-service-xxx
# Events:
#   Error creating: pods "payment-service-xxx" is forbidden:
#   exceeded quota: namespace-quota, requested: cpu=250m,
#   used: cpu=1900m, limited: cpu=2000m

kubectl describe resourcequota -n fintech   # check current usage
# Either free up resources or request quota increase
```

---

**Scenario 7 — Record change-cause for audit trail**
```bash
kubectl annotate deployment payment-service \
  kubernetes.io/change-cause="hotfix: null pointer in FX conversion — ticket FIN-8821"

kubectl rollout history deployment/payment-service
# REVISION  CHANGE-CAUSE
# 3         hotfix: null pointer in FX conversion — ticket FIN-8821
```

---

## Banking Context Relevance

| Concern | Deployment Feature |
|---|---|
| Zero-downtime release during trading hours | RollingUpdate + readinessProbe |
| Emergency rollback for failed patch | `rollout undo` in seconds |
| Audit trail for change management | `change-cause` annotation + `rollout history` |
| Blast radius containment | `maxUnavailable=0` (never kill old pod before new one ready) |
| Regulatory availability SLA | HPA + PodDisruptionBudget |
| Security patching urgency | `rollout restart` to cycle pods onto patched base image |

**Production-hardened strategy for a critical payment service:**
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0    # never drop below desired capacity
    maxSurge: 1          # add one extra pod at a time (conservative)
minReadySeconds: 30      # wait 30s of sustained readiness before proceeding
progressDeadlineSeconds: 300
```

This guarantees: full capacity maintained throughout rollout, automatic pause if new version is unhealthy, 5-minute window before declaring failure.