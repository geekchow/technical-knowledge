## How NodePort Really Works Under the Hood

### Why Every Node Opens the Same Port

When you create a NodePort Service, the K8s control plane picks a port (e.g., `32000`) and **kube-proxy** on **every node** programs that port to be open — even nodes that have zero Pods for that Service.

The reason is simple: **the client doesn't know which node has your Pod**. If you only opened the port on nodes running the Pod, clients would need to discover that dynamically. Instead, NodePort says "hit any node, any IP, same port — we'll figure out routing internally."

```
Client: I want to reach payment-service
Client: I only know node IPs: 10.0.1.1, 10.0.2.1, 10.0.3.1
Client: I'll just pick one... 10.0.1.1:32000

→ Doesn't matter if payment Pod is there or not. It will work.
```

---

### The Real Hero: kube-proxy + iptables

`kube-proxy` runs as a **DaemonSet** (one pod per node). Its job is to watch the API server for Service/Endpoint changes and translate them into **iptables rules** (or IPVS rules) on each node.

```
┌─────────────────────────────────────────────────────┐
│                   Every Node                        │
│                                                     │
│  kube-proxy (DaemonSet Pod)                         │
│       │                                             │
│       │  watches API Server                         │
│       │  Service created / Pod scaled               │
│       │                                             │
│       ▼                                             │
│  iptables rules (in kernel netfilter)               │
│       │                                             │
│       ▼                                             │
│  DNAT: 0.0.0.0:32000 → PodIP:8080                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

iptables operates at the **kernel level** — no userspace proxy involved in the data path. It's pure kernel packet manipulation via **DNAT (Destination NAT)**.

---

### Step-by-Step Packet Journey

Let's say payment-service has 2 Pods:
- Pod A: `10.0.1.15:8080` (on Node 1)
- Pod B: `10.0.2.33:8080` (on Node 2)

And client hits **Node 3** (which has NO payment Pod) at `10.0.3.1:32000`:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Step 1: Packet arrives at Node 3                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  src: client_ip:xxxxx                                        │   │
│  │  dst: 10.0.3.1:32000    ← NodePort                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                 │                                                    │
│                 ▼                                                    │
│  Step 2: iptables PREROUTING chain intercepts                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  KUBE-NODEPORTS chain:                                       │   │
│  │  -A KUBE-NODEPORTS -p tcp --dport 32000                     │   │
│  │     -j KUBE-SVC-PAYMENT                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                 │                                                    │
│                 ▼                                                    │
│  Step 3: Load balance across endpoints (random/probability)         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  KUBE-SVC-PAYMENT chain:                                     │   │
│  │  -A KUBE-SVC-PAYMENT -m statistic --mode random             │   │
│  │     --probability 0.5  -j KUBE-SEP-POD-A                    │   │
│  │  -A KUBE-SVC-PAYMENT               -j KUBE-SEP-POD-B        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                 │                                                    │
│                 ▼                                                    │
│  Step 4: DNAT to actual Pod IP                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  KUBE-SEP-POD-A:                                             │   │
│  │  -A KUBE-SEP-POD-A -p tcp -j DNAT                          │   │
│  │     --to-destination 10.0.1.15:8080                         │   │
│  │                                                              │   │
│  │  Packet now:                                                 │   │
│  │  src: client_ip:xxxxx                                        │   │
│  │  dst: 10.0.1.15:8080   ← Pod A on Node 1                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                 │                                                    │
│                 ▼                                                    │
│  Step 5: Packet routed across nodes via CNI overlay network         │
│  Node 3 → Node 1 (Pod A)                                           │
│                                                                     │
│  Step 6: Response comes back, kernel does reverse SNAT              │
│  Pod A → Node 3 → Client (src rewritten back to node IP)           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### The Actual iptables Rules (Simplified)

You can see this live on any node with `iptables-save | grep KUBE`:

```bash
# Entry point: catch NodePort traffic
-A KUBE-NODEPORTS -p tcp -m tcp --dport 32000 -j KUBE-SVC-XYZ123

# Load balance: 50/50 between 2 pods
-A KUBE-SVC-XYZ123 -m statistic --mode random --probability 0.50000 \
   -j KUBE-SEP-PODA
-A KUBE-SVC-XYZ123 \
   -j KUBE-SEP-PODB

# DNAT to Pod A
-A KUBE-SEP-PODA -p tcp -j DNAT --to-destination 10.0.1.15:8080

# DNAT to Pod B  
-A KUBE-SEP-PODB -p tcp -j DNAT --to-destination 10.0.2.33:8080
```

For N pods, iptables uses cascading probability math to achieve equal distribution: `1/N`, `1/(N-1)`, `1/(N-2)`... so each Pod ends up with equal probability.

---

### The externalTrafficPolicy Nuance — Important for Banking

By default (`externalTrafficPolicy: Cluster`), there's a **hidden extra hop**:

```
Client → Node 3 (no Pod) → DNAT → Node 1 (Pod A)
                                 ↑
                         cross-node hop + SNAT
                         (real client IP is LOST)
```

With `externalTrafficPolicy: Local`:

```
Client → Node 3 (no Pod) → DROP (or 500)
Client → Node 1 (has Pod) → Pod A directly
                             (real client IP preserved)
```

| | Cluster (default) | Local |
|---|---|---|
| Cross-node hop | Yes | No |
| Client IP preserved | ✗ (SNAT'd) | ✓ |
| Risk | None | Uneven load if Pods not spread evenly |
| Use case | General | When you need real client IP (audit logs!) |

In banking, **audit logging with real client IPs** often matters — this setting is relevant.

---

### kube-proxy Modes Comparison

kube-proxy itself has evolved — it supports three modes:

```
iptables (default)
  └── Programs netfilter rules, random LB via probability chains
  └── O(n) rule lookup — degrades with thousands of services

IPVS (recommended at scale)
  └── Uses kernel IPVS (hash table), O(1) lookup
  └── Supports richer LB algorithms: round-robin, least-conn, etc.
  └── Enable: kube-proxy --proxy-mode=ipvs

eBPF (Cilium CNI replaces kube-proxy entirely)
  └── Most modern, no iptables at all
  └── Kernel-level programmable dataplane
  └── Best performance + observability
```

For EKS at scale, many teams switch to **IPVS mode** or adopt **Cilium** to avoid iptables rule explosion when you have hundreds of Services.

---

### Mental Model Summary

```
NodePort = "any node is a valid entry point"
kube-proxy = "kernel-level traffic redirector on every node"
iptables/IPVS = "the actual mechanism doing DNAT in the kernel"
Service Endpoints = "the live list of Pod IPs kube-proxy syncs from API server"

Flow: Packet → iptables PREROUTING → DNAT to PodIP → CNI routes to correct node → Pod
```

The elegance is that **none of this is in userspace** — once kube-proxy programs the rules, it's completely out of the data path. Pure kernel networking.