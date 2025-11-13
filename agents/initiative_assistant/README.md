# Initiative Assistant Agent

## Overview

The Initiative Assistant Agent helps prevent duplicate initiatives by checking existing initiatives when a new one is proposed. It collects initiative information through an interactive chatbot and maintains its own database of initiatives.

## Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key (GOOGLE_AI_STUDIO_KEY or GOOGLE_API_KEY)
- Flask backend running

### Running the Agent

1. Ensure API key is set:
   ```bash
   export GOOGLE_AI_STUDIO_KEY=your_api_key
   ```

2. Start the Flask backend:
   ```bash
   cd web_chat/backend
   python app.py
   ```

3. Access the agent:
   - Agent listing: http://localhost:5001/agents/
   - Direct agent UI: http://localhost:5001/agents/initiative_assistant/

## Features

- **Interactive Data Collection**: Chatbot guides users through providing initiative information
- **Similarity Detection**: Searches database for similar existing initiatives
- **Privacy Protection**: Personal information stored but not exposed to LLM
- **Database Management**: SQLite database (development) or SharePoint (production)

## Configuration

See `config.py` for agent configuration options.

## Database

- **Development**: `data/initiative_assistant/initiatives.db` (SQLite)
- **Production**: SharePoint list/database

Database is automatically initialized on first use.

## API Endpoint

**Endpoint**: `/api/chat/initiative_assistant`

**Request**:
```json
{
    "message": "Haluan tehdä aloitteen...",
    "conversation_id": "optional",
    "context": {
        "user_id": "user123",
        "department": "IT"
    }
}
```

**Response**:
```json
{
    "success": true,
    "response": "Agent response text",
    "agent_id": "initiative_assistant",
    "conversation_id": "conv123",
    "function_calls": [],
    "metadata": {
        "similar_initiatives_found": []
    }
}
```

## Tools

- `save_initiative` - Save collected initiative
- `search_similar_initiatives` - Search for similar initiatives
- `get_initiative_details` - Get initiative details
- `save_feedback` - Save user feedback

## Documentation

See `docs/agents/initiative_assistant.md` for detailed documentation.

