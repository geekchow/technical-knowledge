# Pod and Config

## Kubernetes Pod — Summary

A **Pod** is the smallest deployable unit in Kubernetes, wrapping one or more containers that share:
- the same network namespace (localhost communication)
- the same storage volumes
- the same lifecycle

In practice, most Pods run a single container; multi-container Pods use sidecar patterns (log shippers, proxies, init containers, etc.).

---

## Consuming ConfigMap & Secret

Both resources follow the same injection patterns. The key difference: Secret values are base64-encoded and treated with slightly stricter RBAC in well-governed clusters.

### 1. Environment Variables — single key

```yaml
env:
  - name: DB_NAME
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: database_name

  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: app-secret
        key: password
```

### 2. Environment Variables — entire resource (`envFrom`)

```yaml
envFrom:
  - configMapRef:
      name: app-config       # all keys become env vars
  - secretRef:
      name: app-secret
```

All keys in the ConfigMap/Secret are injected as `KEY=value`. Key naming must be valid env var names.

> ⚠️ Env vars are **static at Pod start** — updating the ConfigMap/Secret does NOT hot-reload them. Pod restart required.

---

### 3. Volume Mount — file-based

ConfigMap/Secret keys are projected as files inside the container filesystem. This is the preferred approach for config files, TLS certs, keystores, etc.

```yaml
volumes:
  - name: config-vol
    configMap:
      name: app-config
      items:                        # optional: select specific keys
        - key: application.yaml
          path: application.yaml

  - name: tls-vol
    secret:
      secretName: tls-secret
      defaultMode: 0400             # file permissions

containers:
  - name: app
    volumeMounts:
      - name: config-vol
        mountPath: /etc/config
      - name: tls-vol
        mountPath: /etc/tls
        readOnly: true
```

Resulting files:
```
/etc/config/application.yaml
/etc/tls/tls.crt
/etc/tls/tls.key
```

> ✅ Volume mounts **do support hot-reload** — kubelet syncs changes (with a short propagation delay, ~1 min by default). Your app still needs to watch/reload the file itself (e.g., Spring Cloud's `@RefreshScope`, or a file watcher).

---

### 4. Projected Volume — combine multiple sources

```yaml
volumes:
  - name: combined
    projected:
      sources:
        - configMap:
            name: app-config
        - secret:
            name: app-secret
        - serviceAccountToken:
            path: token
            expirationSeconds: 3600
```

Useful for consolidating certs + config + SA token into a single mount path.

---

## Quick Comparison Table

| Aspect | `env` / `envFrom` | Volume Mount |
|---|---|---|
| Use case | simple KV pairs | files, certs, large configs |
| Hot reload | ❌ needs pod restart | ✅ kubelet syncs |
| Visibility | `printenv` leaks all | scoped to mountPath |
| Binary data | ❌ | ✅ |
| Secret best practice | avoid for sensitive creds | prefer (restrict file perms) |

---

## Banking / Security Notes

In a regulated banking environment you'd typically layer on:
- **External Secrets Operator** (ESO) or **Vault Agent Injector** — sync secrets from HashiCorp Vault / AWS Secrets Manager into K8s Secrets, avoiding storing plaintext secrets in etcd
- **etcd encryption at rest** — mandatory for any PCI/SOX workload
- **RBAC** — restrict `get`/`list` on Secret objects tightly; use separate namespaces per environment
- **Sealed Secrets** (Bitnami) — encrypt secrets before committing to Git for GitOps pipelines