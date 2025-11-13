"""Tool for searching similar initiatives."""

import sys
import os
from typing import Dict, Any, List

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, os.path.abspath(project_root))

from agents.initiative_assistant.database import InitiativeDatabase


def search_similar_initiatives(
    title: str,
    description: str = None,
    limit: int = 5
) -> Dict[str, Any]:
    """Search for similar existing initiatives.
    
    This tool searches the database for initiatives similar to the provided
    title and description. Personal information is excluded from results.
    
    Args:
        title: Initiative title to search for (required)
        description: Initiative description to search for (optional)
        limit: Maximum number of results (default: 5)
    
    Returns:
        Dictionary with success status and list of similar initiatives
        (without personal information)
    """
    try:
        if not title:
            return {
                "success": False,
                "error": "Title is required for search"
            }
        
        db = InitiativeDatabase()
        similar = db.search_similar(title, description or "", limit)
        
        # Convert to dictionaries without personal information
        results = []
        for initiative in similar:
            # Exclude personal information
            data = initiative.to_dict(include_personal=False)
            results.append(data)
        
        return {
            "success": True,
            "count": len(results),
            "similar_initiatives": results,
            "message": f"Found {len(results)} similar initiative(s)"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to search initiatives: {str(e)}"
        }

