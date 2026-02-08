---
id: 1
title: AI Chatbot Spec Creation
stage: spec
date: 2026-02-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-ai-chat-agent
branch: 004-ai-chat-agent
user: developer
command: /sp.specify
labels: ["chatbot", "cohere", "mcp-tools", "phase-3"]
links:
  spec: specs/004-ai-chat-agent/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-ai-chat-agent/spec.md
  - specs/004-ai-chat-agent/checklists/requirements.md
tests:
  - N/A (specification phase)
---

## Prompt

AI Todo Chatbot Integration for The Evolution of Todo - Phase III: Full-Stack Web Application

Target audience: Hackathon judges seeking groundbreaking, production-grade AI integrations; developers building flagship intelligent productivity apps; and AI agents delivering flawless execution via Claude Code.

Focus: Define exhaustive, zero-ambiguity, flagship-level specifications for integrating a powerful, natural-language AI Todo Chatbot into the existing full-stack application (Next.js frontend + FastAPI backend + Neon DB + Better Auth).

The chatbot must have full control over all core task operations (add, delete, update, mark complete, list) and user information (e.g., "Who am I?" -> reply with logged-in email), using Cohere API (not OpenAI/Gemini) for all AI reasoning and tool calling.

Adapt agent-style logic from the provided OpenAI Agents SDK example to Cohere's chat/completions endpoint.

The chatbot UI must be beautifully integrated into the existing premium frontend with a floating chatbot icon/button that opens a stunning, responsive chat panel — maintaining visual harmony with the flagship UI.

Key requirements:
- 6 MCP-style tools: add_task, delete_task, update_task, complete_task, list_tasks, get_current_user
- Cohere API for all AI reasoning (no OpenAI/Gemini)
- Stateless backend with conversation persistence in Neon DB
- Beautiful glassmorphic UI with floating chat button
- Complete multi-user isolation via JWT

## Response snapshot

Created comprehensive specification for AI Todo Chatbot Integration (Phase III) with:
- 4 user stories covering natural language task management, intelligent conversation, beautiful UI, and security
- 12 functional requirements with clear acceptance criteria
- 8 measurable success criteria (technology-agnostic)
- Complete MCP-style tool specifications for all 6 tools with parameters and return types
- Database schema extensions for Conversation and Message tables
- Backend chat endpoint specification (POST /api/v1/{user_id}/chat)
- Frontend UI component specifications (floating button, chat panel, message bubbles)
- Natural language examples mapping user intents to tool calls
- Security and error handling patterns
- TypeScript types for frontend integration

## Outcome

- ✅ Impact: Complete Phase III specification created enabling AI chatbot implementation
- 🧪 Tests: N/A (specification phase - tests defined in acceptance criteria)
- 📁 Files: 2 files created (spec.md, requirements.md checklist)
- 🔁 Next prompts: /sp.plan to create implementation plan, /sp.tasks to generate tasks
- 🧠 Reflection: Spec adapts OpenAI Agents SDK pattern to Cohere API with prompt engineering approach for tool calling

## Evaluation notes (flywheel)

- Failure modes observed: None - all checklist items passed validation
- Graders run and results (PASS/FAIL): Requirements checklist PASS (all items checked)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate Cohere API tool calling approach during implementation
