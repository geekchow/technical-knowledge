# Kubernetes Security: Deep Dive

## 1. SecurityContext

SecurityContext defines privilege and access control settings at the **Pod** or **Container** level. Container-level settings override Pod-level.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:          # Pod-level — applies to all containers
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    runAsNonRoot: true
  containers:
    - name: app
      image: my-app:1.0
      securityContext:      # Container-level — overrides pod-level
        runAsUser: 1001
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
          add: ["NET_BIND_SERVICE"]
```

### Key Fields

**`runAsUser` / `runAsGroup`**
- Forces the container process to run as a specific Linux UID/GID
- Overrides the `USER` directive in the Dockerfile
- Critical: many base images default to `root` (UID 0) — this overrides that

**`runAsNonRoot: true`**
- Kubernetes will **reject** the pod at admission if the container would run as root
- It checks the image's configured user — if UID is 0, pod fails to start with `CreateContainerConfigError`
- Best practice: combine with `runAsUser` to be explicit

**`allowPrivilegeEscalation: false`**
- Maps to Linux `no_new_privs` flag
- Prevents a process from gaining more privileges than its parent (e.g., via `setuid` binaries or `sudo`)
- Should **always** be `false` in production — this is what stops a `sudo` inside the container from working

**`capabilities`**
- Linux capabilities break root's omnipotence into discrete units
- Default Docker capabilities granted: `CHOWN`, `NET_RAW`, `SETUID`, `SETGID`, etc. — most are unnecessary
- Best practice pattern:

```yaml
capabilities:
  drop: ["ALL"]           # strip everything first
  add: ["NET_BIND_SERVICE"]  # only add what you need (e.g., bind port < 1024)
```

Common capabilities you might legitimately need:
| Capability | Use Case |
|---|---|
| `NET_BIND_SERVICE` | Bind to ports < 1024 |
| `SYS_TIME` | NTP sync containers |
| `CHOWN` | File ownership changes |
| `NET_ADMIN` | Network config (CNI plugins) |

---

## 2. ServiceAccount

A ServiceAccount is a **non-human identity** for pods to authenticate to the Kubernetes API server.

### Default Behavior (dangerous)
Every pod gets the `default` ServiceAccount automatically, and its token is **auto-mounted** at `/var/run/secrets/kubernetes.io/serviceaccount/token`. If your app is compromised, an attacker can call the K8s API with this token.

### Creating and Binding

```bash
# Create a dedicated ServiceAccount
kubectl create serviceaccount my-app-sa -n production
```

```yaml
# Disable auto-mount at SA level
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: production
automountServiceAccountToken: false   # <— disables for all pods using this SA
```

```yaml
# Bind to Pod — override at pod level if you need the token
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  serviceAccountName: my-app-sa
  automountServiceAccountToken: false   # <— belt-and-suspenders
  containers:
    - name: app
      image: my-app:1.0
```

### When do you actually need the token?
- Your app calls the Kubernetes API directly (operators, controllers, custom schedulers)
- Service meshes (Istio uses it for mTLS identity via SPIFFE/SVID)
- Vault agent injector sidecar

For a typical banking microservice that just serves HTTP — **you don't need it. Disable it.**

### Token Projection (modern approach)
Since K8s 1.20+, prefer **projected volumes** with short-lived, audience-bound tokens over the legacy long-lived secret-based tokens:

```yaml
volumes:
  - name: kube-token
    projected:
      sources:
        - serviceAccountToken:
            audience: my-service
            expirationSeconds: 3600
            path: token
```

---

## 3. RBAC

RBAC (Role-Based Access Control) controls **who** (subject) can do **what** (verb) on **which resources**.

### Core Objects

```
Subject (User/Group/ServiceAccount)
    └── RoleBinding / ClusterRoleBinding
            └── Role / ClusterRole
                    └── rules: [apiGroups, resources, verbs]
```

**Role vs ClusterRole**
| | Role | ClusterRole |
|---|---|---|
| Scope | Single namespace | Cluster-wide |
| Use for | App-specific perms | Node resources, PVs, CRDs, or reuse across namespaces |

### Example: App that reads ConfigMaps and Secrets

```yaml
# Role — namespace scoped
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: my-app-role
  namespace: production
rules:
  - apiGroups: [""]           # "" = core API group
    resources: ["configmaps"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["db-credentials"]   # lock down to specific secret name!
    verbs: ["get"]
---
# RoleBinding — binds Role to ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-rolebinding
  namespace: production
subjects:
  - kind: ServiceAccount
    name: my-app-sa
    namespace: production
roleRef:
  kind: Role
  name: my-app-role
  apiGroup: rbac.authorization.k8s.io
```

### ClusterRole + ClusterRoleBinding (cluster-wide)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: node-reader-binding
subjects:
  - kind: Group
    name: monitoring-team      # maps to --user or OIDC group claim
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: node-reader
  apiGroup: rbac.authorization.k8s.io
```

### `kubectl auth can-i` — your debugging best friend

```bash
# Can I delete pods in production?
kubectl auth can-i delete pods -n production

# Can a specific ServiceAccount list secrets?
kubectl auth can-i list secrets \
  --namespace production \
  --as system:serviceaccount:production:my-app-sa

# Full audit — what can this SA do?
kubectl auth can-i --list \
  --namespace production \
  --as system:serviceaccount:production:my-app-sa

# Impersonate a user
kubectl auth can-i create deployments \
  --as jane@company.com \
  -n staging
```

---

## How These Three Layers Work Together

```
Request to K8s API
        │
        ▼
┌─────────────────┐
│  Authentication │  ← ServiceAccount token / OIDC / cert
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Authorization  │  ← RBAC: Role + RoleBinding
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Admission Ctrl │  ← PodSecurity, OPA/Gatekeeper enforce SecurityContext policies
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Container     │  ← SecurityContext enforced by container runtime (containerd/runc)
│   Runtime       │    via Linux kernel: namespaces, cgroups, seccomp, capabilities
└─────────────────┘
```

### Banking Context Hardening Checklist
Given your domain, regulators (PCI-DSS, MAS TRM, DORA) will look for:

- `runAsNonRoot: true` + explicit `runAsUser` (non-zero)
- `allowPrivilegeEscalation: false` on every container
- `capabilities: drop: ["ALL"]` with minimal adds
- `readOnlyRootFilesystem: true` (write to emptyDir/PVC only)
- `automountServiceAccountToken: false` unless explicitly needed
- RBAC following **least privilege** — `resourceNames` to restrict specific secrets
- Separate ServiceAccounts per microservice (never share the `default`)
- Audit RBAC regularly with `kubectl auth can-i --list` per SA