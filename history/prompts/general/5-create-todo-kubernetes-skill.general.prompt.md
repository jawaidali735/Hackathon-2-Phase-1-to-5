---
id: 5
title: Create Todo Kubernetes Skill
stage: general
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: architect
command: manual request
labels: ["kubernetes", "skill", "phase-4", "minikube", "manifests"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/todo-kubernetes/SKILL.md
tests:
  - none
---

## Prompt

Create a Claude Code Skill file for Kubernetes manifests.

Generate a SKILL.md for the Skill named "todo-kubernetes" that:
- Teaches Claude how to generate Deployment and Service YAML for Kubernetes (Minikube).
- Includes instructions for labels, ports, probes, and best practices.
- Mentions trigger terms like "Kubernetes", "deployment YAML", "service YAML", "Minikube".
- Outputs the content in valid SKILL.md format with name, description, instructions, and examples.

## Response snapshot

Created `.claude/skills/todo-kubernetes/SKILL.md` following the established SKILL.md pattern. The skill covers:

- **Trigger words**: Kubernetes, deployment YAML, service YAML, Minikube, k8s manifest, pod, kubectl apply, ConfigMap, Secret, liveness probe, readiness probe
- **Project context**: Frontend (port 3000, health `/`) and Backend (port 8000, health `/docs`) service details
- **Output directory**: `k8s/` with descriptive filenames per component
- **Labeling convention**: `app.kubernetes.io/name`, `app.kubernetes.io/component`, `app.kubernetes.io/part-of: todo-chatbot`
- **Frontend manifests**: Deployment (3-label, probes, security context, resource limits, imagePullPolicy: Never) + NodePort Service
- **Backend manifests**: ConfigMap (CORS, JWT config) + Secret (DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY with CHANGE_ME placeholders) + Deployment (envFrom refs, probes, security context) + NodePort Service
- **Configuration reference tables**: Resource defaults, probe defaults, service types by environment
- **Key rules**: 6 categories (Labels, Ports, Probes, Security, Minikube-specific) with NON-NEGOTIABLE requirements
- **Deployment workflow**: 5-step bash workflow (docker-env, build, apply, validate, access)
- **Validation checklist**: 16-point verification list

## Outcome

- Impact: New skill file enables consistent Kubernetes manifest generation for Todo Chatbot
- Tests: N/A (skill documentation)
- Files: .claude/skills/todo-kubernetes/SKILL.md
- Next prompts: Generate actual k8s manifests, create Helm chart skill
- Reflection: Aligned with k8s-manifest-agent conventions and constitution Phase 4 requirements; included Minikube-specific defaults

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review PASS - format matches existing skills, content aligns with constitution and k8s-manifest-agent
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
