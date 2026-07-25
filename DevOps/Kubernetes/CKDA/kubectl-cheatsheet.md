# 🧭 Kubernetes kubectl Cheat Sheet

## ⚙️ Basic Commands
```bash
kubectl version --short
kubectl cluster-info
kubectl api-resources
kubectl config current-context
kubectl config use-context <context-name>
kubectl config get-contexts
```

## 📦 Namespaces
```bash
kubectl get ns
kubectl create ns my-namespace
kubectl delete ns my-namespace
kubectl get pods -n my-namespace

```

## 🧱 Pods
```bash
kubectl get pods
kubectl get pods -A
kubectl get po -o wide
kubectl run nginx --image=nginx:latest
kubectl describe pod nginx
kubectl logs -f nginx
kubectl logs nginx --previous
kubectl exec -it nginx -- /bin/bash
kubectl delete pod nginx
kubectl get pods --show-labels
kubectl logs -f nginx -c my-sidecar-container
```

## 📄 Deployments
```bash
kubectl get deploy
kubectl create deploy myapp --image=nginx
kubectl scale deploy myapp --replicas=3
kubectl set image deploy/myapp nginx=nginx:1.25
kubectl rollout status deploy/myapp
kubectl rollout undo deploy/myapp
kubectl delete deploy myapp
```

## 🧩 Services
```bash
kubectl get svc
kubectl expose deploy myapp --port=80 --target-port=8080 --type=ClusterIP
kubectl expose deploy myapp --port=80 --type=NodePort
kubectl expose deploy myapp --port=80 --type=LoadBalancer
kubectl describe svc myapp
kubectl delete svc myapp
```

## 🧮 ConfigMaps & Secrets
```bash
kubectl create configmap my-config --from-literal=env=prod
kubectl create configmap my-config --from-file=config.yaml
kubectl get cm my-config -o yaml
kubectl create secret generic my-secret --from-literal=password=verysecret
kubectl create secret generic my-ssl --from-file=tls.crt --from-file=tls.key
kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 -d
```

## 🧠 Nodes & Cluster
```bash
kubectl get nodes -o wide
kubectl describe node <node-name>
kubectl cordon <node-name>
kubectl drain <node-name> --ignore-daemonsets
kubectl uncordon <node-name>
```

## 📊 Monitoring & Debugging
```bash
kubectl get all
kubectl top pod
kubectl top node
kubectl debug -it mypod --image=busybox
kubectl port-forward pod/nginx 8080:80
```

## 📘 YAML Apply & Diff
```bash
kubectl apply -f deployment.yaml
kubectl apply -f deployment.yaml --dry-run=client
kubectl diff -f deployment.yaml
kubectl delete -f deployment.yaml
```

## 🧾 Labels & Selectors
```bash
kubectl label pod nginx app=web
kubectl get pods -l app=web
kubectl label pod nginx app-
kubectl get pods -l 'env=prod,app=web'
```

## 🪶 Context Shortcuts
```bash
alias k='kubectl'
alias kgp='kubectl get pods'
alias kga='kubectl get all'
alias kdp='kubectl describe pod'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
```

## 📚 Resource Short Names
| Resource Type | Short Name |
|----------------|-------------|
| pods | po |
| services | svc |
| deployments | deploy |
| namespaces | ns |
| configmaps | cm |
| secrets | secret |
| replicasets | rs |
| nodes | no |
| persistentvolumeclaims | pvc |
| persistentvolumes | pv |

---

# 🧰 Mounting Volumes, ConfigMaps, and Secrets

## 🔹 1. Mount a Secret as a Volume
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-vol-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ["/bin/sh", "-c", "cat /etc/secret-volume/password && sleep 3600"]
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secret-volume
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: my-secret
```

### 👉 Create the secret
```bash
kubectl create secret generic my-secret --from-literal=password=verysecret
```

---

## 🔹 2. Mount a ConfigMap as a Volume
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-vol-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ["/bin/sh", "-c", "cat /etc/config/app-config && sleep 3600"]
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

### 👉 Create the ConfigMap
```bash
kubectl create configmap app-config --from-literal=app-config="mode=prod"
```

---

## 🔹 3. Combine Secret + ConfigMap Volumes
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: config-secret-combo
spec:
  containers:
  - name: app
    image: busybox
    command: ["/bin/sh", "-c", "echo --- CONFIG ---; cat /config/app.conf; echo --- SECRET ---; cat /secrets/password; sleep 3600"]
    volumeMounts:
    - name: config-volume
      mountPath: /config
    - name: secret-volume
      mountPath: /secrets
      readOnly: true
  volumes:
  - name: config-volume
    configMap:
      name: app-config
  - name: secret-volume
    secret:
      secretName: my-secret
```

---

## 🔹 4. Inject Secret as Environment Variable
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-env-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ["/bin/sh", "-c", "echo The password is $DB_PASSWORD; sleep 3600"]
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: my-secret
          key: password
```

---

## 🔹 5. Inject ConfigMap as Environment Variables
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: config-env-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ["/bin/sh", "-c", "env; sleep 3600"]
    envFrom:
    - configMapRef:
        name: app-config
```

## Inspect k8s api-resources 

```shell
kubectl explain deployment

kubectl explain deployment.spec

kubectl explain pod

kubectl explain pod.spec.containers

kubectl explain secret

# check before apply 
kubectl apply --dry-run=client -f task1-pod.yaml
```

## JsonPath to extract info

```bash
kubectl get pod storepod -o jsonpath="{.status.phase}"

# beautify json output
kubectl get pod storepod -o jsonpath="{.status.conditions}" | jq .


```