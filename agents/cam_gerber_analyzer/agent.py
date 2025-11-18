"""CAM Gerber Analyzer Agent implementation."""

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


class CamGerberAnalyzerAgent:
    """CAM Gerber Analyzer Agent for PCB design analysis."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the agent with configuration.
        
        Args:
            config: Agent configuration dictionary. Uses default if None.
        """
        self.config = config or AGENT_CONFIG
        self.agent_id = self.config["agent_id"]
        self.name = self.config["name"]
        self.model = self.config["model"]
        self.temperature = self.config.get("temperature", 0.3)
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
                        "name": "upload_design_files",
                        "description": "Upload and store Gerber or ODB++ files for analysis. Use this when user provides files.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "files": {
                                    "type": "array",
                                    "description": "List of file objects with filename, content (base64), and file_type",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "filename": {"type": "string"},
                                            "content": {"type": "string"},
                                            "file_type": {"type": "string"}
                                        }
                                    }
                                },
                                "project_name": {"type": "string", "description": "Project name"},
                                "board_name": {"type": "string", "description": "Board name"},
                                "user_id": {"type": "string", "description": "User identifier"}
                            },
                            "required": ["files"]
                        }
                    },
                    {
                        "name": "detect_file_format",
                        "description": "Automatically detect file format (Gerber vs ODB++).",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {"type": "string", "description": "Path to file"},
                                "filename": {"type": "string", "description": "Filename"}
                            }
                        }
                    },
                    {
                        "name": "parse_gerber_file",
                        "description": "Parse a Gerber file and extract layer information.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {"type": "string", "description": "Path to Gerber file"},
                                "file_type": {"type": "string", "description": "Type of file (copper_top, copper_bottom, drill, etc.)"}
                            },
                            "required": ["file_path"]
                        }
                    },
                    {
                        "name": "parse_odbp_file",
                        "description": "Parse an ODB++ archive and extract design information.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "archive_path": {"type": "string", "description": "Path to ODB++ archive"},
                                "directory_path": {"type": "string", "description": "Path to ODB++ directory"}
                            }
                        }
                    },
                    {
                        "name": "generate_design_summary",
                        "description": "Generate comprehensive PCB design summary. This is the PRIMARY tool - always use this after uploading files to create a summary.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "analysis_id": {"type": "integer", "description": "Analysis ID from upload_design_files"}
                            },
                            "required": ["analysis_id"]
                        }
                    },
                    {
                        "name": "perform_cam_analysis",
                        "description": "Perform comprehensive CAM analysis to identify manufacturing issues.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "analysis_id": {"type": "integer", "description": "Analysis ID"},
                                "analysis_options": {"type": "object", "description": "Analysis options"}
                            },
                            "required": ["analysis_id"]
                        }
                    },
                    {
                        "name": "get_analysis_report",
                        "description": "Generate and retrieve analysis report.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "analysis_id": {"type": "integer", "description": "Analysis ID"},
                                "report_format": {"type": "string", "enum": ["pdf", "html", "json"], "description": "Report format"}
                            },
                            "required": ["analysis_id"]
                        }
                    },
                    {
                        "name": "get_analysis_history",
                        "description": "Retrieve analysis history for a project.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "project_name": {"type": "string", "description": "Project name"},
                                "limit": {"type": "integer", "description": "Maximum number of results", "default": 10}
                            }
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
            "upload_design_files": tools.upload_design_files,
            "detect_file_format": tools.detect_file_format,
            "parse_gerber_file": tools.parse_gerber_file,
            "parse_odbp_file": tools.parse_odbp_file,
            "generate_design_summary": tools.generate_design_summary,
            "perform_cam_analysis": tools.perform_cam_analysis,
            "get_analysis_report": tools.get_analysis_report,
            "get_analysis_history": tools.get_analysis_history
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
            context: Additional context (user info, session data, files, etc.)
        
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
        
        # Handle file uploads if present in context
        if context and 'files' in context and context['files']:
            # Files are provided, upload them first
            user_id = context.get('user_id', 'default')
            upload_result = tools.upload_design_files(
                files=context['files'],
                project_name=context.get('project_name'),
                board_name=context.get('board_name'),
                user_id=user_id
            )
            if upload_result.get('success'):
                # Add analysis_id to context for later use
                analysis_id = upload_result.get('analysis_id')
                context['analysis_id'] = analysis_id
                # Automatically generate design summary after upload
                summary_result = tools.generate_design_summary(analysis_id)
                if summary_result.get('success'):
                    # Update message to include summary info
                    summary = summary_result.get('summary', {})
                    summary_info = f"\n\n[Tiedostot ladattu: {len(context['files'])} tiedostoa. Analysis ID: {analysis_id}"
                    if summary.get('board_width') and summary.get('board_height'):
                        summary_info += f". Piirilevyn koko: {summary.get('board_width')}mm × {summary.get('board_height')}mm"
                    if summary.get('layer_count'):
                        summary_info += f". Kerroksia: {summary.get('layer_count')}"
                    summary_info += "]"
                    message = f"{message}{summary_info}"
                else:
                    message = f"{message}\n\n[Tiedostot ladattu: {len(context['files'])} tiedostoa. Analysis ID: {analysis_id}]"
        
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
                    parts=[types.Part(text="I understand. I'm ready to help you analyze PCB design files. Please upload Gerber or ODB++ files, and I'll generate a comprehensive design summary.")]
                ),
                types.Content(role="user", parts=[types.Part(text=message)])
            ]
        else:
            # For existing conversations, build history from stored messages
            previous_messages = history_messages[:-1]  # All except the last (current) message
            
            for msg in previous_messages:
                role = msg.get('role')
                content = msg.get('content', '')
                
                if role == 'user':
                    contents.append(types.Content(role="user", parts=[types.Part(text=content)]))
                elif role == 'assistant':
                    contents.append(types.Content(role="model", parts=[types.Part(text=content)]))
            
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
            "analysis_id": None
        }
        
        # Extract analysis_id from function calls
        for fc in function_calls:
            if fc["name"] == "upload_design_files" and fc["status"] == "completed":
                result_data = fc.get("result", {}).get("data", {})
                metadata["analysis_id"] = result_data.get("analysis_id")
            elif fc["name"] == "generate_design_summary" and fc["status"] == "completed":
                result_data = fc.get("result", {}).get("data", {})
                summary = result_data.get("summary", {})
                metadata["summary"] = summary
        
        # Store assistant response in conversation history
        try:
            add_message(conversation_id, 'assistant', response_text)
        except ValueError:
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
                "Upload and analyze Gerber files",
                "Upload and analyze ODB++ files",
                "Generate comprehensive PCB design summaries",
                "Perform CAM analysis",
                "Detect file formats automatically",
                "Extract panel, material, and design information"
            ]
        }
    
    def is_enabled(self) -> bool:
        """Check if agent is enabled.
        
        Returns:
            True if agent is enabled
        """
        return self.config.get("enabled", False)

