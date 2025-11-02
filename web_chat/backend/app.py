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
            model = data.get('model', 'gemini-2.5-flash')
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

