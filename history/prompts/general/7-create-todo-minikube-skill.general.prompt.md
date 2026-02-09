---
id: 7
title: Create Todo Minikube Skill
stage: general
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: architect
command: manual request
labels: ["minikube", "skill", "phase-4", "kubernetes", "deployment"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/todo-minikube/SKILL.md
tests:
  - none
---

## Prompt

Create a Claude Code Skill file for Minikube deployment tasks.

Generate a SKILL.md for the Skill named "todo-minikube" that:
- Teaches Claude what steps are needed to deploy to Minikube (start cluster, apply manifests or Helm chart).
- Includes example commands, readiness checks, service access instructions.
- Mentions trigger terms like "Minikube deploy", "Minikube start", "service access".
- Outputs a valid SKILL.md with name, description, instructions, and examples.

## Response snapshot

Created `.claude/skills/todo-minikube/SKILL.md` with a complete 5-phase deployment workflow. The skill covers:

- **Trigger terms**: Minikube deploy, Minikube start, service access, pod status, helm install, kubectl get pods, deployment validation, pod logs, rollback, minikube service
- **Prerequisites table**: Minikube 1.30+, kubectl 1.28+, Helm 3.12+, Docker 20.10+ with check commands
- **5-phase deployment workflow**: Pre-Flight Checks → Build Docker Images → Deploy with Helm (install/upgrade/raw manifests) → Validation Checks (8 commands) → Access Services (NodePort URLs + smoke tests)
- **Deployment report template**: Structured table format for pods, services, health checks, issues, and access instructions
- **Troubleshooting guide**: 5 failure scenarios (ImagePullBackOff, CrashLoopBackOff, Pending Pods, Service Not Accessible, Helm Timeout) each with symptom, diagnosis commands, common causes, and fixes
- **Lifecycle commands reference**: 17-row table covering start/stop/delete/deploy/rollback/logs/dashboard
- **Key rules**: 4 categories (Pre-Flight, Deployment, Validation, Troubleshooting) with NON-NEGOTIABLE requirements
- **13-point validation checklist**: From Minikube status through helm test

## Outcome

- Impact: New skill enables consistent Minikube deployment and validation for Todo Chatbot
- Tests: N/A (skill documentation)
- Files: .claude/skills/todo-minikube/SKILL.md
- Next prompts: Execute actual deployment to Minikube, create AI DevOps diagnostics skill
- Reflection: Combined minikube-deploy-agent workflow with constitution Phase 4 validation requirements; cross-references todo-docker, todo-helm, and todo-kubernetes skills

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review PASS - format matches existing skills, workflow aligns with minikube-deploy-agent phases
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
