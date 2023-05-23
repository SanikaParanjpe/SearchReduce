kubectl apply -f client-cluster-ip-service.yml
kubectl apply -f client-deployment.yml
kubectl apply -f server-cluster-ip-service.yml
kubectl apply -f server-deployment.yml
kubectl apply -f ingress-service.yml