## Deploying Prisma to Azure

## Prerequisites

1. Install Azure's AKS CLI
  
        az aks install-cli

2. Get credentials for the AKS cluster

        az aks get-credentials --resource-group <RESOURCE_GROUP> --name <AKS_CLUSTER_NAME>

3. Open the Kubernetes dashboard
   
        az aks browse --resource-group <RESOURCE_GROUP> --name <AKS_CLUSTER_NAME>

4. List deployed assets (Pods, deployments)
   
        kubectl get all

-----

## Kubernetes Deployment

1. Create a name space in Kubernetes

        kubectl create ns <NAMESPACE_FOR_YOUR_SERVICE>

2. Apply `docker-compose.yml` file to the namespace

        kubectl apply -n <NAMESPACE_FOR_YOUR_SERVICE> -f <PATH_TO_DOCKER_COMPOSE>


-----

## Expose your application

    kubectl expose deployment <DEPLOYMENT> --type=LoadBalancer --name=<NAME_FOR_EXPOSED_SERVICE> --namespace=<NAMESPACE_FOR_YOUR_SERVICE>`