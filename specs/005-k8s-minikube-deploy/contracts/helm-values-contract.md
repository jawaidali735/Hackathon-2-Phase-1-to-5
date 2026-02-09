# Helm Values Contract: todo-chatbot

**Feature**: 005-k8s-minikube-deploy
**Date**: 2026-02-08

## Overview

This document defines the interface contract for `helm/todo-chatbot/values.yaml`. Every parameter listed here MUST exist in `values.yaml` with its documented default and a YAML comment.

## Frontend Parameters

| Path | Type | Default | Description | Overridable |
|------|------|---------|-------------|-------------|
| `frontend.enabled` | boolean | `true` | Enable/disable frontend component | Yes |
| `frontend.replicaCount` | integer | `1` | Number of frontend pod replicas | Yes |
| `frontend.image.repository` | string | `todo-frontend` | Image name | Yes |
| `frontend.image.tag` | string | `latest` | Image tag | Yes |
| `frontend.image.pullPolicy` | string | `Never` | Pull policy (Never for Minikube) | Yes |
| `frontend.service.type` | string | `NodePort` | Service type | Yes |
| `frontend.service.port` | integer | `3000` | Service port | Yes |
| `frontend.service.targetPort` | integer | `3000` | Container target port | Yes |
| `frontend.service.nodePort` | integer | (auto) | Fixed NodePort (optional) | Yes |
| `frontend.resources.requests.cpu` | string | `100m` | Min CPU | Yes |
| `frontend.resources.requests.memory` | string | `128Mi` | Min memory | Yes |
| `frontend.resources.limits.cpu` | string | `500m` | Max CPU | Yes |
| `frontend.resources.limits.memory` | string | `512Mi` | Max memory | Yes |
| `frontend.livenessProbe.path` | string | `/` | Liveness HTTP path | Yes |
| `frontend.livenessProbe.initialDelaySeconds` | integer | `15` | Delay before first check | Yes |
| `frontend.livenessProbe.periodSeconds` | integer | `20` | Check interval | Yes |
| `frontend.livenessProbe.timeoutSeconds` | integer | `5` | Check timeout | Yes |
| `frontend.livenessProbe.failureThreshold` | integer | `3` | Failures before restart | Yes |
| `frontend.readinessProbe.path` | string | `/` | Readiness HTTP path | Yes |
| `frontend.readinessProbe.initialDelaySeconds` | integer | `5` | Delay before first check | Yes |
| `frontend.readinessProbe.periodSeconds` | integer | `10` | Check interval | Yes |
| `frontend.readinessProbe.timeoutSeconds` | integer | `3` | Check timeout | Yes |
| `frontend.readinessProbe.failureThreshold` | integer | `3` | Failures before unready | Yes |
| `frontend.env.apiBaseUrl` | string | `http://todo-backend:8000` | Backend URL for SSR | Yes |

## Backend Parameters

| Path | Type | Default | Description | Overridable |
|------|------|---------|-------------|-------------|
| `backend.enabled` | boolean | `true` | Enable/disable backend component | Yes |
| `backend.replicaCount` | integer | `1` | Number of backend pod replicas | Yes |
| `backend.image.repository` | string | `todo-backend` | Image name | Yes |
| `backend.image.tag` | string | `latest` | Image tag | Yes |
| `backend.image.pullPolicy` | string | `Never` | Pull policy (Never for Minikube) | Yes |
| `backend.service.type` | string | `NodePort` | Service type | Yes |
| `backend.service.port` | integer | `8000` | Service port | Yes |
| `backend.service.targetPort` | integer | `8000` | Container target port | Yes |
| `backend.service.nodePort` | integer | (auto) | Fixed NodePort (optional) | Yes |
| `backend.resources.requests.cpu` | string | `100m` | Min CPU | Yes |
| `backend.resources.requests.memory` | string | `128Mi` | Min memory | Yes |
| `backend.resources.limits.cpu` | string | `500m` | Max CPU | Yes |
| `backend.resources.limits.memory` | string | `512Mi` | Max memory | Yes |
| `backend.livenessProbe.path` | string | `/docs` | Liveness HTTP path | Yes |
| `backend.livenessProbe.initialDelaySeconds` | integer | `20` | Delay before first check | Yes |
| `backend.livenessProbe.periodSeconds` | integer | `30` | Check interval | Yes |
| `backend.livenessProbe.timeoutSeconds` | integer | `5` | Check timeout | Yes |
| `backend.livenessProbe.failureThreshold` | integer | `3` | Failures before restart | Yes |
| `backend.readinessProbe.path` | string | `/docs` | Readiness HTTP path | Yes |
| `backend.readinessProbe.initialDelaySeconds` | integer | `10` | Delay before first check | Yes |
| `backend.readinessProbe.periodSeconds` | integer | `10` | Check interval | Yes |
| `backend.readinessProbe.timeoutSeconds` | integer | `3` | Check timeout | Yes |
| `backend.readinessProbe.failureThreshold` | integer | `3` | Failures before unready | Yes |
| `backend.config.corsOrigins` | string | `http://localhost:3000` | CORS origins | Yes |
| `backend.config.jwtAlgorithm` | string | `HS256` | JWT algorithm | Yes |
| `backend.config.jwtExpirationDays` | string | `7` | JWT expiration days | Yes |
| `backend.secrets.databaseUrl` | string | `CHANGE_ME` | PostgreSQL URL | Yes (required) |
| `backend.secrets.betterAuthSecret` | string | `CHANGE_ME` | JWT signing secret | Yes (required) |
| `backend.secrets.openaiApiKey` | string | `CHANGE_ME` | OpenAI API key | Yes (required) |

## Shared Parameters

| Path | Type | Default | Description | Overridable |
|------|------|---------|-------------|-------------|
| `podSecurityContext.runAsNonRoot` | boolean | `true` | Require non-root | Yes |
| `podSecurityContext.fsGroup` | integer | `1001` | Filesystem group | Yes |
| `containerSecurityContext.allowPrivilegeEscalation` | boolean | `false` | Block escalation | Yes |
| `containerSecurityContext.runAsUser` | integer | `1001` | Non-root UID | Yes |
| `containerSecurityContext.runAsGroup` | integer | `1001` | Non-root GID | Yes |

## Override Examples

```bash
# Change backend replicas to 2
helm install my-todo helm/todo-chatbot --set backend.replicaCount=2

# Use ClusterIP instead of NodePort
helm install my-todo helm/todo-chatbot --set frontend.service.type=ClusterIP

# Pass secrets at install
helm install my-todo helm/todo-chatbot \
  --set backend.secrets.databaseUrl="postgresql://..." \
  --set backend.secrets.betterAuthSecret="secret" \
  --set backend.secrets.openaiApiKey="sk-..."

# Use a custom image tag
helm install my-todo helm/todo-chatbot --set frontend.image.tag=v2.0.0

# Increase backend memory for AI agent workload
helm install my-todo helm/todo-chatbot \
  --set backend.resources.limits.memory=1Gi \
  --set backend.resources.requests.memory=256Mi
```

## Validation Rules

1. All `CHANGE_ME` secrets MUST be overridden before deployment to a working environment.
2. `service.type` must be one of: `ClusterIP`, `NodePort`, `LoadBalancer`.
3. `image.pullPolicy` must be one of: `Always`, `IfNotPresent`, `Never`.
4. Resource values must use Kubernetes notation (e.g., `100m` for CPU, `128Mi` for memory).
5. Probe paths must start with `/`.
6. `replicaCount` must be >= 1.
