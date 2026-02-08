# Tasks: AI Todo Chatbot Integration

**Input**: Design documents from `/specs/004-ai-chat-agent/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Manual E2E testing specified - no automated test tasks included.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`
- **Frontend**: `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and configure environment for AI chatbot feature

- [x] T001 Install cohere Python library in backend using `uv add cohere`
- [x] T002 Add COHERE_API_KEY to backend/.env.example with placeholder value
- [x] T003 [P] Install react-markdown in frontend using `npm install react-markdown`
- [x] T004 [P] Update backend/app/core/config.py to load COHERE_API_KEY from environment

**Checkpoint**: Dependencies installed, environment configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database models and CRUD operations that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models

- [x] T005 [P] Create Conversation SQLModel in backend/app/models/conversation.py with id, user_id, created_at, updated_at fields and user_id index
- [x] T006 [P] Create Message SQLModel in backend/app/models/message.py with id, conversation_id, role, content, tool_calls (JSON), created_at fields and conversation_id index
- [x] T007 Update backend/app/models/__init__.py to export Conversation and Message models
- [x] T008 Verify tables auto-create on backend startup by running the application

### Conversation CRUD Operations

- [x] T009 Create backend/app/crud/conversation.py with create_conversation, get_conversation, get_user_conversations functions
- [x] T010 Add get_or_create_conversation function to backend/app/crud/conversation.py for chat endpoint use
- [x] T011 Add add_message and get_messages functions to backend/app/crud/conversation.py

### Chat Module Structure

- [x] T012 Create backend/app/chat/__init__.py module initialization file
- [x] T013 [P] Create backend/app/chat/schemas.py with ChatRequest and ChatResponse Pydantic models per contracts/chat-api.md

**Checkpoint**: Foundation ready - database models created, CRUD operations available, chat module structure in place

---

## Phase 3: User Story 1 - Natural Language Task Management (Priority: P1) 🎯 MVP

**Goal**: Users can add, list, complete, update, and delete tasks through natural conversation

**Independent Test**: Send "Add a task to buy groceries" → verify task created and confirmation shown

### MCP-Style Tools Implementation

- [x] T014 [P] [US1] Create backend/app/chat/tools.py with ToolResult dataclass (success, data, error fields)
- [x] T015 [P] [US1] Implement add_task tool function in backend/app/chat/tools.py that creates task via existing CRUD
- [x] T016 [P] [US1] Implement list_tasks tool function in backend/app/chat/tools.py with filter parameter (all/pending/completed)
- [x] T017 [P] [US1] Implement complete_task tool function in backend/app/chat/tools.py that toggles task completion
- [x] T018 [P] [US1] Implement delete_task tool function in backend/app/chat/tools.py that removes task by ID
- [x] T019 [P] [US1] Implement update_task tool function in backend/app/chat/tools.py that updates title/description
- [x] T020 [US1] Create TOOL_REGISTRY dict in backend/app/chat/tools.py mapping tool names to functions and schemas

### Cohere Integration

- [x] T021 [US1] Create backend/app/chat/cohere_client.py with CohereClient class and async chat method
- [x] T022 [US1] Define SYSTEM_PROMPT constant in backend/app/chat/cohere_client.py with tool descriptions and JSON output format
- [x] T023 [US1] Implement parse_tool_call function in backend/app/chat/cohere_client.py to extract JSON tool calls from response
- [x] T024 [US1] Implement reasoning_loop method in CohereClient that calls Cohere, parses response, executes tools, and loops until natural language response

### Chat Endpoint

- [x] T025 [US1] Create backend/app/api/chat.py with POST /api/v1/{user_id}/chat endpoint
- [x] T026 [US1] Add JWT authentication dependency to chat endpoint matching existing tasks.py pattern
- [x] T027 [US1] Implement user_id validation in chat endpoint (URL must match JWT sub claim, return 403 if mismatch)
- [x] T028 [US1] Wire conversation load/create, Cohere reasoning loop, and message persistence in chat endpoint
- [x] T029 [US1] Add chat router to backend/app/main.py with include_router(chat_router)

**Checkpoint**: User Story 1 complete - natural language task management via API works end-to-end

---

## Phase 4: User Story 2 - Intelligent Conversation Experience (Priority: P1)

**Goal**: Chatbot understands context, handles ambiguity, confirms actions, provides helpful errors

**Independent Test**: Send "complete it" with multiple tasks → verify assistant asks for clarification

### Enhanced Tool Logic

- [x] T030 [US2] Add get_current_user tool function in backend/app/chat/tools.py returning user_id and email from JWT
- [x] T031 [US2] Update TOOL_REGISTRY in backend/app/chat/tools.py to include get_current_user tool
- [x] T032 [US2] Add task title matching logic in complete_task tool to handle "complete buy milk" style requests
- [x] T033 [US2] Add task title matching logic in delete_task tool for natural language task references

### Conversation Context

- [x] T034 [US2] Update reasoning_loop in backend/app/chat/cohere_client.py to include conversation history in prompts
- [x] T035 [US2] Add context_limit parameter (default 20 messages) to get_messages in backend/app/crud/conversation.py
- [x] T036 [US2] Enhance SYSTEM_PROMPT in backend/app/chat/cohere_client.py with instructions for handling ambiguous requests

### Error Handling

- [x] T037 [US2] Add try/except with Cohere API error handling in CohereClient returning user-friendly error messages
- [x] T038 [US2] Add retry_with_backoff decorator in backend/app/chat/cohere_client.py for transient API failures
- [x] T039 [US2] Update tools to return helpful error messages when task not found or validation fails

**Checkpoint**: User Story 2 complete - intelligent conversation with context, error handling, and clarification

---

## Phase 5: User Story 3 - Beautiful Chat Interface (Priority: P2)

**Goal**: Premium glassmorphic chat UI with floating button, slide-in panel, styled message bubbles

**Independent Test**: Open chat panel → verify glassmorphic styling, animations, and theme support

### Chat Button Component

- [x] T040 [P] [US3] Create frontend/src/components/chat/ChatButton.tsx with floating circular button (56px, bottom-right positioned)
- [x] T041 [P] [US3] Add emerald gradient background and glassmorphic effect styling to ChatButton
- [x] T042 [US3] Add subtle pulse animation on idle state to ChatButton using Tailwind animate-pulse
- [x] T043 [US3] Add onClick handler to ChatButton that toggles panel open state

### Chat Panel Container

- [x] T044 [US3] Create frontend/src/components/chat/ChatPanel.tsx container with slide-in animation (300ms ease-out from right)
- [x] T045 [US3] Style ChatPanel with glassmorphic card (backdrop-blur, semi-transparent bg, rounded corners)
- [x] T046 [US3] Add ChatPanel header with AI assistant title and close button
- [x] T047 [US3] Make ChatPanel responsive: 400px width on desktop, full width on mobile (<640px)

### Message Components

- [x] T048 [P] [US3] Create frontend/src/components/chat/MessageBubble.tsx with role-based styling (user: right/indigo, assistant: left/slate)
- [x] T049 [US3] Add timestamp display below each MessageBubble with muted text styling
- [x] T050 [US3] Integrate react-markdown in MessageBubble for rendering assistant responses with bold, lists, code

### Input and Indicators

- [x] T051 [P] [US3] Create frontend/src/components/chat/ChatInput.tsx with text input and send button (paper plane SVG icon)
- [x] T052 [P] [US3] Create frontend/src/components/chat/TypingIndicator.tsx with animated three-dot indicator
- [x] T053 [US3] Add Enter key submit and button click handlers to ChatInput
- [x] T054 [US3] Add light/dark theme support to all chat components using Tailwind dark: variants

### Integration

- [x] T055 [US3] Create frontend/src/components/chat/index.ts barrel export for all chat components
- [x] T056 [US3] Add ChatButton to frontend/src/app/dashboard/page.tsx (or layout for global access)

**Checkpoint**: User Story 3 complete - beautiful chat UI visible and animated on dashboard

---

## Phase 6: User Story 4 - Secure Multi-User Isolation (Priority: P1)

**Goal**: Complete user data isolation - conversations and tasks scoped to authenticated user only

**Independent Test**: Login as User A, create task via chat, login as User B → verify User B cannot see User A's tasks or conversations

### Backend Security

- [x] T057 [US4] Verify all tool functions in backend/app/chat/tools.py filter queries by user_id parameter
- [x] T058 [US4] Add user_id parameter validation in get_conversation to reject cross-user access attempts
- [x] T059 [US4] Ensure chat endpoint extracts user_id from JWT only, never from request body
- [x] T060 [US4] Add 401 response for missing/invalid JWT in chat endpoint error handling

### Frontend Security

- [x] T061 [US4] Create frontend/src/lib/chat-api.ts with sendMessage function that includes Authorization header from auth context
- [x] T062 [US4] Create frontend/src/hooks/useChat.ts hook managing conversationId, messages, isLoading, error state
- [x] T063 [US4] Implement sendMessage in useChat that calls chat API and updates local state
- [x] T064 [US4] Add conversation history persistence in useChat (store conversationId in state, reload on mount)

### State Management

- [x] T065 [US4] Wire useChat hook into ChatPanel for message display and send functionality
- [x] T066 [US4] Add auto-scroll to bottom on new message in ChatPanel message list
- [x] T067 [US4] Add loading state (show TypingIndicator) while waiting for API response
- [x] T068 [US4] Add error state display in ChatPanel with retry option

**Checkpoint**: User Story 4 complete - full security with user isolation verified

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements, micro-interactions, accessibility, and integration verification

### Micro-Interactions

- [x] T069 [P] Add message bubble fade-in animation on new messages in MessageBubble.tsx
- [x] T070 [P] Add send button ripple effect on click in ChatInput.tsx
- [x] T071 Add smooth panel slide animation using CSS transform in ChatPanel.tsx

### Accessibility

- [x] T072 [P] Add ARIA labels to ChatButton (aria-label="Open AI assistant")
- [x] T073 [P] Add ARIA labels to ChatInput (aria-label="Type a message")
- [x] T074 Add role="log" and aria-live="polite" to message list container for screen readers

### Mobile Optimization

- [x] T075 Touch-optimize ChatButton with larger hit target (min 44px) and proper spacing
- [x] T076 Ensure ChatPanel keyboard doesn't obscure input on mobile (adjust height/position)

### Final Integration

- [x] T077 End-to-end test: Add task via chat → verify appears in main task list
- [x] T078 End-to-end test: Complete task via chat → verify status updates in main task list
- [x] T079 End-to-end test: Conversation persists across page refresh
- [x] T080 Performance check: Verify chat response latency < 5 seconds typical

**Checkpoint**: Feature complete - all user stories working, polished, accessible

---

## Dependencies

```text
Phase 1 (Setup) ──────────────────────────────────────┐
                                                       ▼
Phase 2 (Foundation) ─────────────────────────────────┐
    └─ Database models, CRUD, chat module structure    │
                                                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    User Stories (can run in parallel)               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Phase 3: US1 (Natural Language)                                    │
│      └─ Tools, Cohere client, chat endpoint                        │
│                  │                                                  │
│                  ▼                                                  │
│  Phase 4: US2 (Intelligent Conversation)                           │
│      └─ Enhanced tools, context, error handling                    │
│         (depends on US1 tools being complete)                      │
│                                                                     │
│  Phase 5: US3 (Beautiful UI) ──────────────────────────────────────│
│      └─ Frontend components (independent of backend)               │
│                  │                                                  │
│                  ▼                                                  │
│  Phase 6: US4 (Security) ──────────────────────────────────────────│
│      └─ Integration of frontend with backend                       │
│         (depends on US1 endpoint + US3 components)                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                                       │
                                                       ▼
Phase 7 (Polish) ─────────────────────────────────────────────────────
    └─ All user stories complete, final refinements
```

---

## Parallel Execution Opportunities

### Within Phase 2 (Foundation)
```text
T005 (Conversation model) ──┐
                            ├── Can run in parallel
T006 (Message model) ───────┘
```

### Within Phase 3 (US1 - Tools)
```text
T014 (ToolResult) ──────┐
T015 (add_task) ────────┤
T016 (list_tasks) ──────┼── All tool implementations can run in parallel
T017 (complete_task) ───┤
T018 (delete_task) ─────┤
T019 (update_task) ─────┘
```

### Within Phase 5 (US3 - UI Components)
```text
T040-T042 (ChatButton) ─────┐
T048 (MessageBubble) ───────┼── Component files can be created in parallel
T051 (ChatInput) ───────────┤
T052 (TypingIndicator) ─────┘
```

### Across Phases
```text
Phase 3-4 (Backend) ────────┐
                            ├── Frontend and backend can develop in parallel
Phase 5 (Frontend UI) ──────┘    (integration in Phase 6)
```

---

## Implementation Strategy

### MVP Scope (User Story 1 Only)
For minimum viable demo:
- Complete Phase 1 + Phase 2 + Phase 3
- Result: Working chat endpoint that can add/list/complete/delete tasks via API
- Can demo with curl or API client

### Full Feature (All User Stories)
- Complete all phases in order
- Result: Complete AI chatbot with beautiful UI, intelligent conversation, full security

### Suggested Order for Single Developer
1. T001-T004 (Setup) - 5 min
2. T005-T013 (Foundation) - 20 min
3. T014-T029 (US1 MVP) - 45 min
4. **[CHECKPOINT: Demo basic chat via API]**
5. T040-T056 (US3 UI) - 30 min
6. T057-T068 (US4 Integration) - 25 min
7. T030-T039 (US2 Intelligence) - 20 min
8. T069-T080 (Polish) - 15 min

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 80 |
| **Phase 1 (Setup)** | 4 tasks |
| **Phase 2 (Foundation)** | 9 tasks |
| **Phase 3 (US1 - MVP)** | 16 tasks |
| **Phase 4 (US2)** | 10 tasks |
| **Phase 5 (US3)** | 17 tasks |
| **Phase 6 (US4)** | 12 tasks |
| **Phase 7 (Polish)** | 12 tasks |
| **Parallelizable Tasks** | 28 (35%) |
| **MVP Scope** | Phases 1-3 (29 tasks) |
