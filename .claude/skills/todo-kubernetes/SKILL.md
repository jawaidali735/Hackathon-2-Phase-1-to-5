---
name: todo-kubernetes
description: "Use this skill when generating Kubernetes Deployment, Service, ConfigMap, or Secret YAML manifests for the Todo Chatbot application targeting Minikube. Trigger words: Kubernetes, deployment YAML, service YAML, Minikube, k8s manifest, pod, kubectl apply."
---

# Todo Kubernetes Manifests Skill

This skill provides step-by-step guidance for generating Kubernetes Deployment and Service YAML manifests for the Todo Chatbot project's frontend (Next.js) and backend (FastAPI) services, targeting Minikube as the canonical local environment.

## Purpose

Generate declarative Kubernetes manifests that:
1. Deploy the Todo Chatbot frontend and backend as separate Deployments
2. Expose services via ClusterIP (internal) or NodePort (Minikube external access)
3. Include liveness and readiness probes for all containers
4. Follow the Kubernetes recommended labeling scheme
5. Set resource requests/limits appropriate for Minikube
6. Enforce security contexts (non-root, read-only filesystem)
7. Align with the project constitution's Phase 4 principles

## When to Use

Use this skill when:
- Creating Deployment manifests for the frontend or backend
- Creating Service manifests to expose pods in Minikube
- Generating ConfigMaps for non-sensitive configuration
- Generating Secret manifests for sensitive data (JWT keys, DB credentials)
- Setting up health probes, resource limits, or rolling update strategies
- Preparing Kubernetes resources before Helm chart packaging

**Trigger words**: Kubernetes, deployment YAML, service YAML, Minikube, k8s manifest, pod, kubectl apply, ConfigMap, Secret, liveness probe, readiness probe

## Project Context

### Services

| Service | Image | Port | Health Endpoint |
|---------|-------|------|-----------------|
| Frontend | `todo-frontend:latest` | 3000 | `GET /` |
| Backend | `todo-backend:latest` | 8000 | `GET /docs` |

### Output Directory

All manifests MUST be placed in `k8s/` at the project root:

```
k8s/
├── frontend-deployment.yaml
├── frontend-service.yaml
├── backend-deployment.yaml
├── backend-service.yaml
├── backend-configmap.yaml
├── backend-secret.yaml
└── namespace.yaml          # optional
```

### Labeling Convention

All resources MUST use the Kubernetes recommended labels:

```yaml
metadata:
  labels:
    app.kubernetes.io/name: <component>        # e.g., todo-frontend
    app.kubernetes.io/component: <role>         # e.g., frontend, api
    app.kubernetes.io/part-of: todo-chatbot
    app.kubernetes.io/managed-by: claude-code
```

Selectors in Deployments and Services MUST match on `app.kubernetes.io/name`.

## Step-by-Step: Frontend Deployment

### Step 1: Generate the Deployment

```yaml
# k8s/frontend-deployment.yaml
# Apply: kubectl apply -f k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  labels:
    app.kubernetes.io/name: todo-frontend
    app.kubernetes.io/component: frontend
    app.kubernetes.io/part-of: todo-chatbot
    app.kubernetes.io/managed-by: claude-code
spec:
  replicas: 1
  revisionHistoryLimit: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app.kubernetes.io/name: todo-frontend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: todo-frontend
        app.kubernetes.io/component: frontend
        app.kubernetes.io/part-of: todo-chatbot
    spec:
      securityContext:
        runAsNonRoot: true
        fsGroup: 1001
      containers:
        - name: frontend
          image: todo-frontend:latest
          imagePullPolicy: Never  # Use Minikube local images
          ports:
            - name: http
              containerPort: 3000
              protocol: TCP
          env:
            - name: NEXT_PUBLIC_API_BASE_URL
              valueFrom:
                configMapKeyRef:
                  name: todo-frontend-config
                  key: API_BASE_URL
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 15
            periodSeconds: 20
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          securityContext:
            allowPrivilegeEscalation: false
            runAsUser: 1001
            runAsGroup: 1001
```

### Step 2: Generate the Service

```yaml
# k8s/frontend-service.yaml
# Apply: kubectl apply -f k8s/frontend-service.yaml
# Access: minikube service todo-frontend --url
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
  labels:
    app.kubernetes.io/name: todo-frontend
    app.kubernetes.io/component: frontend
    app.kubernetes.io/part-of: todo-chatbot
    app.kubernetes.io/managed-by: claude-code
spec:
  type: NodePort  # NodePort for Minikube external access
  selector:
    app.kubernetes.io/name: todo-frontend
  ports:
    - name: http
      port: 3000
      targetPort: http
      protocol: TCP
      # nodePort: 30080  # Uncomment to pin a specific port
```

## Step-by-Step: Backend Deployment

### Step 1: Generate ConfigMap (non-sensitive config)

```yaml
# k8s/backend-configmap.yaml
# Apply: kubectl apply -f k8s/backend-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-backend-config
  labels:
    app.kubernetes.io/name: todo-backend
    app.kubernetes.io/component: api
    app.kubernetes.io/part-of: todo-chatbot
    app.kubernetes.io/managed-by: claude-code
data:
  CORS_ORIGINS: "http://localhost:3000"
  JWT_ALGORITHM: "HS256"
  JWT_EXPIRATION_DAYS: "7"
```

### Step 2: Generate Secret (sensitive config)

```yaml
# k8s/backend-secret.yaml
# Apply: kubectl apply -f k8s/backend-secret.yaml
# IMPORTANT: Replace placeholder values before applying.
# Do NOT commit real secrets to version control.
apiVersion: v1
kind: Secret
metadata:
  name: todo-backend-secret
  labels:
    app.kubernetes.io/name: todo-backend
    app.kubernetes.io/component: api
    app.kubernetes.io/part-of: todo-chatbot
    app.kubernetes.io/managed-by: claude-code
type: Opaque
stringData:
  DATABASE_URL: "CHANGE_ME"          # Neon PostgreSQL connection string
  BETTER_AUTH_SECRET: "CHANGE_ME"    # JWT signing secret
  OPENAI_API_KEY: "CHANGE_ME"       # OpenAI API key for agent
```

### Step 3: Generate the Deployment

```yaml
# k8s/backend-deployment.yaml
# Apply: kubectl apply -f k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app.kubernetes.io/name: todo-backend
    app.kubernetes.io/component: api
    app.kubernetes.io/part-of: todo-chatbot
    app.kubernetes.io/managed-by: claude-code
spec:
  replicas: 1
  revisionHistoryLimit: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app.kubernetes.io/name: todo-backend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: todo-backend
        app.kubernetes.io/component: api
        app.kubernetes.io/part-of: todo-chatbot
    spec:
      securityContext:
        runAsNonRoot: true
        fsGroup: 1001
      containers:
        - name: backend
          image: todo-backend:latest
          imagePullPolicy: Never  # Use Minikube local images
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
          envFrom:
            - configMapRef:
                name: todo-backend-config
            - secretRef:
                name: todo-backend-secret
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /docs
              port: http
            initialDelaySeconds: 20
            periodSeconds: 30
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /docs
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          securityContext:
            allowPrivilegeEscalation: false
            runAsUser: 1001
            runAsGroup: 1001
```

### Step 4: Generate the Service

```yaml
# k8s/backend-service.yaml
# Apply: kubectl apply -f k8s/backend-service.yaml
# Access: minikube service todo-backend --url
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
  labels:
    app.kubernetes.io/name: todo-backend
    app.kubernetes.io/component: api
    app.kubernetes.io/part-of: todo-chatbot
    app.kubernetes.io/managed-by: claude-code
spec:
  type: NodePort  # NodePort for Minikube external access
  selector:
    app.kubernetes.io/name: todo-backend
  ports:
    - name: http
      port: 8000
      targetPort: http
      protocol: TCP
      # nodePort: 30081  # Uncomment to pin a specific port
```

## Configuration Reference

### Resource Defaults for Minikube

| Resource | Requests | Limits | Notes |
|----------|----------|--------|-------|
| CPU | 100m | 500m | Increase limits for production |
| Memory | 128Mi | 512Mi | Backend may need more with AI agent |

### Probe Defaults

| Probe | Path | Initial Delay | Period | Timeout | Failure Threshold |
|-------|------|---------------|--------|---------|-------------------|
| Frontend liveness | `/` | 15s | 20s | 5s | 3 |
| Frontend readiness | `/` | 5s | 10s | 3s | 3 |
| Backend liveness | `/docs` | 20s | 30s | 5s | 3 |
| Backend readiness | `/docs` | 10s | 10s | 3s | 3 |

### Service Types

| Environment | Service Type | Access Method |
|-------------|--------------|---------------|
| Minikube | NodePort | `minikube service <name> --url` |
| Production | ClusterIP + Ingress | Ingress controller routes traffic |

## Key Rules

### Labels (NON-NEGOTIABLE)
- Every resource MUST have `app.kubernetes.io/name`, `app.kubernetes.io/component`, and `app.kubernetes.io/part-of` labels.
- Deployment `spec.selector.matchLabels` MUST match pod template labels exactly.
- Service `spec.selector` MUST match the Deployment's pod template labels.

### Ports
- Container ports MUST be named (e.g., `http`, `grpc`, `metrics`).
- Service `targetPort` MUST reference the port name, not the number, for maintainability.
- `containerPort` MUST match the actual port the application listens on (frontend: 3000, backend: 8000).

### Probes
- Every Deployment MUST have both `livenessProbe` and `readinessProbe`.
- Liveness probes MUST have a longer `initialDelaySeconds` than readiness probes to avoid restart loops during startup.
- Use `httpGet` probes for HTTP services; use `tcpSocket` only if no HTTP endpoint is available.

### Security
- `runAsNonRoot: true` MUST be set at the pod level.
- `allowPrivilegeEscalation: false` MUST be set on every container.
- Secrets MUST NOT contain real values in committed files; use `CHANGE_ME` placeholders.
- Use `envFrom` with ConfigMap/Secret refs instead of inline `env` entries for cleaner configuration.

### Minikube-Specific
- `imagePullPolicy: Never` MUST be set when using locally-built images with `eval $(minikube docker-env)`.
- NodePort services are preferred for external access during local development.
- Resource limits MUST be modest (128Mi-512Mi memory, 100m-500m CPU) to fit within Minikube's resource constraints.

## Deployment Workflow

Build images, apply manifests, and validate in order:

```bash
# 1. Point Docker to Minikube's daemon
eval $(minikube docker-env)

# 2. Build images locally
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# 3. Apply manifests in dependency order
kubectl apply -f k8s/backend-configmap.yaml
kubectl apply -f k8s/backend-secret.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 4. Validate pods are running
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/part-of=todo-chatbot --timeout=120s

# 5. Access services
minikube service todo-frontend --url
minikube service todo-backend --url
```

## Validation Checklist

Before finalizing any manifest for this project, verify:

- [ ] `apiVersion`, `kind`, `metadata`, `spec` ordering is consistent
- [ ] All three recommended labels present (`name`, `component`, `part-of`)
- [ ] Deployment selector matches pod template labels exactly
- [ ] Service selector matches Deployment pod template labels
- [ ] Container ports are named and match the application's listen port
- [ ] Service `targetPort` references port name, not number
- [ ] `resources.requests` and `resources.limits` set on all containers
- [ ] Both `livenessProbe` and `readinessProbe` configured
- [ ] Liveness `initialDelaySeconds` > readiness `initialDelaySeconds`
- [ ] `runAsNonRoot: true` set at pod security context
- [ ] `allowPrivilegeEscalation: false` set on containers
- [ ] `imagePullPolicy: Never` set for Minikube local images
- [ ] Secrets use `CHANGE_ME` placeholders (no real credentials)
- [ ] `envFrom` used for ConfigMap/Secret injection
- [ ] YAML passes `kubectl apply --dry-run=client` validation
- [ ] Manifests are saved under `k8s/` directory

## Dependencies

- Minikube 1.30+ with Kubernetes 1.28+
- kubectl CLI matching the cluster version
- Docker images built via the `todo-docker` skill
