"""Tests for models endpoint."""

import pytest
from web_chat.backend.app import create_app


@pytest.fixture
def app():
    """Create Flask app for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_models_endpoint_returns_200(client):
    """Test that GET /api/models returns 200 status."""
    response = client.get('/api/models')
    assert response.status_code == 200


def test_models_endpoint_returns_json(client):
    """Test that GET /api/models returns JSON."""
    response = client.get('/api/models')
    assert response.is_json


def test_models_endpoint_has_success_field(client):
    """Test that GET /api/models returns JSON with success: true."""
    response = client.get('/api/models')
    data = response.get_json()
    assert data['success'] is True


def test_models_endpoint_has_models_array(client):
    """Test that GET /api/models includes models array."""
    response = client.get('/api/models')
    data = response.get_json()
    assert 'models' in data
    assert isinstance(data['models'], list)


def test_models_have_required_fields(client):
    """Test that each model has id, name, description fields."""
    response = client.get('/api/models')
    data = response.get_json()
    assert len(data['models']) > 0
    for model in data['models']:
        assert 'id' in model
        assert 'name' in model
        assert 'description' in model
        assert isinstance(model['id'], str)
        assert isinstance(model['name'], str)
        assert isinstance(model['description'], str)


def test_default_model_included(client):
    """Test that default model gemini-2.5-flash is included."""
    response = client.get('/api/models')
    data = response.get_json()
    model_ids = [model['id'] for model in data['models']]
    assert 'gemini-2.5-flash' in model_ids

