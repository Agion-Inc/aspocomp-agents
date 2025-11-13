# Agent UI Pattern

This document describes the pattern for implementing user interfaces for AI agents in the Aspocomp framework.

## Overview

Each agent can have its own custom user interface, which can be:
- **Chat-based**: Conversational interface similar to the main web chat
- **Form-based**: Structured form for data collection (e.g., Initiative Assistant)
- **Custom**: Any other UI pattern that fits the agent's needs

All agent UIs are accessible from a main agent listing page.

## Architecture

### Main Agent Listing Page

**Location**: `web_chat/frontend/agents/index.html`

**Purpose**: 
- Display list of all available agents
- Provide links to each agent's UI
- Show agent descriptions and status

**Structure**:
```
┌─────────────────────────────────────────┐
│  Header (Aspocomp AI Agents)            │
├─────────────────────────────────────────┤
│                                         │
│  Agent List                             │
│  ┌───────────────────────────────────┐ │
│  │ Initiative Assistant               │ │
│  │ [Description]                      │ │
│  │ [Status: Available]                │ │
│  │ [Open Agent UI →]                  │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │ Sales Agent                        │ │
│  │ [Description]                      │ │
│  │ [Status: Available]                │ │
│  │ [Open Agent UI →]                  │ │
│  └───────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### Agent UI Structure

Each agent has its own UI directory:

```
web_chat/frontend/agents/
├── index.html                    # Main agent listing page
├── initiative_assistant/         # Initiative Assistant UI
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── app.js
│       └── api.js
├── sales/                        # Sales Agent UI
│   ├── index.html
│   ├── css/
│   └── js/
└── [agent_name]/                 # Other agent UIs
    ├── index.html
    ├── css/
    └── js/
```

## UI Patterns

### Pattern 1: Chat-Based UI

**Use Case**: Conversational agents that interact through natural language

**Example**: Sales Agent, Technical Support Agent

**Structure**:
- Similar to main web chat interface
- Agent-specific branding and prompts
- Calls agent's API endpoint: `/api/chat/[agent_id]`

**Files**:
- `index.html` - Chat interface HTML
- `css/styles.css` - Chat styling
- `js/app.js` - Chat logic
- `js/api.js` - API calls to agent endpoint

### Pattern 2: Form-Based UI

**Use Case**: Agents that collect structured data

**Example**: Initiative Assistant (collects initiative information)

**Structure**:
- Multi-step form or wizard
- Form validation
- Progress indicators
- Calls agent's API endpoint with structured data

**Files**:
- `index.html` - Form HTML
- `css/styles.css` - Form styling
- `js/app.js` - Form logic and validation
- `js/api.js` - API calls to agent endpoint

### Pattern 3: Custom UI

**Use Case**: Agents with unique interaction patterns

**Example**: Dashboard agents, visualization agents

**Structure**:
- Custom layout and components
- Agent-specific interactions
- Calls agent's API endpoint

**Files**:
- `index.html` - Custom UI HTML
- `css/styles.css` - Custom styling
- `js/app.js` - Custom logic
- `js/api.js` - API calls to agent endpoint

## Implementation Guidelines

### 1. Agent Listing Page

**File**: `web_chat/frontend/agents/index.html`

**Features**:
- List all registered agents
- Show agent name, description, status
- Link to agent UI
- Responsive grid layout

**API Endpoint**: `/api/agents` (to get list of agents)

**Example Structure**:
```html
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aspocomp AI Agents</title>
    <link rel="stylesheet" href="../css/variables.css">
    <link rel="stylesheet" href="css/agent-list.css">
</head>
<body>
    <header class="agent-list-header">
        <h1>Aspocomp AI Agents</h1>
        <p>Valitse agentti käyttöön</p>
    </header>
    
    <main class="agent-list-container">
        <div class="agent-card" data-agent-id="initiative_assistant">
            <h2>Initiative Assistant</h2>
            <p>Auttaa aloitteiden tekemisessä ja estää päällekkäiset aloitteet</p>
            <span class="agent-status">Available</span>
            <a href="initiative_assistant/" class="agent-link">Avaa agentti →</a>
        </div>
        
        <!-- More agent cards -->
    </main>
</body>
</html>
```

### 2. Agent UI Implementation

#### Chat-Based UI Example

**File**: `web_chat/frontend/agents/[agent_name]/index.html`

```html
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Agent Name] - Aspocomp</title>
    <link rel="stylesheet" href="../../../css/variables.css">
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <div class="agent-container">
        <header class="agent-header">
            <a href="../" class="back-link">← Takaisin agentteihin</a>
            <h1>[Agent Name]</h1>
        </header>
        
        <div class="chat-container">
            <!-- Chat messages -->
        </div>
        
        <div class="input-area">
            <!-- Input form -->
        </div>
    </div>
    
    <script src="js/api.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

**API Integration** (`js/api.js`):
```javascript
const AGENT_ID = 'initiative_assistant';
const API_BASE = '/api/chat';

async function sendMessage(message, conversationId) {
    const response = await fetch(`${API_BASE}/${AGENT_ID}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            conversation_id: conversationId,
            context: {
                user_id: getUserId(),
                department: getDepartment()
            }
        })
    });
    
    return await response.json();
}
```

#### Form-Based UI Example

**File**: `web_chat/frontend/agents/initiative_assistant/index.html`

```html
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Initiative Assistant - Aspocomp</title>
    <link rel="stylesheet" href="../../../css/variables.css">
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <div class="agent-container">
        <header class="agent-header">
            <a href="../" class="back-link">← Takaisin agentteihin</a>
            <h1>Initiative Assistant</h1>
        </header>
        
        <div class="form-container">
            <form id="initiative-form">
                <div class="form-step" data-step="1">
                    <h2>Aloitteen perustiedot</h2>
                    <label>
                        Aloitteen nimi:
                        <input type="text" name="title" required>
                    </label>
                    <label>
                        Kuvaus:
                        <textarea name="description" required></textarea>
                    </label>
                </div>
                
                <div class="form-step" data-step="2">
                    <h2>Yhteystiedot</h2>
                    <!-- More form fields -->
                </div>
                
                <div class="form-navigation">
                    <button type="button" id="prev-btn">Edellinen</button>
                    <button type="button" id="next-btn">Seuraava</button>
                    <button type="submit" id="submit-btn">Lähetä</button>
                </div>
            </form>
        </div>
        
        <div class="similar-initiatives" id="similar-initiatives">
            <!-- Similar initiatives will be shown here -->
        </div>
    </div>
    
    <script src="js/api.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

### 3. Shared Components

**Location**: `web_chat/frontend/shared/`

**Components**:
- Header component
- Navigation component
- Loading indicators
- Error messages
- Common CSS variables

## Styling Guidelines

### Use Shared CSS Variables

All agent UIs should use the shared CSS variables from `web_chat/frontend/css/variables.css`:

```css
/* Use shared variables */
.agent-container {
    background-color: var(--color-bg-primary);
    color: var(--color-black);
    font-family: var(--font-family);
}
```

### Consistent Design

- Follow Aspocomp brand guidelines
- Use consistent spacing and typography
- Maintain accessibility standards (WCAG 2.1 AA)
- Responsive design for mobile devices

## API Integration

### Agent API Endpoint

Each agent UI calls its specific endpoint:

**Pattern**: `/api/chat/[agent_id]`

**Request**:
```json
{
    "message": "string",
    "conversation_id": "string (optional)",
    "context": {
        "user_id": "string",
        "department": "string",
        "role": "string"
    }
}
```

**Response**:
```json
{
    "success": true,
    "response": "string",
    "agent_id": "string",
    "conversation_id": "string",
    "function_calls": [],
    "metadata": {}
}
```

### Agent List API

**Endpoint**: `/api/agents`

**Response**:
```json
{
    "success": true,
    "agents": [
        {
            "agent_id": "initiative_assistant",
            "name": "Initiative Assistant",
            "description": "Helps prevent duplicate initiatives",
            "status": "available",
            "ui_type": "form",
            "ui_path": "/agents/initiative_assistant/"
        }
    ]
}
```

## Implementation Checklist

When creating an agent UI:

- [ ] Create agent UI directory: `web_chat/frontend/agents/[agent_name]/`
- [ ] Create `index.html` with appropriate UI pattern
- [ ] Create `css/styles.css` using shared variables
- [ ] Create `js/app.js` for UI logic
- [ ] Create `js/api.js` for API integration
- [ ] Add agent to agent listing page
- [ ] Test UI responsiveness
- [ ] Test API integration
- [ ] Add navigation back to agent list
- [ ] Document UI pattern used

## Examples

### Initiative Assistant (Form-Based)

- **UI Type**: Multi-step form
- **Purpose**: Collect initiative information
- **Features**: Form validation, progress indicator, similarity check results

### Sales Agent (Chat-Based)

- **UI Type**: Chat interface
- **Purpose**: Conversational sales assistance
- **Features**: Chat messages, function call indicators, product information

## References

- **Frontend Documentation**: `docs/frontend.md`
- **Framework Architecture**: `docs/agents_framework.md`
- **Agent Requirements**: `docs/agent_requirements.md`
- **Agent Implementation Guide**: `.cursor/rules/implement_agent.mdc`

