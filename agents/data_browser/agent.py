"""Data Browser Agent implementation."""

import os
import sys
import asyncio
from typing import Dict, Optional, List, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from google import genai
from google.genai import types

from .config import AGENT_CONFIG
from . import tools
from web_chat.backend.conversation_manager import get_conversation, add_message


class DataBrowserAgent:
    """Data Browser Agent for navigating protected web pages and extracting data."""
    
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
                        "name": "navigate_to_page",
                        "description": "Navigate to a web page using Playwright. Optionally use stored credentials for authentication.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "description": "URL to navigate to"},
                                "user_id": {"type": "string", "description": "User ID making the request"},
                                "service_id": {"type": "integer", "description": "Optional service ID if known"},
                                "credential_id": {"type": "integer", "description": "Optional credential ID to use for authentication"},
                                "wait_for_selector": {"type": "string", "description": "Optional CSS selector to wait for after navigation"}
                            },
                            "required": ["url", "user_id"]
                        }
                    },
                    {
                        "name": "extract_page_content",
                        "description": "Extract text and structured content from a previously visited page. Returns JSON or Markdown.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "visit_id": {"type": "integer", "description": "Page visit ID from navigate_to_page"},
                                "output_format": {"type": "string", "enum": ["json", "markdown"], "description": "Output format", "default": "json"},
                                "extraction_selectors": {"type": "object", "description": "Optional CSS selectors for specific content"}
                            },
                            "required": ["visit_id"]
                        }
                    },
                    {
                        "name": "extract_images",
                        "description": "Extract images from a previously visited page. Can download images to local storage.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "visit_id": {"type": "integer", "description": "Page visit ID from navigate_to_page"},
                                "download_images": {"type": "boolean", "description": "Whether to download images", "default": True},
                                "include_base64": {"type": "boolean", "description": "Whether to include base64-encoded image data", "default": False}
                            },
                            "required": ["visit_id"]
                        }
                    },
                    {
                        "name": "save_credentials",
                        "description": "Save credentials securely for a service. Credentials are encrypted and NEVER exposed to LLM.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "service_id": {"type": "integer", "description": "Service ID if known"},
                                "domain": {"type": "string", "description": "Domain name if service_id not provided"},
                                "user_id": {"type": "string", "description": "User ID owning these credentials"},
                                "credential_type": {"type": "string", "enum": ["username_password", "api_key", "token", "oauth"], "description": "Type of credential", "default": "username_password"},
                                "username": {"type": "string", "description": "Username (for username_password type)"},
                                "password": {"type": "string", "description": "Password (for username_password type)"},
                                "email": {"type": "string", "description": "Email (for username_password type, alternative to username)"},
                                "api_key": {"type": "string", "description": "API key (for api_key type)"},
                                "token": {"type": "string", "description": "Token (for token type)"},
                                "expires_at": {"type": "string", "description": "Expiration date in ISO format"},
                                "metadata": {"type": "object", "description": "Additional metadata"}
                            },
                            "required": ["user_id"]
                        }
                    },
                    {
                        "name": "get_service_credentials",
                        "description": "Get available credentials for a service (metadata only, no actual credentials). Use this to check if credentials exist.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "service_id": {"type": "integer", "description": "Service ID"},
                                "domain": {"type": "string", "description": "Domain name if service_id not provided"},
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        }
                    },
                    {
                        "name": "create_navigation_script",
                        "description": "Create a Playwright navigation script for complex navigation flows.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "service_id": {"type": "integer", "description": "Service ID this script is for"},
                                "script_name": {"type": "string", "description": "Name of the script"},
                                "script_code": {"type": "string", "description": "Python code string containing Playwright script"},
                                "description": {"type": "string", "description": "Optional description"}
                            },
                            "required": ["service_id", "script_name", "script_code"]
                        }
                    },
                    {
                        "name": "execute_navigation_script",
                        "description": "Execute a stored Playwright navigation script for complex navigation flows.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "script_id": {"type": "integer", "description": "Navigation script ID"},
                                "url": {"type": "string", "description": "Starting URL"},
                                "user_id": {"type": "string", "description": "User ID making the request"},
                                "parameters": {"type": "object", "description": "Optional parameters dictionary"}
                            },
                            "required": ["script_id", "url", "user_id"]
                        }
                    },
                    {
                        "name": "get_extraction_history",
                        "description": "Get history of extractions for the user.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "service_id": {"type": "integer", "description": "Optional service ID to filter by"},
                                "limit": {"type": "integer", "description": "Maximum number of results", "default": 50}
                            },
                            "required": ["user_id"]
                        }
                    },
                    {
                        "name": "get_page_visit_history",
                        "description": "Get history of page visits for the user.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "service_id": {"type": "integer", "description": "Optional service ID to filter by"},
                                "limit": {"type": "integer", "description": "Maximum number of results", "default": 50}
                            },
                            "required": ["user_id"]
                        }
                    },
                    {
                        "name": "load_env_credentials",
                        "description": "Load credentials from environment variables (.env.local) and save them for a service. Use this for services like training.aspocomp.com.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "domain": {"type": "string", "description": "Domain name (e.g., 'training.aspocomp.com')"},
                                "user_id": {"type": "string", "description": "User ID"},
                                "username_env_var": {"type": "string", "description": "Environment variable name for username"},
                                "password_env_var": {"type": "string", "description": "Environment variable name for password"},
                                "service_name": {"type": "string", "description": "Optional service name"}
                            },
                            "required": ["domain", "user_id", "username_env_var", "password_env_var"]
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
            "navigate_to_page": tools.navigate_to_page,
            "extract_page_content": tools.extract_page_content,
            "extract_images": tools.extract_images,
            "save_credentials": tools.save_credentials,
            "get_service_credentials": tools.get_service_credentials,
            "create_navigation_script": tools.create_navigation_script,
            "execute_navigation_script": tools.execute_navigation_script,
            "get_extraction_history": tools.get_extraction_history,
            "get_page_visit_history": tools.get_page_visit_history,
            "load_env_credentials": tools.load_env_credentials
        }
        
        if tool_name not in tool_map:
            return {
                "ok": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        try:
            result = tool_map[tool_name](**args)
            
            # Handle case where tool returns None
            if result is None:
                return {
                    "ok": False,
                    "error": f"Tool {tool_name} returned None"
                }
            
            # Ensure result is a dictionary
            if not isinstance(result, dict):
                return {
                    "ok": False,
                    "error": f"Tool {tool_name} returned invalid type: {type(result)}"
                }
            
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
                    "error": result.get("error", "Tool execution failed")
                }
        except Exception as e:
            return {
                "ok": False,
                "error": f"Tool execution error: {str(e)}"
            }
    
    async def process_message(
        self,
        message: str,
        conversation_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a user message and return response.
        
        Args:
            message: User's message
            conversation_id: Conversation identifier
            context: Additional context (user info, session data, etc.)
        
        Returns:
            {
                "response": str,
                "agent_id": str,
                "function_calls": list,
                "metadata": dict
            }
        """
        context = context or {}
        user_id = context.get("user_id", "anonymous")
        
        # Get conversation history
        conversation = get_conversation(conversation_id)
        history = conversation.get("messages", []) if conversation else []
        
        # Build messages for Gemini
        messages = []
        
        # Add system prompt
        system_prompt = self.get_system_prompt()
        if system_prompt:
            messages.append({
                "role": "user",
                "parts": [{"text": system_prompt}]
            })
            messages.append({
                "role": "model",
                "parts": [{"text": "Understood. I'm ready to help navigate web pages and extract data."}]
            })
        
        # Add conversation history
        for msg in history[-10:]:  # Last 10 messages
            role = "user" if msg.get("role") == "user" else "model"
            messages.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}]
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "parts": [{"text": message}]
        })
        
        # Initialize Gemini client
        api_key = os.getenv("GOOGLE_AI_STUDIO_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "response": "Error: API key not configured. Please set GOOGLE_AI_STUDIO_KEY or GEMINI_API_KEY environment variable.",
                "agent_id": self.agent_id,
                "function_calls": [],
                "metadata": {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "error": "API_KEY_MISSING"
                }
            }
        
        client = genai.Client(api_key=api_key)
        
        # Build tools
        tools_list = self.build_tools()
        
        # Process with Gemini
        function_calls = []
        response_text = ""
        
        try:
            # Create model with tools in config
            config = types.GenerateContentConfig(
                tools=tools_list,
                temperature=self.temperature,
                max_output_tokens=2048
            )
            model = client.models.generate_content(
                model=self.model,
                contents=messages,
                config=config
            )
            
            # Handle function calls
            for _ in range(self.max_iterations):
                if hasattr(model, 'candidates') and model.candidates:
                    candidate = model.candidates[0]
                    
                    # Check for function calls
                    if hasattr(candidate, 'content') and candidate.content:
                        parts = candidate.content.parts
                        
                        # Check if there are function calls
                        function_calls_found = False
                        for part in parts:
                            if hasattr(part, 'function_call'):
                                fc = part.function_call
                                # Skip if function_call is None
                                if fc is None:
                                    continue
                                function_calls_found = True
                                tool_name = fc.name if hasattr(fc, 'name') else None
                                if not tool_name:
                                    continue
                                args = dict(fc.args) if hasattr(fc, 'args') and fc.args else {}
                                
                                # Add user_id from context if not provided and tool requires it
                                # Tools that require user_id: navigate_to_page, save_credentials, get_service_credentials, 
                                # get_extraction_history, get_page_visit_history, load_env_credentials
                                tools_requiring_user_id = [
                                    "navigate_to_page", "save_credentials", "get_service_credentials",
                                    "get_extraction_history", "get_page_visit_history", "load_env_credentials"
                                ]
                                if tool_name in tools_requiring_user_id and "user_id" not in args and user_id:
                                    args["user_id"] = user_id
                                
                                # Execute tool
                                tool_result = self.execute_tool(tool_name, args)
                                function_calls.append({
                                    "name": tool_name,
                                    "args": args,
                                    "result": tool_result
                                })
                                
                                # Add function result to messages
                                messages.append({
                                    "role": "model",
                                    "parts": [{"text": f"Function {tool_name} called"}]
                                })
                                messages.append({
                                    "role": "user",
                                    "parts": [{
                                        "function_response": {
                                            "name": tool_name,
                                            "response": tool_result
                                        }
                                    }]
                                })
                                
                                # Continue loop to get response with function results
                                model = client.models.generate_content(
                                    model=self.model,
                                    contents=messages,
                                    config=config
                                )
                                continue  # Restart loop to process new response
                        
                        # If no function calls, get text response
                        if not function_calls_found:
                            for part in parts:
                                if hasattr(part, 'text'):
                                    response_text = part.text
                                    break
                            break
                    else:
                        # No content, break
                        break
                else:
                    break
            
            # If we still don't have a response, generate final response
            if not response_text and function_calls:
                # Generate final response with function results
                final_messages = messages + [{
                    "role": "user",
                    "parts": [{"text": "Based on the function call results, provide a helpful response to the user."}]
                }]
                
                final_model = client.models.generate_content(
                    model=self.model,
                    contents=final_messages,
                    config=types.GenerateContentConfig(
                        temperature=self.temperature,
                        max_output_tokens=2048
                    )
                )
                
                if hasattr(final_model, 'candidates') and final_model.candidates:
                    candidate = final_model.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        parts = candidate.content.parts
                        for part in parts:
                            if hasattr(part, 'text'):
                                response_text = part.text
                                break
            
            if not response_text:
                response_text = "I've processed your request. Please check the function call results."
        
        except Exception as e:
            import traceback
            error_msg = f"Error processing message: {str(e)}"
            traceback.print_exc()  # Log full traceback for debugging
            response_text = error_msg
            function_calls = function_calls if 'function_calls' in locals() else []
        
        # Ensure response_text is not None
        if response_text is None:
            response_text = "I encountered an error processing your request."
        
        # Save to conversation
        try:
            add_message(conversation_id, "user", message)
            add_message(conversation_id, "assistant", response_text)
        except Exception as e:
            print(f"Warning: Failed to save conversation: {e}")
        
        # Ensure function_calls is a list
        if not isinstance(function_calls, list):
            function_calls = []
        
        return {
            "response": response_text,
            "agent_id": self.agent_id,
            "function_calls": function_calls,
            "metadata": {
                "user_id": user_id,
                "conversation_id": conversation_id
            }
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
                "Navigate protected web pages with authentication",
                "Extract text, tables, links, and structured content",
                "Extract and download images",
                "Securely manage credentials (encrypted)",
                "Provide data in JSON or Markdown format",
                "Track pages and credentials per service",
                "Execute Playwright scripts for complex navigation"
            ]
        }
    
    def is_enabled(self) -> bool:
        """Check if agent is enabled.
        
        Returns:
            True if agent is enabled
        """
        return self.config.get("enabled", False)

