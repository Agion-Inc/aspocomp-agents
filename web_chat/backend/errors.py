"""Custom error classes for web chat backend."""


class APIError(Exception):
    """Base exception for API errors."""
    
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class APIKeyMissingError(APIError):
    """Raised when API key is not configured."""
    
    def __init__(self, message: str = "API key not found. Set GOOGLE_AI_STUDIO_KEY or GOOGLE_API_KEY."):
        super().__init__(message, "API_KEY_MISSING", 500)


class InvalidRequestError(APIError):
    """Raised when request validation fails."""
    
    def __init__(self, message: str = "Invalid request"):
        super().__init__(message, "INVALID_REQUEST", 400)


class ModelNotFoundError(APIError):
    """Raised when specified model is not found."""
    
    def __init__(self, message: str = "Model not found"):
        super().__init__(message, "MODEL_NOT_FOUND", 404)


class ConversationNotFoundError(APIError):
    """Raised when conversation ID is not found."""
    
    def __init__(self, message: str = "Conversation not found"):
        super().__init__(message, "CONVERSATION_NOT_FOUND", 404)

