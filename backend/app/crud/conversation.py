"""
CRUD operations for Conversation and Message models.
"""
from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.models.conversation import Conversation
from app.models.message import Message


def create_conversation(*, session: Session, user_id: str) -> Conversation:
    """
    Create a new conversation for a user.

    Args:
        session: Database session
        user_id: ID of the user creating the conversation

    Returns:
        Created Conversation object
    """
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def get_conversation(*, session: Session, conversation_id: UUID, user_id: str) -> Optional[Conversation]:
    """
    Get a conversation by ID, ensuring it belongs to the specified user.

    Args:
        session: Database session
        conversation_id: ID of the conversation to retrieve
        user_id: ID of the user who should own the conversation

    Returns:
        Conversation if found and owned by user, None otherwise
    """
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    return session.exec(statement).first()


def get_user_conversations(*, session: Session, user_id: str, limit: int = 10) -> List[Conversation]:
    """
    Get all conversations for a user, ordered by most recent first.

    Args:
        session: Database session
        user_id: ID of the user
        limit: Maximum number of conversations to return

    Returns:
        List of Conversation objects
    """
    statement = select(Conversation).where(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc()).limit(limit)
    return list(session.exec(statement).all())


def get_or_create_conversation(
    *,
    session: Session,
    user_id: str,
    conversation_id: Optional[UUID] = None
) -> Conversation:
    """
    Get an existing conversation or create a new one.

    Args:
        session: Database session
        user_id: ID of the user
        conversation_id: Optional existing conversation ID

    Returns:
        Existing or newly created Conversation

    Raises:
        ValueError: If conversation_id is provided but not found or doesn't belong to user
    """
    if conversation_id:
        conversation = get_conversation(
            session=session,
            conversation_id=conversation_id,
            user_id=user_id
        )
        if not conversation:
            raise ValueError("Conversation not found or access denied")
        return conversation

    return create_conversation(session=session, user_id=user_id)


def update_conversation_timestamp(*, session: Session, conversation: Conversation) -> Conversation:
    """
    Update the conversation's updated_at timestamp.

    Args:
        session: Database session
        conversation: Conversation to update

    Returns:
        Updated Conversation
    """
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def add_message(
    *,
    session: Session,
    conversation_id: UUID,
    role: str,
    content: str,
    tool_calls: Optional[Dict[str, Any]] = None
) -> Message:
    """
    Add a message to a conversation.

    Args:
        session: Database session
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
    session.commit()
    session.refresh(message)
    return message


def get_messages(
    *,
    session: Session,
    conversation_id: UUID,
    limit: int = 20
) -> List[Message]:
    """
    Get messages for a conversation, ordered chronologically.

    Args:
        session: Database session
        conversation_id: ID of the conversation
        limit: Maximum number of messages to return (most recent)

    Returns:
        List of Message objects in chronological order
    """
    # Get the most recent messages, then reverse for chronological order
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(limit)

    messages = list(session.exec(statement).all())
    return list(reversed(messages))  # Return in chronological order
