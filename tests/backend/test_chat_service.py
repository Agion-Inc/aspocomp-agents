"""Tests for chat service."""

import pytest
from unittest.mock import patch
from web_chat.backend.chat_service import send_message
from web_chat.backend.errors import APIKeyMissingError
from web_chat.backend import config


@pytest.fixture
def mock_api_key():
    """Mock API key."""
    with patch.object(config, 'get_api_key', return_value='test-api-key'):
        yield


@pytest.fixture
def mock_no_api_key():
    """Mock no API key."""
    with patch.object(config, 'get_api_key', return_value=None):
        yield


@pytest.mark.asyncio
async def test_send_message_creates_conversation_if_no_id(mock_api_key):
    """Test that send_message() creates conversation if no ID provided."""
    with patch('web_chat.backend.chat_service._call_gemini_agent') as mock_call:
        mock_call.return_value = ('Test response', [])
        
        result = await send_message('Hello', 'gemini-2.5-flash', False, None)
        
        assert 'conversation_id' in result
        assert result['conversation_id'] is not None


@pytest.mark.asyncio
async def test_send_message_uses_existing_conversation(mock_api_key):
    """Test that send_message() uses existing conversation if ID provided."""
    from web_chat.backend.conversation_manager import create_conversation
    
    conv_id = create_conversation()
    
    with patch('web_chat.backend.chat_service._call_gemini_agent') as mock_call:
        mock_call.return_value = ('Test response', [])
        
        result = await send_message('Hello', 'gemini-2.5-flash', False, conv_id)
        
        assert result['conversation_id'] == conv_id


@pytest.mark.asyncio
async def test_send_message_handles_api_key_missing(mock_no_api_key):
    """Test that send_message() handles API key missing error."""
    with pytest.raises(APIKeyMissingError):
        await send_message('Hello', 'gemini-2.5-flash', False, None)


@pytest.mark.asyncio
async def test_send_message_returns_response_with_conversation_id(mock_api_key):
    """Test that send_message() returns response with conversation_id."""
    with patch('web_chat.backend.chat_service._call_gemini_agent') as mock_call:
        mock_call.return_value = ('Test response', [])
        
        result = await send_message('Hello', 'gemini-2.5-flash', False, None)
        
        assert 'conversation_id' in result
        assert 'response' in result
        assert result['response'] == 'Test response'


@pytest.mark.asyncio
async def test_send_message_handles_model_parameter(mock_api_key):
    """Test that send_message() handles model parameter."""
    with patch('web_chat.backend.chat_service._call_gemini_agent') as mock_call:
        mock_call.return_value = ('Test response', [])
        
        await send_message('Hello', 'gemini-2.5-pro', False, None)
        
        # Verify model was passed to _call_gemini_agent
        call_args = mock_call.call_args
        assert call_args[0][1] == 'gemini-2.5-pro'  # model is second positional arg
