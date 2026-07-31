# Kubernetes Pod — Deep Dive

## Concept

A **Pod** is the smallest deployable unit in Kubernetes. It's a wrapper around one or more containers that share:

- **Network namespace** — same IP address, same `localhost`, same port space
- **IPC namespace** — can communicate via shared memory / semaphores
- **Storage volumes** — mounted into each container in the pod

Think of a pod as a "logical host" — much like a VM used to be, but lightweight and ephemeral.

The key mental model: **Kubernetes doesn't schedule containers, it schedules Pods.**

---

## Anatomy of a Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
  labels:
    app: my-app
    env: prod
spec:
  initContainers:           # run to completion BEFORE main containers start
    - name: db-migration
      image: flyway:9
      command: ["flyway", "migrate"]

  containers:
    - name: app
      image: my-bank-service:1.2.3
      ports:
        - containerPort: 8080
      resources:
        requests:            # what scheduler uses for placement
          cpu: "250m"
          memory: "256Mi"
        limits:              # enforced at runtime (cgroups)
          cpu: "500m"
          memory: "512Mi"
      env:
        - name: DB_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
      readinessProbe:        # gates traffic (removes from Service endpoints)
        httpGet:
          path: /actuator/health/readiness
          port: 8080
        initialDelaySeconds: 10
        periodSeconds: 5
      livenessProbe:         # triggers restart on failure
        httpGet:
          path: /actuator/health/liveness
          port: 8080

    - name: log-shipper      # sidecar pattern
      image: fluent-bit:2.1
      volumeMounts:
        - name: app-logs
          mountPath: /var/log/app

  volumes:
    - name: app-logs
      emptyDir: {}

  restartPolicy: Always      # Always | OnFailure | Never
```

---

## Pod Lifecycle

```
Pending → Running → Succeeded / Failed
              ↑
           Unknown (node lost contact)
```

| Phase | Meaning |
|---|---|
| `Pending` | Accepted by API server; waiting for scheduling or image pull |
| `Running` | At least one container running |
| `Succeeded` | All containers exited 0 (typical for Jobs) |
| `Failed` | At least one container exited non-zero |
| `Unknown` | Node unreachable |

Container states within a running pod: `Waiting`, `Running`, `Terminated`

---

## Key Patterns

### 1. Sidecar
A helper container augmenting the main app — log shippers (Fluent Bit), service mesh proxies (Envoy/Istio), secret injectors (Vault Agent).

### 2. Init Container
Runs sequentially before app containers. Ideal for: DB migrations, waiting for dependencies (`until nslookup kafka; do sleep 2; done`), config hydration.

### 3. Ambassador
A proxy container that abstracts external services — your app talks to `localhost:6379`, ambassador handles Redis cluster routing.

### 4. Adapter
Normalizes output format — e.g., translates app metrics to Prometheus format.

---

## Networking Deep Dive

Every pod gets its own IP (from the CNI plugin — Calico, Cilium, Flannel, etc.). Key rules:

- Pod-to-pod communication is flat (no NAT) within the cluster
- Containers inside the same pod share `127.0.0.1` — your app on port `8080` and sidecar on `9090` talk via localhost
- External traffic reaches pods via `Service` → `kube-proxy` → pod IP

```
[Client] → Service (ClusterIP/LoadBalancer) → iptables/IPVS rules → Pod IP:port
```

---

## Pod vs Higher-Level Abstractions

| Abstraction | Use Case |
|---|---|
| **Pod** (raw) | Never in prod; used for debugging |
| **Deployment** | Stateless services; rolling updates, rollbacks |
| **StatefulSet** | Stateful apps (Kafka, Postgres); stable network identity + ordered scaling |
| **DaemonSet** | One pod per node (log agents, monitoring) |
| **Job / CronJob** | Batch / scheduled tasks |
| **ReplicaSet** | Managed by Deployment; rarely used directly |

---

## Scheduling & Resource Management

The scheduler selects a node based on:

1. **Filtering** — `nodeSelector`, `nodeAffinity`, taints/tolerations, resource availability
2. **Scoring** — least requested, spread across zones, etc.

```yaml
affinity:
  podAntiAffinity:            # spread replicas across nodes
    requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels:
            app: my-app
        topologyKey: kubernetes.io/hostname
tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"
```

`requests` → used for scheduling decisions  
`limits` → enforced via cgroups; CPU throttled, memory OOMKilled

---

## Exam Scenarios (CKA / CKAD style)

**Scenario 1 — Pod crashing, CrashLoopBackOff**
```bash
kubectl describe pod my-app          # check Events section
kubectl logs my-app --previous       # logs from last crashed container
kubectl logs my-app -c sidecar       # specific container logs
```
Common causes: bad env var (missing Secret), wrong command, liveness probe misconfigured.

---

**Scenario 2 — Create a multi-container pod with shared volume**
```yaml
spec:
  containers:
    - name: writer
      image: busybox
      command: ["/bin/sh", "-c", "while true; do date >> /data/out.txt; sleep 5; done"]
      volumeMounts:
        - name: shared
          mountPath: /data
    - name: reader
      image: busybox
      command: ["/bin/sh", "-c", "tail -f /data/out.txt"]
      volumeMounts:
        - name: shared
          mountPath: /data
  volumes:
    - name: shared
      emptyDir: {}
```

---

**Scenario 3 — Pod scheduled only on nodes labeled `tier=backend`**
```yaml
spec:
  nodeSelector:
    tier: backend
```
Or use `nodeAffinity` for more expressive rules (preferred vs required).

---

**Scenario 4 — Debug a running pod**
```bash
kubectl exec -it my-app -- /bin/sh
kubectl exec -it my-app -c sidecar -- /bin/bash
# ephemeral debug container (K8s 1.23+)
kubectl debug -it my-app --image=busybox --target=app
```

---

**Scenario 5 — Pod stuck in Pending**
```bash
kubectl describe pod my-app
# Look for: Insufficient cpu/memory, no nodes match selector,
#           PVC not bound, image pull failure
```

---

**Scenario 6 — Static Pod (relevant for control plane)**

Placed as manifests in `/etc/kubernetes/manifests/` on the node. Kubelet manages them directly — no API server needed. This is how `kube-apiserver`, `etcd`, `kube-scheduler` run.

---

## Banking Context Relevance

In a banking IT context, pods are typically combined with:

- **PodDisruptionBudgets (PDB)** — ensure minimum replicas during node maintenance (critical for payment services)
- **NetworkPolicies** — pod-level firewall rules, isolate PCI-DSS scope
- **SecurityContext** — `runAsNonRoot`, `readOnlyRootFilesystem`, drop Linux capabilities
- **ResourceQuotas** per namespace — prevent one team's runaway pods from starving others

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
```

This is usually mandated by compliance (MAS TRM, HKMA guidelines, etc.) in financial institutions.