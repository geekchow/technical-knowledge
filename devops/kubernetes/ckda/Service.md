# Kubernetes Service Types

Let me break this down with ASCII diagrams since visuals really help here.

---

## The 4 Service Types

```
┌─────────────────────────────────────────────────────────────────────┐
│                        K8s Service Types                            │
│                                                                     │
│  ClusterIP ──► NodePort ──► LoadBalancer ──► ExternalName          │
│  (internal)    (node-level)  (cloud LB)       (DNS alias)          │
│                                                                     │
│  Complexity & Exposure:  LOW ──────────────────────────► HIGH      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. ClusterIP (Default)

```
                    ┌─────────────────────────────┐
                    │       K8s Cluster           │
                    │                             │
  External ✗        │  [Service: ClusterIP]       │
  No access         │   10.96.0.1:8080            │
                    │        │                    │
                    │   ┌────┴────┐               │
                    │   ▼        ▼                │
                    │ [Pod A]  [Pod B]  [Pod C]   │
                    │                             │
                    │  Other pods CAN reach it    │
                    └─────────────────────────────┘
```

**Why it exists:** pods are ephemeral with dynamic IPs. ClusterIP gives a **stable virtual IP** + DNS name (`my-svc.namespace.svc.cluster.local`) backed by kube-proxy iptables/ipvs rules.

**Suitable for:** internal microservice-to-microservice calls, DB connections, internal APIs — anything that should **never** be exposed outside the cluster. In banking context: your transaction-service calling account-service internally.

---

## 2. NodePort

```
  External Client
        │
        │  curl nodeIP:30080
        ▼
┌───────────────────────────────────────────┐
│  K8s Cluster                              │
│                                           │
│  Node1 :30080 ──┐                        │
│  Node2 :30080 ──┤──► [ClusterIP:8080]    │
│  Node3 :30080 ──┘         │              │
│                       ┌───┴───┐          │
│                      [Pod A] [Pod B]     │
└───────────────────────────────────────────┘

Port range: 30000-32767
```

**Why it exists:** bridges external traffic into the cluster without needing a cloud LB. NodePort **wraps** ClusterIP (a ClusterIP is automatically created).

**Suitable for:** dev/test environments, on-prem bare metal where you manage your own external LB (like HAProxy in front), or quick demos. **Not ideal for production** — exposes every node, awkward port numbers, no health check of nodes.

---

## 3. LoadBalancer

```
  External Client
        │
        ▼
  ┌───────────┐
  │ Cloud LB  │  (AWS ALB/NLB, GCP LB, Azure LB)
  │ 1.2.3.4:80│
  └─────┬─────┘
        │
┌───────▼───────────────────────────────────┐
│  K8s Cluster                              │
│                                           │
│  [NodePort :3xxxx]                        │
│        │                                  │
│  [ClusterIP]                              │
│        │                                  │
│   ┌────┴────┐                             │
│  [Pod A]  [Pod B]                         │
└───────────────────────────────────────────┘

LoadBalancer WRAPS NodePort WRAPS ClusterIP
```

**Why it exists:** automates external LB provisioning via cloud provider's CCM (Cloud Controller Manager). One service = one external IP.

**Suitable for:** production workloads on cloud (EKS/GKE/AKS). In banking: exposing your public API gateway, payment endpoint. **Downside:** each service gets its own LB = expensive. That's why **Ingress** was introduced (one LB, many routes) — though Ingress is not a Service type itself.

---

## 4. ExternalName

```
┌─────────────────────────────────────────┐
│  K8s Cluster                            │
│                                         │
│  [Pod] ──► [Service: ExternalName]      │
│              "oracle-db"                │
│                  │  DNS CNAME           │
│                  ▼                      │
│        oracle.internal.bank.com         │
└─────────────────────────────────────────┘
        │
        ▼  (outside cluster)
   Oracle DB / Legacy System
```

**Why it exists:** lets pods use a stable in-cluster DNS name to reach **external** resources, decoupling code from the actual external endpoint. No proxying, just DNS-level CNAME.

**Suitable for:** legacy system integration (very relevant in banking!), external databases, migration phases where you gradually move services into the cluster. Your pods just call `oracle-db:1521` — you swap the ExternalName target without touching app config.

---

## Complete Comparison Table

| Feature | ClusterIP | NodePort | LoadBalancer | ExternalName |
|---|---|---|---|---|
| External Access | ✗ | ✓ (NodeIP:Port) | ✓ (dedicated IP) | DNS only |
| Use Case | Internal comms | Dev/on-prem | Production cloud | External DNS alias |
| Includes | — | ClusterIP | NodePort+ClusterIP | — |
| Load Balancing | kube-proxy | kube-proxy | Cloud LB + kube-proxy | None (CNAME) |
| Cost | Free | Free | $$$ (per LB) | Free |
| Banking Use | Service mesh internal calls | UAT env | Public APIs | Legacy Oracle/MQ |

---

## Why These 4 Exist — The Design Philosophy

```
Problem: Pods are cattle, not pets.
         IPs change. Scaling changes pod count.
         
Solution: Service = stable abstraction over dynamic pods

Then:    How far does that abstraction reach?
         
         ┌──────────┐  internal only    → ClusterIP
         │ Cluster  │  
         │ boundary │  open a node port → NodePort
         └──────────┘  
                        delegate to cloud → LoadBalancer
                        
                        reverse direction (reach out) → ExternalName
```

The progression is essentially answering: **"who needs to talk to whom, and from where?"**

---

**Practical tip for your banking context:** In production you'd typically use ClusterIP for all internal services + a single **Ingress controller** (like nginx or AWS ALB Ingress) backed by one LoadBalancer service, rather than one LB per service. ExternalName is your friend for bridging into legacy SWIFT/MQ/Core Banking systems during modernization phases.


>references: https://www.youtube.com/watch?v=T4Z7visMM4E