# Kubernetes Jobs & CronJobs: From Concepts to Examples

## The Problem They Solve

Regular Pods are designed for long-running processes. If a Pod exits, Kubernetes restarts it. But some workloads are **finite** — run once, succeed, and stop. That's what `Job` and `CronJob` are for.

---

## Job

### Core Concept

A `Job` creates one or more Pods to **run a task to completion**. Kubernetes tracks successful completions and retries on failure. Once the desired completions are reached, the Job is done.

### Key Fields

| Field | Purpose |
|---|---|
| `completions` | Total successful Pod completions needed (default: 1) |
| `parallelism` | How many Pods run simultaneously |
| `backoffLimit` | Max retries before marking Job as failed (default: 6) |
| `activeDeadlineSeconds` | Hard timeout for the entire Job |
| `ttlSecondsAfterFinished` | Auto-cleanup after completion |

### Completion Modes

**Sequential (default)** — `completions: 5, parallelism: 1` → runs 5 pods one at a time  
**Parallel fixed** — `completions: 5, parallelism: 3` → runs up to 3 at once, until 5 succeed  
**Work queue** — `completions` unset, `parallelism: N` → pods pull work from a queue, Job ends when any pod exits with 0

---

### Example 1: Simple One-shot Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-schema-migration
spec:
  backoffLimit: 3
  activeDeadlineSeconds: 300       # fail if not done in 5 min
  ttlSecondsAfterFinished: 600     # auto-delete 10 min after finish
  template:
    spec:
      restartPolicy: Never          # Never or OnFailure — NOT Always
      containers:
        - name: migrator
          image: flyway/flyway:9
          args: ["migrate"]
          env:
            - name: FLYWAY_URL
              value: "jdbc:postgresql://postgres:5432/bankdb"
            - name: FLYWAY_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: password
```

> `restartPolicy: Never` → on failure, a **new Pod** is created (up to `backoffLimit`)  
> `restartPolicy: OnFailure` → the **same Pod** restarts in place

---

### Example 2: Parallel Batch Processing Job

Scenario: process 100 trade reconciliation files, 10 at a time.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: trade-reconciliation
spec:
  completions: 100
  parallelism: 10
  backoffLimit: 5
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: reconciler
          image: mybank/reconciler:1.2
          env:
            - name: JOB_COMPLETION_INDEX   # injected by K8s (Indexed completion mode)
              valueFrom:
                fieldRef:
                  fieldPath: metadata.annotations['batch.kubernetes.io/job-completion-index']
```

With **Indexed** mode, each pod gets a unique index (0–99), so you can deterministically map index → file:

```yaml
spec:
  completionMode: Indexed   # adds the index env var automatically
  completions: 100
  parallelism: 10
```

---

## CronJob

### Core Concept

A `CronJob` is a **Job factory** — it creates a new `Job` object on a schedule using standard Unix cron syntax. Think of it as `crontab` for your cluster.

```
┌─────── minute (0-59)
│ ┌───── hour (0-23)
│ │ ┌─── day of month (1-31)
│ │ │ ┌─ month (1-12)
│ │ │ │ ┌ day of week (0-6, Sun=0)
│ │ │ │ │
* * * * *
```

### Key Fields

| Field | Purpose |
|---|---|
| `schedule` | Cron expression |
| `concurrencyPolicy` | `Allow` / `Forbid` / `Replace` |
| `startingDeadlineSeconds` | If scheduler misses the time, how late can it still start |
| `successfulJobsHistoryLimit` | How many completed Jobs to keep (default: 3) |
| `failedJobsHistoryLimit` | How many failed Jobs to keep (default: 1) |
| `suspend` | Pause the CronJob without deleting it |

### `concurrencyPolicy` Explained

```
Allow  → overlapping runs permitted (risky for DB jobs)
Forbid → skip new run if previous is still running
Replace→ kill previous run, start new one
```

---

### Example 3: End-of-Day Settlement Report (Banking Relevant)

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: eod-settlement-report
  namespace: banking-ops
spec:
  schedule: "30 17 * * 1-5"        # 5:30 PM, Mon-Fri (trading days)
  timeZone: "Asia/Shanghai"         # K8s 1.27+ supports timeZone natively
  concurrencyPolicy: Forbid         # never run two settlements at once
  startingDeadlineSeconds: 300      # if missed, only retry within 5 min
  successfulJobsHistoryLimit: 5
  failedJobsHistoryLimit: 3
  suspend: false
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 1800   # max 30 min runtime
      template:
        spec:
          restartPolicy: Never
          serviceAccountName: settlement-sa
          containers:
            - name: settlement
              image: mybank/settlement-engine:3.1
              resources:
                requests:
                  memory: "512Mi"
                  cpu: "500m"
                limits:
                  memory: "1Gi"
                  cpu: "1"
              envFrom:
                - secretRef:
                    name: settlement-db-creds
              volumeMounts:
                - name: report-storage
                  mountPath: /reports
          volumes:
            - name: report-storage
              persistentVolumeClaim:
                claimName: report-pvc
```

---

### Example 4: A-Share Market Data Sync (Your Domain!)

Sync stock data every minute during trading hours:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ashare-market-data-sync
spec:
  schedule: "* 9-15 * * 1-5"       # every minute, 9am-3pm, weekdays
  concurrencyPolicy: Replace         # always use latest run, drop stale
  successfulJobsHistoryLimit: 2
  failedJobsHistoryLimit: 2
  jobTemplate:
    spec:
      backoffLimit: 0                # no retry — next cron tick will catch up
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: market-sync
              image: mybank/market-data-fetcher:latest
              env:
                - name: EXCHANGE
                  value: "SSE,SZSE"
                - name: DATA_SINK
                  value: "kafka://kafka-broker:9092/market-tick"
```

---

## Operational Patterns

### Manually Triggering a CronJob (useful for testing)

```bash
# Trigger immediately from existing CronJob template
kubectl create job --from=cronjob/eod-settlement-report manual-run-001 -n banking-ops

# Watch the job
kubectl get jobs -w -n banking-ops

# Stream logs
kubectl logs -f -l job-name=manual-run-001 -n banking-ops
```

### Suspend / Resume

```bash
# Pause during maintenance window
kubectl patch cronjob eod-settlement-report -p '{"spec":{"suspend":true}}'

# Resume
kubectl patch cronjob eod-settlement-report -p '{"spec":{"suspend":false}}'
```

### Debugging Failed Jobs

```bash
kubectl describe job <job-name>          # see events, failure reasons
kubectl get pods --selector=job-name=<job-name> --show-all
kubectl logs <failed-pod-name> --previous
```

---

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| CronJob creating duplicate runs | Set `concurrencyPolicy: Forbid` |
| Timezone confusion (UTC vs local) | Use `timeZone` field (K8s ≥1.27) or normalize schedule to UTC |
| Jobs accumulating and eating resources | Always set `ttlSecondsAfterFinished` or `successfulJobsHistoryLimit` |
| `restartPolicy: Always` on Job Pod | Not allowed — use `Never` or `OnFailure` |
| Missing `startingDeadlineSeconds` | A missed cron with a long backlog can spawn many Jobs on recovery |
| No resource limits on batch pods | Batch jobs can starve online services — always set `resources` |

---

## Job vs CronJob vs Deployment — Quick Mental Model

```
Deployment   → "keep N replicas alive forever"          (web servers, APIs)
Job          → "run this task until it succeeds once"   (migrations, batch)
CronJob      → "run this Job on a schedule"             (reports, syncs, cleanup)
```

This maps well to banking: your **trading engine** is a Deployment, your **EOD settlement** is a CronJob, and your **one-time DB migration** is a Job.