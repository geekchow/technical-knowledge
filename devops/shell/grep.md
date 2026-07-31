# grep 


## After
```bash
# grep after 3 lines
grep "error" logfile.txt -A 3
```

## Before
```bash
# grep before 5 lines 
grep "pattern" -B 5 file.txt
```


## Context
```bash
# Search for "critical" and show 2 lines before/after
grep "critical" app.log -C 2
```


## Combine sample
```bash
# grep 
kubectl logs pod-name | grep "Exception" -A 10 -B 5
```

