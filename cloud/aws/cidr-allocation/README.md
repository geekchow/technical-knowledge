# Allocate CIDR dynamically via `cidrsubnet`

terraform provide built-in function `cidrsubnet` to caculate subnet cidr from a given vpc cidr.

`cidrsubnet` declaration
```shell
cidrsubnet(prefix, newbits, netnum)
```

Start terraform console
```shell
terraform console
```


Try run `cidrsubnet` in terraform console.
```shell

> cidrsubnet("10.1.0.0/16", 8, 1)
"10.1.1.0/24"
> cidrsubnet("10.1.0.0/16", 8, 2)
"10.1.2.0/24"
> cidrsubnet("10.1.0.0/16", 8, 3)
"10.1.3.0/24"

> cidrsubnet("192.168.1.0/24", 4, 0)
"192.168.1.0/28"
> cidrsubnet("192.168.1.0/24", 4, 1)
"192.168.1.16/28"
> cidrsubnet("192.168.1.0/24", 4, 2)
"192.168.1.32/28"

```

