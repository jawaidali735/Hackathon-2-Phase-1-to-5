---
name: todo-ai-ops
description: "Use this skill when generating kubectl-ai style diagnostics prompts, performing pod health checks, analyzing logs, assessing scaling, or debugging Kubernetes issues for the Todo Chatbot cluster. Trigger terms: kubectl-ai, check pods, analyze cluster, pod health, scaling, log analysis, debug deployment, cluster diagnostics."
---

# Todo AI-Assisted DevOps Skill

This skill provides structured guidance for generating kubectl-ai style diagnostic prompts and executing AI-assisted Kubernetes operations for the Todo Chatbot application running on Minikube.

## Purpose

Generate AI-driven DevOps diagnostics that:
1. Check pod health, readiness, and restart patterns across the Todo Chatbot stack
2. Analyze logs for errors, warnings, and anomalies in frontend and backend containers
3. Assess resource usage and provide scaling recommendations
4. Diagnose deployment failures with progressive, narrowing investigation
5. Produce runnable kubectl commands alongside natural-language kubectl-ai prompts
6. Align with the constitution's Phase 4 AI Observability & Ops Insights principle

## When to Use

Use this skill when:
- Checking overall health of Todo Chatbot pods after deployment
- Investigating pod crashes, restarts, or readiness failures
- Analyzing container logs for error patterns
- Assessing CPU/memory usage and scaling needs
- Debugging networking or service connectivity issues
- Generating a diagnostic report for team visibility
- Producing kubectl-ai prompts for repeatable operations

**Trigger terms**: kubectl-ai, check pods, analyze cluster, pod health, scaling, log analysis, debug deployment, cluster diagnostics, OOMKill, CrashLoopBackOff, resource usage, pod restarts

## Prompt Format Convention

Every diagnostic prompt uses this structured format:

```
### [Category]: [Brief Description]

**kubectl-ai prompt:** `[Natural language prompt for kubectl-ai]`
**kubectl equivalent:** `[Runnable kubectl command]`
**Safety:** [Safe / Caution / Destructive]
**Purpose:** [What this investigates]
**Look for:** [What indicates a problem in the output]
**Follow-up:** [Next prompt if issues found]
```

Safety annotations:
- **Safe** — read-only, no side effects
- **Caution** — may affect running workloads if misused
- **Destructive** — requires explicit confirmation before running

## Diagnostic Category 1: Pod Health Checks

Use these prompts after any deployment or when investigating instability.

### 1.1 Overview: All Todo Chatbot Pods

**kubectl-ai prompt:** `Show me all pods with label part-of=todo-chatbot and their status, restarts, and age`

**kubectl equivalent:**
```bash
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot -o wide
```

**Safety:** Safe

**Purpose:** Get a quick snapshot of all Todo Chatbot pods.

**Look for:** Any pod not in `Running` status or with `READY` less than `1/1`.

**Follow-up:** If a pod is unhealthy, run prompt 1.3 on that specific pod.

---

### 1.2 Readiness and Conditions

**kubectl-ai prompt:** `Show me the conditions (Ready, Initialized, ContainersReady, PodScheduled) for all todo-chatbot pods`

**kubectl equivalent:**
```bash
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .status.conditions[*]}{.type}={.status}{" "}{end}{"\n"}{end}'
```

**Safety:** Safe

**Purpose:** Identify which readiness condition is blocking a pod from becoming Ready.

**Look for:** Any condition showing `False`. Pay special attention to `ContainersReady=False` (probe failure) and `PodScheduled=False` (scheduling issue).

**Follow-up:** If `ContainersReady=False`, run prompt 1.4 to check probe status.

---

### 1.3 Pod Detail and Events

**kubectl-ai prompt:** `Describe pod {pod-name} and show recent events, especially warnings`

**kubectl equivalent:**
```bash
kubectl describe pod {pod-name}
```

**Safety:** Safe

**Purpose:** Deep inspection of a single pod's state, events, and configuration.

**Look for:** `Warning` events, `Back-off restarting failed container`, `Liveness probe failed`, `Readiness probe failed`, `FailedScheduling`.

**Follow-up:** If probe failures, run prompt 1.4. If image issues, run prompt 3.1.

---

### 1.4 Probe Status and Restart History

**kubectl-ai prompt:** `Show restart counts and last termination reasons for all todo-chatbot pods`

**kubectl equivalent:**
```bash
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot \
  -o custom-columns=NAME:.metadata.name,RESTARTS:.status.containerStatuses[0].restartCount,LAST_STATE:.status.containerStatuses[0].lastState.terminated.reason,EXIT_CODE:.status.containerStatuses[0].lastState.terminated.exitCode
```

**Safety:** Safe

**Purpose:** Identify pods that are crash-looping and the reason for termination.

**Look for:** `RESTARTS > 0`, termination reasons like `OOMKilled` (exit code 137), `Error` (exit code 1), or `Completed` (exit code 0 but shouldn't have exited).

**Follow-up:** If `OOMKilled`, run prompt 2.2 for memory analysis. If `Error`, run prompt 3.2 for log extraction.

---

### 1.5 Pods with Excessive Restarts

**kubectl-ai prompt:** `Show me all pods in the cluster that have restarted more than 3 times`

**kubectl equivalent:**
```bash
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot \
  --sort-by='.status.containerStatuses[0].restartCount' \
  -o custom-columns=NAME:.metadata.name,RESTARTS:.status.containerStatuses[0].restartCount,STATUS:.status.phase
```

**Safety:** Safe

**Purpose:** Quickly identify unstable pods that may need investigation.

**Look for:** Any pod with restarts > 0. Pods with restarts > 5 are critical.

**Follow-up:** Run prompt 3.2 for the most-restarted pod.

## Diagnostic Category 2: Resource Usage and Scaling

Use these prompts to assess whether pods are right-sized and if scaling is needed.

### 2.1 Current Resource Usage

**kubectl-ai prompt:** `Show me CPU and memory usage for all todo-chatbot pods compared to their requests and limits`

**kubectl equivalent:**
```bash
# Requires metrics-server: minikube addons enable metrics-server
kubectl top pods -l app.kubernetes.io/part-of=todo-chatbot
```

**Safety:** Safe

**Purpose:** Compare actual resource consumption against configured requests/limits.

**Look for:** CPU or memory usage consistently above 80% of limits (overloaded) or below 10% of requests (over-provisioned).

**Follow-up:** If overloaded, run prompt 2.3 for scaling recommendation.

---

### 2.2 Memory Pressure Analysis

**kubectl-ai prompt:** `Show memory usage, limits, and OOMKill history for todo-chatbot containers`

**kubectl equivalent:**
```bash
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.resources.limits.memory}{"\t"}{end}{range .status.containerStatuses[*]}{.lastState.terminated.reason}{end}{"\n"}{end}'
```

**Safety:** Safe

**Purpose:** Identify containers at risk of or already hit by OOMKill.

**Look for:** `OOMKilled` in termination reasons. Memory limits that are too tight for the workload.

**Follow-up:** Increase memory limits in `values.yaml` and redeploy.

---

### 2.3 Scaling Recommendation

**kubectl-ai prompt:** `Based on current resource usage, recommend replica counts and resource limits for the todo-chatbot frontend and backend`

**kubectl equivalent:**
```bash
# Collect data for manual analysis:
echo "=== Node capacity ===" && kubectl top nodes
echo "=== Pod usage ===" && kubectl top pods -l app.kubernetes.io/part-of=todo-chatbot
echo "=== Current requests/limits ===" && kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}  CPU req: {.spec.containers[0].resources.requests.cpu}{"\n"}  CPU lim: {.spec.containers[0].resources.limits.cpu}{"\n"}  Mem req: {.spec.containers[0].resources.requests.memory}{"\n"}  Mem lim: {.spec.containers[0].resources.limits.memory}{"\n\n"}{end}'
```

**Safety:** Safe

**Purpose:** Generate a data-driven scaling recommendation.

**Look for:** Usage-to-limit ratios. Recommended guidelines for Minikube:

| Service | Replicas | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|----------|-------------|-----------|----------------|--------------|
| Frontend | 1 | 100m | 500m | 128Mi | 512Mi |
| Backend | 1 | 100m | 500m | 128Mi | 512Mi |
| Backend (with AI agent active) | 1 | 200m | 1000m | 256Mi | 1Gi |

**Follow-up:** Update `values.yaml` with recommended values and run `helm upgrade`.

---

### 2.4 Node Resource Availability

**kubectl-ai prompt:** `Show me the Minikube node's total capacity, allocatable resources, and current usage`

**kubectl equivalent:**
```bash
kubectl describe node minikube | grep -A 6 "Allocated resources"
kubectl top nodes
```

**Safety:** Safe

**Purpose:** Check whether the Minikube node has headroom for current or additional pods.

**Look for:** CPU or memory allocation above 85% of allocatable capacity.

**Follow-up:** If constrained, consider stopping Minikube and restarting with more resources: `minikube start --cpus=4 --memory=8192`.

## Diagnostic Category 3: Log Analysis and Debugging

Use these prompts when pods are crashing, returning errors, or behaving unexpectedly.

### 3.1 Image and Pull Issues

**kubectl-ai prompt:** `Show me pods with ImagePullBackOff or ErrImageNeverPull errors in the todo-chatbot namespace`

**kubectl equivalent:**
```bash
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot \
  --field-selector=status.phase!=Running \
  -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,REASON:.status.containerStatuses[0].state.waiting.reason
```

**Safety:** Safe

**Purpose:** Detect image availability issues (common when `minikube docker-env` was not set before building).

**Look for:** `ImagePullBackOff` or `ErrImageNeverPull` in the REASON column.

**Follow-up:** Rebuild images inside Minikube's Docker daemon:
```bash
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
kubectl delete pod -l app.kubernetes.io/part-of=todo-chatbot
```

---

### 3.2 Error Log Extraction

**kubectl-ai prompt:** `Extract error-level logs from the todo-backend pod in the last 15 minutes`

**kubectl equivalent:**
```bash
kubectl logs -l app.kubernetes.io/name=todo-backend --since=15m | grep -iE "error|exception|traceback|fatal"
```

**Safety:** Safe

**Purpose:** Find application-level errors that explain crashes or misbehavior.

**Look for:** Python tracebacks, database connection errors, missing environment variables, authentication failures.

**Follow-up:** If database errors, check Secret values. If auth errors, verify `BETTER_AUTH_SECRET` matches frontend.

---

### 3.3 Frontend Log Extraction

**kubectl-ai prompt:** `Extract warning and error logs from the todo-frontend pod in the last 15 minutes`

**kubectl equivalent:**
```bash
kubectl logs -l app.kubernetes.io/name=todo-frontend --since=15m | grep -iE "error|warn|ERR_"
```

**Safety:** Safe

**Purpose:** Find Next.js runtime errors or connection failures to the backend API.

**Look for:** `ECONNREFUSED` (backend unreachable), `fetch failed`, hydration errors, build-time env var issues.

**Follow-up:** If backend unreachable, verify the `NEXT_PUBLIC_API_BASE_URL` ConfigMap value matches the backend service name (`http://todo-backend:8000`).

---

### 3.4 Crashed Container Logs

**kubectl-ai prompt:** `Show me the logs from the previously crashed container in pod {pod-name}`

**kubectl equivalent:**
```bash
kubectl logs {pod-name} --previous
```

**Safety:** Safe

**Purpose:** Retrieve logs from a container that has already crashed and restarted (current logs may be from the new instance).

**Look for:** The final error or stack trace before exit.

**Follow-up:** Address the root cause (missing env, port conflict, unhandled exception), then redeploy.

---

### 3.5 Event Timeline

**kubectl-ai prompt:** `Show me all Kubernetes events for the todo-chatbot workloads in chronological order, highlighting warnings`

**kubectl equivalent:**
```bash
kubectl get events --sort-by='.lastTimestamp' \
  --field-selector involvedObject.labels.app.kubernetes.io/part-of=todo-chatbot 2>/dev/null \
  || kubectl get events --sort-by='.lastTimestamp' | grep -E "todo-frontend|todo-backend"
```

**Safety:** Safe

**Purpose:** Build a chronological timeline of cluster events to correlate failures.

**Look for:** `Warning` type events. Sequence: `FailedScheduling` → `Pulling` → `BackOff` indicates image or resource issues.

**Follow-up:** Use timestamps to correlate with application logs from prompt 3.2.

---

### 3.6 Service Connectivity Check

**kubectl-ai prompt:** `Verify that the todo-frontend service can reach the todo-backend service on port 8000`

**kubectl equivalent:**
```bash
kubectl run connectivity-test --image=busybox:1.36 --rm -it --restart=Never -- \
  wget --spider --timeout=5 http://todo-backend:8000/docs
```

**Safety:** Caution (creates a temporary pod)

**Purpose:** Test internal DNS resolution and service connectivity between frontend and backend.

**Look for:** `200 OK` or `remote file exists` = success. `bad address` = DNS failure. `Connection refused` = backend not running or wrong port.

**Follow-up:** If DNS failure, check service name and endpoints: `kubectl get endpoints todo-backend`.

## Diagnostic Playbooks

### Playbook A: Post-Deployment Health Check

Run after every `helm install` or `helm upgrade`:

1. Prompt 1.1 — Overview of all pods
2. Prompt 1.2 — Readiness conditions
3. Prompt 2.1 — Resource usage snapshot
4. Prompt 3.6 — Service connectivity
5. Produce a deployment report (see `todo-minikube` skill for template)

### Playbook B: Crash Investigation

Run when a pod is in `CrashLoopBackOff`:

1. Prompt 1.4 — Restart count and termination reason
2. Prompt 3.4 — Previous container logs
3. Prompt 1.3 — Pod describe for events
4. Prompt 3.5 — Event timeline correlation
5. If `OOMKilled` → Prompt 2.2 for memory analysis
6. If application error → Prompt 3.2 for error log extraction

### Playbook C: Scaling Assessment

Run periodically or before increasing load:

1. Prompt 2.1 — Current resource usage
2. Prompt 2.4 — Node capacity
3. Prompt 2.3 — Scaling recommendation
4. Update `values.yaml` with recommendations
5. Run `helm upgrade` and validate with Playbook A

### Playbook D: Connectivity Debugging

Run when services return errors or are unreachable:

1. Prompt 1.1 — Pod status (are pods running?)
2. Prompt 3.6 — Service connectivity test
3. `kubectl get endpoints todo-frontend todo-backend` — endpoints populated?
4. Prompt 3.2 / 3.3 — Application logs for connection errors
5. Verify ConfigMap values match service names

## Scaling Guidelines for Todo Chatbot

Document these in project specs per constitution requirement:

| Environment | Frontend Replicas | Backend Replicas | Backend CPU Limit | Backend Memory Limit |
|-------------|-------------------|------------------|-------------------|----------------------|
| Minikube (dev) | 1 | 1 | 500m | 512Mi |
| Minikube (AI agent active) | 1 | 1 | 1000m | 1Gi |
| Production (light load) | 2 | 2 | 500m | 512Mi |
| Production (moderate load) | 3 | 3 | 1000m | 1Gi |

**Resource quota recommendation for Minikube**: Allocate at least 2 CPUs and 4GB memory to the Minikube VM.

## Key Rules

### Prompt Generation (NON-NEGOTIABLE)
- ALWAYS annotate every prompt with a safety level (Safe / Caution / Destructive).
- ALWAYS provide both a kubectl-ai natural language prompt AND a runnable kubectl equivalent.
- ALWAYS order prompts from broad overview to specific investigation.
- NEVER generate prompts that delete resources or drain nodes without explicit user request.
- ALWAYS use `--dry-run` flags on any mutating kubectl-ai prompt.

### Diagnostics
- ALWAYS run read-only commands first before suggesting any changes.
- ALWAYS check pod logs before recommending a fix.
- ALWAYS correlate events with logs for accurate root-cause analysis.
- NEVER guess at a root cause without evidence from kubectl output.

### Documentation
- All diagnostic prompts used during operations MUST be saved as PHRs in `history/prompts/`.
- Scaling recommendations MUST be documented in the project specs per constitution requirement.

## Validation Checklist

Before completing a diagnostics session, verify:

- [ ] All pods checked and health status reported
- [ ] Resource usage assessed against configured limits
- [ ] Logs reviewed for errors and warnings
- [ ] Service connectivity verified
- [ ] Event timeline reviewed for warnings
- [ ] Findings summarized with evidence (not speculation)
- [ ] Recommended actions listed with specific commands
- [ ] Safety annotations present on all generated prompts
- [ ] Scaling guidelines documented if assessment was performed

## Dependencies

- Minikube with metrics-server addon: `minikube addons enable metrics-server`
- kubectl CLI matching the cluster version
- Todo Chatbot deployed via the `todo-helm` or `todo-kubernetes` skill
- Deployment validated via the `todo-minikube` skill
