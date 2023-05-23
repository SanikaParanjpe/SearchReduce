# Multicontainer application

Multi container deployment kubernetes | React| Flask | Mongo | Ingress Nginx | Redis


It contains React client, flask backend, Redis Cache, Mongo database and Nginx ingress

You should install Ingress Nginx with command:
minikube addons enable ingress

After that you can use the following command to start in main folder:
kubectl apply -f k8s
