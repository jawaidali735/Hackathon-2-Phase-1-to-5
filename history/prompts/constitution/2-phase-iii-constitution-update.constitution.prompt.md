---
id: 2
title: Phase-III Constitution Update
stage: constitution
date: 2026-02-05
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: system
command: /sp.constitution
labels: ["phase-3", "ai-agent", "mcp-tools", "openai-sdk", "chatbot"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

(Phase-III Update)

## Project Extension: AI-Powered Todo Chatbot

### Core additions:
- Agent-first design using OpenAI Agents SDK
- Stateless chat and tool execution
- All task actions executed only via MCP tools
- Clear separation: UI → Agent → MCP Tools → Database

---

## Key standards:
- Agents must not access the database directly
- MCP tools must be stateless and schema-defined
- Conversation context rebuilt from database each request
- All AI actions traced and persisted
- Phase-II auth and user isolation rules remain enforced

---

## Constraints:
- Use OpenAI Agents SDK and Official MCP SDK
- Stateless FastAPI chat endpoint
- Persist conversations and messages in Neon PostgreSQL
- No manual coding; Claude Code only

---

## Success criteria:
- Users manage todos via natural language
- Agent correctly invokes MCP tools
- Conversation resumes after restart
- System remains secure and stateless

## Response snapshot

Constitution successfully updated from version 5.0.0 (corrected) to version 1.2.0 with Phase-III AI-Powered Todo Chatbot requirements.

**Key Changes:**
- **Version Correction:** Fixed version from 5.0.0 to 1.2.0 (MINOR bump for new feature additions)
- **New Core Principle:** Added "Agent-First Design (Phase 3)" principle
- **New Tech Stack Section:** Added "Tech Stack (Phase 3 Standards - AI Agent)" with:
  - OpenAI Agents SDK requirement
  - Official MCP SDK for Python
  - Stateless agent architecture
  - Conversation storage in PostgreSQL
- **New Architecture Section:** Added "AI Agent Architecture (Phase 3)" covering:
  - Agent design principles (stateless, no direct DB access, tool-first)
  - MCP Tools standards (stateless, schema-defined, only DB access layer)
  - Required MCP tools (create, list, get, update, delete, toggle tasks)
  - Conversation management (storage, messages, context, user isolation)
- **New Database Tables:** Added schema for Conversations and Messages tables
- **New API Endpoint:** POST /api/chat for natural language task management
- **Security Extension:** AI Agent security requirements (JWT, user isolation at tool level)
- **UI/UX Extension:** Chat interface requirements for natural language interaction
- **Success Criteria:** Phase 3 specific criteria for chatbot functionality

**Architectural Guarantees:**
- Agents MUST NOT access database directly
- All task operations MUST go through MCP tools
- MCP tools MUST be stateless and schema-defined
- Conversation context MUST be rebuilt from database each request
- OpenAI Agents SDK and Official MCP SDK MUST be used

## Outcome

- ✅ Impact: Constitution extended with Phase-III AI Agent architecture, MCP tools standards, and chatbot requirements. Version corrected to 1.2.0 with proper MINOR bump for new sections.
- 🧪 Tests: None (constitution document update)
- 📁 Files: Updated .specify/memory/constitution.md
- 🔁 Next prompts: Create Phase-III specification using /sp.specify, then /sp.plan and /sp.tasks for implementation planning
- 🧠 Reflection: Phase-III successfully integrated into constitution while maintaining all Phase-I and Phase-II principles. Clear separation of concerns established: UI → Agent → MCP Tools → Database.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation - PASS (all placeholders filled, version incremented correctly, no conflicts with existing principles)
- Prompt variant (if applicable): Standard constitution update workflow
- Next experiment (smallest change to try): None required - constitution update complete
