---
name: todo-helm
description: "Use this skill when scaffolding, modifying, or debugging a Helm chart for the Todo Chatbot application. Covers Chart.yaml, values.yaml, _helpers.tpl, and Deployment/Service/ConfigMap/Secret templates with Go templating. Trigger phrases: Helm chart, values.yaml, templates, helm install, chart scaffold, Helm template."
---

# Todo Helm Chart Scaffolding Skill

This skill provides step-by-step guidance for scaffolding and maintaining a complete Helm chart for the Todo Chatbot project, packaging the frontend (Next.js) and backend (FastAPI) services into a single installable chart targeting Minikube.

## Purpose

Scaffold a Helm chart that:
1. Packages both frontend and backend Deployments, Services, ConfigMaps, and Secrets
2. Uses `values.yaml` for all environment-specific configuration
3. Follows Helm 3 best practices with `_helpers.tpl` for reusable template definitions
4. Supports Minikube (local) and future production clusters via value overrides
5. Passes `helm lint` and `helm template` validation
6. Aligns with the project constitution's Phase 4 Helm Packaging Standards

## When to Use

Use this skill when:
- Scaffolding the initial Helm chart directory structure
- Creating or updating `Chart.yaml`, `values.yaml`, or `_helpers.tpl`
- Writing Helm templates for Deployments, Services, ConfigMaps, or Secrets
- Adding Ingress, HPA, or ServiceAccount templates
- Debugging Helm template rendering issues
- Preparing for `helm install` or `helm upgrade` on Minikube

**Trigger phrases**: Helm chart, values.yaml, templates, helm install, chart scaffold, Helm template, helm lint, helm upgrade, Chart.yaml, _helpers.tpl

## Chart Directory Structure

The chart MUST be placed at `helm/todo-chatbot/` relative to the project root:

```
helm/todo-chatbot/
├── Chart.yaml                    # Chart metadata and version
├── values.yaml                   # Default configuration values
├── .helmignore                   # Files to ignore during packaging
├── templates/
│   ├── _helpers.tpl              # Reusable template definitions
│   ├── NOTES.txt                 # Post-install instructions
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
└── charts/                       # Subcharts (empty for now)
```

## Step-by-Step: Chart Scaffolding

### Step 1: Create `Chart.yaml`

```yaml
# helm/todo-chatbot/Chart.yaml
apiVersion: v2
name: todo-chatbot
description: A Helm chart for the Todo Chatbot application (frontend + backend)
type: application
version: 0.1.0       # Chart version (semver)
appVersion: "1.0.0"  # Application version
keywords:
  - todo
  - chatbot
  - fastapi
  - nextjs
maintainers:
  - name: architect
```

### Step 2: Create `values.yaml`

Every configurable parameter MUST have a YAML comment. Group values by component.

```yaml
# helm/todo-chatbot/values.yaml

# -- Global settings applied to all components
global:
  # -- Kubernetes namespace (overridable via --namespace flag)
  namespace: default

# =============================================================================
# Frontend (Next.js)
# =============================================================================
frontend:
  # -- Enable or disable the frontend component
  enabled: true

  # -- Number of frontend pod replicas
  replicaCount: 1

  image:
    # -- Frontend container image repository
    repository: todo-frontend
    # -- Image tag (defaults to Chart appVersion if not set)
    tag: "latest"
    # -- Image pull policy: Never for Minikube local images, Always for registry
    pullPolicy: Never

  service:
    # -- Service type: NodePort for Minikube, ClusterIP for production
    type: NodePort
    # -- Service port exposed to the cluster
    port: 3000
    # -- Target port on the container
    targetPort: 3000
    # -- Fixed NodePort (optional, 30000-32767). Remove to auto-assign.
    # nodePort: 30080

  resources:
    requests:
      # -- Minimum CPU for frontend pod
      cpu: 100m
      # -- Minimum memory for frontend pod
      memory: 128Mi
    limits:
      # -- Maximum CPU for frontend pod
      cpu: 500m
      # -- Maximum memory for frontend pod
      memory: 512Mi

  livenessProbe:
    # -- Path for liveness probe HTTP check
    path: /
    # -- Seconds to wait before first liveness check
    initialDelaySeconds: 15
    # -- Seconds between liveness checks
    periodSeconds: 20
    # -- Seconds to wait for probe response
    timeoutSeconds: 5
    # -- Consecutive failures before restart
    failureThreshold: 3

  readinessProbe:
    # -- Path for readiness probe HTTP check
    path: /
    # -- Seconds to wait before first readiness check
    initialDelaySeconds: 5
    # -- Seconds between readiness checks
    periodSeconds: 10
    # -- Seconds to wait for probe response
    timeoutSeconds: 3
    # -- Consecutive failures before unready
    failureThreshold: 3

  env:
    # -- Backend API URL the frontend calls
    apiBaseUrl: "http://todo-backend:8000"

# =============================================================================
# Backend (FastAPI)
# =============================================================================
backend:
  # -- Enable or disable the backend component
  enabled: true

  # -- Number of backend pod replicas
  replicaCount: 1

  image:
    # -- Backend container image repository
    repository: todo-backend
    # -- Image tag (defaults to Chart appVersion if not set)
    tag: "latest"
    # -- Image pull policy: Never for Minikube local images, Always for registry
    pullPolicy: Never

  service:
    # -- Service type: NodePort for Minikube, ClusterIP for production
    type: NodePort
    # -- Service port exposed to the cluster
    port: 8000
    # -- Target port on the container
    targetPort: 8000
    # -- Fixed NodePort (optional, 30000-32767). Remove to auto-assign.
    # nodePort: 30081

  resources:
    requests:
      # -- Minimum CPU for backend pod
      cpu: 100m
      # -- Minimum memory for backend pod
      memory: 128Mi
    limits:
      # -- Maximum CPU for backend pod
      cpu: 500m
      # -- Maximum memory for backend pod
      memory: 512Mi

  livenessProbe:
    # -- Path for liveness probe HTTP check
    path: /docs
    # -- Seconds to wait before first liveness check
    initialDelaySeconds: 20
    # -- Seconds between liveness checks
    periodSeconds: 30
    # -- Seconds to wait for probe response
    timeoutSeconds: 5
    # -- Consecutive failures before restart
    failureThreshold: 3

  readinessProbe:
    # -- Path for readiness probe HTTP check
    path: /docs
    # -- Seconds to wait before first readiness check
    initialDelaySeconds: 10
    # -- Seconds between readiness checks
    periodSeconds: 10
    # -- Seconds to wait for probe response
    timeoutSeconds: 3
    # -- Consecutive failures before unready
    failureThreshold: 3

  config:
    # -- Allowed CORS origins
    corsOrigins: "http://localhost:3000"
    # -- JWT signing algorithm
    jwtAlgorithm: "HS256"
    # -- JWT token expiration in days
    jwtExpirationDays: "7"

  secrets:
    # -- Neon PostgreSQL connection string (CHANGE_ME before install)
    databaseUrl: "CHANGE_ME"
    # -- JWT signing secret shared with frontend auth (CHANGE_ME before install)
    betterAuthSecret: "CHANGE_ME"
    # -- OpenAI API key for AI agent (CHANGE_ME before install)
    openaiApiKey: "CHANGE_ME"

# =============================================================================
# Security context (shared)
# =============================================================================
podSecurityContext:
  # -- Require non-root user at pod level
  runAsNonRoot: true
  # -- Filesystem group for volumes
  fsGroup: 1001

containerSecurityContext:
  # -- Prevent privilege escalation
  allowPrivilegeEscalation: false
  # -- Run as non-root user
  runAsUser: 1001
  # -- Run as non-root group
  runAsGroup: 1001
```

### Step 3: Create `_helpers.tpl`

This file defines all reusable template functions. Templates MUST use `include` to call these helpers.

```yaml
{{/* helm/todo-chatbot/templates/_helpers.tpl */}}

{{/*
Chart name, truncated to 63 chars (Kubernetes name limit).
*/}}
{{- define "todo-chatbot.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Fully qualified app name. Uses release name + chart name.
Truncated to 63 chars.
*/}}
{{- define "todo-chatbot.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Chart label value.
*/}}
{{- define "todo-chatbot.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels applied to every resource.
*/}}
{{- define "todo-chatbot.labels" -}}
helm.sh/chart: {{ include "todo-chatbot.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: todo-chatbot
{{- end }}

{{/*
Frontend labels.
*/}}
{{- define "todo-chatbot.frontend.labels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/name: todo-frontend
app.kubernetes.io/component: frontend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Frontend selector labels (subset used in matchLabels).
*/}}
{{- define "todo-chatbot.frontend.selectorLabels" -}}
app.kubernetes.io/name: todo-frontend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Backend labels.
*/}}
{{- define "todo-chatbot.backend.labels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/name: todo-backend
app.kubernetes.io/component: api
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Backend selector labels (subset used in matchLabels).
*/}}
{{- define "todo-chatbot.backend.selectorLabels" -}}
app.kubernetes.io/name: todo-backend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### Step 4: Create Frontend Deployment Template

```yaml
# helm/todo-chatbot/templates/frontend/deployment.yaml
{{- if .Values.frontend.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  labels:
    {{- include "todo-chatbot.frontend.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.frontend.replicaCount }}
  revisionHistoryLimit: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      {{- include "todo-chatbot.frontend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "todo-chatbot.frontend.selectorLabels" . | nindent 8 }}
    spec:
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: frontend
          image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.frontend.service.targetPort }}
              protocol: TCP
          env:
            - name: NEXT_PUBLIC_API_BASE_URL
              valueFrom:
                configMapKeyRef:
                  name: todo-frontend-config
                  key: API_BASE_URL
          resources:
            {{- toYaml .Values.frontend.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: {{ .Values.frontend.livenessProbe.path }}
              port: http
            initialDelaySeconds: {{ .Values.frontend.livenessProbe.initialDelaySeconds }}
            periodSeconds: {{ .Values.frontend.livenessProbe.periodSeconds }}
            timeoutSeconds: {{ .Values.frontend.livenessProbe.timeoutSeconds }}
            failureThreshold: {{ .Values.frontend.livenessProbe.failureThreshold }}
          readinessProbe:
            httpGet:
              path: {{ .Values.frontend.readinessProbe.path }}
              port: http
            initialDelaySeconds: {{ .Values.frontend.readinessProbe.initialDelaySeconds }}
            periodSeconds: {{ .Values.frontend.readinessProbe.periodSeconds }}
            timeoutSeconds: {{ .Values.frontend.readinessProbe.timeoutSeconds }}
            failureThreshold: {{ .Values.frontend.readinessProbe.failureThreshold }}
          securityContext:
            {{- toYaml .Values.containerSecurityContext | nindent 12 }}
{{- end }}
```

### Step 5: Create Frontend Service Template

```yaml
# helm/todo-chatbot/templates/frontend/service.yaml
{{- if .Values.frontend.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
  labels:
    {{- include "todo-chatbot.frontend.labels" . | nindent 4 }}
spec:
  type: {{ .Values.frontend.service.type }}
  selector:
    {{- include "todo-chatbot.frontend.selectorLabels" . | nindent 4 }}
  ports:
    - name: http
      port: {{ .Values.frontend.service.port }}
      targetPort: http
      protocol: TCP
      {{- if and (eq .Values.frontend.service.type "NodePort") .Values.frontend.service.nodePort }}
      nodePort: {{ .Values.frontend.service.nodePort }}
      {{- end }}
{{- end }}
```

### Step 6: Create Backend Deployment Template

```yaml
# helm/todo-chatbot/templates/backend/deployment.yaml
{{- if .Values.backend.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    {{- include "todo-chatbot.backend.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.backend.replicaCount }}
  revisionHistoryLimit: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      {{- include "todo-chatbot.backend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "todo-chatbot.backend.selectorLabels" . | nindent 8 }}
    spec:
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: backend
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.backend.service.targetPort }}
              protocol: TCP
          envFrom:
            - configMapRef:
                name: todo-backend-config
            - secretRef:
                name: todo-backend-secret
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: {{ .Values.backend.livenessProbe.path }}
              port: http
            initialDelaySeconds: {{ .Values.backend.livenessProbe.initialDelaySeconds }}
            periodSeconds: {{ .Values.backend.livenessProbe.periodSeconds }}
            timeoutSeconds: {{ .Values.backend.livenessProbe.timeoutSeconds }}
            failureThreshold: {{ .Values.backend.livenessProbe.failureThreshold }}
          readinessProbe:
            httpGet:
              path: {{ .Values.backend.readinessProbe.path }}
              port: http
            initialDelaySeconds: {{ .Values.backend.readinessProbe.initialDelaySeconds }}
            periodSeconds: {{ .Values.backend.readinessProbe.periodSeconds }}
            timeoutSeconds: {{ .Values.backend.readinessProbe.timeoutSeconds }}
            failureThreshold: {{ .Values.backend.readinessProbe.failureThreshold }}
          securityContext:
            {{- toYaml .Values.containerSecurityContext | nindent 12 }}
{{- end }}
```

### Step 7: Create Backend Service, ConfigMap, and Secret Templates

**Service:**

```yaml
# helm/todo-chatbot/templates/backend/service.yaml
{{- if .Values.backend.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
  labels:
    {{- include "todo-chatbot.backend.labels" . | nindent 4 }}
spec:
  type: {{ .Values.backend.service.type }}
  selector:
    {{- include "todo-chatbot.backend.selectorLabels" . | nindent 4 }}
  ports:
    - name: http
      port: {{ .Values.backend.service.port }}
      targetPort: http
      protocol: TCP
      {{- if and (eq .Values.backend.service.type "NodePort") .Values.backend.service.nodePort }}
      nodePort: {{ .Values.backend.service.nodePort }}
      {{- end }}
{{- end }}
```

**ConfigMap:**

```yaml
# helm/todo-chatbot/templates/backend/configmap.yaml
{{- if .Values.backend.enabled }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-backend-config
  labels:
    {{- include "todo-chatbot.backend.labels" . | nindent 4 }}
data:
  CORS_ORIGINS: {{ .Values.backend.config.corsOrigins | quote }}
  JWT_ALGORITHM: {{ .Values.backend.config.jwtAlgorithm | quote }}
  JWT_EXPIRATION_DAYS: {{ .Values.backend.config.jwtExpirationDays | quote }}
{{- end }}
```

**Secret:**

```yaml
# helm/todo-chatbot/templates/backend/secret.yaml
{{- if .Values.backend.enabled }}
apiVersion: v1
kind: Secret
metadata:
  name: todo-backend-secret
  labels:
    {{- include "todo-chatbot.backend.labels" . | nindent 4 }}
type: Opaque
stringData:
  DATABASE_URL: {{ .Values.backend.secrets.databaseUrl | quote }}
  BETTER_AUTH_SECRET: {{ .Values.backend.secrets.betterAuthSecret | quote }}
  OPENAI_API_KEY: {{ .Values.backend.secrets.openaiApiKey | quote }}
{{- end }}
```

### Step 8: Create Frontend ConfigMap

```yaml
# helm/todo-chatbot/templates/frontend/configmap.yaml
{{- if .Values.frontend.enabled }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-frontend-config
  labels:
    {{- include "todo-chatbot.frontend.labels" . | nindent 4 }}
data:
  API_BASE_URL: {{ .Values.frontend.env.apiBaseUrl | quote }}
{{- end }}
```

### Step 9: Create `NOTES.txt`

```
# helm/todo-chatbot/templates/NOTES.txt
Thank you for installing {{ .Chart.Name }}!

Release: {{ .Release.Name }}
Chart:   {{ .Chart.Name }}-{{ .Chart.Version }}

{{- if .Values.frontend.enabled }}

== Frontend ==
{{- if eq .Values.frontend.service.type "NodePort" }}
  Access the frontend via Minikube:
    minikube service todo-frontend --url
{{- else }}
  Frontend is available at:
    http://todo-frontend:{{ .Values.frontend.service.port }}
{{- end }}
{{- end }}

{{- if .Values.backend.enabled }}

== Backend ==
{{- if eq .Values.backend.service.type "NodePort" }}
  Access the backend via Minikube:
    minikube service todo-backend --url
{{- else }}
  Backend API is available at:
    http://todo-backend:{{ .Values.backend.service.port }}
{{- end }}
{{- end }}

== Quick Validation ==
  kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot
  kubectl wait --for=condition=Ready pod -l app.kubernetes.io/part-of=todo-chatbot --timeout=120s
```

### Step 10: Create Test Connection Template

```yaml
# helm/todo-chatbot/templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "todo-chatbot.fullname" . }}-test"
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
    {{- if .Values.frontend.enabled }}
    - name: test-frontend
      image: busybox:1.36
      command: ['wget', '--spider', '--timeout=5', 'http://todo-frontend:{{ .Values.frontend.service.port }}/']
    {{- end }}
    {{- if .Values.backend.enabled }}
    - name: test-backend
      image: busybox:1.36
      command: ['wget', '--spider', '--timeout=5', 'http://todo-backend:{{ .Values.backend.service.port }}/docs']
    {{- end }}
```

### Step 11: Create `.helmignore`

```
# helm/todo-chatbot/.helmignore
.git
.gitignore
.vscode
.idea
*.md
!README.md
```

## Helm Template Syntax Reference

Quick reference for patterns used throughout this chart:

| Pattern | Purpose | Example |
|---------|---------|---------|
| `{{ include "name" . }}` | Call a named template | `{{ include "todo-chatbot.frontend.labels" . \| nindent 4 }}` |
| `{{ .Values.x.y }}` | Read from values.yaml | `{{ .Values.frontend.replicaCount }}` |
| `{{ toYaml .Values.x \| nindent N }}` | Inline a YAML block | `{{ toYaml .Values.frontend.resources \| nindent 12 }}` |
| `{{ .Chart.Name }}` | Chart metadata | `todo-chatbot` |
| `{{ .Release.Name }}` | Helm release name | User-specified at install |
| `{{- if .Values.x }}` | Conditional block | `{{- if .Values.frontend.enabled }}` |
| `{{ .Values.x \| quote }}` | Quote a string value | `{{ .Values.backend.config.corsOrigins \| quote }}` |
| `{{ default "fallback" .Values.x }}` | Default value | `{{ .Values.frontend.image.tag \| default .Chart.AppVersion }}` |

## Install and Validate Workflow

```bash
# 1. Point Docker to Minikube
eval $(minikube docker-env)

# 2. Build local images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# 3. Lint the chart
helm lint helm/todo-chatbot

# 4. Dry-run to preview rendered manifests
helm template my-todo helm/todo-chatbot

# 5. Install the chart
helm install my-todo helm/todo-chatbot \
  --set backend.secrets.databaseUrl="postgresql://..." \
  --set backend.secrets.betterAuthSecret="your-secret" \
  --set backend.secrets.openaiApiKey="sk-..."

# 6. Validate pods
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot
kubectl wait --for=condition=Ready pod \
  -l app.kubernetes.io/part-of=todo-chatbot --timeout=120s

# 7. Access services
minikube service todo-frontend --url
minikube service todo-backend --url

# 8. Run Helm tests
helm test my-todo

# 9. Upgrade (after changes)
helm upgrade my-todo helm/todo-chatbot

# 10. Uninstall
helm uninstall my-todo
```

## Key Rules

### values.yaml (NON-NEGOTIABLE)
- Every value MUST have a descriptive YAML comment.
- Secret values MUST default to `CHANGE_ME` and MUST NOT contain real credentials.
- Real secrets MUST be passed via `--set` flags or a separate values file excluded from Git.
- All resources MUST have `requests` and `limits` defaults.

### Templates
- All labels MUST be generated via `_helpers.tpl` named templates, not hardcoded.
- Deployment `spec.selector.matchLabels` MUST use the selector labels helper.
- Service `spec.selector` MUST use the same selector labels helper as the Deployment.
- Use `toYaml | nindent` for all block values (resources, securityContext, etc.).
- Use `| quote` for all string values from `values.yaml` injected into ConfigMaps/Secrets.
- All optional resources MUST be wrapped in `{{- if .Values.<component>.enabled }}`.

### Chart.yaml
- `apiVersion` MUST be `v2` (Helm 3).
- `version` MUST follow semantic versioning and increment on every chart change.
- `appVersion` tracks the application version, independent of chart version.

## Validation Checklist

Before finalizing any chart modification, verify:

- [ ] `helm lint helm/todo-chatbot` passes without errors or warnings
- [ ] `helm template my-todo helm/todo-chatbot` renders valid YAML
- [ ] Every `{{ .Values.* }}` reference has a corresponding entry in `values.yaml`
- [ ] All `values.yaml` entries have descriptive YAML comments
- [ ] Labels in Deployment pod template match Service selector
- [ ] `toYaml | nindent` indentation produces correctly nested YAML
- [ ] Secret values default to `CHANGE_ME` placeholders
- [ ] Both liveness and readiness probes defined on all Deployments
- [ ] Resource requests and limits set on all containers
- [ ] Security contexts applied (runAsNonRoot, allowPrivilegeEscalation: false)
- [ ] `imagePullPolicy: Never` set for Minikube local image workflow
- [ ] `NOTES.txt` provides accurate post-install access instructions
- [ ] Test connection template validates service reachability
- [ ] Chart version in `Chart.yaml` incremented if modifying an existing chart

## Dependencies

- Helm 3.12+
- Minikube 1.30+ with Kubernetes 1.28+
- Docker images built via the `todo-docker` skill
- Raw manifests from the `todo-kubernetes` skill serve as reference
