# SearchReduce

Search Reduce allows users to upload documents to the S3 Bucket service provided by Amazon. The main intention of the application is to provide users with a quick and relevant search using a Machine Learning model. The application allows users to upload pdf, text, and word documents to S3.
The application uses the services like Docker and Kubernetes for creating and autoscaling the nodes in order to provide a reliable service. The application uses Redis caching mechanism to fetch the records faster. It also uses MongoDB for database operations, Flask platform for backend operations, and React for frontend operations.

**About Deployment:**

Multi container deployment: kubernetes | React| Flask | Mongo | Ingress Nginx | Redis
It contains React client, flask backend, Redis Cache, Mongo database and Nginx ingress

You should install Ingress Nginx with command:
minikube addons enable ingress

After that you can use the following command to start in main folder:
kubectl apply -f k8s
