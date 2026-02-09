# Research: Local Kubernetes Deployment with AI-Assisted DevOps

**Feature**: 005-k8s-minikube-deploy
**Date**: 2026-02-08

## Research Summary

All technical unknowns from the planning phase have been resolved. This document consolidates the 7 research decisions made during Phase 0.

## R1: Next.js Standalone Output for Docker

**Question**: How to minimize the frontend Docker image while retaining server-side rendering?

**Decision**: Use `output: "standalone"` in `next.config.ts`.

**Rationale**: Next.js standalone output bundles only the files needed for a production deployment into a `standalone` directory with a self-contained `server.js`. This eliminates the ~300MB `node_modules` folder from the final image. The standalone output includes `server.js`, `.next/static`, and `public/` — everything needed to serve the application.

**Impact**: Requires a one-line change to `next.config.ts`. The Dockerfile copies `standalone/`, `.next/static`, and `public/` into the runner stage.

**Source**: Next.js documentation on standalone output mode.

## R2: Backend Dependency Management in Docker

**Question**: Should the backend Dockerfile use `pip`, `uv`, or another package manager?

**Decision**: Use `uv sync --frozen --no-dev` in the builder stage, copy the `.venv` to the runtime stage.

**Rationale**: The project uses `uv` as its canonical package manager (per constitution). The `uv.lock` file provides deterministic, reproducible installs. Using `--frozen` ensures the lockfile is not modified. Using `--no-dev` excludes test dependencies from the production image.

**Impact**: The existing `backend/Dockerfile` (pip-based, single-stage) must be replaced. The `uv` binary is copied from the official `ghcr.io/astral-sh/uv:latest` image into the builder.

## R3: Minikube Image Strategy

**Question**: How to make locally-built Docker images available to Minikube's kubelet?

**Decision**: Use `eval $(minikube docker-env)` to point the Docker CLI at Minikube's Docker daemon, then build images there directly. Set `imagePullPolicy: Never` in all Deployments.

**Rationale**: This avoids the overhead of a container registry (Docker Hub, local registry). Images built inside Minikube's Docker daemon are immediately available to the kubelet. The `imagePullPolicy: Never` setting prevents Kubernetes from attempting to pull images from a remote registry.

**Caveat**: If the developer forgets to run `eval $(minikube docker-env)`, images will be built on the host Docker and pods will fail with `ErrImageNeverPull`. The quickstart guide and skill documentation explicitly warn about this.

## R4: Helm Chart Structure

**Question**: One chart or multiple charts for a 2-service application?

**Decision**: Single Helm chart at `helm/todo-chatbot/` with both services as independently toggleable components via `frontend.enabled` and `backend.enabled` flags.

**Rationale**: A single chart keeps the install command simple (`helm install my-todo helm/todo-chatbot`). The `_helpers.tpl` file provides shared labels. Each component has its own subdirectory under `templates/` for organizational clarity.

## R5: Service Exposure on Minikube

**Question**: How to expose services for browser access on Minikube?

**Decision**: Use `NodePort` services. Access via `minikube service <name> --url`.

**Rationale**: NodePort is the simplest external access mechanism on Minikube. It doesn't require `minikube tunnel` (which LoadBalancer needs) and is more convenient than `kubectl port-forward` for persistent browser access.

## R6: Frontend-to-Backend Communication

**Question**: How does the frontend reach the backend inside the cluster?

**Decision**: Frontend ConfigMap sets `API_BASE_URL` to `http://todo-backend:8000` (internal Kubernetes service DNS).

**Rationale**: Kubernetes provides DNS-based service discovery. The service name `todo-backend` resolves to the ClusterIP of the backend service. This is the idiomatic Kubernetes approach and works regardless of NodePort assignments.

**Caveat**: This works for server-side rendering (SSR) API calls. For client-side (browser) API calls, the browser cannot resolve `todo-backend` DNS. The frontend must proxy client-side requests through its own server, or the client-side code must use the external NodePort URL. This is handled by Next.js API routes acting as a proxy.

## R7: Health Check Endpoints

**Question**: Which endpoints to use for Kubernetes liveness and readiness probes?

**Decision**: Frontend: `GET /` on port 3000. Backend: `GET /docs` on port 8000.

**Rationale**: Both endpoints are always available when the application is healthy, require no authentication, and return HTTP 200. `/docs` is FastAPI's built-in Swagger UI which confirms the application is fully loaded and serving.

## Unresolved Items

None. All research questions resolved.
