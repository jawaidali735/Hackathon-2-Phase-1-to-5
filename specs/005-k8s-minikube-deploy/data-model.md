# Infrastructure Entity Model: Local Kubernetes Deployment

**Feature**: 005-k8s-minikube-deploy
**Date**: 2026-02-08

## Overview

This feature does not introduce new application data models. Instead, it defines infrastructure entities — the resources and artifacts that make up the deployment pipeline. These entities are the "data model" of the infrastructure layer.

## Entities

### Container Image

A packaged, runnable snapshot of a service.

| Attribute | Type | Description |
|-----------|------|-------------|
| repository | string | Image name (e.g., `todo-frontend`, `todo-backend`) |
| tag | string | Version tag (e.g., `latest`, `1.0.0`) |
| baseImage | string | Base image for the runtime stage |
| exposedPort | integer | Port the application listens on |
| healthCheckPath | string | HTTP path for container HEALTHCHECK |
| user | string | Non-root user the container runs as |
| stages | list | Build stages (deps, builder, runner) |

**Instances**:
- `todo-frontend:latest` — Node.js 22 Alpine, port 3000, health `/`, user `nextjs`
- `todo-backend:latest` — Python 3.11 slim, port 8000, health `/docs`, user `appuser`

### Helm Chart

A versioned deployment package.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Chart name: `todo-chatbot` |
| version | semver | Chart version (independent of app version) |
| appVersion | string | Application version being deployed |
| type | string | Always `application` |
| valuesFile | file | `values.yaml` with all configurable parameters |
| templates | directory | Go template files for Kubernetes resources |
| helpers | file | `_helpers.tpl` shared template definitions |

### Deployment (per service)

A Kubernetes workload resource.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | `todo-frontend` or `todo-backend` |
| replicas | integer | Number of pod replicas (default: 1) |
| image | string | Container image reference |
| imagePullPolicy | string | `Never` for Minikube local images |
| containerPort | integer | Port the container exposes |
| resources.requests | object | Minimum CPU/memory (100m/128Mi) |
| resources.limits | object | Maximum CPU/memory (500m/512Mi) |
| livenessProbe | object | HTTP GET probe configuration |
| readinessProbe | object | HTTP GET probe configuration |
| strategy | object | RollingUpdate with maxSurge:1, maxUnavailable:0 |
| securityContext | object | runAsNonRoot, allowPrivilegeEscalation:false |

### Service (per service)

A Kubernetes networking resource.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | `todo-frontend` or `todo-backend` |
| type | string | `NodePort` (Minikube) or `ClusterIP` (production) |
| port | integer | Service port (matches container port) |
| targetPort | string | Named port reference (`http`) |
| nodePort | integer | Optional fixed NodePort (30000-32767) |
| selector | labels | Must match Deployment pod template labels |

### ConfigMap (per service)

Non-sensitive configuration.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | `todo-frontend-config` or `todo-backend-config` |
| data | map | Key-value configuration entries |

**Frontend ConfigMap data**:
- `API_BASE_URL`: Backend internal service URL

**Backend ConfigMap data**:
- `CORS_ORIGINS`: Allowed CORS origins
- `JWT_ALGORITHM`: JWT signing algorithm
- `JWT_EXPIRATION_DAYS`: Token expiration

### Secret

Sensitive configuration (backend only).

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | `todo-backend-secret` |
| type | string | `Opaque` |
| stringData | map | Key-value secrets (CHANGE_ME in version control) |

**Secret data**:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET`: JWT signing secret
- `OPENAI_API_KEY`: OpenAI API key for AI agent

## Relationships

```
Helm Chart (todo-chatbot)
├── contains → Frontend Deployment
│   ├── references → Container Image (todo-frontend)
│   ├── uses → Frontend ConfigMap
│   └── exposed by → Frontend Service (NodePort)
├── contains → Backend Deployment
│   ├── references → Container Image (todo-backend)
│   ├── uses → Backend ConfigMap
│   ├── uses → Backend Secret
│   └── exposed by → Backend Service (NodePort)
└── contains → Test Pod (connectivity test)
    └── tests → Frontend Service + Backend Service
```

## State Transitions

### Pod Lifecycle

```
Pending → ContainerCreating → Running (Ready) → Terminating → Terminated
                                  ↓
                         CrashLoopBackOff (on failure)
```

### Helm Release Lifecycle

```
(none) → deployed → superseded (on upgrade) → uninstalled
                ↓
          failed (on error)
```
