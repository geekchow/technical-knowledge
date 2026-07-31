# 🧪 CKAD Mock Exam — Intermediate Level
### killer.sh Style Simulator

---

> ⏱️ **Total Time: 120 minutes** | 📊 **Total Score: 100 points** | ✅ **Pass Score: 66 points**
> 
> **Rules:** All work must be done via `kubectl` or YAML manifests. You may use `kubectl explain`, `k8s.io/docs` during the real exam. Each task has a suggested time budget — **don't get stuck, move on**.
>
> **Cluster context will be set for you at the start of each task. Always run the context switch command shown.**

---

## 📋 TASK INDEX

| # | Topic | Points | Time Budget |
|---|-------|--------|-------------|
| 1 | Pods & Init Containers | 4 | 4 min |
| 2 | Multi-Container Pod | 5 | 5 min |
| 3 | ConfigMap + Env Injection | 4 | 4 min |
| 4 | Secrets | 4 | 4 min |
| 5 | Deployment Rolling Update | 7 | 6 min |
| 6 | Jobs & CronJobs | 6 | 6 min |
| 7 | Resource Limits & Requests | 4 | 4 min |
| 8 | Probes (Liveness/Readiness) | 7 | 7 min |
| 9 | Service + DNS | 6 | 6 min |
| 10 | NetworkPolicy | 7 | 8 min |
| 11 | Ingress | 7 | 7 min |
| 12 | PersistentVolume + PVC | 8 | 8 min |
| 13 | ServiceAccount + RBAC | 8 | 8 min |
| 14 | SecurityContext | 6 | 6 min |
| 15 | Canary Deployment | 7 | 8 min |
| 16 | Helm | 6 | 5 min |
| 17 | Custom Resource / CRD Check | 4 | 4 min |
| 18 | Troubleshooting | 10 | 10 min |

---

## 🔷 TASK 1 — Pods & Init Containers `[4 pts]` ⏱ 4 min

```bash
# Set context
kubectl config use-context k8s-ckad
```

**Scenario:**  
Create a Pod named `init-demo` in namespace `ckad-prep` with:

- **Init container:** named `delay`, image `busybox:1.36`, runs `sleep 10` then exits 0
- **Main container:** named `app`, image `nginx:1.25`, only starts after init completes
- Pod must remain **Running** after init finishes

Write the manifest to `/tmp/task1.yaml` and apply it.

<details>
<summary>💡 Hint (click only if stuck)</summary>

Use `spec.initContainers[]` alongside `spec.containers[]`. Init containers run sequentially and must complete (exit 0) before main containers start.

</details>

<details>
<summary>✅ Answer</summary>

```yaml
# /tmp/task1.yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-demo
  namespace: ckad-prep
spec:
  initContainers:
  - name: delay
    image: busybox:1.36
    command: ["sleep", "10"]
  containers:
  - name: app
    image: nginx:1.25
```

```bash
kubectl apply -f /tmp/task1.yaml
kubectl get pod init-demo -n ckad-prep -w
```

**Verify:** Status goes `Init:0/1` → `Running`

</details>

---

## 🔷 TASK 2 — Multi-Container Pod (Sidecar) `[5 pts]` ⏱ 5 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
Create a Pod named `log-sidecar` in namespace `ckad-prep`:

- **Container 1:** `app-writer`, image `busybox:1.36`, runs:  
  `sh -c "while true; do echo $(date) >> /var/log/app.log; sleep 2; done"`
- **Container 2:** `log-reader`, image `busybox:1.36`, runs:  
  `sh -c "tail -f /var/log/app.log"`
- Both containers must **share** the log volume via an `emptyDir`
- Volume mounted at `/var/log` in both containers

<details>
<summary>✅ Answer</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: log-sidecar
  namespace: ckad-prep
spec:
  volumes:
  - name: shared-log
    emptyDir: {}
  containers:
  - name: app-writer
    image: busybox:1.36
    command: ["sh", "-c", "while true; do echo $(date) >> /var/log/app.log; sleep 2; done"]
    volumeMounts:
    - name: shared-log
      mountPath: /var/log
  - name: log-reader
    image: busybox:1.36
    command: ["sh", "-c", "tail -f /var/log/app.log"]
    volumeMounts:
    - name: shared-log
      mountPath: /var/log
```

```bash
# Verify sidecar is reading logs
kubectl logs log-sidecar -c log-reader -n ckad-prep
```

</details>

---

## 🔷 TASK 3 — ConfigMap + Env Injection `[4 pts]` ⏱ 4 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
1. Create a ConfigMap named `app-config` in namespace `ckad-prep` with:
   - `DB_HOST=postgres.internal`
   - `DB_PORT=5432`
   - `LOG_LEVEL=INFO`

2. Create a Pod named `config-consumer`, image `busybox:1.36`, that:
   - Injects **all keys** from `app-config` as environment variables
   - Runs `env` and exits

3. After running, confirm `DB_HOST` appears in pod logs.

<details>
<summary>✅ Answer</summary>

```bash
kubectl create configmap app-config \
  --from-literal=DB_HOST=postgres.internal \
  --from-literal=DB_PORT=5432 \
  --from-literal=LOG_LEVEL=INFO \
  -n ckad-prep
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: config-consumer
  namespace: ckad-prep
spec:
  restartPolicy: Never
  containers:
  - name: main
    image: busybox:1.36
    command: ["env"]
    envFrom:
    - configMapRef:
        name: app-config
```

```bash
kubectl logs config-consumer -n ckad-prep | grep DB_HOST
# Expected: DB_HOST=postgres.internal
```

</details>

---

## 🔷 TASK 4 — Secrets `[4 pts]` ⏱ 4 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
1. Create a Secret named `db-secret` in namespace `ckad-prep`:
   - `username=admin`
   - `password=S3cur3P@ss`

2. Create a Pod named `secret-consumer`, image `busybox:1.36`, command `env`:
   - Mount `username` as env var `DB_USER`
   - Mount `password` as env var `DB_PASS`
   - `restartPolicy: Never`

<details>
<summary>✅ Answer</summary>

```bash
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password='S3cur3P@ss' \
  -n ckad-prep
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-consumer
  namespace: ckad-prep
spec:
  restartPolicy: Never
  containers:
  - name: main
    image: busybox:1.36
    command: ["env"]
    env:
    - name: DB_USER
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: username
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
```

</details>

---

## 🔷 TASK 5 — Deployment Rolling Update `[7 pts]` ⏱ 6 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
There is an existing Deployment `web-app` in namespace `ckad-prep` running image `nginx:1.23`.

Perform the following **without downtime**:

1. Update the image to `nginx:1.25`
2. Set `maxSurge=2`, `maxUnavailable=0` in the rolling update strategy
3. Set `replicas=4`
4. **Annotate** the rollout with `change-cause="upgrade to nginx 1.25"`
5. After rollout, **verify** rollout history shows 2 revisions

<details>
<summary>✅ Answer</summary>

```bash
# If deployment doesn't exist, create it first:
kubectl create deployment web-app --image=nginx:1.23 --replicas=4 -n ckad-prep

# Patch strategy
kubectl patch deployment web-app -n ckad-prep -p '{
  "spec": {
    "strategy": {
      "rollingUpdate": {"maxSurge": 2, "maxUnavailable": 0}
    }
  }
}'

# Update image with annotation
kubectl set image deployment/web-app nginx=nginx:1.25 -n ckad-prep
kubectl annotate deployment/web-app kubernetes.io/change-cause="upgrade to nginx 1.25" -n ckad-prep

# Verify
kubectl rollout status deployment/web-app -n ckad-prep
kubectl rollout history deployment/web-app -n ckad-prep
```

</details>

---

## 🔷 TASK 6 — Jobs & CronJobs `[6 pts]` ⏱ 6 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**

**Part A (3pts):** Create a Job named `batch-pi` in namespace `ckad-prep`:
- Image: `perl:5.34`, command: `perl -Mbignum=bpi -wle 'print bpi(500)'`
- `completions: 1`, `backoffLimit: 2`

**Part B (3pts):** Create a CronJob named `cleanup-job` in namespace `ckad-prep`:
- Runs **every 5 minutes**
- Image: `busybox:1.36`, command: `echo "cleanup done"`
- `successfulJobsHistoryLimit: 3`
- `failedJobsHistoryLimit: 1`

<details>
<summary>✅ Answer</summary>

```bash
# Part A
kubectl create job batch-pi \
  --image=perl:5.34 \
  -n ckad-prep \
  -- perl -Mbignum=bpi -wle 'print bpi(500)'

kubectl patch job batch-pi -n ckad-prep \
  -p '{"spec":{"backoffLimit":2}}'
```

```yaml
# Part B - cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cleanup-job
  namespace: ckad-prep
spec:
  schedule: "*/5 * * * *"
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
          - name: cleanup
            image: busybox:1.36
            command: ["echo", "cleanup done"]
```

</details>

---

## 🔷 TASK 7 — Resource Limits & Requests `[4 pts]` ⏱ 4 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
Create a Pod named `resource-pod` in namespace `ckad-prep`, image `nginx:1.25`:

| | CPU | Memory |
|--|-----|--------|
| **requests** | 100m | 64Mi |
| **limits** | 500m | 128Mi |

Also create a `LimitRange` named `default-limits` in the same namespace that sets:
- Default CPU limit: `200m`
- Default memory limit: `256Mi`

<details>
<summary>✅ Answer</summary>

```yaml
# limitrange.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: ckad-prep
spec:
  limits:
  - type: Container
    default:
      cpu: 200m
      memory: 256Mi
---
apiVersion: v1
kind: Pod
metadata:
  name: resource-pod
  namespace: ckad-prep
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    resources:
      requests:
        cpu: 100m
        memory: 64Mi
      limits:
        cpu: 500m
        memory: 128Mi
```

</details>

---

## 🔷 TASK 8 — Liveness & Readiness Probes `[7 pts]` ⏱ 7 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
Create a Deployment named `probe-app` in namespace `ckad-prep`, image `nginx:1.25`, `replicas: 2`:

- **Readiness probe:** HTTP GET `/` on port `80`, `initialDelaySeconds: 5`, `periodSeconds: 10`
- **Liveness probe:** HTTP GET `/healthz` on port `80`, `initialDelaySeconds: 15`, `failureThreshold: 3`, `periodSeconds: 20`
- **Startup probe:** HTTP GET `/` on port `80`, `failureThreshold: 30`, `periodSeconds: 5`

> ⚠️ The startup probe gives the app 150 seconds (30×5) to start before liveness kicks in.

<details>
<summary>✅ Answer</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: probe-app
  namespace: ckad-prep
spec:
  replicas: 2
  selector:
    matchLabels:
      app: probe-app
  template:
    metadata:
      labels:
        app: probe-app
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
        startupProbe:
          httpGet:
            path: /
            port: 80
          failureThreshold: 30
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /healthz
            port: 80
          initialDelaySeconds: 15
          failureThreshold: 3
          periodSeconds: 20
```

</details>

---

## 🔷 TASK 9 — Service + DNS `[6 pts]` ⏱ 6 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
There is a Deployment `backend` running in namespace `ckad-prep` with label `app=backend`, exposing port `8080`.

1. Expose it as a **ClusterIP Service** named `backend-svc` on port `80`, targeting container port `8080`
2. Create a Pod named `dns-test`, image `busybox:1.36`, in namespace `ckad-prep` that runs:  
   `nslookup backend-svc.ckad-prep.svc.cluster.local`  
   then exits (`restartPolicy: Never`)
3. Confirm DNS resolves correctly from the pod logs

<details>
<summary>✅ Answer</summary>

```bash
kubectl expose deployment backend \
  --name=backend-svc \
  --port=80 \
  --target-port=8080 \
  -n ckad-prep
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: dns-test
  namespace: ckad-prep
spec:
  restartPolicy: Never
  containers:
  - name: dns
    image: busybox:1.36
    command: ["nslookup", "backend-svc.ckad-prep.svc.cluster.local"]
```

```bash
kubectl logs dns-test -n ckad-prep
# Should show: Address: <ClusterIP>
```

</details>

---

## 🔷 TASK 10 — NetworkPolicy `[7 pts]` ⏱ 8 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
In namespace `ckad-prep`:
- Pod `frontend` has label `role=frontend`
- Pod `backend` has label `role=backend`
- Pod `monitoring` has label `role=monitoring`

Create a NetworkPolicy named `backend-policy` that:
1. **Allows** ingress to `backend` pods **only** from `frontend` pods (port `8080`)
2. **Allows** ingress to `backend` pods from `monitoring` pods (port `9090`)  
3. **Denies** all other ingress to `backend`
4. **Allows** all egress from `backend`

<details>
<summary>✅ Answer</summary>

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: ckad-prep
spec:
  podSelector:
    matchLabels:
      role: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - port: 8080
  - from:
    - podSelector:
        matchLabels:
          role: monitoring
    ports:
    - port: 9090
  egress:
  - {}  # Allow all egress
```

> ⚠️ **Common trap:** Two separate `ingress[]` items (OR logic). Merging into one item with two `from[]` entries is also valid — but combining `ports` under one `from` block applies AND logic between source and port together. Keep them as separate rules to be safe.

</details>

---

## 🔷 TASK 11 — Ingress `[7 pts]` ⏱ 7 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
An nginx Ingress controller is already deployed. In namespace `ckad-prep`:

1. Service `web-svc` exists on port `80`
2. Service `api-svc` exists on port `3000`

Create an Ingress named `app-ingress` that routes:
- `app.example.com/` → `web-svc:80`
- `app.example.com/api` → `api-svc:3000`

TLS is **not** required. Set the IngressClass annotation to `nginx`.

<details>
<summary>✅ Answer</summary>

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: ckad-prep
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-svc
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-svc
            port:
              number: 3000
```

</details>

---

## 🔷 TASK 12 — PersistentVolume + PVC `[8 pts]` ⏱ 8 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**

**Part A:** Create a PersistentVolume named `data-pv`:
- `capacity: 2Gi`
- `accessModes: ReadWriteOnce`
- `hostPath: /mnt/data`
- `storageClassName: manual`
- `persistentVolumeReclaimPolicy: Retain`

**Part B:** Create a PersistentVolumeClaim named `data-pvc` in namespace `ckad-prep`:
- Request `1Gi`, `storageClassName: manual`, `ReadWriteOnce`

**Part C:** Create a Pod named `storage-pod`, image `nginx:1.25`, in `ckad-prep`:
- Mount the PVC at `/usr/share/nginx/html`
- Verify the PVC is bound: `kubectl get pvc -n ckad-prep`

<details>
<summary>✅ Answer</summary>

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: data-pv
spec:
  capacity:
    storage: 2Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/data
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
  namespace: ckad-prep
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: manual
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: storage-pod
  namespace: ckad-prep
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    volumeMounts:
    - name: data
      mountPath: /usr/share/nginx/html
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: data-pvc
```

</details>

---

## 🔷 TASK 13 — ServiceAccount + RBAC `[8 pts]` ⏱ 8 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
In namespace `ckad-prep`:

1. Create a ServiceAccount named `pod-reader-sa`
2. Create a Role named `pod-reader` that allows: `get`, `list`, `watch` on `pods`
3. Create a RoleBinding named `pod-reader-binding` that binds the role to `pod-reader-sa`
4. Create a Pod named `sa-pod`, image `bitnami/kubectl:latest`:
   - Uses `pod-reader-sa`
   - Runs: `kubectl get pods -n ckad-prep`
   - `restartPolicy: Never`
5. Confirm from pod logs that it can list pods

<details>
<summary>✅ Answer</summary>

```bash
kubectl create serviceaccount pod-reader-sa -n ckad-prep

kubectl create role pod-reader \
  --verb=get,list,watch \
  --resource=pods \
  -n ckad-prep

kubectl create rolebinding pod-reader-binding \
  --role=pod-reader \
  --serviceaccount=ckad-prep:pod-reader-sa \
  -n ckad-prep
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sa-pod
  namespace: ckad-prep
spec:
  serviceAccountName: pod-reader-sa
  restartPolicy: Never
  containers:
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["kubectl", "get", "pods", "-n", "ckad-prep"]
```

```bash
kubectl logs sa-pod -n ckad-prep
# Should list pods, not give 403
```

</details>

---

## 🔷 TASK 14 — SecurityContext `[6 pts]` ⏱ 6 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
Create a Pod named `secure-pod` in namespace `ckad-prep`, image `busybox:1.36`, command `sleep 3600`:

**Pod-level SecurityContext:**
- Run as user `1000`, group `3000`
- `fsGroup: 2000`

**Container-level SecurityContext:**
- `allowPrivilegeEscalation: false`
- `readOnlyRootFilesystem: true`
- `capabilities: drop: ["ALL"]`

Verify: `kubectl exec secure-pod -n ckad-prep -- id`  
Expected: `uid=1000 gid=3000`

<details>
<summary>✅ Answer</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
  namespace: ckad-prep
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
  containers:
  - name: app
    image: busybox:1.36
    command: ["sleep", "3600"]
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

</details>

---

## 🔷 TASK 15 — Canary Deployment `[7 pts]` ⏱ 8 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
A production Deployment `app-stable` runs `nginx:1.23` with `replicas: 4` and label `app=myapp, version=stable`.  
A Service `app-svc` selects on `app=myapp` (routes to all matching pods).

Implement a **canary deployment** sending ~25% traffic to new version:
1. Create Deployment `app-canary`, image `nginx:1.25`, `replicas: 1`, labels: `app=myapp, version=canary`
2. Confirm the Service now routes to **both** stable (4 pods) and canary (1 pod) = ~20% canary traffic
3. Scale `app-stable` to `3` replicas to achieve exactly **25% canary** (1 of 4 total pods)

<details>
<summary>✅ Answer</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
  namespace: ckad-prep
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
      version: canary
  template:
    metadata:
      labels:
        app: myapp
        version: canary
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
```

```bash
# Scale stable down to 3 for 25% canary ratio
kubectl scale deployment app-stable --replicas=3 -n ckad-prep

# Verify: 3 stable + 1 canary = 4 total, 25% canary
kubectl get pods -n ckad-prep -l app=myapp --show-labels
```

> 💡 **Key insight:** The Service selector `app=myapp` matches BOTH deployments. This is classic label-based canary in Kubernetes.

</details>

---

## 🔷 TASK 16 — Helm `[6 pts]` ⏱ 5 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**

1. Add the Bitnami Helm repo: `https://charts.bitnami.com/bitnami`
2. Install a release named `my-nginx` using chart `bitnami/nginx` in namespace `ckad-prep`, with:
   - `service.type=ClusterIP`
   - `replicaCount=2`
3. List all Helm releases in the namespace
4. Upgrade `my-nginx` to set `replicaCount=3`
5. Roll back `my-nginx` to revision 1

<details>
<summary>✅ Answer</summary>

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install my-nginx bitnami/nginx \
  --namespace ckad-prep \
  --set service.type=ClusterIP \
  --set replicaCount=2

helm list -n ckad-prep

helm upgrade my-nginx bitnami/nginx \
  --namespace ckad-prep \
  --set replicaCount=3

helm rollback my-nginx 1 -n ckad-prep

helm history my-nginx -n ckad-prep
```

</details>

---

## 🔷 TASK 17 — CRD Inspection `[4 pts]` ⏱ 4 min

```bash
kubectl config use-context k8s-ckad
```

**Scenario:**  
A CRD `backupconfigs.storage.mycompany.io` has been installed in the cluster.

1. List all CRDs in the cluster and find it
2. Describe the CRD to find its **group**, **version**, and **scope**
3. List all custom resources of this type across all namespaces
4. Extract just the `spec` field of the first resource using `jsonpath`

<details>
<summary>✅ Answer</summary>

```bash
# 1. List CRDs
kubectl get crds | grep backupconfigs

# 2. Describe
kubectl describe crd backupconfigs.storage.mycompany.io

# 3. List instances
kubectl get backupconfigs -A

# 4. Jsonpath on first resource
kubectl get backupconfigs -A -o jsonpath='{.items[0].spec}'
```

</details>

---

## 🔷 TASK 18 — Troubleshooting `[10 pts]` ⏱ 10 min

```bash
kubectl config use-context k8s-broken
```

> ⚠️ **This is the hardest task. Worth 10 points.**

**Scenario:**  
The following issues have been reported. Investigate and fix each one.

**Bug A (4pts):** Deployment `broken-deploy` in namespace `ckad-debug` has 0/3 pods running.  
Find the root cause and fix it. Common causes: wrong image name, missing ConfigMap/Secret, resource quota exceeded, node selector mismatch.

**Bug B (3pts):** Pod `crashing-pod` in namespace `ckad-debug` is in `CrashLoopBackOff`.  
Diagnose why and fix the manifest.

**Bug C (3pts):** Service `missing-backend` in namespace `ckad-debug` has **0 endpoints**.  
The pods appear Running but traffic never reaches them. Find and fix the label mismatch.

<details>
<summary>💡 Debugging Toolkit</summary>

```bash
# Check events
kubectl describe deployment broken-deploy -n ckad-debug
kubectl describe pod <pod-name> -n ckad-debug

# Check logs (including previous crash)
kubectl logs crashing-pod -n ckad-debug
kubectl logs crashing-pod -n ckad-debug --previous

# Check endpoints
kubectl get endpoints missing-backend -n ckad-debug
kubectl get pods -n ckad-debug --show-labels
kubectl describe service missing-backend -n ckad-debug
```

</details>

<details>
<summary>✅ Answer Framework</summary>

```bash
# Bug A - Typical fixes:
kubectl describe deploy broken-deploy -n ckad-debug
# → Fix image typo: kubectl set image deployment/broken-deploy ...
# → Or create missing configmap/secret
# → Or remove wrong nodeSelector

# Bug B - CrashLoopBackOff:
kubectl logs crashing-pod --previous -n ckad-debug
# → Fix command syntax, missing env var, or wrong entrypoint

# Bug C - Label mismatch:
kubectl get pods -n ckad-debug --show-labels
kubectl describe svc missing-backend -n ckad-debug
# Selector: app=backend  vs  pods labeled: app=Back-end  ← mismatch!
kubectl patch service missing-backend -n ckad-debug \
  -p '{"spec":{"selector":{"app":"Back-end"}}}'
# OR patch the pod labels to match service selector
```

</details>

---

## 📊 SCORE YOURSELF

| Score Range | Result |
|-------------|--------|
| 90–100 | 🏆 Outstanding — Ready for the real exam |
| 75–89 | ✅ Pass — Strong performance |
| 66–74 | ⚠️ Borderline pass — Review weak areas |
| < 66 | ❌ Not yet — Keep practicing |

---

## 🎯 What to Study Next (Based on Typical Weak Areas)

**If you struggled with 10 (NetworkPolicy):** AND/OR logic in `from[]` blocks is notoriously tricky. Practice at [networkpolicy.io](https://networkpolicy.io).

**If you struggled with 13 (RBAC):** Remember: Role → namespace-scoped. ClusterRole → cluster-wide. ServiceAccount must be in same namespace as RoleBinding.

**If you struggled with 18 (Troubleshooting):** This is 10 pts on the real exam. Practice: `describe`, `logs --previous`, `get events --sort-by='.lastTimestamp'`.

**Speed tip:** Alias these before your exam starts:
```bash
alias k=kubectl
export do="--dry-run=client -o yaml"
# Usage: k run mypod --image=nginx $do > pod.yaml
```

---

> 💬 **Ready to review answers, get more tasks, or drill a specific topic?** Just say which task number you want to go deep on!
