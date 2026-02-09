---
id: 6
title: Create Todo Helm Skill
stage: general
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: architect
command: manual request
labels: ["helm", "skill", "phase-4", "kubernetes", "charts"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/todo-helm/SKILL.md
tests:
  - none
---

## Prompt

Create a Claude Code Skill file for Helm chart scaffolding.

Generate a SKILL.md for the Skill named "todo-helm" that:
- Teaches Claude how to scaffold a Helm chart structure with Chart.yaml, values.yaml, and templates.
- Shows how to template Deployments and Services using Helm templating syntax.
- Mentions trigger phrases like "Helm chart", "values.yaml", "templates".
- Outputs the complete SKILL.md with proper YAML frontmatter and detailed markdown instructions.

## Response snapshot

Created `.claude/skills/todo-helm/SKILL.md` with comprehensive Helm chart scaffolding guidance. The skill covers:

- **Trigger phrases**: Helm chart, values.yaml, templates, helm install, chart scaffold, Helm template, helm lint, helm upgrade, Chart.yaml, _helpers.tpl
- **Chart structure**: Full directory tree at `helm/todo-chatbot/` with Chart.yaml, values.yaml, .helmignore, _helpers.tpl, NOTES.txt, and per-component template directories
- **11-step scaffolding guide**: Chart.yaml → values.yaml → _helpers.tpl → frontend Deployment → frontend Service → backend Deployment → backend Service/ConfigMap/Secret → frontend ConfigMap → NOTES.txt → test-connection → .helmignore
- **values.yaml**: Fully commented with every parameter documented, grouped by component (frontend, backend, shared security context)
- **_helpers.tpl**: 7 named templates (name, fullname, chart, common labels, frontend labels/selectors, backend labels/selectors)
- **Template syntax reference table**: 8 common Helm patterns with examples
- **Install workflow**: 10-step bash sequence from docker-env through helm test
- **Key rules**: 3 categories (values.yaml, templates, Chart.yaml) with NON-NEGOTIABLE requirements
- **14-point validation checklist**: From helm lint through chart version increment

## Outcome

- Impact: New skill enables consistent Helm chart scaffolding for Todo Chatbot
- Tests: N/A (skill documentation)
- Files: .claude/skills/todo-helm/SKILL.md
- Next prompts: Scaffold actual Helm chart using the skill, deploy to Minikube
- Reflection: Combined helm-chart-agent patterns with constitution Phase 4 requirements; cross-references todo-docker and todo-kubernetes skills

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review PASS - format matches existing skills, content aligns with helm-chart-agent and constitution
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
