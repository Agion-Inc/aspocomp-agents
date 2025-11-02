"""Tests for chat endpoint."""

import pytest
from unittest.mock import patch
from web_chat.backend.app import create_app
from web_chat.backend.errors import APIKeyMissingError


@pytest.fixture
def app():
    """Create Flask app for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_chat_endpoint_valid_message_returns_200(client):
    """Test that POST /api/chat with valid message returns 200."""
    async def mock_send_message(*args, **kwargs):
        return {
            'success': True,
            'response': 'Test response',
            'conversation_id': 'test-conv-id',
            'function_calls': [],
            'timestamp': '2025-01-01T00:00:00Z'
        }
    
    with patch('web_chat.backend.app.send_message', side_effect=mock_send_message):
        response = client.post('/api/chat', 
                              json={'message': 'Hello'},
                              content_type='application/json')
        assert response.status_code == 200


def test_chat_endpoint_returns_json(client):
    """Test that POST /api/chat returns JSON."""
    async def mock_send_message(*args, **kwargs):
        return {
            'success': True,
            'response': 'Test response',
            'conversation_id': 'test-conv-id',
            'function_calls': [],
            'timestamp': '2025-01-01T00:00:00Z'
        }
    
    with patch('web_chat.backend.app.send_message', side_effect=mock_send_message):
        response = client.post('/api/chat', 
                              json={'message': 'Hello'},
                              content_type='application/json')
        assert response.is_json


def test_chat_endpoint_has_success_field(client):
    """Test that POST /api/chat returns JSON with success: true."""
    async def mock_send_message(*args, **kwargs):
        return {
            'success': True,
            'response': 'Test response',
            'conversation_id': 'test-conv-id',
            'function_calls': [],
            'timestamp': '2025-01-01T00:00:00Z'
        }
    
    with patch('web_chat.backend.app.send_message', side_effect=mock_send_message):
        response = client.post('/api/chat', 
                              json={'message': 'Hello'},
                              content_type='application/json')
        data = response.get_json()
        assert data['success'] is True


def test_chat_endpoint_includes_response_field(client):
    """Test that POST /api/chat includes response field with text."""
    async def mock_send_message(*args, **kwargs):
        return {
            'success': True,
            'response': 'Test response',
            'conversation_id': 'test-conv-id',
            'function_calls': [],
            'timestamp': '2025-01-01T00:00:00Z'
        }
    
    with patch('web_chat.backend.app.send_message', side_effect=mock_send_message):
        response = client.post('/api/chat', 
                              json={'message': 'Hello'},
                              content_type='application/json')
        data = response.get_json()
        assert 'response' in data
        assert data['response'] == 'Test response'


def test_chat_endpoint_includes_conversation_id(client):
    """Test that POST /api/chat includes conversation_id."""
    async def mock_send_message(*args, **kwargs):
        return {
            'success': True,
            'response': 'Test response',
            'conversation_id': 'test-conv-id',
            'function_calls': [],
            'timestamp': '2025-01-01T00:00:00Z'
        }
    
    with patch('web_chat.backend.app.send_message', side_effect=mock_send_message):
        response = client.post('/api/chat', 
                              json={'message': 'Hello'},
                              content_type='application/json')
        data = response.get_json()
        assert 'conversation_id' in data


def test_chat_endpoint_validates_message_field(client):
    """Test that POST /api/chat validates required message field (400 if missing)."""
    response = client.post('/api/chat', 
                          json={},
                          content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data


def test_chat_endpoint_accepts_optional_model(client):
    """Test that POST /api/chat accepts optional model parameter."""
    call_args_list = []
    
    async def mock_send_message(*args, **kwargs):
        call_args_list.append(args)
        return {
            'success': True,
            'response': 'Test response',
            'conversation_id': 'test-conv-id',
            'function_calls': [],
            'timestamp': '2025-01-01T00:00:00Z'
        }
    
    with patch('web_chat.backend.app.send_message', side_effect=mock_send_message):
        response = client.post('/api/chat', 
                              json={'message': 'Hello', 'model': 'gemini-2.5-pro'},
                              content_type='application/json')
        assert response.status_code == 200
        # Verify model was passed
        assert len(call_args_list) > 0
        assert call_args_list[0][1] == 'gemini-2.5-pro'  # model is second positional arg


def test_chat_endpoint_accepts_optional_conversation_id(client):
    """Test that POST /api/chat accepts optional conversation_id parameter."""
    call_args_list = []
    
    async def mock_send_message(*args, **kwargs):
        call_args_list.append(args)
        return {
            'success': True,
            'response': 'Test response',
            'conversation_id': 'test-conv-id',
            'function_calls': [],
            'timestamp': '2025-01-01T00:00:00Z'
        }
    
    with patch('web_chat.backend.app.send_message', side_effect=mock_send_message):
        response = client.post('/api/chat', 
                              json={'message': 'Hello', 'conversation_id': 'existing-id'},
                              content_type='application/json')
        assert response.status_code == 200
        # Verify conversation_id was passed
        assert len(call_args_list) > 0
        assert call_args_list[0][3] == 'existing-id'  # conversation_id is fourth positional arg


def test_chat_endpoint_handles_api_errors(client):
    """Test that POST /api/chat handles API errors gracefully (500)."""
    async def mock_send_message(*args, **kwargs):
        raise APIKeyMissingError()
    
    with patch('web_chat.backend.app.send_message', side_effect=mock_send_message):
        response = client.post('/api/chat', 
                              json={'message': 'Hello'},
                              content_type='application/json')
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data


def test_chat_endpoint_validates_json_format(client):
    """Test that POST /api/chat validates request JSON format."""
    response = client.post('/api/chat', 
                          data='invalid json',
                          content_type='application/json')
    # Flask returns 400 for invalid JSON automatically
    assert response.status_code in [400, 500]  # 500 if error handler catches it
