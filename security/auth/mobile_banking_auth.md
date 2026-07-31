# 🏦 **1. High-Level Flow Overview**

A mobile banking app must ensure:

-   **You are who you say you are** → *Authentication*\
-   **You can only do what you're allowed to do** → *Authorization*\
-   **Your device/app identity is verified** → *Device/App attestation*\
-   **Requests are safe and not fraudulent** → *Risk & fraud checks*

Most modern banks use:

-   **API Gateway + Identity Provider (IdP)**
-   **OAuth 2.0 / OpenID Connect tokens**
-   **Microservices behind the gateway**
-   **Device-bound cryptographic keys**
-   **Backend for Frontend (BFF)** pattern

------------------------------------------------------------------------

# 🧩 **2. Typical Components**

  -----------------------------------------------------------------------
  Component                   Responsibility
  --------------------------- -------------------------------------------
  **Mobile App**              UI, local crypto store, token storage,
                              secure biometric

  **Authentication Service /  Login, MFA, OAuth2/OIDC token issuance
  IdP**                       

  **API Gateway**             Token validation, routing, rate limiting,
                              threat detection

  **Microservices**           Accounts, payments, transfers, cards,
                              notifications

  **Risk / Fraud Engine**     Geo/IP/device/fingerprint scoring

  **Device Binding Service**  Associates device with user identity

  **Audit/Logging services**  Transaction audit trail
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 🔐 **3. Authentication Flow (Mobile Banking)**

### **3.1 First-Time Login**

**1. App installs → device registration** - App generates **asymmetric
key pair** inside secure HW (Secure Enclave/Keystore) - Sends device
ID + public key → *Device Binding Service* - Server stores device public
key

**2. User enters credentials (username/password or phone/email)** - Sent
over **TLS**, with **MTLS** in some banks.

**3. IdP validates user credentials** - Checks password + brute-force
detection - Checks device fingerprint - risk score from fraud engine

**4. MFA challenge** - OTP / Push / Biometrics / Security token

**5. IdP issues tokens** - **ID Token (JWT)** - **Access Token (often
opaque or JWT)** - **Refresh Token (device-bound, cryptographically
protected)**

**6. App securely stores tokens** - Refresh token stored in Secure
Enclave or hardware-backed keystore.

------------------------------------------------------------------------

### **3.2 Subsequent Logins**

User opens app:

-   App calls "silent authentication" using **device-bound refresh
    token**
-   App uses biometrics locally (FaceID/TouchID) to unlock token usage
-   App exchanges refresh token → new access token
-   No credentials needed.

------------------------------------------------------------------------

# 🛡 **4. Authorization Flow (Microservices)**

Microservices *never* authenticate directly with user credentials.

Instead:

1.  Mobile app sends request → API Gateway\

2.  Request contains **Bearer Access Token**\

3.  API Gateway validates token:

    -   Signature (RSA/ECDSA)
    -   Expiration
    -   Audience / issuer
    -   Scope/roles

4.  Gateway enriches context (user ID, roles, risk score)

5.  Gateway forwards to relevant microservice\

6.  Microservice performs **fine-grained authorization** Examples:

    -   Payments service → Can user transfer this amount?
    -   Cards service → Does user own this card?
    -   Accounts → Filter accounts by ownership

------------------------------------------------------------------------

# 🧿 **5. Token Types**

### **Access Token (JWT or Opaque)**

-   Short-lived (5--10 mins)
-   Carries:
    -   user_id
    -   device_id
    -   scopes: `accounts.read`, `payments.transfer`
    -   risk_score
    -   auth_strength (password + otp + biometric)

### **Refresh Token**

-   Long-lived (30--90 days)
-   Device-bound → cannot be used from browsers/other devices
-   Rotated after every use (secure refresh token rotation)

------------------------------------------------------------------------

# 📲 **6. Device Binding / Attestation**

Banks almost always bind the app to a physical device:

-   Secure Enclave / Keystore key pair

-   Public key registered at onboarding

-   App signs every sensitive request:

        signature = Sign(privateKey, transactionPayloadHash)

-   Backend validates signature using stored public key

This prevents:

-   Token theft reuse
-   Using your refresh token on another device
-   App cloning

------------------------------------------------------------------------

# 🕵️‍♂️ **7. Risk Engine Integration**

Every request or login is scored:

-   Geo-location anomaly
-   Device integrity (rooted/jailbroken)
-   IP reputation
-   Velocity checks (too many requests)
-   Transaction patterns

Risk score influences:

-   Whether MFA is required
-   Whether transaction is blocked
-   Transfer limits

------------------------------------------------------------------------

# 📡 **8. API Gateway Pattern**

The gateway:

-   Validates tokens
-   Rate limits
-   Normalizes errors
-   Routes to microservices
-   Attaches user context to headers (or uses a service mesh)

Example headers:

    X-User-ID: 12345
    X-Device-ID: aabbcc112233
    X-Scopes: accounts.read,payments.transfer
    X-Auth-Strength: mfa

------------------------------------------------------------------------

# ⚙️ **9. Microservices Behavior**

### Microservices do NOT:

-   Validate JWT signatures
-   Manage user sessions

### Microservices DO:

-   Authorize based on scopes/roles
-   Enforce data ownership ("User 123 can only see accounts for user
    123")
-   Log all activity
-   Interact with Event Store for audit

------------------------------------------------------------------------

# 🔄 **10. Example Mobile Banking Request Flow**

### **GET /accounts**

1.  App → GET /accounts with Access Token\
2.  Gateway validates token\
3.  Gateway calls Accounts service with user ID\
4.  Accounts service filters accounts by user\
5.  Response returned

------------------------------------------------------------------------

### **POST /transfer**

1.  App signs transfer payload using device private key\
2.  App sends: payload + signature + access token\
3.  Gateway validates token\
4.  Payment service validates signature (device identity)\
5.  Fraud engine scores transaction\
6.  If risky → triggers MFA\
7.  If approved → executes transfer\
8.  Logs audit event

------------------------------------------------------------------------

# 🎯 Summary (Super Simple)

**Authentication:**\
- OAuth2/OIDC with MFA + biometrics\
- Device-bound refresh tokens\
- Tokens from IdP

**Authorization:**\
- Gateway validates tokens and scopes\
- Microservices enforce fine-grained access rules

**Security Enhancements:**\
- Device binding\
- Transaction signing\
- Fraud/risk scoring\
- Secure enclave key usage\
- API gateway as control plane
