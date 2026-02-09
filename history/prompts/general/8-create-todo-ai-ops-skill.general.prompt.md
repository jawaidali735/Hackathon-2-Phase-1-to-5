---
id: 8
title: Create Todo AI Ops Skill
stage: general
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: architect
command: manual request
labels: ["ai-ops", "skill", "phase-4", "kubernetes", "diagnostics", "kubectl-ai"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/todo-ai-ops/SKILL.md
tests:
  - none
---

## Prompt

Create a Claude Code Skill file for AI-assisted DevOps tasks.

Generate a SKILL.md for the Skill named "todo-ai-ops" that:
- Teaches Claude how to generate kubectl-ai style troubleshooting and diagnostics prompts for Kubernetes.
- Includes examples of health checks, logs analysis, scaling suggestions.
- Mentions trigger terms like "kubectl-ai", "check pods", "analyze cluster".
- Outputs the complete SKILL.md following best practices with frontmatter and markdown instructions.

## Response snapshot

Created `.claude/skills/todo-ai-ops/SKILL.md` with comprehensive AI-assisted DevOps diagnostics guidance. The skill covers:

- **Trigger terms**: kubectl-ai, check pods, analyze cluster, pod health, scaling, log analysis, debug deployment, cluster diagnostics, OOMKill, CrashLoopBackOff, resource usage, pod restarts
- **Structured prompt format**: Every prompt includes kubectl-ai natural language, runnable kubectl equivalent, safety annotation, purpose, what to look for, and follow-up
- **3 diagnostic categories with 15 prompts total**:
  - Pod Health Checks (5 prompts): overview, readiness conditions, pod detail, probe/restart history, excessive restarts
  - Resource Usage & Scaling (4 prompts): current usage, memory pressure, scaling recommendation with guidelines table, node capacity
  - Log Analysis & Debugging (6 prompts): image pull issues, backend error logs, frontend logs, crashed container logs, event timeline, service connectivity
- **4 diagnostic playbooks**: Post-Deployment Health Check, Crash Investigation, Scaling Assessment, Connectivity Debugging
- **Scaling guidelines table**: Minikube dev, Minikube with AI agent, production light, production moderate
- **Key rules**: Prompt generation (safety annotations, dual format, broad-to-specific), diagnostics (read-only first, evidence-based), documentation (PHR + scaling docs)
- **9-point validation checklist**

## Outcome

- Impact: New skill enables AI-driven Kubernetes diagnostics for Todo Chatbot
- Tests: N/A (skill documentation)
- Files: .claude/skills/todo-ai-ops/SKILL.md
- Next prompts: Execute actual diagnostics against a running Minikube deployment
- Reflection: Combined ai-ops-agent patterns with constitution Phase 4 AI Observability requirements; all prompts include both kubectl-ai and kubectl equivalents for maximum utility

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review PASS - format matches existing skills, content aligns with ai-ops-agent and constitution
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
