# API Contract: Chat Endpoint

**Feature**: 004-ai-chat-agent
**Date**: 2026-02-06
**Base URL**: `/api/v1`

---

## POST /api/v1/{user_id}/chat

Send a message to the AI chatbot and receive a response.

### Authentication

**Required**: Bearer JWT token in `Authorization` header

```
Authorization: Bearer <jwt_token>
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User ID (must match JWT `sub` claim) |

### Request Body

```json
{
  "conversation_id": "uuid (optional)",
  "message": "string (required)"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| conversation_id | UUID | No | Valid UUID format | Existing conversation to continue. Omit to start new conversation. |
| message | string | Yes | 1-2000 characters | User's natural language message |

### Request Schema (TypeScript)

```typescript
interface ChatRequest {
  conversation_id?: string;
  message: string;
}
```

### Request Schema (Python/Pydantic)

```python
class ChatRequest(BaseModel):
    conversation_id: Optional[uuid.UUID] = None
    message: str = Field(min_length=1, max_length=2000)
```

---

## Response

### Success Response (200 OK)

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "I've added 'Buy groceries' to your tasks!",
  "tool_calls": [
    {
      "tool": "add_task",
      "params": {
        "title": "Buy groceries"
      },
      "result": {
        "success": true,
        "task": {
          "id": "123e4567-e89b-12d3-a456-426614174000",
          "title": "Buy groceries",
          "completed": false,
          "created_at": "2026-02-06T10:30:00Z"
        }
      }
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| conversation_id | UUID | Conversation ID (new or existing) |
| response | string | AI assistant's text response |
| tool_calls | array | List of tools executed (may be empty) |

### Tool Call Object

```json
{
  "tool": "string",
  "params": {},
  "result": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| tool | string | Name of tool executed |
| params | object | Parameters passed to tool |
| result | object | Tool execution result |

### Response Schema (TypeScript)

```typescript
interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls?: ToolCall[];
}

interface ToolCall {
  tool: string;
  params: Record<string, unknown>;
  result: Record<string, unknown>;
}
```

### Response Schema (Python/Pydantic)

```python
class ToolCall(BaseModel):
    tool: str
    params: dict
    result: dict

class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    response: str
    tool_calls: Optional[List[ToolCall]] = None
```

---

## Error Responses

### 400 Bad Request

Invalid request body or parameters.

```json
{
  "detail": "Message cannot be empty"
}
```

| Condition | Message |
|-----------|---------|
| Empty message | "Message cannot be empty" |
| Message too long | "Message exceeds 2000 character limit" |
| Invalid conversation_id | "Invalid conversation ID format" |

### 401 Unauthorized

Missing or invalid JWT token.

```json
{
  "detail": "Could not validate credentials"
}
```

| Condition | Message |
|-----------|---------|
| Missing token | "Not authenticated" |
| Invalid token | "Could not validate credentials" |
| Expired token | "Token has expired" |

### 403 Forbidden

User ID mismatch between URL and JWT.

```json
{
  "detail": "User ID does not match authenticated user"
}
```

### 404 Not Found

Conversation not found or doesn't belong to user.

```json
{
  "detail": "Conversation not found"
}
```

### 500 Internal Server Error

Server-side error (Cohere API failure, database error).

```json
{
  "detail": "An error occurred while processing your request"
}
```

---

## Example Requests

### Start New Conversation

```bash
curl -X POST "https://api.example.com/api/v1/user123/chat" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

### Continue Existing Conversation

```bash
curl -X POST "https://api.example.com/api/v1/user123/chat" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Now mark it as complete"
  }'
```

---

## Example Responses

### Task Added Successfully

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Done! I've added 'Buy groceries' to your task list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "params": {"title": "Buy groceries"},
      "result": {
        "success": true,
        "task": {
          "id": "123e4567-e89b-12d3-a456-426614174000",
          "title": "Buy groceries",
          "completed": false
        }
      }
    }
  ]
}
```

### List Tasks

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "You have 3 tasks:\n\n1. **Buy groceries** - pending\n2. **Finish report** - pending\n3. **Call mom** - completed",
  "tool_calls": [
    {
      "tool": "list_tasks",
      "params": {"filter": "all"},
      "result": {
        "success": true,
        "tasks": [...],
        "count": 3
      }
    }
  ]
}
```

### Greeting (No Tool Call)

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Hello! I'm your AI task assistant. I can help you add, complete, update, or delete tasks. What would you like to do?",
  "tool_calls": []
}
```

### Who Am I

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "You're logged in as john@example.com.",
  "tool_calls": [
    {
      "tool": "get_current_user",
      "params": {},
      "result": {
        "success": true,
        "user": {
          "user_id": "user123",
          "email": "john@example.com"
        }
      }
    }
  ]
}
```

---

## Rate Limiting

| Limit | Value |
|-------|-------|
| Requests per minute | 30 |
| Concurrent requests | 3 |

When rate limited, response is `429 Too Many Requests`:

```json
{
  "detail": "Rate limit exceeded. Please wait before sending more messages."
}
```

---

## OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: Chat API
  version: 1.0.0
paths:
  /api/v1/{user_id}/chat:
    post:
      summary: Send chat message
      security:
        - bearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatRequest'
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'
        '400':
          description: Bad request
        '401':
          description: Unauthorized
        '403':
          description: Forbidden
        '500':
          description: Server error

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    ChatRequest:
      type: object
      required:
        - message
      properties:
        conversation_id:
          type: string
          format: uuid
        message:
          type: string
          minLength: 1
          maxLength: 2000
    ChatResponse:
      type: object
      required:
        - conversation_id
        - response
      properties:
        conversation_id:
          type: string
          format: uuid
        response:
          type: string
        tool_calls:
          type: array
          items:
            $ref: '#/components/schemas/ToolCall'
    ToolCall:
      type: object
      properties:
        tool:
          type: string
        params:
          type: object
        result:
          type: object
```
