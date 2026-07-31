---
Source-AI: Claude
Category: Technical
Time-Context: Coding Session
Topics: [Mobile Security, API Protection, iOS Development, HMAC Signing, Apple App Attest, AWS WAF, Defense in Depth]
tags:
  - ai-distilled
---

# Mobile API Token Security

## Summary
Phil is hardening the CloudFront-exposed Lambda backend for 会意典 (iOS dictionary app) beyond a static `X-App-Secret` header. The conversation covered four layered defences — HMAC request signing, Apple App Attest, certificate pinning, and AWS WAF — including the real threat model, how each attack route works in practice, and a phased implementation roadmap.

## Key Takeaway
HMAC signing solves replay attacks but the secret key still lives in the binary and can be extracted in minutes with `strings MyApp`. The only complete fix is Apple App Attest — the private key is generated inside the Secure Enclave, never leaves the chip, and cannot be extracted even by the app itself.

## Key Insights
- TLS (CloudFront) already protects against network sniffing — the real threats are **binary reverse engineering** and **replay attacks**, not packet capture.
- HMAC + nonce dedup defeats replay (captured requests expire in 30 s, nonces burned in DynamoDB), but an attacker who extracts the key generates fresh valid signatures indefinitely — nonce and timestamp defences are completely bypassed.
- Apple App Attest eliminates the key-extraction class entirely: trust anchor shifts from "a string Phil put in the binary" to "Apple's Secure Enclave + WWDR CA". Forgery requires real Apple hardware running the unmodified binary.
- For a cost-per-request AI app, the real risk is **API cost abuse**, not data theft — the attacker's goal is hammering the Lambda to run up the OpenAI/Claude bill.
- AWS WAF at ~$8–9/month caps blast radius even if the key is stolen — rate limiting turns unlimited abuse into a throttled, expensive attack.
- Certificate pinning stops MITM proxying (Charles, mitmproxy) even on developer devices, closing the route where an attacker probes signing logic via intercepted traffic.

## Decisions Made
- Implementation order: **Layer 1 (HMAC) → Layer 4 (WAF) → Layer 3 (cert pinning) → Layer 2 (App Attest)**
- AWS WAF at ~$8/month: deploy immediately. Bot Control (~$18/month): defer until bot traffic is observed.

## Action Items
- [ ] Implement HMAC request signing on iOS + Lambda (replace static `X-App-Secret`)
- [ ] Add nonce deduplication store in DynamoDB with 60 s TTL
- [ ] Deploy AWS WAF Web ACL: rate-limit + geo-block + Core Managed Rules
- [ ] Plan App Attest registration flow (backend challenge endpoint + public key store in DynamoDB)
- [ ] Add certificate pinning via `URLSessionDelegate` or TrustKit

## Technical Details

### Threat Model

| Threat | Risk | Description |
|---|---|---|
| **Binary extraction** | 🔴 HIGH | Attacker reverse-engineers the `.ipa`, finds hardcoded secret |
| **Replay attack** | 🔴 HIGH | Static secret never rotates → valid forever once stolen |
| **MitM / SSL strip** | 🟡 MED | Without cert pinning, attacker proxies traffic (Charles, mitmproxy) |
| **Network sniffing** | 🟢 LOW | TLS already handles this |

---

### How the Key Gets Stolen (Attack Routes)

**Route 1 — Static Binary Extraction (easiest, ~10 min)**
```bash
unzip MyApp.ipa
cd Payload/MyApp.app
strings MyApp | grep -E '[a-f0-9]{32,}'   # plaintext secrets in __TEXT segment
# or deeper with radare2:
r2 MyApp
> iz    # list all strings in data sections
```

**Route 2 — Runtime Memory Dump (jailbroken device)**
```bash
frida -U -n MyApp -e "
  Interceptor.attach(ptr('HMAC_address'), {
    onEnter(args) {
      console.log('Key:', hexdump(args[1].readByteArray(args[2].toInt32())));
    }
  });
"
```
The key must be in memory when HMAC runs — memory dumps always win against obfuscation.

**Route 3 — MITM Proxy (no cert pinning)**
Charles Proxy / mitmproxy on same WiFi → attacker sees all headers → valid `X-Signature` captured, or signing logic probed by replaying modified canonical strings.

**Once key is stolen — forge indefinitely:**
```python
import hmac, hashlib, time, uuid

STOLEN_KEY = "extracted-secret"

def forge_request(path, body=b""):
    timestamp = str(int(time.time()))
    nonce = uuid.uuid4().hex           # fresh nonce → passes DynamoDB dedup
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = f"{path}{timestamp}{nonce}{body_hash}"
    sig = hmac.new(STOLEN_KEY.encode(), canonical.encode(), hashlib.sha256).hexdigest()
    return {"X-Timestamp": timestamp, "X-Nonce": nonce, "X-Signature": sig}
# Lambda sees: valid timestamp ✓, fresh nonce ✓, valid HMAC ✓ — indistinguishable from real app
```

---

### Layer 1 — HMAC Request Signing

**iOS — per-request signed headers**
```swift
import CryptoKit

struct RequestSigner {
    private static let appSecret = "your-secret-key"

    static func signedHeaders(for path: String, body: Data?) -> [String: String] {
        let timestamp = String(Int(Date().timeIntervalSince1970))
        let nonce     = UUID().uuidString.replacingOccurrences(of: "-", with: "")
        let bodyHash  = body.map { SHA256.hash(data: $0).hexString } ?? ""
        let canonical = "\(path)\(timestamp)\(nonce)\(bodyHash)"
        let key = SymmetricKey(data: Data(appSecret.utf8))
        let sig = HMAC<SHA256>.authenticationCode(for: Data(canonical.utf8), using: key)
        return ["X-Timestamp": timestamp, "X-Nonce": nonce, "X-Signature": Data(sig).hexString]
    }
}
```

**Lambda — verify + anti-replay**
```python
import hmac, hashlib, time

REPLAY_WINDOW_SECONDS = 30

def _verify_hmac_request(headers: dict, path: str, body: bytes) -> bool:
    secret = _get_ssm_param(SSM_APP_SECRET).encode()
    timestamp, nonce, provided_sig = (
        headers.get("x-timestamp", ""),
        headers.get("x-nonce", ""),
        headers.get("x-signature", ""),
    )
    try:
        if abs(time.time() - int(timestamp)) > REPLAY_WINDOW_SECONDS:
            return False
    except ValueError:
        return False
    if _is_nonce_used(nonce):       # DynamoDB TTL store
        return False
    _mark_nonce_used(nonce)
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = f"{path}{timestamp}{nonce}{body_hash}"
    expected  = hmac.new(secret, canonical.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, provided_sig)
```

[explain in details](hmac_explainer.html)

### Layer 2 — Apple App Attest (Architecture)

```
┌─────────────────────────────────────────────────────────┐
│  iOS App                                                  │
│                                                           │
│  1. DCAppAttestService.generateKey()  → keyId             │
│  2. Send keyId to backend to register                    │
│  3. Backend returns challenge (random nonce)             │
│  4. DCAppAttestService.attestKey(keyId, challenge)       │
│     → Apple WWDR CA signs an attestation object         │
│  5. Send attestation to backend for verification         │
│  6. Backend verifies cert chain against Apple's CA      │
│  7. Future requests: generateAssertion(keyId, payload)  │
│     → cryptographic proof this payload is from your app │
└─────────────────────────────────────────────────────────┘
```

**iOS — attestation + per-request assertion**
```swift
import DeviceCheck

class AppAttestManager {
    private let service = DCAppAttestService.shared

    func registerDevice() async throws {
        let keyId = try await service.generateKey()
        let challenge = try await fetchChallenge()
        let clientDataHash = Data(SHA256.hash(data: Data(challenge.utf8)))
        let attestation = try await service.attestKey(keyId, clientDataHash: clientDataHash)
        try await sendAttestation(keyId: keyId, attestation: attestation, challenge: challenge)
        UserDefaults.standard.set(keyId, forKey: "attestKeyId")
    }

    func generateAssertion(for requestBody: Data) async throws -> (assertion: Data, keyId: String) {
        guard let keyId = UserDefaults.standard.string(forKey: "attestKeyId") else {
            throw AttestError.notRegistered
        }
        let clientDataHash = Data(SHA256.hash(data: requestBody))
        let assertion = try await service.generateAssertion(keyId, clientDataHash: clientDataHash)
        return (assertion, keyId)
    }
}
```

**Lambda — verify assertion**
```python
import cbor2, hashlib, base64
from cryptography.hazmat.primitives.asymmetric import ec

def _verify_app_attest_assertion(headers, body, key_id):
    assertion = cbor2.loads(base64.b64decode(headers.get("x-attest-assertion", "")))
    public_key = _load_public_key(key_id)          # from DynamoDB, stored at registration
    client_data_hash = hashlib.sha256(body).digest()
    auth_data = assertion["authenticatorData"]
    verification_data = auth_data + client_data_hash
    try:
        public_key.verify(
            assertion["signature"],
            hashlib.sha256(verification_data).digest(),
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except Exception:
        return False
```

---

### Layer 3 — Certificate Pinning

```swift
class PinnedSessionDelegate: NSObject, URLSessionDelegate {
    private let pinnedHashes = ["BBBBBBB+your+cloudfront+spki+hash+here="]

    func urlSession(_ session: URLSession,
                    didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust,
              let certs = SecTrustCopyCertificateChain(serverTrust) as? [SecCertificate],
              let first = certs.first else {
            completionHandler(.cancelAuthenticationChallenge, nil); return
        }
        let serverHash = extractSPKIHash(from: first)
        if pinnedHashes.contains(serverHash) {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

---

### Layer 4 — AWS WAF (Terraform)

```hcl
resource "aws_wafv2_web_acl" "api_protection" {
  rule {
    name = "RateLimitPerIP"; priority = 1; action { block {} }
    statement {
      rate_based_statement { limit = 100; aggregate_key_type = "IP" }
    }
  }
  rule {
    name = "GeoBlock"; priority = 2; action { block {} }
    statement {
      not_statement {
        geo_match_statement { country_codes = ["CN", "GB", "AU", "US"] }
      }
    }
  }
}
```

**WAF cost for mobile app at current traffic scale:**

| Component | Cost/month |
|---|---|
| 1 Web ACL | $5.00 |
| Rate-limit rule | $1.00 |
| Geo-block rule | $1.00 |
| AWS Core Managed Rules (SQLi, XSS) | $1.00 |
| **Fixed subtotal** | **$8.00** |
| + requests (500K early stage) | ~$0.30 |
| **Realistic total** | **~$8–9/month** |

Note: As of Oct 2024, CloudFront no longer charges for requests blocked by WAF — WAF pays for itself if it's blocking significant junk traffic.

---

### Implementation Roadmap

```
Week 1:  Layer 1 — HMAC signing          ← biggest security gain, moderate effort
Week 2:  Layer 4 — WAF (rate + geo)      ← pure AWS config, zero code changes
Week 3:  Layer 3 — certificate pinning   ← protects dev/QA environments too
Month 2: Layer 2 — App Attest            ← requires backend registration flow
```

---

### HMAC vs App Attest: Attack Surface Comparison

| Attack | HMAC only | HMAC + App Attest |
|---|---|---|
| Network sniff | ✅ Protected | ✅ Protected |
| Replay attack | ✅ Protected (nonce) | ✅ Protected |
| Binary extraction | ❌ Key stolen | ✅ No key to steal |
| Jailbreak + Frida | ❌ Key dumped at runtime | ✅ Key in Secure Enclave |
| Simulator/script abuse | ❌ Can forge requests | ✅ Blocked (real device required) |
| Automated API scraping | ❌ Unlimited if key stolen | ✅ Requires real Apple hardware |

---

### Defense-in-Depth Request Flow

```
Request from iOS App
        │
        ▼
[CloudFront + TLS]          ← encrypts transit (sniff protection)
        │
        ▼
[AWS WAF]                   ← rate limit / geo-block / bot detection
        │
        ▼
[Lambda]
  ├─ App Attest assertion   ← proves: real device + unmodified binary + correct App ID
  ├─ HMAC signature check   ← proves: request integrity + anti-replay
  └─ Nonce dedup (DynamoDB) ← kills replayed captured requests
```

## Resources Referenced
- Apple `DCAppAttestService` — iOS framework for hardware-backed attestation via Secure Enclave
- AWS WAF pricing (2025) — Web ACL $5/month + $1/rule/month + $0.60/million requests
- TrustKit — iOS library for certificate pinning with reporting
- Frida — dynamic instrumentation toolkit used for runtime memory inspection on jailbroken devices
- cbor2 + cryptography — Python libraries required for App Attest assertion verification on Lambda

## Related Questions
- When implementing App Attest, what does the backend DynamoDB schema look like for storing public keys per `keyId`?
- Is nonce deduplication in a single DynamoDB table sufficient, or does Lambda cold-start latency risk race conditions on concurrent requests?
- How does CloudFront certificate rotation interact with pinned SPKI hashes — what's the re-pinning process in production?

## Related Topics
HMAC Request Signing
Apple App Attest
Certificate Pinning iOS
AWS WAF Rate Limiting
Replay Attack Prevention
Secure Enclave
Defense in Depth API Security
Mobile Binary Reverse Engineering
DynamoDB Nonce Store
API Cost Abuse Protection
