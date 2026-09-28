# Kubernetes Workshop: Web1 + Web2 + MySQL

Architecture:

Web1 (Flask) ----\
                  > mysql-service (ClusterIP) --> MySQL Pod
Web2 (Flask) ----/

Web1 is exposed with NodePort 30081.
Web2 is exposed with NodePort 30082.

## 1. Build the application image

Replace `YOUR_DOCKERHUB_USERNAME` with your Docker Hub username.

```bash
cd app
docker build -t YOUR_DOCKERHUB_USERNAME/k8s-cloud-web:1.0 .
docker login
docker push YOUR_DOCKERHUB_USERNAME/k8s-cloud-web:1.0
cd ..
```

## 2. Update the Kubernetes manifest

Edit `k8s/web.yaml` and replace both occurrences of:

```text
YOUR_DOCKERHUB_USERNAME
```

with your Docker Hub username.

## 3. Deploy MySQL

```bash
kubectl apply -f k8s/mysql.yaml
kubectl get pods
kubectl get svc
```

Wait until the MySQL Pod is Ready:

```bash
kubectl wait --for=condition=ready pod -l app=mysql --timeout=180s
```

## 4. Deploy Web1 and Web2

```bash
kubectl apply -f k8s/web.yaml
kubectl get deployments
kubectl get pods
kubectl get svc
```

## 5. Test inside the cluster

```bash
kubectl run curl-test --rm -it --image=curlimages/curl -- sh
```

Inside the temporary Pod:

```bash
curl http://web1-service
curl http://web2-service
exit
```

Each request inserts a row into the same MySQL database.

## 6. Check the database

Find the MySQL Pod:

```bash
kubectl get pods -l app=mysql
```

Then run:

```bash
kubectl exec -it deployment/mysql -- mysql -uroot -pcloud123 appdb
```

In MySQL:

```sql
SELECT * FROM visitors;
exit
```

You should see rows created by both Web1 and Web2.

## 7. Test NodePort

Get the node information:

```bash
kubectl get nodes -o wide
kubectl get svc
```

The services use:

- Web1: NodePort 30081
- Web2: NodePort 30082

How the browser URL is exposed depends on the Killercoda Kubernetes scenario. If direct NodePort access is not exposed by the scenario, use the internal curl test above.

## 8. Demonstrate scaling

```bash
kubectl scale deployment web1 --replicas=3
kubectl get pods -l app=web1
```

All Web1 replicas still connect to the same `mysql-service`.

## 9. Demonstrate self-healing

```bash
kubectl get pods -l app=web1
kubectl delete pod <WEB1_POD_NAME>
kubectl get pods -l app=web1 -w
```

Kubernetes creates a replacement Pod to maintain the desired replica count.

## 10. Cleanup

```bash
kubectl delete -f k8s/web.yaml
kubectl delete -f k8s/mysql.yaml
```

## Key cloud concepts

- One container image can be reused for Web1 and Web2.
- Environment variables configure each workload.
- Applications use the Kubernetes Service name `mysql-service`, not a MySQL Pod IP.
- ClusterIP provides stable internal access to the database.
- NodePort exposes the two web services for workshop testing.
- Deployment manages replicas and self-healing.

Note: The password is intentionally simple and included in the workshop files for classroom use only.
