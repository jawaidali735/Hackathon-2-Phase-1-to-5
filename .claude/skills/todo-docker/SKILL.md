---
name: todo-docker
description: "Use this skill when generating, optimizing, or troubleshooting Dockerfiles for the Todo Chatbot frontend (Next.js 16+) and backend (FastAPI/Python). Trigger words: Dockerfile, containerize, build image, Docker build, Docker image, dockerize, container."
---

# Todo Docker Containerization Skill

This skill provides step-by-step guidance for generating production-grade Dockerfiles for the Todo Chatbot project's frontend (Next.js 16+) and backend (FastAPI with uv).

## Purpose

Generate optimized, multi-stage Dockerfiles that:
1. Produce minimal image sizes through multi-stage builds
2. Maximize Docker layer caching for fast rebuilds
3. Follow security best practices (non-root user, no secrets in image)
4. Align with the project constitution's Phase 4 Cloud-Native First principle
5. Work with Minikube and Kubernetes deployments

## When to Use

Use this skill when:
- Creating a Dockerfile for the frontend (`frontend/Dockerfile`)
- Creating or optimizing the backend Dockerfile (`backend/Dockerfile`)
- Generating `.dockerignore` files for either service
- Debugging Docker build failures for the Todo Chatbot
- Optimizing image size or build speed for existing Dockerfiles
- Preparing services for Kubernetes deployment in Minikube

**Trigger words**: Dockerfile, containerize, build image, Docker build, Docker image, dockerize, container, multi-stage build

## Project Context

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Package manager**: npm
- **Build command**: `next build`
- **Start command**: `next start`
- **Default port**: 3000
- **Key dependencies**: React 19, Tailwind CSS, Better Auth, Drizzle ORM
- **Output directory**: `.next/`

### Backend
- **Framework**: Python FastAPI
- **Package manager**: uv (constitution-mandated)
- **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Default port**: 8000
- **Key dependencies**: FastAPI, SQLModel, OpenAI Agents SDK, MCP SDK
- **Config file**: `pyproject.toml`

## Step-by-Step: Frontend Dockerfile

### Step 1: Create `.dockerignore`

Generate `frontend/.dockerignore` to exclude build artifacts and dev files:

```dockerignore
node_modules
.next
.git
.gitignore
*.md
.env*
.vscode
.idea
coverage
tests
__tests__
.eslintrc*
.prettierrc*
Dockerfile
docker-compose*
```

### Step 2: Generate Multi-Stage Dockerfile

The frontend Dockerfile MUST use three stages:

```dockerfile
# ============================================================
# Build: docker build -t todo-frontend:latest .
# Run:   docker run -p 3000:3000 todo-frontend:latest
# ============================================================

# --- Stage 1: Install dependencies ---
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# --- Stage 2: Build the application ---
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build-time env vars (non-secret, override at runtime)
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# --- Stage 3: Production runtime ---
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Non-root user for security
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copy only the built output and production essentials
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
```

**Important**: The standalone output requires `output: "standalone"` in `next.config.ts`:

```typescript
const nextConfig = {
  output: "standalone",
};
```

### Step 3: Verify Build

```bash
cd frontend
docker build -t todo-frontend:latest .
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
  todo-frontend:latest
```

## Step-by-Step: Backend Dockerfile

### Step 1: Create `.dockerignore`

Generate `backend/.dockerignore`:

```dockerignore
.git
.gitignore
*.md
.env*
.vscode
.idea
__pycache__
*.pyc
*.pyo
.pytest_cache
.mypy_cache
.ruff_cache
tests
Dockerfile
docker-compose*
.venv
```

### Step 2: Generate Multi-Stage Dockerfile

The backend Dockerfile MUST use uv (per constitution) and multi-stage builds:

```dockerfile
# ============================================================
# Build: docker build -t todo-backend:latest .
# Run:   docker run -p 8000:8000 todo-backend:latest
# ============================================================

# --- Stage 1: Build with uv ---
FROM python:3.11-slim AS builder
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for cache efficiency
COPY pyproject.toml uv.lock* ./

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY . .

# Install the project itself
RUN uv sync --frozen --no-dev

# --- Stage 2: Production runtime ---
FROM python:3.11-slim AS runner
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Non-root user for security
RUN groupadd --system --gid 1001 appgroup \
    && useradd --system --uid 1001 --gid appgroup appuser

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# Ensure the venv is on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Set ownership
RUN chown -R appuser:appgroup /app

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 3: Verify Build

```bash
cd backend
docker build -t todo-backend:latest .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e BETTER_AUTH_SECRET=... \
  todo-backend:latest
```

## Environment Variables

### Frontend (runtime injection)
| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | Yes | Backend API URL |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | Yes | Auth service URL |
| `NEXT_PUBLIC_AUTH_ENABLED` | No | Enable/disable auth (default: true) |

### Backend (runtime injection)
| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret |
| `CORS_ORIGINS` | Yes | Allowed CORS origins |
| `OPENAI_API_KEY` | Yes | OpenAI API key for agent |
| `JWT_ALGORITHM` | No | JWT algorithm (default: HS256) |

**CRITICAL**: Never bake secrets into images. Pass them at runtime via `-e` flags, `--env-file`, or Kubernetes Secrets.

## Optimization Checklist

Before finalizing any Dockerfile for this project, verify:

- [ ] Multi-stage build used (minimum 2 stages: build + runtime)
- [ ] Base images use specific version tags (no `latest`)
- [ ] Dependency manifests copied before source code (cache optimization)
- [ ] Non-root user configured in runtime stage
- [ ] `.dockerignore` present and excludes node_modules, .git, .env, tests
- [ ] `HEALTHCHECK` instruction defined
- [ ] No secrets or `.env` files copied into image
- [ ] `EXPOSE` matches the service port
- [ ] `CMD` uses exec form (JSON array), not shell form
- [ ] Build and run commands documented as comments at top of Dockerfile
- [ ] Image builds successfully with `docker build`
- [ ] Container starts and responds on expected port

## Kubernetes Integration Notes

When building for Minikube deployment:

1. **Use Minikube's Docker daemon** to avoid pushing to a remote registry:
   ```bash
   eval $(minikube docker-env)
   docker build -t todo-frontend:latest ./frontend
   docker build -t todo-backend:latest ./backend
   ```

2. **Set `imagePullPolicy: Never`** in Kubernetes manifests when using local images.

3. **Health check endpoints** exposed by `HEALTHCHECK` should align with Kubernetes liveness/readiness probes.

## Dependencies

- Docker 20.10+ (BuildKit enabled)
- Node.js 22 (for frontend base image)
- Python 3.11 (for backend base image)
- uv (installed inside builder stage for backend)

## Verification

After building both images, validate with:

```bash
# Check image sizes (should be well under 500MB each)
docker images | grep todo-

# Test frontend
docker run --rm -p 3000:3000 todo-frontend:latest &
curl -f http://localhost:3000 && echo "Frontend OK"

# Test backend
docker run --rm -p 8000:8000 -e DATABASE_URL=... todo-backend:latest &
curl -f http://localhost:8000/docs && echo "Backend OK"
```
