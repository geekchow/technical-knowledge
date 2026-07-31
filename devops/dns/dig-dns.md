# How does DNS work ?


```shell
dig facebook.github.io

# dig @8.8.8.8 +trace facebook.github.io
# doesn't work behind GFW.
```

```shell
; <<>> DiG 9.10.6 <<>> facebook.github.io
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 55601
;; flags: qr rd ra; QUERY: 1, ANSWER: 4, AUTHORITY: 8, ADDITIONAL: 9

;; QUESTION SECTION:
;facebook.github.io.		IN	A

;; ANSWER SECTION:
facebook.github.io.	669	IN	A	185.199.109.153
facebook.github.io.	669	IN	A	185.199.108.153
facebook.github.io.	669	IN	A	185.199.110.153
facebook.github.io.	669	IN	A	185.199.111.153
######################################################
# fqdn facebook.github.io A records point to four ips# 
######################################################

;; AUTHORITY SECTION:
github.io.		488	IN	NS	ns-1622.awsdns-10.co.uk.
github.io.		488	IN	NS	dns1.p05.nsone.net.
github.io.		488	IN	NS	dns2.p05.nsone.net.
github.io.		488	IN	NS	ns-1339.awsdns-39.org.
github.io.		488	IN	NS	dns3.p05.nsone.net.
github.io.		488	IN	NS	dns4.p05.nsone.net.
github.io.		488	IN	NS	ns-692.awsdns-22.net.
github.io.		488	IN	NS	ns-393.awsdns-49.com.
######################################################
# dns servers which holds the dns record of github.io#
##################################################

;; ADDITIONAL SECTION:
dns1.p05.nsone.net.	44595	IN	A	198.51.44.5
dns2.p05.nsone.net.	44595	IN	A	198.51.45.5
dns3.p05.nsone.net.	48118	IN	A	198.51.44.69
dns4.p05.nsone.net.	78176	IN	A	198.51.45.69
ns-1339.awsdns-39.org.	44597	IN	A	205.251.197.59
ns-1622.awsdns-10.co.uk. 120727	IN	A	205.251.198.86
ns-393.awsdns-49.com.	125151	IN	A	205.251.193.137
ns-692.awsdns-22.net.	44593	IN	A	205.251.194.180
dns1.p05.nsone.net.	44595	IN	AAAA	2620:4d:4000:6259:7:5:0:1
##################################################
# DNS Servers ips addresses #
##################################################
```



> references
  - https://www.ruanyifeng.com/blog/2016/06/dns.html
  - https://www.youtube.com/watch?v=oKiojDyAuXg