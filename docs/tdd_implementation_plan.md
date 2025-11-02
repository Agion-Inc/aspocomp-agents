# TDD-Driven Implementation Plan for Web UI

**Approach**: Test-Driven Development (TDD) - Write tests first, then implement code to make tests pass.

**TDD Cycle**: Red → Green → Refactor
1. **Red**: Write failing test
2. **Green**: Write minimal code to make test pass
3. **Refactor**: Improve code while keeping tests passing

---

## Phase 1: Backend Foundation & Health Check

### 1.1 Setup Backend Project Structure
**Status**: ❌ Not started

**Tasks**:
- [ ] Create `web_chat/backend/` directory structure
- [ ] Create `requirements.txt` with Flask, flask-cors, python-dotenv
- [ ] Create `web_chat/backend/__init__.py`
- [ ] Create `web_chat/backend/config.py` for configuration
- [ ] Create `web_chat/backend/errors.py` for custom error classes

**Tests**:
- [ ] Test: `config.py` loads environment variables correctly
- [ ] Test: `errors.py` defines custom error classes

**Implementation**:
- [ ] Implement `config.py` with environment variable loading
- [ ] Implement `errors.py` with `APIError` class

**Validation**:
- [ ] Verify structure exists
- [ ] Verify dependencies install correctly
- [ ] Run tests: `pytest tests/backend/test_config.py`

---

### 1.2 Flask App Setup & Health Endpoint
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: `GET /api/health` returns 200 status
- [ ] Test: `GET /api/health` returns JSON with `status: "healthy"`
- [ ] Test: `GET /api/health` includes `api_key_configured` boolean
- [ ] Test: `GET /api/health` includes `timestamp` in ISO format
- [ ] Test: CORS headers are present in response

**Implementation**:
- [ ] Create `web_chat/backend/app.py` with Flask app
- [ ] Configure CORS for cross-origin requests
- [ ] Implement `GET /api/health` endpoint
- [ ] Add error handling middleware

**Validation**:
- [ ] Run tests: `pytest tests/backend/test_health.py`
- [ ] Manual test: `curl http://localhost:5000/api/health`
- [ ] Verify CORS headers in browser DevTools

---

## Phase 2: Backend API Endpoints

### 2.1 Models Endpoint
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: `GET /api/models` returns 200 status
- [ ] Test: `GET /api/models` returns JSON with `success: true`
- [ ] Test: `GET /api/models` includes `models` array
- [ ] Test: Each model has `id`, `name`, `description` fields
- [ ] Test: Default model `gemini-2.5-flash` is included

**Implementation**:
- [ ] Implement `GET /api/models` endpoint
- [ ] Define model list (hardcoded for MVP)
- [ ] Return JSON response

**Validation**:
- [ ] Run tests: `pytest tests/backend/test_models.py`
- [ ] Manual test: `curl http://localhost:5000/api/models`
- [ ] Verify response structure matches API spec

---

### 2.2 Conversation Manager
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: `create_conversation()` returns unique conversation ID
- [ ] Test: `get_conversation(id)` returns conversation with messages
- [ ] Test: `add_message(id, role, content)` adds message to conversation
- [ ] Test: `clear_conversation(id)` removes all messages
- [ ] Test: `get_conversation()` returns empty list for non-existent ID
- [ ] Test: Conversation messages are stored in order

**Implementation**:
- [ ] Create `web_chat/backend/conversation_manager.py`
- [ ] Implement in-memory storage (dict)
- [ ] Implement `create_conversation()`, `get_conversation()`, `add_message()`, `clear_conversation()`
- [ ] Add UUID generation for conversation IDs

**Validation**:
- [ ] Run tests: `pytest tests/backend/test_conversation_manager.py`
- [ ] Verify conversation state persists during session

---

### 2.3 Chat Service - Basic Integration
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: `send_message()` calls gemini_agent functions correctly
- [ ] Test: `send_message()` handles API key missing error
- [ ] Test: `send_message()` creates conversation if no ID provided
- [ ] Test: `send_message()` uses existing conversation if ID provided
- [ ] Test: `send_message()` returns response with conversation_id
- [ ] Test: `send_message()` handles model parameter

**Implementation**:
- [ ] Create `web_chat/backend/chat_service.py`
- [ ] Import functions from `gemini_agent.py`
- [ ] Implement `send_message()` function
- [ ] Add error handling for API key issues
- [ ] Integrate with conversation_manager

**Validation**:
- [ ] Run tests: `pytest tests/backend/test_chat_service.py`
- [ ] Mock gemini_agent calls in tests
- [ ] Verify integration with conversation_manager

---

### 2.4 Chat Endpoint - Basic Message
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: `POST /api/chat` with valid message returns 200
- [ ] Test: `POST /api/chat` returns JSON with `success: true`
- [ ] Test: `POST /api/chat` includes `response` field with text
- [ ] Test: `POST /api/chat` includes `conversation_id`
- [ ] Test: `POST /api/chat` validates required `message` field (400 if missing)
- [ ] Test: `POST /api/chat` accepts optional `model` parameter
- [ ] Test: `POST /api/chat` accepts optional `conversation_id` parameter
- [ ] Test: `POST /api/chat` handles API errors gracefully (500)
- [ ] Test: `POST /api/chat` validates request JSON format

**Implementation**:
- [ ] Implement `POST /api/chat` endpoint in `app.py`
- [ ] Add request validation
- [ ] Call `chat_service.send_message()`
- [ ] Format response JSON
- [ ] Add error handling

**Validation**:
- [ ] Run tests: `pytest tests/backend/test_chat_endpoint.py`
- [ ] Manual test: `curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d '{"message":"Hello"}'`
- [ ] Verify error responses for invalid requests

---

### 2.5 Chat Endpoint - Function Calls
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: `POST /api/chat` includes `function_calls` array when functions are called
- [ ] Test: Function call object has `name`, `args`, `status`, `result` fields
- [ ] Test: Function call `status` can be "pending", "executing", "completed", "failed"
- [ ] Test: Function call result is included when status is "completed"
- [ ] Test: Function call error is included when status is "failed"

**Implementation**:
- [ ] Extend `chat_service.send_message()` to track function calls
- [ ] Extract function calls from gemini_agent response
- [ ] Format function call data in response
- [ ] Handle function call errors

**Validation**:
- [ ] Run tests: `pytest tests/backend/test_function_calls.py`
- [ ] Test with message that triggers function call (e.g., "What time is it?")
- [ ] Verify function call data structure

---

### 2.6 Clear Conversation Endpoint
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: `DELETE /api/conversation/:id` returns 200 for valid ID
- [ ] Test: `DELETE /api/conversation/:id` returns JSON with `success: true`
- [ ] Test: `DELETE /api/conversation/:id` clears conversation messages
- [ ] Test: `DELETE /api/conversation/:id` returns 404 for non-existent ID
- [ ] Test: `DELETE /api/conversation/:id` validates ID format

**Implementation**:
- [ ] Implement `DELETE /api/conversation/:id` endpoint
- [ ] Call `conversation_manager.clear_conversation()`
- [ ] Add error handling

**Validation**:
- [ ] Run tests: `pytest tests/backend/test_conversation_endpoint.py`
- [ ] Manual test: Create conversation, send message, clear conversation, verify cleared

---

## Phase 3: Frontend Foundation

### 3.1 HTML Structure
**Status**: ❌ Not started

**Tests** (Write first - using DOM testing):
- [ ] Test: HTML file loads without errors
- [ ] Test: Header element exists with title "Gemini Agent Chat"
- [ ] Test: Message container element exists
- [ ] Test: Input area element exists
- [ ] Test: Send button exists
- [ ] Test: Model selector dropdown exists
- [ ] Test: Settings button exists
- [ ] Test: Clear conversation button exists

**Implementation**:
- [ ] Create `web_chat/frontend/index.html`
- [ ] Add header with title and controls
- [ ] Add message container div
- [ ] Add input area with textarea and send button
- [ ] Add script tags for JS files
- [ ] Add link tags for CSS files

**Validation**:
- [ ] Open HTML file in browser
- [ ] Verify structure with browser DevTools
- [ ] Run HTML validator: `html5validator index.html`

---

### 3.2 CSS Foundation - Black & White Theme
**Status**: ❌ Not started

**Tests** (Write first - using CSS testing):
- [ ] Test: CSS variables defined for colors (black, white, grays)
- [ ] Test: Body has white background
- [ ] Test: Container has correct max-width and centering
- [ ] Test: Header has white background with gray border
- [ ] Test: Message container has light gray background

**Implementation**:
- [ ] Create `web_chat/frontend/css/variables.css` with CSS variables
- [ ] Create `web_chat/frontend/css/styles.css` with base styles
- [ ] Define black & white color palette
- [ ] Add reset/normalize CSS
- [ ] Add container and layout styles

**Validation**:
- [ ] Visual inspection in browser
- [ ] Verify colors match design spec
- [ ] Test in different browsers

---

### 3.3 Message Container Styling
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: Message container is scrollable
- [ ] Test: Message container auto-scrolls to bottom on new message
- [ ] Test: User messages are right-aligned with black background
- [ ] Test: Assistant messages are left-aligned with white background
- [ ] Test: Messages have correct padding and spacing

**Implementation**:
- [ ] Style `.messages-container` with scroll and overflow
- [ ] Style `.message--user` with black background, white text, right alignment
- [ ] Style `.message--assistant` with white background, black text, left alignment, border
- [ ] Add spacing between messages
- [ ] Implement auto-scroll functionality

**Validation**:
- [ ] Visual inspection
- [ ] Test scrolling behavior
- [ ] Test message alignment

---

## Phase 4: Frontend API Client

### 4.1 API Client - Basic Functions
**Status**: ❌ Not started

**Tests** (Write first - using Jest or similar):
- [ ] Test: `api.healthCheck()` makes GET request to `/api/health`
- [ ] Test: `api.healthCheck()` returns parsed JSON response
- [ ] Test: `api.healthCheck()` handles network errors
- [ ] Test: `api.getModels()` makes GET request to `/api/models`
- [ ] Test: `api.getModels()` returns models array
- [ ] Test: `api.sendMessage(message, options)` makes POST request to `/api/chat`
- [ ] Test: `api.sendMessage()` includes message in request body
- [ ] Test: `api.sendMessage()` includes optional parameters (model, conversation_id)
- [ ] Test: `api.clearConversation(id)` makes DELETE request to `/api/conversation/:id`

**Implementation**:
- [ ] Create `web_chat/frontend/js/api.js`
- [ ] Implement `healthCheck()` function
- [ ] Implement `getModels()` function
- [ ] Implement `sendMessage()` function
- [ ] Implement `clearConversation()` function
- [ ] Add error handling

**Validation**:
- [ ] Run tests: `pytest tests/frontend/test_api.js` (or appropriate test runner)
- [ ] Test in browser console
- [ ] Mock fetch API for testing

---

### 4.2 API Client - Error Handling
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: `api.sendMessage()` handles 400 errors with user-friendly message
- [ ] Test: `api.sendMessage()` handles 500 errors with user-friendly message
- [ ] Test: `api.sendMessage()` handles network failures
- [ ] Test: `api.sendMessage()` handles JSON parse errors
- [ ] Test: Error messages are returned in consistent format

**Implementation**:
- [ ] Add error handling to all API functions
- [ ] Create error message formatter
- [ ] Add retry logic for network errors (optional)

**Validation**:
- [ ] Run error handling tests
- [ ] Test with backend offline
- [ ] Test with invalid requests

---

## Phase 5: Frontend UI Components

### 5.1 Message Rendering
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: `renderMessage(message)` creates correct DOM structure
- [ ] Test: `renderMessage()` sets correct CSS classes for user/assistant
- [ ] Test: `renderMessage()` escapes HTML in content
- [ ] Test: `renderMessage()` renders timestamp correctly
- [ ] Test: `renderMessage()` handles empty messages
- [ ] Test: `renderMessage()` appends message to container

**Implementation**:
- [ ] Create `web_chat/frontend/js/ui.js`
- [ ] Implement `renderMessage()` function
- [ ] Add HTML escaping for security
- [ ] Add timestamp formatting
- [ ] Style message bubbles

**Validation**:
- [ ] Run tests
- [ ] Visual inspection in browser
- [ ] Test with various message types

---

### 5.2 Markdown Rendering
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: `renderMarkdown(text)` converts markdown to HTML
- [ ] Test: `renderMarkdown()` handles code blocks
- [ ] Test: `renderMarkdown()` handles links
- [ ] Test: `renderMarkdown()` handles bold/italic text
- [ ] Test: `renderMarkdown()` handles lists

**Implementation**:
- [ ] Add markdown parser library (e.g., marked.js) or implement basic parser
- [ ] Implement `renderMarkdown()` function
- [ ] Style code blocks with monochrome theme
- [ ] Style links (black text, underline on hover)

**Validation**:
- [ ] Run tests
- [ ] Test with various markdown content
- [ ] Verify styling matches design

---

### 5.3 Input Area & Send Functionality
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: Input field accepts text input
- [ ] Test: Send button is disabled when input is empty
- [ ] Test: Send button is enabled when input has text
- [ ] Test: Pressing Enter sends message
- [ ] Test: Shift+Enter creates new line instead of sending
- [ ] Test: `sendMessage()` clears input after sending
- [ ] Test: `sendMessage()` shows loading state
- [ ] Test: `sendMessage()` handles errors and shows error message

**Implementation**:
- [ ] Implement input field event handlers
- [ ] Implement send button click handler
- [ ] Implement Enter key handler
- [ ] Add input validation
- [ ] Add loading state UI
- [ ] Integrate with API client

**Validation**:
- [ ] Run tests
- [ ] Test in browser
- [ ] Test keyboard shortcuts
- [ ] Test error scenarios

---

## Phase 6: Function Call Indicators

### 6.1 Function Call UI Component
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: `renderFunctionCall(fc)` creates correct DOM structure
- [ ] Test: `renderFunctionCall()` displays function name
- [ ] Test: `renderFunctionCall()` displays status (pending/executing/completed/failed)
- [ ] Test: `renderFunctionCall()` shows spinner for pending/executing
- [ ] Test: `renderFunctionCall()` shows result for completed
- [ ] Test: `renderFunctionCall()` shows error for failed
- [ ] Test: `renderFunctionCall()` has correct styling (dark gray background)

**Implementation**:
- [ ] Implement `renderFunctionCall()` function
- [ ] Create function call indicator component
- [ ] Add spinner animation (black/white)
- [ ] Style function call indicators
- [ ] Add collapsible details section

**Validation**:
- [ ] Run tests
- [ ] Visual inspection
- [ ] Test with different function call statuses

---

### 6.2 Function Call Integration
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: Function calls appear in message when received from API
- [ ] Test: Function call status updates from pending → executing → completed
- [ ] Test: Multiple function calls are displayed correctly
- [ ] Test: Function call errors are displayed correctly

**Implementation**:
- [ ] Integrate function call rendering with message rendering
- [ ] Update function call status dynamically
- [ ] Handle function call results
- [ ] Add error handling for function calls

**Validation**:
- [ ] Run tests
- [ ] Test with messages that trigger function calls
- [ ] Verify status updates work correctly

---

## Phase 7: Integration & Polish

### 7.1 Conversation Continuity
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: Conversation ID is stored and reused
- [ ] Test: New conversation creates new ID
- [ ] Test: Clear conversation resets ID
- [ ] Test: Conversation history persists during session

**Implementation**:
- [ ] Store conversation_id in app state
- [ ] Pass conversation_id to API calls
- [ ] Handle conversation creation
- [ ] Implement clear conversation functionality

**Validation**:
- [ ] Run tests
- [ ] Test multi-turn conversations
- [ ] Verify conversation continuity

---

### 7.2 Settings Modal
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: Settings button opens modal
- [ ] Test: Modal displays model selector
- [ ] Test: Modal displays MCP toggle
- [ ] Test: Modal can be closed
- [ ] Test: Settings changes are saved
- [ ] Test: Settings persist across page reloads (localStorage)

**Implementation**:
- [ ] Create settings modal HTML
- [ ] Style modal (black & white theme)
- [ ] Implement open/close functionality
- [ ] Add model selector
- [ ] Add MCP toggle
- [ ] Save settings to localStorage

**Validation**:
- [ ] Run tests
- [ ] Visual inspection
- [ ] Test settings persistence

---

### 7.3 Responsive Design
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: Layout works on mobile (< 768px)
- [ ] Test: Layout works on tablet (768px - 1024px)
- [ ] Test: Layout works on desktop (> 1024px)
- [ ] Test: Touch interactions work on mobile

**Implementation**:
- [ ] Add responsive CSS breakpoints
- [ ] Adjust layout for mobile
- [ ] Test touch interactions
- [ ] Optimize for different screen sizes

**Validation**:
- [ ] Test on different devices
- [ ] Use browser DevTools responsive mode
- [ ] Verify usability on mobile

---

### 7.4 Accessibility
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: All interactive elements have ARIA labels
- [ ] Test: Keyboard navigation works (Tab, Enter, Escape)
- [ ] Test: Focus indicators are visible
- [ ] Test: Screen reader can navigate interface
- [ ] Test: Color contrast meets WCAG AA standards

**Implementation**:
- [ ] Add ARIA labels to all interactive elements
- [ ] Ensure keyboard navigation works
- [ ] Add focus indicators
- [ ] Test with screen reader
- [ ] Verify color contrast

**Validation**:
- [ ] Test with keyboard only
- [ ] Test with screen reader (VoiceOver, NVDA)
- [ ] Use accessibility checker tools

---

### 7.5 Error Handling & User Feedback
**Status**: ❌ Not started

**Tests** (Write first):
- [ ] Test: Error messages are displayed to user
- [ ] Test: Loading states are shown during API calls
- [ ] Test: Network errors show retry option
- [ ] Test: Validation errors are shown for invalid input

**Implementation**:
- [ ] Add error message display component
- [ ] Add loading indicators
- [ ] Add retry functionality
- [ ] Add input validation feedback

**Validation**:
- [ ] Run tests
- [ ] Test error scenarios
- [ ] Verify user feedback is clear

---

## Phase 8: End-to-End Testing

### 8.1 E2E Test Suite
**Status**: ❌ Not started

**Tests** (Write with Playwright or Cypress):
- [ ] Test: User can send message and receive response
- [ ] Test: User can send multiple messages in conversation
- [ ] Test: Function calls are displayed correctly
- [ ] Test: User can clear conversation
- [ ] Test: User can change model in settings
- [ ] Test: Error handling works correctly
- [ ] Test: Responsive design works on mobile

**Implementation**:
- [ ] Set up E2E testing framework
- [ ] Write E2E test scenarios
- [ ] Configure test environment
- [ ] Run E2E tests

**Validation**:
- [ ] All E2E tests pass
- [ ] Tests cover main user flows
- [ ] Tests run in CI/CD (if applicable)

---

## Testing Infrastructure

### Test Setup
**Status**: ❌ Not started

**Tasks**:
- [ ] Set up pytest for backend tests
- [ ] Set up test framework for frontend (Jest/Mocha or similar)
- [ ] Create test directory structure
- [ ] Add test configuration files
- [ ] Add test scripts to package.json/requirements.txt
- [ ] Set up test coverage reporting

---

## Implementation Order Summary

1. **Backend Foundation** (Phase 1)
   - Setup → Health endpoint → Models endpoint

2. **Backend API** (Phase 2)
   - Conversation manager → Chat service → Chat endpoint → Function calls → Clear endpoint

3. **Frontend Foundation** (Phase 3)
   - HTML structure → CSS foundation → Message container styling

4. **Frontend API Client** (Phase 4)
   - Basic API functions → Error handling

5. **Frontend UI Components** (Phase 5)
   - Message rendering → Markdown → Input area

6. **Function Call Features** (Phase 6)
   - Function call UI → Integration

7. **Integration & Polish** (Phase 7)
   - Conversation continuity → Settings → Responsive → Accessibility → Error handling

8. **E2E Testing** (Phase 8)
   - Complete test suite

---

## Testing Commands

```bash
# Backend tests
pytest tests/backend/
pytest tests/backend/test_health.py -v
pytest tests/backend/test_chat_endpoint.py -v

# Frontend tests
npm test  # or appropriate test runner
npm run test:watch

# E2E tests
npm run test:e2e

# Coverage
pytest --cov=web_chat/backend tests/
npm run test:coverage
```

---

## Definition of Done

Each task is considered done when:
- ✅ All tests pass
- ✅ Code is implemented according to design spec
- ✅ Manual testing confirms functionality
- ✅ Code follows project style guidelines
- ✅ Documentation is updated (if needed)
- ✅ No linting errors

