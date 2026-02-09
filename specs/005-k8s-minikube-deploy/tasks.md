# Tasks: Local Kubernetes Deployment with AI-Assisted DevOps

**Input**: Design documents from `/specs/005-k8s-minikube-deploy/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/helm-values-contract.md, quickstart.md

**Tests**: Not explicitly requested in the feature specification. Test tasks are omitted. Validation is performed through `helm lint`, `helm test`, and manual smoke tests as defined in the quickstart.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/` (Next.js application)
- **Backend**: `backend/` (FastAPI application)
- **Helm chart**: `helm/todo-chatbot/` (canonical deployment package)
- **Raw manifests**: `k8s/` (reference/fallback)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Modify existing configuration and create ignore files required by all subsequent phases

- [x] T001 Add `output: "standalone"` to Next.js config in `frontend/next.config.ts`
- [x] T002 [P] Create frontend Docker ignore file at `frontend/.dockerignore`
- [x] T003 [P] Create backend Docker ignore file at `backend/.dockerignore`

---

## Phase 2: Foundational — Docker Images (Blocking Prerequisites)

**Purpose**: Build production-ready container images for both services. All Kubernetes and Helm work depends on working images.

**CRITICAL**: No user story work can begin until both images build successfully.

- [x] T004 [P] Create multi-stage frontend Dockerfile at `frontend/Dockerfile` (3-stage: deps with npm ci, builder with next build, runner with node:22-alpine standalone server.js, non-root nextjs user uid 1001, HEALTHCHECK on port 3000)
- [x] T005 [P] Replace existing backend Dockerfile at `backend/Dockerfile` with multi-stage build (2-stage: builder with python:3.11-slim + uv from ghcr.io/astral-sh/uv:latest, uv sync --frozen --no-dev, runner with python:3.11-slim copying .venv, non-root appuser uid 1001, HEALTHCHECK on port 8000)
- [ ] T006 Validate both Docker images build successfully and are each under 500MB (run `docker build -t todo-frontend:latest ./frontend` and `docker build -t todo-backend:latest ./backend`)

**Checkpoint**: Both container images build and pass size constraints. Foundational phase complete — user story implementation can begin.

---

## Phase 3: User Story 1 — Containerize and Deploy Services Locally (Priority: P1) MVP

**Goal**: Deploy the entire Todo Chatbot application (frontend + backend) to a local Minikube cluster using a Helm chart, with all pods reaching Ready state and services accessible from the browser.

**Independent Test**: Build both Docker images inside Minikube's Docker daemon, run `helm install my-todo helm/todo-chatbot --set backend.secrets.databaseUrl=... --set backend.secrets.betterAuthSecret=... --set backend.secrets.openaiApiKey=...`, confirm all pods reach Ready 1/1 within 2 minutes, open frontend URL in browser, access backend `/docs` endpoint.

### Helm Chart Scaffolding

- [x] T007 Create Helm chart metadata file at `helm/todo-chatbot/Chart.yaml` (apiVersion v2, name todo-chatbot, version 0.1.0, appVersion 1.0.0, type application, description)
- [x] T008 Create Helm ignore file at `helm/todo-chatbot/.helmignore`
- [x] T009 Create Helm shared template helpers at `helm/todo-chatbot/templates/_helpers.tpl` (named templates: todo-chatbot.name, todo-chatbot.fullname, todo-chatbot.chart, todo-chatbot.labels, todo-chatbot.frontend.labels, todo-chatbot.frontend.selectorLabels, todo-chatbot.backend.labels, todo-chatbot.backend.selectorLabels)
- [x] T010 [US1] Create Helm values file at `helm/todo-chatbot/values.yaml` with all parameters from contracts/helm-values-contract.md (frontend, backend, shared sections with YAML comments on every parameter, CHANGE_ME placeholders for secrets)

### Frontend Kubernetes Resources

- [x] T011 [P] [US1] Create frontend Deployment template at `helm/todo-chatbot/templates/frontend/deployment.yaml` (replicas from values, image with pullPolicy Never, container port 3000 named http, envFrom configmap, resources from values, liveness/readiness probes from values, security context from values, RollingUpdate strategy maxSurge:1 maxUnavailable:0, conditional on frontend.enabled)
- [x] T012 [P] [US1] Create frontend Service template at `helm/todo-chatbot/templates/frontend/service.yaml` (type NodePort from values, port/targetPort from values, selector matching deployment pod labels, conditional on frontend.enabled)
- [x] T013 [P] [US1] Create frontend ConfigMap template at `helm/todo-chatbot/templates/frontend/configmap.yaml` (API_BASE_URL from values frontend.env.apiBaseUrl, conditional on frontend.enabled)

### Backend Kubernetes Resources

- [x] T014 [P] [US1] Create backend Deployment template at `helm/todo-chatbot/templates/backend/deployment.yaml` (replicas from values, image with pullPolicy Never, container port 8000 named http, envFrom configmap + secret, resources from values, liveness/readiness probes from values, security context from values, RollingUpdate strategy maxSurge:1 maxUnavailable:0, conditional on backend.enabled)
- [x] T015 [P] [US1] Create backend Service template at `helm/todo-chatbot/templates/backend/service.yaml` (type NodePort from values, port/targetPort from values, selector matching deployment pod labels, conditional on backend.enabled)
- [x] T016 [P] [US1] Create backend ConfigMap template at `helm/todo-chatbot/templates/backend/configmap.yaml` (CORS_ORIGINS, JWT_ALGORITHM, JWT_EXPIRATION_DAYS from values backend.config, conditional on backend.enabled)
- [x] T017 [P] [US1] Create backend Secret template at `helm/todo-chatbot/templates/backend/secret.yaml` (type Opaque, stringData with DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY from values backend.secrets, conditional on backend.enabled)

### Helm Test and Notes

- [x] T018 [US1] Create Helm connectivity test at `helm/todo-chatbot/templates/tests/test-connection.yaml` (busybox pod with wget --spider against frontend service port 3000 and backend service port 8000, helm.sh/hook: test annotation)
- [x] T019 [US1] Create post-install notes template at `helm/todo-chatbot/templates/NOTES.txt` (display commands to get frontend and backend URLs via minikube service)

### Validation

- [ ] T020 [US1] Validate Helm chart with `helm lint helm/todo-chatbot` and `helm template my-todo helm/todo-chatbot` dry-run — fix any errors

**Checkpoint**: Helm chart lints cleanly and renders valid manifests. With a running Minikube cluster, `helm install` deploys both services, all pods reach Ready 1/1, frontend loads in browser, backend `/docs` loads. User Story 1 is complete.

---

## Phase 4: User Story 2 — Configurable Deployment via Helm Values (Priority: P2)

**Goal**: Ensure every deployment parameter is configurable via values.yaml without modifying templates. Demonstrate overrides for replica count, service type, resource limits, and secrets.

**Independent Test**: Install with `--set backend.replicaCount=2`, verify 2 backend pods run. Upgrade with `--set frontend.service.type=ClusterIP`, verify service type changes. Confirm all parameters in values.yaml have descriptive YAML comments.

### Implementation

- [x] T021 [US2] Audit `helm/todo-chatbot/values.yaml` against `contracts/helm-values-contract.md` — verify every parameter exists with correct default, type, and descriptive YAML comment; fix any missing or incorrect entries
- [x] T022 [US2] Verify all Helm templates correctly reference values for: image.repository, image.tag, image.pullPolicy, replicaCount, service.type, service.port, service.targetPort, service.nodePort (conditional), resources.requests, resources.limits, probe paths and timing, security context — fix any hardcoded values that should come from values.yaml
- [ ] T023 [US2] Validate replica override by running `helm template my-todo helm/todo-chatbot --set backend.replicaCount=2` and confirming the backend Deployment shows 2 replicas in rendered output
- [ ] T024 [US2] Validate service type override by running `helm template my-todo helm/todo-chatbot --set frontend.service.type=ClusterIP` and confirming the frontend Service renders as ClusterIP without nodePort
- [ ] T025 [US2] Validate secret override by running `helm template my-todo helm/todo-chatbot --set backend.secrets.databaseUrl="postgresql://test"` and confirming the Secret renders with the override value (not CHANGE_ME)

**Checkpoint**: All configurable parameters work via `--set` flags. Values.yaml is fully documented. Overrides for replicas, service type, and secrets verified through `helm template` dry-runs. User Story 2 is complete.

---

## Phase 5: User Story 3 — Health Monitoring and Deployment Validation (Priority: P3)

**Goal**: Ensure health probes catch failures, `helm test` validates connectivity, and developers can diagnose problems through structured checks.

**Independent Test**: Deploy the Helm chart, run validation checks (pod readiness, endpoint existence, no Warning events), run `helm test`, then break a configuration (wrong image tag) and confirm validation catches it.

### Implementation

- [x] T026 [US3] Verify liveness and readiness probes are correctly configured in both Deployment templates — confirm httpGet path, port, initialDelaySeconds, periodSeconds, timeoutSeconds, failureThreshold all reference values.yaml
- [x] T027 [US3] Verify RollingUpdate strategy is configured in both Deployment templates with maxSurge:1 and maxUnavailable:0 from plan.md
- [x] T028 [US3] Verify `helm/todo-chatbot/templates/tests/test-connection.yaml` tests both frontend (port 3000) and backend (port 8000) service connectivity with wget --spider
- [x] T029 [US3] Create empty `helm/todo-chatbot/charts/` directory to satisfy Helm chart structure requirements

**Checkpoint**: Health probes configured for both services, connectivity test covers both endpoints, rolling update strategy ensures zero-downtime upgrades. User Story 3 is complete.

---

## Phase 6: User Story 4 — AI-Assisted Infrastructure Generation (Priority: P4)

**Goal**: Generate raw Kubernetes manifests using AI agents and document all generation prompts in PHR records. Provide reference manifests in `k8s/` directory.

**Independent Test**: Verify each infrastructure artifact in `k8s/` has a corresponding PHR in `history/prompts/k8s-minikube-deploy/`. Run `kubectl apply --dry-run=client -f k8s/` and confirm all manifests are valid.

### Implementation

- [x] T030 [P] [US4] Generate raw frontend Deployment manifest at `k8s/frontend-deployment.yaml` using k8s-manifest-agent and record PHR
- [x] T031 [P] [US4] Generate raw frontend Service manifest at `k8s/frontend-service.yaml` using k8s-manifest-agent and record PHR
- [x] T032 [P] [US4] Generate raw backend Deployment manifest at `k8s/backend-deployment.yaml` using k8s-manifest-agent and record PHR
- [x] T033 [P] [US4] Generate raw backend Service manifest at `k8s/backend-service.yaml` using k8s-manifest-agent and record PHR
- [x] T034 [P] [US4] Generate raw backend ConfigMap manifest at `k8s/backend-configmap.yaml` using k8s-manifest-agent and record PHR
- [x] T035 [P] [US4] Generate raw backend Secret manifest at `k8s/backend-secret.yaml` using k8s-manifest-agent and record PHR
- [ ] T036 [US4] Validate all raw manifests pass `kubectl apply --dry-run=client -f k8s/` without errors

**Checkpoint**: All 6 raw manifests in `k8s/` pass dry-run validation. Each has a corresponding PHR. User Story 4 is complete.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and cleanup across all stories

- [ ] T037 [P] Verify both Docker images run as non-root (uid 1001) by inspecting running containers
- [ ] T038 [P] Verify container images do not contain `.env` files, secrets, or dev dependencies in final stage
- [ ] T039 Run full quickstart.md validation checklist: minikube status, images built, helm lint passes, helm install completes, all pods Running/Ready 1/1, zero restarts, frontend loads, backend /docs loads, helm test passes
- [ ] T040 Create PHR records for all AI-generated Dockerfiles (frontend and backend) documenting the prompts used
- [ ] T041 Final commit of all infrastructure artifacts (Dockerfiles, .dockerignore files, Helm chart, raw manifests, PHR records)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001 for standalone output needed by frontend Dockerfile)
- **User Story 1 (Phase 3)**: Depends on Foundational (working Docker images required for Helm chart testing)
- **User Story 2 (Phase 4)**: Depends on User Story 1 (Helm chart must exist before auditing configurability)
- **User Story 3 (Phase 5)**: Depends on User Story 1 (Helm templates must exist before verifying probe configuration)
- **User Story 4 (Phase 6)**: Depends on Foundational only (raw manifests are independent of Helm chart)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 2 (Foundational) — core deployment story
- **User Story 2 (P2)**: Depends on US1 — audits and validates the chart created in US1
- **User Story 3 (P3)**: Depends on US1 — verifies health monitoring in templates from US1
- **User Story 4 (P4)**: Depends on Phase 2 only — raw manifests are independent of Helm chart; can run in parallel with US2/US3

### Within Each User Story

- Scaffolding before templates (Chart.yaml, _helpers.tpl before Deployments)
- Templates before validation (create YAML before helm lint)
- Independent verification at each checkpoint

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002 (frontend .dockerignore) || T003 (backend .dockerignore)
```

**Phase 2 (Foundational)**:
```
T004 (frontend Dockerfile) || T005 (backend Dockerfile)
→ T006 (validate builds) after both complete
```

**Phase 3 (US1) — Templates**:
```
T011 (frontend deploy) || T012 (frontend svc) || T013 (frontend cm)
T014 (backend deploy) || T015 (backend svc) || T016 (backend cm) || T017 (backend secret)
All frontend templates || All backend templates (fully parallel)
```

**Phase 6 (US4) — Raw Manifests**:
```
T030 || T031 || T032 || T033 || T034 || T035 (all 6 manifests in parallel)
→ T036 (validate) after all complete
```

**Cross-Story Parallelism**:
```
US2 (Phase 4) || US4 (Phase 6) — can run simultaneously after US1
US3 (Phase 5) || US4 (Phase 6) — can run simultaneously after US1
```

---

## Parallel Example: User Story 1

```bash
# Launch all frontend templates in parallel:
Task: "Create frontend Deployment at helm/todo-chatbot/templates/frontend/deployment.yaml"
Task: "Create frontend Service at helm/todo-chatbot/templates/frontend/service.yaml"
Task: "Create frontend ConfigMap at helm/todo-chatbot/templates/frontend/configmap.yaml"

# Launch all backend templates in parallel:
Task: "Create backend Deployment at helm/todo-chatbot/templates/backend/deployment.yaml"
Task: "Create backend Service at helm/todo-chatbot/templates/backend/service.yaml"
Task: "Create backend ConfigMap at helm/todo-chatbot/templates/backend/configmap.yaml"
Task: "Create backend Secret at helm/todo-chatbot/templates/backend/secret.yaml"

# All frontend and backend templates can also run in parallel with each other
```

## Parallel Example: User Story 4

```bash
# Launch all raw manifest generations in parallel:
Task: "Generate frontend-deployment.yaml in k8s/"
Task: "Generate frontend-service.yaml in k8s/"
Task: "Generate backend-deployment.yaml in k8s/"
Task: "Generate backend-service.yaml in k8s/"
Task: "Generate backend-configmap.yaml in k8s/"
Task: "Generate backend-secret.yaml in k8s/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T003) — add standalone output, create .dockerignore files
2. Complete Phase 2: Foundational (T004–T006) — build and validate Docker images
3. Complete Phase 3: User Story 1 (T007–T020) — scaffold Helm chart, create all templates, validate
4. **STOP and VALIDATE**: `helm lint`, `helm install` in Minikube, verify pods Ready, access services
5. Deploy/demo if ready — this is a fully functional local Kubernetes deployment

### Incremental Delivery

1. Setup + Foundational → Docker images ready
2. Add User Story 1 → Full Helm deployment working (MVP!)
3. Add User Story 2 → Configurability verified and documented
4. Add User Story 3 → Health monitoring and validation complete
5. Add User Story 4 → AI generation documented with raw manifests
6. Polish → Final validation and cleanup

### Suggested MVP Scope

**User Story 1 (Phase 3)** is the MVP. After completing Phases 1–3 (T001–T020), the developer has:
- Working Docker images for both services
- A complete Helm chart that deploys the entire application
- Both services accessible from outside the cluster
- Frontend-to-backend communication working via internal DNS
- Connectivity test via `helm test`

This represents the core value proposition of Phase IV.
