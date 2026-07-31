## ALB SSL policy conflict (AWS Load Balancer Controller)

### Symptom

You may see an error like this in the AWS Load Balancer Controller logs or in a failed model build:

```
Failed build model due to failed to merge listenPort config for port: 443: conflicting sslPolicy,
    <NAMESPACE>/<INGRESS_A>: ELBSecurityPolicy-TLS13-1-2-2021-06 |
    <NAMESPACE>/<INGRESS_B>: ELBSecurityPolicy-TLS13-1-2-Res-2021-06
```

This happens when two or more Ingress resources are being grouped onto the same ALB listener (typically port 443) but they specify different TLS/SSL policies. An ALB listener can have only one ssl-policy, so the controller refuses to merge the conflicting configuration.

### Why this occurs

Ingresses are grouped together by the controller when they share grouping annotations or an explicit load balancer name. Common grouping causes:

- They share `alb.ingress.kubernetes.io/group.name`.
- They share `alb.ingress.kubernetes.io/load-balancer-name` (forces the same ALB).
- Other grouping rules in your configuration (less common).

When Ingresses are grouped, listener-level annotations must match across all grouped Ingresses. `alb.ingress.kubernetes.io/ssl-policy` is a listener-level setting and therefore must be identical for all members of the group.

### Fix options

You have three practical ways to resolve the conflict depending on your needs:

1) Unify the ssl policy across the grouped Ingresses

    - Pick a single policy and apply it to every Ingress in the ALB group. For example:

```yaml
alb.ingress.kubernetes.io/ssl-policy: ELBSecurityPolicy-TLS13-1-2-2021-06
```

    - Apply the change by editing the Ingress resources:

```bash
kubectl -n test-dev edit ingress test-app-ingress
kubectl -n test-dev edit ingress test-mgmt-ingress
```

    - Note: the `-Res` policy is generally more restrictive. For a detailed comparison of these policies, see the [Reference: AWS TLS Policy Comparison](#reference-aws-tls-policy-comparison) section below. Confirm that all client platforms that access the ALB can negotiate the stricter policy before switching.

2) Stop grouping them so each Ingress gets its own ALB

    - Give each Ingress a different `alb.ingress.kubernetes.io/group.name`, or remove the grouping annotation entirely.
    - If you used `alb.ingress.kubernetes.io/load-balancer-name` on multiple Ingresses, use distinct names or remove the annotation so the controller creates separate ALBs.

    - Each ALB will then be able to use its own independent `ssl-policy`.

3) Consolidate into a single Ingress (when appropriate)

    - If the Ingresses represent related rules for the same service domain, combine them into one Ingress with multiple rules and a single `alb.ingress.kubernetes.io/ssl-policy`.
    - This reduces ALB count and simplifies management.

### How to identify grouped Ingresses

List Ingress annotations in the namespace and look for group or load balancer name annotations (replace <NAMESPACE> with your namespace):

```bash
kubectl get ingress -n <NAMESPACE> \
    -o custom-columns=NAME:.metadata.name,GROUP:.metadata.annotations.alb.ingress.kubernetes.io/group.name,LBNAME:.metadata.annotations.alb.ingress.kubernetes.io/load-balancer-name,SSLPOLICY:.metadata.annotations.alb.ingress.kubernetes.io/ssl-policy
```

This shows which Ingresses belong to the same group and which `ssl-policy` each has.

### Other annotations that must match when grouped

When Ingresses are grouped, listener-level properties must be consistent across the group. Common listener-level annotations that must match include:

- `alb.ingress.kubernetes.io/listen-ports`
- `alb.ingress.kubernetes.io/scheme` (internet-facing or internal)
- `alb.ingress.kubernetes.io/ip-address-type` (ipv4 or dualstack)

If any of these differ between grouped Ingresses the controller may also fail to build the model.

### After you make changes

The AWS Load Balancer Controller will reconcile automatically. To follow progress and inspect errors, watch the controller logs:

```bash
kubectl -n kube-system logs deploy/aws-load-balancer-controller -f
```

If conflicts persist, re-check all grouped Ingresses and ensure their listener-level annotations are identical.

### Summary

Either unify the `alb.ingress.kubernetes.io/ssl-policy` across all Ingresses that share an ALB, or split them into separate ALBs by changing or removing grouping annotations. Consolidating related rules into a single Ingress is another valid approach when appropriate.



---

## Reference: AWS TLS Policy Comparison

Below is a technical comparison of the two AWS managed TLS policies commonly seen in ALB/NLB configuration conflicts:

**ELBSecurityPolicy-TLS13-1-2-2021-06** (standard) vs **ELBSecurityPolicy-TLS13-1-2-Res-2021-06** (restricted)

**What they have in common:**
- Protocols: TLS 1.3 and TLS 1.2 only (TLS 1.0/1.1 disabled)
- Works with RSA and ECDSA certificates
- TLS 1.3 cipher suites are the same in both (AES-GCM 128/256 and CHACHA20-POLY1305)

**Key differences:**

*ELBSecurityPolicy-TLS13-1-2-2021-06 (standard):*
- Includes a wider set of TLS 1.2 ciphers for compatibility, typically including some CBC-mode suites (e.g., ECDHE-*-AES128/256-SHA256/SHA384) alongside AEAD suites (AES-GCM, CHACHA20)
- Better for supporting older TLS 1.2 clients (older Java, legacy Windows/IE stacks) that don’t negotiate GCM/CHACHA20

*ELBSecurityPolicy-TLS13-1-2-Res-2021-06 (restricted):*
- Removes TLS 1.2 CBC-mode and SHA1 suites; keeps only modern AEAD, forward-secrecy ciphers (ECDHE with AES-GCM and CHACHA20-POLY1305)
- Stricter posture; aligns better with modern security guidance and many compliance requirements
- May break very old TLS 1.2 clients that need CBC/SHA1

**When to choose which:**
- Pick “Res” if you want the strongest security and your clients are modern (most current browsers, recent JVMs, updated OS stacks)
- Pick the non-Res policy if you have to accommodate legacy TLS 1.2 clients and you’re seeing handshake failures with “Res”

**How to verify with clients:**
- Test a legacy CBC suite against your endpoint; it should fail under “Res” and succeed under the standard policy. Example:

```bash
openssl s_client -connect your.host:443 -tls1_2 -cipher 'ECDHE-RSA-AES128-SHA256'
```

- Test modern AEAD suites; they should succeed on both:

```bash
openssl s_client -connect your.host:443 -tls1_2 -cipher 'ECDHE-RSA-AES128-GCM-SHA256'
openssl s_client -connect your.host:443 -tls1_3
```