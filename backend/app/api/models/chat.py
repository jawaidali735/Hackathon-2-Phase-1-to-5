"""
Chat API request/response models.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    conversation_id: Optional[str] = None


class ToolCallInfo(BaseModel):
    """Information about a tool call executed during chat."""
    tool: str
    params: Dict[str, Any]
    result: Any


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: str
    response: str
    tool_calls: Optional[List[ToolCallInfo]] = None


# Alias for compatibility
ToolCall = ToolCallInfo
