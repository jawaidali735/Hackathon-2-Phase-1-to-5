# Research: AI Todo Chatbot Integration

**Feature**: 004-ai-chat-agent
**Date**: 2026-02-06
**Status**: Complete

---

## Research Areas

### 1. Cohere API for Tool Calling

**Decision**: Use Cohere `command-r-plus` model with prompt engineering for tool calls

**Rationale**:
- Cohere's `command-r-plus` model excels at instruction following and structured output
- Native tool/function calling available via `tools` parameter in chat API
- Supports JSON mode for structured responses
- Better reasoning capabilities than `command-r`

**Implementation Approach**:
```python
import cohere

co = cohere.ClientV2(api_key="COHERE_API_KEY")

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description"}
                },
                "required": ["title"]
            }
        }
    }
    # ... more tools
]

response = co.chat(
    model="command-r-plus",
    messages=[{"role": "user", "content": "Add a task to buy groceries"}],
    tools=tools
)
```

**Alternatives Considered**:
- OpenAI Agents SDK: Rejected per user requirements (must use Cohere)
- Cohere `command-r`: Less accurate for complex tool parsing
- Manual prompt engineering only: More fragile than native tool support

---

### 2. Stateless Backend Architecture

**Decision**: Fully stateless with database-backed conversation history

**Rationale**:
- Aligns with constitution's statelessness principle
- Enables horizontal scaling
- No server memory required between requests
- Conversation context rebuilt from database on each request

**Implementation Pattern**:
```python
async def chat_endpoint(user_id: str, request: ChatRequest, session: Session):
    # 1. Load or create conversation
    conversation = get_or_create_conversation(session, user_id, request.conversation_id)

    # 2. Load message history from DB
    history = get_messages(session, conversation.id, limit=20)

    # 3. Process with Cohere (stateless call)
    response = await process_with_cohere(history, request.message)

    # 4. Persist new messages
    save_message(session, conversation.id, "user", request.message)
    save_message(session, conversation.id, "assistant", response.text)

    return ChatResponse(conversation_id=conversation.id, response=response.text)
```

**Alternatives Considered**:
- In-memory conversation cache: Rejected (violates statelessness)
- Redis session storage: Over-engineered for this use case
- Single conversation per user: Too restrictive

---

### 3. MCP-Style Tool Design

**Decision**: Stateless tools with user_id passed as parameter (from JWT)

**Rationale**:
- Tools never trust user input for user_id
- user_id extracted from JWT by endpoint, passed to tools
- Each tool is atomic and independently testable
- Consistent error response format

**Tool Interface Pattern**:
```python
@dataclass
class ToolResult:
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

def add_task(session: Session, user_id: str, title: str, description: str = None) -> ToolResult:
    try:
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        session.commit()
        return ToolResult(success=True, data=task.model_dump())
    except Exception as e:
        return ToolResult(success=False, error=str(e))
```

**Alternatives Considered**:
- Class-based tools: Unnecessary complexity
- Tools with embedded authentication: Security risk
- Direct database access in endpoint: Violates agent-first design

---

### 4. Frontend Chat Panel Architecture

**Decision**: React client component with local state + API calls

**Rationale**:
- Client component required for interactivity
- Local state for messages, loading, conversation_id
- API calls to backend chat endpoint
- No global state management needed (chat is self-contained)

**Component Structure**:
```
ChatProvider (context for chat state)
├── ChatButton (floating trigger)
└── ChatPanel (slide-in container)
    ├── ChatHeader (title, close button)
    ├── MessageList (scrollable messages)
    │   └── MessageBubble (individual message)
    ├── TypingIndicator (when loading)
    └── ChatInput (input + send button)
```

**Alternatives Considered**:
- Server components: Not suitable for real-time interaction
- Global state (Redux/Zustand): Over-engineered
- iframe embed: Poor UX, integration issues

---

### 5. Markdown Rendering in Chat

**Decision**: Use `react-markdown` with custom styling

**Rationale**:
- Assistant responses benefit from rich formatting
- Lists, bold, code blocks improve readability
- Lightweight library with good React integration
- Custom components for styling consistency

**Implementation**:
```tsx
import ReactMarkdown from 'react-markdown';

<ReactMarkdown
  components={{
    p: ({children}) => <p className="mb-2">{children}</p>,
    ul: ({children}) => <ul className="list-disc ml-4">{children}</ul>,
    strong: ({children}) => <strong className="font-semibold">{children}</strong>,
  }}
>
  {message.content}
</ReactMarkdown>
```

**Alternatives Considered**:
- Plain text only: Poor user experience
- Custom markdown parser: Reinventing the wheel
- Full MDX: Over-powered for chat messages

---

### 6. Error Handling Strategy

**Decision**: Graceful degradation with user-friendly messages

**Rationale**:
- Users should never see raw error messages
- Cohere API failures should suggest retry
- Parsing failures should attempt recovery
- All errors logged for debugging

**Error Categories**:
| Error Type | User Message | Action |
|------------|--------------|--------|
| Cohere API timeout | "I'm thinking hard about this. Please wait..." | Auto-retry once |
| Cohere API error | "I'm having trouble right now. Please try again." | Log, show retry |
| JSON parse failure | (hidden, retry internally) | Retry with clarified prompt |
| Task not found | "I couldn't find a task matching that." | Suggest list tasks |
| Auth failure | "Please log in again." | Redirect to login |

---

## Dependencies Verification

### Backend Dependencies (Python)
```
cohere>=5.0.0       # Cohere API client
sqlmodel>=0.0.14    # Already installed
fastapi>=0.100.0    # Already installed
python-jose>=3.3.0  # Already installed (JWT)
```

### Frontend Dependencies (npm)
```
react-markdown      # Markdown rendering
@types/react        # Already installed
tailwindcss         # Already installed
```

---

## Security Research

### JWT Token Handling
- Extract user_id from `sub` claim (existing pattern)
- Extract email from `email` claim if available
- Validate URL user_id matches JWT user_id
- All tools receive user_id from endpoint, not from user input

### Data Isolation
- Conversations filtered by user_id at query level
- Messages accessed only through parent conversation
- Tools enforce user_id on all database operations
- No cross-user data access possible

---

## Performance Considerations

### Cohere API Latency
- Typical response: 1-3 seconds
- Complex multi-tool queries: 3-5 seconds
- Mitigation: Show typing indicator, streaming if available

### Database Queries
- Conversation lookup: O(1) with UUID index
- Message history: O(n) where n = message count, limited to 20
- Task operations: O(1) with existing indexes

### Frontend Performance
- Lazy load chat panel on first open
- Virtualize message list for long conversations (future)
- Debounce input to prevent rapid submissions

---

## Conclusion

All research areas resolved. No blocking unknowns remain. Ready for implementation per plan.md phases.
