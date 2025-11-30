"""
CORTEX 3.0 Security Module
==========================

Enterprise-grade security framework providing authentication, authorization,
input validation, data encryption, and comprehensive audit logging for
production-ready security in the CORTEX documentation generation system.

Components:
- AuthenticationManager: Multi-factor authentication and session management
- AuthorizationManager: Role-based access control and permissions
- InputValidator: Comprehensive input validation and sanitization
- EncryptionManager: Data encryption and cryptographic operations
- AuditLogger: Security audit logging and compliance tracking
"""

__version__ = "3.0.0"

# Import security components
from .authentication import AuthenticationManager, AuthenticationError
from .authorization import AuthorizationManager, AuthorizationError, Role, Permission
from .validation import InputValidator, ValidationError
from .encryption import EncryptionManager, EncryptionError
from .audit import AuditLogger, AuditEvent

# Security utilities
from .utils import SecurityUtils, TokenManager

# Security exceptions
from .exceptions import SecurityError, AuthenticationError, AuthorizationError, ValidationError, EncryptionError

__all__ = [
    # Core components
    'AuthenticationManager',
    'AuthorizationManager', 
    'InputValidator',
    'EncryptionManager',
    'AuditLogger',
    
    # Data types
    'Role',
    'Permission',
    'AuditEvent',
    
    # Utilities
    'SecurityUtils',
    'TokenManager',
    
    # Exceptions
    'SecurityError',
    'AuthenticationError',
    'AuthorizationError',
    'ValidationError',
    'EncryptionError'
]