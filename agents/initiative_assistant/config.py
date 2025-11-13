"""Configuration for Initiative Assistant Agent."""

import os

AGENT_CONFIG = {
    "agent_id": "initiative_assistant",
    "name": "Initiative Assistant",
    "description": "Helps prevent duplicate initiatives by checking existing ones",
    "enabled": True,
    "model": "gemini-2.5-flash",
    "temperature": 0.7,
    "max_iterations": 5,
    
    # Database configuration
    "database": {
        "type": "sqlite",  # or "sharepoint" for production
        "path": os.path.join(
            os.path.dirname(__file__),
            "../../data/initiative_assistant/initiatives.db"
        ),
        "sharepoint_list": "Initiatives",  # Production
        "sharepoint_site": "https://aspocomp.sharepoint.com/sites/agents"
    },
    
    # Tools
    "tools": [
        "save_initiative",
        "search_similar_initiatives",
        "get_initiative_details",
        "save_feedback"
    ],
    
    # System prompt
    "system_prompt_path": os.path.join(
        os.path.dirname(__file__),
        "prompts/system_prompt.txt"
    )
}

