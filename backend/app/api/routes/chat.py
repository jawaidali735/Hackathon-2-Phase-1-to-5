"""
Chat API route for OpenAI Agents SDK powered chatbot with MCP tools.
Uses todo-app's existing auth system.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlmodel import Session
from uuid import UUID
import logging
from app.api.models.chat import ChatRequest, ChatResponse, ToolCall
from app.db.database import get_session
from app.db_async import get_async_session
from app.core.auth import get_current_user, get_current_user_email, get_current_user_name, verify_user_id_match, security
from app.crud.conversation_async import get_user_conversations_async, get_messages_async, get_or_create_conversation_async, add_message_async, update_conversation_timestamp_async
from app.models.conversation import Conversation
from app.chat.agent import run_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/{user_id}", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Send a message to the AI chatbot using OpenAI Agents SDK with MCP tools.

    The chatbot can manage tasks through natural language:
    - Add tasks: "Add a task to buy groceries"
    - List tasks: "Show me my tasks"
    - Complete tasks: "Mark buy groceries as done"
    - Delete tasks: "Delete the groceries task"
    - Update tasks: "Update my report task to 'Finish quarterly report'"
    - Get user info: "Who am I?"

    Args:
        user_id: User ID from URL path
        request: Chat request with message and optional conversation_id
        current_user: User ID from JWT token (via dependency)
        session: Database session
        credentials: JWT credentials

    Returns:
        ChatResponse with AI response and tool call info
    """
    # Verify user ID matches token
    if not verify_user_id_match(current_user, user_id):
        raise HTTPException(status_code=403, detail="User ID mismatch")

    try:
        # Get or create conversation (using sync CRUD since run_agent uses sync Session)
        from app.crud.conversation import get_or_create_conversation, get_messages, add_message, update_conversation_timestamp

        try:
            conversation = get_or_create_conversation(
                session=session,
                user_id=user_id,
                conversation_id=UUID(request.conversation_id) if request.conversation_id else None
            )
        except ValueError:
            # Conversation not found - create a new one instead of failing
            logger.warning(f"Conversation {request.conversation_id} not found, creating new one")
            conversation = get_or_create_conversation(
                session=session,
                user_id=user_id,
                conversation_id=None  # Force create new
            )

        # Load conversation history
        conversation_history = get_messages(
            session=session,
            conversation_id=conversation.id,
            limit=20
        )

        # Get user email and name from JWT if available
        user_email = await get_current_user_email(credentials)
        user_name = await get_current_user_name(credentials)

        # Run the OpenAI Agents SDK agent
        try:
            logger.info(f"Running agent for user {user_id} with message: {request.message[:50]}...")
            response_text, tool_calls_made = await run_agent(
                session=session,
                user_id=user_id,
                email=user_email,
                name=user_name,
                user_message=request.message,
                conversation_history=conversation_history
            )
            logger.info(f"Agent response: {response_text[:100] if response_text else 'None'}...")
        except ValueError as e:
            logger.error(f"Agent initialization failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI service is not configured properly"
            )
        except Exception as e:
            logger.error(f"Agent execution failed: {type(e).__name__}: {e}", exc_info=True)
            # Return a user-friendly error message but don't save it to database
            response_text = "I'm having trouble thinking right now. Please try again."
            tool_calls_made = []

        # Save user message to database
        add_message(
            session=session,
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )

        # Only save successful assistant responses to database, not error messages
        if response_text and "I'm having trouble thinking right now" not in response_text:
            add_message(
                session=session,
                conversation_id=conversation.id,
                role="assistant",
                content=response_text,
                tool_calls={"calls": tool_calls_made} if tool_calls_made else None
            )
        else:
            # If there was an error, don't save the error message to the database
            # Just return the error response to the frontend without storing it
            logger.warning(f"Not saving error response to database for user {user_id}")

        # Update conversation timestamp
        update_conversation_timestamp(session=session, conversation=conversation)

        # Format tool calls for response
        formatted_tool_calls = [
            ToolCall(
                tool=tc["tool"],
                params=tc["params"],
                result=tc["result"]
            )
            for tc in tool_calls_made
        ] if tool_calls_made else None

        return ChatResponse(
            conversation_id=str(conversation.id),
            response=response_text,
            tool_calls=formatted_tool_calls
        )

    except HTTPException:
        raise
    except Exception as e:
        # Rollback session on any database error
        try:
            session.rollback()
        except:
            pass
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again."
        )


@router.get("/conversations", tags=["conversations"])
async def get_user_conversations_endpoint(
    user_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    limit: int = 10
):
    """
    Get all conversations for a user, ordered by most recent.
    """
    # Verify user ID matches token
    if not verify_user_id_match(current_user, user_id):
        raise HTTPException(status_code=403, detail="User ID mismatch")

    try:
        # Get user conversations from async CRUD function
        conversations = await get_user_conversations_async(
            session=db,
            user_id=user_id,
            limit=limit
        )

        # Format conversations for response
        formatted_conversations = []
        for conv in conversations:
            formatted_conversations.append({
                "id": str(conv.id),
                "user_id": conv.user_id,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            })

        return {"conversations": formatted_conversations}

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error for debugging
        import traceback
        logger.error(f"Error fetching user conversations: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching conversations"
        )


# NOTE: This route MUST be defined BEFORE /conversations/{conversation_id}/messages
# to prevent FastAPI from matching "recent" as a conversation_id
@router.get("/conversations/recent", tags=["conversations"])
async def get_recent_conversation(
    user_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get the most recent conversation for a user.
    """
    # Verify user ID matches token
    if not verify_user_id_match(current_user, user_id):
        raise HTTPException(status_code=403, detail="User ID mismatch")

    try:
        # Get user's most recent conversation
        conversations = await get_user_conversations_async(
            session=db,
            user_id=user_id,
            limit=1
        )

        if not conversations:
            # No conversations exist, return 204 No Content
            from fastapi.responses import Response
            return Response(status_code=204)

        # Return the most recent conversation
        recent_conv = conversations[0]
        return {
            "id": str(recent_conv.id),
            "user_id": recent_conv.user_id,
            "created_at": recent_conv.created_at.isoformat(),
            "updated_at": recent_conv.updated_at.isoformat()
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error for debugging
        import traceback
        logger.error(f"Error fetching recent conversation: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching conversation"
        )


@router.get("/conversations/{conversation_id}/messages", tags=["conversations"])
async def get_conversation_messages_endpoint(
    user_id: str,
    conversation_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get all messages for a specific conversation.
    """
    # Verify user ID matches token
    if not verify_user_id_match(current_user, user_id):
        raise HTTPException(status_code=403, detail="User ID mismatch")

    try:
        # Validate conversation_id is a valid UUID
        try:
            uuid_obj = UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid conversation ID format"
            )

        # Verify conversation exists and belongs to the user
        statement = select(Conversation).where(
            Conversation.id == uuid_obj,
            Conversation.user_id == user_id  # Use user_id from URL which matches authenticated user
        )
        result = await db.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found or access denied"
            )

        # Load conversation messages
        messages = await get_messages_async(
            session=db,
            conversation_id=uuid_obj,
            limit=50  # Limit to last 50 messages
        )

        # Format messages for response
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
                "toolCalls": msg.tool_calls  # camelCase for frontend compatibility
            })

        return {"messages": formatted_messages}

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error for debugging
        import traceback
        logger.error(f"Error fetching conversation messages: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching messages"
        )
