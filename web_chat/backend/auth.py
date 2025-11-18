"""Authentication module for admin interface."""

import os
import hashlib
import secrets
from functools import wraps
from flask import session, request, jsonify
from typing import Optional


# In-memory session storage (in production, use Redis or database)
_active_sessions: dict = {}


def get_admin_password() -> str:
    """Get admin password from environment or use default.
    
    Returns:
        Admin password hash
    """
    # In production, this should be a strong password hash stored securely
    # For now, we'll use environment variable or default
    password = os.environ.get('ADMIN_PASSWORD', 'admin123')  # Default for development
    return password


def hash_password(password: str) -> str:
    """Hash a password using SHA-256.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash.
    
    Args:
        password: Plain text password
        hashed: Hashed password
        
    Returns:
        True if password matches
    """
    return hash_password(password) == hashed


def create_session() -> str:
    """Create a new session.
    
    Returns:
        Session token
    """
    token = secrets.token_urlsafe(32)
    _active_sessions[token] = {
        'authenticated': True,
        'created_at': os.urandom(16).hex()  # Simple timestamp placeholder
    }
    return token


def validate_session(token: Optional[str]) -> bool:
    """Validate a session token.
    
    Args:
        token: Session token
        
    Returns:
        True if session is valid
    """
    if not token:
        return False
    return token in _active_sessions and _active_sessions[token].get('authenticated', False)


def destroy_session(token: Optional[str]) -> None:
    """Destroy a session.
    
    Args:
        token: Session token
    """
    if token and token in _active_sessions:
        del _active_sessions[token]


def login(password: str) -> Optional[str]:
    """Attempt to login with password.
    
    Args:
        password: Admin password
        
    Returns:
        Session token if successful, None otherwise
    """
    expected_password = get_admin_password()
    
    if password == expected_password:
        return create_session()
    return None


def require_auth(f):
    """Decorator to require authentication for a route.
    
    Usage:
        @app.route('/admin/api/initiatives')
        @require_auth
        def list_initiatives():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session token in header or cookie
        token = request.headers.get('X-Session-Token') or request.cookies.get('admin_session')
        
        if not validate_session(token):
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        # Add token to request context
        request.admin_token = token
        return f(*args, **kwargs)
    
    return decorated_function

