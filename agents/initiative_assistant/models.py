"""Data models for Initiative Assistant Agent."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


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
    status: str = "proposed"  # proposed, in_progress, completed, cancelled
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    feedback_count: int = 0
    similarity_checked: bool = False
    
    def to_dict(self, include_personal: bool = False) -> Dict[str, Any]:
        """Convert to dictionary, optionally excluding personal information.
        
        Args:
            include_personal: If True, include personal information (for database storage).
                            If False, exclude personal information (for LLM).
        
        Returns:
            Dictionary representation of the initiative.
        """
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
            "feedback_count": self.feedback_count,
            "similarity_checked": self.similarity_checked,
        }
        
        if include_personal:
            data.update({
                "creator_name": self.creator_name,
                "creator_department": self.creator_department,
                "creator_email": self.creator_email,
                "creator_contact": self.creator_contact,
            })
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Initiative':
        """Create Initiative from dictionary."""
        # Parse datetime strings if present
        created_at = None
        updated_at = None
        
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
            else:
                created_at = data["created_at"]
        
        if data.get("updated_at"):
            if isinstance(data["updated_at"], str):
                updated_at = datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
            else:
                updated_at = data["updated_at"]
        
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            creator_name=data.get("creator_name", ""),
            creator_department=data.get("creator_department"),
            creator_email=data.get("creator_email"),
            creator_contact=data.get("creator_contact"),
            goals=data.get("goals"),
            related_processes=data.get("related_processes"),
            expected_outcomes=data.get("expected_outcomes"),
            status=data.get("status", "proposed"),
            created_at=created_at,
            updated_at=updated_at,
            feedback_count=data.get("feedback_count", 0),
            similarity_checked=data.get("similarity_checked", False)
        )


@dataclass
class Feedback:
    """Data model for feedback on initiatives."""
    id: Optional[int] = None
    initiative_id: int = 0
    feedback_text: str = ""
    feedback_type: Optional[str] = None  # positive, negative, suggestion, question
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "initiative_id": self.initiative_id,
            "feedback_text": self.feedback_text,
            "feedback_type": self.feedback_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Feedback':
        """Create Feedback from dictionary."""
        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
            else:
                created_at = data["created_at"]
        
        return cls(
            id=data.get("id"),
            initiative_id=data.get("initiative_id", 0),
            feedback_text=data.get("feedback_text", ""),
            feedback_type=data.get("feedback_type"),
            created_at=created_at
        )


@dataclass
class SimilarityMatch:
    """Data model for similarity matches between initiatives."""
    id: Optional[int] = None
    initiative_id: int = 0
    similar_to_id: int = 0
    similarity_score: Optional[float] = None
    similarity_reasons: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "initiative_id": self.initiative_id,
            "similar_to_id": self.similar_to_id,
            "similarity_score": self.similarity_score,
            "similarity_reasons": self.similarity_reasons,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimilarityMatch':
        """Create SimilarityMatch from dictionary."""
        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
            else:
                created_at = data["created_at"]
        
        return cls(
            id=data.get("id"),
            initiative_id=data.get("initiative_id", 0),
            similar_to_id=data.get("similar_to_id", 0),
            similarity_score=data.get("similarity_score"),
            similarity_reasons=data.get("similarity_reasons"),
            created_at=created_at
        )

