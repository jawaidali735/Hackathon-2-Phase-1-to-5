"""
Request and response schemas for the chat endpoint.
Per contracts/chat-api.md specification.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID


class ChatRequest(BaseModel):
    """
    Request body for the chat endpoint.
    """
    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Existing conversation ID to continue. Omit to start new conversation."
    )
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="User's natural language message"
    )


class ToolCall(BaseModel):
    """
    Represents a tool call made during chat processing.
    """
    tool: str = Field(description="Name of the tool executed")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters passed to the tool")
    result: Dict[str, Any] = Field(default_factory=dict, description="Result returned by the tool")


class ChatResponse(BaseModel):
    """
    Response body for the chat endpoint.
    """
    conversation_id: UUID = Field(description="Conversation ID (new or existing)")
    response: str = Field(description="AI assistant's text response")
    tool_calls: Optional[List[ToolCall]] = Field(
        default=None,
        description="List of tools executed during processing"
    )
