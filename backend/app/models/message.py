"""
Message model for AI chatbot conversation messages.
"""
from sqlmodel import SQLModel, Field, Column, select
from sqlalchemy import JSON
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class Message(SQLModel, table=True):
    """
    Message model representing individual messages within a conversation.
    """
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", index=True, nullable=False)
    role: str = Field(nullable=False)  # 'user' or 'assistant'
    content: str = Field(nullable=False)
    tool_calls: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class MessageRead(SQLModel):
    """
    Model for reading message data.
    """
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    tool_calls: Optional[Dict[str, Any]]
    created_at: datetime


class MessageCreate(SQLModel):
    """
    Model for creating a new message.
    """
    role: str
    content: str
    tool_calls: Optional[Dict[str, Any]] = None


class MessageRepository:
    """
    Repository for async message database operations.
    """

    async def create(self, db, conversation_id: str, role: str, content: str, tool_calls: Optional[Dict] = None) -> Message:
        """Create a new message in a conversation."""
        conv_uuid = uuid.UUID(str(conversation_id))
        message = Message(
            conversation_id=conv_uuid,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    async def get_conversation_messages(self, db, conversation_id: str) -> List[Message]:
        """Get all messages for a conversation."""
        try:
            conv_uuid = uuid.UUID(str(conversation_id))
            query = select(Message).where(
                Message.conversation_id == conv_uuid
            ).order_by(Message.created_at)
            result = await db.execute(query)
            return result.scalars().all()
        except Exception:
            return []
