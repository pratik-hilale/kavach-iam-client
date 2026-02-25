class IAMError(Exception):
    """Base exception for IAM Client errors."""
    pass

class IAMUnauthorized(IAMError):
    """Raised when authentication fails (401)."""
    pass

class IAMForbidden(IAMError):
    """Raised when the client has insufficient permissions (403)."""
    pass

class IAMNotFound(IAMError):
    """Raised when a requested resource (e.g., User) is not found (404)."""
    pass

class IAMUnavailable(IAMError):
    """Raised when the IAM service is down or connection times out."""
    pass

class IAMAPIError(IAMError):
    """Raised when the IAM API returns a general non-200 status code."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"IAM API Error ({status_code}): {message}")

class IAMTokenError(IAMError):
    """Raised when token verification or decoding fails."""
    pass