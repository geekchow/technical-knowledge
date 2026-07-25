
## Kubernetes Storage Abstraction — Why & How

### The Core Problem First

In traditional deployments, storage is tightly coupled to the machine. In Kubernetes, **pods are ephemeral and can be scheduled on any node** — so you need a storage layer that is decoupled from both the pod lifecycle and the physical infrastructure. That's exactly what PV/PVC solves.

---

### The Abstraction Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEVELOPER'S WORLD                        │
│                                                                 │
│   Pod Spec                                                      │
│   ┌─────────────────────────────────┐                          │
│   │  containers:                    │                          │
│   │    - name: app                  │                          │
│   │  volumes:                       │                          │
│   │    - name: data                 │                          │
│   │      persistentVolumeClaim: ────┼──────┐                  │
│   │        claimName: my-pvc        │      │                  │
│   └─────────────────────────────────┘      │                  │
│                                            ▼                  │
│                              ┌─────────────────────────┐      │
│                              │   PVC (PersistentVolume  │      │
│                              │        Claim)            │      │
│                              │                          │      │
│                              │  storageClassName: fast  │      │
│                              │  accessModes:            │      │
│                              │    - ReadWriteOnce       │      │
│                              │  resources:              │      │
│                              │    requests:             │      │
│                              │      storage: 10Gi       │      │
│                              └──────────┬───────────────┘      │
│                                         │  binding (1:1)       │
└─────────────────────────────────────────┼──────────────────────┘
                                          │
┌─────────────────────────────────────────┼──────────────────────-┐
│                   CLUSTER ADMIN'S WORLD │                       │
│                                         ▼                       │
│                              ┌─────────────────────────┐        │
│                              │   PV (PersistentVolume)  │       │
│                              │                          │       │
│                              │  storageClassName: fast  │       │
│                              │  accessModes:            │       │
│                              │    - ReadWriteOnce       │       │
│                              │  capacity: 20Gi          │       │
│                              │  reclaimPolicy: Retain   │       │
│                              └──────────┬───────────────┘       │
│                                         │                       │
│              ┌──────────────────────────┼───────────────┐       │
│              ▼                          ▼               ▼       │
│       ┌────────────┐           ┌──────────────┐  ┌──────────┐   │
│       │  AWS EBS   │           │  NFS Server  │  │  GCE PD  │   │
│       └────────────┘           └──────────────┘  └──────────┘   │
│                                                                 │
│                    StorageClass (provisioner)                   │
│       ┌──────────────────────────────────────────────────┐      │
│       │  name: fast                                      │      │
│       │  provisioner: ebs.csi.aws.com                    │      │
│       │  parameters: { type: gp3, iops: "3000" }         │      │
│       └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

---

### PV / PVC Deep Dive

**PersistentVolume (PV)** — cluster-level resource, provisioned by admin (or dynamically via StorageClass). It's the actual storage asset.

**PersistentVolumeClaim (PVC)** — namespace-level resource, created by developer. It's a *request* for storage. Kubernetes binds a matching PV to it.

The binding is **1:1** — once a PV is bound to a PVC, no other PVC can claim it, even if the PV has remaining capacity.

#### Access Modes — Critical to Understand

| Mode | Abbreviation | Meaning |
|---|---|---|
| `ReadWriteOnce` | RWO | Mounted read-write by **one node** |
| `ReadOnlyMany` | ROX | Mounted read-only by **many nodes** |
| `ReadWriteMany` | RWX | Mounted read-write by **many nodes** |
| `ReadWriteOncePod` | RWOP | Mounted read-write by **one pod** (k8s 1.22+) |

> **Banking context**: For a stateful trading engine that needs exclusive write access, RWO is correct. For a shared config/reference-data volume read by many replicas, ROX fits. RWX requires network filesystems like NFS or CephFS — block storage (EBS, GCE PD) only supports RWO.

#### `storageClassName` — The Matching Key

This is how PVC finds the right PV (or triggers dynamic provisioning):

```yaml
# StorageClass — defined once by infra team
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
reclaimPolicy: Retain   # or Delete

---
# PVC — developer requests storage
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: trade-data-pvc
spec:
  storageClassName: fast-ssd   # must match
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
```

With dynamic provisioning, the StorageClass's provisioner **automatically creates the PV** when PVC is submitted — no manual PV creation needed. This is the modern default.

#### Reclaim Policies

- **Retain** — PV persists after PVC deletion, data safe, must be manually reclaimed (right choice for financial data)
- **Delete** — PV and underlying storage deleted automatically (CI/CD scratch space)
- **Recycle** — deprecated, don't use

---

### Volume Types — Ephemeral vs Persistent

```
Pod Lifecycle Scope                        External Scope
──────────────────────────────────────    ──────────────────────
emptyDir        hostPath                  PVC → PV → Real Storage
configMap       secret                    
     │               │
     └── die with ───┘
         pod restart*
         (*emptyDir yes, hostPath no)
```

#### `emptyDir`

Created fresh when pod starts, **deleted when pod is removed**. Shared between containers in the same pod.

```yaml
volumes:
  - name: cache
    emptyDir:
      medium: Memory   # RAM-backed tmpfs — useful for fast scratch space
      sizeLimit: 512Mi
```

Use cases: inter-container scratch space, ML inference temp files, aggregation buffers. Think of it as `/tmp` for the pod.

#### `hostPath`

Mounts a path from the **node's filesystem** into the pod. Survives pod restarts (data stays on node), but **breaks pod portability** — if pod reschedules to a different node, different data.

```yaml
volumes:
  - name: node-logs
    hostPath:
      path: /var/log/app
      type: DirectoryOrCreate
```

Mostly used for system-level DaemonSets (log collectors, node monitoring agents). **Avoid in application pods** — it's a security and portability risk.

#### `configMap` and `secret` as Volumes

Instead of env vars, you mount them as files — cleaner for complex configs, supports live updates (with some caveats).

```yaml
volumes:
  - name: app-config
    configMap:
      name: trading-engine-config
      items:
        - key: application.yaml
          path: application.yaml   # mounted as a file

  - name: db-creds
    secret:
      secretName: db-secret
      defaultMode: 0400   # read-only for owner — important for secrets
```

Mounted at a path like `/etc/config/application.yaml`. Changes to ConfigMap propagate to the volume (with ~1min kubelet sync delay), unlike env vars which require pod restart.

---

### Why This Abstraction Matters — The Pros

**1. Separation of Concerns (the main win)**

Developers write PVCs with logical requirements (`I need 50Gi, ReadWriteOnce`). Infra teams manage PVs and StorageClasses. Neither needs to know the other's details. In a bank with strict infra governance, this maps perfectly to team boundaries.

**2. Portability**

Your deployment YAML doesn't reference AWS EBS ARNs or GCE disk names. You reference a `storageClassName`. Move from AWS to GCP → change the StorageClass, not every application manifest.

**3. Lifecycle Independence**

PVs outlive pods. Your trade records in a PV survive pod crashes, rollouts, and rescheduling. The `Retain` reclaim policy gives you data durability guarantees your compliance team will appreciate.

**4. Policy Enforcement at the Platform Level**

Cluster admins can define StorageClasses with encryption, specific IOPS tiers, backup policies baked in. Developers just pick a class name like `encrypted-retain` — they get compliant storage without knowing the details.

**5. Dynamic Provisioning = No Manual Toil**

In a modern setup, a developer creates a PVC and storage is automatically provisioned within seconds. No ticket to the storage team, no manual EBS volume creation. Critical for CI/CD pipelines and RAG systems that need ephemeral vector stores.

---

### Quick Mental Model for Your Context

Think of it like this: **PVC is like a bond futures contract** — you're specifying what you need (size, access mode, class) and the exchange (Kubernetes) matches you with actual supply (PV). The underlying physical delivery (EBS, NFS) is abstracted away. StorageClass is the contract specification standard.