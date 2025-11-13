"""Tool for saving initiatives to database."""

import sys
import os
from typing import Dict, Any

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, os.path.abspath(project_root))

from agents.initiative_assistant.database import InitiativeDatabase
from agents.initiative_assistant.models import Initiative
from datetime import datetime


def save_initiative(
    title: str,
    description: str,
    creator_name: str,
    creator_department: str = None,
    creator_email: str = None,
    creator_contact: str = None,
    goals: str = None,
    related_processes: str = None,
    expected_outcomes: str = None,
    status: str = "proposed"
) -> Dict[str, Any]:
    """Save initiative to database.
    
    This tool saves a new initiative to the database. Personal information
    (creator_name, creator_email, creator_contact) is stored but will not
    be exposed to the LLM in future queries.
    
    Args:
        title: Initiative title (required)
        description: Initiative description (required)
        creator_name: Creator's name (required, personal info - stored but not exposed)
        creator_department: Creator's department (optional)
        creator_email: Creator's email (optional, personal info - stored but not exposed)
        creator_contact: Creator's contact info (optional, personal info - stored but not exposed)
        goals: Initiative goals and objectives (optional)
        related_processes: Related processes or systems (optional)
        expected_outcomes: Expected outcomes (optional)
        status: Initiative status (default: "proposed")
    
    Returns:
        Dictionary with success status, initiative_id, and message
    """
    try:
        # Validate required fields
        if not title or not description or not creator_name:
            return {
                "success": False,
                "error": "Title, description, and creator_name are required"
            }
        
        # Create initiative object
        initiative = Initiative(
            title=title,
            description=description,
            creator_name=creator_name,
            creator_department=creator_department,
            creator_email=creator_email,
            creator_contact=creator_contact,
            goals=goals,
            related_processes=related_processes,
            expected_outcomes=expected_outcomes,
            status=status,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save to database
        db = InitiativeDatabase()
        initiative_id = db.save_initiative(initiative)
        
        return {
            "success": True,
            "initiative_id": initiative_id,
            "message": f"Initiative '{title}' saved successfully with ID {initiative_id}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to save initiative: {str(e)}"
        }

