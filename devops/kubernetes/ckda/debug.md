# Kubernetes Debugging Best Practices

## Pod & Container Logs

```bash
# Follow logs with timestamps
kubectl logs -f pod-name --timestamps=true

# Previous crashed container (crucial for crashloopbackoff)
kubectl logs pod-name --previous

# Multi-container pod
kubectl logs pod-name -c container-name

# Label selector — aggregate logs across replicas
kubectl logs -l app=my-service --all-containers=true --max-log-requests=10

# Tail recent lines
kubectl logs pod-name --tail=100
```

## Ephemeral Debug Containers (Modern Approach)

```bash
# Inject a debug sidecar into a running pod (k8s 1.23+)
kubectl debug -it pod-name --image=nicolaka/netshoot --target=app-container

# Clone a crashing pod with debug shell (overrides entrypoint)
kubectl debug -it pod-name --image=busybox --copy-to=debug-pod --share-processes

# Node-level debugging
kubectl debug node/node-name -it --image=nicolaka/netshoot
```

`nicolaka/netshoot` is far more useful than busybox — it includes `curl`, `dig`, `tcpdump`, `netstat`, `ss`, `nmap`, etc.

## Network Connectivity Testing

```bash
# Your example — better with netshoot
kubectl run tmp --restart=Never -i --rm --image=nicolaka/netshoot -- \
  curl -v http://svc-name.namespace.svc.cluster.local:4444

# DNS resolution check
kubectl run tmp --restart=Never -i --rm --image=nicolaka/netshoot -- \
  dig svc-name.namespace.svc.cluster.local

# Test from within same namespace context
kubectl run tmp -n target-namespace --restart=Never -i --rm \
  --image=nicolaka/netshoot -- curl svc:4444

# Check if issue is DNS vs connectivity
kubectl run tmp --restart=Never -i --rm --image=nicolaka/netshoot -- \
  nslookup kubernetes.default
```

Key insight: always test from **same namespace** as the caller, since short-name `svc` only resolves within the same namespace.

## Events — the Most Underused Tool

```bash
# Sort by time (default output is unordered)
kubectl get events --sort-by='.lastTimestamp'

# Watch live
kubectl get events -w

# Filter by specific object
kubectl get events --field-selector involvedObject.name=pod-name

# Filter warnings only
kubectl get events --field-selector type=Warning

# Cross-namespace
kubectl get events -A --sort-by='.lastTimestamp' | tail -30
```

## Describe — Reading it Effectively

```bash
kubectl describe pod pod-name
```

Focus on these sections in order:

| Section | What to look for |
|---|---|
| **Events** | Bottom of output, most actionable |
| **Conditions** | `Ready`, `PodScheduled`, `ContainersReady` |
| **State / Last State** | Exit codes, OOMKilled, restart count |
| **Resource Limits** | OOM or CPU throttling clues |
| **Volumes / Mounts** | Mount failures, secret/configmap missing |

Common exit codes: `137` = OOMKilled, `1` = app error, `126/127` = command not found, `143` = SIGTERM.

## Resource & Status Inspection

```bash
# Wide output shows node placement and IP
kubectl get pods -o wide

# Raw YAML diff from what you applied
kubectl get pod pod-name -o yaml | diff - your-manifest.yaml

# JSONPath for scripting
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\n"}{end}'

# All resources in namespace
kubectl get all -n namespace

# Check resource quota/limits
kubectl describe resourcequota -n namespace
kubectl describe limitrange -n namespace
```

## Advanced: exec + live inspection

```bash
# Shell into running container
kubectl exec -it pod-name -- /bin/sh

# Check env vars (misconfigured secrets/configmaps show up here)
kubectl exec pod-name -- env | sort

# File system inspection
kubectl exec pod-name -- ls -la /app/config

# Port-forward to test service locally
kubectl port-forward svc/my-service 8080:4444
# then curl localhost:8080 from your machine
```

## Systematic Debugging Flow

```
Pod not starting?
  → kubectl get events (scheduling/image issues)
  → kubectl describe pod (conditions + events)
  → kubectl logs --previous (crash reason)

Service not reachable?
  → kubectl get endpoints svc-name  ← often the smoking gun
  → kubectl describe svc svc-name (selector match?)
  → ephemeral pod curl test from same namespace

Intermittent issues?
  → kubectl top pods (resource pressure)
  → kubectl get events -w (live)
  → check HPA: kubectl describe hpa
```

```bash
# endpoints check — if this is empty, selector doesn't match pod labels
kubectl get endpoints service-name -n namespace
```

This is probably the single most useful command for "service not working" issues — an empty endpoints list immediately tells you it's a label selector mismatch rather than a network problem.