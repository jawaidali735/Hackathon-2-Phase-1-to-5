# Feature Specification: AI Todo Chatbot Integration

**Feature Branch**: `004-ai-chat-agent`
**Created**: 2026-02-06
**Status**: Draft
**Version**: v1.0
**Input**: User description: "AI Todo Chatbot Integration for The Evolution of Todo - Phase III: Full-Stack Web Application with Cohere-powered natural language task management"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Management (Priority: P1)

As a user, I want to manage my tasks through natural conversation so that I can add, complete, update, and delete tasks without navigating menus or forms.

**Why this priority**: Core chatbot functionality that delivers the primary value proposition - conversational task management that feels like talking to a personal assistant.

**Independent Test**: Can be fully tested by sending natural language messages like "Add a task to buy groceries" and verifying the task appears in the user's task list, delivering immediate conversational productivity value.

**Acceptance Scenarios**:

1. **Given** I am logged in and open the chatbot, **When** I type "Add a task to finish the report by Friday", **Then** a new task is created with title "finish the report by Friday" and the assistant confirms the action.

2. **Given** I have existing tasks, **When** I type "Show me my tasks", **Then** the assistant lists all my tasks with their completion status.

3. **Given** I have a task called "Buy milk", **When** I type "Mark buy milk as done", **Then** the task is marked complete and the assistant confirms.

4. **Given** I have multiple tasks, **When** I type "Delete the groceries task", **Then** the matching task is removed and the assistant confirms deletion.

5. **Given** I have a task, **When** I type "Update my report task to 'Finish quarterly report'", **Then** the task title is updated and confirmed.

---

### User Story 2 - Intelligent Conversation Experience (Priority: P1)

As a user, I want the chatbot to understand context, confirm actions, and handle errors gracefully so that I have confidence in my task management.

**Why this priority**: User trust and delight depend on the assistant behaving intelligently - understanding intent, asking clarifying questions when needed, and providing helpful feedback.

**Independent Test**: Can be tested by sending ambiguous requests and verifying the assistant asks clarifying questions or makes reasonable interpretations.

**Acceptance Scenarios**:

1. **Given** I type an ambiguous request like "complete it", **When** I have multiple incomplete tasks, **Then** the assistant asks which task I mean or lists options.

2. **Given** I request to delete a task that doesn't exist, **When** the assistant processes my request, **Then** it responds helpfully explaining no matching task was found.

3. **Given** I ask "Who am I?", **When** the assistant processes my request, **Then** it responds with my logged-in email address.

4. **Given** I type a greeting like "Hello!", **When** the assistant responds, **Then** it greets me warmly and offers to help with tasks.

---

### User Story 3 - Beautiful Chat Interface (Priority: P2)

As a user, I want a visually stunning chat interface that matches the premium app design so that I enjoy using the chatbot.

**Why this priority**: Visual appeal enhances user engagement and demonstrates flagship-level product quality for hackathon judges.

**Independent Test**: Can be tested by opening the chat panel and verifying visual elements render correctly across light/dark themes.

**Acceptance Scenarios**:

1. **Given** I am on any page of the app, **When** I look at the bottom-right corner, **Then** I see a floating chat button with emerald accent and subtle pulse animation.

2. **Given** I click the chat button, **When** the panel opens, **Then** I see a glassmorphic chat window that slides in smoothly.

3. **Given** I send a message, **When** viewing the chat, **Then** my messages appear on the right (indigo) and assistant messages on the left (slate) with timestamps.

4. **Given** I'm waiting for a response, **When** the assistant is processing, **Then** I see a typing indicator animation.

---

### User Story 4 - Secure Multi-User Isolation (Priority: P1)

As a user, I want my conversations and tasks to be completely private so that no other user can access my data.

**Why this priority**: Security and privacy are non-negotiable for production applications handling user data.

**Independent Test**: Can be tested by logging in as two different users and verifying each only sees their own tasks and conversation history.

**Acceptance Scenarios**:

1. **Given** I am User A with my own tasks, **When** User B asks to list tasks, **Then** User B only sees their own tasks, not mine.

2. **Given** I start a conversation, **When** I return later, **Then** I see my previous conversation history restored.

3. **Given** an unauthenticated request is made, **When** the backend processes it, **Then** the request is rejected with 401 Unauthorized.

---

### Edge Cases

- What happens when a user asks to complete/delete a task with an ambiguous name matching multiple tasks?
- How does the system handle very long messages exceeding reasonable limits?
- What happens if the Cohere API is unavailable or returns an error?
- How does the system handle rapid consecutive messages?
- What happens when a user has no tasks and asks to list them?

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a chat endpoint that accepts natural language messages and returns intelligent responses
- **FR-002**: System MUST expose 6 tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`, `get_current_user`
- **FR-003**: System MUST use Cohere API for all AI reasoning and natural language understanding
- **FR-004**: System MUST persist all conversations and messages in the database
- **FR-005**: System MUST rebuild conversation context from database on each request (stateless)
- **FR-006**: System MUST extract user_id from JWT token for all operations
- **FR-007**: System MUST display a floating chat button on all authenticated pages
- **FR-008**: System MUST provide a slide-in chat panel with message history
- **FR-009**: System MUST show typing indicators during AI processing
- **FR-010**: System MUST support both light and dark theme styling
- **FR-011**: System MUST handle tool chaining (multiple tool calls in sequence)
- **FR-012**: System MUST provide confirmation messages after successful operations

### Key Entities

- **Conversation**: Represents a chat session for a user (id, user_id, created_at)
- **Message**: Individual messages within a conversation (id, conversation_id, role, content, created_at)
- **Task**: Existing task entity used by MCP tools (id, user_id, title, description, completed, timestamps)
- **User**: Authenticated user identified by JWT (user_id, email extracted from token)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task via natural language in under 5 seconds end-to-end
- **SC-002**: 95% of common task management intents are correctly understood on first attempt
- **SC-003**: Chat panel opens within 300ms of clicking the trigger button
- **SC-004**: Conversation history loads and displays within 1 second
- **SC-005**: All 6 tools execute successfully with proper confirmation to user
- **SC-006**: Zero cross-user data leakage in multi-user testing
- **SC-007**: Chat interface renders correctly on mobile (375px+) and desktop viewports
- **SC-008**: System gracefully handles AI provider errors with user-friendly messages

---

## Cohere API Adaptation Strategy

### Overview

Replace OpenAI Agents SDK with direct Cohere chat API calls. The system uses structured prompt engineering to instruct Cohere to reason step-by-step, identify user intent, and output structured JSON for tool calls when needed.

### Prompt Engineering Approach

The system prompt instructs Cohere to:
1. Analyze the user's message to understand intent
2. Determine if a tool call is needed or if a direct response suffices
3. Output a structured JSON block when tool execution is required
4. Provide natural, friendly responses to the user

### Tool Call Flow

```
User Message → Cohere API → Parse Response
                              ↓
                    [Tool Call Detected?]
                     /              \
                   Yes               No
                    ↓                ↓
            Execute Tool      Return Response
                    ↓
            Feed Result Back to Cohere (if multi-step)
                    ↓
            Return Final Response
```

### System Prompt Template

```
You are a helpful AI assistant for a todo application. You help users manage their tasks through natural conversation.

Available tools:
- add_task(title, description?): Create a new task
- list_tasks(filter?): List tasks (all/pending/completed)
- complete_task(task_id, completed?): Mark task complete/incomplete
- delete_task(task_id): Delete a task
- update_task(task_id, title?, description?): Update task details
- get_current_user(): Get current user's email and ID

When you need to use a tool, respond with a JSON block:
{"tool": "tool_name", "params": {...}}

When no tool is needed, respond naturally to the user.

Always confirm actions after tool execution. Be friendly and helpful.
```

---

## MCP-Style Tools Specification

### Tool 1: add_task

**Purpose**: Create a new task for the authenticated user

| Parameter   | Type   | Required | Description                    |
| ----------- | ------ | -------- | ------------------------------ |
| title       | string | Yes      | Task title (1-200 chars)       |
| description | string | No       | Task description (max 1000)    |

**Returns**:
```json
{
  "success": true,
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string|null",
    "completed": false,
    "created_at": "ISO datetime"
  }
}
```

**Errors**: 400 (validation), 401 (unauthorized), 500 (server error)

---

### Tool 2: list_tasks

**Purpose**: Retrieve tasks for the authenticated user

| Parameter | Type   | Required | Description                           |
| --------- | ------ | -------- | ------------------------------------- |
| filter    | string | No       | "all", "pending", "completed" (default: "all") |

**Returns**:
```json
{
  "success": true,
  "tasks": [...],
  "count": 5
}
```

**Errors**: 401 (unauthorized), 500 (server error)

---

### Tool 3: complete_task

**Purpose**: Toggle or set task completion status

| Parameter | Type    | Required | Description                     |
| --------- | ------- | -------- | ------------------------------- |
| task_id   | string  | Yes      | UUID of task to complete        |
| completed | boolean | No       | Explicit status (default: true) |

**Returns**:
```json
{
  "success": true,
  "task": {...}
}
```

**Errors**: 400 (validation), 401 (unauthorized), 404 (not found), 500 (server error)

---

### Tool 4: delete_task

**Purpose**: Remove a task from the system

| Parameter | Type   | Required | Description          |
| --------- | ------ | -------- | -------------------- |
| task_id   | string | Yes      | UUID of task to delete |

**Returns**:
```json
{
  "success": true,
  "deleted_task_id": "uuid"
}
```

**Errors**: 401 (unauthorized), 404 (not found), 500 (server error)

---

### Tool 5: update_task

**Purpose**: Modify existing task properties

| Parameter   | Type   | Required | Description          |
| ----------- | ------ | -------- | -------------------- |
| task_id     | string | Yes      | UUID of task         |
| title       | string | No       | New title            |
| description | string | No       | New description      |

**Returns**:
```json
{
  "success": true,
  "task": {...}
}
```

**Errors**: 400 (validation), 401 (unauthorized), 404 (not found), 500 (server error)

---

### Tool 6: get_current_user

**Purpose**: Return the authenticated user's identity

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| (none)    | -    | -        | -           |

**Returns**:
```json
{
  "success": true,
  "user": {
    "user_id": "string",
    "email": "string"
  }
}
```

**Errors**: 401 (unauthorized)

---

## Database Extensions

### Conversation Table

| Column     | Type      | Constraints      | Description                |
| ---------- | --------- | ---------------- | -------------------------- |
| id         | UUID      | PK, default uuid | Unique conversation ID     |
| user_id    | VARCHAR   | NOT NULL, INDEX  | Owner of conversation      |
| created_at | TIMESTAMP | NOT NULL         | When conversation started  |

### Message Table

| Column          | Type      | Constraints      | Description                        |
| --------------- | --------- | ---------------- | ---------------------------------- |
| id              | UUID      | PK, default uuid | Unique message ID                  |
| conversation_id | UUID      | FK, NOT NULL     | Parent conversation                |
| role            | VARCHAR   | NOT NULL         | "user" or "assistant"              |
| content         | TEXT      | NOT NULL         | Message content                    |
| tool_calls      | JSON      | NULL             | Tool calls made (if any)           |
| created_at      | TIMESTAMP | NOT NULL         | When message was created           |

---

## Backend Chat Endpoint

### Endpoint: POST /api/v1/{user_id}/chat

**Authentication**: Bearer JWT required

**Request Body**:
```json
{
  "conversation_id": "uuid (optional - omit for new conversation)",
  "message": "string (required)"
}
```

**Success Response (200)**:
```json
{
  "conversation_id": "uuid",
  "response": "string",
  "tool_calls": [
    {
      "tool": "add_task",
      "params": {...},
      "result": {...}
    }
  ]
}
```

**Error Responses**:
- 400: Invalid request body
- 401: Missing or invalid JWT
- 403: User ID mismatch with JWT
- 500: Server error (including Cohere API failures)

### Processing Flow

1. Validate JWT and extract user_id/email
2. Verify URL user_id matches JWT user_id
3. Load or create conversation
4. Load conversation history from database
5. Build Cohere prompt with history and tools context
6. Call Cohere API with user message
7. Parse response for tool calls
8. Execute tools if needed (may loop for multi-step)
9. Persist user message and assistant response
10. Return response to frontend

---

## Frontend Chat UI Integration

### Floating Chat Button

- **Position**: Fixed, bottom-right corner (bottom: 24px, right: 24px)
- **Size**: 56px circular button
- **Style**: Emerald gradient background, glassmorphic effect
- **Animation**: Subtle pulse animation when idle
- **Icon**: Chat bubble SVG icon (white)

### Chat Panel

- **Trigger**: Click floating button to open/close
- **Animation**: Slide in from right (300ms ease-out)
- **Size**: 400px width (desktop), full width (mobile < 640px)
- **Height**: 600px max, responsive to viewport
- **Style**: Glassmorphic card, rounded corners, subtle shadow

### Message Bubbles

- **User messages**: Right-aligned, indigo background, white text
- **Assistant messages**: Left-aligned, slate/gray background, dark text
- **Timestamps**: Small, muted text below each bubble
- **Max width**: 80% of chat area

### Input Area

- **Position**: Fixed at bottom of chat panel
- **Input**: Text field with placeholder "Type a message..."
- **Send button**: Circular, emerald accent, paper plane SVG icon
- **Behavior**: Send on Enter key or button click

### States

- **Loading**: Typing indicator (three animated dots)
- **Error**: Error message with retry option
- **Empty**: Welcome message with suggested prompts

---

## Natural Language Examples & Flows

### Adding Tasks

| User Says | Intent Detected | Tool Called |
| --------- | --------------- | ----------- |
| "Add buy groceries" | add_task | add_task(title="buy groceries") |
| "Create a task to call mom tomorrow" | add_task | add_task(title="call mom tomorrow") |
| "I need to finish the report" | add_task | add_task(title="finish the report") |
| "Remind me to exercise" | add_task | add_task(title="exercise") |

### Listing Tasks

| User Says | Intent Detected | Tool Called |
| --------- | --------------- | ----------- |
| "Show my tasks" | list_tasks | list_tasks() |
| "What do I need to do?" | list_tasks | list_tasks(filter="pending") |
| "List completed tasks" | list_tasks | list_tasks(filter="completed") |

### Completing Tasks

| User Says | Intent Detected | Tool Called |
| --------- | --------------- | ----------- |
| "Mark groceries as done" | complete_task | complete_task(task_id=matched_id) |
| "I finished the report" | complete_task | complete_task(task_id=matched_id) |
| "Complete exercise task" | complete_task | complete_task(task_id=matched_id) |

### Deleting Tasks

| User Says | Intent Detected | Tool Called |
| --------- | --------------- | ----------- |
| "Delete the groceries task" | delete_task | delete_task(task_id=matched_id) |
| "Remove exercise from my list" | delete_task | delete_task(task_id=matched_id) |

### User Identity

| User Says | Intent Detected | Tool Called |
| --------- | --------------- | ----------- |
| "Who am I?" | get_current_user | get_current_user() |
| "What's my email?" | get_current_user | get_current_user() |

---

## Security & User Isolation

### Authentication

- All chat requests require valid JWT in Authorization header
- JWT validated using BETTER_AUTH_SECRET (shared with frontend)
- User ID extracted from JWT `sub` claim
- URL user_id must match JWT user_id (403 if mismatch)

### Data Isolation

- All database queries filtered by user_id
- Conversations scoped to user_id
- Tasks scoped to user_id
- No cross-user data access possible

### Input Validation

- Message content limited to 2000 characters
- Task titles limited to 200 characters
- Task descriptions limited to 1000 characters
- All inputs sanitized before database storage

---

## Error Handling & Confirmations

### Error Responses

| Scenario | User-Facing Message |
| -------- | ------------------- |
| Cohere API unavailable | "I'm having trouble thinking right now. Please try again in a moment." |
| Task not found | "I couldn't find a task matching '{query}'. Would you like to see your current tasks?" |
| Ambiguous task reference | "I found multiple tasks that could match. Which one did you mean? [list options]" |
| Invalid request | "I didn't quite understand that. Could you rephrase?" |
| Server error | "Something went wrong on my end. Please try again." |

### Confirmation Messages

| Action | Confirmation Template |
| ------ | --------------------- |
| Task added | "I've added '{title}' to your tasks." |
| Task completed | "Great job! I've marked '{title}' as complete." |
| Task deleted | "Done! I've removed '{title}' from your list." |
| Task updated | "I've updated '{title}' with the new details." |

---

## TypeScript/Frontend Types

```typescript
// Chat API Types
interface ChatRequest {
  conversation_id?: string;
  message: string;
}

interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls?: ToolCall[];
}

interface ToolCall {
  tool: string;
  params: Record<string, unknown>;
  result: Record<string, unknown>;
}

// Message Types
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tool_calls?: ToolCall[];
}

// Chat State
interface ChatState {
  isOpen: boolean;
  conversationId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}
```

---

## Acceptance Criteria

### Backend Acceptance

- [ ] POST /api/v1/{user_id}/chat endpoint accepts messages and returns responses
- [ ] Cohere API integration works with proper prompt engineering
- [ ] All 6 tools (add, list, complete, delete, update, get_user) execute correctly
- [ ] Tool chaining works for multi-step operations
- [ ] Conversations and messages persist in database
- [ ] JWT authentication enforced on all requests
- [ ] User isolation verified - no cross-user data access

### Frontend Acceptance

- [ ] Floating chat button visible on authenticated pages
- [ ] Chat panel opens/closes smoothly with animation
- [ ] Messages display with correct styling (user right, assistant left)
- [ ] Typing indicator shows during AI processing
- [ ] Send button and Enter key both submit messages
- [ ] Chat works in both light and dark themes
- [ ] Responsive design works on mobile and desktop

### Integration Acceptance

- [ ] End-to-end: User can add task via chat and see it in main task list
- [ ] End-to-end: User can complete task via chat and status updates everywhere
- [ ] Conversation history persists across page refreshes
- [ ] Multi-user test passes with complete isolation

---

## Assumptions

- Cohere API is available and responsive (fallback: user-friendly error)
- Users have modern browsers with JavaScript enabled
- JWT tokens include user email in claims (or derivable from user_id)
- Existing task CRUD operations in backend remain unchanged
- Frontend build system supports additional components without modification
