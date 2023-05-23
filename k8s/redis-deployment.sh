kubectl apply -f redis-sc.yml
kubectl apply -f redis-pv.yml
kubectl apply -f redis-config.yml
kubectl apply -f redis-statefulset.yml
kubectl apply -f redis-service.yml