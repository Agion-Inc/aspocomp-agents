"""Tests for backend error classes."""

import pytest
from web_chat.backend.errors import (
    APIError,
    APIKeyMissingError,
    InvalidRequestError,
    ModelNotFoundError,
    ConversationNotFoundError
)


def test_api_error_creation():
    """Test APIError creation with custom message and error code."""
    error = APIError("Test error", "TEST_ERROR", 400)
    assert error.message == "Test error"
    assert error.error_code == "TEST_ERROR"
    assert error.status_code == 400


def test_api_key_missing_error():
    """Test APIKeyMissingError has correct attributes."""
    error = APIKeyMissingError()
    assert error.message == "API key not found. Set GOOGLE_AI_STUDIO_KEY or GOOGLE_API_KEY."
    assert error.error_code == "API_KEY_MISSING"
    assert error.status_code == 500


def test_invalid_request_error():
    """Test InvalidRequestError has correct attributes."""
    error = InvalidRequestError("Custom message")
    assert error.message == "Custom message"
    assert error.error_code == "INVALID_REQUEST"
    assert error.status_code == 400


def test_model_not_found_error():
    """Test ModelNotFoundError has correct attributes."""
    error = ModelNotFoundError()
    assert error.error_code == "MODEL_NOT_FOUND"
    assert error.status_code == 404


def test_conversation_not_found_error():
    """Test ConversationNotFoundError has correct attributes."""
    error = ConversationNotFoundError()
    assert error.error_code == "CONVERSATION_NOT_FOUND"
    assert error.status_code == 404

