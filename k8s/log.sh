#!/bin/bash

kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
    - name: python-container
      image: python:bullseye
      command: ["python3", "-m", "http.server", "8080"]
EOF

(eval $(minikube docker-env) && docker build --target backend -t habr-app-demo/backend:latest backend)
(eval $(minikube docker-env) && docker build --target worker -t habr-app-demo/worker:latest backend)
(eval $(minikube docker-env) && docker build -t habr-app-demo/frontend:latest frontend)

kubectl apply -f k8s/backend-deployment.yaml

kubectl apply -f k8s/mongodb-statefulset.yaml
kubectl apply -f k8s/mongodb-service.yaml
kubectl patch deployment backend-deployment --patch-file k8s/backend-deployment-patch.yaml

(echo -n $(openssl rand -hex 14) > password.txt &&
 kubectl create secret generic mongodb-secret --from-file password.txt &&
 rm password.txt)

kubectl delete statefulset mongodb-statefulset
kubectl delete pvc mongodb-pvc-mongodb-statefulset-0

kubectl apply -f k8s/mongodb-statefulset-v2.yaml
kubectl patch deployment backend-deployment --patch-file k8s/backend-deployment-patch-2.yaml

kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/worker-deployment.yaml
kubectl apply -f k8s/redis.yaml

kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f "k8s/*-ingress.yaml"

kubectl exec deploy/backend-deployment -- python -m tools.add_test_content
