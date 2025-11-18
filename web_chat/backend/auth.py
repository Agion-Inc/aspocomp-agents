"""Authentication module for Azure AD authentication."""

import os
import secrets
from functools import wraps
from flask import session, request, jsonify, redirect, url_for
from typing import Optional, Dict, Any
import msal
from web_chat.backend import config


# In-memory session storage (in production, use Redis or database)
_active_sessions: dict = {}


def get_azure_config() -> Dict[str, Any]:
    """Get Azure AD configuration.
    
    Returns:
        Dictionary with Azure AD configuration
    """
    client_id = config.get_azure_client_id()
    client_secret = config.get_azure_client_secret()
    tenant_id = config.get_azure_tenant_id()
    redirect_uri = config.get_azure_redirect_uri()
    
    if not all([client_id, client_secret, tenant_id, redirect_uri]):
        raise ValueError("Azure AD configuration is incomplete. Check environment variables.")
    
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "authority": authority,
        "redirect_uri": redirect_uri,
        "scopes": ["User.Read"]  # Basic user profile scope
    }


def get_msal_app(cache=None):
    """Get MSAL application instance.
    
    Args:
        cache: Optional token cache
        
    Returns:
        ConfidentialClientApplication instance
    """
    azure_config = get_azure_config()
    return msal.ConfidentialClientApplication(
        azure_config["client_id"],
        authority=azure_config["authority"],
        client_credential=azure_config["client_secret"],
        token_cache=cache
    )


def build_auth_code_flow(scopes=None, state=None):
    """Build authorization code flow for Azure AD login.
    
    Args:
        scopes: List of scopes to request
        state: Optional state parameter for CSRF protection
        
    Returns:
        Authorization URL and state
    """
    azure_config = get_azure_config()
    if scopes is None:
        scopes = azure_config["scopes"]
    
    app = get_msal_app()
    
    # Generate state if not provided
    if state is None:
        state = secrets.token_urlsafe(32)
    
    # Build authorization URL
    auth_url = app.get_authorization_request_url(
        scopes=scopes,
        state=state,
        redirect_uri=azure_config["redirect_uri"]
    )
    
    return auth_url, state


def acquire_token_by_authorization_code(code: str, scopes=None):
    """Acquire token using authorization code.
    
    Args:
        code: Authorization code from Azure AD
        scopes: List of scopes
        
    Returns:
        Token result dictionary
    """
    azure_config = get_azure_config()
    if scopes is None:
        scopes = azure_config["scopes"]
    
    app = get_msal_app()
    
    result = app.acquire_token_by_authorization_code(
        code,
        scopes=scopes,
        redirect_uri=azure_config["redirect_uri"]
    )
    
    return result


def create_session(user_info: Dict[str, Any], token: str) -> str:
    """Create a new session for authenticated user.
    
    Args:
        user_info: User information from Azure AD
        token: Access token
    
    Returns:
        Session token
    """
    session_token = secrets.token_urlsafe(32)
    _active_sessions[session_token] = {
        'authenticated': True,
        'user_info': user_info,
        'token': token,
        'created_at': os.urandom(16).hex()
    }
    return session_token


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


def get_user_info(token: Optional[str]) -> Optional[Dict[str, Any]]:
    """Get user information from session.
    
    Args:
        token: Session token
        
    Returns:
        User info dictionary or None
    """
    if not token or token not in _active_sessions:
        return None
    return _active_sessions[token].get('user_info')


def destroy_session(token: Optional[str]) -> None:
    """Destroy a session.
    
    Args:
        token: Session token
    """
    if token and token in _active_sessions:
        del _active_sessions[token]


def require_auth(f):
    """Decorator to require Azure AD authentication for a route.
    
    Usage:
        @app.route('/agents/')
        @require_auth
        def agents_index():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if Azure AD is configured
        if not config.is_azure_auth_configured():
            return jsonify({
                'success': False,
                'error': 'Azure AD authentication is not configured',
                'error_code': 'AUTH_NOT_CONFIGURED'
            }), 500
        
        # Check for session token in header, cookie, or session
        token = (
            request.headers.get('X-Session-Token') or 
            request.cookies.get('azure_session') or
            session.get('azure_session_token')
        )
        
        if not validate_session(token):
            # If this is an API request, return JSON error
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Authentication required',
                    'error_code': 'UNAUTHORIZED'
                }), 401
            
            # For HTML requests, redirect to login
            return redirect(url_for('azure_login'))
        
        # Add token and user info to request context
        request.azure_session_token = token
        request.user_info = get_user_info(token)
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_auth_api(f):
    """Decorator to require Azure AD authentication for API routes only.
    Returns JSON error instead of redirecting.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if Azure AD is configured
        if not config.is_azure_auth_configured():
            return jsonify({
                'success': False,
                'error': 'Azure AD authentication is not configured',
                'error_code': 'AUTH_NOT_CONFIGURED'
            }), 500
        
        # Check for session token
        token = (
            request.headers.get('X-Session-Token') or 
            request.cookies.get('azure_session') or
            session.get('azure_session_token')
        )
        
        if not validate_session(token):
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        # Add token and user info to request context
        request.azure_session_token = token
        request.user_info = get_user_info(token)
        
        return f(*args, **kwargs)
    
    return decorated_function
