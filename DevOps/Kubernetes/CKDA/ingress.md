# Ingress

## Kubernetes Ingress

### The Problem It Solves

In Kubernetes, your apps run in Pods, exposed via **Services**. But Services have a fundamental limitation when it comes to external HTTP traffic:

- `ClusterIP` — only reachable inside the cluster
- `NodePort` — exposes a raw port (e.g., `30080`) on every node, ugly and hard to manage
- `LoadBalancer` — works, but provisions a **separate cloud load balancer per Service**, which gets expensive fast (imagine 20 microservices = 20 LBs, 20 public IPs)

None of these give you **L7 (HTTP/HTTPS) routing** — things like path-based routing, host-based routing, TLS termination, or rewriting headers.

**Ingress solves exactly this**: one entry point, intelligent routing to many backend services.

---

### What Ingress Actually Is

Ingress is a Kubernetes **API object** (a routing rule declaration) + an **Ingress Controller** (the actual runtime that enforces those rules, e.g., nginx, Traefik, AWS ALB Ingress Controller).

```
Internet
    │
    ▼
[ Ingress Controller ]  ← one LoadBalancer/IP for everything
    │
    ├── /api/*         → Service: api-service:8080
    ├── /admin/*       → Service: admin-service:3000
    └── app.bank.com   → Service: frontend-service:80
```

A typical Ingress manifest:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: banking-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  tls:
    - hosts: ["app.bank.com"]
      secretName: tls-cert-secret
  rules:
    - host: app.bank.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 8080
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80
```

---

### Relationship Between Ingress and Service

They operate at **different layers** and complement each other:

| Layer | Component | Responsibility |
|---|---|---|
| L7 (HTTP) | **Ingress** | Host/path routing, TLS termination, redirects |
| L4 (TCP) | **Service** | Load balance traffic across healthy Pods |
| L3 | **Pod** | Actually runs your app |

**Ingress does NOT replace Services** — it routes to Services, which then forward to Pods. The chain is always:

```
Ingress Controller → Service (ClusterIP) → Pod
```

A Service is still required as the backend target. Ingress just decides *which* Service gets the traffic based on HTTP-level rules.

---

### Key Capabilities Ingress Unlocks

- **TLS termination** — handle HTTPS at the edge, services talk plain HTTP internally
- **Virtual hosting** — route `api.bank.com` and `admin.bank.com` from the same IP
- **Path-based routing** — `/payments/*` → payments-service, `/accounts/*` → accounts-service
- **Rate limiting, auth, WAF** — via controller annotations (critical for banking scenarios)
- **Cost efficiency** — one cloud LB instead of N

---

### Banking Context Note

In your domain, Ingress controllers are often paired with **OAuth2 proxy sidecars** or **JWT validation plugins** (e.g., nginx `auth_request`), so authentication happens at the ingress layer before traffic ever reaches your microservices — a clean separation of concerns that aligns well with zero-trust architecture patterns.


## Ingress with AWS Load Balancer Controller

### What is AWS Load Balancer Controller?

It's an **Ingress Controller** implementation maintained by AWS that maps Kubernetes Ingress resources to **AWS Application Load Balancers (ALB)**. Instead of nginx running inside your cluster, AWS provisions and manages a real ALB in your VPC.

---

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          AWS Cloud                              │
│                                                                 │
│   Client                                                        │
│     │                                                           │
│     ▼                                                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               AWS ALB (auto-provisioned)                 │   │
│  │                                                          │   │
│  │  Listener :443 (HTTPS)                                   │   │
│  │   ├── Rule: host=api.bank.com  path=/payments/*          │   │
│  │   │         → Target Group A                             │   │
│  │   ├── Rule: host=api.bank.com  path=/accounts/*          │   │
│  │   │         → Target Group B                             │   │
│  │   └── Rule: default                                      │   │
│  │             → Target Group C                             │   │
│  └──────────────┬──────────────┬───────────────────────────┘   │
│                 │              │                                 │
│  ┌──────────────▼──────────────▼──────────────────────────┐    │
│  │                  EKS Cluster (VPC)                      │    │
│  │                                                         │    │
│  │  ┌─────────────────────────────────────────────────┐   │    │
│  │  │         aws-load-balancer-controller             │   │    │
│  │  │         (watches Ingress objects via API server) │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  │                                                         │    │
│  │  Target Group A          Target Group B                 │    │
│  │  ┌────────────────┐      ┌────────────────┐            │    │
│  │  │ payment-svc    │      │ account-svc    │            │    │
│  │  │ (ClusterIP)    │      │ (ClusterIP)    │            │    │
│  │  └───────┬────────┘      └───────┬────────┘            │    │
│  │          │                       │                      │    │
│  │    ┌─────▼─────┐          ┌──────▼────┐                │    │
│  │    │  Pod      │          │  Pod      │                │    │
│  │    │  Pod      │          │  Pod      │                │    │
│  │    └───────────┘          └───────────┘                │    │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

### Two Target Type Modes — This is Critical

AWS LB Controller supports two `target-type` modes, and they behave very differently:

#### Mode 1: `instance` (default)
```
ALB → NodePort (Service) → kube-proxy → Pod
```
Traffic hits a NodePort on EC2 nodes, then kube-proxy routes to Pods. Standard but adds one hop.

#### Mode 2: `ip` (recommended for EKS)
```
ALB → Pod IP directly (bypasses Service/kube-proxy entirely)
```
ALB registers **Pod IPs** directly into Target Groups. This requires VPC CNI (which EKS uses by default). Fewer hops, lower latency, and you get **real client IPs** in your app.

```
┌─────────────────────────────────────────────┐
│  ip mode (recommended)                      │
│                                             │
│  ALB Target Group                           │
│    ├── 10.0.1.15:8080  (Pod A)             │
│    ├── 10.0.2.33:8080  (Pod B)             │
│    └── 10.0.3.07:8080  (Pod C)             │
│                                             │
│  No kube-proxy, no NodePort involved        │
└─────────────────────────────────────────────┘
```

---

### How the Controller Reconciliation Works

This is the core mechanism — understanding the **control loop**:

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   kubectl apply ingress.yaml                             │
│          │                                               │
│          ▼                                               │
│   K8s API Server stores Ingress object                   │
│          │                                               │
│          │  (watch event)                                │
│          ▼                                               │
│   aws-load-balancer-controller                           │
│   (running as Deployment in kube-system)                 │
│          │                                               │
│          │  calls AWS APIs                               │
│          ▼                                               │
│   ┌──────────────────────────────────────┐               │
│   │  1. Create/Update ALB                │               │
│   │  2. Create Listeners (80, 443)       │               │
│   │  3. Create Listener Rules            │               │
│   │     (from Ingress path/host rules)   │               │
│   │  4. Create Target Groups             │               │
│   │  5. Register Pod/Node IPs as targets │               │
│   └──────────────────────────────────────┘               │
│          │                                               │
│          ▼                                               │
│   Updates Ingress status with ALB DNS name               │
│   e.g. xxx.us-east-1.elb.amazonaws.com                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

When Pods scale up/down, the controller also **automatically updates Target Group registrations** — this is why `ip` mode is powerful.

---

### Real Manifest — Banking Microservices Example

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: banking-api-ingress
  namespace: banking
  annotations:
    # Tell K8s to use AWS LB Controller
    kubernetes.io/ingress.class: alb

    # Use ip mode - Pod IPs directly in Target Group
    alb.ingress.kubernetes.io/target-type: ip

    # Internet-facing or internal (use internal for banking!)
    alb.ingress.kubernetes.io/scheme: internal

    # TLS - ACM cert ARN
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:123:certificate/xxx

    # Force HTTPS redirect
    alb.ingress.kubernetes.io/ssl-redirect: "443"

    # WAF integration - attach AWS WAF WebACL
    alb.ingress.kubernetes.io/wafv2-acl-arn: arn:aws:wafv2:us-east-1:123:regional/webacl/xxx

    # Security Groups
    alb.ingress.kubernetes.io/security-groups: sg-xxxxxxxxx

    # Health check
    alb.ingress.kubernetes.io/healthcheck-path: /actuator/health
    alb.ingress.kubernetes.io/healthcheck-interval-seconds: "15"

    # Access logs to S3
    alb.ingress.kubernetes.io/load-balancer-attributes: >
      access_logs.s3.enabled=true,
      access_logs.s3.bucket=my-alb-logs,
      idle_timeout.timeout_seconds=60
spec:
  rules:
    - host: api-internal.bank.com
      http:
        paths:
          - path: /payments
            pathType: Prefix
            backend:
              service:
                name: payment-service
                port:
                  number: 8080
          - path: /accounts
            pathType: Prefix
            backend:
              service:
                name: account-service
                port:
                  number: 8080
          - path: /auth
            pathType: Prefix
            backend:
              service:
                name: auth-service
                port:
                  number: 8080
```

---

### IngressGroup — One ALB Shared Across Namespaces

A very useful feature for cost control. Multiple Ingress objects across namespaces share **one ALB**:

```yaml
# payments namespace
metadata:
  annotations:
    alb.ingress.kubernetes.io/group.name: banking-shared-alb
    alb.ingress.kubernetes.io/group.order: "10"

# accounts namespace  
metadata:
  annotations:
    alb.ingress.kubernetes.io/group.name: banking-shared-alb
    alb.ingress.kubernetes.io/group.order: "20"
```

```
banking-shared-alb (single ALB)
  ├── Rules from payments/ingress    (order 10)
  └── Rules from accounts/ingress   (order 20)
```

---

### Ingress vs Service — Clarified in AWS Context

| | Service (ClusterIP) | Service (LoadBalancer) | Ingress + ALB Controller |
|---|---|---|---|
| OSI Layer | L4 | L4 | L7 |
| AWS Resource | None | NLB (one per Service) | ALB (shared) |
| Host routing | ✗ | ✗ | ✓ |
| Path routing | ✗ | ✗ | ✓ |
| TLS termination | ✗ | ✗ | ✓ (ACM) |
| WAF integration | ✗ | ✗ | ✓ |
| Cost | Free | $$$ per service | $ shared |
| Best for | Internal comms | Non-HTTP / single service | HTTP APIs, multi-service |

The relationship stays the same: **Ingress routes to Services, Services route to Pods**. But in `ip` mode, the ALB bypasses the Service's load balancing and talks directly to Pod IPs — the Service still exists as a selector/discovery mechanism but isn't in the data path.

---

### IAM — Don't Forget This

The controller calls AWS APIs on your behalf, so it needs IRSA (IAM Roles for Service Accounts):

```
aws-load-balancer-controller Pod
    └── ServiceAccount
            └── IRSA annotation → IAM Role
                    └── Policy: elasticloadbalancing:*, ec2:Describe*, wafv2:*, acm:*, ...
```

This is the standard pattern for any AWS controller in EKS — important to lock down with least privilege in a banking environment.

**references**

- https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/how-it-works/#ingress-creation

- https://www.youtube.com/watch?v=5XpPiORNy1o

- ![architecture](./controller-design.png)