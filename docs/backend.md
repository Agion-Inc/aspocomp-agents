# Backend Documentation

## Overview
Python-based REST API server that provides HTTP endpoints for interacting with the Gemini Agent CLI. The backend acts as a bridge between the web frontend and the `gemini_agent.py` module.

## API Architecture

### Technology Stack
- **Framework**: Flask (lightweight, minimal dependencies)
- **HTTP Server**: Flask development server (dev) or Gunicorn (production)
- **API Format**: RESTful JSON API
- **CORS**: Enabled for cross-origin requests
- **Error Handling**: Standardized JSON error responses

## API Endpoints

### 1. POST /api/chat
**Purpose**: Send a message to the Gemini Agent and receive a response

**Request**:
```json
{
  "message": "string",
  "model": "string (optional, default: gemini-2.5-flash)",
  "mcp_enabled": "boolean (optional, default: false)",
  "conversation_id": "string (optional, for conversation continuity)"
}
```

**Response**:
```json
{
  "success": true,
  "response": "string",
  "conversation_id": "string",
  "function_calls": [
    {
      "name": "string",
      "args": {},
      "status": "completed",
      "result": {}
    }
  ],
  "timestamp": "ISO 8601 datetime"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "string",
  "error_code": "string"
}
```

### 2. GET /api/models
**Purpose**: List available Gemini models

**Response**:
```json
{
  "success": true,
  "models": [
    {
      "id": "gemini-2.5-flash",
      "name": "Gemini 2.5 Flash",
      "description": "Fast and efficient model"
    }
  ]
}
```

### 3. DELETE /api/conversation/:conversation_id
**Purpose**: Clear conversation history

**Response**:
```json
{
  "success": true,
  "message": "Conversation cleared"
}
```

### 4. GET /api/health
**Purpose**: Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "timestamp": "ISO 8601 datetime"
}
```

## Service Architecture

### Core Components

#### 1. Chat Service
**File**: `web_chat/backend/chat_service.py`

**Responsibilities**:
- Interface with `gemini_agent.py` module
- Manage conversation state
- Handle function calling logic
- Process responses and format for frontend

**Key Functions**:
```python
def send_message(message: str, model: str, mcp_enabled: bool, conversation_id: str) -> dict
def create_conversation() -> str
def get_conversation(conversation_id: str) -> dict
def clear_conversation(conversation_id: str) -> None
```

#### 2. API Routes
**File**: `web_chat/backend/app.py`

**Responsibilities**:
- Define HTTP endpoints
- Request validation
- Response formatting
- Error handling

**Key Routes**:
- `/api/chat` - Main chat endpoint
- `/api/models` - Model listing
- `/api/conversation/:id` - Conversation management
- `/api/health` - Health check

#### 3. Conversation Manager
**File**: `web_chat/backend/conversation_manager.py`

**Responsibilities**:
- Store conversation history in memory (or database if needed)
- Manage conversation state
- Clean up old conversations

**Storage**:
- In-memory dictionary (simple implementation)
- Optional: Redis or SQLite for persistence

### Integration with gemini_agent.py

The backend will import and use functions from `gemini_agent.py`:

```python
from gemini_agent import (
    load_env_files,
    load_api_key,
    build_cli_tools,
    build_system_prompt,
    execute_cli_function,
    find_function_call_parts,
    make_function_response_part,
    run_single_turn_async,
    run_chat_loop_async  # Adapted for API use
)
```

**Integration Pattern**:
1. Initialize Gemini client using API key from environment
2. Build conversation history from stored messages
3. Call async functions with proper event loop handling
4. Extract function calls and execute them
5. Format response for frontend consumption

## Authentication & Security

### API Key Management
- API key stored in environment variable (`GOOGLE_AI_STUDIO_KEY` or `GOOGLE_API_KEY`)
- Loaded using `load_env_files()` from `gemini_agent.py`
- Never exposed to frontend

### CORS Configuration
```python
# Allow requests from frontend origin
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"]
    }
})
```

### Rate Limiting (Future)
- Simple rate limiting per IP address
- Prevent abuse of API endpoints

## Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "details": {} // Optional additional details
}
```

### Common Error Codes
- `API_KEY_MISSING`: Gemini API key not configured
- `INVALID_REQUEST`: Malformed request data
- `MODEL_NOT_FOUND`: Specified model not available
- `FUNCTION_CALL_FAILED`: CLI function execution error
- `INTERNAL_ERROR`: Unexpected server error

### Error Handling Flow
1. Validate request data
2. Check API key availability
3. Attempt Gemini API call
4. Catch and format exceptions
5. Return standardized error response

## Request/Response Flow

### Chat Request Flow
```
1. Frontend sends POST /api/chat
   ↓
2. Backend validates request
   ↓
3. Load conversation history (if conversation_id provided)
   ↓
4. Build message context with system prompt
   ↓
5. Call gemini_agent.run_single_turn_async()
   ↓
6. Handle function calls (up to 3 iterations)
   ↓
7. Format response with function call details
   ↓
8. Return JSON response to frontend
```

### Function Call Flow
```
1. Gemini response contains function_call part
   ↓
2. Extract function name and arguments
   ↓
3. Call execute_cli_function()
   ↓
4. Wait for execution to complete
   ↓
5. Format function result
   ↓
6. Add function result to conversation context
   ↓
7. Continue conversation with updated context
```

## Configuration

### Environment Variables
```bash
# Required
GOOGLE_AI_STUDIO_KEY=your_api_key_here
# or
GOOGLE_API_KEY=your_api_key_here

# Optional
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
HOST=0.0.0.0
```

### Flask Configuration
```python
# Development
DEBUG = True
HOST = '127.0.0.1'
PORT = 5000

# Production
DEBUG = False
HOST = '0.0.0.0'
PORT = 5000
```

## File Structure

```
web_chat/
├── backend/
│   ├── app.py                    # Flask application and routes
│   ├── chat_service.py           # Core chat logic
│   ├── conversation_manager.py   # Conversation state management
│   ├── config.py                 # Configuration settings
│   ├── errors.py                 # Custom error classes
│   └── requirements.txt          # Python dependencies
```

## Dependencies

### Required Packages
```
flask>=3.0.0
flask-cors>=4.0.0
python-dotenv>=1.0.0
```

### Integration with Existing Code
- Uses `gemini_agent.py` directly (no modifications needed)
- Imports existing functions and utilities
- Leverages existing CLI tool execution logic

## Startup & Deployment

### Development Server
```bash
cd web_chat/backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
export GOOGLE_AI_STUDIO_KEY=your_key
python app.py
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using systemd service (example)
[Unit]
Description=Gemini Agent Web Chat API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/web_chat/backend
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Environment="GOOGLE_AI_STUDIO_KEY=your_key"
Restart=always

[Install]
WantedBy=multi-user.target
```

## Future Enhancements

1. **WebSocket Support**: Real-time streaming responses
2. **Database Integration**: Persistent conversation storage
3. **User Authentication**: Multi-user support with sessions
4. **Rate Limiting**: Prevent API abuse
5. **Logging**: Structured logging for debugging
6. **Metrics**: Performance monitoring
7. **Caching**: Cache frequent responses

## Testing Strategy

### Unit Tests
- Test chat service functions
- Test conversation manager
- Test error handling

### Integration Tests
- Test API endpoints
- Test function calling flow
- Test error scenarios

### Manual Testing
- Test with various message types
- Test function call execution
- Test error handling
- Test conversation continuity

