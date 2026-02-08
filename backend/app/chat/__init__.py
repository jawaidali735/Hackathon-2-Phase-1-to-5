"""
Chat module for AI-powered chatbot functionality.

This module provides:
- OpenAI Agents SDK agent with Groq API via LiteLLM
- MCP-style tools for task management using @function_tool
- Request/response schemas for chat endpoint
"""
from app.chat.schemas import ChatRequest, ChatResponse, ToolCall
from app.chat.agent import run_agent, create_todo_agent

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "ToolCall",
    "run_agent",
    "create_todo_agent",
]
