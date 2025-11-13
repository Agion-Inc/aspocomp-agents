"""Tool for saving feedback about initiatives."""

import sys
import os
from typing import Dict, Any
from datetime import datetime

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, os.path.abspath(project_root))

from agents.initiative_assistant.database import InitiativeDatabase
from agents.initiative_assistant.models import Feedback


def save_feedback(
    initiative_id: int,
    feedback_text: str,
    feedback_type: str = None
) -> Dict[str, Any]:
    """Save feedback about an initiative.
    
    Args:
        initiative_id: ID of the initiative
        feedback_text: Feedback text (required)
        feedback_type: Type of feedback (optional: positive, negative, suggestion, question)
    
    Returns:
        Dictionary with success status and feedback_id
    """
    try:
        if not feedback_text:
            return {
                "success": False,
                "error": "Feedback text is required"
            }
        
        feedback = Feedback(
            initiative_id=initiative_id,
            feedback_text=feedback_text,
            feedback_type=feedback_type,
            created_at=datetime.now()
        )
        
        db = InitiativeDatabase()
        feedback_id = db.save_feedback(feedback)
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": f"Feedback saved successfully"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to save feedback: {str(e)}"
        }

