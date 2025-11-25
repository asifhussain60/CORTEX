"""
CORTEX 3.0 Security Exceptions
==============================

Security-related exception classes for the CORTEX security framework.
"""


class SecurityError(Exception):
    """Base exception for all security-related errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "SECURITY_ERROR"
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class AuthenticationError(SecurityError):
    """Exception raised for authentication failures."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message, error_code or "AUTH_ERROR", details)


class AuthorizationError(SecurityError):
    """Exception raised for authorization failures."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message, error_code or "AUTHZ_ERROR", details)


class ValidationError(SecurityError):
    """Exception raised for input validation failures."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message, error_code or "VALIDATION_ERROR", details)


class EncryptionError(SecurityError):
    """Exception raised for encryption/decryption failures."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message, error_code or "ENCRYPTION_ERROR", details)


class TokenError(SecurityError):
    """Exception raised for token-related failures."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message, error_code or "TOKEN_ERROR", details)


class AuditError(SecurityError):
    """Exception raised for audit logging failures."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message, error_code or "AUDIT_ERROR", details)