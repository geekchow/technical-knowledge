# CKAD Exam Sample — Helm Topic

---

## Question 1 — Install & Override Values (Weight: 4%)

**Context:** You are working in namespace `staging`.

A Helm chart named `webapp` is available in a repo already added as `myrepo`. Install a release named `frontend` using chart `myrepo/webapp` with the following requirements:

- Set `replicaCount` to `3`
- Set `image.tag` to `v2.1.0`
- Set `service.type` to `ClusterIP`
- The release must be installed into namespace `staging`

**Do not use a values file.**

<details>
<summary>Answer</summary>

```bash
helm install frontend myrepo/webapp \
  --namespace staging \
  --set replicaCount=3 \
  --set image.tag=v2.1.0 \
  --set service.type=ClusterIP
```
</details>

---

## Question 2 — Upgrade & Rollback (Weight: 5%)

**Context:** A release named `payments` is already running in namespace `production`.

1. Upgrade the release to chart version `3.2.1`, overriding `resources.requests.memory` to `256Mi`
2. After the upgrade, verify the revision number
3. Roll back to the **previous** revision

<details>
<summary>Answer</summary>

```bash
# Step 1: Upgrade
helm upgrade payments myrepo/payments \
  --namespace production \
  --version 3.2.1 \
  --set resources.requests.memory=256Mi

# Step 2: Check revision
helm history payments -n production

# Step 3: Rollback
helm rollback payments 0 -n production
# "0" rolls back to the previous revision
# Or explicitly: helm rollback payments 1 -n production
```
</details>

---

## Question 3 — Inspect & Debug (Weight: 3%)

**Context:** A release named `auth-service` in namespace `dev` is failing. 

1. Render the chart templates locally **without installing** and save the output to `/tmp/auth-manifest.yaml`
2. Check what user-supplied values are currently applied to the live release

<details>
<summary>Answer</summary>

```bash
# Render templates dry-run
helm template auth-service myrepo/auth-service \
  --namespace dev > /tmp/auth-manifest.yaml

# Check live user values (--all to include computed values)
helm get values auth-service -n dev
```
</details>

---

## Question 4 — Repo Management & Search (Weight: 3%)

**Tasks:**

1. Add a Helm repo named `bitnami` with URL `https://charts.bitnami.com/bitnami`
2. Update all repos
3. Find all charts in `bitnami` that match the keyword `redis` and identify the latest chart version

<details>
<summary>Answer</summary>

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm search repo bitnami/redis --versions | head -5
```
</details>

---

## Question 5 — Uninstall & Retain History (Weight: 2%)

A release `legacy-app` in namespace `qa` must be removed, but you need to **preserve its history** for audit purposes.

<details>
<summary>Answer</summary>

```bash
helm uninstall legacy-app -n qa --keep-history

# Verify history is retained
helm history legacy-app -n qa
```
</details>

---

## Key Helm Commands Cheat Sheet for CKAD

| Task | Command |
|---|---|
| Install | `helm install <release> <chart>` |
| Upgrade | `helm upgrade <release> <chart>` |
| Rollback | `helm rollback <release> <revision>` |
| Dry-run render | `helm template` or `helm install --dry-run` |
| Live values | `helm get values <release>` |
| Release status | `helm status <release>` |
| History | `helm history <release>` |
| Uninstall | `helm uninstall <release>` |

---

**Tips for the real exam:**
- Always specify `--namespace` / `-n`; don't assume the default namespace
- `helm template` vs `--dry-run`: template works offline, `--dry-run` hits the API server for validation
- Rollback revision `0` always means "one step back" — useful shorthand under time pressure
