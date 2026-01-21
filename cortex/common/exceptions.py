"""
cortex/common/exceptions.py

Common exception types with diagnostics for production use.
"""


class ValidationError(Exception):
    """Validation error with diagnostic context.
    
    Provides structured error information for debugging and monitoring.
    """
    
    def __init__(self, message: str, file_path: str = None, line_info: str = None, 
                 context: dict = None):
        """Initialize validation error.
        
        Args:
            message: Error message
            file_path: Path to file that caused error (optional)
            line_info: Line number or error details (optional)
            context: Additional context dict (optional)
        """
        self.message = message
        self.file_path = file_path
        self.line_info = line_info
        self.context = context or {}
        
        # Build detailed message
        parts = [message]
        if file_path:
            parts.append(f"file: {file_path}")
        if line_info:
            parts.append(f"line: {line_info}")
        
        super().__init__(" | ".join(parts))


class RecoverableError(Exception):
    """Error that can be recovered from via retry or fallback.
    
    Used to distinguish transient errors from permanent failures.
    """
    
    def __init__(self, message: str, retry_count: int = 0, 
                 retry_delay_ms: float = 100):
        """Initialize recoverable error.
        
        Args:
            message: Error message
            retry_count: Number of retries attempted
            retry_delay_ms: Delay between retries in milliseconds
        """
        self.message = message
        self.retry_count = retry_count
        self.retry_delay_ms = retry_delay_ms
        
        super().__init__(
            f"{message} (retries: {retry_count}, delay: {retry_delay_ms}ms)"
        )


class ConfigurationError(Exception):
    """Configuration validation error.
    
    Indicates invalid or missing configuration values.
    """
    
    def __init__(self, message: str, config_key: str = None, 
                 expected: str = None, received: str = None):
        """Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that failed validation
            expected: Expected value or type
            received: Actual value received
        """
        self.message = message
        self.config_key = config_key
        self.expected = expected
        self.received = received
        
        parts = [message]
        if config_key:
            parts.append(f"key: {config_key}")
        if expected and received:
            parts.append(f"expected: {expected}, got: {received}")
        
        super().__init__(" | ".join(parts))


class HealthCheckError(Exception):
    """Health check failure.
    
    Indicates a component failed its health verification.
    """
    
    def __init__(self, component: str, message: str, 
                 recovery_action: str = None):
        """Initialize health check error.
        
        Args:
            component: Component that failed (e.g., "database", "audit_logger")
            message: Failure reason
            recovery_action: Suggested recovery action
        """
        self.component = component
        self.message = message
        self.recovery_action = recovery_action
        
        parts = [f"{component} health check failed: {message}"]
        if recovery_action:
            parts.append(f"recovery: {recovery_action}")
        
        super().__init__(" | ".join(parts))
