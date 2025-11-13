# Agent Database Pattern

This document describes the pattern for agents that require their own databases and data models.

## Overview

Some agents need to maintain their own data stores to function effectively. This pattern provides guidelines for implementing agent-specific databases while maintaining consistency across the framework.

## Database Architecture

### Development Environment

**Location**: `data/[agent_name]/[database].db` (SQLite)

**Structure**:
```
data/
├── initiative_assistant/
│   └── initiatives.db
├── sales/
│   └── leads.db
└── [other_agent]/
    └── [database].db
```

**Benefits**:
- Easy to set up and develop locally
- No external dependencies
- Fast iteration and testing
- Can be version controlled (gitignored)

### Production Environment

**Location**: SharePoint lists/databases (shared SharePoint location)

**Structure**:
- Each agent has its own SharePoint list or database
- Shared SharePoint location for all agent data
- Access controlled through SharePoint permissions

**Benefits**:
- Centralized data management
- Enterprise-grade security
- Integration with existing Aspocomp systems
- Backup and recovery

## Data Model Pattern

### Schema Definition

Each agent defines its own data model in `agents/[agent_name]/models.py`:

```python
# agents/initiative_assistant/models.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Initiative:
    """Data model for initiatives."""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    creator_name: str = ""  # Personal info - NOT exposed to LLM
    creator_department: Optional[str] = None
    creator_email: Optional[str] = None  # Personal info - NOT exposed to LLM
    creator_contact: Optional[str] = None  # Personal info - NOT exposed to LLM
    goals: Optional[str] = None
    related_processes: Optional[str] = None
    expected_outcomes: Optional[str] = None
    status: str = "proposed"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self, include_personal: bool = False) -> dict:
        """Convert to dictionary, optionally excluding personal information."""
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "goals": self.goals,
            "related_processes": self.related_processes,
            "expected_outcomes": self.expected_outcomes,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_personal:
            data.update({
                "creator_name": self.creator_name,
                "creator_department": self.creator_department,
                "creator_email": self.creator_email,
                "creator_contact": self.creator_contact,
            })
        return data
```

### Privacy Considerations

**Critical Rule**: Personal information stored in database but **NOT exposed to LLM/chatbot**.

**Personal Information Examples**:
- Names
- Email addresses
- Phone numbers
- Contact information
- Employee IDs
- Department assignments (may be sensitive)

**Non-Personal Information** (safe for LLM):
- Titles
- Descriptions
- Goals
- Status
- Dates (without personal context)
- Generic categories

**Implementation Pattern**:
```python
# When passing data to LLM
initiative_data = initiative.to_dict(include_personal=False)  # Exclude personal info

# When storing in database
initiative_data = initiative.to_dict(include_personal=True)  # Include all data
```

## Database Operations Pattern

### Database Module Structure

Each agent has a `database.py` module:

```python
# agents/initiative_assistant/database.py

import sqlite3
import os
from typing import List, Optional
from datetime import datetime
from .models import Initiative

class InitiativeDatabase:
    """Database operations for Initiative Assistant."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        if db_path is None:
            # Default to development database
            data_dir = os.path.join(os.path.dirname(__file__), '../../data/initiative_assistant')
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, 'initiatives.db')
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS initiatives (
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
                status TEXT DEFAULT 'proposed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_initiative(self, initiative: Initiative) -> int:
        """Save initiative to database."""
        # Implementation
        pass
    
    def search_similar(self, title: str, description: str) -> List[Initiative]:
        """Search for similar initiatives (excluding personal info from results)."""
        # Implementation
        # Return initiatives with personal info excluded
        pass
    
    def get_initiative(self, initiative_id: int, include_personal: bool = False) -> Optional[Initiative]:
        """Get initiative by ID."""
        # Implementation
        # include_personal=False by default for LLM access
        pass
```

## Agent Tools Pattern

Agent tools interact with the database:

```python
# agents/initiative_assistant/tools/save_initiative.py

from typing import Dict, Any
from ..database import InitiativeDatabase
from ..models import Initiative

def save_initiative(
    title: str,
    description: str,
    creator_name: str,
    creator_email: str = None,
    goals: str = None,
    **kwargs
) -> Dict[str, Any]:
    """Save initiative to database.
    
    Args:
        title: Initiative title
        description: Initiative description
        creator_name: Creator's name (personal info, stored but not exposed)
        creator_email: Creator's email (personal info, stored but not exposed)
        goals: Initiative goals
    
    Returns:
        Dictionary with initiative_id and status
    """
    db = InitiativeDatabase()
    
    initiative = Initiative(
        title=title,
        description=description,
        creator_name=creator_name,
        creator_email=creator_email,
        goals=goals
    )
    
    initiative_id = db.save_initiative(initiative)
    
    return {
        "success": True,
        "initiative_id": initiative_id,
        "message": "Initiative saved successfully"
    }
```

## Configuration Pattern

Agent configuration includes database settings:

```python
# agents/initiative_assistant/config.py

import os

AGENT_CONFIG = {
    "agent_id": "initiative_assistant",
    "name": "Initiative Assistant",
    "description": "Helps prevent duplicate initiatives",
    "enabled": True,
    "model": "gemini-2.5-flash",
    "temperature": 0.7,
    "max_iterations": 5,
    
    # Database configuration
    "database": {
        "type": "sqlite",  # or "sharepoint" for production
        "path": "data/initiative_assistant/initiatives.db",  # Development
        "sharepoint_list": "Initiatives",  # Production
        "sharepoint_site": "https://aspocomp.sharepoint.com/sites/agents"
    },
    
    "tools": [
        "save_initiative",
        "search_similar_initiatives",
        "get_initiative_details"
    ],
    
    "system_prompt_path": "agents/initiative_assistant/prompts/system_prompt.txt"
}
```

## Implementation Checklist

When creating an agent with a database:

- [ ] Create `data/[agent_name]/` directory
- [ ] Define data models in `models.py`
- [ ] Implement database operations in `database.py`
- [ ] Create database initialization schema
- [ ] Implement privacy filtering (exclude personal info from LLM)
- [ ] Create agent tools that use database
- [ ] Add database configuration to `config.py`
- [ ] Write tests for database operations
- [ ] Document database schema
- [ ] Plan SharePoint migration (production)

## Best Practices

1. **Privacy First**: Always exclude personal information when passing data to LLM
2. **Schema Versioning**: Include version in database schema for migrations
3. **Error Handling**: Handle database errors gracefully
4. **Transactions**: Use transactions for multi-step operations
5. **Indexing**: Add indexes for frequently queried fields
6. **Backup**: Regular backups of development databases
7. **Migration Path**: Plan migration from SQLite to SharePoint

## References

- **Initiative Assistant Example**: `docs/agents/initiative_assistant.md`
- **Framework Architecture**: `docs/agents_framework.md`
- **Agent Requirements**: `docs/agent_requirements.md`

