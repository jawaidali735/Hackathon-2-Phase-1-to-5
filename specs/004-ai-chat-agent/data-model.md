# Data Model: AI Todo Chatbot Integration

**Feature**: 004-ai-chat-agent
**Date**: 2026-02-06

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│    User     │       │   Conversation   │       │   Message   │
├─────────────┤       ├──────────────────┤       ├─────────────┤
│ id (PK)     │──┐    │ id (PK)          │──┐    │ id (PK)     │
│ email       │  │    │ user_id (FK)     │  │    │ conv_id(FK) │
│ ...         │  └───<│ created_at       │  └───<│ role        │
└─────────────┘       │ updated_at       │       │ content     │
       │              └──────────────────┘       │ tool_calls  │
       │                                         │ created_at  │
       │              ┌──────────────────┐       └─────────────┘
       │              │      Task        │
       │              ├──────────────────┤
       └─────────────<│ id (PK)          │
                      │ user_id (FK)     │
                      │ title            │
                      │ description      │
                      │ completed        │
                      │ created_at       │
                      │ updated_at       │
                      └──────────────────┘
```

---

## New Entities

### Conversation

Represents a chat session between a user and the AI assistant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Unique conversation identifier |
| user_id | String | FK→users.id, NOT NULL, INDEX | Owner of the conversation |
| created_at | DateTime | NOT NULL, default now | When conversation started |
| updated_at | DateTime | NOT NULL, default now | Last activity timestamp |

**SQLModel Definition**:
```python
class Conversation(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

**Indexes**:
- `ix_conversation_user_id` on `user_id` (for user's conversation lookup)

---

### Message

Individual messages within a conversation, from either user or assistant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Unique message identifier |
| conversation_id | UUID | FK→conversations.id, NOT NULL, INDEX | Parent conversation |
| role | String | NOT NULL, enum('user','assistant') | Message sender role |
| content | Text | NOT NULL | Message text content |
| tool_calls | JSON | NULL | Tool calls made (if any) |
| created_at | DateTime | NOT NULL, default now | When message was created |

**SQLModel Definition**:
```python
class Message(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", index=True, nullable=False)
    role: str = Field(nullable=False)  # 'user' or 'assistant'
    content: str = Field(nullable=False)
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

**Indexes**:
- `ix_message_conversation_id` on `conversation_id` (for message retrieval)

**Constraints**:
- `role` must be one of: 'user', 'assistant'
- `conversation_id` must reference existing conversation

---

## Existing Entities (Reference)

### Task (No Changes)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Task identifier |
| user_id | String | FK, INDEX | Task owner |
| title | String(200) | NOT NULL | Task title |
| description | String(1000) | NULL | Optional description |
| completed | Boolean | default False | Completion status |
| created_at | DateTime | NOT NULL | Creation timestamp |
| updated_at | DateTime | NOT NULL | Last update timestamp |

---

## Relationships

### User → Conversation (1:N)
- One user can have many conversations
- Conversation deletion cascades when user deleted
- Query pattern: `SELECT * FROM conversation WHERE user_id = ?`

### Conversation → Message (1:N)
- One conversation has many messages
- Messages deleted when conversation deleted (CASCADE)
- Query pattern: `SELECT * FROM message WHERE conversation_id = ? ORDER BY created_at`

### User → Task (1:N) - Existing
- Unchanged from Phase 2
- Tasks accessed via MCP tools, not directly in chat

---

## Data Access Patterns

### Create Conversation
```python
def create_conversation(session: Session, user_id: str) -> Conversation:
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation
```

### Get User's Latest Conversation
```python
def get_latest_conversation(session: Session, user_id: str) -> Optional[Conversation]:
    statement = select(Conversation).where(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc()).limit(1)
    return session.exec(statement).first()
```

### Get Conversation by ID
```python
def get_conversation(session: Session, conversation_id: uuid.UUID, user_id: str) -> Optional[Conversation]:
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id  # Enforce user isolation
    )
    return session.exec(statement).first()
```

### Add Message to Conversation
```python
def add_message(
    session: Session,
    conversation_id: uuid.UUID,
    role: str,
    content: str,
    tool_calls: Optional[dict] = None
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
```

### Get Conversation History
```python
def get_messages(
    session: Session,
    conversation_id: uuid.UUID,
    limit: int = 20
) -> List[Message]:
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(limit)
    messages = session.exec(statement).all()
    return list(reversed(messages))  # Return in chronological order
```

---

## Validation Rules

### Conversation
- `user_id` must be non-empty string
- `user_id` must match authenticated user (enforced at API layer)

### Message
- `role` must be 'user' or 'assistant'
- `content` must be non-empty string
- `content` max length: 10,000 characters (for assistant responses with tool results)
- `tool_calls` must be valid JSON if present

---

## Migration Strategy

### Approach: Auto-create tables on startup

SQLModel will auto-create tables if they don't exist. No Alembic migration needed for new tables.

```python
# In database.py or startup
from sqlmodel import SQLModel
from app.models.conversation import Conversation
from app.models.message import Message

def create_tables():
    SQLModel.metadata.create_all(engine)
```

### Rollback
If needed, drop tables manually:
```sql
DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS conversation;
```

---

## Schema Response Types

### ConversationRead
```python
class ConversationRead(SQLModel):
    id: uuid.UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
```

### MessageRead
```python
class MessageRead(SQLModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    tool_calls: Optional[dict]
    created_at: datetime
```
