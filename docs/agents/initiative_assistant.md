# Initiative Assistant Agent

## Overview

The Initiative Assistant Agent helps prevent duplicate initiatives by checking existing initiatives when a new one is proposed. It collects initiative information through an interactive chatbot and maintains its own database of initiatives.

## Status

**Status**: Planned - Phase 1 (First Test)  
**Priority**: High  
**Agent ID**: `initiative_assistant`

## Goals

- Collect initiative information from users through interactive conversation
- Check for similar existing initiatives in the database
- Prevent duplicate work by identifying similar initiatives
- Build a knowledge base of initiatives over time

## Functional Requirements

### 1. Interactive Data Collection
- **Chatbot Interface**: Agent collects required information about initiatives through natural conversation
- **Information Collected**:
  - Initiative title/name
  - Initiative description
  - Initiative creator information (name, department, contact)
  - Initiative goals and objectives
  - Related processes or systems
  - Expected outcomes
- **Conversation Flow**: Agent guides user through providing all necessary information
- **Validation**: Agent validates collected information before saving

### 2. Similarity Detection
- **Database Search**: Agent searches existing initiatives in the database
- **Similarity Analysis**: Uses semantic search and keyword matching to find similar initiatives
- **Response**: Reports if similar initiatives exist, providing:
  - List of similar initiatives found
  - Similarity reasons
  - Links to existing initiatives (if applicable)

### 3. Database Management
- **Own Database**: Agent maintains its own SQLite database (development) or SharePoint (production)
- **Data Storage**: Stores initiative information and feedback
- **Privacy**: Personal information (creator details) stored but not exposed to chatbot
- **Data Model**: See Data Model section below

## Technical Architecture

### API Endpoint

**Endpoint**: `/api/chat/initiative_assistant`

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
    "agent_id": "initiative_assistant",
    "conversation_id": "string",
    "function_calls": [],
    "metadata": {
        "initiative_collected": false,
        "similar_initiatives_found": []
    }
}
```

### Database Structure

**Development**: `data/initiative_assistant/initiatives.db` (SQLite)  
**Production**: SharePoint list/database

#### Data Model Schema

```sql
-- Initiatives table
CREATE TABLE initiatives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    creator_name TEXT NOT NULL,
    creator_department TEXT,
    creator_email TEXT,
    creator_contact TEXT,
    goals TEXT,
    related_processes TEXT,
    expected_outcomes TEXT,
    status TEXT DEFAULT 'proposed',  -- proposed, in_progress, completed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    feedback_count INTEGER DEFAULT 0,
    similarity_checked BOOLEAN DEFAULT FALSE
);

-- Feedback table (for storing user feedback on initiatives)
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    initiative_id INTEGER NOT NULL,
    feedback_text TEXT NOT NULL,
    feedback_type TEXT,  -- positive, negative, suggestion, question
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (initiative_id) REFERENCES initiatives(id)
);

-- Similarity matches (cache similarity results)
CREATE TABLE similarity_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    initiative_id INTEGER NOT NULL,
    similar_to_id INTEGER NOT NULL,
    similarity_score REAL,
    similarity_reasons TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (initiative_id) REFERENCES initiatives(id),
    FOREIGN KEY (similar_to_id) REFERENCES initiatives(id)
);
```

**Privacy Note**: 
- `creator_name`, `creator_email`, `creator_contact` are stored in database
- These fields are NOT exposed to the LLM/chatbot
- Only non-sensitive information (title, description, goals) is used for similarity matching

### Agent Tools/Functions

The agent has access to the following tools:

1. **`save_initiative`**: Save collected initiative information to database
   - Parameters: title, description, creator info, goals, etc.
   - Returns: initiative_id

2. **`search_similar_initiatives`**: Search for similar initiatives
   - Parameters: title, description, keywords
   - Returns: List of similar initiatives with similarity scores

3. **`get_initiative_details`**: Get details of a specific initiative
   - Parameters: initiative_id
   - Returns: Initiative details (excluding personal information)

4. **`save_feedback`**: Save user feedback about an initiative
   - Parameters: initiative_id, feedback_text, feedback_type
   - Returns: feedback_id

### System Prompt

The agent uses a specialized system prompt that:
- Guides the conversation to collect initiative information
- Explains the purpose (preventing duplicates)
- Instructs agent to use tools for database operations
- Emphasizes privacy (not exposing personal information)
- Provides examples of good conversations

See `agents/initiative_assistant/prompts/system_prompt.txt` for full prompt.

## Implementation Plan

### Phase 1: Basic Structure
- [ ] Create agent directory structure
- [ ] Implement base agent class
- [ ] Create database schema and initialization
- [ ] Implement database connection (SQLite for development)

### Phase 2: Core Functionality
- [ ] Implement data collection conversation flow
- [ ] Implement similarity search algorithm
- [ ] Create agent tools (save_initiative, search_similar_initiatives)
- [ ] Implement API endpoint integration

### Phase 3: Integration
- [ ] Integrate with web chat backend
- [ ] Add agent to agent registry
- [ ] Test end-to-end flow
- [ ] Implement feedback mechanism

### Phase 4: Production Readiness
- [ ] SharePoint integration (production database)
- [ ] Performance optimization
- [ ] Error handling and validation
- [ ] Documentation and testing

## File Structure

```
agents/initiative_assistant/
├── README.md
├── agent.py                 # Main agent implementation
├── config.py                # Agent configuration
├── database.py              # Database operations
├── models.py                # Data models/schemas
├── prompts/
│   └── system_prompt.txt    # LLM system prompt
├── tools/
│   ├── __init__.py
│   ├── save_initiative.py
│   ├── search_similar.py
│   └── get_initiative.py
└── tests/
    ├── __init__.py
    └── test_initiative_assistant.py

data/
└── initiative_assistant/
    └── initiatives.db      # SQLite database (development)
```

## Configuration

```python
AGENT_CONFIG = {
    "agent_id": "initiative_assistant",
    "name": "Initiative Assistant",
    "description": "Helps prevent duplicate initiatives by checking existing ones",
    "enabled": True,
    "model": "gemini-2.5-flash",
    "temperature": 0.7,
    "max_iterations": 5,
    "database_path": "data/initiative_assistant/initiatives.db",  # Development
    "sharepoint_list": "Initiatives",  # Production
    "tools": [
        "save_initiative",
        "search_similar_initiatives",
        "get_initiative_details",
        "save_feedback"
    ],
    "system_prompt_path": "agents/initiative_assistant/prompts/system_prompt.txt"
}
```

## Usage Examples

### Example 1: Collecting New Initiative

**User**: "Haluan tehdä aloitteen uudesta työohjejärjestelmästä"

**Agent**: "Hei! Autan sinua aloitteen tekemisessä. Kerro minulle hieman tarkemmin, mikä on aloitteesi tarkoitus ja mitä haluat saavuttaa?"

**User**: "Haluamme automatisoida työohjeiden päivitysprosessin"

**Agent**: "Kiitos! Tämä kuulostaa hyvältä. Voisitko kertoa vielä:
- Mikä ongelma tämä ratkaisee?
- Mitä järjestelmiä tai prosesseja tämä koskee?
- Kuka vastaa tämän aloitteen toteutuksesta?"

[Agent continues collecting information, then searches for similar initiatives]

**Agent**: "Olen kerännyt aloitteesi tiedot. Tarkistan nyt, onko vastaavia aloitteita jo olemassa..."

[Agent searches database]

**Agent**: "Löysin 2 samankaltaista aloitteita:
1. 'Työohjeiden digitalisointiprojekti' (2024-01-15) - Samankaltainen koska molemmat koskevat työohjeiden automatisointia
2. 'Prosessien automatisointi' (2024-02-20) - Samankaltainen koska molemmat automatisointiprojekteja

Haluatko tarkistaa nämä aloitteet ennen kuin tallennamme uuden?"

### Example 2: Checking Similar Initiatives

**User**: "Onko tehty aloite työohjeiden päivityksestä?"

**Agent**: "Tarkistan kannasta..." [searches]

**Agent**: "Löysin seuraavat aloitteet työohjeiden päivityksestä:
- 'Työohjeiden digitalisointiprojekti' (2024-01-15, status: in_progress)
- 'Automaattinen työohjeiden päivitys' (2024-03-10, status: proposed)

Haluatko lisätietoja jostakin näistä?"

## Privacy and Security

- **Personal Information**: Creator names, emails, and contact information are stored but NOT exposed to the LLM
- **Data Access**: Only non-sensitive fields (title, description, goals) are used for similarity matching
- **GDPR Compliance**: Personal data stored with consent, right to deletion supported
- **Access Control**: Database access controlled through agent's authentication

## Testing

### Unit Tests
- Test database operations
- Test similarity search algorithm
- Test data collection flow
- Test privacy (personal info not exposed)

### Integration Tests
- Test API endpoint
- Test end-to-end conversation flow
- Test database persistence
- Test SharePoint integration (production)

## References

- **General Requirements**: `docs/agent_requirements.md`
- **Framework Architecture**: `docs/agents_framework.md`
- **Implementation Guide**: `.cursor/rules/implement_agent.mdc`
- **Agent List**: `docs/agent_list.md`

