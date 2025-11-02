"""Conversation manager for storing conversation state."""

import uuid
from typing import Dict, List, Optional
from datetime import datetime


# In-memory storage for conversations
_conversations: Dict[str, Dict] = {}


def create_conversation() -> str:
    """Create a new conversation and return its ID."""
    conv_id = str(uuid.uuid4())
    _conversations[conv_id] = {
        'id': conv_id,
        'messages': [],
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    return conv_id


def get_conversation(conversation_id: str) -> Optional[Dict]:
    """Get conversation by ID."""
    return _conversations.get(conversation_id)


def add_message(conversation_id: str, role: str, content: str) -> None:
    """Add a message to a conversation."""
    if conversation_id not in _conversations:
        raise ValueError(f"Conversation {conversation_id} not found")
    
    message = {
        'role': role,
        'content': content,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    _conversations[conversation_id]['messages'].append(message)


def clear_conversation(conversation_id: str) -> None:
    """Clear all messages from a conversation."""
    if conversation_id not in _conversations:
        raise ValueError(f"Conversation {conversation_id} not found")
    
    _conversations[conversation_id]['messages'] = []

