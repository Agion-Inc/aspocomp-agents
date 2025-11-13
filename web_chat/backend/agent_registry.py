"""Agent registry for discovering and managing agents."""

import os
import sys
from typing import Dict, List, Optional, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class AgentRegistry:
    """Registry for managing AI agents."""
    
    def __init__(self):
        """Initialize agent registry."""
        self._agents: Dict[str, Any] = {}
        self._load_agents()
    
    def _load_agents(self):
        """Load and register available agents."""
        try:
            # Import Initiative Assistant Agent
            from agents.initiative_assistant import InitiativeAssistantAgent
            from agents.initiative_assistant.config import AGENT_CONFIG
            
            agent = InitiativeAssistantAgent(AGENT_CONFIG)
            if agent.is_enabled():
                self._agents[agent.agent_id] = agent
                print(f"[Agent Registry] Registered agent: {agent.agent_id}")
        except Exception as e:
            print(f"[Agent Registry] Failed to load Initiative Assistant: {e}")
    
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents.
        
        Returns:
            List of agent information dictionaries
        """
        agents_list = []
        for agent_id, agent in self._agents.items():
            capabilities = agent.get_capabilities()
            agents_list.append({
                "agent_id": agent_id,
                "name": capabilities.get("name", agent_id),
                "description": capabilities.get("description", ""),
                "status": "available" if agent.is_enabled() else "disabled",
                "ui_type": "chat",  # Can be determined from agent config
                "ui_path": f"/agents/{agent_id}/"
            })
        return agents_list
    
    def is_agent_available(self, agent_id: str) -> bool:
        """Check if agent is available.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if agent is available
        """
        return agent_id in self._agents and self._agents[agent_id].is_enabled()


# Global registry instance
_registry = None

def get_registry() -> AgentRegistry:
    """Get global agent registry instance.
    
    Returns:
        AgentRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry

