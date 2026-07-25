# Kubernetes Egress
  > Egress Network Policy, Istio Gateway, and More

## What is Kubernetes Egress?

In Kubernetes, Egress refers to the traffic that flows out of a cluster, from a pod to an external endpoint. Egress traffic can be used to access external services such as databases, APIs, and other services running outside of the cluster.

<b>In a Kubernetes cluster, pods are isolated from the external network by default</b>, which means that they are not able to initiate connections to external services. To allow pods to access external services, Kubernetes provides a feature called Egress Network Policy, which allows you to define rules that specify which external endpoints pods are allowed to access.

This is part of a series of articles about service mesh.


## Kubernetes Ingress vs. Egress Traffic

In Kubernetes, ingress and egress traffic refer to the direction of network traffic in relation to a Kubernetes cluster.

Ingress traffic refers to the traffic that flows into the cluster, from an external endpoint to a pod. Ingress traffic is typically used for incoming HTTP or HTTPS requests to a Kubernetes cluster, and it is typically handled by an Ingress controller. An Ingress controller is a component that listens for incoming requests and routes them to the appropriate service based on the URL or other information.

Egress traffic, on the other hand, refers to the traffic that flows out of a cluster, from a pod to an external endpoint. Egress traffic is used to access external services such as databases, APIs, and other services running outside of the cluster.

Both types of traffic are important for the proper functioning of a Kubernetes cluster, and they need to be properly configured and secured to ensure that the cluster is accessible and secure.

## Restricting Egress Traffic with Network Policies

You can restrict egress traffic with Kubernetes network policies by creating and applying NetworkPolicy objects that specify the desired egress rules.

To create a NetworkPolicy that restricts egress traffic to a specific set of IP ranges, you can define an egress rule that specifies the to field with the desired IP ranges, and ports field if necessary.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-egress
spec:
  podSelector:
    matchLabels:
      app: myapp
  egress:
  - to:
    - ipBlock:
        cidr: 10.0.0.0/28
    ports:
    - protocol: TCP
      port: 80
```


You can also restrict egress traffic to a specific set of ports, protocols, and IP ranges.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-egress
spec:
  podSelector:
    matchLabels:
      app: myapp
  egress:
  - ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
    to:
    - ipBlock:
        cidr: 10.0.0.0/28
```

Note: CIDR 10.0.0.0/28 has 16 IP addresses ranging from 10.0.0.0 – 10.0.0.15.

Once you have created the NetworkPolicy, you can apply it to the desired pods in your cluster by using the kubectl apply command.

```shell
kubectl apply -f restrict-egress.yaml
```

This will restrict egress traffic from the pods with label “app: myapp” to the specified IP ranges or ports.

<b>One limitation of using NetworkPolicy for restricting access to specific resources is that it only works for traffic within the same cluster</b>. NetworkPolicy objects do not have visibility or control over traffic that originates from outside the cluster or that is sent to external destinations. If you want to control access to external resources, you will need to use other network security tools, such as a firewall or an external load balancer, in conjunction with NetworkPolicy. The policy rules must specify these resources as IP addresses. 

## Controlling Kubernetes Egress traffic with Istio Egress Gateway

Istio is an open source service mesh platform that provides a way to connect, secure, control, and observe services in a microservices architecture. It provides a set of APIs and tools for configuring, managing, and observing the behavior of service-to-service communication in a Kubernetes cluster.

Istio’s Egress Gateway can be used to control egress traffic from a Kubernetes cluster by directing it through a specific service proxy before it reaches its destination. This allows for the application of rules and policies to the outbound traffic, such as traffic shaping, rate limiting, and access control.

Here are the general steps for controlling egress traffic using Istio’s Egress Gateway:

1. Create a Gateway resource that defines the ports and protocols that the Egress Gateway will listen on.
2. Create a VirtualService resource that routes traffic to the Egress Gateway. This can be done by using the hosts field to match the external destinations that the egress traffic should be sent to and the gateway field to specify the Egress Gateway.
3. Create a DestinationRule resource that defines the service for the external destinations.
4. Create a ServiceEntry resource to configure the external services that the Egress Gateway should be able to reach.
5. Create a Policy resource to apply rules and policies to the egress traffic, such as access control, rate limiting, and traffic shaping.


With these steps, the egress traffic will be directed through the Istio Egress Gateway, where rules and policies can be applied before it reaches its destination.

## Quick tutorial: Deploying Istio and creating an Egress Gateway

To get started with Istio:

2. Install Istio: First, you need to have Istio installed on your Kubernetes cluster. You can use the Istio installation guide to install it.
2. Create the Egress Gateway: Once Istio is installed, you can create the Egress Gateway by applying the following Gateway and VirtualService resources:


```yaml 
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: istio-egressgateway
spec:
  selector:
    istio: egressgateway
  servers:
  - port:
      name: http
      number: 80
      protocol: HTTP
    hosts:
    - "*"
```

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: istio-egressgateway
spec:
  hosts:
  - "*"
  gateways:
  - istio-egressgateway
  http:
  - match:
    - port: 80
    route:
    - destination:
        host: istio-egressgateway
```

3. Create the Egress Gateway Service: After creating the Gateway and VirtualService resources, you need to create the Egress Gateway Service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: istio-egressgateway
  labels:
    istio: egressgateway
spec:
  type: ClusterIP
  selector:
    istio: egressgateway
  ports:
  - name: http
    port: 80
    targetPort: 80
```

4. Configure the Egress Gateway: You can configure the Egress Gateway to control the traffic by creating a DestinationRule, ServiceEntry, and Policy resources.

5. Verify the deployment: You can use the following command to check the pods running on your cluster:

```shell
kubectl get pods -n istio-system
```

You should see the istio-egressgateway pod running.


> origin https://www.solo.io/topics/service-mesh/kubernetes-egress/