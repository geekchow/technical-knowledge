---
title: "DNS Record Types Explained"
date: 2026-06-11
tags: [DNS, Networking]
---

# DNS Record Types Explained

DNS records are the **actual data stored on authoritative DNS servers** that define how a domain should be resolved or handled. Each record has a **type**, which determines its purpose.  

---

## 🔹 Common DNS Record Types (Explained in Detail)

---

### 1. A Record (Address Record)
- **Purpose:** Maps a domain name to an IPv4 address.  
- **Example:**  
  ```
  example.com.   IN   A   93.184.216.34
  ```
- **Use Case:** When you type `example.com`, the A record tells your browser which server (IPv4 address) to connect to.  
- **Analogy:** Like a street address for a house.  

---

### 2. AAAA Record (IPv6 Address Record)
- **Purpose:** Same as an A record, but for IPv6 addresses.  
- **Example:**  
  ```
  example.com.   IN   AAAA   2606:2800:220:1:248:1893:25c8:1946
  ```
- **Use Case:** Required as the world transitions to IPv6.  
- **Analogy:** Like having a new-format street address for the same house.  

---

### 3. CNAME Record (Canonical Name Record)
- **Purpose:** Makes one domain an alias of another.  
- **Example:**  
  ```
  www.example.com.   IN   CNAME   example.com.
  ```
- **Use Case:** Often used so `www.example.com` points to `example.com` without duplicating A/AAAA records.  
- **Analogy:** Like saying “Call me by my nickname, but it still refers to the same person.”  

---

### 4. MX Record (Mail Exchange Record)
- **Purpose:** Specifies the mail servers responsible for receiving emails for a domain.  
- **Example:**  
  ```
  example.com.   IN   MX   10 mail1.example.com.
  example.com.   IN   MX   20 mail2.example.com.
  ```
- **Use Case:** When you send an email to `user@example.com`, mail servers use the MX record to know where to deliver it.  
- **Priority:** The number (10, 20, etc.) defines priority (lower = higher priority).  
- **Analogy:** Like listing multiple mailboxes, with a preferred one.  

---

### 5. TXT Record (Text Record)
- **Purpose:** Holds arbitrary text data. Widely used for verification and security.  
- **Examples:**
  - **SPF (Sender Policy Framework):** Prevents email spoofing.  
    ```
    example.com. IN TXT "v=spf1 include:_spf.google.com ~all"
    ```
  - **Domain Verification (Google, Microsoft, etc.):**  
    ```
    example.com. IN TXT "google-site-verification=abc123"
    ```
- **Analogy:** Like sticky notes attached to a domain for different purposes.  

---

### 6. NS Record (Name Server Record)
- **Purpose:** Specifies which DNS servers are authoritative for a domain.  
- **Example:**  
  ```
  example.com.   IN   NS   ns1.example-dns.com.
  example.com.   IN   NS   ns2.example-dns.com.
  ```
- **Use Case:** When delegating a domain to another DNS provider.  
- **Analogy:** Like saying “This company’s help desk handles all inquiries for my account.”  

---

### 7. SOA Record (Start of Authority)
- **Purpose:** Defines authoritative information about a DNS zone.  
- **Contains:**  
  - Primary nameserver  
  - Email of the domain admin  
  - Serial number (for tracking changes)  
  - Refresh/retry/expire timings for caching  
- **Example:**  
  ```
  example.com. IN SOA ns1.example.com. admin.example.com. (
                 2025090201 ; Serial
                 3600       ; Refresh
                 600        ; Retry
                 1209600    ; Expire
                 86400 )    ; Minimum TTL
  ```
- **Analogy:** Like the title page of a book — it defines who published it and when it was updated.  

---

### 8. PTR Record (Pointer Record)
- **Purpose:** Reverse DNS lookup — maps an IP address back to a domain.  
- **Example:**  
  ```
  34.216.184.93.in-addr.arpa.   IN   PTR   example.com.
  ```
- **Use Case:** Often used for spam prevention (mail servers check that the sending IP has a matching PTR).  
- **Analogy:** Like looking up a phone number to find out who owns it.  

---

### 9. SRV Record (Service Record)
- **Purpose:** Defines services available in a domain (protocol, port, target).  
- **Example (used in SIP, XMPP, Microsoft services):**  
  ```
  _sip._tcp.example.com.   IN   SRV   10 60 5060 sipserver.example.com.
  ```
  - Priority = 10  
  - Weight = 60  
  - Port = 5060  
  - Target = sipserver.example.com  
- **Analogy:** Like a business card that says “This service is available at this location and port.”  

---

### 10. CAA Record (Certification Authority Authorization)
- **Purpose:** Specifies which Certificate Authorities (CAs) are allowed to issue SSL/TLS certificates for the domain.  
- **Example:**  
  ```
  example.com. IN CAA 0 issue "letsencrypt.org"
  ```
- **Use Case:** Prevents unauthorized or fraudulent certificates.  
- **Analogy:** Like saying “Only this locksmith is allowed to make copies of my keys.”  

---

## ⚡ Summary Table

| Record Type | Purpose | Example |
|-------------|---------|---------|
| **A** | IPv4 address | `example.com → 93.184.216.34` |
| **AAAA** | IPv6 address | `example.com → 2606:2800::1234` |
| **CNAME** | Alias to another domain | `www.example.com → example.com` |
| **MX** | Mail servers | `example.com → mail.example.com` |
| **TXT** | Extra text info (SPF, verification) | `v=spf1 include:_spf.google.com ~all` |
| **NS** | Authoritative nameservers | `example.com → ns1.dns.com` |
| **SOA** | Zone metadata | Serial, refresh, retry, etc. |
| **PTR** | Reverse lookup | `93.184.216.34 → example.com` |
| **SRV** | Service definition | `_sip._tcp.example.com → sipserver` |
| **CAA** | Allowed SSL certificate issuers | `issue "letsencrypt.org"` |
