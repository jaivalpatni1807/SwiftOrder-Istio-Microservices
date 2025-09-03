# SwiftOrder-Istio: A Microservices Application with Istio

SwiftOrder is a sample e-commerce application built with microservices and deployed on a Kubernetes cluster with Istio. This project demonstrates how Istio enhances a microservices architecture by providing advanced features such as traffic management for canary deployments, mTLS for secure communication, and authorization policies.

## Project Architecture

The application is composed of three services:

- **order-api**: A Flask-based Python application that handles incoming order requests. It acts as the central orchestrator, communicating with the user-service and inventory-service to validate and confirm orders.

- **user-service**: A Node.js and Express application that manages user credit information. It checks if a user has sufficient credit to place an order. This service has two versions, v1 and v2, configured for canary deployments.

- **inventory-service**: A Flask-based Python application that manages product stock. It verifies if an item is available in stock before an order is confirmed.

- **PostgreSQL Database**: A PostgreSQL database is used by both the user-service and inventory-service to store user and inventory data.

The services communicate via HTTP, and their interactions are governed by Istio to apply security and traffic routing policies.

## Istio Features Demonstrated

### Canary Deployment
The user-service is deployed in two versions, v1 and v2. A VirtualService resource is configured to route 90% of the traffic to v1 and 10% to v2, allowing for a controlled, gradual rollout of the new version.

### Mutual TLS (mTLS)
A PeerAuthentication policy is enabled to enforce strict mTLS mode within the swift-order namespace. This ensures that all service-to-service communication is encrypted and authenticated, providing enhanced security.

### Authorization Policies
AuthorizationPolicy resources are used to restrict communication between services. Specifically, policies are in place to ensure that only the order-api service account can communicate with the user-service and inventory-service.

### Ingress Gateway
An Istio Gateway and VirtualService expose the order-api to external traffic, allowing users to interact with the application.

## How to Deploy and Run SwiftOrder

### Prerequisites

- **Minikube**: A local Kubernetes cluster
- **kubectl**: The Kubernetes command-line tool
- **Istio and other addons**: Enabled within your Minikube cluster

```bash
minikube addons enable istio-provisioner
minikube addons enable istio
minikube addons enable ingress
minikube addons enable registry
minikube addons enable default-storageclass
minikube addons enable storage-provisioner
```

### Deployment Steps

#### 1. Set up Minikube's Docker Environment

Use the following command to point your local Docker daemon to the Minikube internal registry. This allows you to build images directly into the Minikube cluster.

```bash
minikube -p minikube docker-env | Invoke-Expression
```

#### 2. Build Docker Images

Build the Docker images for each service using their respective Dockerfiles.

```bash
docker build -t swiftorder_order:latest ./app-code/order-api
docker build -t swiftorder_inventory:latest ./app-code/inventory-service
docker build -t swiftorder_user:latest ./app-code/user-service
```

#### 3. Deploy the Database and Services

Apply the Kubernetes manifests in the k8s-istio directory in the correct order.

```bash
# Create the swift-order namespace and enable Istio injection
kubectl apply -f k8s-istio/00-namespace.yaml

# Deploy the PostgreSQL database (StatefulSet, Service, ConfigMaps, Secret)
kubectl apply -f k8s-istio/k8s-db/

# Deploy the microservices (Deployments, Services, ServiceAccounts)
kubectl apply -f k8s-istio/01-deployments-services.yaml

# Apply Istio Gateway to expose the application
kubectl apply -f k8s-istio/02-gateway.yaml

# Apply DestinationRules to define service subsets (v1/v2)
kubectl apply -f k8s-istio/03-destinationrules.yaml

# Apply the baseline VirtualService, routing all user-service traffic to v1
kubectl apply -f k8s-istio/04-virtualservices-baseline.yaml

# Enforce mTLS for all services in the namespace
kubectl apply -f k8s-istio/06-mtls-peer-auth.yaml

# Apply Authorization Policies
kubectl apply -f k8s-istio/07-authz-policies.yaml
```

#### 4. Expose the Gateway

To access the application from your host machine, you need to expose the Istio ingress gateway. The `minikube tunnel` command creates a dedicated external IP for the ingress gateway.

```bash
minikube tunnel
```

> **Note**: Keep this command running in a separate terminal.

#### 5. Verify the Deployment

You can check the status of your pods and services to ensure everything is running correctly.

```bash
kubectl get pods -n swift-order
kubectl get svc -n swift-order
```

#### 6. Test the Application

You can now send requests to the order-api. The gateway's external IP will be shown in the minikube tunnel output.

**External IP**: The output of `minikube tunnel` will give you the external IP to use for testing.

**Test endpoints**:

- Check stock: 
  ```bash
  curl -X GET http://<EXTERNAL-IP>/inventory/A543/check
  ```

- Check credit (v1): 
  ```bash
  curl -X GET http://<EXTERNAL-IP>/users/101/credit
  ```

- Create a new order: 
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"userId": 101, "itemId": "A543"}' http://<EXTERNAL-IP>/api/orders
  ```

## Canary Deployment Example

To demonstrate a canary release, you can switch from the baseline virtual service to the canary version, which routes 10% of traffic to the user-service v2.

### Apply the Canary VirtualService

This will overwrite the previous user-service VirtualService.

```bash
kubectl apply -f k8s-istio/05-virtualservices-canary.yaml
```

### Test the Canary Release

Repeatedly send requests to the user-service to observe the traffic splitting. You can check the version field in the response to see which version handled the request.

```bash
curl http://<EXTERNAL-IP>/api/orders
```

You should see approximately 9 out of 10 requests being served by user-service-v1 and 1 being served by user-service-v2. This demonstrates how Istio provides fine-grained control over service traffic.

## Project Structure

```
SwiftOrder-Istio/
├── app-code/
│   ├── order-api/
│   ├── inventory-service/
│   └── user-service/
└── k8s-istio/
    ├── k8s-db/
    │   ├── 00-secret.yaml
    │   ├── 01-configmap.yaml
    │   └── 02-postgre-statefulset.yaml
    ├── 00-namespace.yaml
    ├── 01-deployments-services.yaml
    ├── 02-gateway.yaml
    ├── 03-destinationrules.yaml
    ├── 04-virtualservices-baseline.yaml
    ├── 05-virtualservices-canary.yaml
    ├── 06-mtls-peer-auth.yaml
    └── 07-authz-policies.yaml
```

## Technologies Used

- **Kubernetes**: Container orchestration platform
- **Istio**: Service mesh for microservices
- **Flask**: Python web framework (order-api, inventory-service)
- **Node.js/Express**: JavaScript runtime and web framework (user-service)
- **PostgreSQL**: Relational database
- **Docker**: Containerization platform
- **Minikube**: Local Kubernetes development environment
