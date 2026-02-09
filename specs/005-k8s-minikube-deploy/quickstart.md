# Quickstart: Deploy Todo Chatbot to Minikube

**Feature**: 005-k8s-minikube-deploy
**Date**: 2026-02-08

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Docker | 20.10+ | `docker version` |
| Minikube | 1.30+ | `minikube version` |
| kubectl | 1.28+ | `kubectl version --client` |
| Helm | 3.12+ | `helm version` |

## Step 1: Start Minikube

Start a Minikube cluster with sufficient resources for both services:

```bash
minikube start --cpus=2 --memory=4096 --driver=docker
```

Verify the cluster is running:

```bash
minikube status
kubectl config current-context  # Should output: minikube
```

## Step 2: Build Docker Images

Point the Docker CLI to Minikube's Docker daemon, then build both images:

```bash
eval $(minikube docker-env)

docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
```

Verify images are available:

```bash
docker images | grep todo-
```

## Step 3: Deploy with Helm

Lint the chart, then install with your secrets:

```bash
helm lint helm/todo-chatbot

helm install my-todo helm/todo-chatbot \
  --set backend.secrets.databaseUrl="YOUR_DATABASE_URL" \
  --set backend.secrets.betterAuthSecret="YOUR_AUTH_SECRET" \
  --set backend.secrets.openaiApiKey="YOUR_OPENAI_KEY" \
  --wait \
  --timeout 5m0s
```

## Step 4: Validate Deployment

Check that all pods are running and ready:

```bash
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot
kubectl wait --for=condition=Ready pod \
  -l app.kubernetes.io/part-of=todo-chatbot --timeout=120s
```

Run Helm's built-in connectivity test:

```bash
helm test my-todo
```

## Step 5: Access Services

Get the URLs for both services:

```bash
minikube service todo-frontend --url
minikube service todo-backend --url
```

Open the frontend URL in your browser. Open the backend URL with `/docs` appended to see the API documentation.

## Quick Validation Checklist

- [ ] `minikube status` shows Running
- [ ] Both Docker images built without errors
- [ ] `helm lint` passes
- [ ] `helm install` completes without timeout
- [ ] All pods show `Running` with `Ready 1/1`
- [ ] Zero restarts on all pods
- [ ] Frontend loads in browser
- [ ] Backend `/docs` loads in browser
- [ ] `helm test` passes

## Cleanup

```bash
helm uninstall my-todo
minikube stop
```

## Troubleshooting

**Pods stuck in ImagePullBackOff**: You forgot to run `eval $(minikube docker-env)` before building images. Rebuild inside Minikube's Docker daemon.

**Pods stuck in CrashLoopBackOff**: Check pod logs with `kubectl logs <pod-name> --previous`. Common causes: missing secrets, database unreachable.

**Service not accessible**: Verify endpoints with `kubectl get endpoints todo-frontend todo-backend`. If empty, check that Service selector labels match Deployment pod labels.
