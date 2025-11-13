"""Tool for getting initiative details."""

import sys
import os
from typing import Dict, Any, Optional

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, os.path.abspath(project_root))

from agents.initiative_assistant.database import InitiativeDatabase


def get_initiative_details(
    initiative_id: int
) -> Dict[str, Any]:
    """Get details of a specific initiative.
    
    Personal information (creator_name, creator_email, creator_contact)
    is excluded from the response.
    
    Args:
        initiative_id: ID of the initiative to retrieve
    
    Returns:
        Dictionary with initiative details (without personal information)
    """
    try:
        db = InitiativeDatabase()
        initiative = db.get_initiative(initiative_id, include_personal=False)
        
        if initiative is None:
            return {
                "success": False,
                "error": f"Initiative with ID {initiative_id} not found"
            }
        
        # Convert to dictionary without personal information
        data = initiative.to_dict(include_personal=False)
        
        return {
            "success": True,
            "initiative": data
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get initiative: {str(e)}"
        }

