---
title: "Using AWS Route 53 as Your Domain's Authoritative DNS Server"
date: 2026-06-10
tags: [AWS, Route53, DNS]
---

# Using AWS Route 53 as Your Domain's Authoritative DNS Server

Amazon Route 53 is a scalable and highly available Domain Name System (DNS) web service.  
To make Route 53 the authoritative DNS server for your domain, follow these steps:

---

## 1. Create a Hosted Zone in Route 53
1. Log in to the [AWS Management Console](https://console.aws.amazon.com/route53/).
2. Go to **Route 53 > Hosted Zones**.
3. Click **Create hosted zone**.
4. Enter your domain name (e.g., `example.com`).
5. Select **Public hosted zone** (for internet-facing domains).
6. Click **Create hosted zone**.

✅ Route 53 will automatically create an **NS (Name Server)** record set and an **SOA (Start of Authority)** record.

---

## 2. Get the Route 53 Name Servers
1. After creating the hosted zone, open it in the Route 53 console.
2. Copy the **four NS records** assigned to your domain, for example:
   - `ns-123.awsdns-45.com`
   - `ns-456.awsdns-78.net`
   - `ns-789.awsdns-12.org`
   - `ns-101.awsdns-34.co.uk`

---

## 3. Update Your Domain Registrar
1. Log in to your **domain registrar’s dashboard** (where you purchased your domain, e.g., GoDaddy, Namecheap, Google Domains).
2. Find the section to manage **Nameservers**.
3. Select **Custom nameservers**.
4. Replace the current nameservers with the **four Route 53 nameservers**.
5. Save your changes.

⚠️ DNS propagation may take up to **24–48 hours** worldwide.

---

## 4. Add DNS Records in Route 53
Once Route 53 is your authoritative DNS provider, you can manage DNS records directly in the hosted zone:
- **A record** → Points your domain (e.g., `example.com`) to an IP address.
- **CNAME record** → Aliases one domain to another (e.g., `www.example.com` → `example.com`).
- **MX record** → Directs email traffic to your mail servers.
- **TXT record** → Used for verification, SPF, DKIM, etc.

Example:
- Add an **A record** for `example.com` → `192.0.2.10`.
- Add a **CNAME record** for `www.example.com` → `example.com`.

---

## 5. Verify Setup
You can test your configuration by:
- Running `dig NS example.com` or `nslookup -type=NS example.com` in your terminal.
- Using online DNS checkers like [DNS Checker](https://dnschecker.org) to confirm your domain resolves via Route 53 nameservers.

---

## ✅ Summary
By creating a hosted zone in Route 53, updating your registrar with Route 53’s name servers, and managing your DNS records in Route 53, you have successfully set up **AWS Route 53 as your domain’s authoritative DNS server**.
