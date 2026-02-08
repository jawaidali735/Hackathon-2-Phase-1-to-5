# Implementation Plan: AI Todo Chatbot Integration

**Branch**: `004-ai-chat-agent` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ai-chat-agent/spec.md`

## Summary

Integrate an intelligent AI-powered chatbot into the existing full-stack Todo application, enabling natural language task management through Cohere API. The implementation extends the FastAPI backend with a stateless chat endpoint, 6 MCP-style tools, conversation persistence, and a premium glassmorphic chat UI in the Next.js frontend.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, SQLModel, cohere (Python), Next.js 16+, Tailwind CSS
**Storage**: Neon Serverless PostgreSQL (existing) + Conversation/Message tables
**Testing**: pytest (backend), manual E2E testing (frontend)
**Target Platform**: Web application (desktop + mobile responsive)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: <2s typical response, <5s end-to-end task creation via chat
**Constraints**: Stateless backend, JWT authentication required, user data isolation
**Scale/Scope**: Multi-user, conversation history persistence, 6 MCP tools

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Spec-Driven Development | ✅ PASS | Full spec created at `spec.md` |
| AI-Native Architecture | ✅ PASS | Using Cohere API for AI reasoning |
| Multi-User Data Isolation | ✅ PASS | JWT user_id enforced on all tools |
| Single Source of Truth | ✅ PASS | Follows constitution tech stack |
| Statelessness with JWT | ✅ PASS | Stateless endpoint, context from DB |
| Agent-First Design | ✅ PASS | MCP tools for all data operations |

**Constitution Deviation**: Using Cohere API instead of OpenAI Agents SDK (constitution specifies OpenAI). This is an approved deviation per user requirements - Cohere provides equivalent tool-calling capabilities via prompt engineering.

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-chat-agent/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chat-api.md      # Chat endpoint contract
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── tasks.py          # Existing task endpoints
│   │   └── chat.py           # NEW: Chat endpoint
│   ├── chat/                  # NEW: Chat module
│   │   ├── __init__.py
│   │   ├── cohere_client.py  # Cohere API integration
│   │   ├── tools.py          # MCP-style tool implementations
│   │   └── schemas.py        # Request/response schemas
│   ├── models/
│   │   ├── task.py           # Existing task model
│   │   ├── conversation.py   # NEW: Conversation model
│   │   └── message.py        # NEW: Message model
│   └── crud/
│       ├── task.py           # Existing CRUD
│       └── conversation.py   # NEW: Conversation CRUD
└── tests/
    └── test_chat.py          # NEW: Chat endpoint tests

frontend/
├── src/
│   ├── components/
│   │   └── chat/             # NEW: Chat components
│   │       ├── ChatButton.tsx
│   │       ├── ChatPanel.tsx
│   │       ├── MessageBubble.tsx
│   │       ├── ChatInput.tsx
│   │       └── TypingIndicator.tsx
│   ├── hooks/
│   │   └── useChat.ts        # NEW: Chat state hook
│   └── lib/
│       └── chat-api.ts       # NEW: Chat API client
```

**Structure Decision**: Extend existing web application structure. Backend chat module added under `app/chat/`, frontend chat components under `components/chat/`.

## Complexity Tracking

| Deviation | Why Needed | Alternative Rejected |
|-----------|------------|---------------------|
| Cohere instead of OpenAI | User requirement - hackathon constraint | OpenAI rejected per user spec |
| Prompt engineering for tools | Cohere doesn't have native tool schema | Direct tool calls unavailable in Cohere |

---

## Key Architectural Decisions

### Decision 1: Cohere Model Selection
**Choice**: `command-r-plus`
**Rationale**: Superior reasoning and instruction-following capabilities compared to `command-r`. Better at structured JSON output for tool calls.
**Alternatives**: `command-r` (rejected - less accurate tool parsing)

### Decision 2: Tool Call Parsing Strategy
**Choice**: Strict JSON block extraction with markdown code fence
**Rationale**: Reliable parsing, clear format for Cohere to follow. Response must contain ```json block for tool calls.
**Alternatives**: Regex fallback (rejected - fragile, error-prone)

### Decision 3: Multi-Step Tool Chaining
**Choice**: Loop until no tool call detected
**Rationale**: Supports complex queries like "List my tasks then delete the first one" which require sequential tool execution.
**Flow**: Call Cohere → Parse response → If tool call, execute and feed result back → Repeat until natural language response

### Decision 4: Conversation Persistence
**Choice**: Create new conversation if `conversation_id` not provided
**Rationale**: Flexible UX - users can start fresh or continue existing conversations.
**Behavior**: Missing ID = new conversation, provided ID = load and continue

### Decision 5: Frontend Chat Panel Layout
**Choice**: Slide-in panel from bottom-right
**Rationale**: Premium immersion, doesn't obscure main content, familiar pattern (Intercom/Drift style).
**Alternatives**: Full bottom sheet (rejected - blocks content), modal (rejected - too intrusive)

### Decision 6: Message Rendering
**Choice**: Markdown support in assistant responses
**Rationale**: Rich formatting (bold, italic, lists, code) for professional, readable responses.
**Implementation**: Use `react-markdown` for rendering

### Decision 7: Typing Indicator
**Choice**: Animated dots with fade
**Rationale**: Delightful micro-interaction, conveys processing state without being distracting.

---

## Implementation Phases

### Phase 1: Database Foundation
**Owner**: Database Engineer Agent
**Duration**: Atomic, testable

**Tasks**:
1. Create `Conversation` SQLModel (id, user_id, created_at)
2. Create `Message` SQLModel (id, conversation_id, role, content, tool_calls, created_at)
3. Add indexes on user_id and conversation_id
4. Create CRUD operations for conversations and messages
5. Verify tables created on app startup

**Validation**:
- [ ] Models import without errors
- [ ] Tables auto-create on startup
- [ ] CRUD operations pass unit tests

**Rollback**: Delete new model files, remove from imports

---

### Phase 2: MCP-Style Tools
**Owner**: MCP Tools Engineer Agent
**Duration**: Atomic, testable

**Tasks**:
1. Implement `add_task(user_id, title, description?)` tool
2. Implement `list_tasks(user_id, filter?)` tool
3. Implement `complete_task(user_id, task_id, completed?)` tool
4. Implement `delete_task(user_id, task_id)` tool
5. Implement `update_task(user_id, task_id, title?, description?)` tool
6. Implement `get_current_user(user_id, email)` tool
7. Create tool registry with schema definitions

**Validation**:
- [ ] Each tool executes independently
- [ ] User isolation enforced (user_id filtering)
- [ ] Error responses structured correctly

**Rollback**: Delete `app/chat/tools.py`

---

### Phase 3: Cohere Integration
**Owner**: Chatbot Backend Engineer Agent
**Duration**: Atomic, testable

**Tasks**:
1. Create Cohere client wrapper with async support
2. Define system prompt with tool schemas
3. Implement JSON tool call parser
4. Implement reasoning loop (call → parse → execute → repeat)
5. Add error handling for API failures
6. Add retry logic with exponential backoff

**Validation**:
- [ ] Cohere client connects successfully
- [ ] Tool calls parsed correctly from responses
- [ ] Multi-step chaining works
- [ ] API errors handled gracefully

**Rollback**: Delete `app/chat/cohere_client.py`

---

### Phase 4: Chat Endpoint
**Owner**: Chatbot Backend Engineer Agent
**Duration**: Atomic, testable

**Tasks**:
1. Create `POST /api/v1/{user_id}/chat` endpoint
2. Add JWT authentication dependency
3. Implement conversation load/create logic
4. Wire Cohere reasoning loop
5. Persist user message and assistant response
6. Return structured response with tool_calls

**Validation**:
- [ ] Endpoint accepts messages and returns responses
- [ ] JWT required (401 without)
- [ ] User ID validation (403 on mismatch)
- [ ] Conversation persists across requests

**Rollback**: Delete `app/api/chat.py`, remove router from main.py

---

### Phase 5: Frontend Chat Button
**Owner**: Frontend Chatbot Engineer Agent
**Duration**: Atomic, testable

**Tasks**:
1. Create `ChatButton.tsx` component
2. Style with emerald gradient, glassmorphic effect
3. Add subtle pulse animation on idle
4. Position fixed bottom-right (24px offset)
5. Add click handler to toggle panel

**Validation**:
- [ ] Button visible on dashboard
- [ ] Styling matches spec (emerald, glassmorphic)
- [ ] Animation plays smoothly
- [ ] Click toggles panel state

**Rollback**: Delete `components/chat/ChatButton.tsx`

---

### Phase 6: Chat Panel UI
**Owner**: Frontend Chatbot Engineer Agent
**Duration**: Atomic, testable

**Tasks**:
1. Create `ChatPanel.tsx` container
2. Implement slide-in animation (300ms ease-out)
3. Create `MessageBubble.tsx` (user right/indigo, assistant left/slate)
4. Create `ChatInput.tsx` with send button
5. Create `TypingIndicator.tsx` (animated dots)
6. Add markdown rendering for assistant messages
7. Implement theme-aware styling (light/dark)

**Validation**:
- [ ] Panel slides in smoothly
- [ ] Messages display correctly styled
- [ ] Input sends on Enter and button click
- [ ] Typing indicator shows during loading
- [ ] Works in light and dark themes

**Rollback**: Delete `components/chat/` directory

---

### Phase 7: Chat State & API Integration
**Owner**: Frontend Chatbot Engineer Agent
**Duration**: Atomic, testable

**Tasks**:
1. Create `useChat.ts` hook for state management
2. Create `chat-api.ts` for backend communication
3. Implement send message flow
4. Add loading state management
5. Implement error handling and display
6. Add auto-scroll to bottom on new messages
7. Persist conversation_id in state

**Validation**:
- [ ] Messages send and receive correctly
- [ ] Loading state shows during request
- [ ] Errors display user-friendly messages
- [ ] Conversation continues across messages

**Rollback**: Delete `hooks/useChat.ts`, `lib/chat-api.ts`

---

### Phase 8: Polish & Integration
**Owner**: Frontend Chatbot Engineer Agent
**Duration**: Final validation

**Tasks**:
1. Add micro-interactions (bubble fade-in, send ripple)
2. Mobile responsive optimization
3. Add ARIA labels for accessibility
4. End-to-end testing of all flows
5. Performance optimization (debounce, memoization)

**Validation**:
- [ ] Animations cinematic and smooth
- [ ] Mobile touch-optimized
- [ ] Screen reader accessible
- [ ] All E2E scenarios pass

---

## Testing Strategy

### Unit Tests (Backend)
- Tool execution with mock database
- Cohere response parsing
- JWT validation
- Conversation CRUD operations

### Integration Tests (Backend)
- Full chat flow with real Cohere API
- Multi-step tool chaining
- User isolation verification
- Error recovery

### E2E Tests (Frontend)
- Chat button → panel → send → receive
- Task created via chat appears in list
- Conversation history persists
- Theme switching

### Security Tests
- Invalid JWT → 401
- Cross-user conversation access → denied
- Tool calls respect user_id isolation

---

## Environment Variables

### Backend (.env additions)
```
COHERE_API_KEY=<your-cohere-api-key>
```

### Frontend (no additions required)
Uses existing `NEXT_PUBLIC_API_BASE_URL`

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Cohere API latency | Implement timeout with user-friendly message |
| JSON parsing failures | Retry with clarified prompt (max 2 retries) |
| Rate limiting | Queue requests, show "busy" state |
| Large conversation history | Limit context to last 20 messages |

---

## Success Metrics

Per spec success criteria:
- SC-001: Task creation <5s ✅ (target <2s Cohere + <1s DB)
- SC-002: 95% intent accuracy ✅ (Cohere command-r-plus)
- SC-003: Panel opens <300ms ✅ (CSS animation)
- SC-004: History loads <1s ✅ (indexed queries)
- SC-005: All 6 tools work ✅ (unit tested)
- SC-006: Zero data leakage ✅ (JWT isolation)
- SC-007: Mobile responsive ✅ (Tailwind breakpoints)
- SC-008: Graceful errors ✅ (error handling)
