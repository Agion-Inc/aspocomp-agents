"""Configuration module for web chat backend."""

import os
from typing import Optional


def load_env_files() -> None:
    """Load environment variables from .env.local and .env files."""
    for filename in (".env.local", ".env"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
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


# Load environment files on import
load_env_files()

