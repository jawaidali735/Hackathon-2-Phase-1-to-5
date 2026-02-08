"""
OpenAI Agents SDK based agent for AI chatbot task management.
Uses LiteLLM with Groq API for LLM inference.
Implements MCP-style tools for task CRUD operations.
"""
import json
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from contextvars import ContextVar
from uuid import UUID

from agents import Agent, Runner, function_tool, RunResult, ModelSettings
from agents.tool import FunctionTool
from agents.extensions.models.litellm_model import LitellmModel

from sqlmodel import Session
from app.core.config import settings
from app.models.task import TaskCreate, TaskUpdate, TaskComplete
from app.models.message import Message
from app.crud.task import (
    create_task as crud_create_task,
    get_tasks as crud_get_tasks,
    get_task_by_id,
    update_task as crud_update_task,
    update_task_completion,
    delete_task as crud_delete_task,
)

logger = logging.getLogger(__name__)

# Context variables for passing session and user context to tools
_current_session: ContextVar[Optional[Session]] = ContextVar('current_session', default=None)
_current_user_id: ContextVar[Optional[str]] = ContextVar('current_user_id', default=None)
_current_email: ContextVar[Optional[str]] = ContextVar('current_email', default=None)
_current_name: ContextVar[Optional[str]] = ContextVar('current_name', default=None)


@dataclass
class ToolCallRecord:
    """Record of a tool call for response tracking."""
    tool: str
    params: Dict[str, Any]
    result: Dict[str, Any]


# Track tool calls during agent execution
_tool_calls: ContextVar[List[ToolCallRecord]] = ContextVar('tool_calls', default=None)


def _get_session() -> Session:
    """Get current database session from context, recovering from closed/rolled-back state."""
    session = _current_session.get()
    if session is None:
        raise RuntimeError("No database session in context")
    # If session is in a bad state after rollback, recover it
    if not session.is_active:
        session.rollback()
    return session


def _get_user_id() -> str:
    """Get current user ID from context."""
    user_id = _current_user_id.get()
    if user_id is None:
        raise RuntimeError("No user ID in context")
    return user_id


def _record_tool_call(tool_name: str, params: Dict[str, Any], result: Dict[str, Any]):
    """Record a tool call for tracking."""
    calls = _tool_calls.get()
    if calls is not None:
        calls.append(ToolCallRecord(tool=tool_name, params=params, result=result))


# ============================================================================
# MCP Tools using @function_tool decorator
# ============================================================================

@function_tool(strict_mode=False)
def add_task(title: str, description: str = "") -> str:
    """Create a new task."""
    session = _get_session()
    user_id = _get_user_id()

    try:
        # Convert empty string to None for database
        desc = description if description else None
        task_in = TaskCreate(title=title, description=desc)
        task = crud_create_task(session=session, task_in=task_in, user_id=user_id)

        result = {
            "success": True,
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
        }
        _record_tool_call("add_task", {"title": title, "description": description}, result)
        return json.dumps(result)
    except ValueError as e:
        result = {"success": False, "error": str(e)}
        _record_tool_call("add_task", {"title": title, "description": description}, result)
        return json.dumps(result)
    except Exception as e:
        # Rollback session on any database error
        try:
            session.rollback()
        except:
            pass
        logger.error(f"Error creating task: {e}")
        result = {"success": False, "error": "Failed to create task. Please try again."}
        _record_tool_call("add_task", {"title": title, "description": description}, result)
        return json.dumps(result)


@function_tool(strict_mode=False)
def list_tasks(status: str = "all") -> str:
    """List tasks. status: all, pending, or completed."""
    session = _get_session()
    user_id = _get_user_id()

    try:
        # Determine filter based on status
        completed = None
        if status == "completed":
            completed = True
        elif status == "pending":
            completed = False
        # "all" or any other value shows all tasks

        tasks = crud_get_tasks(session=session, user_id=user_id, completed=completed)

        task_list = [
            {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ]

        result = {
            "success": True,
            "tasks": task_list,
            "count": len(task_list)
        }
        _record_tool_call("list_tasks", {"status": status}, result)
        return json.dumps(result)
    except Exception as e:
        # Rollback session on any database error
        try:
            session.rollback()
        except:
            pass
        logger.error(f"Error listing tasks: {e}")
        result = {"success": False, "error": "Failed to list tasks. Please try again."}
        _record_tool_call("list_tasks", {"status": status}, result)
        return json.dumps(result)


@function_tool(strict_mode=False)
def complete_task(task_id: str = "", title: str = "", completed: bool = True) -> str:
    """Mark task as complete or incomplete by ID or title."""
    session = _get_session()
    user_id = _get_user_id()
    # Convert empty strings to None for logic
    tid = task_id if task_id else None
    ttitle = title if title else None
    params = {"task_id": tid, "title": ttitle, "completed": completed}

    try:
        # If title provided instead of task_id, search for matching task
        if not tid and ttitle:
            tasks = crud_get_tasks(session=session, user_id=user_id)
            matching_tasks = [t for t in tasks if ttitle.lower() in t.title.lower()]

            if len(matching_tasks) == 0:
                result = {"success": False, "error": f"No task found matching '{ttitle}'"}
                _record_tool_call("complete_task", params, result)
                return json.dumps(result)
            elif len(matching_tasks) > 1:
                task_names = [t.title for t in matching_tasks]
                result = {"success": False, "error": f"Multiple tasks match '{ttitle}': {task_names}. Please be more specific."}
                _record_tool_call("complete_task", params, result)
                return json.dumps(result)
            tid = str(matching_tasks[0].id)

        if not tid:
            result = {"success": False, "error": "Either task_id or title is required"}
            _record_tool_call("complete_task", params, result)
            return json.dumps(result)

        task = update_task_completion(
            session=session,
            task_id=UUID(tid),
            user_id=user_id,
            task_complete=TaskComplete(completed=completed)
        )

        if not task:
            result = {"success": False, "error": "Task not found"}
            _record_tool_call("complete_task", params, result)
            return json.dumps(result)

        result = {
            "success": True,
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }
        }
        _record_tool_call("complete_task", params, result)
        return json.dumps(result)
    except ValueError as e:
        result = {"success": False, "error": str(e)}
        _record_tool_call("complete_task", params, result)
        return json.dumps(result)
    except Exception as e:
        # Rollback session on any database error
        try:
            session.rollback()
        except:
            pass
        logger.error(f"Error completing task: {e}")
        result = {"success": False, "error": "Failed to update task completion. Please try again."}
        _record_tool_call("complete_task", params, result)
        return json.dumps(result)


@function_tool(strict_mode=False)
def delete_task(task_id: str = "", title: str = "") -> str:
    """Delete a task by ID or title."""
    session = _get_session()
    user_id = _get_user_id()
    # Convert empty strings to None for logic
    tid = task_id if task_id else None
    ttitle = title if title else None
    params = {"task_id": tid, "title": ttitle}

    try:
        # If title provided instead of task_id, search for matching task
        if not tid and ttitle:
            tasks = crud_get_tasks(session=session, user_id=user_id)
            matching_tasks = [t for t in tasks if ttitle.lower() in t.title.lower()]

            if len(matching_tasks) == 0:
                result = {"success": False, "error": f"No task found matching '{ttitle}'"}
                _record_tool_call("delete_task", params, result)
                return json.dumps(result)
            elif len(matching_tasks) > 1:
                task_names = [t.title for t in matching_tasks]
                result = {"success": False, "error": f"Multiple tasks match '{ttitle}': {task_names}. Please be more specific."}
                _record_tool_call("delete_task", params, result)
                return json.dumps(result)
            tid = str(matching_tasks[0].id)

        if not tid:
            result = {"success": False, "error": "Either task_id or title is required"}
            _record_tool_call("delete_task", params, result)
            return json.dumps(result)

        success = crud_delete_task(
            session=session,
            task_id=UUID(tid),
            user_id=user_id
        )

        if not success:
            result = {"success": False, "error": "Task not found"}
            _record_tool_call("delete_task", params, result)
            return json.dumps(result)

        result = {"success": True, "deleted_task_id": tid}
        _record_tool_call("delete_task", params, result)
        return json.dumps(result)
    except Exception as e:
        # Rollback session on any database error
        try:
            session.rollback()
        except:
            pass
        logger.error(f"Error deleting task: {e}")
        result = {"success": False, "error": "Failed to delete task. Please try again."}
        _record_tool_call("delete_task", params, result)
        return json.dumps(result)


@function_tool(strict_mode=False)
def update_task(task_id: str = "", title: str = "", description: str = "", search_title: str = "") -> str:
    """Update a task's title or description by ID or search_title."""
    session = _get_session()
    user_id = _get_user_id()
    # Convert empty strings to None for logic
    tid = task_id if task_id else None
    new_title = title if title else None
    new_desc = description if description else None
    search = search_title if search_title else None
    params = {"task_id": tid, "title": new_title, "description": new_desc, "search_title": search}

    try:
        # If search_title provided instead of task_id, find the task
        if not tid and search:
            tasks = crud_get_tasks(session=session, user_id=user_id)
            matching_tasks = [t for t in tasks if search.lower() in t.title.lower()]

            if len(matching_tasks) == 0:
                result = {"success": False, "error": f"No task found matching '{search}'"}
                _record_tool_call("update_task", params, result)
                return json.dumps(result)
            elif len(matching_tasks) > 1:
                task_names = [t.title for t in matching_tasks]
                result = {"success": False, "error": f"Multiple tasks match '{search}': {task_names}. Please be more specific."}
                _record_tool_call("update_task", params, result)
                return json.dumps(result)
            tid = str(matching_tasks[0].id)

        if not tid:
            result = {"success": False, "error": "Either task_id or search_title is required"}
            _record_tool_call("update_task", params, result)
            return json.dumps(result)

        if not new_title and new_desc is None:
            result = {"success": False, "error": "At least one of title or description is required to update"}
            _record_tool_call("update_task", params, result)
            return json.dumps(result)

        # Only include fields that are being updated (not None)
        update_dict = {}
        if new_title:
            update_dict["title"] = new_title
        if new_desc is not None:  # Allow empty string to clear description
            update_dict["description"] = new_desc

        task_update = TaskUpdate(**update_dict)
        task = crud_update_task(
            session=session,
            task_id=UUID(tid),
            user_id=user_id,
            task_in=task_update
        )

        if not task:
            result = {"success": False, "error": "Task not found"}
            _record_tool_call("update_task", params, result)
            return json.dumps(result)

        result = {
            "success": True,
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }
        }
        _record_tool_call("update_task", params, result)
        return json.dumps(result)
    except ValueError as e:
        result = {"success": False, "error": str(e)}
        _record_tool_call("update_task", params, result)
        return json.dumps(result)
    except Exception as e:
        # Rollback session on any database error
        try:
            session.rollback()
        except:
            pass
        logger.error(f"Error updating task: {e}")
        result = {"success": False, "error": "Failed to update task. Please try again."}
        _record_tool_call("update_task", params, result)
        return json.dumps(result)


@function_tool(strict_mode=False)
def get_current_user(include_details: bool = True) -> str:
    """Get current user's name and email."""
    user_id = _get_user_id()
    email = _current_email.get()
    name = _current_name.get()

    user_info = {"user_id": user_id}
    if include_details:
        user_info["name"] = name or "Unknown"
        user_info["email"] = email or "unknown"

    result = {
        "success": True,
        "user": user_info
    }
    _record_tool_call("get_current_user", {"include_details": include_details}, result)
    return json.dumps(result)


# ============================================================================
# Agent Configuration
# ============================================================================

SYSTEM_INSTRUCTIONS = """You are a friendly task management assistant. You understand English, Urdu, Hindi, and Roman Urdu.

RULES:
- Use tools for all task operations. Never just talk about tasks without acting.
- For "all/sab/sare tasks" operations: call list_tasks() first, then act on each task.
- For identity questions ("who am I?", "name?"): call get_current_user().
- For greetings/chat: respond naturally, no tools needed.
- Show tasks as numbered lists. Never show IDs or technical details.
- Only act on the current message, not history.
- Respond in the user's language.
"""


def _get_available_model() -> tuple[LitellmModel, str]:
    """
    Get the first available model with fallback order: Groq -> OpenAI -> Gemini.

    Returns:
        Tuple of (LitellmModel instance, provider name)

    Raises:
        ValueError: If no API keys are configured
    """
    # Fallback order: Groq -> OpenAI -> Gemini (prioritizing Groq as primary since it's proven to work)
    providers = [
        ("groq", settings.GROQ_API_KEY, "groq/llama-3.3-70b-versatile"),  # Primary provider (known to work)
        ("openai", settings.OPENAI_API_KEY, "gpt-4o-mini"),  # Fallback with OpenAI API key
        ("gemini", settings.GEMINI_API_KEY, "gemini/gemini-2.0-flash"),
    ]

    for provider_name, api_key, model_name in providers:
        if api_key:
            logger.info(f"Using {provider_name} as LLM provider with model {model_name}")
            return LitellmModel(model=model_name, api_key=api_key), provider_name

    raise ValueError("No API keys configured. Please set GROQ_API_KEY or OPENAI_API_KEY")


def create_todo_agent(provider: str = None) -> Agent:
    """
    Create the Todo management agent with MCP tools.
    Uses fallback system: Groq -> OpenAI (with various models).

    Args:
        provider: Optional specific provider to use ("groq", "gemini", "openai")

    Returns:
        Configured Agent instance
    """
    if provider:
        # Use specific provider if requested
        if provider == "groq":
            api_key, model_name = settings.GROQ_API_KEY, "groq/llama-3.3-70b-versatile"
        elif provider == "gemini":
            api_key, model_name = settings.GEMINI_API_KEY, "gemini/gemini-2.0-flash"
        elif provider == "openai":
            api_key, model_name = settings.OPENAI_API_KEY, "gpt-4o-mini"
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not configured")
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        if not api_key:
            raise ValueError(f"{provider.upper()}_API_KEY is not configured")

        model = LitellmModel(model=model_name, api_key=api_key)
        logger.info(f"Using specified provider {provider} with model {model_name}")
    else:
        # Use fallback system
        model, _ = _get_available_model()

    tools = [add_task, list_tasks, complete_task, delete_task, update_task, get_current_user]

    # Fix Groq XML-style tool call generation by adding additionalProperties: false
    # Without this, Groq's llama-3.3-70b generates <function=name {params}> instead of JSON
    for tool in tools:
        if hasattr(tool, 'params_json_schema') and isinstance(tool.params_json_schema, dict):
            tool.params_json_schema["additionalProperties"] = False

    agent = Agent(
        name="TodoAssistant",
        instructions=SYSTEM_INSTRUCTIONS,
        model=model,
        model_settings=ModelSettings(temperature=0.1),
        tools=tools,
    )

    return agent


def _format_messages_for_agent(messages: List[Message]) -> List[Dict[str, str]]:
    """
    Format database messages for agent input.
    Includes tool call summaries in assistant messages so agent remembers what actions it took.
    Filters out error messages to prevent context pollution.

    Args:
        messages: List of Message objects from database

    Returns:
        List of message dicts compatible with agent
    """
    # Error messages that should be filtered from history
    error_messages = [
        "I'm having trouble thinking right now. Please try again.",
        "AI service is not configured properly",
        "An error occurred while processing your request",
    ]

    # Build valid user-assistant pairs only
    # Skip orphan user messages (no assistant response) to avoid confusing the model
    formatted = []
    i = 0
    while i < len(messages):
        msg = messages[i]

        # Skip error messages
        if msg.role == "assistant" and msg.content in error_messages:
            i += 1
            continue

        if msg.role == "user":
            # Check if next message is assistant response
            if i + 1 < len(messages) and messages[i + 1].role == "assistant" and messages[i + 1].content not in error_messages:
                formatted.append({"role": "user", "content": msg.content})
                formatted.append({"role": "assistant", "content": messages[i + 1].content})
                i += 2
                continue
            else:
                # Orphan user message - skip it
                i += 1
                continue
        else:
            # Standalone assistant message - skip
            i += 1
            continue

    # Keep only last 6 messages (3 pairs) to avoid token overflow
    return formatted[-6:]


async def _run_with_agent(agent: Agent, user_message: str, history: List[Dict[str, str]]) -> RunResult:
    """Execute agent with message and history. Retries on Groq tool_use_failed errors."""
    if history:
        messages_input = history + [
            {"role": "user", "content": f"[CURRENT USER MESSAGE - RESPOND TO THIS]\n{user_message}"}
        ]
    else:
        messages_input = user_message

    # Retry up to 3 times for Groq's intermittent XML tool call format errors
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return await Runner.run(agent, messages_input)
        except Exception as e:
            error_str = str(e).lower()
            is_tool_format_error = "tool_use_failed" in error_str or "tool call validation failed" in error_str
            if is_tool_format_error and attempt < max_retries - 1:
                logger.warning(f"Groq tool format error (attempt {attempt + 1}/{max_retries}), retrying...")
                continue
            raise


async def run_agent(
    session: Session,
    user_id: str,
    email: Optional[str],
    user_message: str,
    conversation_history: List[Message],
    name: Optional[str] = None,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Run the agent with the given message and context.
    Implements stateless conversation by loading history from DB.
    Uses fallback system: Groq -> OpenAI -> Gemini (on rate limit errors).

    Args:
        session: Database session for tool execution
        user_id: Authenticated user ID from JWT
        email: User email from JWT
        user_message: The new user message
        conversation_history: Previous messages loaded from database
        name: User display name from JWT or derived from email

    Returns:
        Tuple of (agent_response, tool_calls_made)
    """
    # Set context variables for tools
    session_token = _current_session.set(session)
    user_id_token = _current_user_id.set(user_id)
    email_token = _current_email.set(email)
    name_token = _current_name.set(name)
    tool_calls_token = _tool_calls.set([])

    # Provider: Only use Groq (others have quota/rate limit issues)
    providers = ["groq"]
    provider_keys = {
        "groq": settings.GROQ_API_KEY,
        "openai": settings.OPENAI_API_KEY,
        "gemini": settings.GEMINI_API_KEY,
    }
    # Filter to only available providers
    available_providers = [p for p in providers if provider_keys.get(p)]

    try:
        # Format conversation history
        history = _format_messages_for_agent(conversation_history)

        last_error = None
        for provider in available_providers:
            try:
                logger.info(f"Attempting to use provider: {provider}")
                # Reset tool calls for each attempt
                _tool_calls.set([])

                # Create agent with specific provider
                agent = create_todo_agent(provider=provider)

                # Run agent
                result = await _run_with_agent(agent, user_message, history)

                # Get tool calls that were made
                tool_calls = _tool_calls.get() or []
                tool_calls_data = [
                    {"tool": tc.tool, "params": tc.params, "result": tc.result}
                    for tc in tool_calls
                ]

                logger.info(f"Successfully completed with provider: {provider}")
                return result.final_output, tool_calls_data

            except Exception as e:
                error_str = str(e).lower()
                # Check for rate limit, quota, or API compatibility errors
                should_fallback = (
                    "rate" in error_str or
                    "limit" in error_str or
                    "quota" in error_str or
                    "exceeded" in error_str or
                    "unknown field" in error_str or  # Cohere compatibility issue
                    "strict" in error_str or  # Cohere strict parameter issue
                    "apiconnectionerror" in error_str or
                    "cohereexception" in error_str
                )
                if should_fallback:
                    logger.warning(f"Error on {provider}, trying next provider. Error: {e}")
                    last_error = e
                    continue
                else:
                    # Non-recoverable error, re-raise
                    raise

        # All providers exhausted
        if last_error:
            raise last_error
        raise ValueError("No providers available")

    finally:
        # Reset context variables
        _current_session.reset(session_token)
        _current_user_id.reset(user_id_token)
        _current_email.reset(email_token)
        _current_name.reset(name_token)
        _tool_calls.reset(tool_calls_token)
