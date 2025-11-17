"""
CORTEX 3.0 Advanced Error Handling System
==========================================

Enterprise-grade error handling with detailed error codes, recovery mechanisms,
circuit breakers, and comprehensive logging for production debugging.

Features:
- Structured error classification and codes
- Automatic recovery mechanisms
- Circuit breaker patterns
- Comprehensive error logging and tracking
- Error analytics and reporting
"""

from .error_manager import ErrorManager, CortexError, ErrorSeverity
from .recovery_system import RecoverySystem, RecoveryStrategy
from .circuit_breaker import CircuitBreaker, CircuitBreakerState
from .error_logger import ErrorLogger, LogLevel
from .error_analytics import ErrorAnalytics, ErrorPattern

__version__ = "3.0.0"
__all__ = [
    'ErrorManager',
    'CortexError',
    'ErrorSeverity',
    'RecoverySystem',
    'RecoveryStrategy',
    'CircuitBreaker',
    'CircuitBreakerState',
    'ErrorLogger',
    'LogLevel',
    'ErrorAnalytics',
    'ErrorPattern'
]