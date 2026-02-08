# Quickstart: AI Todo Chatbot Integration

**Feature**: 004-ai-chat-agent
**Date**: 2026-02-06

---

## Prerequisites

Before implementing this feature, ensure:

1. **Existing Application Running**
   - Backend API at `http://localhost:8000`
   - Frontend at `http://localhost:3000`
   - Database connected (Neon PostgreSQL)
   - JWT authentication working

2. **Environment Variables**
   - Backend `.env` has `BETTER_AUTH_SECRET`, `DATABASE_URL`
   - Frontend `.env.local` has `NEXT_PUBLIC_API_BASE_URL`

3. **Cohere API Access**
   - Sign up at [cohere.com](https://cohere.com)
   - Get API key from dashboard
   - Add `COHERE_API_KEY` to backend `.env`

---

## Quick Setup

### 1. Install Backend Dependencies

```bash
cd backend
uv add cohere
```

### 2. Add Environment Variable

```bash
# backend/.env
COHERE_API_KEY=your_cohere_api_key_here
```

### 3. Create Database Models

Create `backend/app/models/conversation.py`:
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Conversation(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

Create `backend/app/models/message.py`:
```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from typing import Optional
from datetime import datetime
import uuid

class Message(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", index=True)
    role: str = Field(nullable=False)
    content: str = Field(nullable=False)
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 4. Register Models

Update `backend/app/models/__init__.py`:
```python
from .task import Task, TaskCreate, TaskRead, TaskUpdate, TaskComplete
from .conversation import Conversation
from .message import Message
```

### 5. Start Backend

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Tables will auto-create on startup.

---

## Verification Steps

### Test Database Tables

```bash
# Connect to your Neon database and verify tables exist
psql $DATABASE_URL -c "\dt"
```

Expected output includes:
- `conversation`
- `message`
- `task` (existing)

### Test Cohere Connection

```python
# Quick test script
import cohere
import os

co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
response = co.chat(
    model="command-r-plus",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.message.content[0].text)
```

---

## Implementation Order

Follow this exact sequence:

| Phase | Component | Files | Checkpoint |
|-------|-----------|-------|------------|
| 1 | Database Models | `models/conversation.py`, `models/message.py` | Tables created |
| 2 | MCP Tools | `chat/tools.py` | Tools execute independently |
| 3 | Cohere Client | `chat/cohere_client.py` | API responds |
| 4 | Chat Endpoint | `api/chat.py` | Endpoint returns response |
| 5 | Chat Button | `components/chat/ChatButton.tsx` | Button visible |
| 6 | Chat Panel | `components/chat/ChatPanel.tsx` | Panel opens |
| 7 | Integration | `hooks/useChat.ts` | Full flow works |
| 8 | Polish | All components | Visual perfection |

---

## Testing the Chat

### Manual Test Flow

1. **Login** to the frontend application
2. **Click** the chat button (bottom-right)
3. **Send**: "Hello"
4. **Verify**: Greeting response
5. **Send**: "Add a task to buy groceries"
6. **Verify**: Task created, confirmation shown
7. **Send**: "Show my tasks"
8. **Verify**: Task list displayed
9. **Send**: "Who am I?"
10. **Verify**: Email displayed

### API Test (curl)

```bash
# Get JWT token from frontend auth flow, then:
curl -X POST "http://localhost:8000/api/v1/{user_id}/chat" \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to test the API"}'
```

---

## Common Issues

### "COHERE_API_KEY not set"
- Ensure `.env` file exists in `backend/` directory
- Restart the backend server after adding the key

### "Table conversation does not exist"
- Ensure models are imported in `models/__init__.py`
- Restart backend to trigger table creation

### "401 Unauthorized"
- Verify JWT token is valid
- Check `BETTER_AUTH_SECRET` matches frontend

### "User ID mismatch"
- Ensure URL `user_id` matches JWT `sub` claim
- Frontend must send correct user ID

### Chat panel not appearing
- Check browser console for errors
- Verify `ChatButton` component is mounted
- Check z-index conflicts with other elements

---

## File Structure After Implementation

```
backend/
├── app/
│   ├── api/
│   │   ├── tasks.py
│   │   └── chat.py          ← NEW
│   ├── chat/                 ← NEW DIRECTORY
│   │   ├── __init__.py
│   │   ├── cohere_client.py
│   │   ├── tools.py
│   │   └── schemas.py
│   ├── models/
│   │   ├── task.py
│   │   ├── conversation.py  ← NEW
│   │   └── message.py       ← NEW
│   ├── crud/
│   │   ├── task.py
│   │   └── conversation.py  ← NEW
│   └── main.py              ← UPDATED (add chat router)

frontend/
├── src/
│   ├── components/
│   │   ├── dashboard/
│   │   └── chat/            ← NEW DIRECTORY
│   │       ├── ChatButton.tsx
│   │       ├── ChatPanel.tsx
│   │       ├── MessageBubble.tsx
│   │       ├── ChatInput.tsx
│   │       └── TypingIndicator.tsx
│   ├── hooks/
│   │   └── useChat.ts       ← NEW
│   └── lib/
│       └── chat-api.ts      ← NEW
```

---

## Next Steps

After setup:

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Assign tasks to appropriate agents
3. Implement in phase order
4. Validate each phase before proceeding
5. Final E2E testing
