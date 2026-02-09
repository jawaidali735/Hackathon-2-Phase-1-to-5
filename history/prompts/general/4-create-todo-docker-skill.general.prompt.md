---
id: 4
title: Create Todo Docker Skill
stage: general
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: architect
command: /sp.constitution (follow-up)
labels: ["docker", "skill", "phase-4", "containerization"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/todo-docker/SKILL.md
tests:
  - none
---

## Prompt

Create a Claude Code Skill file for Docker containerization.

Generate a SKILL.md for the Skill named "todo-docker" that:
- Teaches Claude how to generate optimized Dockerfiles for Todo Chatbot frontend (Next.js) and backend (FastAPI).
- Includes clear step-by-step instructions and examples.
- Explains when Claude should use this Skill (trigger words like "Dockerfile", "containerize", "build image").
- Follows the official Claude Code SKILL.md format with YAML frontmatter (name, description) and markdown body.

Place the generated content in proper SKILL.md format.

## Response snapshot

Created `.claude/skills/todo-docker/SKILL.md` following the established SKILL.md pattern (YAML frontmatter with name + description, markdown body). The skill covers:

- **When to Use**: Trigger words (Dockerfile, containerize, build image, dockerize, container, multi-stage build)
- **Project Context**: Frontend (Next.js 16+, npm, port 3000) and Backend (FastAPI, uv, port 8000) specifics
- **Frontend Dockerfile**: 3-stage multi-stage build (deps → builder → runner) with node:22-alpine, standalone output, non-root nextjs user, HEALTHCHECK
- **Backend Dockerfile**: 2-stage build using uv (per constitution mandate), python:3.11-slim, non-root appuser, HEALTHCHECK
- **.dockerignore templates**: For both frontend and backend
- **Environment variables table**: All required runtime env vars documented
- **Optimization checklist**: 12-point verification list
- **Kubernetes integration notes**: Minikube docker-env, imagePullPolicy, health probe alignment
- **Verification commands**: Build and smoke-test commands

## Outcome

- Impact: New skill file enables Claude to generate project-specific Dockerfiles consistently
- Tests: N/A (skill documentation)
- Files: .claude/skills/todo-docker/SKILL.md
- Next prompts: Generate actual Dockerfiles using the skill, create Helm chart skill
- Reflection: Followed existing skill format from integrate-openai-agents and mcp-server skills; included project-specific details from constitution Phase 4

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review PASS - format matches existing skills, content aligns with constitution
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
