"""Flask application for web chat backend."""

import sys
import os
# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, os.path.abspath(project_root))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
import asyncio
from web_chat.backend import config
from web_chat.backend.errors import APIError, InvalidRequestError, ConversationNotFoundError
from web_chat.backend.chat_service import send_message
from web_chat.backend.conversation_manager import clear_conversation, get_conversation
from web_chat.backend.agent_registry import get_registry


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Configure CORS - allow all origins for development
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'api_key_configured': config.is_api_key_configured(),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
    
    @app.route('/api/models', methods=['GET'])
    def models():
        """Get available Gemini models."""
        models_list = [
            {
                'id': 'gemini-2.5-flash',
                'name': 'Gemini 2.5 Flash',
                'description': 'Fast and efficient model for quick responses'
            },
            {
                'id': 'gemini-2.5-pro',
                'name': 'Gemini 2.5 Pro',
                'description': 'Advanced model for complex tasks'
            }
        ]
        return jsonify({
            'success': True,
            'models': models_list
        })
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        """Send a message to Gemini Agent."""
        try:
            if not request.is_json:
                raise InvalidRequestError("Request must be JSON")
            
            data = request.get_json()
            if not data or 'message' not in data:
                raise InvalidRequestError("Message field is required")
            
            message = data['message']
            # Always use gemini-2.5-flash for chat
            model = 'gemini-2.5-flash'
            mcp_enabled = data.get('mcp_enabled', False)
            conversation_id = data.get('conversation_id')
            
            # Run async function
            result = asyncio.run(send_message(message, model, mcp_enabled, conversation_id))
            
            return jsonify(result)
        except APIError as e:
            raise e
        except Exception as e:
            raise APIError(str(e), "INTERNAL_ERROR", 500)
    
    @app.route('/api/conversation/<conversation_id>', methods=['DELETE'])
    def clear_conversation_endpoint(conversation_id):
        """Clear conversation history."""
        try:
            # Check if conversation exists
            if get_conversation(conversation_id) is None:
                raise ConversationNotFoundError()
            
            clear_conversation(conversation_id)
            
            return jsonify({
                'success': True,
                'message': 'Conversation cleared'
            })
        except APIError as e:
            raise e
        except Exception as e:
            raise APIError(str(e), "INTERNAL_ERROR", 500)
    
    @app.route('/api/agents', methods=['GET'])
    def list_agents():
        """List all available agents."""
        try:
            registry = get_registry()
            agents = registry.list_agents()
            
            return jsonify({
                'success': True,
                'agents': agents
            })
        except Exception as e:
            raise APIError(str(e), "INTERNAL_ERROR", 500)
    
    @app.route('/api/chat/<agent_id>', methods=['POST'])
    def chat_agent(agent_id):
        """Send a message to a specific agent."""
        try:
            if not request.is_json:
                raise InvalidRequestError("Request must be JSON")
            
            data = request.get_json()
            if not data or 'message' not in data:
                raise InvalidRequestError("Message field is required")
            
            message = data['message']
            conversation_id = data.get('conversation_id')
            context = data.get('context', {})
            
            # Get agent from registry
            registry = get_registry()
            agent = registry.get_agent(agent_id)
            
            if not agent:
                raise APIError(f"Agent '{agent_id}' not found", "AGENT_NOT_FOUND", 404)
            
            if not agent.is_enabled():
                raise APIError(f"Agent '{agent_id}' is disabled", "AGENT_DISABLED", 403)
            
            # Process message with agent
            result = asyncio.run(agent.process_message(message, conversation_id, context))
            
            return jsonify(result)
        except APIError as e:
            raise e
        except Exception as e:
            raise APIError(str(e), "INTERNAL_ERROR", 500)
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle API errors."""
        response = jsonify({
            'success': False,
            'error': error.message,
            'error_code': error.error_code
        })
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'success': False,
            'error': 'Not found',
            'error_code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors."""
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
        }), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Serve static files from frontend directory
    @app.route('/')
    def index():
        frontend_dir = os.path.join(os.path.dirname(__file__), '../frontend')
        return send_from_directory(frontend_dir, 'index.html')
    
    @app.route('/agents/')
    def agents_index():
        """Serve agent listing page."""
        frontend_dir = os.path.join(os.path.dirname(__file__), '../frontend')
        agents_dir = os.path.join(frontend_dir, 'agents')
        return send_from_directory(agents_dir, 'index.html')
    
    @app.route('/agents/<path:path>')
    def serve_agent_static(path):
        """Serve agent-specific static files."""
        frontend_dir = os.path.join(os.path.dirname(__file__), '../frontend')
        agents_dir = os.path.join(frontend_dir, 'agents')
        
        # Remove trailing slash if present
        clean_path = path.rstrip('/')
        
        # If path is empty or just an agent name, serve index.html from that agent directory
        if not clean_path or '/' not in clean_path:
            agent_dir = os.path.join(agents_dir, clean_path) if clean_path else agents_dir
            index_path = os.path.join(agent_dir, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(agent_dir, 'index.html')
            # Fallback to agent listing
            return send_from_directory(agents_dir, 'index.html')
        
        # Split path into agent name and file path
        parts = clean_path.split('/', 1)
        agent_name = parts[0]
        file_path = parts[1] if len(parts) > 1 else 'index.html'
        
        agent_dir = os.path.join(agents_dir, agent_name)
        full_file_path = os.path.join(agent_dir, file_path)
        
        # Check if file exists in agent directory
        if os.path.exists(full_file_path) and os.path.isfile(full_file_path):
            return send_from_directory(agent_dir, file_path)
        
        # If it's a directory request, try index.html
        if os.path.isdir(os.path.join(agent_dir, file_path)):
            index_path = os.path.join(agent_dir, file_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(os.path.join(agent_dir, file_path), 'index.html')
        
        # Fallback to agent listing
        return send_from_directory(agents_dir, 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        frontend_dir = os.path.join(os.path.dirname(__file__), '../frontend')
        try:
            return send_from_directory(frontend_dir, path)
        except:
            # Also try serving from public directory for images/videos
            public_dir = os.path.join(os.path.dirname(__file__), '../../public')
            if os.path.exists(os.path.join(public_dir, path)):
                return send_from_directory(public_dir, path)
            return send_from_directory(frontend_dir, 'index.html')
    
    app.run(debug=True, host='0.0.0.0', port=5001)

