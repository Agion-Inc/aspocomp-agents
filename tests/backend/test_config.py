"""Tests for backend configuration."""

import os
import pytest
from unittest.mock import patch
from web_chat.backend import config


def test_get_api_key_with_env_var():
    """Test that get_api_key() returns API key from environment."""
    with patch.dict(os.environ, {"GOOGLE_AI_STUDIO_KEY": "test-key-123"}):
        key = config.get_api_key()
        assert key == "test-key-123"


def test_get_api_key_fallback():
    """Test that get_api_key() falls back to GOOGLE_API_KEY."""
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "fallback-key-456"}, clear=True):
        key = config.get_api_key()
        assert key == "fallback-key-456"


def test_get_api_key_not_set():
    """Test that get_api_key() returns None when not set."""
    with patch.dict(os.environ, {}, clear=True):
        key = config.get_api_key()
        assert key is None


def test_is_api_key_configured_true():
    """Test that is_api_key_configured() returns True when key is set."""
    with patch.dict(os.environ, {"GOOGLE_AI_STUDIO_KEY": "test-key"}):
        assert config.is_api_key_configured() is True


def test_is_api_key_configured_false():
    """Test that is_api_key_configured() returns False when key is not set."""
    with patch.dict(os.environ, {}, clear=True):
        assert config.is_api_key_configured() is False

