"""Chat service for handling Gemini Agent interactions."""

import asyncio
import sys
import os
from typing import Dict, Optional, List
from datetime import datetime

# Add parent directory to path to import gemini_agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from google import genai
from web_chat.backend import config
from web_chat.backend.errors import APIKeyMissingError
from web_chat.backend.conversation_manager import (
    create_conversation,
    get_conversation,
    add_message
)


async def send_message(
    message: str,
    model: str = 'gemini-2.5-flash',
    mcp_enabled: bool = False,
    conversation_id: Optional[str] = None
) -> Dict:
    """Send a message to Gemini Agent and return response.
    
    Args:
        message: User message text
        model: Gemini model to use
        mcp_enabled: Whether to enable MCP tools
        conversation_id: Existing conversation ID (creates new if None)
    
    Returns:
        Dictionary with response, conversation_id, function_calls, etc.
    """
    # Check API key
    api_key = config.get_api_key()
    if not api_key:
        raise APIKeyMissingError()
    
    # Create or get conversation
    if not conversation_id:
        conversation_id = create_conversation()
    
    # Add user message to conversation
    add_message(conversation_id, 'user', message)
    
    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    
    # Get conversation history
    conversation = get_conversation(conversation_id)
    history_messages = conversation['messages'] if conversation else []
    
    # Build conversation context from history
    # Skip system prompt messages and use actual conversation history
    conversation_context = []
    for msg in history_messages:
        if msg['role'] in ['user', 'assistant']:
            conversation_context.append(msg['content'])
    
    # Call Gemini agent (simplified version)
    # We'll need to adapt run_single_turn_async to return data instead of printing
    response_text, function_calls = await _call_gemini_agent(
        client, model, message, mcp_enabled
    )
    
    # Add assistant response to conversation
    add_message(conversation_id, 'assistant', response_text)
    
    return {
        'success': True,
        'response': response_text,
        'conversation_id': conversation_id,
        'function_calls': function_calls,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }


async def _call_gemini_agent(
    client: genai.Client,
    model: str,
    user_prompt: str,
    mcp_enabled: bool
) -> tuple[str, List[Dict]]:
    """Call Gemini agent and return response text and function calls.
    
    Returns:
        Tuple of (response_text, function_calls_list)
    """
    # Import gemini_agent functions
    from gemini_agent import (
        build_cli_tools,
        build_system_prompt,
        execute_cli_function,
        find_function_call_parts,
        make_function_response_part
    )
    from google.genai import types
    
    tools = build_cli_tools()
    system_prompt = build_system_prompt()
    
    # Build contents with system prompt and conversation history
    # For now, include system prompt and current message
    # TODO: Include full conversation history in future
    contents = [
        types.Content(role="user", parts=[types.Part(text=system_prompt)]),
        types.Content(role="model", parts=[types.Part(text="I understand. I'm ready to help you with any task using my available functions. What can I do for you?")]),
        types.Content(role="user", parts=[types.Part(text=user_prompt)])
    ]
    
    function_calls = []
    
    # No MCP for now - just CLI tools
    gen_config = types.GenerateContentConfig(tools=tools)
    response = await client.aio.models.generate_content(
        model=model,
        contents=contents,
        config=gen_config,
    )
    
    # Handle function calls (up to 3 iterations)
    for _ in range(3):
        calls = find_function_call_parts(response)
        if not calls:
            break
        
        name, fargs = calls[0]
        result = execute_cli_function(name, fargs)
        
        # Track function call
        function_calls.append({
            'name': name,
            'args': fargs,
            'status': 'completed' if result.get('ok') else 'failed',
            'result': result
        })
        
        contents.append(types.Content(role="tool", parts=[make_function_response_part(name, result)]))
        response = await client.aio.models.generate_content(
            model=model,
            contents=contents,
            config=gen_config,
        )
    
    # Extract response text
    response_text = ""
    try:
        parts = response.candidates[0].content.parts if response.candidates else []
        for part in parts:
            if getattr(part, "text", None):
                response_text += part.text
    except Exception:
        response_text = "Error extracting response"
    
    return response_text, function_calls

