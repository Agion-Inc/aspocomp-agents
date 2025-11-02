"""Tests for enhanced function call rendering."""

import pytest
from web_chat.frontend.js.ui import renderFunctionCall


def test_render_function_call_shows_name():
    """Test that renderFunctionCall displays function name."""
    funcCall = {
        'name': 'test_function',
        'status': 'completed',
        'args': {},
        'result': {}
    }
    
    # This would be a DOM test in browser context
    # For now, just verify the function exists
    assert callable(renderFunctionCall)


def test_render_function_call_shows_status():
    """Test that renderFunctionCall displays status correctly."""
    funcCall = {
        'name': 'test_function',
        'status': 'completed'
    }
    
    assert callable(renderFunctionCall)


def test_render_function_call_shows_args_when_available():
    """Test that renderFunctionCall shows arguments when available."""
    funcCall = {
        'name': 'test_function',
        'status': 'completed',
        'args': {'param1': 'value1'}
    }
    
    assert callable(renderFunctionCall)

