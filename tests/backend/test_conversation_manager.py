"""Tests for conversation manager."""

import pytest
from web_chat.backend.conversation_manager import (
    create_conversation,
    get_conversation,
    add_message,
    clear_conversation
)


def test_create_conversation_returns_unique_id():
    """Test that create_conversation() returns unique conversation ID."""
    id1 = create_conversation()
    id2 = create_conversation()
    assert id1 != id2
    assert isinstance(id1, str)
    assert len(id1) > 0


def test_get_conversation_returns_conversation():
    """Test that get_conversation(id) returns conversation with messages."""
    conv_id = create_conversation()
    conversation = get_conversation(conv_id)
    assert conversation is not None
    assert 'id' in conversation
    assert 'messages' in conversation
    assert conversation['id'] == conv_id
    assert isinstance(conversation['messages'], list)


def test_add_message_adds_to_conversation():
    """Test that add_message(id, role, content) adds message to conversation."""
    conv_id = create_conversation()
    add_message(conv_id, 'user', 'Hello')
    conversation = get_conversation(conv_id)
    assert len(conversation['messages']) == 1
    assert conversation['messages'][0]['role'] == 'user'
    assert conversation['messages'][0]['content'] == 'Hello'


def test_clear_conversation_removes_messages():
    """Test that clear_conversation(id) removes all messages."""
    conv_id = create_conversation()
    add_message(conv_id, 'user', 'Hello')
    add_message(conv_id, 'assistant', 'Hi there')
    assert len(get_conversation(conv_id)['messages']) == 2
    clear_conversation(conv_id)
    assert len(get_conversation(conv_id)['messages']) == 0


def test_get_conversation_returns_none_for_nonexistent():
    """Test that get_conversation() returns None for non-existent ID."""
    conversation = get_conversation('nonexistent-id-12345')
    assert conversation is None


def test_conversation_messages_stored_in_order():
    """Test that conversation messages are stored in order."""
    conv_id = create_conversation()
    add_message(conv_id, 'user', 'First')
    add_message(conv_id, 'assistant', 'Second')
    add_message(conv_id, 'user', 'Third')
    conversation = get_conversation(conv_id)
    assert len(conversation['messages']) == 3
    assert conversation['messages'][0]['content'] == 'First'
    assert conversation['messages'][1]['content'] == 'Second'
    assert conversation['messages'][2]['content'] == 'Third'

