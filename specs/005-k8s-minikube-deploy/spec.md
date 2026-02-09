# Feature Specification: Local Kubernetes Deployment with AI-Assisted DevOps

**Feature Branch**: `005-k8s-minikube-deploy`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Phase IV of the Todo Chatbot project — local Kubernetes deployment using Minikube and Helm charts with AI-assisted DevOps."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Containerize and Deploy Services Locally (Priority: P1)

A developer wants to run the entire Todo Chatbot application (frontend and backend) inside a local Kubernetes cluster so they can validate the deployment pipeline before any production rollout. They build container images for both services, install a single Helm chart, and verify that all pods start successfully and services are reachable through the browser and API endpoints.

**Why this priority**: This is the core deliverable of Phase IV. Without working container images and a functional Kubernetes deployment, no other story can proceed. It proves that the application runs correctly in a containerized, orchestrated environment.

**Independent Test**: Can be fully tested by building both Docker images, running `helm install`, confirming all pods reach Ready state, and accessing the frontend in a browser and the backend API docs endpoint. Delivers a fully operational local cluster deployment.

**Acceptance Scenarios**:

1. **Given** the frontend and backend source code exist, **When** a developer builds Docker images for both services, **Then** both images build without errors and are available in the local image store.
2. **Given** Docker images are built and available, **When** the developer installs the Helm chart into Minikube, **Then** all pods reach Running status with all containers reporting Ready within 2 minutes.
3. **Given** the Helm chart is installed and pods are healthy, **When** the developer opens the frontend service URL in a browser, **Then** the Todo Chatbot UI renders correctly and is interactive.
4. **Given** the Helm chart is installed and pods are healthy, **When** the developer accesses the backend service API documentation endpoint, **Then** the API docs page loads and shows all available endpoints.
5. **Given** the frontend is running in the cluster, **When** the frontend makes an API call to the backend, **Then** the request is routed through the internal Kubernetes service and returns a valid response.

---

### User Story 2 - Configurable Deployment via Helm Values (Priority: P2)

A developer wants to customize the deployment without modifying template files. They adjust parameters like replica counts, image tags, service types, and resource limits through a centralized configuration file. The same chart supports both local development (Minikube) and future production environments by changing only configuration values.

**Why this priority**: Configurability makes the deployment reusable and portable across environments. Without it, every environment change requires editing template files, breaking the "declarative over imperative" principle.

**Independent Test**: Can be tested by installing the Helm chart with custom values (e.g., changing replica count from 1 to 2), verifying the cluster reflects the override, then reinstalling with defaults and confirming it reverts.

**Acceptance Scenarios**:

1. **Given** the Helm chart is available, **When** the developer overrides the replica count for the backend to 2 during install, **Then** 2 backend pods start and reach Ready state.
2. **Given** the Helm chart is installed, **When** the developer changes the service type from NodePort to ClusterIP via a values override, **Then** the service is recreated with the new type after upgrade.
3. **Given** the Helm chart values file exists, **When** a reviewer reads it, **Then** every configurable parameter has a descriptive comment explaining its purpose and valid options.
4. **Given** secrets are required (database URL, auth secret, API key), **When** the developer installs the chart, **Then** secret values are passed at install time and are not stored in any file committed to version control.

---

### User Story 3 - Health Monitoring and Deployment Validation (Priority: P3)

A developer wants confidence that the deployed services are healthy and behaving correctly. After deployment, they run a validation workflow that checks pod readiness, verifies service endpoints have active backends, and confirms no warning events exist in the cluster. If a pod is unhealthy, the developer can quickly identify the root cause through structured diagnostics.

**Why this priority**: Deployment without validation is incomplete. Health checks ensure the deployment is genuinely working, not just "kubectl says Running." This story completes the deployment lifecycle.

**Independent Test**: Can be tested by deploying the Helm chart, running the validation checks, then deliberately breaking a configuration (e.g., wrong image tag) and confirming the validation catches the failure.

**Acceptance Scenarios**:

1. **Given** the Helm chart is installed, **When** the developer runs pod readiness checks, **Then** all pods report Ready within the expected timeout.
2. **Given** the Helm chart is installed, **When** the developer checks service endpoints, **Then** all services have at least one active endpoint (not empty).
3. **Given** the Helm chart is installed, **When** the developer queries cluster events, **Then** there are no Warning-type events related to the Todo Chatbot workloads.
4. **Given** a pod is failing (e.g., CrashLoopBackOff), **When** the developer inspects pod logs and events, **Then** the root cause (missing environment variable, image pull failure, resource exhaustion) is identifiable from the output.
5. **Given** the Helm chart is installed, **When** the developer runs Helm's built-in test, **Then** the test verifies frontend and backend services are reachable from within the cluster.

---

### User Story 4 - AI-Assisted Infrastructure Generation (Priority: P4)

A developer uses AI tools (Claude Code, Docker AI, kubectl-ai) to generate infrastructure artifacts — Dockerfiles, Kubernetes manifests, and Helm chart templates — rather than writing them from scratch. Every AI-generated artifact includes a documented prompt so it can be reproduced or refined later. This accelerates infrastructure setup while maintaining auditability.

**Why this priority**: AI-assisted generation is a differentiating aspect of Phase IV but is a process concern, not a runtime requirement. The deployment works regardless of how artifacts were generated; this story ensures the AI-assisted workflow is documented and reproducible.

**Independent Test**: Can be tested by verifying that each infrastructure artifact (Dockerfile, manifest, Helm template) has a corresponding prompt record in the project's history, and that re-running the prompt produces a functionally equivalent artifact.

**Acceptance Scenarios**:

1. **Given** the developer needs a Dockerfile for a service, **When** they use an AI tool with a documented prompt, **Then** the generated Dockerfile builds a working container image.
2. **Given** the developer needs Kubernetes manifests, **When** they use an AI tool with a documented prompt, **Then** the generated manifests pass dry-run validation.
3. **Given** AI-generated infrastructure artifacts exist, **When** a reviewer checks the project history, **Then** every artifact has a corresponding prompt record documenting how it was generated.
4. **Given** a prompt record exists for an artifact, **When** the developer re-runs the prompt, **Then** the output is functionally equivalent to the original artifact.

---

### Edge Cases

- What happens when Minikube runs out of memory or CPU while deploying both services?
- What happens when a Docker image build fails due to missing dependencies?
- What happens when the backend cannot connect to the external database from inside the cluster?
- What happens when secrets are not provided at install time (using placeholder defaults)?
- What happens when the developer forgets to build images inside Minikube's Docker context (images built on host instead)?
- What happens when the Helm chart is installed a second time without uninstalling first?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST produce a container image for the frontend service that, when started, serves the application on its configured port.
- **FR-002**: The system MUST produce a container image for the backend service that, when started, serves the API on its configured port.
- **FR-003**: Container images MUST use multi-stage builds to separate build dependencies from runtime, producing minimal final images.
- **FR-004**: Container images MUST run as a non-root user for security.
- **FR-005**: Container images MUST include a health check mechanism that reports whether the service is ready to accept traffic.
- **FR-006**: A Helm chart MUST package both frontend and backend services into a single installable unit.
- **FR-007**: The Helm chart MUST support configurable parameters including: image repository, image tag, replica count, service type, service port, resource requests, resource limits, and health check paths.
- **FR-008**: All configurable parameters in the Helm chart MUST have documented comments explaining their purpose and valid options.
- **FR-009**: The Helm chart MUST use a shared template helper for labels and selectors to ensure consistency across all resources.
- **FR-010**: The Helm chart MUST include Kubernetes health probes (liveness and readiness) for all deployments.
- **FR-011**: The Helm chart MUST support separate handling of sensitive configuration (secrets) and non-sensitive configuration (config maps).
- **FR-012**: Secret values in the Helm chart MUST default to placeholder values and MUST NOT contain real credentials in any version-controlled file.
- **FR-013**: The Helm chart MUST include a built-in connectivity test that verifies both services are reachable from within the cluster.
- **FR-014**: Kubernetes Deployments MUST specify resource requests and limits for CPU and memory on all containers.
- **FR-015**: Kubernetes Deployments MUST use a rolling update strategy to enable zero-downtime upgrades.
- **FR-016**: The frontend service MUST be accessible from outside the cluster when deployed to Minikube (via NodePort or equivalent mechanism).
- **FR-017**: The backend service MUST be accessible from outside the cluster when deployed to Minikube (via NodePort or equivalent mechanism).
- **FR-018**: The frontend MUST be able to reach the backend via internal Kubernetes service DNS (not external URLs).
- **FR-019**: All generated infrastructure artifacts (Dockerfiles, manifests, Helm charts) MUST be committed to version control.
- **FR-020**: All AI-generated infrastructure artifacts MUST have a corresponding prompt history record documenting the prompt used to generate them.

### Key Entities

- **Container Image**: A packaged, runnable snapshot of a service (frontend or backend) with all dependencies. Key attributes: repository name, tag, base image, exposed port, health check path.
- **Helm Chart**: A versioned package of Kubernetes resource templates and a configuration values file. Key attributes: chart name, version, app version, configurable values, template files.
- **Deployment**: A Kubernetes resource managing a set of identical pod replicas for a service. Key attributes: replica count, image reference, resource limits, health probes, update strategy.
- **Service**: A Kubernetes resource providing a stable network endpoint for accessing pods. Key attributes: service type (NodePort/ClusterIP), port mapping, selector labels.
- **ConfigMap**: A Kubernetes resource storing non-sensitive configuration as key-value pairs. Key attributes: environment variables for application settings.
- **Secret**: A Kubernetes resource storing sensitive configuration (credentials, API keys). Key attributes: database URL, auth secret, API keys — all using placeholders in version control.

## Constraints

- Deployment targets Minikube only; no cloud-provider-specific features (LoadBalancer with external IP, cloud storage, managed databases).
- All infrastructure artifacts MUST be generated with AI assistance (Claude Code, Docker AI, kubectl-ai) and the generation prompts MUST be documented.
- No imperative cluster changes without a corresponding declarative manifest in version control.
- Helm MUST be the canonical deployment mechanism; raw `kubectl apply` is permitted only as a fallback during development.
- Container images MUST NOT contain secrets, `.env` files, or development dependencies in the final stage.
- Resource requests and limits MUST be appropriate for a single-node Minikube cluster (modest allocations, not production-scale).
- The external database (Neon PostgreSQL) is accessed from within the cluster; no database is deployed inside Minikube.

## Assumptions

- Minikube is installed and available on the developer's machine with the Docker driver.
- The developer has Helm 3 and kubectl installed and configured.
- Docker is available for building container images.
- The existing frontend (Next.js) and backend (FastAPI) applications are functional and can be built from their respective directories.
- The Neon PostgreSQL database is accessible from within the Minikube cluster (no network restrictions blocking outbound connections from pods).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both container images build successfully from source in a single command each, with the final images each under 500MB in size.
- **SC-002**: A single Helm install command deploys the entire application (frontend + backend) with all pods reaching Ready status within 2 minutes.
- **SC-003**: The frontend is accessible via browser through the exposed Minikube service URL and renders the Todo Chatbot UI correctly.
- **SC-004**: The backend API documentation endpoint is accessible via the exposed Minikube service URL and displays all available API endpoints.
- **SC-005**: The frontend can communicate with the backend through the internal cluster service, successfully performing at least one end-to-end operation (e.g., listing tasks).
- **SC-006**: All configurable deployment parameters can be overridden at install time without modifying any template file, verified by successfully deploying with at least 3 different value overrides.
- **SC-007**: Helm chart validation (`helm lint`) passes without errors or warnings.
- **SC-008**: Health probes (liveness and readiness) pass for all pods, verified by 0 restarts and Ready=1/1 status sustained for at least 5 minutes after deployment.
- **SC-009**: Every AI-generated infrastructure artifact has a corresponding prompt history record in the project repository, verified by audit of the `history/prompts/` directory.
- **SC-010**: A reviewer can deploy the entire application from scratch by following the documented steps, completing the process in under 10 minutes on a machine with prerequisites installed.
