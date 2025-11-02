# Frontend Documentation

## Overview
Modern chat interface for the Gemini Agent CLI, providing a web-based user experience for interacting with the Gemini AI agent and its extensive tool suite.

## UI/UX Design Principles

### 1. Modern Chat Interface
- **Clean, minimal design** inspired by modern chat applications (ChatGPT, Claude, etc.)
- **Conversation-centric** layout with clear message bubbles
- **Responsive design** that works on desktop, tablet, and mobile devices
- **Accessible** following WCAG 2.1 AA guidelines

### 2. Visual Design
- **Color Scheme**: 
  - Strict black & white palette with grayscale accents
  - User messages: Black (#000000) background with white (#ffffff) text
  - Assistant messages: White (#ffffff) background with black (#000000) text, subtle border (#e5e5e5)
  - Function call indicators: Dark gray (#333333) background with white text
  - Background: Pure white (#ffffff) with subtle gray (#fafafa) for message area
  - Borders and dividers: Light gray (#e5e5e5) for subtle separation
  - Hover states: Light gray (#f5f5f5) backgrounds
  - No colored accents - purely monochrome
- **Typography**: 
  - System fonts: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
  - Monospace font for code blocks: 'Courier New', monospace
  - High contrast text for readability
- **Spacing**: Generous padding and margins for readability
- **Shadows**: Subtle black/gray shadows (#000000 with low opacity) for depth and message separation

### 3. Layout Structure

```
┌─────────────────────────────────────────┐
│  Header (Gemini Agent - Chat)          │
│  [Model Selector] [Settings] [Clear]   │
├─────────────────────────────────────────┤
│                                         │
│  Chat Messages Area (scrollable)        │
│  ┌───────────────────────────────────┐ │
│  │ User: Message text...              │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │ Assistant: Response text...       │ │
│  │ [Function Call Indicator]          │ │
│  └───────────────────────────────────┘ │
│                                         │
├─────────────────────────────────────────┤
│  Input Area                              │
│  [Text Input] [Send Button] [Attach]   │
└─────────────────────────────────────────┘
```

## Views/Screens

### Main Chat View
**Purpose**: Primary interface for conversation with Gemini Agent

**Components**:
1. **Header Bar**
   - Title: "Gemini Agent Chat"
   - Model selector dropdown (default: gemini-2.5-flash)
   - Settings icon (gear) - opens settings modal
   - Clear conversation button (trash icon)

2. **Message Container**
   - Scrollable area containing all messages
   - Auto-scroll to bottom on new messages
   - Lazy loading for message history (if implemented)

3. **Message Bubble (User)**
   - Right-aligned
   - Black background (#000000)
   - White text (#ffffff)
   - Timestamp (hover to show, gray text)
   - Avatar/icon on the right (black/white)

4. **Message Bubble (Assistant)**
   - Left-aligned
   - White background (#ffffff)
   - Black text (#000000)
   - Subtle border (#e5e5e5) for separation
   - Timestamp (hover to show, gray text)
   - Avatar/icon on the left (black/white)
   - Markdown rendering support
   - Code block syntax highlighting (monochrome theme)
   - Link detection and rendering (black text, underline on hover)

5. **Function Call Indicator**
   - Shows when assistant is calling a function
   - Dark gray background (#333333)
   - White text (#ffffff)
   - Subtle spinner animation (black/white)
   - Function name and parameters preview
   - Collapsible section showing execution details
   - Borders in gray (#e5e5e5)

6. **Input Area**
   - Multi-line text input with auto-resize
   - Placeholder: "Type your message..."
   - Send button (enabled only when text entered)
   - File attachment button (for future image uploads)
   - Character counter (optional)

### Settings Modal
**Purpose**: Configure chat behavior and preferences

**Settings**:
- Model selection (gemini-2.5-flash, gemini-2.5-pro, etc.)
- Enable/disable MCP tools
- Max function call iterations (default: 3)
- Temperature setting (if exposed)
- Enable/disable streaming (if implemented)
- Clear conversation history
- Export conversation history

## UI Components

### Message Component
```javascript
// Pseudocode structure
Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  functionCalls?: FunctionCall[]
  error?: string
}
```

### Function Call Indicator Component
```javascript
// Pseudocode structure
FunctionCall {
  name: string
  args: object
  status: 'pending' | 'executing' | 'completed' | 'failed'
  result?: object
  startTime?: Date
  endTime?: Date
}
```

## User Interactions

### 1. Sending Messages
- User types message in input area
- Press Enter (or Shift+Enter for new line) to send
- Click Send button to send
- Message appears immediately in chat
- Shows "thinking..." indicator while waiting for response
- Response streams in (if streaming implemented) or appears when complete

### 2. Function Call Visibility
- When function is called, show indicator with function name
- Expandable section shows parameters and execution progress
- Show result summary when function completes
- Distinguish successful vs failed function calls using gray tones (dark gray for success, darker gray for failures)

### 3. Message Actions
- Copy message text (copy icon)
- Regenerate response (if implemented)
- Edit and resend (user messages only)
- Delete message (with confirmation)

### 4. Code Block Interaction
- Syntax highlighting for code blocks
- Copy code button for each code block
- Language indicator (if detected)

## Styling Guidelines

### CSS Architecture
- **Plain CSS** (no frameworks like Bootstrap or Tailwind)
- **CSS Variables** for black & white theme values
- **Mobile-first** responsive design
- **BEM naming convention** (optional but recommended)
- **Monochrome palette**: Only black (#000000), white (#ffffff), and grayscale shades (#fafafa, #f5f5f5, #e5e5e5, #333333)

### Key CSS Classes
- `.chat-container` - Main container (white background)
- `.chat-header` - Header bar (white with gray border)
- `.messages-container` - Scrollable message area (light gray background)
- `.message` - Individual message bubble
- `.message--user` - User message styling (black background, white text)
- `.message--assistant` - Assistant message styling (white background, black text, gray border)
- `.message--function-call` - Function call indicator (dark gray background, white text)
- `.input-area` - Input section (white with gray border)
- `.input-field` - Text input field (white background, black text, gray border)
- `.button` - Button base styles
- `.button--primary` - Primary action button (black background, white text)
- `.button--secondary` - Secondary action button (white background, black text, gray border)

### Responsive Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## Accessibility Features

1. **Keyboard Navigation**
   - Tab navigation through all interactive elements
   - Enter to send message
   - Escape to close modals

2. **Screen Reader Support**
   - ARIA labels for all interactive elements
   - Role attributes for message regions
   - Live regions for dynamic content updates

3. **Visual Accessibility**
   - High contrast ratios (WCAG AA)
   - Focus indicators
   - Clear visual feedback for all actions

## Future Enhancements (Not in Initial Implementation)

1. **Inverted Dark Mode**: Pure white text on black background option
2. **Message Search**: Search through conversation history
3. **Export/Import**: Save conversations as JSON/Markdown
4. **File Uploads**: Drag-and-drop file attachments
5. **Image Display**: Show generated images inline in chat (grayscale conversion)
6. **Streaming Responses**: Real-time token streaming
7. **Voice Input**: Speech-to-text for messages
8. **Voice Output**: Text-to-speech for responses
9. **Typography Options**: Font weight and size customization for readability

## File Structure

```
web_chat/
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── css/
│   │   ├── styles.css      # Main stylesheet
│   │   └── variables.css   # CSS variables
│   ├── js/
│   │   ├── app.js          # Main application logic
│   │   ├── api.js          # API client
│   │   ├── ui.js           # UI components
│   │   └── utils.js        # Utility functions
│   └── assets/
│       ├── icons/          # SVG icons
│       └── images/         # Images
```

## Implementation Notes

- **No Build Step**: Plain HTML, CSS, and JavaScript - no compilation needed
- **Vanilla JavaScript**: No frameworks (React, Vue, etc.) - pure ES6+
- **API Communication**: Fetch API for HTTP requests
- **State Management**: Simple object-based state management
- **Error Handling**: User-friendly error messages with retry options
- **Loading States**: Clear indicators for async operations

