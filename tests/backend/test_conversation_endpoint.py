"""Tests for clear conversation endpoint."""

import pytest
from web_chat.backend.app import create_app
from web_chat.backend.conversation_manager import create_conversation, add_message, get_conversation


@pytest.fixture
def app():
    """Create Flask app for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_clear_conversation_returns_200_for_valid_id(client):
    """Test that DELETE /api/conversation/:id returns 200 for valid ID."""
    conv_id = create_conversation()
    add_message(conv_id, 'user', 'Hello')
    
    response = client.delete(f'/api/conversation/{conv_id}')
    assert response.status_code == 200


def test_clear_conversation_returns_json_with_success(client):
    """Test that DELETE /api/conversation/:id returns JSON with success: true."""
    conv_id = create_conversation()
    
    response = client.delete(f'/api/conversation/{conv_id}')
    data = response.get_json()
    assert data['success'] is True
    assert 'message' in data


def test_clear_conversation_clears_messages(client):
    """Test that DELETE /api/conversation/:id clears conversation messages."""
    conv_id = create_conversation()
    add_message(conv_id, 'user', 'Hello')
    add_message(conv_id, 'assistant', 'Hi')
    
    assert len(get_conversation(conv_id)['messages']) == 2
    
    response = client.delete(f'/api/conversation/{conv_id}')
    assert response.status_code == 200
    
    assert len(get_conversation(conv_id)['messages']) == 0


def test_clear_conversation_returns_404_for_nonexistent(client):
    """Test that DELETE /api/conversation/:id returns 404 for non-existent ID."""
    response = client.delete('/api/conversation/nonexistent-id-12345')
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False

