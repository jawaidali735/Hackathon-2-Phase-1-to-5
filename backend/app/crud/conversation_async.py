"""
Async CRUD operations for Conversation and Message models.
"""
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.models.conversation import Conversation
from app.models.message import Message


async def create_conversation_async(*, session: AsyncSession, user_id: str) -> Conversation:
    """
    Create a new conversation for a user asynchronously.

    Args:
        session: Async database session
        user_id: ID of the user creating the conversation

    Returns:
        Created Conversation object
    """
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


async def get_conversation_async(*, session: AsyncSession, conversation_id: UUID, user_id: str) -> Optional[Conversation]:
    """
    Get a conversation by ID, ensuring it belongs to the specified user asynchronously.

    Args:
        session: Async database session
        conversation_id: ID of the conversation to retrieve
        user_id: ID of the user who should own the conversation

    Returns:
        Conversation if found and owned by user, None otherwise
    """
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_conversations_async(*, session: AsyncSession, user_id: str, limit: int = 10) -> List[Conversation]:
    """
    Get all conversations for a user, ordered by most recent first asynchronously.

    Args:
        session: Async database session
        user_id: ID of the user
        limit: Maximum number of conversations to return

    Returns:
        List of Conversation objects
    """
    statement = select(Conversation).where(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc()).limit(limit)
    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_or_create_conversation_async(
    *,
    session: AsyncSession,
    user_id: str,
    conversation_id: Optional[UUID] = None
) -> Conversation:
    """
    Get an existing conversation or create a new one asynchronously.

    Args:
        session: Async database session
        user_id: ID of the user
        conversation_id: Optional existing conversation ID

    Returns:
        Existing or newly created Conversation

    Raises:
        ValueError: If conversation_id is provided but not found or doesn't belong to user
    """
    if conversation_id:
        conversation = await get_conversation_async(
            session=session,
            conversation_id=conversation_id,
            user_id=user_id
        )
        if not conversation:
            raise ValueError("Conversation not found or access denied")
        return conversation

    return await create_conversation_async(session=session, user_id=user_id)


async def update_conversation_timestamp_async(*, session: AsyncSession, conversation: Conversation) -> Conversation:
    """
    Update the conversation's updated_at timestamp asynchronously.

    Args:
        session: Async database session
        conversation: Conversation to update

    Returns:
        Updated Conversation
    """
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


async def add_message_async(
    *,
    session: AsyncSession,
    conversation_id: UUID,
    role: str,
    content: str,
    tool_calls: Optional[Dict[str, Any]] = None
) -> Message:
    """
    Add a message to a conversation asynchronously.

    Args:
        session: Async database session
        conversation_id: ID of the conversation
        role: Message role ('user' or 'assistant')
        content: Message content
        tool_calls: Optional tool calls data

    Returns:
        Created Message object
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def get_messages_async(
    *,
    session: AsyncSession,
    conversation_id: UUID,
    limit: int = 20
) -> List[Message]:
    """
    Get messages for a conversation, ordered chronologically asynchronously.

    Args:
        session: Async database session
        conversation_id: ID of the conversation
        limit: Maximum number of messages to return (most recent)

    Returns:
        List of Message objects in chronological order
    """
    # Get the most recent messages, then reverse for chronological order
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(limit)

    result = await session.execute(statement)
    messages = list(result.scalars().all())
    return list(reversed(messages))  # Return in chronological order