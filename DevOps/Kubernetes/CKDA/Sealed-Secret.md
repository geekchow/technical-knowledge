## Bitnami Sealed Secrets — Deep Dive

### Core Concept

The fundamental problem: you can't store raw K8s Secrets in Git (base64 is not encryption). Sealed Secrets solves this with **asymmetric encryption** — encrypt with a public key, only the in-cluster controller can decrypt with the private key.

```
Developer                Git Repo              Kubernetes Cluster
    │                        │                        │
    │──kubeseal encrypt──▶   │──kubectl apply──▶      │
    │  (public key)          │  SealedSecret          │──controller decrypts──▶ Secret
    │                        │  (safe to commit)      │  (private key, in-cluster only)
```

---

### Component Breakdown

**1. Controller (server-side)**
- Runs as a `Deployment` in `kube-system` (or dedicated namespace)
- Holds the **master key pair** (RSA-4096 by default) in a K8s Secret
- Watches for `SealedSecret` CRD resources → decrypts → creates/updates the corresponding `Secret`
- Auto-rotates key pair every **30 days** by default (old keys retained for decryption)

**2. `kubeseal` CLI (client-side)**
- Fetches the controller's public certificate
- Encrypts your Secret → outputs a `SealedSecret` YAML
- Safe to run in CI pipelines, dev machines

**3. `SealedSecret` CRD**
- The encrypted artifact you commit to Git
- Per-namespace + per-name binding (by default) — prevents replay attacks

---

### Encryption Scopes (Critical Detail)

| Scope | Binding | Use Case |
|---|---|---|
| `strict` (default) | namespace + secret name | most secure, GitOps standard |
| `namespace-wide` | namespace only | secret can be renamed |
| `cluster-wide` | none | cross-namespace sharing, less safe |

```bash
kubeseal --scope cluster-wide ...
```

---

### Step-by-Step Workflow

#### Install controller
```bash
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm install sealed-secrets sealed-secrets/sealed-secrets \
  --namespace kube-system \
  --set fullnameOverride=sealed-secrets-controller
```

#### Fetch public cert (do once, commit to repo)
```bash
kubeseal --fetch-cert \
  --controller-name=sealed-secrets-controller \
  --controller-namespace=kube-system \
  > pub-cert.pem
```

> Committing `pub-cert.pem` to Git allows **offline encryption** in CI without cluster access.

#### Create a plain Secret (never commit this)
```bash
kubectl create secret generic db-secret \
  --namespace=prod \
  --from-literal=password=SuperSecret123 \
  --dry-run=client -o yaml > db-secret.yaml
```

#### Seal it
```bash
kubeseal \
  --cert pub-cert.pem \
  --format yaml \
  < db-secret.yaml \
  > db-sealed-secret.yaml   # ✅ commit this to Git
```

#### Resulting `SealedSecret` YAML
```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: db-secret
  namespace: prod
spec:
  encryptedData:
    password: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEq...  # RSA+AES encrypted
  template:
    metadata:
      name: db-secret
      namespace: prod
    type: Opaque
```

#### Apply to cluster (via GitOps / ArgoCD / Flux)
```bash
kubectl apply -f db-sealed-secret.yaml
# controller auto-creates the real Secret
kubectl get secret db-secret -n prod  # exists now
```

---

### GitOps Pipeline Integration

```
Developer PR
    │
    ▼
Git Repo (SealedSecret YAMLs committed)
    │
    ▼
ArgoCD / Flux detects drift
    │
    ▼
kubectl apply SealedSecret to cluster
    │
    ▼
sealed-secrets-controller decrypts
    │
    ▼
Native K8s Secret created in namespace
    │
    ▼
Pod consumes via env / volumeMount (as normal)
```

With **ArgoCD**, `SealedSecret` is treated like any other manifest — no special plugin needed. ArgoCD health checks even understand `SealedSecret` status.

---

### Key Rotation — Important for Banking

The controller rotates keys every 30 days but **keeps old keys** so previously sealed secrets still decrypt. However, old `SealedSecrets` are NOT automatically re-encrypted.

```bash
# Force re-seal all secrets after key rotation (recommended practice)
kubeseal --re-encrypt < old-sealed.yaml > new-sealed.yaml
```

**Recommended rotation policy for regulated environments:**
- Rotate master key on schedule (default 30d is fine, or align with your key management policy)
- After rotation, re-seal all secrets and commit updated YAMLs to Git
- Treat old `pub-cert.pem` files as expired — update CI/CD pipeline cert reference

---

### Backup the Master Key — Critical

If you lose the controller's master key (e.g., cluster disaster), **all SealedSecrets become unrecoverable**.

```bash
# Backup (store in vault, NOT in Git)
kubectl get secret -n kube-system \
  -l sealedsecrets.bitnami.com/sealed-secrets-key \
  -o yaml > master-key-backup.yaml

# Restore to new cluster
kubectl apply -f master-key-backup.yaml
kubectl rollout restart deployment sealed-secrets-controller -n kube-system
```

---

### Comparison with Alternatives

| Tool | Approach | Cluster Dependency | Complexity |
|---|---|---|---|
| **Sealed Secrets** | Asymmetric encrypt, CRD | Controller required | Low |
| **Vault + ESO** | External secret store, sync | Vault + ESO operator | High, but enterprise-grade |
| **SOPS + age/KMS** | File-level encryption, no CRD | None (just key access) | Medium |
| **AWS Secrets Manager + ESO** | Cloud-native store | ESO operator | Medium |

**For banking context:** Sealed Secrets is great for smaller teams / single cluster. For multi-cluster, multi-region, PCI-scoped workloads, pairing **ESO + HashiCorp Vault Enterprise** (with HSM backing) gives you audit trails, dynamic secrets, and fine-grained lease management that regulators prefer.