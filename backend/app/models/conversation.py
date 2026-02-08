"""
Conversation model for AI chatbot conversations.
"""
from sqlmodel import SQLModel, Field, select
from typing import Optional
from datetime import datetime
import uuid


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session between a user and the AI assistant.
    """
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ConversationRead(SQLModel):
    """
    Model for reading conversation data.
    """
    id: uuid.UUID
    user_id: str
    created_at: datetime
    updated_at: datetime


class ConversationRepository:
    """
    Repository for async conversation database operations.
    """

    async def create(self, db, user_id: str) -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    async def get_by_id(self, db, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """Get a conversation by ID with user isolation."""
        try:
            conv_uuid = uuid.UUID(str(conversation_id))
            query = select(Conversation).where(
                Conversation.id == conv_uuid,
                Conversation.user_id == user_id
            )
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception:
            return None

    async def update_timestamp(self, db, conversation_id: str) -> None:
        """Update the conversation's updated_at timestamp."""
        try:
            conv_uuid = uuid.UUID(str(conversation_id))
            query = select(Conversation).where(Conversation.id == conv_uuid)
            result = await db.execute(query)
            conversation = result.scalar_one_or_none()
            if conversation:
                conversation.updated_at = datetime.utcnow()
                db.add(conversation)
                await db.commit()
        except Exception:
            pass
