# Architecture Documentation

## Tech Stack

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS variables
- **JavaScript (ES6+)**: Vanilla JavaScript, no frameworks
- **Fetch API**: HTTP requests to backend

### Backend
- **Python 3.8+**: Runtime environment
- **Flask 3.0+**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **google-genai**: Gemini API client (from gemini_agent.py)

### Integration
- **gemini_agent.py**: Core agent logic (existing module)
- **CLI Tools**: npm scripts for function execution

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Frontend (HTML/CSS/JS)                          │  │
│  │  - index.html                                    │  │
│  │  - styles.css                                    │  │
│  │  - app.js                                        │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        │ HTTP/REST API
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Flask Backend Server                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │  API Routes (app.py)                             │  │
│  │  - POST /api/chat                                 │  │
│  │  - GET /api/models                               │  │
│  │  - DELETE /api/conversation/:id                  │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Chat Service (chat_service.py)                  │  │
│  │  - Message processing                            │  │
│  │  - Conversation management                       │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        │ Import & Call
                        ↓
┌─────────────────────────────────────────────────────────┐
│         gemini_agent.py Module                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  - load_api_key()                                │  │
│  │  - build_cli_tools()                             │  │
│  │  - execute_cli_function()                        │  │
│  │  - run_single_turn_async()                       │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        │ Function Calls
                        ↓
┌─────────────────────────────────────────────────────────┐
│              CLI Tools (npm scripts)                    │
│  - html-to-md                                          │
│  - image-optimizer                                     │
│  - download-file                                       │
│  - google-search                                       │
│  - data-indexing                                       │
│  - semantic-search                                     │
│  - ... (15 total tools)                                │
└─────────────────────────────────────────────────────────┘
                        │ API Calls
                        ↓
┌─────────────────────────────────────────────────────────┐
│         External Services                              │
│  - Google Gemini API                                   │
│  - ChromaDB (if used)                                  │
│  - Replicate API (for video generation)              │
│  - OpenAI API (for image generation)                  │
└─────────────────────────────────────────────────────────┘
```

## Folder Structure

```
ai_training/
├── gemini_agent.py              # Existing agent module
├── web_chat/                     # New web UI project
│   ├── frontend/
│   │   ├── index.html
│   │   ├── css/
│   │   │   ├── styles.css
│   │   │   └── variables.css
│   │   ├── js/
│   │   │   ├── app.js            # Main application
│   │   │   ├── api.js            # API client
│   │   │   ├── ui.js             # UI components
│   │   │   └── utils.js          # Utilities
│   │   └── assets/
│   │       ├── icons/
│   │       └── images/
│   └── backend/
│       ├── app.py                # Flask app
│       ├── chat_service.py      # Chat logic
│       ├── conversation_manager.py
│       ├── config.py
│       ├── errors.py
│       └── requirements.txt
└── docs/
    ├── frontend.md
    ├── backend.md
    └── architecture.md
```

## Data Flow

### Chat Message Flow

1. **User Input**
   - User types message in frontend
   - Frontend validates input
   - Frontend sends POST request to `/api/chat`

2. **Backend Processing**
   - Flask receives request
   - Chat service validates and processes request
   - Loads conversation history (if exists)
   - Builds message context with system prompt

3. **Gemini Agent Integration**
   - Calls `run_single_turn_async()` from gemini_agent.py
   - Agent processes message with Gemini API
   - Agent may call functions (up to 3 iterations)
   - Each function call executes via `execute_cli_function()`

4. **Function Execution**
   - Function name and args extracted
   - npm script executed via subprocess
   - Result captured and formatted
   - Result added to conversation context

5. **Response Generation**
   - Final response generated by Gemini
   - Response formatted with function call details
   - JSON response sent to frontend

6. **Frontend Display**
   - Frontend receives response
   - Message displayed in chat UI
   - Function calls shown with indicators
   - User can continue conversation

## Component Interactions

### Frontend Components
```
app.js (Main Application)
├── api.js (API Client)
│   └── fetch('/api/chat', ...)
├── ui.js (UI Components)
│   ├── renderMessage()
│   ├── renderFunctionCall()
│   └── updateUI()
└── utils.js (Utilities)
    ├── formatTimestamp()
    └── escapeHtml()
```

### Backend Components
```
app.py (Flask Routes)
├── chat_service.py
│   ├── send_message()
│   ├── create_conversation()
│   └── clear_conversation()
└── conversation_manager.py
    ├── store_message()
    └── get_conversation()
```

## Security Considerations

### API Key Security
- API keys stored in environment variables only
- Never exposed to frontend
- Loaded securely via `load_env_files()` from gemini_agent.py

### CORS Configuration
- Restricted to known frontend origins
- Prevents unauthorized cross-origin requests

### Input Validation
- All user input validated on backend
- Prevents injection attacks
- Sanitizes function arguments

### Error Handling
- No sensitive information leaked in errors
- Generic error messages to frontend
- Detailed errors logged server-side only

## Performance Considerations

### Frontend
- Efficient DOM manipulation
- Lazy loading for long conversations
- Debounced input handling
- Optimized CSS animations

### Backend
- Async/await for non-blocking operations
- Efficient conversation state management
- Connection pooling for external APIs
- Caching of system prompts and tool definitions

### Scalability
- Stateless API design (conversation state in memory)
- Horizontal scaling possible with external state store
- No database required for MVP
- Can add Redis/SQLite for production

## Testing Frameworks

### Frontend Testing
- Manual testing with browser DevTools
- Console-based testing
- Future: Jest or similar for unit tests

### Backend Testing
- Python unittest framework
- Flask test client for API testing
- Mock Gemini API responses
- Test function call execution

## Deployment

### Development
- Frontend: Static files served directly (no build step)
- Backend: Flask development server
- Both run on localhost

### Production
- Frontend: Served via nginx or Flask static file serving
- Backend: Gunicorn with multiple workers
- Environment variables for configuration
- Reverse proxy (nginx) for HTTPS

## Dependencies

### Frontend Dependencies
- None (vanilla HTML/CSS/JS)
- Optional: Syntax highlighting library for code blocks

### Backend Dependencies
```txt
flask>=3.0.0
flask-cors>=4.0.0
python-dotenv>=1.0.0
```

### Existing Dependencies (from gemini_agent.py)
- google-genai
- Subprocess (standard library)
- asyncio (standard library)

## Development Workflow

### Setup
1. Install Python dependencies: `pip install -r web_chat/backend/requirements.txt`
2. Configure API key in environment
3. Start backend: `python web_chat/backend/app.py`
4. Open frontend: `open web_chat/frontend/index.html`

### Development Process
1. Make changes to frontend files
2. Refresh browser to see changes
3. Backend changes require server restart
4. Test with various message types and function calls

## Future Enhancements

### Phase 2 Features
- WebSocket support for streaming responses
- Database for persistent conversation storage
- User authentication and multi-user support
- File upload support
- Image display in chat

### Phase 3 Features
- Advanced conversation management
- Export/import conversations
- Search functionality
- Dark mode
- Customizable themes

