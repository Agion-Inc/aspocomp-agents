"""Initiative Assistant Agent implementation."""

import os
import sys
import asyncio
from typing import Dict, Optional, List, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from google import genai
from google.genai import types

from .config import AGENT_CONFIG
from . import tools
from web_chat.backend.conversation_manager import get_conversation, add_message


class InitiativeAssistantAgent:
    """Initiative Assistant Agent for preventing duplicate initiatives."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the agent with configuration.
        
        Args:
            config: Agent configuration dictionary. Uses default if None.
        """
        self.config = config or AGENT_CONFIG
        self.agent_id = self.config["agent_id"]
        self.name = self.config["name"]
        self.model = self.config["model"]
        self.temperature = self.config.get("temperature", 0.7)
        self.max_iterations = self.config.get("max_iterations", 5)
    
    def get_system_prompt(self) -> str:
        """Load and return agent-specific system prompt.
        
        Returns:
            System prompt text
        """
        prompt_path = self.config.get("system_prompt_path")
        if prompt_path and os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def build_tools(self) -> List[types.Tool]:
        """Build function declarations for agent tools.
        
        Returns:
            List of Tool objects for Gemini API
        """
        return [
            types.Tool(
                function_declarations=[
                    {
                        "name": "save_initiative",
                        "description": "Save a new initiative to the database. Use this when user confirms they want to save their initiative.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Initiative title"},
                                "description": {"type": "string", "description": "Initiative description"},
                                "creator_name": {"type": "string", "description": "Creator's name"},
                                "creator_department": {"type": "string", "description": "Creator's department"},
                                "creator_email": {"type": "string", "description": "Creator's email"},
                                "creator_contact": {"type": "string", "description": "Creator's contact information"},
                                "goals": {"type": "string", "description": "Initiative goals and objectives"},
                                "related_processes": {"type": "string", "description": "Related processes or systems"},
                                "expected_outcomes": {"type": "string", "description": "Expected outcomes"},
                                "status": {"type": "string", "enum": ["proposed", "in_progress", "completed", "cancelled"], "description": "Initiative status"}
                            },
                            "required": ["title", "description", "creator_name"]
                        }
                    },
                    {
                        "name": "search_similar_initiatives",
                        "description": "Search for similar existing initiatives in the database. Always use this before saving a new initiative.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Initiative title to search for"},
                                "description": {"type": "string", "description": "Initiative description to search for"},
                                "limit": {"type": "integer", "description": "Maximum number of results", "default": 5}
                            },
                            "required": ["title"]
                        }
                    },
                    {
                        "name": "get_initiative_details",
                        "description": "Get details of a specific initiative by ID. Personal information is excluded.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "initiative_id": {"type": "integer", "description": "ID of the initiative"}
                            },
                            "required": ["initiative_id"]
                        }
                    },
                    {
                        "name": "save_feedback",
                        "description": "Save feedback about an initiative.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "initiative_id": {"type": "integer", "description": "ID of the initiative"},
                                "feedback_text": {"type": "string", "description": "Feedback text"},
                                "feedback_type": {"type": "string", "enum": ["positive", "negative", "suggestion", "question"], "description": "Type of feedback"}
                            },
                            "required": ["initiative_id", "feedback_text"]
                        }
                    }
                ]
            )
        ]
    
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent tool.
        
        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments
            
        Returns:
            Tool execution result
        """
        tool_map = {
            "save_initiative": tools.save_initiative,
            "search_similar_initiatives": tools.search_similar_initiatives,
            "get_initiative_details": tools.get_initiative_details,
            "save_feedback": tools.save_feedback
        }
        
        if tool_name not in tool_map:
            return {
                "ok": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        try:
            result = tool_map[tool_name](**args)
            # Convert to expected format
            if result.get("success"):
                return {
                    "ok": True,
                    "output": result.get("message", "Success"),
                    "data": result
                }
            else:
                return {
                    "ok": False,
                    "error": result.get("error", "Unknown error")
                }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }
    
    def find_function_call_parts(self, response: types.GenerateContentResponse) -> Optional[tuple]:
        """Extract function call from Gemini response.
        
        Args:
            response: Gemini API response
            
        Returns:
            Tuple of (function_name, function_args) or None
        """
        if not response.candidates:
            return None
        
        parts = response.candidates[0].content.parts
        for part in parts:
            if hasattr(part, "function_call") and part.function_call:
                func_call = part.function_call
                name = func_call.name
                args = {}
                if func_call.args:
                    args = dict(func_call.args)
                return (name, args)
        
        return None
    
    def make_function_response_part(self, function_name: str, result: Dict[str, Any]) -> types.Part:
        """Create a function response part for Gemini API.
        
        Args:
            function_name: Name of the function called
            result: Function execution result
            
        Returns:
            Part object for Gemini API
        """
        # FunctionResponse expects a dictionary, not a JSON string
        if result.get("ok"):
            response_dict = {
                "result": result.get("data", {}),
                "message": result.get("output", "Success")
            }
        else:
            response_dict = {
                "error": result.get("error", "Unknown error")
            }
        
        return types.Part(
            function_response=types.FunctionResponse(
                name=function_name,
                response=response_dict
            )
        )
    
    async def process_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a user message and return response.
        
        Args:
            message: User's message
            conversation_id: Conversation identifier (optional)
            context: Additional context (user info, session data, etc.)
        
        Returns:
            Dictionary with response, agent_id, function_calls, metadata
        """
        # Load API key
        api_key = os.environ.get("GOOGLE_AI_STUDIO_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "API key not configured",
                "agent_id": self.agent_id
            }
        
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        # Get system prompt
        system_prompt = self.get_system_prompt()
        
        # Build tools
        agent_tools = self.build_tools()
        
        # Ensure conversation exists and store user message
        from web_chat.backend.conversation_manager import create_conversation
        if not conversation_id:
            conversation_id = create_conversation()
        
        # Store user message in conversation history BEFORE retrieving history
        try:
            add_message(conversation_id, 'user', message)
        except ValueError:
            # Conversation doesn't exist, create it
            conversation_id = create_conversation()
            add_message(conversation_id, 'user', message)
        
        # Build conversation contents with history
        contents = []
        
        # Get conversation with updated history (includes current user message)
        conversation = get_conversation(conversation_id)
        history_messages = conversation.get('messages', []) if conversation else []
        
        # Check if this is a new conversation (only has the user message we just added)
        is_new_conversation = len(history_messages) == 1
        
        if is_new_conversation:
            # Initialize with system prompt for new conversations
            contents = [
                types.Content(role="user", parts=[types.Part(text=system_prompt)]),
                types.Content(
                    role="model",
                    parts=[types.Part(text="I understand. I'm ready to help you create initiatives and check for duplicates. What would you like to do?")]
                ),
                types.Content(role="user", parts=[types.Part(text=message)])
            ]
        else:
            # For existing conversations, build history from stored messages
            # Include all previous messages except the last one (which is the current message we just added)
            # We'll add the current message separately to ensure proper ordering
            previous_messages = history_messages[:-1]  # All except the last (current) message
            
            for msg in previous_messages:
                role = msg.get('role')
                content = msg.get('content', '')
                
                if role == 'user':
                    contents.append(types.Content(role="user", parts=[types.Part(text=content)]))
                elif role == 'assistant':
                    contents.append(types.Content(role="model", parts=[types.Part(text=content)]))
                # Note: tool responses are handled separately during function call iterations
            
            # Add current user message
            contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
        
        # Configure generation
        gen_config = types.GenerateContentConfig(
            tools=agent_tools,
            temperature=self.temperature
        )
        
        # Generate response - always use gemini-2.5-flash for chat
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=gen_config
        )
        
        function_calls = []
        
        # Handle function calls (up to max_iterations)
        for iteration in range(self.max_iterations):
            func_call = self.find_function_call_parts(response)
            if not func_call:
                break
            
            function_name, function_args = func_call
            
            # Execute tool
            tool_result = self.execute_tool(function_name, function_args)
            
            # Track function call
            function_calls.append({
                "name": function_name,
                "args": function_args,
                "status": "completed" if tool_result.get("ok") else "failed",
                "result": tool_result
            })
            
            # Add function response to conversation
            contents.append(
                types.Content(
                    role="tool",
                    parts=[self.make_function_response_part(function_name, tool_result)]
                )
            )
            
            # Continue conversation with function result - always use gemini-2.5-flash
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=gen_config
            )
        
        # Extract response text
        response_text = ""
        try:
            if response.candidates:
                parts = response.candidates[0].content.parts
                for part in parts:
                    if hasattr(part, "text") and part.text:
                        response_text += part.text
        except Exception as e:
            response_text = f"Error extracting response: {str(e)}"
        
        # Build metadata
        metadata = {
            "function_calls_count": len(function_calls),
            "similar_initiatives_found": []
        }
        
        # Extract similar initiatives from function calls
        for fc in function_calls:
            if fc["name"] == "search_similar_initiatives" and fc["status"] == "completed":
                result_data = fc.get("result", {}).get("data", {})
                similar = result_data.get("similar_initiatives", [])
                metadata["similar_initiatives_found"] = similar
        
        # Store assistant response in conversation history
        # (User message was already stored above)
        try:
            add_message(conversation_id, 'assistant', response_text)
        except ValueError:
            # Should not happen as we created conversation above, but handle gracefully
            pass
        
        return {
            "success": True,
            "response": response_text,
            "agent_id": self.agent_id,
            "conversation_id": conversation_id,
            "function_calls": function_calls,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities and supported functions.
        
        Returns:
            Dictionary with agent capabilities
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.config.get("description", ""),
            "tools": self.config.get("tools", []),
            "capabilities": [
                "Collect initiative information through conversation",
                "Search for similar existing initiatives",
                "Save initiatives to database",
                "Provide feedback on initiatives"
            ]
        }
    
    def is_enabled(self) -> bool:
        """Check if agent is enabled.
        
        Returns:
            True if agent is enabled
        """
        return self.config.get("enabled", False)

