"""Configuration module for web chat backend."""

import os
import sys
from typing import Optional


def get_project_root() -> str:
    """Get the project root directory."""
    # Get the directory where this file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels: web_chat/backend -> web_chat -> project root
    project_root = os.path.join(current_dir, '../..')
    return os.path.abspath(project_root)


def load_env_files() -> None:
    """Load environment variables from .env.local and .env files."""
    project_root = get_project_root()
    for filename in (".env.local", ".env"):
        filepath = os.path.join(project_root, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value
        except FileNotFoundError:
            continue
        except Exception:
            continue


def get_api_key() -> Optional[str]:
    """Get Gemini API key from environment variables."""
    return os.environ.get("GOOGLE_AI_STUDIO_KEY") or os.environ.get("GOOGLE_API_KEY")


def is_api_key_configured() -> bool:
    """Check if API key is configured."""
    return get_api_key() is not None


def get_azure_client_id() -> Optional[str]:
    """Get Azure AD client ID from environment variables."""
    return os.environ.get("MICROSOFT_CLIENT_ID")


def get_azure_client_secret() -> Optional[str]:
    """Get Azure AD client secret from environment variables."""
    return os.environ.get("MICROSOFT_CLIENT_SECRET")


def get_azure_tenant_id() -> Optional[str]:
    """Get Azure AD tenant ID from environment variables."""
    return os.environ.get("MICROSOFT_TENANT_ID")


def get_azure_redirect_uri() -> Optional[str]:
    """Get Azure AD redirect URI from environment variables."""
    return os.environ.get("MICROSOFT_REDIRECT_URI")


def is_azure_auth_configured() -> bool:
    """Check if Azure AD authentication is configured."""
    return all([
        get_azure_client_id(),
        get_azure_client_secret(),
        get_azure_tenant_id(),
        get_azure_redirect_uri()
    ])


# Load environment files on import
load_env_files()

