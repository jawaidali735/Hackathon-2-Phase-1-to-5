---
name: todo-minikube
description: "Use this skill when deploying the Todo Chatbot to Minikube, validating pod health, accessing services, or troubleshooting a local Kubernetes deployment. Trigger terms: Minikube deploy, Minikube start, service access, pod status, helm install to Minikube, kubectl get pods, deployment validation."
---

# Todo Minikube Deployment Skill

This skill provides a complete, ordered workflow for deploying the Todo Chatbot application to a Minikube cluster, validating that all resources are healthy, and accessing the running services.

## Purpose

Execute a reliable local deployment that:
1. Starts and configures a Minikube cluster
2. Builds Docker images inside the Minikube Docker daemon
3. Installs the Helm chart (or applies raw manifests) into the cluster
4. Validates all pods reach Ready state with passing health probes
5. Provides service access URLs for the frontend and backend
6. Diagnoses and remediates common deployment failures
7. Aligns with the constitution's Phase 4 Test-Driven Deployment Validation principle

## When to Use

Use this skill when:
- Starting a Minikube cluster for the first time
- Deploying the Todo Chatbot Helm chart to Minikube
- Upgrading an existing deployment after code or config changes
- Checking pod health, service endpoints, or logs
- Accessing the frontend or backend via Minikube service URLs
- Troubleshooting CrashLoopBackOff, ImagePullBackOff, or Pending pods
- Rolling back a failed Helm release

**Trigger terms**: Minikube deploy, Minikube start, service access, pod status, helm install, kubectl get pods, deployment validation, pod logs, rollback, minikube service

## Prerequisites

| Tool | Minimum Version | Check Command |
|------|----------------|---------------|
| Minikube | 1.30+ | `minikube version` |
| kubectl | 1.28+ | `kubectl version --client` |
| Helm | 3.12+ | `helm version` |
| Docker | 20.10+ | `docker version` |

### Project Artifacts Required

- Docker images buildable via the `todo-docker` skill
- Helm chart at `helm/todo-chatbot/` scaffolded via the `todo-helm` skill
- OR raw manifests at `k8s/` generated via the `todo-kubernetes` skill

## Complete Deployment Workflow

### Phase 1: Pre-Flight Checks

Run these checks before every deployment. Do not skip any step.

```bash
# 1a. Check Minikube status
minikube status

# If not running, start it:
minikube start --cpus=2 --memory=4096 --driver=docker

# 1b. Verify kubectl context points to Minikube
kubectl config current-context
# Expected output: minikube

# If wrong context:
kubectl config use-context minikube

# 1c. Verify Helm is installed
helm version

# 1d. Check for existing releases that might conflict
helm list --all-namespaces
```

**Decision point**: If a release named `my-todo` already exists, use `helm upgrade` (Step 3b) instead of a fresh install.

### Phase 2: Build Docker Images

Images MUST be built inside Minikube's Docker daemon so they are available to the cluster without a registry push.

```bash
# 2a. Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# 2b. Verify the Docker daemon switched
docker info | grep -i name
# Expected: should mention minikube

# 2c. Build frontend image
docker build -t todo-frontend:latest ./frontend

# 2d. Build backend image
docker build -t todo-backend:latest ./backend

# 2e. Verify images are available
docker images | grep todo-
# Expected: todo-frontend and todo-backend with "latest" tag
```

**Important**: If you skip `eval $(minikube docker-env)`, images will be built in your host Docker and Kubernetes will fail with `ImagePullBackOff` because `imagePullPolicy: Never` is set.

### Phase 3: Deploy with Helm

#### 3a. Fresh Install

```bash
# Lint the chart first
helm lint helm/todo-chatbot

# Install with secrets passed via --set (never hardcode in values.yaml)
helm install my-todo helm/todo-chatbot \
  --set backend.secrets.databaseUrl="postgresql://user:pass@host/db" \
  --set backend.secrets.betterAuthSecret="your-jwt-secret" \
  --set backend.secrets.openaiApiKey="sk-your-key" \
  --wait \
  --timeout 5m0s
```

#### 3b. Upgrade Existing Release

```bash
helm upgrade my-todo helm/todo-chatbot \
  --set backend.secrets.databaseUrl="postgresql://user:pass@host/db" \
  --set backend.secrets.betterAuthSecret="your-jwt-secret" \
  --set backend.secrets.openaiApiKey="sk-your-key" \
  --wait \
  --timeout 5m0s
```

#### 3c. Alternative: Deploy Raw Manifests (without Helm)

If Helm is not yet set up, deploy using raw manifests:

```bash
kubectl apply -f k8s/backend-configmap.yaml
kubectl apply -f k8s/backend-secret.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
```

### Phase 4: Validation Checks

Run ALL of these checks after every deployment. Every check MUST pass.

```bash
# 4a. Helm release status (skip if using raw manifests)
helm status my-todo
# Expected: STATUS: deployed

# 4b. Pod health — all pods Running with all containers Ready
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot -o wide
# Expected: STATUS=Running, READY=1/1 for each pod

# 4c. Wait for readiness with timeout
kubectl wait --for=condition=Ready pod \
  -l app.kubernetes.io/part-of=todo-chatbot \
  --timeout=120s
# Expected: pod/todo-frontend-xxx condition met
#           pod/todo-backend-xxx condition met

# 4d. Check restart counts (restarts > 0 = warning)
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot \
  -o custom-columns=NAME:.metadata.name,RESTARTS:.status.containerStatuses[0].restartCount
# Expected: RESTARTS=0 for all pods

# 4e. Verify services exist with correct types
kubectl get svc -l app.kubernetes.io/part-of=todo-chatbot
# Expected: todo-frontend NodePort, todo-backend NodePort

# 4f. Verify endpoints are populated (not empty)
kubectl get endpoints todo-frontend todo-backend
# Expected: ENDPOINTS column shows IP:PORT, not <none>

# 4g. Check for warning events
kubectl get events --sort-by='.lastTimestamp' --field-selector type=Warning | tail -10
# Expected: no recent warnings related to todo-chatbot pods

# 4h. Run Helm tests (if using Helm)
helm test my-todo
# Expected: Phase: Succeeded
```

### Phase 5: Access Services

```bash
# 5a. Get frontend URL
minikube service todo-frontend --url
# Example output: http://192.168.49.2:30080

# 5b. Get backend URL
minikube service todo-backend --url
# Example output: http://192.168.49.2:30081

# 5c. Smoke test frontend
curl -sf $(minikube service todo-frontend --url) > /dev/null && echo "Frontend OK" || echo "Frontend FAIL"

# 5d. Smoke test backend
curl -sf $(minikube service todo-backend --url)/docs > /dev/null && echo "Backend OK" || echo "Backend FAIL"
```

**Alternative access**: If NodePort is not used, port-forward instead:

```bash
kubectl port-forward svc/todo-frontend 3000:3000 &
kubectl port-forward svc/todo-backend 8000:8000 &
# Access at http://localhost:3000 and http://localhost:8000
```

## Deployment Report Template

After completing validation, produce this report:

```
## Deployment Report
- **Release**: my-todo
- **Namespace**: default
- **Chart**: todo-chatbot v0.1.0
- **Status**: Deployed / Failed

### Pod Status
| Pod | Status | Ready | Restarts | Node |
|-----|--------|-------|----------|------|
| todo-frontend-xxx | Running | 1/1 | 0 | minikube |
| todo-backend-xxx  | Running | 1/1 | 0 | minikube |

### Services
| Service | Type | Port | External URL |
|---------|------|------|-------------|
| todo-frontend | NodePort | 3000 | http://192.168.49.2:30080 |
| todo-backend  | NodePort | 8000 | http://192.168.49.2:30081 |

### Health Checks
- [ ] All pods Running with Ready=1/1
- [ ] Zero restarts across all pods
- [ ] Endpoints populated for all services
- [ ] No Warning events in the last 5 minutes
- [ ] Frontend responds with 200 OK
- [ ] Backend /docs responds with 200 OK
- [ ] Helm test passed (if applicable)

### Issues Found
- (none, or list each issue with remediation)

### Access Instructions
- Frontend: <URL>
- Backend API docs: <URL>/docs
```

## Troubleshooting Guide

### ImagePullBackOff

**Symptom**: Pod stuck in `ImagePullBackOff` or `ErrImageNeverPull`.

**Cause**: Image was built on the host Docker, not inside Minikube's Docker daemon.

**Fix**:
```bash
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
kubectl delete pod -l app.kubernetes.io/part-of=todo-chatbot
# Pods will be recreated by the Deployment controller
```

### CrashLoopBackOff

**Symptom**: Pod repeatedly crashes and restarts.

**Diagnose**:
```bash
# Get logs from the crashed container
kubectl logs <pod-name> --previous

# Get detailed pod state
kubectl describe pod <pod-name>
```

**Common causes**:
- Missing environment variables (DATABASE_URL, BETTER_AUTH_SECRET)
- Database unreachable from inside the cluster (Neon firewall, connection string)
- Application error during startup

**Fix**: Correct the environment/config, then redeploy:
```bash
helm upgrade my-todo helm/todo-chatbot --set backend.secrets.databaseUrl="corrected-url" --wait
```

### Pending Pods

**Symptom**: Pod stuck in `Pending` state.

**Diagnose**:
```bash
kubectl describe pod <pod-name>
# Look at Events section for scheduling failures
kubectl top nodes
# Check if Minikube has enough resources
```

**Common causes**:
- Insufficient CPU/memory on the Minikube node
- Resource requests exceed available capacity

**Fix**: Either reduce resource requests in `values.yaml` or increase Minikube resources:
```bash
minikube stop
minikube start --cpus=4 --memory=8192
```

### Service Not Accessible

**Symptom**: `minikube service` returns an error or connection refused.

**Diagnose**:
```bash
# Verify endpoints are populated
kubectl get endpoints todo-frontend todo-backend

# Verify selector labels match
kubectl get pods --show-labels
kubectl get svc todo-frontend -o yaml | grep -A5 selector
```

**Common causes**:
- Service selector labels don't match pod labels
- Pod is not Ready (readiness probe failing)
- Wrong port mapping

**Fix**: Ensure Deployment pod template labels match Service selector labels exactly. Refer to the `todo-kubernetes` skill for correct label conventions.

### Helm Install Timeout

**Symptom**: `helm install` fails with `context deadline exceeded`.

**Diagnose**:
```bash
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot
kubectl describe pod <pending-or-crashing-pod>
kubectl logs <pod-name>
```

**Fix**: Resolve the underlying pod issue (image, config, resources), then retry:
```bash
helm uninstall my-todo
helm install my-todo helm/todo-chatbot --wait --timeout 5m0s
```

## Lifecycle Commands Reference

| Operation | Command |
|-----------|---------|
| Start cluster | `minikube start --cpus=2 --memory=4096 --driver=docker` |
| Stop cluster | `minikube stop` |
| Delete cluster | `minikube delete` |
| Switch Docker context | `eval $(minikube docker-env)` |
| Fresh install | `helm install my-todo helm/todo-chatbot --wait --timeout 5m0s` |
| Upgrade release | `helm upgrade my-todo helm/todo-chatbot --wait --timeout 5m0s` |
| Idempotent deploy | `helm upgrade --install my-todo helm/todo-chatbot --wait --timeout 5m0s` |
| Rollback | `helm rollback my-todo <revision>` |
| Uninstall | `helm uninstall my-todo` |
| View release history | `helm history my-todo` |
| Get service URL | `minikube service <name> --url` |
| Port forward | `kubectl port-forward svc/<name> <local>:<remote>` |
| Pod logs | `kubectl logs <pod-name>` |
| Pod logs (crashed) | `kubectl logs <pod-name> --previous` |
| Describe pod | `kubectl describe pod <pod-name>` |
| Restart pods | `kubectl rollout restart deployment/<name>` |
| Open dashboard | `minikube dashboard` |

## Key Rules

### Pre-Flight (NON-NEGOTIABLE)
- ALWAYS verify `minikube status` returns `Running` before any deployment.
- ALWAYS verify `kubectl config current-context` returns `minikube`.
- ALWAYS run `eval $(minikube docker-env)` before building images.

### Deployment
- ALWAYS use `--wait` with `helm install` and `helm upgrade` to get accurate status.
- ALWAYS use `--timeout 5m0s` to avoid indefinite hangs.
- ALWAYS pass secrets via `--set` flags, never rely on `CHANGE_ME` defaults in values.yaml.
- Prefer `helm upgrade --install` for idempotent operations.

### Validation
- ALWAYS run the full validation checklist (Phase 4) after every deployment.
- NEVER claim success if any pod is not in `Running` state with `Ready=1/1`.
- ALWAYS check restart counts; restarts > 0 indicate instability.
- ALWAYS verify endpoints are populated, not `<none>`.

### Troubleshooting
- ALWAYS read pod logs before suggesting fixes.
- NEVER delete resources without explicit user consent.
- ALWAYS suggest the least destructive fix first.

## Validation Checklist

Before reporting a deployment as successful, verify:

- [ ] Minikube cluster is Running
- [ ] kubectl context is set to minikube
- [ ] Docker images built inside Minikube Docker daemon
- [ ] `helm lint` passed (if using Helm)
- [ ] `helm install`/`upgrade` completed without errors
- [ ] Helm release status is `deployed`
- [ ] All pods in `Running` state with `Ready=1/1`
- [ ] Zero restarts across all pods
- [ ] Service endpoints populated (not `<none>`)
- [ ] No Warning events in cluster
- [ ] Frontend accessible via `minikube service` URL
- [ ] Backend `/docs` accessible via `minikube service` URL
- [ ] `helm test` passed (if using Helm)

## Dependencies

- Minikube 1.30+ with Docker driver
- Helm 3.12+ (for Helm-based deployments)
- Docker images built via the `todo-docker` skill
- Helm chart scaffolded via the `todo-helm` skill or raw manifests from the `todo-kubernetes` skill
