# Web Chat Subsystem

## Overview
The Web Chat subsystem provides a modern web-based user interface for interacting with the Gemini Agent CLI. It consists of a frontend (HTML/CSS/JavaScript) and a backend (Flask API) that integrates with the existing `gemini_agent.py` module.

## Subsystem Components

### Frontend Component
**Location**: `web_chat/frontend/`

**Purpose**: Provides the user interface for chat interactions

**Key Files**:
- `index.html` - Main HTML structure
- `css/styles.css` - Styling and layout
- `js/app.js` - Main application logic
- `js/api.js` - API client for backend communication
- `js/ui.js` - UI component rendering
- `js/utils.js` - Utility functions

**Responsibilities**:
- Render chat messages
- Handle user input
- Display function call indicators
- Manage UI state
- Communicate with backend API

**Dependencies**:
- Backend API (Flask server)
- Browser APIs (Fetch, DOM)

### Backend Component
**Location**: `web_chat/backend/`

**Purpose**: Provides REST API for frontend and integrates with gemini_agent.py

**Key Files**:
- `app.py` - Flask application and routes
- `chat_service.py` - Core chat logic and Gemini integration
- `conversation_manager.py` - Conversation state management
- `config.py` - Configuration settings
- `errors.py` - Error handling

**Responsibilities**:
- Handle HTTP requests from frontend
- Integrate with gemini_agent.py module
- Execute function calls via CLI tools
- Manage conversation state
- Format responses for frontend

**Dependencies**:
- Flask framework
- gemini_agent.py module
- CLI tools (npm scripts)

## Integration Points

### With gemini_agent.py
The backend imports and uses functions from `gemini_agent.py`:
- `load_api_key()` - Load API key from environment
- `build_cli_tools()` - Build tool definitions
- `execute_cli_function()` - Execute CLI functions
- `run_single_turn_async()` - Process messages with Gemini

### With CLI Tools
Functions are executed via npm scripts:
- `html_to_md` → `npm run html-to-md`
- `image_optimizer` → `npm run optimize-image`
- `google_search` → `npm run google-search`
- ... (15 total tools)

### With External Services
- Google Gemini API (via google-genai library)
- ChromaDB (for semantic search)
- Replicate API (for video generation)
- OpenAI API (for image generation)

## Data Flow

### Request Flow
```
Frontend → Backend API → gemini_agent.py → Gemini API
                                    ↓
                            CLI Tools (if needed)
                                    ↓
                            External Services
```

### Response Flow
```
Gemini API → gemini_agent.py → Backend API → Frontend
                 ↓
        Function Results (if any)
```

## State Management

### Conversation State
- Stored in memory (backend)
- Conversation ID used to track sessions
- Messages stored in conversation history
- Cleared on explicit request or timeout

### Frontend State
- Message list (array of message objects)
- Current conversation ID
- UI state (loading, error, etc.)
- Selected model
- MCP enabled flag

## Error Handling

### Backend Errors
- API key missing → 500 error with clear message
- Invalid request → 400 error with validation details
- Function call failure → 500 error with function details
- Gemini API error → 500 error with API error message

### Frontend Errors
- Network errors → Display retry option
- API errors → Show user-friendly error message
- Parsing errors → Fallback to plain text display

## Configuration

### Environment Variables
- `GOOGLE_AI_STUDIO_KEY` or `GOOGLE_API_KEY` - Required
- `FLASK_ENV` - Development/production mode
- `PORT` - Server port (default: 5000)
- `HOST` - Server host (default: 127.0.0.1)

### Frontend Configuration
- API endpoint URL (configurable)
- Default model selection
- UI preferences (stored in localStorage)

## Testing Strategy

### Unit Tests
- Test chat service functions
- Test conversation manager
- Test error handling

### Integration Tests
- Test API endpoints
- Test function calling flow
- Test conversation continuity

### E2E Tests
- Test complete chat flow
- Test function call display
- Test error scenarios

## Performance Considerations

### Frontend
- Efficient DOM updates
- Lazy loading for long conversations
- Debounced input handling

### Backend
- Async/await for non-blocking operations
- Efficient state management
- Caching of system prompts

## Security Considerations

### API Key Security
- Never exposed to frontend
- Loaded from environment variables
- Validated before use

### Input Validation
- All user input validated
- Function arguments sanitized
- Prevents injection attacks

### CORS
- Restricted to known origins
- Prevents unauthorized access

## Future Enhancements

### Phase 2
- WebSocket for streaming responses
- Database for persistent storage
- User authentication
- File uploads

### Phase 3
- Advanced conversation management
- Search functionality
- Export/import conversations
- Dark mode

## Related Documentation
- [Frontend Documentation](../frontend.md)
- [Backend Documentation](../backend.md)
- [Architecture Documentation](../architecture.md)

