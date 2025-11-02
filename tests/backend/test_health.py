"""Tests for Flask app health endpoint."""

import pytest
from datetime import datetime
from flask import Flask
from flask_cors import CORS
from web_chat.backend.app import create_app


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_health_endpoint_returns_200(client):
    """Test that GET /api/health returns 200 status."""
    response = client.get('/api/health')
    assert response.status_code == 200


def test_health_endpoint_returns_json(client):
    """Test that GET /api/health returns JSON."""
    response = client.get('/api/health')
    assert response.is_json


def test_health_endpoint_has_status_field(client):
    """Test that GET /api/health returns JSON with status: 'healthy'."""
    response = client.get('/api/health')
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_health_endpoint_has_api_key_configured(client):
    """Test that GET /api/health includes api_key_configured boolean."""
    response = client.get('/api/health')
    data = response.get_json()
    assert 'api_key_configured' in data
    assert isinstance(data['api_key_configured'], bool)


def test_health_endpoint_has_timestamp(client):
    """Test that GET /api/health includes timestamp in ISO format."""
    response = client.get('/api/health')
    data = response.get_json()
    assert 'timestamp' in data
    # Verify timestamp is valid ISO format
    datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))


def test_health_endpoint_cors_headers(client):
    """Test that CORS headers are present in response."""
    response = client.get('/api/health')
    assert 'Access-Control-Allow-Origin' in response.headers

