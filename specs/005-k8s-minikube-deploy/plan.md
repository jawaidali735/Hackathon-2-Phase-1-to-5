# Implementation Plan: Local Kubernetes Deployment with AI-Assisted DevOps

**Branch**: `005-k8s-minikube-deploy` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-k8s-minikube-deploy/spec.md`

## Summary

Deploy the Todo Chatbot application (Next.js frontend + FastAPI backend) to a local Minikube Kubernetes cluster using Docker container images and a Helm chart. All infrastructure artifacts (Dockerfiles, manifests, Helm templates) are generated with AI assistance and documented with prompt history records. The Helm chart packages both services as a single installable unit with configurable values, health probes, and secret management.

## Technical Context

**Language/Version**: Dockerfile (multi-stage), YAML (Kubernetes/Helm), Go templates (Helm)
**Primary Dependencies**: Docker 20.10+, Minikube 1.30+, Helm 3.12+, kubectl 1.28+
**Storage**: External Neon PostgreSQL (accessed from cluster, not deployed in-cluster)
**Testing**: `helm lint`, `kubectl --dry-run=client`, `helm test`, smoke tests via curl
**Target Platform**: Minikube (single-node local Kubernetes cluster, Docker driver)
**Project Type**: Web application (frontend + backend, infrastructure-as-code)
**Performance Goals**: Images < 500MB each; pods Ready within 2 minutes; reviewer deploys in < 10 minutes
**Constraints**: Minikube-only (no cloud features); modest resources (128Mi-512Mi memory, 100m-500m CPU per container)
**Scale/Scope**: 2 services, 1 Helm chart, 6 edge cases, 20 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| Spec-Driven Development | PASS | Spec at `specs/005-k8s-minikube-deploy/spec.md` approved before planning |
| AI-Native Architecture | PASS | All artifacts generated via Claude Code / Docker AI with PHR documentation |
| Cloud-Native First (Phase 4) | PASS | Docker images + Kubernetes + Helm charts as canonical deployment |
| Declarative over Imperative | PASS | All manifests in version-controlled YAML; Helm is canonical mechanism |
| Minikube as Canonical Environment | PASS | Minikube is the sole target; no cloud-provider features |
| Helm Packaging Standards | PASS | Single chart, values.yaml with comments, configurable parameters |
| Security & Config Management | PASS | Secrets in Kubernetes Secrets with CHANGE_ME placeholders; non-root containers |
| AI Observability & Ops Insights | PASS | AI-generated diagnostics prompts documented in skills |
| Test-Driven Deployment Validation | PASS | Health probes, helm test, validation checklist defined |
| Documentation as Code | PASS | Prompt history, constitution, spec, plan all in version control |
| No Hardcoded Secrets | PASS | Secrets via --set flags at install; placeholders in values.yaml |
| Multi-stage Docker Builds | PASS | Frontend: 3-stage (deps → builder → runner); Backend: 2-stage (builder → runner) |

**Gate Result**: ALL PASS — proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/005-k8s-minikube-deploy/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (infrastructure entities)
├── quickstart.md        # Phase 1 output (deployment quickstart)
├── contracts/           # Phase 1 output (Helm values contract)
│   └── helm-values-contract.md
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── Dockerfile              # Multi-stage Next.js build (NEW)
├── .dockerignore           # Exclude node_modules, .next, .env (NEW)
├── next.config.ts          # Must add output: "standalone" (MODIFY)
├── package.json
├── package-lock.json
└── src/                    # Existing application source

backend/
├── Dockerfile              # Multi-stage FastAPI/uv build (REPLACE existing)
├── .dockerignore           # Exclude .venv, __pycache__, .env (NEW)
├── pyproject.toml
├── uv.lock
└── app/                    # Existing application source

helm/todo-chatbot/
├── Chart.yaml              # Chart metadata (NEW)
├── values.yaml             # Configurable defaults (NEW)
├── .helmignore             # Packaging exclusions (NEW)
├── templates/
│   ├── _helpers.tpl        # Shared label/selector helpers (NEW)
│   ├── NOTES.txt           # Post-install instructions (NEW)
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── secret.yaml
│   └── tests/
│       └── test-connection.yaml
└── charts/                 # Subcharts (empty)

k8s/                        # Raw manifests for reference/fallback (NEW)
├── frontend-deployment.yaml
├── frontend-service.yaml
├── backend-deployment.yaml
├── backend-service.yaml
├── backend-configmap.yaml
└── backend-secret.yaml
```

**Structure Decision**: Infrastructure-as-code additions to the existing web application layout. `helm/todo-chatbot/` is the canonical deployment package. `k8s/` provides raw manifests for reference and `kubectl apply` fallback. Existing `frontend/` and `backend/` directories gain Dockerfiles and .dockerignore files. The existing `backend/Dockerfile` will be replaced with a constitution-compliant multi-stage build using uv.

## Phase 0: Research

### R1: Next.js Standalone Output for Docker

**Decision**: Use `output: "standalone"` in `next.config.ts` for the frontend Docker image.

**Rationale**: Next.js standalone output produces a self-contained `server.js` that includes only the files needed for production. This eliminates the need to copy `node_modules` into the final image, reducing image size from ~1GB to ~150-200MB.

**Alternatives considered**:
- Standard `next start` with full `node_modules`: Rejected — image size 3-5x larger, includes dev dependencies.
- Nginx static export: Rejected — loses SSR and API routes; Todo Chatbot frontend uses server-side features.

### R2: Backend Dependency Management in Docker

**Decision**: Use `uv` for dependency installation inside the Docker builder stage, copying the `.venv` to the runtime stage.

**Rationale**: The project already uses `uv` with `pyproject.toml` and `uv.lock`. Using `uv sync --frozen --no-dev` in the builder installs only production dependencies deterministically. The virtual environment is then copied wholesale to the runtime stage.

**Alternatives considered**:
- `pip install -r requirements.txt`: Rejected — the project's canonical package manager is uv per constitution; `requirements.txt` exists but may drift from `pyproject.toml`.
- Multi-stage with pip and `pyproject.toml`: Rejected — no lockfile pinning, slower resolution, less deterministic than uv.

### R3: Minikube Image Strategy

**Decision**: Build images inside Minikube's Docker daemon using `eval $(minikube docker-env)` with `imagePullPolicy: Never`.

**Rationale**: This avoids the need for a container registry. Images built inside Minikube's Docker daemon are directly available to the kubelet. Setting `imagePullPolicy: Never` prevents Kubernetes from attempting to pull from a remote registry.

**Alternatives considered**:
- Push to Docker Hub: Rejected — adds external dependency, requires authentication, slower iteration loop.
- `minikube image load`: Viable alternative but requires copying the full image each time; `docker-env` avoids the copy step entirely.

### R4: Helm Chart Structure

**Decision**: Single Helm chart at `helm/todo-chatbot/` packaging both frontend and backend as independently toggleable components.

**Rationale**: A single chart simplifies the install command (`helm install my-todo helm/todo-chatbot`). Both components share common labels and can be enabled/disabled via `frontend.enabled` and `backend.enabled` flags in values.yaml.

**Alternatives considered**:
- Separate charts per service: Rejected — adds install complexity for a 2-service application; overkill for Minikube.
- Umbrella chart with subcharts: Rejected — unnecessary indirection for this scale.

### R5: Service Exposure on Minikube

**Decision**: Use `NodePort` services for both frontend and backend, accessed via `minikube service <name> --url`.

**Rationale**: NodePort is the standard mechanism for external access on Minikube without requiring `minikube tunnel`. It provides stable, predictable URLs for browser and API access.

**Alternatives considered**:
- LoadBalancer + `minikube tunnel`: Viable but requires a separate terminal running the tunnel process continuously.
- ClusterIP + port-forward: Rejected as default — less convenient for browser access; suitable as optional override.
- Ingress: Over-engineered for local development with only 2 services.

### R6: Frontend-to-Backend Communication in Cluster

**Decision**: Frontend ConfigMap sets `API_BASE_URL` to `http://todo-backend:8000` (internal Kubernetes service DNS).

**Rationale**: Within the cluster, services resolve via DNS names. The frontend's server-side rendering and API proxy can reach the backend through the Kubernetes service without external routing.

**Alternatives considered**:
- External URL via NodePort: Rejected — breaks when service ports change; adds unnecessary external hop.
- Environment variable at build time: Rejected — prevents runtime configurability.

### R7: Health Check Endpoints

**Decision**: Frontend liveness/readiness on `GET /` (port 3000). Backend liveness/readiness on `GET /docs` (port 8000).

**Rationale**: Both endpoints are lightweight, always available when the application is healthy, and don't require authentication. `/docs` is FastAPI's built-in Swagger UI endpoint.

**Alternatives considered**:
- Custom `/healthz` endpoint: Would require code changes; unnecessary since existing endpoints serve the purpose.
- TCP socket checks: Less informative than HTTP checks; can't distinguish between "process running" and "application ready."

## Phase 1: Design

### Infrastructure Entities

See [data-model.md](./data-model.md) for the complete infrastructure entity model.

### Helm Values Contract

See [contracts/helm-values-contract.md](./contracts/helm-values-contract.md) for the complete Helm values interface specification.

### Quickstart Guide

See [quickstart.md](./quickstart.md) for the deployment quickstart steps.

### Key Design Decisions

1. **Frontend Dockerfile** — 3-stage build: `deps` (npm ci) → `builder` (next build) → `runner` (node:22-alpine, standalone server.js, non-root nextjs user). Requires adding `output: "standalone"` to `next.config.ts`.

2. **Backend Dockerfile** — 2-stage build: `builder` (python:3.11-slim + uv, sync dependencies) → `runner` (python:3.11-slim, copy .venv, non-root appuser). Replaces the existing single-stage pip-based Dockerfile.

3. **Helm _helpers.tpl** — Defines 7 named templates: `todo-chatbot.name`, `todo-chatbot.fullname`, `todo-chatbot.chart`, `todo-chatbot.labels`, `todo-chatbot.frontend.labels`, `todo-chatbot.frontend.selectorLabels`, `todo-chatbot.backend.labels`, `todo-chatbot.backend.selectorLabels`. All resources use these helpers for consistent labeling.

4. **Secret Management** — `values.yaml` contains `CHANGE_ME` placeholders for `databaseUrl`, `betterAuthSecret`, `openaiApiKey`. Real values passed at install via `--set` flags. The Secret YAML uses `stringData` for readability.

5. **Connectivity Test** — `templates/tests/test-connection.yaml` runs a `busybox` pod with `wget --spider` against both services' ports. Executed via `helm test`.

### Post-Design Constitution Re-check

| Principle | Status |
|-----------|--------|
| Cloud-Native First | PASS — Docker images + K8s + Helm |
| Declarative over Imperative | PASS — all manifests in YAML, version-controlled |
| Minikube as Canonical | PASS — NodePort services, imagePullPolicy: Never |
| Helm Packaging Standards | PASS — single chart, documented values.yaml |
| Security & Config Management | PASS — non-root, Secrets with placeholders |
| Test-Driven Deployment Validation | PASS — probes + helm test + smoke tests |
| AI-Assisted Infrastructure | PASS — all artifacts via Claude Code with PHR |
| Documentation as Code | PASS — quickstart, contracts, research all in spec dir |

**Post-Design Gate**: ALL PASS.

## Complexity Tracking

No violations to justify. The design follows all constitution principles without exceptions.
