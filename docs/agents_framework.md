# AI Agents Framework for Aspocomp

## Overview

This document describes the framework architecture for running multiple specialized AI agents for Aspocomp. Each agent operates independently in its own folder while being connected to the main web chat system for unified user interaction.

## Architecture Principles

### 1. Modular Agent Structure
- Each agent is self-contained in its own folder under `agents/`
- Agents can be developed, tested, and deployed independently
- Agents share common infrastructure through the framework

### 2. Integration with Main Web Chat
- All agents connect to the main web chat backend
- Unified API interface for agent communication
- Centralized conversation management
- Shared authentication and authorization

### 3. Independent Operation
- Agents can run as separate services
- Each agent has its own configuration
- Agents can be enabled/disabled independently
- No direct dependencies between agents

### 4. Database and Data Models
- Each agent can have its own database
- Development: SQLite databases in `data/[agent_name]/` directory
- Production: SharePoint lists/databases (shared SharePoint location)
- Each agent defines its own data model/schema
- Privacy: Personal information stored but not exposed to LLM/chatbot

## Folder Structure

```
ai_training/
├── agents/                          # Agent framework root
│   ├── README.md                    # Framework overview and setup
│   ├── base/                        # Base agent classes and utilities
│   │   ├── __init__.py
│   │   ├── agent_base.py           # Base agent class
│   │   ├── agent_interface.py     # Common interfaces
│   │   └── agent_utils.py          # Shared utilities
│   ├── initiative_assistant/        # Initiative Assistant Agent
│   │   ├── README.md
│   │   ├── agent.py                # Main agent implementation
│   │   ├── config.py               # Agent configuration
│   │   ├── database.py             # Database operations
│   │   ├── models.py               # Data models/schemas
│   │   ├── tools/                  # Agent-specific tools
│   │   │   ├── __init__.py
│   │   │   ├── save_initiative.py
│   │   │   └── search_similar.py
│   │   ├── prompts/                # Agent prompts and system messages
│   │   │   └── system_prompt.txt
│   │   └── tests/                  # Agent-specific tests
│   │       └── ...
│   ├── sales/                       # Sales Agent
│   │   ├── README.md
│   │   ├── agent.py
│   │   ├── config.py
│   │   ├── database.py             # Agent-specific database (if needed)
│   │   ├── models.py               # Agent-specific data models
│   │   ├── tools/
│   │   ├── prompts/
│   │   └── tests/
│   └── ...                         # Additional agents
├── data/                            # Agent databases (development)
│   ├── initiative_assistant/
│   │   └── initiatives.db         # SQLite database
│   └── [agent_name]/               # Other agent databases
│       └── [database].db
├── web_chat/                        # Main web chat system
│   ├── backend/
│   │   ├── app.py                  # Main Flask app
│   │   ├── agent_router.py        # Routes agent requests
│   │   ├── agent_registry.py      # Agent discovery and registration
│   │   └── ...
│   └── frontend/
│       ├── index.html              # Main chat interface
│       ├── css/                    # Shared CSS
│       ├── js/                     # Shared JS
│       └── agents/                 # Agent-specific UIs
│           ├── index.html          # Agent listing page
│           ├── initiative_assistant/
│           │   ├── index.html      # Agent UI
│           │   ├── css/
│           │   └── js/
│           └── [agent_name]/       # Other agent UIs
│               ├── index.html
│               ├── css/
│               └── js/
└── docs/
    ├── agents/                     # Agent documentation
    │   ├── README.md               # Agents framework overview
    │   ├── initiative_assistant.md # Initiative assistant docs
    │   ├── sales.md                # Sales agent documentation
    │   └── ...                     # Additional agent docs
    ├── aspocomp_brand_domain.md    # Brand and domain knowledge
    └── agents_framework.md         # This file
```

## Agent Interface Specification

### Base Agent Class

All agents must implement the base agent interface:

```python
class BaseAgent:
    """Base class for all Aspocomp AI agents"""
    
    def __init__(self, config: dict):
        """Initialize agent with configuration"""
        pass
    
    async def process_message(
        self, 
        message: str, 
        conversation_id: str,
        context: dict
    ) -> dict:
        """
        Process a user message and return response
        
        Returns:
            {
                "response": str,
                "agent_id": str,
                "function_calls": list,
                "metadata": dict
            }
        """
        pass
    
    def get_capabilities(self) -> dict:
        """Return agent capabilities and supported functions"""
        pass
    
    def get_system_prompt(self) -> str:
        """Return agent-specific system prompt"""
        pass
    
    def is_enabled(self) -> bool:
        """Check if agent is enabled"""
        pass
```

### Agent Configuration

Each agent should have a `config.py` file:

```python
# agents/sales/config.py
AGENT_CONFIG = {
    "agent_id": "sales",
    "name": "Aspocomp Sales Agent",
    "description": "Handles RFQ requests and sales inquiries",
    "enabled": True,
    "model": "gemini-2.5-flash",
    "temperature": 0.7,
    "max_iterations": 3,
    "tools": [
        "generate_quote",
        "get_product_info",
        "check_availability"
    ],
    "system_prompt_path": "agents/sales/prompts/system_prompt.txt"
}
```

## Integration with Web Chat

### Agent Registry

The main web chat backend includes an agent registry that:
- Discovers available agents
- Registers agents at startup
- Routes messages to appropriate agents
- Manages agent lifecycle

### API Endpoints

Each agent has its own dedicated API endpoint:

**Pattern**: `/api/chat/[agent_id]`

**Examples**:
- `/api/chat/initiative_assistant` - Initiative Assistant Agent
- `/api/chat/sales` - Sales Agent
- `/api/chat/technical_support` - Technical Support Agent

**Request Format**:
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

**Response Format**:
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

### Message Routing

1. **User sends message** → Web chat frontend
2. **Web chat backend** → Agent router determines which agent(s) to use
3. **Agent router** → Routes to appropriate agent endpoint (`/api/chat/[agent_id]`)
4. **Agent processes** → Uses own LLM prompt and tools
5. **Agent returns** → Response formatted and returned to frontend

### Routing Strategies

- **Direct routing**: User selects specific agent
- **Intent-based routing**: Analyze user intent to select agent
- **Multi-agent collaboration**: Route to multiple agents if needed
- **Fallback**: Default to general chat agent if no specific agent matches

## Agent Development Guidelines

### 1. Agent Structure
- Follow the standard folder structure
- Implement base agent interface
- Include comprehensive README.md
- Document in `docs/agents/[agent_name].md`

### 2. System Prompts
- Each agent has its own LLM prompt (`prompts/system_prompt.txt`)
- Use Aspocomp brand voice and tone
- Include domain-specific knowledge
- Reference `aspocomp_brand_domain.md`
- Keep prompts maintainable and version-controlled
- Prompt should guide conversation flow and tool usage

### 3. Tools and Functions
- Each agent defines its own tools/functions
- Tools are agent-specific and stored in `agents/[agent_name]/tools/`
- Use consistent naming conventions
- Document tool parameters and return values
- Handle errors gracefully
- Tools can interact with agent's database

### 4. Database and Data Models
- Each agent can have its own database
- **Development**: SQLite in `data/[agent_name]/[database].db`
- **Production**: SharePoint lists/databases (shared location)
- Define data model/schema in `models.py`
- **Privacy**: Personal information stored but NOT exposed to LLM
- Database operations in `database.py`

### 5. User Interface
- Each agent can have its own custom UI
- **UI Types**: Chat-based, form-based, or custom
- **Location**: `web_chat/frontend/agents/[agent_name]/`
- **Agent Listing**: Main page at `web_chat/frontend/agents/index.html`
- **Navigation**: Link from agent list to agent UI
- **Shared Components**: Use shared CSS variables and components

### 6. Testing
- Unit tests for agent logic
- Integration tests with web chat
- Test agent-specific tools
- Test error handling

### 5. Configuration
- Environment-based configuration
- Support for different environments (dev, staging, prod)
- Secure handling of API keys
- Configurable model selection

## Agent Communication Protocol

### Request Format
```json
{
    "message": "string",
    "conversation_id": "string",
    "agent_id": "string (optional)",
    "context": {
        "user_id": "string",
        "session_id": "string",
        "metadata": {}
    }
}
```

### Response Format
```json
{
    "success": true,
    "response": "string",
    "agent_id": "string",
    "conversation_id": "string",
    "function_calls": [
        {
            "name": "string",
            "args": {},
            "status": "completed|failed",
            "result": {}
        }
    ],
    "metadata": {
        "confidence": 0.0-1.0,
        "suggested_actions": []
    }
}
```

## Security and Privacy

### Authentication
- **SSO Integration**: All agents must support Single Sign-On (SSO) authentication
- Agents inherit authentication from main web chat
- No direct external access to agents
- API key management through main system

### Data Security
- **Encryption**: All data transfer must be encrypted (HTTPS/TLS)
- **Secure Storage**: Sensitive data must be stored securely
- **Secure Communication**: All agent communications must be encrypted

### Data Privacy
- **GDPR Compliance**: All agents must comply with GDPR regulations
- Customer data handled according to GDPR
- No storage of personal data without explicit consent
- No storage of sensitive information in agents
- **Data Minimization**: Only collect and store necessary data
- **Right to Deletion**: Users must be able to request deletion of their data
- Audit logging for compliance

### Access Control
- Role-based access to agents
- Configurable agent availability
- Rate limiting per agent
- Authorization based on user roles and permissions

## Deployment

### Development
- Agents run as part of main web chat backend
- Hot-reload support for development
- Local testing environment

### Production
- Agents can run as separate microservices
- Load balancing for high availability
- Monitoring and logging per agent
- Health checks for each agent

## Monitoring and Observability

### Metrics
- Request count per agent
- Response time per agent (target: <3 seconds)
- Error rate per agent
- Function call success rate
- User satisfaction ratings
- Understanding accuracy (target: >90%)

### Logging
- Structured logging per agent
- Request/response logging
- Question and answer logging for analytics
- Error tracking
- Performance metrics
- User feedback logging

### Health Checks
- Agent availability endpoint
- Dependency checks
- Configuration validation
- Document system connectivity
- Authentication system status

### Analytics
- Usage patterns and common questions
- User satisfaction tracking
- Performance trends
- Error analysis

## Future Enhancements

### Phase 1: Core Framework
- Base agent implementation
- Agent registry and routing
- Basic agent integration

### Phase 2: Advanced Features
- Multi-agent collaboration
- Agent-to-agent communication
- Advanced routing strategies
- Agent learning and improvement

### Phase 3: Enterprise Features
- Agent marketplace
- Custom agent development tools
- Advanced analytics
- A/B testing for agents

## Documentation Requirements

Each agent must include:
1. **README.md**: Overview, setup, usage
2. **docs/agents/[agent_name].md**: Detailed documentation
3. **System prompt documentation**: Explain prompt design
4. **Tool documentation**: Document all tools and functions
5. **API documentation**: If agent exposes APIs

## Agent Requirements

All agents must meet the general requirements specified in `docs/agent_requirements.md`, including:

- **Performance**: Response time under 3 seconds
- **Availability**: 24/7 operation
- **Security**: Encrypted communication, SSO authentication, GDPR compliance
- **Language Support**: Finnish and English
- **Document Retrieval**: Support for PDF, Word, intranet pages, training portal
- **Context Recognition**: Adapt to user's department, role, and situation
- **Feedback Mechanism**: User feedback collection and processing
- **Logging**: Comprehensive logging for analytics and quality monitoring

See `docs/agent_requirements.md` for complete requirements specification.

## Agent Catalog

See `docs/agent_list.md` for the complete list of planned agents, organized by category and priority.

## Database and Data Model Pattern

See `docs/agent_database_pattern.md` for comprehensive guidelines on:
- Agent-specific databases (SQLite for development, SharePoint for production)
- Data model patterns
- Privacy considerations (personal information not exposed to LLM)
- Database operations and tools

## User Interface Pattern

See `docs/agent_ui_pattern.md` for comprehensive guidelines on:
- Agent-specific user interfaces (chat, form, or custom)
- Agent listing page implementation
- UI structure and organization
- API integration patterns
- Styling guidelines

## References

- `docs/agent_requirements.md`: General requirements for all agents
- `docs/agent_database_pattern.md`: Database and data model pattern
- `docs/agent_ui_pattern.md`: User interface pattern for agents
- `docs/agent_list.md`: Complete list of planned agents
- `docs/aspocomp_brand_domain.md`: Brand and domain knowledge
- `docs/architecture.md`: System architecture
- `docs/backend.md`: Backend API documentation
- `docs/frontend.md`: Frontend documentation

